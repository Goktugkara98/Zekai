# =============================================================================
# OpenRouter AI Servisi Modülü (OpenRouter AI Service Module)
# =============================================================================
# Bu modül, OpenRouter platformu üzerinden sunulan çeşitli AI modelleriyle
# etkileşim kurmak için özel servis mantığını içerir. BaseAIService tarafından
# yönlendirilen istekleri işler ve OpenRouter API'sinden yanıtlar alır.
#
# ÖNEMLİ NOTLAR:
# 1. Bu dosya, OpenRouter API etkileşim mantığının tamamlanması gereken
#    bir implementasyondur.
# 2. Bu sınıf, `BaseAIService` sınıfından miras almaktadır. `send_chat_request`
#    metodu, BaseAIService'in beklediği imzaya ve dönüş tipine uygun hale
#    getirilmiştir.
# 3. `_fill_payload_template`, `_extract_response_by_path` ve
#    `_generate_mock_response` gibi yardımcı metotlar bu sınıfta
#    tanımlanmıştır. Bu metotlar, BaseAIService'e taşınabilir veya
#    ortak bir yardımcı modülde yer alabilir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 OPENROUTERAISERVICE SINIFI (OPENROUTERAISERVICE CLASS)
#     2.1. __init__                     : Başlatıcı metot (BaseAIService'ten miras alınır).
#     2.2. _generate_mock_response      : Test için sahte (mock) yanıt üretir.
#     2.3. _fill_payload_template       : OpenRouter API'si için istek gövdesini (payload) hazırlar.
#     2.4. _extract_response_by_path    : JSON yanıttan belirtilen yoldaki veriyi çıkarır.
#     2.5. send_chat_request            : OpenRouter modeline sohbet isteği gönderir.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
import requests
import json
import traceback # Hata ayıklama için
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING

from flask import current_app # Loglama ve uygulama yapılandırmasına erişim için

# BaseAIService'ten miras almak için import.
from app.services.base_ai_service import BaseAIService # TYPE_CHECKING bloğu dışında

if TYPE_CHECKING:
    from app.models.entities.model import Model as AIModelEntity
    # from app.repositories.model_repository import ModelRepository # Genellikle __init__ içinde alınır

# =============================================================================
# 2.0 OPENROUTERAISERVICE SINIFI (OPENROUTERAISERVICE CLASS)
# =============================================================================
class OpenRouterAIService(BaseAIService):
    """
    OpenRouter API'si üzerinden AI modelleriyle etkileşim kurmak için servis.
    Bu sınıf, `BaseAIService`'ten miras alır ve OpenRouter'a özgü
    API çağrılarını ve yanıt işlemeyi yönetir.
    """

    # -------------------------------------------------------------------------
    # 2.1. Başlatıcı metot (__init__)
    #      BaseAIService'ten miras alındığı için `api_key` ve `config` alır.
    #      OpenRouter için özel başlatma parametreleri gerekirse override edilebilir.
    # -------------------------------------------------------------------------
    def __init__(self, api_key: str, config: Dict[str, Any]):
        """
        OpenRouterAIService'i başlatır.

        Args:
            api_key (str): OpenRouter API için kullanılacak API anahtarı.
                           Bu, modele özgü veya genel OpenRouter anahtarı olabilir.
            config (Dict[str, Any]): Flask uygulamasının yapılandırma ayarları.
        """
        super().__init__(model_repository=None, config=config) # type: ignore # BaseAIService model_repository bekliyor, ancak bu alt servis için doğrudan gerekli olmayabilir.
                                                                # BaseAIService._get_service_instance model_repository'yi kullanıyor.
                                                                # Bu servisin doğrudan model_repository'ye ihtiyacı varsa, __init__ imzası güncellenmeli.
        self.api_key: str = api_key # Modele özgü API anahtarı
        # self.openrouter_site_url = self.config.get('OPENROUTER_SITE_URL', self.config.get('APP_SITE_URL')) # Örnek ek konfigürasyon
        current_app.logger.info(f"OpenRouterAIService örneği başarıyla başlatıldı. API Anahtar Uzunluğu: {len(self.api_key) if self.api_key else 'Yok'}")


    # -------------------------------------------------------------------------
    # 2.2. Test için sahte (mock) yanıt üretir (_generate_mock_response)
    # -------------------------------------------------------------------------
    def _generate_mock_response(self, user_message: Optional[str], model_name: str) -> str:
        """
        Geliştirme ve test amaçlı sahte (mock) bir AI yanıtı üretir.
        Bu metot, bu sınıfa özgü veya BaseAIService'e taşınabilir.
        """
        message_content = user_message if user_message else "bir mesaj (kullanıcı mesajı boş)"
        return (f"Bu, '{model_name}' (OpenRouter) modelinden mesajınıza ('{message_content}') "
                f"verilen SAHTE bir yanıttır. Mock mod aktif.")

    # -------------------------------------------------------------------------
    # 2.3. OpenRouter API'si için istek gövdesini (payload) hazırlar (_fill_payload_template)
    # -------------------------------------------------------------------------
    def _fill_payload_template(self,
                               payload_template_str_or_dict: Union[str, Dict[str, Any]],
                               conversation_history: List[Dict[str, str]],
                               current_user_message: Optional[str],
                               openrouter_model_identifier: Optional[str]
                               ) -> Dict[str, Any]:
        """
        OpenRouter API'si için payload şablonunu doldurur.
        'messages' formatını ve 'model' adını ayarlar.
        Bu metot, bu sınıfa özgü veya BaseAIService'e taşınabilir.
        """
        try:
            if isinstance(payload_template_str_or_dict, str) and payload_template_str_or_dict.strip():
                payload = json.loads(payload_template_str_or_dict)
            elif isinstance(payload_template_str_or_dict, dict):
                payload = payload_template_str_or_dict
            else: # Varsayılan boş şablon veya model adına göre temel şablon
                payload = {"model": openrouter_model_identifier or "", "messages": []}
        except json.JSONDecodeError as e:
            current_app.logger.error(f"_fill_payload_template: Payload şablonu geçersiz JSON: {e}. Şablon: {payload_template_str_or_dict}")
            raise ValueError(f"Payload şablonu geçersiz JSON: {e}") from e

        messages = []
        for msg in conversation_history:
            # OpenRouter genellikle 'user' ve 'assistant' rollerini bekler.
            role = msg.get("role")
            api_role = "assistant" if role == "model" else role # 'model' -> 'assistant'
            if api_role in ["user", "assistant", "system"] and msg.get("content"): # OpenRouter 'system' rolünü de destekleyebilir.
                messages.append({"role": api_role, "content": msg.get("content")})

        if current_user_message:
            messages.append({"role": "user", "content": current_user_message})

        payload["messages"] = messages
        if openrouter_model_identifier and ("model" not in payload or not payload.get("model")):
            payload["model"] = openrouter_model_identifier

        return payload

    # -------------------------------------------------------------------------
    # 2.4. JSON yanıttan belirtilen yoldaki veriyi çıkarır (_extract_response_by_path)
    # -------------------------------------------------------------------------
    def _extract_response_by_path(self, response_json: Dict[str, Any], path_str: Optional[str]) -> Optional[str]:
        """
        Verilen JSON yanıtından, nokta ile ayrılmış bir yol (path) kullanarak veri çıkarır.
        Örn: "choices.0.message.content"
        Bu metot, bu sınıfa özgü veya BaseAIService'e taşınabilir.
        """
        if not path_str: # Yol belirtilmemişse veya boşsa
            current_app.logger.warning("_extract_response_by_path: Yanıt yolu (path_str) belirtilmemiş.")
            # Varsayılan olarak, yanıtın kendisini string olarak döndürmeyi deneyebiliriz veya belirli bir anahtarı arayabiliriz.
            # OpenRouter için sıkça 'choices[0].message.content' kullanılır.
            # Bu fonksiyonun daha genel olması için, yol boşsa None döndürmek daha güvenli olabilir.
            return None
        try:
            keys = path_str.split('.')
            current_data: Any = response_json
            for key_part in keys:
                if key_part.isdigit(): # Liste indeksi
                    index = int(key_part)
                    if not isinstance(current_data, list) or index >= len(current_data):
                        current_app.logger.warning(f"_extract_response_by_path: '{path_str}' yolunda '{key_part}' indeksi geçersiz.")
                        return None
                    current_data = current_data[index]
                elif isinstance(current_data, dict): # Sözlük anahtarı
                    if key_part not in current_data:
                        current_app.logger.warning(f"_extract_response_by_path: '{path_str}' yolunda '{key_part}' anahtarı bulunamadı.")
                        return None
                    current_data = current_data[key_part]
                else: # Beklenmeyen veri tipi
                    current_app.logger.warning(f"_extract_response_by_path: '{path_str}' yolunda '{key_part}' beklenmeyen veri tipiyle karşılaşıldı: {type(current_data)}")
                    return None
            return str(current_data) if current_data is not None else None
        except Exception as e:
            current_app.logger.error(f"_extract_response_by_path: Yanıt yolundan ('{path_str}') veri çıkarılırken hata: {e}", exc_info=True)
            return None

    # -------------------------------------------------------------------------
    # 2.5. OpenRouter modeline sohbet isteği gönderir (send_chat_request)
    # -------------------------------------------------------------------------
    def send_chat_request(self,
                          model_entity: 'AIModelEntity',
                          chat_message: Optional[str],
                          chat_history: List[Dict[str, str]]
                          ) -> Dict[str, Any]:
        """
        OpenRouter API'sine bir sohbet isteği gönderir.
        BaseAIService tarafından beklenen imzaya ve dönüş tipine uygun hale getirilmiştir.
        """
        model_name_for_log = getattr(model_entity, 'name', 'Bilinmeyen OpenRouter Modeli')
        model_id_for_log = getattr(model_entity, 'id', 'Bilinmeyen ID')
        current_app.logger.info(f"OpenRouterAIService.send_chat_request: İstek alındı. Model: {model_name_for_log} (ID: {model_id_for_log})")

        # API anahtarı __init__ içinde self.api_key olarak ayarlandı.
        if not self.api_key:
            current_app.logger.error(f"OpenRouterAIService: Model '{model_name_for_log}' için API anahtarı yapılandırılmamış.")
            return {"error": "AI modeli için API anahtarı eksik.", "status_code": 500}

        # OpenRouter'a gönderilecek model adı (örn: "mistralai/mistral-7b-instruct")
        # Bu, model_entity.external_model_name alanında saklanmalıdır.
        openrouter_model_identifier: Optional[str] = getattr(model_entity, 'external_model_name', None)
        if not openrouter_model_identifier:
            current_app.logger.error(f"OpenRouterAIService: Model '{model_name_for_log}' için harici model adı (external_model_name) yapılandırılmamış.")
            return {"error": "AI modeli için harici model adı (OpenRouter model ID) yapılandırması eksik.", "status_code": 500}

        # OpenRouter API URL'si. Model entity'sinden alınır, yoksa varsayılan kullanılır.
        api_url: Optional[str] = getattr(model_entity, 'api_url', None)
        if not api_url: # Varsayılan OpenRouter API URL'si
            api_url = "https://openrouter.ai/api/v1/chat/completions"
            current_app.logger.info(f"OpenRouterAIService: Model için api_url belirtilmemiş, varsayılan kullanılıyor: {api_url}")


        use_mock_str: str = self.config.get('USE_MOCK_API', 'false').lower()
        if use_mock_str == 'true':
            current_app.logger.info(f"OpenRouterAIService: Mock API kullanılıyor. Model: {model_name_for_log}")
            mock_text_response = self._generate_mock_response(chat_message, model_name_for_log)
            mock_raw_api_response = {"mock_response": True, "choices": [{"message": {"content": mock_text_response}}]}
            return {"response": mock_text_response, "raw_response": mock_raw_api_response, "status_code": 200}

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.get('APP_SITE_URL', self.config.get('SERVER_NAME', '')), # Uygulamanızın URL'si
            "X-Title": self.config.get('APP_NAME', 'ZekaiApp') # Uygulamanızın adı
        }
        custom_headers_raw: Optional[Union[str, Dict]] = getattr(model_entity, 'request_headers', None)
        if custom_headers_raw:
            try:
                custom_headers = json.loads(custom_headers_raw) if isinstance(custom_headers_raw, str) else \
                                 (custom_headers_raw if isinstance(custom_headers_raw, dict) else {})
                headers.update(custom_headers)
            except json.JSONDecodeError:
                current_app.logger.warning(f"OpenRouterAIService: Model '{model_name_for_log}' için request_headers JSON parse hatası. Özel başlıklar yoksayıldı.")

        # İstek gövdesi şablonu model_entity.request_body'den alınır.
        body_template_raw: Optional[Union[str, Dict]] = getattr(model_entity, 'request_body', None)
        # Eğer request_body boşsa veya tanımlı değilse, temel bir şablon oluşturulur.
        if not body_template_raw:
            body_template_raw = {} # Boş dict, _fill_payload_template modeli ve mesajları ekleyecek

        request_payload: Dict[str, Any]
        try:
            request_payload = self._fill_payload_template(
                payload_template_str_or_dict=body_template_raw,
                conversation_history=chat_history,
                current_user_message=chat_message,
                openrouter_model_identifier=openrouter_model_identifier
            )
            # Modelden gelen `details` içindeki ek parametreleri payload'a ekle
            # (temperature, max_tokens vb.)
            model_params = getattr(model_entity, 'details', {})
            if isinstance(model_params, dict):
                # Sadece OpenRouter tarafından desteklenen ve güvenli olan parametreleri filtrele
                allowed_openrouter_params = {"temperature", "max_tokens", "top_p", "top_k", "frequency_penalty", "presence_penalty", "stop", "stream", "seed", "user"}
                # "messages" ve "model" zaten _fill_payload_template tarafından eklendi/işlendi.
                for k, v in model_params.items():
                    if k in allowed_openrouter_params and k not in request_payload:
                        request_payload[k] = v
            
            # Stream parametresi özel ele alınmalı
            if request_payload.get('stream', False):
                current_app.logger.warning("OpenRouterAIService: Stream isteği algılandı ancak bu fonksiyon şu anda streaming desteklemiyor. 'stream=False' olarak ayarlanacak.")
                request_payload['stream'] = False


        except ValueError as e:
            error_msg = f"OpenRouter payload oluşturma hatası: {str(e)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg}. Model: {model_name_for_log}")
            return {"error": error_msg, "details": str(e), "status_code": 500}

        current_app.logger.debug(f"OpenRouterAIService: API isteği gönderiliyor. URL: {api_url}, Model ID (OpenRouter): {openrouter_model_identifier}, Payload (ilk 500 krk): {json.dumps(request_payload)[:500]}...")
        try:
            api_timeout: float = float(self.config.get("API_TIMEOUT_SECONDS", 60.0)) # config'den API_TIMEOUT_SECONDS al
            api_http_response = requests.post(api_url, json=request_payload, headers=headers, timeout=api_timeout)
            http_status_code = api_http_response.status_code
            response_content_text = api_http_response.text

            current_app.logger.debug(f"OpenRouterAIService: API yanıtı alındı. Durum: {http_status_code}, Yanıt (ilk 200 krk): '{response_content_text[:200]}...'")

            if http_status_code >= 400:
                current_app.logger.error(f"OpenRouterAIService: API Hatası. Durum: {http_status_code}, Model: {model_name_for_log}, Yanıt: {response_content_text}")
                return {"error": f"OpenRouter API Hatası (HTTP {http_status_code})", "details": response_content_text, "status_code": http_status_code}

            response_json_data: Dict[str, Any] = json.loads(response_content_text)

            response_path_str: Optional[str] = getattr(model_entity, 'response_path', "choices.0.message.content")
            ai_response_text: Optional[str] = self._extract_response_by_path(response_json_data, response_path_str)

            if ai_response_text is None or not ai_response_text.strip():
                warning_msg = f"OpenRouter: Yanıt yolundan ('{response_path_str}') anlamlı metin verisi alınamadı veya boş."
                current_app.logger.warning(f"OpenRouterAIService: {warning_msg} Model: {model_name_for_log}. Tam JSON yanıt: {response_json_data}")
                # Hata durumu yerine, boş yanıtı veya ham yanıtı döndürebiliriz.
                # Kullanıcıya "Anlamlı yanıt alınamadı" demek yerine, belki de API'nin döndürdüğü bir şey vardır.
                return {"response": "", "raw_response": response_json_data, "status_code": 204 if http_status_code < 300 else http_status_code, "details": warning_msg}


            current_app.logger.info(f"OpenRouterAIService: Başarılı yanıt işlendi. Model: {model_name_for_log}")
            # 'usage' verisi varsa ekleyelim
            usage_data = response_json_data.get('usage')
            return {"response": ai_response_text, "raw_response": response_json_data, "status_code": 200, "usage": usage_data}

        except requests.exceptions.Timeout:
            error_msg = "OpenRouter API isteği zaman aşımına uğradı."
            current_app.logger.error(f"OpenRouterAIService: {error_msg} URL: {api_url}, Model: {model_name_for_log}")
            return {"error": error_msg, "details": "Timeout", "status_code": 504} # Gateway Timeout
        except requests.exceptions.RequestException as req_err:
            error_msg = f"OpenRouter API bağlantı hatası: {str(req_err)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg} URL: {api_url}, Model: {model_name_for_log}", exc_info=True)
            return {"error": error_msg, "details": str(req_err), "status_code": 503} # Service Unavailable
        except json.JSONDecodeError as json_err: # Yanıt JSON değilse
            error_msg = f"OpenRouter API yanıtı JSON formatında değil: {str(json_err)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg} Model: {model_name_for_log}. Yanıt: {response_content_text[:200] if 'response_content_text' in locals() else 'Yanıt alınamadı.'}")
            return {"error": error_msg, "details": response_content_text[:200] if 'response_content_text' in locals() else str(json_err) , "status_code": 502} # Bad Gateway
        except Exception as e:
            error_msg = f"OpenRouter servisinde beklenmedik bir hata oluştu: {str(e)}"
            current_app.logger.error(f"OpenRouterAIService: {error_msg} Model: {model_name_for_log}", exc_info=True)
            return {"error": error_msg, "details": str(e) if current_app.debug else "Sunucu hatası.", "status_code": 500}
