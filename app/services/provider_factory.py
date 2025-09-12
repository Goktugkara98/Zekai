# =============================================================================
# PROVIDER FACTORY
# =============================================================================
# Bu dosya, provider türüne göre uygun servisi döndürür.
# =============================================================================

import logging
from typing import Dict, Any, Optional
from app.services.gemini_service import GeminiService
from app.services.openrouter_service import OpenRouterService

logger = logging.getLogger(__name__)

class ProviderFactory:
    """
    Provider türüne göre uygun servisi döndüren factory sınıfı
    """
    
    _services = {}
    
    @classmethod
    def get_service(cls, provider_type: str, **kwargs) -> Optional[Any]:
        """
        Provider türüne göre servis döndür
        
        Args:
            provider_type (str): Provider türü (gemini, openrouter, openai, anthropic)
            **kwargs: Servis için ek parametreler
            
        Returns:
            Optional[Any]: Provider servisi veya None
        """
        try:
            provider_type = provider_type.lower()
            
            if provider_type == 'gemini':
                return cls._get_gemini_service(**kwargs)
            elif provider_type == 'openrouter':
                return cls._get_openrouter_service(**kwargs)
            elif provider_type == 'openai':
                return cls._get_openai_service(**kwargs)
            elif provider_type == 'anthropic':
                return cls._get_anthropic_service(**kwargs)
            else:
                logger.error(f"Desteklenmeyen provider türü: {provider_type}")
                return None
                
        except Exception as e:
            logger.error(f"Provider servis oluşturma hatası: {str(e)}")
            return None
    
    @classmethod
    def _get_gemini_service(cls, **kwargs) -> GeminiService:
        """Gemini servisini döndür"""
        if 'gemini' not in cls._services:
            cls._services['gemini'] = GeminiService()
        return cls._services['gemini']
    
    @classmethod
    def _get_openrouter_service(cls, **kwargs) -> OpenRouterService:
        """OpenRouter servisini döndür"""
        if 'openrouter' not in cls._services:
            cls._services['openrouter'] = OpenRouterService()
        return cls._services['openrouter']
    
    @classmethod
    def _get_openai_service(cls, **kwargs):
        """OpenAI servisini döndür (gelecekte implement edilecek)"""
        logger.warning("OpenAI servisi henüz implement edilmedi")
        return None
    
    @classmethod
    def _get_anthropic_service(cls, **kwargs):
        """Anthropic servisini döndür (gelecekte implement edilecek)"""
        logger.warning("Anthropic servisi henüz implement edilmedi")
        return None
    
    @classmethod
    def test_provider_connection(cls, provider_type: str, api_key: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Provider bağlantısını test et
        
        Args:
            provider_type (str): Provider türü
            api_key (str): API anahtarı
            model (str): Model adı (opsiyonel)
            **kwargs: Ek parametreler
            
        Returns:
            Dict[str, Any]: Test sonucu
        """
        try:
            service = cls.get_service(provider_type, **kwargs)
            if not service:
                return {
                    "success": False,
                    "error": f"Desteklenmeyen provider türü: {provider_type}"
                }
            
            # API anahtarını ayarla
            service.set_api_key(api_key)
            
            # Model ayarla (varsa)
            if model and hasattr(service, 'set_model'):
                service.set_model(model)
            
            # Bağlantıyı test et
            return service.test_connection()
            
        except Exception as e:
            logger.error(f"Provider bağlantı testi hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Bağlantı testi hatası: {str(e)}"
            }
    
    @classmethod
    def get_available_models(cls, provider_type: str, api_key: str = None) -> Dict[str, Any]:
        """
        Provider'ın kullanılabilir modellerini al
        
        Args:
            provider_type (str): Provider türü
            api_key (str): API anahtarı (opsiyonel)
            
        Returns:
            Dict[str, Any]: Model listesi
        """
        try:
            service = cls.get_service(provider_type)
            if not service:
                return {
                    "success": False,
                    "error": f"Desteklenmeyen provider türü: {provider_type}"
                }
            
            # API anahtarını ayarla (varsa)
            if api_key and hasattr(service, 'set_api_key'):
                service.set_api_key(api_key)
            
            # Modelleri al
            if hasattr(service, 'get_available_models'):
                models = service.get_available_models()
                return {
                    "success": True,
                    "models": models,
                    "count": len(models)
                }
            else:
                return {
                    "success": False,
                    "error": "Bu provider model listesi desteklemiyor"
                }
                
        except Exception as e:
            logger.error(f"Model listesi alma hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Model listesi alma hatası: {str(e)}"
            }
    
    @classmethod
    def clear_cache(cls):
        """Servis cache'ini temizle"""
        cls._services.clear()
        logger.info("Provider servis cache'i temizlendi")
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Desteklenen provider türlerini döndür"""
        return ['gemini', 'openrouter', 'openai', 'anthropic']
    
    @classmethod
    def is_provider_supported(cls, provider_type: str) -> bool:
        """Provider türünün desteklenip desteklenmediğini kontrol et"""
        return provider_type.lower() in cls.get_supported_providers()
