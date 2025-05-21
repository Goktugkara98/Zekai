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
        self.config = config # Gelecekteki kullanımlar için sakla

        current_app.logger.info("--- GeminiService Başlatılıyor ---")
        current_app.logger.info(f"Kullanılacak API Anahtarı Uzunluğu: {len(self.api_key) if self.api_key else 'Yok'}")
        # Ortam değişkenlerini loglamak güvenlik riski oluşturabilir, dikkatli olunmalı.
        # current_app.logger.info(f"Ortam Değişkeni GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
        # current_app.logger.info(f"Ortam Değişkeni GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")


        if not self.api_key:
            current_app.logger.error("GeminiService API anahtarı olmadan başlatıldı.")
            # genai.configure muhtemelen başarısız olacak veya sonraki çağrılar hata verecektir.
            # Hata, send_chat_request sırasında veya genai.configure hemen bir hata fırlatırsa yakalanacaktır.
            return

        try:
            genai.configure(api_key=self.api_key)
            current_app.logger.info("GeminiService: genai.configure(api_key='<sağlanan_anahtar>') başarıyla çağrıldı.")
        except Exception as e:
            current_app.logger.error(f"Sağlanan API anahtarı ile Gemini yapılandırılamadı: {e}", exc_info=True)
            # Bu, geçersiz anahtar formatı veya anahtarla ilgili diğer sorunları gösterebilir.

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
        if not self.api_key: # __init__ içinde kontrol edilmiş olsa da, burada da kontrol etmek iyi bir pratik.
            current_app.logger.error("GeminiService.send_chat_request: API anahtarı yapılandırılmamış.")
            return {"error": "Gemini API anahtarı yapılandırılmamış.", "status_code": 500}

        if not chat_message and not chat_history:
            current_app.logger.warning("GeminiService.send_chat_request: Hem chat_message hem de chat_history boş.")
            return {"error": "Girdi sağlanmadı. Hem chat_message hem de chat_history boş.", "status_code": 400}

        target_model_name = 'gemini-pro' # Varsayılan model
        if hasattr(model_entity, 'external_model_name') and model_entity.external_model_name:
            target_model_name = model_entity.external_model_name
            current_app.logger.info(f"GeminiService: Entity'den alınan Gemini modeli kullanılıyor: {target_model_name}")
        else:
            current_app.logger.info(f"GeminiService: Varsayılan Gemini modeli kullanılıyor: {target_model_name}")

        try:
            model = genai.GenerativeModel(target_model_name)
            gemini_history_for_api = []
            for message in chat_history:
                role = message.get('role')
                # Gemini 'user' ve 'model' rollerini bekler. 'assistant' -> 'model' dönüşümü yapılır.
                api_role = 'model' if role == 'assistant' else role
                if api_role not in ['user', 'model']:
                    current_app.logger.warning(f"GeminiService: Geçmişte desteklenmeyen rol '{role}', atlanıyor.")
                    continue

                # Gemini 'parts' anahtarını bekler, 'content' varsa 'parts'a dönüştürülür.
                parts_content = message.get('parts')
                if not parts_content: # 'parts' yoksa 'content'i kullan
                    content_value = message.get('content')
                    if content_value:
                        parts_content = [content_value] # Tek bir string ise liste içine al
                    else: # Hem parts hem de content yoksa atla
                        current_app.logger.warning(f"GeminiService: Geçmişte içeriksiz mesaj (rol: {role}), atlanıyor.")
                        continue
                
                # parts_content'in liste olduğundan emin ol
                if not isinstance(parts_content, list):
                    parts_content = [str(parts_content)]


                gemini_history_for_api.append({'role': api_role, 'parts': parts_content})

            current_app.logger.debug(f"Gemini API'sine gönderilecek geçmiş: {gemini_history_for_api}")
            current_app.logger.debug(f"Gemini API'sine gönderilecek yeni mesaj: {chat_message}")

            api_response = None
            if gemini_history_for_api:
                chat_session = model.start_chat(history=gemini_history_for_api)
                if chat_message: # Hem geçmiş hem yeni mesaj varsa
                    api_response = chat_session.send_message(chat_message)
                else: # Sadece geçmiş varsa (ve yeni mesaj yoksa)
                    # Bu durumda, Gemini'ye boş bir mesaj göndermek yerine,
                    # son model yanıtını döndürmek veya farklı bir mantık uygulamak gerekebilir.
                    # Şimdilik, eğer son mesaj modelden ise onu döndürelim.
                    if gemini_history_for_api and gemini_history_for_api[-1]['role'] == 'model':
                        last_model_parts = gemini_history_for_api[-1]['parts']
                        # parts bir liste olabilir, tüm metinleri birleştir
                        response_text = "".join(str(p) for p in last_model_parts)
                        current_app.logger.info(f"GeminiService: Yeni mesaj yok, geçmişteki son model yanıtı döndürülüyor.")
                        return {"response": response_text, "status_code": 200}
                    else:
                        # Son mesaj kullanıcıdan ise veya geçmiş boşsa ve yeni mesaj yoksa (bu durum başta yakalanmalı)
                        current_app.logger.info(f"GeminiService: Yeni mesaj yok ve geçmişteki son mesaj modelden değil.")
                        return {"response": "Yeni mesaj gönderilmedi; sadece geçmiş sağlandı.", "status_code": 200} # Veya hata
            elif chat_message: # Sadece yeni mesaj varsa (geçmiş yok)
                api_response = model.generate_content(chat_message)
            else:
                # Bu durum en başta yakalanmalıydı, ama bir güvenlik önlemi olarak.
                current_app.logger.error("GeminiService.send_chat_request: Mantık hatası, hem mesaj hem geçmiş boş.")
                return {"error": "İşlenecek girdi bulunamadı.", "status_code": 400}

            if not api_response: # Eğer yukarıdaki mantıkta bir şekilde api_response None kalırsa
                 current_app.logger.error(f"GeminiService: API yanıtı alınamadı (api_response is None). Model: {target_model_name}")
                 return {"error": "Gemini API'sinden yanıt alınamadı.", "status_code": 500}

            response_text = api_response.text
            current_app.logger.info(f"GeminiService: Model {target_model_name} için Gemini API yanıtı başarıyla alındı.")
            # Kullanım verileri (token sayısı vb.) gerekirse buradan çekilebilir:
            # Örneğin: response.usage_metadata (generate_content için)
            # token_count = model.count_tokens(chat_message or gemini_history_for_api)
            return {"response": response_text, "status_code": 200}

        except Exception as e:
            current_app.logger.error(f"GeminiService: Model {target_model_name} için Gemini API çağrısı sırasında hata: {e}", exc_info=True)
            error_message = str(e)
            # Gemini kütüphanesinden gelen spesifik hata türleri veya kodları varsa burada ayrıştırılabilir.
            return {"error": "Gemini API isteği başarısız oldu.", "details": error_message, "status_code": 500}

# =============================================================================
# 3.0 ÖRNEK KULLANIM (EXAMPLE USAGE)
# =============================================================================
# Bu bölüm, modül doğrudan çalıştırıldığında test amaçlıdır.
# Üretim ortamında bu kısım çalıştırılmamalıdır.
# if __name__ == '__main__':
#     # Flask current_app olmadan çalıştırırken loglama için temel yapılandırma
#     import logging
#     logging.basicConfig(level=logging.DEBUG)
#     # Flask current_app yerine geçecek sahte bir logger oluştur
#     class MockLogger:
#         def info(self, msg): print(f"INFO: {msg}")
#         def warning(self, msg): print(f"WARNING: {msg}")
#         def error(self, msg, exc_info=False): print(f"ERROR: {msg}")
#         def debug(self, msg): print(f"DEBUG: {msg}")
#     current_app = type('obj', (object,), {'logger': MockLogger(), 'debug': True})


#     # API anahtarınızı buraya girin veya ortam değişkeni olarak ayarlayın
#     # TEST_API_KEY = os.getenv("GEMINI_API_KEY_TEST")
#     TEST_API_KEY = "YOUR_GEMINI_API_KEY_HERE" # GERÇEK ANAHTARINIZI GİRİN

#     if TEST_API_KEY == "YOUR_GEMINI_API_KEY_HERE" or not TEST_API_KEY:
#         print("Lütfen `YOUR_GEMINI_API_KEY_HERE` kısmına geçerli bir Gemini API anahtarı girin veya GEMINI_API_KEY_TEST ortam değişkenini ayarlayın.")
#     else:
#         try:
#             # Sahte Model Entity'si
#             class MockModelEntity:
#                 def __init__(self, external_name):
#                     self.external_model_name = external_name
#                     self.name = f"TestModel ({external_name})" # Test için
#                     self.id = 1 # Test için

#             gemini_service = GeminiService(api_key=TEST_API_KEY)
#             test_model = MockModelEntity(external_name='gemini-1.5-flash-latest') # veya 'gemini-pro'

#             # Test 1: Sadece yeni mesaj
#             print("\n--- Test 1: Sadece Yeni Mesaj ---")
#             response1 = gemini_service.send_chat_request(
#                 model_entity=test_model,
#                 chat_message="Merhaba, bana bir şaka anlatır mısın?",
#                 chat_history=[]
#             )
#             print(f"Yanıt 1: {response1}")

#             # Test 2: Geçmiş ve yeni mesaj
#             print("\n--- Test 2: Geçmiş ve Yeni Mesaj ---")
#             history2 = [
#                 {'role': 'user', 'content': 'En sevdiğin renk nedir?'},
#                 {'role': 'assistant', 'content': 'Ben bir yapay zeka olduğum için favori bir rengim yok, ama maviyi severim!'}
#             ]
#             response2 = gemini_service.send_chat_request(
#                 model_entity=test_model,
#                 chat_message="Peki ya en sevdiğin yemek?",
#                 chat_history=history2
#             )
#             print(f"Yanıt 2: {response2}")

#             # Test 3: Sadece geçmiş (son mesaj modelden)
#             print("\n--- Test 3: Sadece Geçmiş (Son Mesaj Modelden) ---")
#             history3 = [
#                 {'role': 'user', 'content': 'Bugün nasılsın?'},
#                 {'role': 'model', 'content': 'Harikayım, size yardımcı olmak için buradayım!'}
#             ]
#             response3 = gemini_service.send_chat_request(
#                 model_entity=test_model,
#                 chat_message=None, # Yeni mesaj yok
#                 chat_history=history3
#             )
#             print(f"Yanıt 3: {response3}")

#             # Test 4: Sadece geçmiş (son mesaj kullanıcıdan)
#             print("\n--- Test 4: Sadece Geçmiş (Son Mesaj Kullanıcıdan) ---")
#             history4 = [
#                 {'role': 'user', 'content': 'Bir soru sorabilir miyim?'}
#             ]
#             response4 = gemini_service.send_chat_request(
#                 model_entity=test_model,
#                 chat_message=None,
#                 chat_history=history4
#             )
#             print(f"Yanıt 4: {response4}") # Bu durumda API'ye gitmemeli, "No new message" gibi bir yanıt vermeli

#             # Test 5: Hatalı rol
#             print("\n--- Test 5: Hatalı Rol ---")
#             history5 = [
#                 {'role': 'system', 'content': 'Bu bir sistem mesajıdır.'}
#             ]
#             response5 = gemini_service.send_chat_request(
#                 model_entity=test_model,
#                 chat_message="Bu mesaj işlenecek mi?",
#                 chat_history=history5
#             )
#             print(f"Yanıt 5: {response5}")


#         except ValueError as e:
#             print(f"Test sırasında yapılandırma hatası: {e}")
#         except Exception as e:
#             print(f"Test sırasında beklenmedik bir hata oluştu: {e}", exc_info=True)
