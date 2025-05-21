# =============================================================================
# OpenAI Servisi Modülü (OpenAI Service Module) - REVİZE EDİLMİŞ
# =============================================================================
# Bu modül, OpenAI API'si (veya OpenAI uyumlu API'ler) ile etkileşim kurmak için
# özel servis mantığını içerir. BaseAIService (veya AIModelService) tarafından
# yönlendirilen istekleri işler ve OpenAI modellerinden yanıtlar alır.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 OPENAISERVICE SINIFI (OPENAISERVICE CLASS)
#     2.1. __init__                     : Başlatıcı metot.
#     2.2. _prepare_openai_messages     : OpenAI API'si için mesaj listesini hazırlar.
#     2.3. _generate_mock_response      : Test için sahte (mock) yanıt üretir.
#     2.4. send_chat_request            : OpenAI modeline sohbet isteği gönderir.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
import json # Bu dosyada doğrudan kullanılmıyor ama gelecekte gerekebilir.
import traceback # Hata ayıklama için
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import httpx # HTTP istekleri için

from openai import OpenAI, APITimeoutError, APIConnectionError, APIStatusError, RateLimitError # OpenAI kütüphanesi ve hataları
from flask import current_app # Loglama ve uygulama yapılandırmasına erişim için

# Döngüsel bağımlılıkları önlemek için TYPE_CHECKING kullanılır.
if TYPE_CHECKING:
    from app.models.entities.model import Model as AIModelEntity

# =============================================================================
# 2.0 OPENAISERVICE SINIFI (OPENAISERVICE CLASS)
# =============================================================================
class OpenAIService:
    """
    OpenAI API'si (veya OpenAI uyumlu API'ler) için AI Servis uygulaması.
    `BaseAIService` (veya `AIModelService`) tarafından delege edilen istekleri işler.
    """

    # -------------------------------------------------------------------------
    # 2.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, api_key: str, config: Dict[str, Any]): # api_key parametresi BaseAIService'ten gelecek
        """
        OpenAIService'i başlatır.

        Args:
            api_key (str): OpenAI API için kullanılacak API anahtarı. Bu, modele özgü anahtardır.
            config (Dict[str, Any]): Flask uygulamasının yapılandırma ayarları.
                                   'USE_MOCK_API', 'API_TIMEOUT_SECONDS' gibi anahtarları içerebilir.
        """
        self.api_key: str = api_key # Modele özgü API anahtarı
        self.config: Dict[str, Any] = config
        current_app.logger.info(f"OpenAIService örneği başarıyla başlatıldı. API Anahtar Uzunluğu: {len(self.api_key) if self.api_key else 'Yok'}")

    # -------------------------------------------------------------------------
    # 2.2. OpenAI API'si için mesaj listesini hazırlar (_prepare_openai_messages)
    # -------------------------------------------------------------------------
    def _prepare_openai_messages(self,
                                 model_entity: 'AIModelEntity',
                                 conversation_history: List[Dict[str, str]],
                                 current_user_message: Optional[str]
                                 ) -> List[Dict[str, str]]:
        """
        OpenAI API'sinin `chat.completions.create` metodu için `messages` listesini hazırlar.
        Modelin `prompt_template` alanı varsa sistem mesajı olarak kullanır.
        """
        messages: List[Dict[str, str]] = []
        system_prompt_content: Optional[str] = getattr(model_entity, 'prompt_template', None)

        if not system_prompt_content and hasattr(model_entity, 'details') and isinstance(model_entity.details, dict):
            system_prompt_content = model_entity.details.get('system_prompt')

        if system_prompt_content:
            # Placeholder'ları işle (varsa)
            # Bu kısım, prompt_template'in nasıl kullanılacağına bağlı olarak daha karmaşık hale gelebilir.
            # Şimdilik, sadece {user_message} placeholder'ını basitçe ele alıyoruz.
            if "{user_message}" in system_prompt_content:
                if not conversation_history and current_user_message: # Sadece ilk mesajsa ve geçmiş yoksa
                    # Bu durumda, sistem mesajı aslında kullanıcı mesajını içeren bir şablondur.
                    # OpenAI'de bu genellikle tek bir 'user' mesajı olarak gönderilir.
                    messages.append({"role": "user", "content": system_prompt_content.format(user_message=current_user_message)})
                    current_user_message = None # İşlendi olarak işaretle
                else: # Geçmiş varsa veya kullanıcı mesajı yoksa, placeholder'ı olduğu gibi bırak veya temizle.
                      # Genellikle, sohbet için sistem prompt'u placeholder içermemeli.
                    clean_system_prompt = system_prompt_content.split("{user_message}")[0].strip()
                    if clean_system_prompt:
                         messages.append({"role": "system", "content": clean_system_prompt})
            else:
                messages.append({"role": "system", "content": system_prompt_content})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant."}) # Varsayılan sistem mesajı

        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content")
            # OpenAI 'model' rolünü 'assistant' olarak bekler.
            api_role = "assistant" if role == "model" else role
            if api_role in ["user", "assistant"] and content:
                messages.append({"role": api_role, "content": content})

        if current_user_message: # Eğer yukarıda işlenmediyse
            messages.append({"role": "user", "content": current_user_message})

        current_app.logger.debug(f"_prepare_openai_messages: Hazırlanan mesajlar (ilk 2): {messages[:2]}")
        return messages

    # -------------------------------------------------------------------------
    # 2.3. Test için sahte (mock) yanıt üretir (_generate_mock_response)
    # -------------------------------------------------------------------------
    def _generate_mock_response(self, user_message: Optional[str], model_name: str) -> str:
        """Geliştirme ve test amaçlı sahte (mock) bir AI yanıtı üretir."""
        message_content = user_message if user_message else "bir mesaj (kullanıcı mesajı boş)"
        return (f"Bu, '{model_name}' modelinden mesajınıza ('{message_content}') verilen SAHTE bir OpenAI yanıtıdır. "
                "Gerçek OpenAI servisi şu anda mock (taklit) modunda çalışmaktadır.")

    # -------------------------------------------------------------------------
    # 2.4. OpenAI modeline sohbet isteği gönderir (send_chat_request)
    # -------------------------------------------------------------------------
    def send_chat_request(self,
                          model_entity: 'AIModelEntity',
                          chat_message: Optional[str],
                          chat_history: List[Dict[str, str]]
                          ) -> Dict[str, Any]:
        """
        OpenAI API'sine (veya uyumlu bir API'ye) bir sohbet isteği gönderir.
        """
        model_name_for_log = getattr(model_entity, 'name', 'Bilinmeyen Model')
        model_id_for_log = getattr(model_entity, 'id', 'Bilinmeyen ID')
        current_app.logger.info(f"OpenAIService.send_chat_request: İstek alındı. Model: {model_name_for_log} (ID: {model_id_for_log})")

        # API anahtarı __init__ içinde self.api_key olarak ayarlandı.
        if not self.api_key: # __init__ içinde kontrol edilmiş olsa da, burada da kontrol etmek iyi bir pratik.
            current_app.logger.error(f"OpenAIService: Model '{model_name_for_log}' için API anahtarı yapılandırılmamış.")
            return {"error": "AI modeli için API anahtarı eksik.", "status_code": 500}

        openai_model_name: Optional[str] = getattr(model_entity, 'external_model_name', None)
        base_url: Optional[str] = getattr(model_entity, 'api_url', None) # OpenAI uyumlu API'ler için

        if not openai_model_name:
            current_app.logger.error(f"OpenAIService: Model '{model_name_for_log}' için harici model adı (external_model_name) yapılandırılmamış.")
            return {"error": "AI modeli için harici model adı (OpenAI model ID) yapılandırması eksik.", "status_code": 500}

        use_mock_str: str = self.config.get('USE_MOCK_API', 'false').lower()
        if use_mock_str == 'true':
            current_app.logger.info(f"OpenAIService: Mock API kullanılıyor. Model: {openai_model_name}")
            mock_text_response = self._generate_mock_response(chat_message, openai_model_name)
            mock_raw_api_response = {
                "choices": [{"message": {"role": "assistant", "content": mock_text_response}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            }
            return {
                "response": mock_text_response,
                "raw_response": mock_raw_api_response,
                "status_code": 200,
                "usage": mock_raw_api_response.get("usage")
            }

        try:
            # httpx.Client için özel transport, başlıkları ASCII uyumlu hale getirmek için
            # Bu, özellikle Türkçe karakterler içeren başlıklar varsa gerekebilir.
            # Ancak, modern HTTP kütüphaneleri genellikle UTF-8 başlıkları doğru işler.
            # Eğer sorun yaşanmıyorsa bu özel transporta gerek olmayabilir.
            class ASCIISafeTransport(httpx.HTTPTransport):
                def handle_request(self, request: httpx.Request) -> httpx.Response:
                    safe_headers = {}
                    for k, v in request.headers.items():
                        safe_k = k.encode('ascii', 'ignore').decode('ascii')
                        safe_v = v.encode('ascii', 'ignore').decode('ascii') if isinstance(v, str) else v
                        safe_headers[safe_k] = safe_v
                    request.headers = httpx.Headers(safe_headers)
                    return super().handle_request(request)

            http_client = httpx.Client(
                # transport=ASCIISafeTransport(), # Gerekirse aktif edin
                headers={"User-Agent": f"ZekaiApp/1.0 ({self.config.get('APP_VERSION', 'unknown')})"} # Uygulama versiyonu eklenebilir
            )
            client = OpenAI(api_key=self.api_key, base_url=base_url, http_client=http_client)
        except Exception as e:
            current_app.logger.error(f"OpenAIService: OpenAI istemcisi başlatılırken hata: {e}", exc_info=True)
            return {"error": "OpenAI API istemcisi başlatılamadı.", "details": str(e), "status_code": 500}

        try:
            messages_for_api = self._prepare_openai_messages(model_entity, chat_history, chat_message)
        except Exception as e:
            current_app.logger.error(f"OpenAIService: Mesajlar hazırlanırken hata: {e}", exc_info=True)
            return {"error": "OpenAI için mesajlar hazırlanırken bir hata oluştu.", "details": str(e), "status_code": 500}

        model_params = getattr(model_entity, 'details', {})
        if not isinstance(model_params, dict): model_params = {} # details dict değilse boş dict yap

        allowed_params = {"temperature", "max_tokens", "top_p", "presence_penalty", "frequency_penalty", "stop", "stream"}
        api_call_params = {k: v for k, v in model_params.items() if k in allowed_params}

        if 'stream' in api_call_params and api_call_params['stream']:
            current_app.logger.warning("OpenAIService: Stream isteği algılandı ancak bu fonksiyon şu anda streaming desteklemiyor. 'stream=False' olarak ayarlanacak.")
            api_call_params['stream'] = False

        current_app.logger.debug(
            f"OpenAIService: OpenAI API isteği gönderiliyor. Model: {openai_model_name}, "
            f"Mesaj sayısı: {len(messages_for_api)}, Ek parametreler: {api_call_params}, Base URL: {base_url}"
        )

        try:
            api_timeout_seconds: float = float(self.config.get("API_TIMEOUT_SECONDS", 60.0))
            completion = client.chat.completions.create(
                model=openai_model_name, # Model adı zaten string olmalı
                messages=messages_for_api, # Mesajlar _prepare_openai_messages içinde hazırlandı
                timeout=api_timeout_seconds,
                **api_call_params
            )

            ai_response_text = completion.choices[0].message.content
            usage_data = completion.usage

            current_app.logger.info(f"OpenAIService: Başarılı yanıt işlendi. Model: {openai_model_name}")
            return {
                "response": ai_response_text,
                "raw_response": completion.model_dump(),
                "status_code": 200,
                "usage": usage_data.model_dump() if usage_data else None
            }
        except APITimeoutError:
            current_app.logger.error(f"OpenAIService: OpenAI API isteği zaman aşımına uğradı. Model: {openai_model_name}")
            return {"error": "AI servisine yapılan istek zaman aşımına uğradı.", "status_code": 504}
        except APIConnectionError as e:
            current_app.logger.error(f"OpenAIService: OpenAI API bağlantı hatası: {e}. Model: {openai_model_name}")
            return {"error": f"AI servisine bağlanılamadı: {e}", "status_code": 503}
        except RateLimitError as e:
            current_app.logger.error(f"OpenAIService: OpenAI API rate limit aşıldı: {e}. Model: {openai_model_name}")
            return {"error": f"AI servisi rate limit hatası: {e}", "details": str(e), "status_code": 429}
        except APIStatusError as e:
            current_app.logger.error(f"OpenAIService: OpenAI API durum hatası: {e}. HTTP Kodu: {e.status_code}, Yanıt: {e.response.text if e.response else 'Yok'}")
            return {
                "error": f"AI servisinden hata alındı (HTTP {e.status_code}).",
                "details": str(e.response.text if e.response else e),
                "status_code": e.status_code
            }
        except Exception as e:
            current_app.logger.error(f"OpenAIService: Sohbet isteği işlenirken beklenmedik genel bir hata oluştu: {e}", exc_info=True)
            return {
                "error": "AI isteği işlenirken sunucuda beklenmedik bir hata oluştu.",
                "details": str(e) if current_app.debug else "Sunucu hatası oluştu.",
                "status_code": 500
            }
