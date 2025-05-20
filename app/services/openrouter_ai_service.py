# =============================================================================
# OpenRouter AI Servisi Modülü (OpenRouter AI Service Module)
# =============================================================================
# Bu modül, OpenRouter platformu üzerinden sunulan çeşitli AI modelleriyle
# etkileşim kurmak için özel servis mantığını içerir. BaseAIService tarafından
# yönlendirilen istekleri işler ve OpenRouter API'sinden yanıtlar alır.
#
# ÖNEMLİ NOTLAR:
# 1. Bu dosya şu anda büyük ölçüde bir placeholder (yer tutucu) implementasyonudur
#    ve OpenRouter API etkileşim mantığının tamamlanması gerekmektedir.
# 2. Bu sınıf, `BaseAIService` sınıfından miras almaktadır. Ancak, `handle_chat`
#    metodu, `BaseAIService`'in alt servislerden beklediği `send_chat_request`
#    metoduyla aynı imzaya ve dönüş tipine sahip değildir. Entegrasyon için
#    bu durumun ele alınması gerekir.
# 3. Bu sınıf, `self._fill_payload_template`, `self._extract_response_by_path` ve
#    `self._generate_mock_response` gibi metotları çağırmaktadır. Bu metotlar
#    `BaseAIService`'te tanımlı değildir (GoogleAIService'te özel olarak bulunurlar).
#    Bu çağrıların çalışabilmesi için bu metotların ya `BaseAIService`'e
#    taşınması, ya bu sınıfta yeniden implemente edilmesi ya da ortak bir
#    yardımcı modülden çağrılması gerekmektedir.
#
# Ana Sınıf:
#   OpenRouterAIService: OpenRouter API'si ile iletişim kuran servis.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. OpenRouterAIService Sınıfı
#    2.1. __init__: (BaseAIService'ten miras alınır)
#    2.2. handle_chat: OpenRouter modeline sohbet isteği gönderir (TODO: Tamamlanacak).
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import requests
import json
import traceback # Hata ayıklama için
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

from flask import current_app # Loglama ve uygulama yapılandırmasına erişim için

# BaseAIService'ten miras almak için import.
# TYPE_CHECKING bloğu dışında bırakıldı çünkü doğrudan miras alınıyor.
from app.services.base_ai_service import BaseAIService

if TYPE_CHECKING:
    from app.models.entities.model import Model as AIModelEntity
    from app.repositories.model_repository import ModelRepository
    # config ve model_repository __init__ içinde BaseAIService tarafından alınır.

# 2. OpenRouterAIService Sınıfı
# =============================================================================
class OpenRouterAIService(BaseAIService):
    """
    OpenRouter API'si üzerinden AI modelleriyle etkileşim kurmak için servis.
    Bu sınıf, `BaseAIService`'ten miras alır ve OpenRouter'a özgü
    API çağrılarını ve yanıt işlemeyi yönetir.

    Not: Bu sınıfın `__init__` metodu `BaseAIService`'ten miras alınır,
    bu nedenle `config` ve `model_repository` özelliklerine sahiptir.
    """

    # TODO: Eğer OpenRouter için özel başlatma parametreleri veya
    #       varsayılan değerler gerekiyorsa __init__ metodu override edilebilir.
    # def __init__(self, config: Dict[str, Any], model_repository: 'ModelRepository'):
    #     super().__init__(config, model_repository)
    #     self.openrouter_site_url = self.config.get('OPENROUTER_SITE_URL', 'YOUR_APP_URL') # Örnek
    #     current_app.logger.info("OpenRouterAIService örneği başarıyla başlatıldı.")


    # NOT: Aşağıdaki _generate_mock_response, _fill_payload_template ve
    # _extract_response_by_path metotları BaseAIService'te tanımlı DEĞİLDİR.
    # Bu metotların ya BaseAIService'e eklenmesi, ya burada implemente edilmesi
    # ya da OpenRouter'a özel versiyonlarının oluşturulması gerekmektedir.
    # Geçici olarak, bu metotların var olduğu varsayımıyla kod bırakılmıştır,
    # ancak bu durum çalışma zamanı hatalarına yol açacaktır.

    def _generate_mock_response(self, user_message: Optional[str], model_name: str) -> str:
        """
        Geliştirme ve test amaçlı sahte (mock) bir AI yanıtı üretir.
        Bu metodun BaseAIService'e taşınması veya burada implemente edilmesi gerekir.
        """
        current_app.logger.warning("_generate_mock_response çağrıldı ancak BaseAIService'te tanımlı değil. Bu bir placeholder.")
        message_content = user_message if user_message else "bir mesaj (kullanıcı mesajı boş)"
        return (f"Bu, '{model_name}' (OpenRouter) modelinden mesajınıza ('{message_content}') "
                f"verilen SAHTE bir yanıttır. Mock mod aktif.")

    def _fill_payload_template(self,
                               payload_template_str: str,
                               conversation_history: List[Dict[str, str]],
                               current_user_message: Optional[str]
                               ) -> Dict[str, Any]:
        """
        Payload şablonunu doldurur. OpenRouter için 'messages' formatı beklenir.
        Bu metodun BaseAIService'e taşınması veya burada implemente edilmesi gerekir.
        """
        current_app.logger.warning("_fill_payload_template çağrıldı ancak BaseAIService'te tanımlı değil. Bu bir placeholder.")
        try:
            payload = json.loads(payload_template_str) if isinstance(payload_template_str, str) else \
                      (payload_template_str if isinstance(payload_template_str, dict) else {})
        except json.JSONDecodeError as e:
            raise ValueError(f"Payload şablonu geçersiz JSON: {e}") from e

        messages = []
        for msg in conversation_history:
            messages.append({"role": msg.get("role"), "content": msg.get("content")})
        if current_user_message:
            messages.append({"role": "user", "content": current_user_message})

        # OpenRouter genellikle payload'da "model" ve "messages" alanlarını bekler.
        # Şablonun bu yapıyı desteklediği varsayılır.
        # Örnek: payload_template = {"model": "mistralai/mistral-7b-instruct", "messages": []}
        if "messages" in payload:
            payload["messages"] = messages
        elif "contents" in payload: # Gemini tarzı bir şablon varsa OpenRouter'a uyarla
            payload["messages"] = messages
            del payload["contents"]
        else: # Şablonda ne 'messages' ne de 'contents' varsa, 'messages'ı ekle
            payload["messages"] = messages
        return payload

    def _extract_response_by_path(self, response_json: Dict[str, Any], path_str: str) -> Optional[str]:
        """
        JSON yanıttan veri çıkarır.
        Bu metodun BaseAIService'e taşınması veya burada implemente edilmesi gerekir.
        """
        current_app.logger.warning("_extract_response_by_path çağrıldı ancak BaseAIService'te tanımlı değil. Bu bir placeholder.")
        try:
            keys = path_str.split('.')
            current_data: Any = response_json
            for key_part in keys:
                if key_part.isdigit():
                    index = int(key_part)
                    if not isinstance(current_data, list) or index >= len(current_data): return None
                    current_data = current_data[index]
                elif isinstance(current_data, dict):
                    if key_part not in current_data: return None
                    current_data = current_data[key_part]
                else: return None
            return str(current_data) if current_data is not None else None
        except Exception:
            return None

    def handle_chat(self,
                    user_message: Optional[str],
                    conversation_history: List[Dict[str, str]],
                    model_details: Dict[str, Any], # Normalde model_entity olmalı
                    # chat_id: str, # Bu parametre orijinal kodda vardı, ancak BaseAIService'in arayüzüne uymuyor.
                    use_mock_api: bool # Bu da config'den gelmeli
                   ) -> Tuple[str, Dict[str, Any], int, Dict[str, Any], str]:
        """
        OpenRouter AI modeline bir sohbet isteği gönderir.
        NOT: Bu metodun imzası ve dönüş tipi, `BaseAIService`'in beklediği
             `send_chat_request` metodundan farklıdır. Entegrasyon için uyum sağlanmalıdır.

        Args:
            user_message: Kullanıcının en son mesajı (opsiyonel).
            conversation_history: Önceki konuşma geçmişi.
            model_details: Kullanılacak AI modelinin detaylarını içeren sözlük.
                           Normalde bu bir `AIModelEntity` nesnesi olmalıdır.
                           `api_url`, `api_key`, `request_body_template`, `response_path`
                           ve OpenRouter için spesifik model adı (`openrouter_model_name` gibi)
                           alanlarını içermelidir.
            use_mock_api: Mock API'nin kullanılıp kullanılmayacağını belirten boolean.
                          Bu genellikle `self.config` üzerinden yönetilmelidir.

        Returns:
            Bir tuple: (
                ai_yanit_metni: str,
                ham_api_yaniti: Dict[str, Any],
                http_durum_kodu: int,
                istek_payload_logu: Dict[str, Any],
                log_icin_model_adi: str
            )
            Bu dönüş tipi, BaseAIService'in beklediği `Dict[str, Any]` formatından farklıdır.
        """
        # `model_details` yerine `model_entity: 'AIModelEntity'` kullanılmalı ve
        # `use_mock_api` `self.config` üzerinden alınmalıdır.
        # Bu metodun adı `send_chat_request` olmalı ve dönüş tipi
        # `Dict[str, Any]` (örn: {"response": "...", "status_code": 200}) olmalıdır.

        model_name_for_log: str = model_details.get('name', 'OpenRouter Modeli (Yapılandırma Eksik)')
        # OpenRouter'a gönderilecek gerçek model adı (örn: "mistralai/mistral-7b-instruct")
        # Bu, `model_details` içinde `openrouter_model_name` gibi özel bir alanda saklanmalı.
        openrouter_model_identifier: Optional[str] = model_details.get('openrouter_model_name', model_details.get('name'))


        current_app.logger.info(f"OpenRouterAIService.handle_chat: İstek alındı. Model: {model_name_for_log}")

        # Mock API kullanımı (config'den kontrol edilmeli)
        # `use_mock_api` parametresi yerine `self.config.get('USE_MOCK_API', 'false').lower() == 'true'` kullanılmalı.
        if use_mock_api or self.config.get('USE_MOCK_API', 'false').lower() == 'true':
            current_app.logger.info(f"OpenRouterAIService: Mock API kullanılıyor. Model: {model_name_for_log}")
            mock_text_response = self._generate_mock_response(user_message, model_name_for_log)
            mock_raw_api_response = {"mock_response": True, "choices": [{"message": {"content": mock_text_response}}]}
            # BaseAIService uyumlu dönüş:
            # return {"response": mock_text_response, "raw_response": mock_raw_api_response, "status_code": 200}
            return mock_text_response, mock_raw_api_response, 200, {}, model_name_for_log # Orijinal dönüş tipi

        # --- TODO: OpenRouter API Etkileşim Mantığını Tamamla ---
        current_app.logger.warning(f"OpenRouterAIService.handle_chat: OpenRouter API etkileşim mantığı henüz tam olarak implemente edilmemiştir. Bu bir placeholder'dır. Model: {model_name_for_log}")

        api_url: Optional[str] = model_details.get('api_url') # Örn: "https://openrouter.ai/api/v1/chat/completions"
        api_key: Optional[str] = model_details.get('api_key') # Model_details'ten veya self.config'den alınabilir

        if not api_url or not api_key:
            error_msg = "OpenRouter API yapılandırma hatası: API URL veya API Anahtarı eksik."
            current_app.logger.error(f"OpenRouterAIService: {error_msg} Model: {model_name_for_log}")
            # BaseAIService uyumlu dönüş:
            # return {"error": error_msg, "status_code": 500}
            return error_msg, {"error_details": error_msg}, 500, {}, model_name_for_log # Orijinal dönüş

        # HTTP Başlıklarını Hazırla
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # OpenRouter için gerekli olabilecek diğer başlıklar:
            # "HTTP-Referer": self.config.get('APP_SITE_URL', ''), # Uygulamanızın URL'si
            # "X-Title": self.config.get('APP_NAME', '') # Uygulamanızın adı
        }
        # Modelden gelen özel başlıkları ekle (eğer varsa ve JSON string ise parse et)
        custom_headers_str: Optional[Union[str, Dict]] = model_details.get('request_headers')
        if custom_headers_str:
            try:
                custom_headers = json.loads(custom_headers_str) if isinstance(custom_headers_str, str) else \
                                 (custom_headers_str if isinstance(custom_headers_str, dict) else {})
                headers.update(custom_headers)
            except json.JSONDecodeError:
                current_app.logger.warning(f"OpenRouterAIService: Model '{model_name_for_log}' için request_headers JSON parse hatası. Özel başlıklar yoksayıldı.")

        # İstek Gövdesi Şablonunu (Request Body Template) Hazırla ve Doldur
        # OpenRouter genellikle payload'da 'model' (örn: "mistralai/mistral-7b-instruct") ve 'messages' alanlarını bekler.
        # `model_details.request_body_template` bu yapıya uygun olmalıdır.
        # Örnek şablon: `{"model": "MODEL_PLACEHOLDER", "messages": []}`
        body_template_raw: Optional[Union[str, Dict]] = model_details.get('request_body_template')
        body_template_str: str = json.dumps(body_template_raw) if isinstance(body_template_raw, dict) else \
                                 (body_template_raw if isinstance(body_template_raw, str) else \
                                  f'{{"model": "{openrouter_model_identifier}", "messages": []}}') # Varsayılan şablon

        request_payload: Dict[str, Any]
        try:
            # _fill_payload_template, 'messages' anahtarını dolduracak şekilde ayarlanmalı.
            # Ayrıca, OpenRouter'a gönderilecek 'model' adını da payload'a eklemeli.
            # Bu, _fill_payload_template içinde veya burada ayrıca yapılabilir.
            interim_payload = self._fill_payload_template(
                payload_template_str=body_template_str,
                conversation_history=conversation_history, # user_message zaten eklenecekse burada None olabilir
                current_user_message=user_message
            )
            # OpenRouter model tanımlayıcısını payload'a ekle (eğer şablonda yoksa)
            if "model" not in interim_payload and openrouter_model_identifier:
                interim_payload["model"] = openrouter_model_identifier
            elif "model" in interim_payload and not interim_payload["model"] and openrouter_model_identifier:
                 interim_payload["model"] = openrouter_model_identifier


            request_payload = interim_payload
        except ValueError as e:
            error_msg = f"OpenRouter payload oluşturma hatası: {str(e)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg}. Model: {model_name_for_log}")
            # BaseAIService uyumlu dönüş:
            # return {"error": error_msg, "status_code": 500}
            return error_msg, {"error_details": str(e)}, 500, {}, model_name_for_log # Orijinal dönüş

        # HTTP POST İsteğini Yap
        current_app.logger.debug(f"OpenRouterAIService: API isteği gönderiliyor. URL: {api_url}, Model ID (OpenRouter): {openrouter_model_identifier}, Payload (ilk 500 krk): {json.dumps(request_payload)[:500]}...")
        try:
            api_http_response = requests.post(api_url, json=request_payload, headers=headers, timeout=self.config.get("API_TIMEOUT", 45))
            http_status_code = api_http_response.status_code
            response_content_text = api_http_response.text # Yanıtı bir kere oku

            current_app.logger.debug(f"OpenRouterAIService: API yanıtı alındı. Durum: {http_status_code}, Yanıt (ilk 200 krk): '{response_content_text[:200]}...'")

            if http_status_code >= 400: # İstemci veya sunucu hatası
                current_app.logger.error(f"OpenRouterAIService: API Hatası. Durum: {http_status_code}, Model: {model_name_for_log}, Yanıt: {response_content_text}")
                # BaseAIService uyumlu dönüş:
                # return {"error": f"OpenRouter API Hatası (HTTP {http_status_code})", "details": response_content_text, "status_code": http_status_code}
                return f"OpenRouter API Hatası (HTTP {http_status_code})", {"error_details": response_content_text}, http_status_code, request_payload, model_name_for_log

            response_json_data: Dict[str, Any] = json.loads(response_content_text)

            # Yanıt Metnini Çıkar
            # OpenRouter için yaygın yanıt yolu: "choices[0].message.content"
            response_path_str: str = model_details.get('response_path', "choices.0.message.content")
            ai_response_text: Optional[str] = self._extract_response_by_path(response_json_data, response_path_str)

            if ai_response_text is None or not ai_response_text.strip():
                warning_msg = f"OpenRouter: Yanıt yolundan ('{response_path_str}') anlamlı metin verisi alınamadı veya boş."
                current_app.logger.warning(f"OpenRouterAIService: {warning_msg} Model: {model_name_for_log}. Tam JSON yanıt: {response_json_data}")
                ai_response_text = "AI modelinden anlamlı bir yanıt alınamadı." # Kullanıcıya gösterilecek mesaj
                # BaseAIService uyumlu dönüş:
                # return {"error": warning_msg, "raw_response": response_json_data, "status_code": 204 if http_status_code < 300 else http_status_code }
                return ai_response_text, response_json_data, 204 if http_status_code < 300 else http_status_code, request_payload, model_name_for_log


            current_app.logger.info(f"OpenRouterAIService: Başarılı yanıt işlendi. Model: {model_name_for_log}")
            # BaseAIService uyumlu dönüş:
            # return {"response": ai_response_text, "raw_response": response_json_data, "status_code": 200}
            return ai_response_text, response_json_data, 200, request_payload, model_name_for_log

        except requests.exceptions.HTTPError as http_err: # raise_for_status() tarafından fırlatılır
            error_text = http_err.response.text if http_err.response is not None else "No response body"
            status_code_from_err = http_err.response.status_code if http_err.response is not None else 500
            current_app.logger.error(f"OpenRouterAIService: API HTTP Hatası. Durum: {status_code_from_err}, Model: {model_name_for_log}, Hata: {error_text}", exc_info=True)
            return f"OpenRouter API Hatası (HTTP {status_code_from_err})", {"error_details": error_text}, status_code_from_err, request_payload, model_name_for_log
        except requests.exceptions.Timeout:
            error_msg = "OpenRouter API isteği zaman aşımına uğradı."
            current_app.logger.error(f"OpenRouterAIService: {error_msg} URL: {api_url}, Model: {model_name_for_log}")
            return error_msg, {"error_details": "Timeout"}, 504, request_payload, model_name_for_log
        except requests.exceptions.RequestException as req_err: # Diğer bağlantı hataları
            error_msg = f"OpenRouter API bağlantı hatası: {str(req_err)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg} URL: {api_url}, Model: {model_name_for_log}", exc_info=True)
            return error_msg, {"error_details": str(req_err)}, 503, request_payload, model_name_for_log
        except Exception as e: # Diğer beklenmedik hatalar
            error_msg = f"OpenRouter servisinde beklenmedik bir hata oluştu: {str(e)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg} Model: {model_name_for_log}", exc_info=True)
            return error_msg, {"error_details": str(e), "trace": traceback.format_exc() if current_app.debug else None}, 500, request_payload, model_name_for_log
        # --- OpenRouter API Etkileşim Mantığının Sonu ---

# =============================================================================
# Bu modüle eklenebilecek diğer OpenRouter'a özgü servis fonksiyonları
# (örn: görüntü oluşturma, embedding vb.) buraya gelebilir.
# =============================================================================
