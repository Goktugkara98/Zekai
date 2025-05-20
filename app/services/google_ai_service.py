# =============================================================================
# Google AI Servisi Modülü (Google AI Service Module)
# =============================================================================
# Bu modül, Google AI platformu (örn: Gemini API) ile etkileşim kurmak için
# özel servis mantığını içerir. BaseAIService tarafından yönlendirilen
# istekleri işler ve Google'ın AI modellerinden yanıtlar alır.
#
# Ana Sınıf:
#   GoogleAIService: Google AI modelleriyle iletişim kuran servis.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. GoogleAIService Sınıfı
#    2.1. __init__: Başlatıcı metot.
#    2.2. _fill_payload_template: İstek payload'unu konuşma geçmişiyle doldurur.
#    2.3. _extract_response_by_path: JSON yanıttan belirli bir yoldaki veriyi çıkarır.
#    2.4. _generate_mock_response: Test için sahte (mock) yanıt üretir.
#    2.5. send_chat_request: Google AI modeline sohbet isteği gönderir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import requests
import json
import traceback # Hata ayıklama için
from typing import Dict, Any, Optional, List, TYPE_CHECKING, Union

from flask import current_app # Loglama ve uygulama yapılandırmasına erişim için

# Döngüsel bağımlılıkları önlemek için TYPE_CHECKING kullanılır.
if TYPE_CHECKING:
    from app.models.entities.model import Model as AIModelEntity # Model entity'sinin doğru yolu
    from app.repositories.model_repository import ModelRepository

# 2. GoogleAIService Sınıfı
# =============================================================================
class GoogleAIService:
    """
    Google AI modelleri (örneğin Gemini API) için AI Servis uygulaması.
    `BaseAIService` tarafından delege edilen istekleri işler.
    """

    def __init__(self, config: Dict[str, Any], model_repository: 'ModelRepository'):
        """
        GoogleAIService'i başlatır.

        Args:
            config: Flask uygulamasının yapılandırma ayarları.
                    'GOOGLE_API_KEY', 'USE_MOCK_API', 'API_TIMEOUT' gibi
                    anahtarları içerebilir.
            model_repository: AI Model verilerine erişim için depo.
                              (Şu an doğrudan bu serviste aktif olarak kullanılmıyor
                               ancak gelecekteki genişletmeler veya model bazlı
                               özel yapılandırmalar için tutulabilir.)
        """
        self.config: Dict[str, Any] = config
        self.model_repository: 'ModelRepository' = model_repository
        # Genel bir Google API anahtarı uygulama yapılandırmasından alınabilir.
        # Modele özgü API anahtarları ise `model_entity` üzerinden gelecektir.
        self.default_api_key: Optional[str] = self.config.get('GOOGLE_API_KEY')
        current_app.logger.info("GoogleAIService örneği başarıyla başlatıldı.")

    def _fill_payload_template(self,
                               payload_template_str: str,
                               conversation_history: List[Dict[str, str]],
                               current_user_message: Optional[str]
                               ) -> Dict[str, Any]:
        """
        Verilen payload şablonunu (JSON string) konuşma geçmişi ve mevcut kullanıcı
        mesajıyla doldurarak Google Gemini API'sinin beklediği 'contents' formatını oluşturur.

        Args:
            payload_template_str: JSON formatında payload şablonu.
                                  Örn: `{"contents": [], "generationConfig": {"temperature": 0.7}}`
                                  Bu şablondaki "contents" listesi doldurulacaktır.
            conversation_history: Konuşma geçmişi. Her eleman şu formatta bir sözlüktür:
                                  `{"role": "user" | "assistant", "content": "mesaj içeriği"}`.
                                  Gemini için "assistant" rolü "model" olarak çevrilir.
            current_user_message: Kullanıcının en son gönderdiği mesaj (opsiyonel).

        Returns:
            Google Gemini API'sine gönderilmeye hazır, doldurulmuş payload (sözlük olarak).

        Raises:
            ValueError: Eğer `payload_template_str` geçersiz bir JSON ise veya
                        beklenen formatta değilse.
        """
        try:
            # Payload şablonunu JSON'dan Python sözlüğüne çevir
            payload: Dict[str, Any] = json.loads(payload_template_str)
        except json.JSONDecodeError as e:
            current_app.logger.error(f"_fill_payload_template: Payload şablonu JSON parse hatası: {e}. Şablon: '{payload_template_str}'")
            raise ValueError(f"Payload şablonu geçersiz JSON formatında.") from e

        # Gemini API'si için 'contents' listesini oluştur
        gemini_contents: List[Dict[str, Any]] = []
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content")
            if role and content:
                # Gemini API'si 'assistant' yerine 'model' rolünü kullanır.
                gemini_role = "model" if role == "assistant" else role
                gemini_contents.append({"role": gemini_role, "parts": [{"text": content}]})

        if current_user_message:
            # Mevcut kullanıcı mesajını da 'user' rolüyle ekle
            gemini_contents.append({"role": "user", "parts": [{"text": current_user_message}]})

        # Payload içinde "contents" anahtarını bul ve oluşturulan gemini_contents ile güncelle.
        # Eğer şablonda "contents" anahtarı yoksa veya farklı bir yapı bekleniyorsa,
        # bu kısım modelin özel gereksinimlerine göre ayarlanmalıdır.
        # Örn: Bazı modeller şablonda "$messages" gibi bir yer tutucu kullanabilir.
        if "contents" in payload:
            payload["contents"] = gemini_contents
        else:
            # Eğer şablonda 'contents' yoksa, bu bir yapılandırma sorunudur.
            # Ancak, esneklik için, eğer şablon boş bir sözlükse veya
            # eski bir OpenAI formatına benzer şekilde "messages" anahtarı içeriyorsa,
            # 'contents' anahtarını ekleyip 'messages'ı (varsa) silelim.
            current_app.logger.warning(
                "_fill_payload_template: Payload şablonunda 'contents' anahtarı bulunamadı. "
                "Gemini formatı için bu genellikle gereklidir. Şablon: '{payload_template_str}'. "
                "'contents' anahtarı oluşturuluyor."
            )
            payload["contents"] = gemini_contents
            if "messages" in payload: # Eski formatla uyumluluk denemesi
                del payload["messages"]


        # Generation Config (üretim yapılandırması) gibi diğer ayarlar şablondan gelebilir
        # veya burada varsayılan değerlerle zenginleştirilebilir.
        # Örneğin: payload.setdefault("generationConfig", {"temperature": 0.9, "topP": 1.0})
        current_app.logger.debug(f"_fill_payload_template: Doldurulmuş payload: {payload}")
        return payload

    def _extract_response_by_path(self, response_json: Dict[str, Any], path_str: str) -> Optional[str]:
        """
        İç içe bir JSON (Python sözlüğü) nesnesinden, nokta (.) ile ayrılmış bir
        yol (path) string'i kullanarak bir metin değeri çıkarmaya çalışır.
        Örneğin, Gemini API için yaygın bir yol: "candidates.0.content.parts.0.text"

        Args:
            response_json: API'den gelen yanıtın parse edilmiş JSON (Python sözlüğü) hali.
            path_str: Çıkarılacak veriye giden yol (örn: "adaylar.0.icerik.bolumler.0.metin").

        Returns:
            Yoldaki metin değeri veya yol geçersizse/bulunamazsa None.
        """
        try:
            keys = path_str.split('.')
            current_data: Any = response_json
            for key_part in keys:
                if key_part.isdigit(): # Dizi indeksi (örn: "0", "1")
                    index = int(key_part)
                    if not isinstance(current_data, list) or index >= len(current_data):
                        current_app.logger.warning(f"_extract_response_by_path: Yanıt yolu hatası - Geçersiz dizi indeksi. İndeks: {index}, Yol Parçası: '{key_part}', Veri: {current_data}")
                        return None
                    current_data = current_data[index]
                elif isinstance(current_data, dict): # Sözlük anahtarı
                    if key_part not in current_data:
                        current_app.logger.warning(f"_extract_response_by_path: Yanıt yolu hatası - Anahtar bulunamadı. Anahtar: '{key_part}', Veri: {current_data}")
                        return None
                    current_data = current_data[key_part]
                else: # Beklenmedik bir veri tipiyle karşılaşıldı
                    current_app.logger.warning(f"_extract_response_by_path: Yanıt yolu hatası - Beklenmedik veri tipi. Yol Parçası: '{key_part}', Veri Tipi: {type(current_data)}, Veri: {current_data}")
                    return None

            # Son ulaşılan değerin string olup olmadığını kontrol et
            if isinstance(current_data, str):
                return current_data
            elif current_data is not None:
                # Eğer string değilse ama bir değer varsa, string'e çevirmeyi dene ve uyar.
                current_app.logger.warning(f"_extract_response_by_path: Yanıt yoluyla ulaşılan değer string değil, '{type(current_data)}' tipinde. Değer: '{current_data}'. String'e çevriliyor. Yol: '{path_str}'")
                return str(current_data)
            # Eğer current_data None ise (yolun sonunda değer yoksa)
            current_app.logger.info(f"_extract_response_by_path: Yanıt yoluyla ulaşılan değer None. Yol: '{path_str}'")
            return None

        except Exception as e:
            current_app.logger.error(f"_extract_response_by_path: Yanıt ayıklanırken beklenmedik hata: {e}. Yol: '{path_str}', JSON: {response_json}", exc_info=True)
            return None

    def _generate_mock_response(self, user_message: Optional[str], model_name: str) -> str:
        """Geliştirme ve test amaçlı sahte (mock) bir AI yanıtı üretir."""
        message_content = user_message if user_message else "bir mesaj (kullanıcı mesajı boş)"
        return (f"Bu, '{model_name}' modelinden mesajınıza ('{message_content}') verilen SAHTE bir yanıttır. "
                "Gerçek Google AI servisi şu anda mock (taklit) modunda çalışmaktadır.")

    def send_chat_request(self,
                          model_entity: 'AIModelEntity',
                          chat_message: Optional[str],
                          chat_history: List[Dict[str, str]]
                          ) -> Dict[str, Any]:
        """
        Google AI (örn: Gemini) modeline bir sohbet isteği gönderir.

        Args:
            model_entity: Kullanılacak AI modelinin veritabanı entity'si.
                          Bu entity, `api_url`, `api_key` (opsiyonel), `request_method`,
                          `request_headers` (JSON string), `request_body_template` (JSON string),
                          `response_path` gibi alanları içermelidir.
            chat_message: Kullanıcının en son gönderdiği mesaj (opsiyonel).
            chat_history: Önceki konuşma geçmişi.

        Returns:
            Bir sözlük:
            Başarı durumunda: `{"response": "AI'nın cevabı", "raw_response": {...}, "status_code": 200}`
            Hata durumunda: `{"error": "Hata mesajı", "details": "...", "status_code": HTTP_status_kodu}`
        """
        print("\n====GoogleAIService.send_chat_request BAŞLADI====")
        print(f"Parametreler: model_entity={model_entity.name}, chat_message={chat_message}, chat_history_len={len(chat_history)}")
        current_app.logger.info(f"GoogleAIService.send_chat_request: İstek alındı. Model: {model_entity.name} (ID: {model_entity.id})")

        # Model entity'sinden API etkileşimi için gerekli yapılandırma bilgilerini al.
        print("----Model yapılandırma bilgilerini alma----")
        # Bu alanların Model entity'sinde tanımlı olduğunu varsayıyoruz.
        api_url: Optional[str] = getattr(model_entity, 'api_url', None)
        print(f"api_url: {api_url}")
        # API anahtarı: Önce modele özgü olanı, sonra servisin varsayılanını,
        # sonra da genel uygulama yapılandırmasındaki Google API anahtarını dene.
        model_specific_api_key: Optional[str] = getattr(model_entity, 'api_key', None)
        api_key: Optional[str] = model_specific_api_key or self.default_api_key
        print(f"API anahtarı var mı: {api_key is not None}")

        request_method: str = getattr(model_entity, 'request_method', 'POST').upper()
        print(f"request_method: {request_method}")
        # Gemini için yaygın bir yanıt yolu, model yapılandırmasından gelmeli.
        response_path_str: str = getattr(model_entity, 'response_path', "candidates[0].content.parts[0].text")
        print(f"response_path_str: {response_path_str}")

        # `request_headers` ve `request_body_template` alanları veritabanında JSON string
        # olarak saklanıyorsa, burada Python dict/str nesnelerine dönüştürülmeli.
        print("----İstek başlıkları ve gövde şablonu alınıyor----")
        headers_json_str: str = getattr(model_entity, 'request_headers', '{}') # Varsayılan boş JSON objesi
        body_template_json_str: str = getattr(model_entity, 'request_body', '{"contents": []}') # Minimal Gemini şablonu
        print(f"headers_json_str: {headers_json_str}")
        print(f"body_template_json_str: {body_template_json_str}")

        # Temel yapılandırma kontrolleri
        print("----Temel yapılandırma kontrolleri----")
        if not api_url:
            print(f"HATA: Model '{model_entity.name}' için API URL'si yapılandırılmamış")
            current_app.logger.error(f"GoogleAIService: Model '{model_entity.name}' için API URL'si yapılandırılmamış.")
            return {"error": "AI modeli için API URL yapılandırması eksik.", "status_code": 500}

        use_mock_str: str = self.config.get('USE_MOCK_API', 'false').lower()
        print(f"use_mock_str: {use_mock_str}")
        if not api_key and use_mock_str != 'true':
            print(f"HATA: Model '{model_entity.name}' için API anahtarı bulunamadı ve mock mod aktif değil")
            current_app.logger.error(f"GoogleAIService: Model '{model_entity.name}' için API anahtarı bulunamadı ve mock mod aktif değil.")
            return {"error": "AI modeli için API anahtarı eksik.", "status_code": 500}

        # API URL'sine API anahtarını ekle (Google'ın tipik URL formatı için)
        print("----API URL'sine API anahtarını ekleme----")
        # Eğer modelin `api_url` alanı zaten anahtarı içeriyorsa bu adım atlanabilir.
        if api_key and 'generativelanguage.googleapis.com' in api_url and '?key=' not in api_url:
            separator = '&' if '?' in api_url else '?'
            api_url_with_key = f"{api_url}{separator}key={api_key}"
            print("API anahtarı URL'ye eklendi")
        else:
            api_url_with_key = api_url # api_url zaten anahtarı içeriyor olabilir veya anahtar yok (mock mod)
            print("API anahtarı URL'ye eklenmedi (zaten içeriyor veya mock mod)")
        print(f"api_url_with_key: {api_url_with_key}")

        try:
            print("----Request başlıklarını JSON'dan Python dict'ine çevirme----")
            # Request başlıklarını JSON string'den Python dict'ine çevir
            request_headers: Dict[str, str] = json.loads(headers_json_str) \
                if isinstance(headers_json_str, str) else \
                (headers_json_str if isinstance(headers_json_str, dict) else {})
            print(f"request_headers: {request_headers}")
        except json.JSONDecodeError:
            print(f"HATA: request_headers JSON parse hatası. Headers: '{headers_json_str}'")
            current_app.logger.warning(f"GoogleAIService: Model '{model_entity.name}' için request_headers JSON parse hatası. Varsayılan başlıklar kullanılacak. Başlık String: '{headers_json_str}'")
            request_headers = {}

        # POST istekleri için Content-Type başlığını ayarla (eğer yoksa)
        if request_method == 'POST' and "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/json"
            print("Content-Type başlığı eklendi: application/json")

        try:
            print("----_fill_payload_template çağrılıyor----")
            print(f"Parametreler: payload_template_str={body_template_json_str[:50]}..., conversation_history_len={len(chat_history)}, current_user_message={chat_message}")
            # İstek gövdesini (payload) şablondan ve konuşma geçmişinden oluştur
            request_payload = self._fill_payload_template(
                payload_template_str=body_template_json_str,
                conversation_history=chat_history,
                current_user_message=chat_message
            )
            print(f"request_payload oluşturuldu: {json.dumps(request_payload)[:100]}...")
        except ValueError as e: # _fill_payload_template'den gelebilir
            print(f"HATA: Payload oluşturulurken hata: {e}")
            current_app.logger.error(f"GoogleAIService: Payload oluşturulurken hata: {e}. Model: {model_entity.name}")
            return {"error": f"İstek gövdesi (payload) oluşturma hatası: {e}", "status_code": 500}

        # Mock API kullanımı (uygulama yapılandırmasından kontrol edilir)
        if use_mock_str == 'true':
            print("----Mock API kullanılıyor----")
            current_app.logger.info(f"GoogleAIService: Mock API kullanılıyor. Model: {model_entity.name}")
            print("_generate_mock_response çağrılıyor")
            mock_text_response = self._generate_mock_response(chat_message, model_entity.name)
            print(f"mock_text_response: {mock_text_response}")
            # Gemini API'sine benzer bir mock yanıt yapısı
            mock_raw_api_response = {
                "candidates": [{"content": {"parts": [{"text": mock_text_response}], "role": "model"}}]
                # Diğer sahte alanlar eklenebilir (safetyRatings vb.)
            }
            print("Mock yanıt döndürülüyor")
            print("====GoogleAIService.send_chat_request TAMAMLANDI (Mock)====\n")
            return {"response": mock_text_response, "raw_response": mock_raw_api_response, "status_code": 200}

        # Gerçek API çağrısı
        print("----Gerçek API çağrısı yapılıyor----")
        print(f"URL: {api_url_with_key}, Metod: {request_method}")
        print(f"Payload (ilk 100 karakter): {json.dumps(request_payload)[:100]}...")
        print(f"Başlıklar: {request_headers}")
        current_app.logger.debug(f"GoogleAIService: Google AI API isteği gönderiliyor. URL: {api_url_with_key}, Metod: {request_method}, Payload: {json.dumps(request_payload)[:500]}..., Başlıklar: {request_headers}")
        try:
            api_http_response: Optional[requests.Response] = None
            api_timeout: int = self.config.get("API_TIMEOUT", 60) # Saniye cinsinden
            print(f"api_timeout: {api_timeout} saniye")

            if request_method == 'POST':
                print("POST isteği gönderiliyor...")
                api_http_response = requests.post(api_url_with_key, json=request_payload, headers=request_headers, timeout=api_timeout)
            elif request_method == 'GET': # Sohbet için daha az yaygın, ama desteklenebilir
                print("GET isteği gönderiliyor...")
                api_http_response = requests.get(api_url_with_key, params=request_payload, headers=request_headers, timeout=api_timeout)
            else:
                print(f"HATA: Desteklenmeyen HTTP istek metodu: {request_method}")
                current_app.logger.error(f"GoogleAIService: Desteklenmeyen HTTP istek metodu: {request_method}. Model: {model_entity.name}")
                return {"error": f"Desteklenmeyen istek metodu: {request_method}", "status_code": 405} # Method Not Allowed

            http_status_code = api_http_response.status_code
            response_content_text = api_http_response.text # Yanıtı bir kere oku, tekrar tekrar .text çağırma
            print(f"API yanıtı alındı. HTTP Status: {http_status_code}")
            print(f"Yanıt (ilk 100 karakter): '{response_content_text[:100]}...'")

            current_app.logger.debug(f"GoogleAIService: Google AI API yanıtı alındı. Durum: {http_status_code}, Yanıt (ilk 200 karakter): '{response_content_text[:200]}...'")

            if http_status_code >= 400: # İstemci veya sunucu hatası
                print(f"HATA: API hatası alındı. HTTP Status: {http_status_code}")
                current_app.logger.error(f"GoogleAIService: Google AI API Hatası. Durum: {http_status_code}, Yanıt: {response_content_text}")
                print("====GoogleAIService.send_chat_request TAMAMLANDI (HTTP Hata)====\n")
                return {
                    "error": f"AI servisinden hata alındı (HTTP {http_status_code}).",
                    "details": response_content_text, # Hata detayını yanıta ekle
                    "status_code": http_status_code
                }

            # Başarılı yanıtı JSON olarak parse et
            print("----Yanıtı JSON olarak parse etme----")
            try:
                response_json_data: Dict[str, Any] = json.loads(response_content_text)
                print("Yanıt başarıyla JSON olarak parse edildi")
            except json.JSONDecodeError:
                print("HATA: Yanıt JSON formatında değil veya parse edilemedi")
                current_app.logger.error(f"GoogleAIService: Google AI API yanıtı JSON formatında değil veya parse edilemedi. Yanıt: {response_content_text}")
                print("====GoogleAIService.send_chat_request TAMAMLANDI (JSON Parse Hata)====\n")
                return {"error": "AI servisinden gelen yanıt JSON formatında değil.", "details": response_content_text, "status_code": 502} # Bad Gateway

            # İstenen metin verisini yanıttan, belirtilen yola göre ayıkla
            print("----_extract_response_by_path çağrılıyor----")
            print(f"Parametreler: response_path_str={response_path_str}")
            ai_response_text: Optional[str] = self._extract_response_by_path(response_json_data, response_path_str)
            print(f"ai_response_text: {ai_response_text}")

            if ai_response_text is None:
                print("HATA: Yanıt yolundan metin verisi alınamadı")
                current_app.logger.warning(f"GoogleAIService: Yanıt yolundan ('{response_path_str}') metin verisi alınamadı. Tam JSON yanıt: {response_json_data}")
                # Yanıt yolu yanlış olabilir veya API farklı bir formatta yanıt vermiş olabilir.
                print("====GoogleAIService.send_chat_request TAMAMLANDI (Yanıt Yolu Hata)====\n")
                return {"error": "AI yanıtı formatı beklenenden farklı veya beklenen metin verisi boş.", "raw_response": response_json_data, "status_code": 204} # No Content or structure mismatch

            print("Başarılı yanıt işlendi")
            current_app.logger.info(f"GoogleAIService: Başarılı yanıt işlendi. Model: {model_entity.name}")
            print("====GoogleAIService.send_chat_request TAMAMLANDI (Başarılı)====\n")
            return {"response": ai_response_text, "raw_response": response_json_data, "status_code": 200}

        except requests.exceptions.Timeout:
            print("HATA: API isteği zaman aşımına uğradı")
            current_app.logger.error(f"GoogleAIService: Google AI API isteği zaman aşımına uğradı. URL: {api_url_with_key}")
            print("====GoogleAIService.send_chat_request TAMAMLANDI (Timeout)====\n")
            return {"error": "AI servisine yapılan istek zaman aşımına uğradı.", "status_code": 504} # Gateway Timeout
        except requests.exceptions.RequestException as req_err:
            print(f"HATA: API isteği sırasında ağ veya bağlantı hatası: {req_err}")
            current_app.logger.error(f"GoogleAIService: Google AI API isteği sırasında bir ağ veya bağlantı hatası oluştu: {req_err}. URL: {api_url_with_key}")
            print("====GoogleAIService.send_chat_request TAMAMLANDI (RequestException)====\n")
            return {"error": f"AI servisine ulaşılamadı: {req_err}", "status_code": 503} # Service Unavailable
        except Exception as e: # Diğer beklenmedik hatalar
            print(f"HATA: Beklenmedik genel hata: {e}")
            current_app.logger.error(f"GoogleAIService: Sohbet isteği işlenirken beklenmedik genel bir hata oluştu: {e}", exc_info=True)
            # error_details = str(e)
            # if current_app.debug:
            #     error_details += f" | Trace: {traceback.format_exc()}"
            print("====GoogleAIService.send_chat_request TAMAMLANDI (Genel Hata)====\n")
            return {
                "error": "AI isteği işlenirken sunucuda beklenmedik bir hata oluştu.",
                "details": str(e) if current_app.debug else "Sunucu hatası oluştu.", # Prod'da detayı gizle
                # "trace": traceback.format_exc() if current_app.debug else None,
                "status_code": 500 # Internal Server Error
            }
