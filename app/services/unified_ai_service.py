# =============================================================================
# BİRLEŞİK AI SERVİS MODÜLÜ (UNIFIED AI SERVICE MODULE)
# =============================================================================
# Bu modül, farklı AI sağlayıcıları için birleşik bir interface sağlar.
# Strategy pattern kullanarak Gemini, OpenAI, OpenRouter ve diğer sağlayıcıları
# tek bir API üzerinden yönetir.
#
# ÖZELLİKLER:
# - Unified interface for all AI providers
# - Automatic provider selection and fallback
# - Cost tracking ve budget management
# - Performance monitoring ve analytics
# - Configuration management
# =============================================================================

import logging
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
import importlib
from dataclasses import dataclass
from enum import Enum

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

class ProviderType(Enum):
    """Desteklenen AI sağlayıcı tipleri"""
    GEMINI = "gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"

@dataclass
class AIResponse:
    """AI yanıtı için standart data class"""
    content: str
    provider_used: str
    model_used: str
    success: bool
    processing_time_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: Optional[Decimal] = None
    cost_currency: str = "USD"
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAIProvider(ABC):
    """Tüm AI sağlayıcıları için temel abstract sınıf"""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
        self.provider_type = None
        
    @abstractmethod
    def send_chat_request(self, 
                         model_entity, 
                         chat_message: Optional[str], 
                         chat_history: List[Dict[str, str]]) -> AIResponse:
        """Chat request gönderir"""
        pass
    
    @abstractmethod
    def validate_configuration(self) -> List[str]:
        """Konfigürasyonu validate eder"""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Desteklenen modelleri döndürür"""
        pass

class GeminiProvider(BaseAIProvider):
    """Google Gemini sağlayıcısı"""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)
        self.provider_type = ProviderType.GEMINI
        self._service = None
        
    def _get_service(self):
        """Lazy loading ile Gemini service'i yükler"""
        if self._service is None:
            try:
                from app.services.gemini_service import GeminiService
                self._service = GeminiService(self.api_key, self.config)
            except ImportError as e:
                logger.error(f"Gemini service import edilemedi: {e}")
                raise
        return self._service
    
    def send_chat_request(self, 
                         model_entity, 
                         chat_message: Optional[str], 
                         chat_history: List[Dict[str, str]]) -> AIResponse:
        """Gemini API'sine request gönderir"""
        start_time = datetime.utcnow()
        
        try:
            service = self._get_service()
            result = service.send_chat_request(model_entity, chat_message, chat_history)
            
            end_time = datetime.utcnow()
            processing_time = int((end_time - start_time).total_seconds() * 1000)
            
            if result.get("status_code") == 200:
                return AIResponse(
                    content=result.get("response", ""),
                    provider_used="gemini",
                    model_used=getattr(model_entity, 'external_model_name', 'gemini-pro'),
                    success=True,
                    processing_time_ms=processing_time,
                    metadata={"original_response": result}
                )
            else:
                return AIResponse(
                    content="",
                    provider_used="gemini",
                    model_used=getattr(model_entity, 'external_model_name', 'gemini-pro'),
                    success=False,
                    processing_time_ms=processing_time,
                    error_message=result.get("error", "Bilinmeyen hata")
                )
                
        except Exception as e:
            logger.error(f"Gemini provider hatası: {e}")
            return AIResponse(
                content="",
                provider_used="gemini",
                model_used=getattr(model_entity, 'external_model_name', 'gemini-pro'),
                success=False,
                error_message=str(e)
            )
    
    def validate_configuration(self) -> List[str]:
        """Gemini konfigürasyonunu validate eder"""
        errors = []
        if not self.api_key:
            errors.append("Gemini API anahtarı gereklidir")
        return errors
    
    def get_supported_models(self) -> List[str]:
        """Desteklenen Gemini modellerini döndürür"""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]

class OpenRouterProvider(BaseAIProvider):
    """OpenRouter sağlayıcısı"""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)
        self.provider_type = ProviderType.OPENROUTER
        self._service = None
        
    def _get_service(self):
        """Lazy loading ile OpenRouter service'i yükler"""
        if self._service is None:
            try:
                from app.services.enhanced_openrouter_service import EnhancedOpenRouterService
                self._service = EnhancedOpenRouterService(self.api_key, self.config)
            except ImportError as e:
                logger.error(f"OpenRouter service import edilemedi: {e}")
                raise
        return self._service
    
    def send_chat_request(self, 
                         model_entity, 
                         chat_message: Optional[str], 
                         chat_history: List[Dict[str, str]]) -> AIResponse:
        """OpenRouter API'sine request gönderir"""
        try:
            service = self._get_service()
            result = service.send_chat_request(model_entity, chat_message, chat_history)
            
            if result.get("status_code") == 200:
                return AIResponse(
                    content=result.get("response", ""),
                    provider_used="openrouter",
                    model_used=result.get("model_used", "unknown"),
                    success=True,
                    processing_time_ms=result.get("processing_time"),
                    input_tokens=result.get("usage", {}).get("prompt_tokens"),
                    output_tokens=result.get("usage", {}).get("completion_tokens"),
                    cost=Decimal(result["cost"]) if result.get("cost") else None,
                    cost_currency=result.get("cost_currency", "USD"),
                    metadata={"original_response": result}
                )
            else:
                return AIResponse(
                    content="",
                    provider_used="openrouter",
                    model_used=getattr(model_entity, 'external_model_name', 'unknown'),
                    success=False,
                    error_message=result.get("error", "Bilinmeyen hata")
                )
                
        except Exception as e:
            logger.error(f"OpenRouter provider hatası: {e}")
            return AIResponse(
                content="",
                provider_used="openrouter",
                model_used=getattr(model_entity, 'external_model_name', 'unknown'),
                success=False,
                error_message=str(e)
            )
    
    def validate_configuration(self) -> List[str]:
        """OpenRouter konfigürasyonunu validate eder"""
        errors = []
        if not self.api_key:
            errors.append("OpenRouter API anahtarı gereklidir")
        return errors
    
    def get_supported_models(self) -> List[str]:
        """Desteklenen OpenRouter modellerini döndürür"""
        try:
            service = self._get_service()
            models_result = service.get_available_models()
            if models_result.get("status_code") == 200:
                return [model.get("id", "") for model in models_result.get("models", [])]
        except Exception as e:
            logger.warning(f"OpenRouter modelleri alınamadı: {e}")
        
        # Fallback olarak bilinen modeller
        return [
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-2-70b-chat",
            "mistralai/mixtral-8x7b-instruct"
        ]

class UnifiedAIService:
    """
    Tüm AI sağlayıcılarını yöneten birleşik servis sınıfı.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        UnifiedAIService'i başlatır.
        
        Args:
            config: Genel konfigürasyon
        """
        self.config = config or {}
        self._providers: Dict[str, BaseAIProvider] = {}
        self._provider_configs: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self._request_history: List[Dict[str, Any]] = []
        self._provider_stats: Dict[str, Dict[str, Any]] = {}
        
    def register_provider(self, 
                         provider_name: str, 
                         provider_type: ProviderType, 
                         api_key: str, 
                         provider_config: Optional[Dict[str, Any]] = None):
        """
        Yeni bir AI sağlayıcısı kaydeder.
        
        Args:
            provider_name: Sağlayıcı adı
            provider_type: Sağlayıcı tipi
            api_key: API anahtarı
            provider_config: Sağlayıcıya özel konfigürasyon
        """
        try:
            config = {**self.config, **(provider_config or {})}
            
            if provider_type == ProviderType.GEMINI:
                provider = GeminiProvider(api_key, config)
            elif provider_type == ProviderType.OPENROUTER:
                provider = OpenRouterProvider(api_key, config)
            else:
                raise ValueError(f"Desteklenmeyen sağlayıcı tipi: {provider_type}")
            
            # Konfigürasyonu validate et
            validation_errors = provider.validate_configuration()
            if validation_errors:
                raise ValueError(f"Konfigürasyon hataları: {', '.join(validation_errors)}")
            
            self._providers[provider_name] = provider
            self._provider_configs[provider_name] = config
            
            # Stats başlat
            self._provider_stats[provider_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_cost': Decimal('0'),
                'avg_response_time': 0,
                'last_used': None
            }
            
            logger.info(f"AI sağlayıcısı kaydedildi: {provider_name} ({provider_type.value})")
            
        except Exception as e:
            logger.error(f"Sağlayıcı kaydedilemedi ({provider_name}): {e}")
            raise
    
    def send_chat_request(self, 
                         model_entity, 
                         chat_message: Optional[str], 
                         chat_history: List[Dict[str, str]],
                         preferred_provider: Optional[str] = None) -> AIResponse:
        """
        Birleşik chat request gönderir.
        
        Args:
            model_entity: Model entity'si
            chat_message: Chat mesajı
            chat_history: Chat geçmişi
            preferred_provider: Tercih edilen sağlayıcı
            
        Returns:
            AIResponse: Standart AI yanıtı
        """
        start_time = datetime.utcnow()
        
        # Sağlayıcı seçimi
        provider_name = self._select_provider(model_entity, preferred_provider)
        
        if not provider_name or provider_name not in self._providers:
            return AIResponse(
                content="",
                provider_used="unknown",
                model_used="unknown",
                success=False,
                error_message="Uygun sağlayıcı bulunamadı"
            )
        
        provider = self._providers[provider_name]
        
        try:
            # Request gönder
            response = provider.send_chat_request(model_entity, chat_message, chat_history)
            
            # Stats güncelle
            self._update_provider_stats(provider_name, response, start_time)
            
            # Request history'ye ekle
            self._request_history.append({
                'timestamp': start_time,
                'provider': provider_name,
                'model': response.model_used,
                'success': response.success,
                'processing_time': response.processing_time_ms,
                'cost': response.cost,
                'error': response.error_message
            })
            
            # History'yi sınırla (son 1000 request)
            if len(self._request_history) > 1000:
                self._request_history = self._request_history[-1000:]
            
            return response
            
        except Exception as e:
            logger.error(f"Unified AI service hatası: {e}")
            return AIResponse(
                content="",
                provider_used=provider_name,
                model_used=getattr(model_entity, 'external_model_name', 'unknown'),
                success=False,
                error_message=str(e)
            )
    
    def _select_provider(self, 
                        model_entity, 
                        preferred_provider: Optional[str] = None) -> Optional[str]:
        """
        Model entity'sine göre uygun sağlayıcıyı seçer.
        
        Args:
            model_entity: Model entity'si
            preferred_provider: Tercih edilen sağlayıcı
            
        Returns:
            Optional[str]: Seçilen sağlayıcı adı
        """
        # Tercih edilen sağlayıcı varsa ve kayıtlıysa onu kullan
        if preferred_provider and preferred_provider in self._providers:
            return preferred_provider
        
        # Model entity'sindeki service_provider'ı kullan
        service_provider = getattr(model_entity, 'service_provider', None)
        if service_provider:
            # Kayıtlı sağlayıcılar arasında ara
            for provider_name, provider in self._providers.items():
                if provider.provider_type.value == service_provider.lower():
                    return provider_name
        
        # Fallback: İlk kayıtlı sağlayıcıyı kullan
        if self._providers:
            return list(self._providers.keys())[0]
        
        return None
    
    def _update_provider_stats(self, 
                              provider_name: str, 
                              response: AIResponse, 
                              start_time: datetime):
        """
        Sağlayıcı istatistiklerini günceller.
        
        Args:
            provider_name: Sağlayıcı adı
            response: AI yanıtı
            start_time: Request başlama zamanı
        """
        if provider_name not in self._provider_stats:
            return
        
        stats = self._provider_stats[provider_name]
        stats['total_requests'] += 1
        stats['last_used'] = datetime.utcnow()
        
        if response.success:
            stats['successful_requests'] += 1
            
            if response.cost:
                stats['total_cost'] += response.cost
            
            if response.processing_time_ms:
                # Moving average hesaplama
                current_avg = stats['avg_response_time']
                new_avg = ((current_avg * (stats['successful_requests'] - 1)) + 
                          response.processing_time_ms) / stats['successful_requests']
                stats['avg_response_time'] = new_avg
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """
        Tüm sağlayıcıların istatistiklerini döndürür.
        
        Returns:
            Dict: Sağlayıcı istatistikleri
        """
        return {
            'providers': self._provider_stats,
            'total_providers': len(self._providers),
            'total_requests': sum(stats['total_requests'] for stats in self._provider_stats.values()),
            'recent_requests': len([r for r in self._request_history 
                                  if (datetime.utcnow() - r['timestamp']).total_seconds() < 3600])
        }
    
    def get_supported_models(self, provider_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Desteklenen modelleri döndürür.
        
        Args:
            provider_name: Belirli bir sağlayıcının modelleri (None ise tümü)
            
        Returns:
            Dict: Sağlayıcı -> modeller mapping'i
        """
        if provider_name and provider_name in self._providers:
            return {provider_name: self._providers[provider_name].get_supported_models()}
        
        result = {}
        for name, provider in self._providers.items():
            try:
                result[name] = provider.get_supported_models()
            except Exception as e:
                logger.warning(f"Sağlayıcı modelleri alınamadı ({name}): {e}")
                result[name] = []
        
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """
        Tüm sağlayıcıların sağlık durumunu kontrol eder.
        
        Returns:
            Dict: Sağlık durumu raporu
        """
        health_status = {}
        
        for provider_name, provider in self._providers.items():
            try:
                validation_errors = provider.validate_configuration()
                health_status[provider_name] = {
                    'status': 'healthy' if not validation_errors else 'warning',
                    'errors': validation_errors,
                    'last_used': self._provider_stats[provider_name].get('last_used'),
                    'success_rate': (
                        self._provider_stats[provider_name]['successful_requests'] /
                        max(self._provider_stats[provider_name]['total_requests'], 1)
                    )
                }
            except Exception as e:
                health_status[provider_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'overall_status': 'healthy' if all(
                status['status'] == 'healthy' 
                for status in health_status.values()
            ) else 'degraded',
            'providers': health_status,
            'timestamp': datetime.utcnow().isoformat()
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_unified_ai_service(config: Optional[Dict[str, Any]] = None) -> UnifiedAIService:
    """
    UnifiedAIService factory function.
    
    Args:
        config: Genel konfigürasyon
        
    Returns:
        UnifiedAIService: Yapılandırılmış servis instance'ı
    """
    return UnifiedAIService(config)

def setup_default_providers(service: UnifiedAIService, 
                           api_keys: Dict[str, str],
                           provider_configs: Optional[Dict[str, Dict[str, Any]]] = None):
    """
    Varsayılan sağlayıcıları kurar.
    
    Args:
        service: UnifiedAIService instance'ı
        api_keys: Sağlayıcı API anahtarları
        provider_configs: Sağlayıcı konfigürasyonları
    """
    configs = provider_configs or {}
    
    # Gemini sağlayıcısını kur
    if 'gemini' in api_keys:
        service.register_provider(
            'gemini',
            ProviderType.GEMINI,
            api_keys['gemini'],
            configs.get('gemini')
        )
    
    # OpenRouter sağlayıcısını kur
    if 'openrouter' in api_keys:
        service.register_provider(
            'openrouter',
            ProviderType.OPENROUTER,
            api_keys['openrouter'],
            configs.get('openrouter')
        )
    
    logger.info(f"Varsayılan sağlayıcılar kuruldu: {list(api_keys.keys())}")

