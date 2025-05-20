# =============================================================================
# Temel AI Servisi (Base AI Service)
# =============================================================================
# Bu modül, farklı AI sağlayıcıları arasında bir soyutlama katmanı görevi görür.
# Gelen istekleri, modelin sağlayıcı türüne göre uygun AI servisine yönlendirir.
#
# Ana Sınıf:
#   BaseAIService: AI isteklerini işlemek için temel sınıf.
# =============================================================================

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from flask import current_app # Loglama ve yapılandırma erişimi için

# Döngüsel bağımlılıkları önlemek için TYPE_CHECKING kullanılır
if TYPE_CHECKING:
    from app.repositories.model_repository import ModelRepository
    from app.services.google_ai_service import GoogleAIService
    # Diğer AI servisleri eklendikçe buraya import edilecek
    # from app.services.openrouter_ai_service import OpenRouterAIService

# AI Sağlayıcı Türleri için sabitler (veritabanındaki ID'lerle eşleşmeli)
# Bu ID'ler genellikle `Model` entity'nizdeki `provider_type_id` gibi bir alandan gelir.
# Şimdilik manuel olarak tanımlıyoruz, idealde bu bir enum veya config'den gelmeli.
PROVIDER_TYPE_GOOGLE = 1
PROVIDER_TYPE_OPENROUTER = 2 # Örnek olarak eklendi

class BaseAIService:
    """
    Farklı AI modelleri ve sağlayıcıları için temel istek işleme servisi.
    """
    def __init__(self, model_repository: 'ModelRepository', config: Dict[str, Any]):
        """
        BaseAIService'i başlatır.

        Args:
            model_repository (ModelRepository): AI model verilerine erişim için depo.
            config (Dict[str, Any]): Uygulama yapılandırma ayarları.
        """
        self.model_repository = model_repository
        self.config = config
        # Spesifik AI servislerini burada başlatmak yerine, talep üzerine get_service metodu içinde başlatacağız.
        # Bu, gereksiz servis başlatmalarını önler.
        self.service_instances: Dict[int, Any] = {}

    def _get_service_instance(self, provider_type_id: int) -> Any:
        """
        Belirtilen sağlayıcı türü için AI servis örneğini döndürür veya oluşturur.

        Args:
            provider_type_id (int): AI sağlayıcısının tür ID'si.

        Returns:
            Any: İlgili AI servisinin bir örneği.

        Raises:
            ValueError: Desteklenmeyen sağlayıcı türü ID'si için.
        """
        if provider_type_id in self.service_instances:
            return self.service_instances[provider_type_id]

        service_instance = None
        if provider_type_id == PROVIDER_TYPE_GOOGLE:
            from app.services.google_ai_service import GoogleAIService # Gecikmeli import
            # GoogleAIService'in de model_repository ve config'e ihtiyacı olabilir.
            # Veya sadece config'e ve API anahtarı gibi spesifik ayarlara.
            service_instance = GoogleAIService(config=self.config, model_repository=self.model_repository)
            current_app.logger.info("GoogleAIService örneği oluşturuldu.")
        # elif provider_type_id == PROVIDER_TYPE_OPENROUTER:
        #     from app.services.openrouter_ai_service import OpenRouterAIService # Gecikmeli import
        #     service_instance = OpenRouterAIService(config=self.config, model_repository=self.model_repository)
        #     current_app.logger.info("OpenRouterAIService örneği oluşturuldu.")
        else:
            current_app.logger.error(f"Desteklenmeyen AI sağlayıcı türü ID'si: {provider_type_id}")
            raise ValueError(f"Desteklenmeyen AI sağlayıcı türü ID'si: {provider_type_id}")
        
        self.service_instances[provider_type_id] = service_instance
        return service_instance

    def process_chat_request(self, model_id: str, chat_message: Optional[str], chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Bir sohbet isteğini işler, uygun AI modelini ve servisini kullanarak yanıt üretir.

        Args:
            model_id (str): Kullanılacak AI modelinin ID'si.
            chat_message (Optional[str]): Kullanıcının en son gönderdiği mesaj. Boş olabilir eğer sadece geçmiş ile devam ediliyorsa.
            chat_history (List[Dict[str, str]]): Önceki konuşma geçmişi. 
                                                 Format: [{"role": "user/assistant", "content": "mesaj"}].

        Returns:
            Dict[str, Any]: AI tarafından üretilen yanıtı veya bir hata mesajını içeren bir sözlük.
                            Başarılı yanıt formatı: {"response": "AI cevabı", "chat_id": "varsa_chat_id"}
                            Hata formatı: {"error": "hata mesajı", "details": "...", "status_code": http_status_kodu}
        """
        current_app.logger.info(f"Sohbet isteği işleniyor: model_id={model_id}, message='{chat_message is not None}', history_len={len(chat_history)}")

        try:
            # 1. Model detaylarını veritabanından al
            # ModelRepository'nin get_by_id metodu Model objesi veya None döndürmeli.
            # Model entity'nizde provider_type_id gibi bir alan olmalı.
            model_entity = self.model_repository.get_by_id(int(model_id)) # ID'yi int'e çevir
            
            if not model_entity:
                current_app.logger.error(f"Model bulunamadı: ID={model_id}")
                return {"error": "Belirtilen AI modeli bulunamadı.", "status_code": 404}

            # Model entity'sinden sağlayıcı türü ID'sini al.
            # Bu alanın adının `provider_type_id` olduğunu varsayıyoruz. Model.py'nizi kontrol edin.
            # Eğer böyle bir alan yoksa, şimdilik varsayılan olarak Google'ı (1) kullanabiliriz.
            provider_type_id = getattr(model_entity, 'provider_type_id', None)

            if provider_type_id is None:
                # Eğer provider_type_id modelde tanımlı değilse ve sadece Google ile çalışıyorsak:
                if int(model_id) == 1: # Veya model_entity.name == "Gemini Pro" gibi bir kontrol
                    provider_type_id = PROVIDER_TYPE_GOOGLE
                    current_app.logger.warning(f"Model {model_id} için provider_type_id bulunamadı, varsayılan olarak Google ({PROVIDER_TYPE_GOOGLE}) kullanılıyor.")
                else:
                    current_app.logger.error(f"Model {model_id} için sağlayıcı türü (provider_type_id) tanımlanmamış.")
                    return {"error": f"Model {model_id} için sağlayıcı türü yapılandırılmamış.", "status_code": 500}
            
            # 2. AI sağlayıcı türüne göre uygun servisi seç
            # Şimdilik sadece Google AI (provider_type_id = 1) destekleniyor.
            if provider_type_id == PROVIDER_TYPE_GOOGLE:
                ai_service = self._get_service_instance(PROVIDER_TYPE_GOOGLE)
                
                # 3. İsteği spesifik AI servisine gönder
                # GoogleAIService'in send_chat_request gibi bir metodu olmalı.
                # Bu metod model_entity, chat_message, chat_history gibi parametreler almalı.
                response_data = ai_service.send_chat_request(
                    model_entity=model_entity,
                    chat_message=chat_message,
                    chat_history=chat_history
                )
                # response_data'nın yapısı GoogleAIService tarafından belirlenir.
                # Örneğin: {"response": "...", "raw_response": {...}, "status_code": 200}
                # Veya hata durumunda: {"error": "...", "details": "...", "status_code": 500}
                return response_data
            # elif provider_type_id == PROVIDER_TYPE_OPENROUTER:
            #     ai_service = self._get_service_instance(PROVIDER_TYPE_OPENROUTER)
            #     response_data = ai_service.send_chat_request(
            #         model_entity=model_entity,
            #         chat_message=chat_message,
            #         chat_history=chat_history
            #     )
            #     return response_data
            else:
                current_app.logger.error(f"Model {model_id} için desteklenmeyen sağlayıcı türü: {provider_type_id}")
                return {"error": f"Model {model_id} için belirtilen AI sağlayıcı türü ({provider_type_id}) desteklenmiyor.", "status_code": 501}

        except ValueError as ve: # _get_service_instance'dan gelebilir
            current_app.logger.error(f"Servis örneği alınırken hata: {ve}", exc_info=True)
            return {"error": "AI servisi yapılandırma hatası.", "details": str(ve), "status_code": 500}
        except Exception as e:
            current_app.logger.error(f"Sohbet isteği işlenirken genel hata: {e}", exc_info=True)
            import traceback
            return {
                "error": "Sohbet isteği işlenirken sunucuda beklenmedik bir hata oluştu.",
                "details": str(e),
                "trace": traceback.format_exc(),
                "status_code": 500
            }

    def process_image_request(self, model_id: str, prompt: str, image_data: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Bir görüntü oluşturma veya işleme isteğini işler. (Gelecekteki kullanım için placeholder)

        Args:
            model_id (str): Kullanılacak AI modelinin ID'si.
            prompt (str): Görüntü oluşturma veya işleme için metin istemi.
            image_data (Optional[bytes]): Varsa, işlenecek görüntü verisi.

        Returns:
            Dict[str, Any]: Oluşturulan görüntünün URL'sini/verisini veya bir hata mesajını içeren sözlük.
        """
        current_app.logger.info(f"Görüntü isteği işleniyor: model_id={model_id}, prompt='{prompt[:50]}...'")
        # Bu metod, ilgili AI servisinin görüntü işleme yeteneklerini çağıracaktır.
        # Şimdilik implemente edilmedi.
        return {"error": "Görüntü işleme henüz desteklenmiyor.", "status_code": 501}

# Diğer temel servis fonksiyonları buraya eklenebilir.
