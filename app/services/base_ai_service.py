# =============================================================================
# Temel AI Servisi Modülü (Base AI Service Module)
# =============================================================================
# Bu modül, farklı AI sağlayıcıları (örn: Google, OpenRouter) arasında bir
# soyutlama katmanı görevi görür. Gelen AI isteklerini, modelin
# yapılandırmasına göre uygun olan spesifik AI servisine yönlendirir.
#
# Ana Sınıf:
#   BaseAIService: AI isteklerini işlemek ve yönlendirmek için temel sınıf.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Sabitler ve Global Değişkenler (Constants & Globals)
# 3. BaseAIService Sınıfı
#    3.1. __init__: Başlatıcı metot.
#    3.2. _get_service_instance: Sağlayıcı türüne göre servis örneği getirir/oluşturur.
#    3.3. process_chat_request: Sohbet isteklerini işler ve yönlendirir.
#    3.4. process_image_request: Görüntü isteklerini işler (gelecek için placeholder).
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Type
import traceback # Hata ayıklama için

from flask import current_app # Loglama ve uygulama yapılandırmasına erişim için

# Döngüsel bağımlılıkları önlemek için TYPE_CHECKING kullanılır.
# Bu bloktaki importlar sadece tip denetimi sırasında çalışır, çalışma zamanında değil.
if TYPE_CHECKING:
    from app.repositories.model_repository import ModelRepository
    from app.services.google_ai_service import GoogleAIService
    # Diğer AI servisleri eklendikçe buraya import edilecek
    # from app.services.openrouter_ai_service import OpenRouterAIService
    # from app.models.entities.model import Model as AIModelEntity

# 2. Sabitler ve Global Değişkenler (Constants & Globals)
# =============================================================================
# AI Sağlayıcı Türleri için sabitler.
# Bu ID'ler, veritabanındaki AI modellerinin `provider_type_id` gibi bir
# alanıyla eşleşmelidir. İdealde, bu bir enum veya merkezi bir yapılandırma
# dosyasından (config) gelmelidir.
PROVIDER_TYPE_GOOGLE: int = 1
PROVIDER_TYPE_OPENROUTER: int = 2 # Örnek olarak eklendi
# Diğer sağlayıcı türleri buraya eklenebilir.

# 3. BaseAIService Sınıfı
# =============================================================================
class BaseAIService:
    """
    Farklı AI modelleri ve sağlayıcıları için temel istek işleme ve yönlendirme servisi.
    Bu sınıf, gelen bir isteği, modelin sağlayıcı türüne göre uygun olan
    spesifik bir AI servisine (örn: GoogleAIService) delege eder.
    """

    def __init__(self, model_repository: 'ModelRepository', config: Dict[str, Any]):
        """
        BaseAIService'i başlatır.

        Args:
            model_repository (ModelRepository): AI model verilerine erişim için depo (repository).
            config (Dict[str, Any]): Flask uygulamasının yapılandırma ayarları.
        """
        self.model_repository: 'ModelRepository' = model_repository
        self.config: Dict[str, Any] = config
        # Spesifik AI servislerinin örneklerini talep üzerine (lazy loading) oluşturmak
        # için bir sözlük tutulur. Bu, gereksiz yere tüm servislerin başlatılmasını önler.
        self.service_instances: Dict[int, Any] = {}
        current_app.logger.info("BaseAIService örneği başarıyla başlatıldı.")

    def _get_service_instance(self, provider_type_id: int) -> Any:
        """
        Belirtilen sağlayıcı türü ID'sine karşılık gelen AI servis örneğini döndürür.
        Eğer örnek daha önce oluşturulmamışsa, yenisini oluşturur ve saklar.

        Args:
            provider_type_id: AI sağlayıcısının tür ID'si (örn: PROVIDER_TYPE_GOOGLE).

        Returns:
            İlgili AI servisinin bir örneği (örn: GoogleAIService).

        Raises:
            ValueError: Eğer `provider_type_id` desteklenmeyen bir değere sahipse.
        """
        if provider_type_id in self.service_instances:
            current_app.logger.debug(f"_get_service_instance: Sağlayıcı ID {provider_type_id} için mevcut servis örneği kullanılıyor.")
            return self.service_instances[provider_type_id]

        current_app.logger.info(f"_get_service_instance: Sağlayıcı ID {provider_type_id} için yeni servis örneği oluşturulacak.")
        service_instance: Optional[Any] = None

        if provider_type_id == PROVIDER_TYPE_GOOGLE:
            # Gecikmeli import (lazy import) ile döngüsel bağımlılıklar önlenir.
            from app.services.google_ai_service import GoogleAIService
            # GoogleAIService, kendi yapılandırması ve bağımlılıkları ile başlatılır.
            # Genellikle config ve model_repository gibi nesnelere ihtiyaç duyabilir.
            service_instance = GoogleAIService(config=self.config, model_repository=self.model_repository)
            current_app.logger.info("GoogleAIService örneği başarıyla oluşturuldu ve saklandı.")
        # elif provider_type_id == PROVIDER_TYPE_OPENROUTER:
        #     from app.services.openrouter_ai_service import OpenRouterAIService # Gecikmeli import
        #     service_instance = OpenRouterAIService(config=self.config, model_repository=self.model_repository)
        #     current_app.logger.info("OpenRouterAIService örneği başarıyla oluşturuldu ve saklandı.")
        # Diğer AI sağlayıcıları için benzer bloklar buraya eklenebilir.
        else:
            current_app.logger.error(f"_get_service_instance: Desteklenmeyen AI sağlayıcı türü ID'si: {provider_type_id}")
            raise ValueError(f"Desteklenmeyen AI sağlayıcı türü ID'si: {provider_type_id}")

        self.service_instances[provider_type_id] = service_instance
        return service_instance

    def process_chat_request(self,
                             model_id: str,
                             chat_message: Optional[str],
                             chat_history: List[Dict[str, str]]
                             ) -> Dict[str, Any]:
        """
        Bir sohbet isteğini işler. Model ID'sine göre ilgili AI modelini veritabanından
        alır, modelin sağlayıcı türüne göre uygun AI servisini belirler ve isteği
        o servise yönlendirerek yanıt üretir.

        Args:
            model_id: Kullanılacak AI modelinin ID'si (string olarak gelir, int'e çevrilir).
            chat_message: Kullanıcının en son gönderdiği mesaj. Eğer sadece konuşma
                          geçmişi ile devam ediliyorsa (örn: "devam et" komutu) None olabilir.
            chat_history: Önceki konuşma geçmişi. Her bir eleman şu formatta bir sözlüktür:
                          `{"role": "user" | "assistant", "content": "mesaj içeriği"}`.

        Returns:
            AI tarafından üretilen yanıtı veya bir hata mesajını içeren bir sözlük.
            Başarılı yanıt formatı (örnek):
                `{"response": "AI'nın cevabı", "chat_id": "opsiyonel_sohbet_id", "status_code": 200}`
            Hata yanıt formatı (örnek):
                `{"error": "Hata mesajı", "details": "Ek hata detayı", "status_code": HTTP_status_kodu}`
        """
        print("\n====BaseAIService.process_chat_request BAŞLADI====")
        print(f"Parametreler: model_id={model_id}, chat_message={chat_message}, chat_history_len={len(chat_history)}")
        current_app.logger.info(
            f"process_chat_request: Sohbet isteği işleniyor. Model ID: {model_id}, "
            f"Mesaj var mı: {chat_message is not None}, Geçmiş uzunluğu: {len(chat_history)}"
        )

        try:
            # 1. Model ID'sini integer'a çevir
            print("----Model ID'sini integer'a çevirme----")
            try:
                model_id_int = int(model_id)
                print(f"model_id_int: {model_id_int}")
            except ValueError:
                print(f"HATA: Geçersiz model ID formatı: {model_id}")
                current_app.logger.error(f"process_chat_request: Geçersiz model ID formatı: {model_id}. Sayısal olmalı.")
                return {"error": "Geçersiz model ID formatı.", "status_code": 400} # Bad Request

            # 2. Model detaylarını veritabanından al
            print("----Model detaylarını veritabanından alma----")
            print(f"model_repository.get_model_by_id({model_id_int}) çağrılıyor")
            # ModelRepository.get_model_by_id (veya get_by_id) bir Model entity nesnesi veya None döndürmeli.
            # Bu entity, `provider_type_id` gibi bir alan içermelidir.
            model_entity: Optional['AIModelEntity'] = self.model_repository.get_model_by_id(model_id_int) # API key'e burada gerek yok
            print(f"model_entity: {model_entity}")

            if not model_entity:
                print(f"HATA: Model bulunamadı. ID: {model_id_int}")
                current_app.logger.error(f"process_chat_request: Model bulunamadı. ID: {model_id_int}")
                return {"error": "Belirtilen AI modeli bulunamadı.", "status_code": 404} # Not Found

            # 3. Model entity'sinden sağlayıcı türü ID'sini al
            print("----Sağlayıcı türü ID'sini alma----")
            # Bu alanın adının `provider_type_id` olduğunu varsayıyoruz.
            # Model entity tanımınızı (örn: app/models/entities/model.py) kontrol edin.
            provider_type_id: Optional[int] = getattr(model_entity, 'provider_type_id', None)
            print(f"provider_type_id: {provider_type_id}")

            if provider_type_id is None:
                print(f"HATA: Model {model_entity.name} için provider_type_id tanımlanmamış")
                # Geçici çözüm: Eğer provider_type_id modelde tanımlı değilse,
                # ve sadece Google ile çalışıyorsak, varsayılan olarak Google'ı kullan.
                # Bu, model verilerinin eksik olduğu durumlar için bir fallback olabilir,
                # ancak idealde her modelin bir sağlayıcı türü olmalıdır.
                # Örnek: if model_entity.name.startswith("Gemini"): provider_type_id = PROVIDER_TYPE_GOOGLE
                current_app.logger.warning(
                    f"process_chat_request: Model {model_entity.name} (ID: {model_id_int}) için 'provider_type_id' alanı "
                    f"tanımlanmamış veya None. Bu model için sağlayıcı türü belirlenemiyor."
                )
                # Bu durumu nasıl ele alacağınız projenizin gereksinimlerine bağlıdır.
                # Şimdilik, hata döndürelim.
                # Alternatif olarak, varsayılan bir sağlayıcı atanabilir:
                # provider_type_id = PROVIDER_TYPE_GOOGLE # Varsayılan atama
                # current_app.logger.info(f"Varsayılan sağlayıcı ({provider_type_id}) atandı.")
                return {"error": f"Model '{model_entity.name}' için sağlayıcı türü yapılandırılmamış.", "status_code": 500} # Internal Server Error

            # 4. AI sağlayıcı türüne göre uygun servisi çağır
            print("----Uygun AI servisini alma----")
            print(f"_get_service_instance({provider_type_id}) çağrılıyor")
            specific_ai_service = self._get_service_instance(provider_type_id)
            print(f"specific_ai_service: {specific_ai_service.__class__.__name__}")

            # 5. İsteği spesifik AI servisine gönder
            print("====Spesifik AI servisine istek gönderiliyor====")
            print(f"specific_ai_service.send_chat_request çağrılıyor")
            print(f"Parametreler: model_entity={model_entity.name}, chat_message={chat_message}, chat_history_len={len(chat_history)}")
            # Her spesifik AI servisinin (örn: GoogleAIService) `send_chat_request`
            # adında bir metodu olmalı ve bu metot model_entity, chat_message, chat_history
            # gibi parametreleri almalıdır.
            current_app.logger.debug(
                f"process_chat_request: İstek, sağlayıcı ID {provider_type_id} için "
                f"{specific_ai_service.__class__.__name__} servisine yönlendiriliyor."
            )
            response_data: Dict[str, Any] = specific_ai_service.send_chat_request(
                model_entity=model_entity,
                chat_message=chat_message,
                chat_history=chat_history
            )
            print(f"send_chat_request yanıtı: {response_data}")
            print("====Spesifik AI servisinden yanıt alındı====")
            # response_data'nın yapısı (başarı ve hata durumları için) spesifik servis
            # tarafından belirlenir ve HTTP status kodunu içermelidir.
            # Örneğin: {"response": "...", "raw_response": {...}, "status_code": 200}
            # Veya hata: {"error": "...", "details": "...", "status_code": 500}
            current_app.logger.info(
                f"process_chat_request: {specific_ai_service.__class__.__name__} servisinden yanıt alındı. "
                f"Status: {response_data.get('status_code', 'Belirtilmemiş')}"
            )
            print("====BaseAIService.process_chat_request TAMAMLANDI====\n")
            return response_data

        except ValueError as ve: # _get_service_instance'dan veya int(model_id)'den gelebilir
            current_app.logger.error(f"process_chat_request: Değer hatası oluştu: {str(ve)}", exc_info=True)
            return {"error": "AI servisi yapılandırma veya istek formatı hatası.", "details": str(ve), "status_code": 400 if "model ID" in str(ve) else 500}
        except Exception as e:
            current_app.logger.error(f"process_chat_request: Sohbet isteği işlenirken genel ve beklenmedik bir hata oluştu: {str(e)}", exc_info=True)
            # Geliştirme ortamında traceback'i yanıta eklemek faydalı olabilir.
            # error_details = str(e)
            # if current_app.debug:
            #     error_details += f" | Trace: {traceback.format_exc()}"
            return {
                "error": "Sohbet isteği işlenirken sunucuda beklenmedik bir hata oluştu.",
                "details": str(e) if current_app.debug else "Daha fazla bilgi için sistem loglarına bakın.", # Prod'da detayı gizle
                # "trace": traceback.format_exc() if current_app.debug else None, # Sadece debug modunda
                "status_code": 500 # Internal Server Error
            }

    def process_image_request(self,
                              model_id: str,
                              prompt: str,
                              image_data: Optional[bytes] = None
                              ) -> Dict[str, Any]:
        """
        Bir görüntü oluşturma veya işleme isteğini işler.
        Bu metod, gelecekteki kullanım için bir placeholder (yer tutucu) olarak eklenmiştir.
        Görüntü işleme yetenekleri eklendiğinde implemente edilecektir.

        Args:
            model_id: Kullanılacak AI modelinin ID'si.
            prompt: Görüntü oluşturma veya işleme için metin tabanlı istem (prompt).
            image_data: Eğer mevcutsa, işlenecek görüntü verisi (byte dizisi olarak).
                        Örneğin, bir görüntü düzenleme modeli için.

        Returns:
            Oluşturulan görüntünün URL'sini/verisini veya bir hata mesajını içeren bir sözlük.
            Şu an için her zaman desteklenmediğine dair bir hata döndürür.
        """
        current_app.logger.info(
            f"process_image_request: Görüntü isteği alındı. Model ID: {model_id}, "
            f"Prompt (ilk 50 karakter): '{prompt[:50]}...'"
        )
        # Bu metod, modelin sağlayıcı türüne göre ilgili AI servisinin
        # görüntü işleme/oluşturma yeteneklerini (örn: `generate_image` metodu) çağıracaktır.
        # Şimdilik implemente edilmemiştir.
        #
        # Örnek Akış:
        # 1. model_id ile model_entity'yi al.
        # 2. provider_type_id'yi belirle.
        # 3. _get_service_instance ile ilgili servisi al.
        # 4. Servisin görüntü işleme metodunu çağır:
        #    `response = specific_ai_service.generate_image(model_entity, prompt, image_data)`
        # 5. Yanıtı formatla ve döndür.

        return {"error": "Görüntü işleme özelliği henüz bu serviste desteklenmiyor.", "status_code": 501} # Not Implemented

# =============================================================================
# Diğer temel AI servis fonksiyonları (örn: metin özetleme, çeviri vb. için
# genel yönlendirme metodları) buraya eklenebilir.
# =============================================================================
