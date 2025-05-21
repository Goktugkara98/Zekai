# =============================================================================
# Gemini AI Servis Modülü (Gemini AI Service Module)
# =============================================================================
# Bu modül, Google Gemini API'si ile etkileşim kurmak için özel bir servis
# sınıfı içerir. BaseAIService tarafından dinamik olarak yüklenip kullanılır.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 GEMINISERVICE SINIFI (GEMINISERVICE CLASS)
#     2.1. __init__             : Başlatıcı metot, API anahtarını yapılandırır.
#     2.2. send_chat_request    : Gemini API'sine sohbet isteği gönderir ve yanıtı işler.
# 3.0 ÖRNEK KULLANIM (EXAMPLE USAGE)
#     (Bu bölüm, modül doğrudan çalıştırıldığında test amaçlıdır.)
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
import google.generativeai as genai
import os
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from flask import current_app # Loglama için

if TYPE_CHECKING:
    from app.models.entities.model import Model as AIModelEntity

# =============================================================================
# 2.0 GEMINISERVICE SINIFI (GEMINISERVICE CLASS)
# =============================================================================
class GeminiService:
    """
    Google Gemini API'si ile etkileşim kurmak için servis sınıfı.
    """

    # -------------------------------------------------------------------------
    # 2.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        GeminiService'i başlatır ve Gemini API'sini yapılandırır.

        Args:
            api_key (str): Gemini API için kullanılacak API anahtarı.
            config (Optional[Dict]): Uygulama yapılandırması (şu anda doğrudan kullanılmıyor).
        """
        self.api_key = api_key
        self.config = config

        if not self.api_key:
            # Hata, send_chat_request sırasında veya genai.configure hemen bir hata fırlatırsa yakalanacaktır.
            return

        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            # Bu, geçersiz anahtar formatı veya anahtarla ilgili diğer sorunları gösterebilir.
            # Hatanın yukarıya yayılmasına izin verilir.
            raise

    # -------------------------------------------------------------------------
    # 2.2. Gemini API'sine sohbet isteği gönderir (send_chat_request)
    # -------------------------------------------------------------------------
    def send_chat_request(self, model_entity: 'AIModelEntity', chat_message: Optional[str], chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Bir sohbet isteğini Gemini API'sine gönderir.

        Args:
            model_entity (AIModelEntity): Kullanılacak AI modelinin entity'si.
                                          `external_model_name` alanı Gemini model adını belirtir.
            chat_message (Optional[str]): Gönderilecek mevcut kullanıcı mesajı.
            chat_history (List[Dict[str, str]]): Konuşmadaki önceki mesajların listesi.
                                                 Her sözlük 'role' ve 'content' veya 'parts' içermelidir.

        Returns:
            Dict[str, Any]: Yanıtı veya bir hata mesajını içeren bir sözlük.
                            Başarılı yanıt: {"response": "...", "status_code": 200}
                            Hata yanıtı: {"error": "...", "details": "...", "status_code": ...}
        """
        if not self.api_key:
            return {"error": "Gemini API anahtarı yapılandırılmamış.", "status_code": 500}

        if not chat_message and not chat_history:
            return {"error": "Girdi sağlanmadı. Hem chat_message hem de chat_history boş.", "status_code": 400}

        target_model_name = 'gemini-pro' # Varsayılan model
        if hasattr(model_entity, 'external_model_name') and model_entity.external_model_name:
            target_model_name = model_entity.external_model_name

        try:
            print(f"\n=== GEMINI API DETAYLARI ===")
            print(f"API URL: https://generativelanguage.googleapis.com/v1/models/{target_model_name}")
            print(f"Model Adı: {target_model_name}")
            print(f"API Key: {self.api_key[:4]}...{self.api_key[-4:] if len(self.api_key) > 8 else '****'}")
            print(f"Safety Settings: {getattr(genai, 'safety_settings', 'Varsayılan')}")
            print("=" * 50)
            
            model = genai.GenerativeModel(target_model_name)
            gemini_history_for_api = []
            for message in chat_history:
                role = message.get('role')
                api_role = 'model' if role == 'assistant' else role
                if api_role not in ['user', 'model']:
                    continue

                parts_content = message.get('parts')
                if not parts_content:
                    content_value = message.get('content')
                    if content_value:
                        parts_content = [content_value]
                    else:
                        continue
                
                if not isinstance(parts_content, list):
                    parts_content = [str(parts_content)]

                gemini_history_for_api.append({'role': api_role, 'parts': parts_content})

            api_response = None
            if gemini_history_for_api:
                print("\n=== GEMINI API'YE GÖNDERİLEN MESAJ ===")
                print("Chat History:", gemini_history_for_api)
                print("New Message:", chat_message)
                print("=" * 50 + "\n")
                
                # Eğer history'de zaten bu mesaj varsa, chat_message'ı boş bırak
                if chat_message and gemini_history_for_api and \
                   gemini_history_for_api[-1]['role'] == 'user' and \
                   gemini_history_for_api[-1]['parts'] and \
                   gemini_history_for_api[-1]['parts'][0].get('text') == chat_message:
                    chat_message = None
                
                chat_session = model.start_chat(history=gemini_history_for_api)
                if chat_message:
                    print(f"\n=== GEMINI API'YE GÖNDERİLEN MESAJ DETAYI ===")
                    print(f"Mesaj: {chat_message}")
                    print("=" * 50)
                    
                    try:
                        api_response = chat_session.send_message(chat_message)
                        print(f"\n=== GEMINI API YANITI ===")
                        print(f"Yanıt Durumu: Başarılı")
                        print(f"Yanıt Metni: {api_response.text[:100]}..." if len(api_response.text) > 100 else api_response.text)
                        print(f"Yanıt Uzunluğu: {len(api_response.text)} karakter")
                        print("=" * 50)
                    except Exception as e:
                        print(f"\n=== GEMINI API HATA ===")
                        print(f"Hata: {str(e)}")
                        print("=" * 50)
                        raise
                else:
                    if gemini_history_for_api and gemini_history_for_api[-1]['role'] == 'model':
                        last_model_parts = gemini_history_for_api[-1]['parts']
                        response_text = "".join(str(p) for p in last_model_parts)
                        return {"response": response_text, "status_code": 200}
                    else:
                        return {"response": "Yeni mesaj gönderilmedi; sadece geçmiş sağlandı.", "status_code": 200}
            elif chat_message:
                print(f"\n=== GEMINI API TEK MESAJ GÖNDERİMİ ===")
                print(f"Mesaj: {chat_message}")
                print("=" * 50)
                
                try:
                    api_response = model.generate_content(chat_message)
                    print(f"\n=== GEMINI API TEK MESAJ YANITI ===")
                    print(f"Yanıt Durumu: Başarılı")
                    print(f"Yanıt Metni: {api_response.text[:100]}..." if len(api_response.text) > 100 else api_response.text)
                    print("=" * 50)
                except Exception as e:
                    print(f"\n=== GEMINI API TEK MESAJ HATASI ===")
                    print(f"Hata: {str(e)}")
                    print("=" * 50)
                    raise
            else:
                print(f"\n=== GEMINI API GİRDİ HATASI ===")
                print("Hata: İşlenecek girdi bulunamadı.")
                print("=" * 50)
                return {"error": "İşlenecek girdi bulunamadı.", "status_code": 400}

            if not api_response:
                print(f"\n=== GEMINI API YANIT YOK ===")
                print("Hata: Gemini API'sinden yanıt alınamadı.")
                print("=" * 50)
                return {"error": "Gemini API'sinden yanıt alınamadı.", "status_code": 500}

            response_text = api_response.text
            print(f"\n=== GEMINI API İşLEM TAMAMLANDI ===")
            print(f"Son Yanıt: {response_text[:150]}..." if len(response_text) > 150 else response_text)
            print("=" * 50)
            return {"response": response_text, "status_code": 200}

        except Exception as e:
            import traceback
            error_message = f"Gemini API hatası: {str(e)}"
            print(f"\n=== GEMINI API GENEL HATA ===")
            print(f"Hata Mesajı: {error_message}")
            print(f"Hata Detayları: {str(e)}")
            print(f"Hata İzi: \n{traceback.format_exc()}")
            print("=" * 50)
            return {"error": error_message, "details": str(e), "status_code": 500}

# =============================================================================
# 3.0 ÖRNEK KULLANIM (EXAMPLE USAGE)
# =============================================================================
# Bu bölüm, modül doğrudan çalıştırıldığında test amaçlıdır.
# Üretim ortamında bu kısım çalıştırılmamalıdır.
# if __name__ == '__main__':
#     pass # Loglama ve print fonksiyonları kaldırıldı.