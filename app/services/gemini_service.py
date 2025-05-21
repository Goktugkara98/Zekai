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
                chat_session = model.start_chat(history=gemini_history_for_api)
                if chat_message:
                    api_response = chat_session.send_message(chat_message)
                else:
                    if gemini_history_for_api and gemini_history_for_api[-1]['role'] == 'model':
                        last_model_parts = gemini_history_for_api[-1]['parts']
                        response_text = "".join(str(p) for p in last_model_parts)
                        return {"response": response_text, "status_code": 200}
                    else:
                        return {"response": "Yeni mesaj gönderilmedi; sadece geçmiş sağlandı.", "status_code": 200}
            elif chat_message:
                api_response = model.generate_content(chat_message)
            else:
                return {"error": "İşlenecek girdi bulunamadı.", "status_code": 400}

            if not api_response:
                 return {"error": "Gemini API'sinden yanıt alınamadı.", "status_code": 500}

            response_text = api_response.text
            return {"response": response_text, "status_code": 200}

        except Exception as e:
            error_message = str(e)
            return {"error": "Gemini API isteği başarısız oldu.", "details": error_message, "status_code": 500}

# =============================================================================
# 3.0 ÖRNEK KULLANIM (EXAMPLE USAGE)
# =============================================================================
# Bu bölüm, modül doğrudan çalıştırıldığında test amaçlıdır.
# Üretim ortamında bu kısım çalıştırılmamalıdır.
# if __name__ == '__main__':
#     pass # Loglama ve print fonksiyonları kaldırıldı.