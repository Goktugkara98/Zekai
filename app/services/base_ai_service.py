# =============================================================================
# İyileştirilmiş Temel AI Servisi Modülü (Improved Base AI Service Module)
# =============================================================================
# Bu modül, farklı AI sağlayıcıları arasında bir soyutlama katmanı görevi görür.
# Connection pooling, caching ve error handling iyileştirmeleri eklenmiştir.
#
# İYİLEŞTİRMELER:
# - Connection pooling eklendi
# - Service instance caching optimize edildi
# - Error handling iyileştirildi
# - Logging sistemi eklendi
# - Performance monitoring
# =============================================================================

import importlib
import logging
import hashlib
import time
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Tuple
from datetime import datetime, timedelta
from threading import Lock

if TYPE_CHECKING:
    from app.repositories.model_repository import ModelRepository
    from app.models.entities.model import Model as AIModelEntity

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

# =============================================================================
# SERVICE CACHE MANAGER
# =============================================================================
class ServiceCacheManager:
    """AI servis instance'larını yöneten cache manager"""
    
    def __init__(self, max_cache_size: int = 50, cache_ttl_hours: int = 24):
        self.cache = {}
        self.cache_timestamps = {}
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Cache'den servis instance'ını al"""
        with self._lock:
            if key not in self.cache:
                return None
                
            # TTL kontrolü
            if datetime.utcnow() - self.cache_timestamps[key] > self.cache_ttl:
                logger.debug(f"Cache expired for key: {key}")
                self._remove_key(key)
                return None
                
            return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Cache'e servis instance'ını ekle"""
        with self._lock:
            # Cache boyut kontrolü
            if len(self.cache) >= self.max_cache_size:
                self._evict_oldest()
                
            self.cache[key] = value
            self.cache_timestamps[key] = datetime.utcnow()
            logger.debug(f"Cached service instance: {key}")
    
    def _remove_key(self, key: str) -> None:
        """Cache'den key'i kaldır"""
        if key in self.cache:
            del self.cache[key]
        if key in self.cache_timestamps:
            del self.cache_timestamps[key]
    
    def _evict_oldest(self) -> None:
        """En eski cache entry'sini kaldır"""
        if not self.cache_timestamps:
            return
            
        oldest_key = min(self.cache_timestamps.keys(), 
                        key=lambda k: self.cache_timestamps[k])
        logger.debug(f"Evicting oldest cache entry: {oldest_key}")
        self._remove_key(oldest_key)
    
    def clear(self) -> None:
        """Cache'i temizle"""
        with self._lock:
            self.cache.clear()
            self.cache_timestamps.clear()
            logger.info("Service cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache istatistiklerini döndür"""
        with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_cache_size,
                "keys": list(self.cache.keys()),
                "oldest_entry": min(self.cache_timestamps.values()) if self.cache_timestamps else None
            }

# =============================================================================
# IMPROVED BASE AI SERVICE CLASS
# =============================================================================
class BaseAIService:
    """
    Farklı AI modelleri ve sağlayıcıları için geliştirilmiş temel istek işleme servisi.
    """

    def __init__(self, model_repository: 'ModelRepository', config: Dict[str, Any]):
        """
        BaseAIService'i başlatır.

        Args:
            model_repository (ModelRepository): AI model verilerine erişim için depo.
            config (Dict[str, Any]): Flask uygulamasının yapılandırma ayarları.
        """
        self.model_repository = model_repository
        self.config = config
        
        # Cache manager'ı başlat
        cache_config = config.get('AI_SERVICE_CACHE', {})
        self.cache_manager = ServiceCacheManager(
            max_cache_size=cache_config.get('max_size', 50),
            cache_ttl_hours=cache_config.get('ttl_hours', 24)
        )
        
        # Performance tracking
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }
        
        logger.info("BaseAIService initialized with improved caching and monitoring")

    def _generate_cache_key(self, service_provider_name: str, api_key: str) -> str:
        """
        Cache key oluşturur.
        
        Args:
            service_provider_name: Servis sağlayıcı adı
            api_key: API anahtarı
            
        Returns:
            str: Cache key
        """
        api_key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:16]
        return f"{service_provider_name}_{api_key_hash}"

    def _get_service_instance(self, service_provider_name: str, model_id: int) -> Any:
        """
        Belirtilen servis sağlayıcı adına ve model ID'sine karşılık gelen AI servis sınıfını
        dinamik olarak yükler, örneğini oluşturur ve döndürür.

        Args:
            service_provider_name: AI sağlayıcısının adı
            model_id: Model ID'si

        Returns:
            İlgili AI servisinin bir örneği.

        Raises:
            ValueError: Servis sağlayıcı adı boşsa, model bulunamazsa veya API anahtarı eksikse.
            ImportError: İlgili servis modülü yüklenemezse.
            AttributeError: Servis sınıfı modül içinde bulunamazsa.
            Exception: Servis örneği oluşturulurken bir hata oluşursa.
        """
        start_time = time.time()
        
        try:
            if not service_provider_name:
                raise ValueError("Servis sağlayıcı adı (service_provider_name) boş olamaz.")

            # Model entity'sini al
            model_entity: Optional['AIModelEntity'] = self.model_repository.get_model_by_id(
                model_id, include_api_key=True
            )

            if not model_entity:
                raise ValueError(f"Model (ID: {model_id}) bulunamadı.")

            api_key: Optional[str] = getattr(model_entity, 'api_key', None)
            if not api_key:
                model_name_for_log = getattr(model_entity, 'name', f"ID:{model_id}")
                raise ValueError(f"Model '{model_name_for_log}' için API anahtarı yapılandırılmamış.")

            # Cache key oluştur
            cache_key = self._generate_cache_key(service_provider_name, api_key)
            
            # Cache'den kontrol et
            cached_instance = self.cache_manager.get(cache_key)
            if cached_instance:
                logger.debug(f"Service instance found in cache: {service_provider_name}")
                return cached_instance

            # Yeni instance oluştur
            logger.debug(f"Creating new service instance: {service_provider_name}")
            
            # Module ve class adlarını belirle
            module_path, class_name = self._resolve_service_module_and_class(service_provider_name)
            
            # Modülü yükle
            service_module = importlib.import_module(module_path)
            service_class = getattr(service_module, class_name)

            # Constructor parametrelerini hazırla
            init_args = self._prepare_service_init_args(service_class, api_key)
            
            # Instance oluştur
            service_instance = service_class(**init_args)
            
            # Cache'e ekle
            self.cache_manager.set(cache_key, service_instance)
            
            creation_time = time.time() - start_time
            logger.info(f"Service instance created: {service_provider_name} (took {creation_time:.3f}s)")
            
            return service_instance

        except ImportError as e:
            raise ImportError(f"AI servis modülü '{service_provider_name}' yüklenemedi: {e}") from e
        except AttributeError as e:
            raise AttributeError(f"AI servis sınıfı bulunamadı: {e}") from e
        except Exception as e:
            raise Exception(f"AI servisi '{service_provider_name}' başlatılırken hata: {e}") from e

    def _resolve_service_module_and_class(self, service_provider_name: str) -> Tuple[str, str]:
        """
        Servis sağlayıcı adından module path ve class name'i çıkarır.
        
        Args:
            service_provider_name: Servis sağlayıcı adı
            
        Returns:
            Tuple[str, str]: (module_path, class_name)
        """
        # Özel mapping'ler
        special_mappings = {
            'google_gemini_ai': ('app.services.gemini_service_improved', 'GeminiService'),
            'gemini': ('app.services.gemini_service_improved', 'GeminiService'),
            'openai': ('app.services.openai_service', 'OpenAIService'),
            'openrouter_ai': ('app.services.openrouter_ai_service', 'OpenrouterAiService')
        }
        
        if service_provider_name in special_mappings:
            return special_mappings[service_provider_name]
        
        # Genel naming convention
        module_name_parts = service_provider_name.split('_')
        class_name_parts = []
        
        for part in module_name_parts:
            if part.lower() == "ai":
                class_name_parts.append("AI")
            elif part.lower() == "openai":
                class_name_parts.append("OpenAI")
            else:
                class_name_parts.append(part.capitalize())
        
        class_name = "".join(class_name_parts)
        if not class_name.endswith("Service"):
            class_name += "Service"
        
        module_path = f"app.services.{service_provider_name}"
        
        return module_path, class_name

    def _prepare_service_init_args(self, service_class: type, api_key: str) -> Dict[str, Any]:
        """
        Servis sınıfının constructor parametrelerini hazırlar.
        
        Args:
            service_class: Servis sınıfı
            api_key: API anahtarı
            
        Returns:
            Dict: Constructor parametreleri
        """
        import inspect
        
        init_args = {}
        sig = inspect.signature(service_class.__init__)
        params = sig.parameters

        if 'api_key' in params:
            init_args['api_key'] = api_key
        if 'config' in params:
            init_args['config'] = self.config

        return init_args

    def process_chat_request(self,
                           model_id: int,
                           chat_message: Optional[str],
                           chat_history: List[Dict[str, str]]
                           ) -> Dict[str, Any]:
        """
        Bir sohbet isteğini işler.
        """
        request_start_time = time.time()
        self.request_stats['total_requests'] += 1
        
        try:
            # Model ID validation
            try:
                model_id_int = int(model_id)
            except ValueError:
                self.request_stats['failed_requests'] += 1
                return {"error": "Geçersiz model ID formatı.", "status_code": 400}

            # Model entity'sini al
            model_entity: Optional['AIModelEntity'] = self.model_repository.get_model_by_id(model_id_int)

            if not model_entity:
                self.request_stats['failed_requests'] += 1
                return {"error": "Belirtilen AI modeli bulunamadı.", "status_code": 404}

            # Servis sağlayıcıyı belirle
            service_provider_name: Optional[str] = getattr(model_entity, 'service_provider', None)
            if not service_provider_name:
                model_name_for_log = getattr(model_entity, 'name', f"ID:{model_id_int}")
                self.request_stats['failed_requests'] += 1
                return {
                    "error": f"Model '{model_name_for_log}' için servis sağlayıcı yapılandırılmamış.",
                    "status_code": 500
                }

            logger.info(f"Processing chat request - Model: {model_id_int}, Provider: {service_provider_name}")

            # Servis instance'ını al
            specific_ai_service = self._get_service_instance(service_provider_name, model_id_int)

            # Servis metodunu kontrol et
            if not hasattr(specific_ai_service, 'send_chat_request'):
                self.request_stats['failed_requests'] += 1
                raise AttributeError(f"'{service_provider_name}' servisi sohbet işleme desteklemiyor.")

            # Chat request'i gönder
            response_data: Dict[str, Any] = specific_ai_service.send_chat_request(
                model_entity=model_entity,
                chat_message=chat_message,
                chat_history=chat_history
            )

            # Response time'ı hesapla ve istatistikleri güncelle
            response_time = time.time() - request_start_time
            self._update_stats(response_time, success=True)

            logger.info(f"Chat request completed - Response time: {response_time:.3f}s")
            
            return response_data

        except (ValueError, ImportError, AttributeError) as e:
            response_time = time.time() - request_start_time
            self._update_stats(response_time, success=False)
            
            logger.error(f"Chat request configuration error: {str(e)}")
            return {
                "error": "AI servisi yapılandırma hatası.",
                "details": str(e),
                "status_code": 500
            }
            
        except Exception as e:
            response_time = time.time() - request_start_time
            self._update_stats(response_time, success=False)
            
            logger.error(f"Unexpected error in chat request: {str(e)}", exc_info=True)
            return {
                "error": "Sohbet isteği işlenirken beklenmedik bir hata oluştu.",
                "details": str(e) if self.config.get('DEBUG') else "Sistem loglarına bakın.",
                "status_code": 500
            }

    def _update_stats(self, response_time: float, success: bool) -> None:
        """
        İstatistikleri günceller.
        
        Args:
            response_time: Yanıt süresi
            success: İstek başarılı mı
        """
        if success:
            self.request_stats['successful_requests'] += 1
        else:
            self.request_stats['failed_requests'] += 1
        
        # Average response time güncelle
        total_requests = self.request_stats['total_requests']
        current_avg = self.request_stats['average_response_time']
        self.request_stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Servis istatistiklerini döndürür.
        
        Returns:
            Dict: İstatistik bilgileri
        """
        cache_stats = self.cache_manager.get_stats()
        
        return {
            "request_stats": self.request_stats.copy(),
            "cache_stats": cache_stats,
            "success_rate": (
                self.request_stats['successful_requests'] / 
                max(self.request_stats['total_requests'], 1) * 100
            )
        }

    def clear_cache(self) -> None:
        """Cache'i temizler."""
        self.cache_manager.clear()
        logger.info("BaseAIService cache cleared")

    def process_image_request(self,
                            model_id: str,
                            prompt: str,
                            image_data: Optional[bytes] = None
                            ) -> Dict[str, Any]:
        """
        Görüntü oluşturma veya işleme isteğini işler.
        """
        # Bu metod gelecekte implement edilecek
        return {
            "error": "Görüntü işleme henüz desteklenmiyor.",
            "status_code": 501
        }

