# =============================================================================
# Temel AI Servisi Modülü (Base AI Service Module) - Dinamik Yükleme ile Revize Edilmiş
# =============================================================================
# Bu modül, farklı AI sağlayıcıları arasında bir soyutlama katmanı görevi görür.
# Gelen AI isteklerini, modelin veritabanındaki `service_provider` alanına
# göre uygun olan spesifik AI servisine dinamik olarak yönlendirir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 BASEAISERVICE SINIFI (BASEAISERVICE CLASS)
#     2.1. __init__                 : Başlatıcı metot.
#     2.2. _get_service_instance    : Sağlayıcı adına ve model ID'sine göre servis örneği getirir/oluşturur.
#     2.3. process_chat_request     : Sohbet isteklerini işler ve yönlendirir.
#     2.4. process_image_request    : Görüntü isteklerini işler (Placeholder).
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Tuple
import importlib # Dinamik import için
import traceback # Hata ayıklama için
import sys # sys.path için (şu an kullanılmıyor ama gelecekte gerekebilir)
import hashlib # API anahtarını hashlemek için

from flask import current_app # Loglama ve uygulama yapılandırmasına erişim için

# Döngüsel bağımlılıkları önlemek için TYPE_CHECKING kullanılır.
if TYPE_CHECKING:
    from app.repositories.model_repository import ModelRepository
    from app.models.entities.model import Model as AIModelEntity # AIModelEntity olarak yeniden adlandırıldı

# =============================================================================
# 2.0 BASEAISERVICE SINIFI (BASEAISERVICE CLASS)
# =============================================================================
class BaseAIService:
    """
    Farklı AI modelleri ve sağlayıcıları için temel istek işleme ve yönlendirme servisi.
    İstekleri, modelin `service_provider` alanına göre dinamik olarak yüklenen
    spesifik AI servisine delege eder.
    """

    # -------------------------------------------------------------------------
    # 2.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, model_repository: 'ModelRepository', config: Dict[str, Any]):
        """
        BaseAIService'i başlatır.

        Args:
            model_repository (ModelRepository): AI model verilerine erişim için depo.
            config (Dict[str, Any]): Flask uygulamasının yapılandırma ayarları.
        """
        self.model_repository: 'ModelRepository' = model_repository
        self.config: Dict[str, Any] = config
        self.service_instances: Dict[Tuple[str, str], Any] = {} # (provider_name, api_key_hash) -> instance

    # -------------------------------------------------------------------------
    # 2.2. Sağlayıcı adına ve model ID'sine göre servis örneği getirir/oluşturur (_get_service_instance)
    # -------------------------------------------------------------------------
    def _get_service_instance(self, service_provider_name: str, model_id: int) -> Any:
        """
        Belirtilen servis sağlayıcı adına ve model ID'sine karşılık gelen AI servis sınıfını
        dinamik olarak yükler, örneğini oluşturur ve döndürür.
        Örnekler, (servis_sağlayıcı_adı, api_anahtarı_hash) anahtarıyla tekrar kullanılmak üzere saklanır.

        Args:
            service_provider_name: AI sağlayıcısının adı (veritabanındaki `service_provider` alanından gelir).
            model_id: Model ID'si, API anahtarını ve diğer model detaylarını almak için kullanılır.

        Returns:
            İlgili AI servisinin bir örneği.

        Raises:
            ValueError: Servis sağlayıcı adı boşsa, model bulunamazsa veya API anahtarı eksikse.
            ImportError: İlgili servis modülü yüklenemezse.
            AttributeError: Servis sınıfı modül içinde bulunamazsa.
            Exception: Servis örneği oluşturulurken bir hata oluşursa.
        """

        if not service_provider_name:
            raise ValueError("Servis sağlayıcı adı (service_provider_name) boş olamaz.")

        model_entity: Optional['AIModelEntity'] = self.model_repository.get_model_by_id(model_id, include_api_key=True)

        if not model_entity:
            raise ValueError(f"Model (ID: {model_id}) bulunamadı.")

        api_key: Optional[str] = getattr(model_entity, 'api_key', None)
        if not api_key:
            model_name_for_log = getattr(model_entity, 'name', f"ID:{model_id}")
            raise ValueError(f"Model '{model_name_for_log}' için API anahtarı (api_key) yapılandırılmamış veya alınamadı.")

        api_key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
        cache_key = (service_provider_name, api_key_hash)

        if cache_key in self.service_instances:
            return self.service_instances[cache_key]

        module_path: Optional[str] = None
        class_name: Optional[str] = None
        try:
            module_name_parts = service_provider_name.split('_')
            class_name_parts = []
            for part in module_name_parts:
                if part.lower() == "ai": class_name_parts.append("AI")
                elif part.lower() == "openai": class_name_parts.append("OpenAI")
                else: class_name_parts.append(part.capitalize())
            class_name = "".join(class_name_parts)
            if not class_name.endswith("Service"):
                class_name += "Service"


            module_path = f"app.services.{service_provider_name}"

            service_module = importlib.import_module(module_path)
            service_class = getattr(service_module, class_name)

            init_args = {}
            import inspect
            sig = inspect.signature(service_class.__init__)
            params = sig.parameters

            if 'api_key' in params: init_args['api_key'] = api_key
            if 'config' in params: init_args['config'] = self.config

            service_instance = service_class(**init_args)

            self.service_instances[cache_key] = service_instance
            return service_instance

        except ImportError as e:
            raise ImportError(f"AI servis modülü '{module_path or service_provider_name}' yüklenemedi: {e}") from e
        except AttributeError as e:
            raise AttributeError(f"AI servis sınıfı '{class_name or 'UnknownClass'}' modül '{module_path or service_provider_name}' içinde bulunamadı: {e}") from e
        except Exception as e:
            raise Exception(f"AI servisi '{class_name or 'UnknownClass'}' başlatılırken bir hata oluştu: {e}") from e

    # -------------------------------------------------------------------------
    # 2.3. Sohbet isteklerini işler ve yönlendirir (process_chat_request)
    # -------------------------------------------------------------------------
    def process_chat_request(self,
                             model_id: str,
                             chat_message: Optional[str],
                             chat_history: List[Dict[str, str]]
                             ) -> Dict[str, Any]:
        """
        Bir sohbet isteğini işler. Model ID'sine göre ilgili AI modelini veritabanından
        alır, modelin `service_provider` alanına göre uygun AI servisini dinamik olarak
        belirler ve isteği o servise yönlendirerek yanıt üretir.
        """
        db_connection_instance: Optional[DatabaseConnection] = None
        try:
            model_id_int: int
            try:
                model_id_int = int(model_id)
            except ValueError:
                return {"error": "Geçersiz model ID formatı.", "status_code": 400}

            model_entity: Optional['AIModelEntity'] = self.model_repository.get_model_by_id(model_id_int)

            if not model_entity:
                return {"error": "Belirtilen AI modeli bulunamadı.", "status_code": 404}

            service_provider_name: Optional[str] = getattr(model_entity, 'service_provider', None)
            if not service_provider_name:
                model_name_for_log = getattr(model_entity, 'name', f"ID:{model_id_int}")
                return {"error": f"Model '{model_name_for_log}' için servis sağlayıcı (service_provider) yapılandırılmamış.", "status_code": 500}

            specific_ai_service = self._get_service_instance(service_provider_name, model_id_int)

            if not hasattr(specific_ai_service, 'send_chat_request'):
                raise AttributeError(f"'{service_provider_name}' servisi sohbet işleme (send_chat_request) desteklemiyor.")


            response_data: Dict[str, Any] = specific_ai_service.send_chat_request(
                model_entity=model_entity,
                chat_message=chat_message,
                chat_history=chat_history
            )

            return response_data

        except (ValueError, ImportError, AttributeError) as e:
            return {"error": "AI servisi yapılandırma veya istek formatı hatası.", "details": str(e), "status_code": 500}
        except Exception as e:
            return {
                "error": "Sohbet isteği işlenirken sunucuda beklenmedik bir hata oluştu.",
                "details": str(e) if current_app.debug else "Daha fazla bilgi için sistem loglarına bakın.",
                "status_code": 500
            }


    # -------------------------------------------------------------------------
    # 2.4. Görüntü isteklerini işler (process_image_request) (Placeholder)
    # -------------------------------------------------------------------------
    def process_image_request(self,
                              model_id: str,
                              prompt: str,
                              image_data: Optional[bytes] = None
                              ) -> Dict[str, Any]:
        """
        Bir görüntü oluşturma veya işleme isteğini işler. (Placeholder)
        Bu metodun, `process_chat_request` benzeri bir dinamik yükleme ve
        yönlendirme mantığına sahip olması beklenir.
        """
        try:
            model_id_int: int
            try:
                model_id_int = int(model_id)
            except ValueError:
                return {"error": "Geçersiz model ID formatı.", "status_code": 400}

            model_entity: Optional['AIModelEntity'] = self.model_repository.get_model_by_id(model_id_int)

            if not model_entity:
                return {"error": "Belirtilen AI görüntü modeli bulunamadı.", "status_code": 404}

            service_provider_name: Optional[str] = getattr(model_entity, 'service_provider', None)
            if not service_provider_name:
                model_name_for_log = getattr(model_entity, 'name', f"ID:{model_id_int}")
                return {"error": f"Model '{model_name_for_log}' için servis sağlayıcı yapılandırılmamış.", "status_code": 500}

            specific_ai_service = self._get_service_instance(service_provider_name, model_id_int)

            if not hasattr(specific_ai_service, 'generate_image_request'):
                return {"error": f"'{service_provider_name}' servisi görüntü işleme (generate_image_request) desteklemiyor.", "status_code": 501}

            return specific_ai_service.generate_image_request(
                model_entity=model_entity,
                prompt=prompt,
                image_data=image_data
            )
        except (ValueError, ImportError, AttributeError) as e:
            return {"error": "AI görüntü servisi yapılandırma hatası.", "details": str(e), "status_code": 500}
        except Exception as e:
            return {"error": "Görüntü isteği işlenirken sunucuda hata.", "details": str(e) if current_app.debug else "Loglara bakın.", "status_code": 500}