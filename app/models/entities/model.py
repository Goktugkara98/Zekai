# =============================================================================
# ENHANCED MODEL VERİ MODELİ (ENHANCED MODEL DATA MODEL) - OPENROUTER UYUMLU
# =============================================================================
# Bu dosya, AI (Yapay Zeka) modellerini temsil eden geliştirilmiş `Model` sınıfını tanımlar.
# OpenRouter ve diğer alternatif AI sağlayıcıları ile tam uyumlu çalışacak şekilde
# genişletilmiş ve yeni özellikler eklenmiştir.
#
# YENİ ÖZELLİKLER:
# - OpenRouter routing ve load balancing desteği
# - Dinamik pricing ve cost management
# - Model capabilities ve metadata
# - Provider-specific configuration
# - Enhanced error handling ve validation
# =============================================================================

from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from decimal import Decimal
import json

# =============================================================================
# ENHANCED MODEL SINIFI TANIMI (ENHANCED MODEL CLASS DEFINITION)
# =============================================================================
class Model:
    """
    AI (Yapay Zeka) modellerini temsil eden geliştirilmiş sınıf.
    OpenRouter ve diğer alternatif AI sağlayıcıları ile tam uyumlu.

    Attributes:
        # Temel Tanımlayıcı Alanlar
        id (Optional[int]): Modelin benzersiz kimliği.
        category_id (Optional[int]): Modelin ait olduğu kategorinin kimliği.
        name (Optional[str]): Modelin kullanıcı dostu adı.
        icon (Optional[str]): Model için kullanılacak ikonun sınıfı veya yolu.
        description (Optional[str]): Modelin kısa açıklaması.
        
        # Temel API Konfigürasyonu
        service_provider (Optional[str]): AI servis sağlayıcısı
        external_model_name (Optional[str]): Sağlayıcının kendi model adı
        api_url (Optional[str]): Model API endpoint'i
        request_method (str): HTTP metodu (varsayılan: 'POST')
        request_headers (Optional[Dict[str, Any]]): API request header'ları
        request_body (Optional[Dict[str, Any]]): API request body template'i
        response_path (Optional[str]): Response'dan veri çekme yolu
        api_key (Optional[str]): API anahtarı
        
        # Gelişmiş Konfigürasyon
        prompt_template (Optional[str]): Varsayılan prompt template'i
        status (str): Model durumu (varsayılan: 'active')
        
        # OpenRouter ve Routing Özellikleri
        routing_config (Optional[Dict[str, Any]]): Routing konfigürasyonu
        fallback_models (Optional[List[str]]): Yedek model listesi
        load_balancing_strategy (Optional[str]): Load balancing stratejisi
        
        # Pricing ve Cost Management
        input_cost_per_token (Optional[Decimal]): Input token başına maliyet
        output_cost_per_token (Optional[Decimal]): Output token başına maliyet
        cost_currency (str): Maliyet para birimi (varsayılan: 'USD')
        cost_updated_at (Optional[datetime]): Maliyet güncelleme tarihi
        
        # Model Capabilities
        max_context_length (Optional[int]): Maksimum context uzunluğu
        supports_streaming (bool): Streaming desteği (varsayılan: False)
        supports_function_calling (bool): Function calling desteği (varsayılan: False)
        model_family (Optional[str]): Model ailesi (örn: 'gpt', 'claude', 'gemini')
        model_version (Optional[str]): Model versiyonu
        
        # Provider-Specific Configuration
        provider_config (Optional[Dict[str, Any]]): Sağlayıcıya özel konfigürasyon
        custom_headers (Optional[Dict[str, str]]): Özel HTTP header'ları
        auth_method (str): Authentication metodu (varsayılan: 'bearer_token')
        
        # Metadata ve Detaylar
        details (Optional[Dict[str, Any]]): Ek model detayları
        tags (Optional[List[str]]): Model etiketleri
        
        # Timestamp Alanları
        created_at (Optional[datetime]): Oluşturulma tarihi
        updated_at (Optional[datetime]): Güncellenme tarihi
    """

    def __init__(self,
                 # Temel Alanlar
                 id: Optional[int] = None,
                 category_id: Optional[int] = None,
                 name: Optional[str] = None,
                 icon: Optional[str] = None,
                 description: Optional[str] = None,
                 
                 # API Konfigürasyonu
                 service_provider: Optional[str] = None,
                 external_model_name: Optional[str] = None,
                 api_url: Optional[str] = None,
                 request_method: str = 'POST',
                 request_headers: Optional[Dict[str, Any]] = None,
                 request_body: Optional[Dict[str, Any]] = None,
                 response_path: Optional[str] = None,
                 api_key: Optional[str] = None,
                 
                 # Gelişmiş Konfigürasyon
                 prompt_template: Optional[str] = None,
                 status: str = 'active',
                 
                 # OpenRouter Özellikleri
                 routing_config: Optional[Dict[str, Any]] = None,
                 fallback_models: Optional[List[str]] = None,
                 load_balancing_strategy: Optional[str] = None,
                 
                 # Pricing
                 input_cost_per_token: Optional[Union[Decimal, float, str]] = None,
                 output_cost_per_token: Optional[Union[Decimal, float, str]] = None,
                 cost_currency: str = 'USD',
                 cost_updated_at: Optional[Union[datetime, str]] = None,
                 
                 # Capabilities
                 max_context_length: Optional[int] = None,
                 supports_streaming: bool = False,
                 supports_function_calling: bool = False,
                 model_family: Optional[str] = None,
                 model_version: Optional[str] = None,
                 
                 # Provider-Specific
                 provider_config: Optional[Dict[str, Any]] = None,
                 custom_headers: Optional[Dict[str, str]] = None,
                 auth_method: str = 'bearer_token',
                 
                 # Metadata
                 details: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 
                 # Timestamps
                 created_at: Optional[Union[datetime, str]] = None,
                 updated_at: Optional[Union[datetime, str]] = None):
        """
        Enhanced Model sınıfının constructor'ı.
        """
        # Temel alanları ata
        self.id = id
        self.category_id = category_id
        self.name = name
        self.icon = icon
        self.description = description
        
        # API konfigürasyonu
        self.service_provider = service_provider
        self.external_model_name = external_model_name
        self.api_url = api_url
        self.request_method = request_method.upper() if request_method else 'POST'
        self.request_headers = request_headers if request_headers is not None else {}
        self.request_body = request_body if request_body is not None else {}
        self.response_path = response_path
        self.api_key = api_key
        
        # Gelişmiş konfigürasyon
        self.prompt_template = prompt_template
        self.status = status
        
        # OpenRouter özellikleri
        self.routing_config = routing_config if routing_config is not None else {}
        self.fallback_models = fallback_models if fallback_models is not None else []
        self.load_balancing_strategy = load_balancing_strategy
        
        # Pricing alanları
        self.input_cost_per_token = self._parse_decimal(input_cost_per_token)
        self.output_cost_per_token = self._parse_decimal(output_cost_per_token)
        self.cost_currency = cost_currency
        self.cost_updated_at = self._parse_datetime(cost_updated_at)
        
        # Capabilities
        self.max_context_length = max_context_length
        self.supports_streaming = supports_streaming
        self.supports_function_calling = supports_function_calling
        self.model_family = model_family
        self.model_version = model_version
        
        # Provider-specific
        self.provider_config = provider_config if provider_config is not None else {}
        self.custom_headers = custom_headers if custom_headers is not None else {}
        self.auth_method = auth_method
        
        # Metadata
        self.details = details if details is not None else {}
        self.tags = tags if tags is not None else []
        
        # Timestamps
        self.created_at = self._parse_datetime(created_at)
        self.updated_at = self._parse_datetime(updated_at)

    def _parse_decimal(self, value: Optional[Union[Decimal, float, str]]) -> Optional[Decimal]:
        """
        Decimal değerini parse eder.
        """
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None

    def _parse_datetime(self, value: Optional[Union[datetime, str]]) -> Optional[datetime]:
        """
        Datetime değerini parse eder.
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                # ISO format datetime parse
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Alternative format
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """
        Dictionary'den Model instance'ı oluşturur.
        """
        return cls(
            id=data.get('id'),
            category_id=data.get('category_id'),
            name=data.get('name'),
            icon=data.get('icon'),
            description=data.get('description'),
            service_provider=data.get('service_provider'),
            external_model_name=data.get('external_model_name'),
            api_url=data.get('api_url'),
            request_method=data.get('request_method', 'POST'),
            request_headers=data.get('request_headers'),
            request_body=data.get('request_body'),
            response_path=data.get('response_path'),
            api_key=data.get('api_key'),
            prompt_template=data.get('prompt_template'),
            status=data.get('status', 'active'),
            routing_config=data.get('routing_config'),
            fallback_models=data.get('fallback_models'),
            load_balancing_strategy=data.get('load_balancing_strategy'),
            input_cost_per_token=data.get('input_cost_per_token'),
            output_cost_per_token=data.get('output_cost_per_token'),
            cost_currency=data.get('cost_currency', 'USD'),
            cost_updated_at=data.get('cost_updated_at'),
            max_context_length=data.get('max_context_length'),
            supports_streaming=data.get('supports_streaming', False),
            supports_function_calling=data.get('supports_function_calling', False),
            model_family=data.get('model_family'),
            model_version=data.get('model_version'),
            provider_config=data.get('provider_config'),
            custom_headers=data.get('custom_headers'),
            auth_method=data.get('auth_method', 'bearer_token'),
            details=data.get('details'),
            tags=data.get('tags'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Model instance'ını dictionary'e dönüştürür.
        
        Args:
            include_sensitive: API key gibi hassas bilgileri dahil et
        """
        result = {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'service_provider': self.service_provider,
            'external_model_name': self.external_model_name,
            'api_url': self.api_url,
            'request_method': self.request_method,
            'request_headers': self.request_headers,
            'request_body': self.request_body,
            'response_path': self.response_path,
            'prompt_template': self.prompt_template,
            'status': self.status,
            'routing_config': self.routing_config,
            'fallback_models': self.fallback_models,
            'load_balancing_strategy': self.load_balancing_strategy,
            'input_cost_per_token': str(self.input_cost_per_token) if self.input_cost_per_token else None,
            'output_cost_per_token': str(self.output_cost_per_token) if self.output_cost_per_token else None,
            'cost_currency': self.cost_currency,
            'cost_updated_at': self.cost_updated_at.isoformat() if self.cost_updated_at else None,
            'max_context_length': self.max_context_length,
            'supports_streaming': self.supports_streaming,
            'supports_function_calling': self.supports_function_calling,
            'model_family': self.model_family,
            'model_version': self.model_version,
            'provider_config': self.provider_config,
            'custom_headers': self.custom_headers,
            'auth_method': self.auth_method,
            'details': self.details,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            result['api_key'] = self.api_key
            
        return result

    def is_openrouter_compatible(self) -> bool:
        """
        Modelin OpenRouter ile uyumlu olup olmadığını kontrol eder.
        """
        return (
            self.service_provider == 'openrouter' or
            (self.api_url and 'openrouter.ai' in self.api_url) or
            (self.external_model_name and '/' in self.external_model_name)
        )

    def get_effective_cost(self, input_tokens: int, output_tokens: int) -> Optional[Decimal]:
        """
        Verilen token sayıları için toplam maliyeti hesaplar.
        """
        if not self.input_cost_per_token or not self.output_cost_per_token:
            return None
            
        input_cost = self.input_cost_per_token * Decimal(input_tokens)
        output_cost = self.output_cost_per_token * Decimal(output_tokens)
        
        return input_cost + output_cost

    def validate(self) -> List[str]:
        """
        Model konfigürasyonunu validate eder ve hataları döndürür.
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Model adı gereklidir")
            
        if not self.service_provider or not self.service_provider.strip():
            errors.append("Servis sağlayıcı gereklidir")
            
        if not self.external_model_name or not self.external_model_name.strip():
            errors.append("Harici model adı gereklidir")
            
        if self.status not in ['active', 'inactive', 'beta', 'deprecated']:
            errors.append("Geçersiz status değeri")
            
        if self.auth_method not in ['bearer_token', 'api_key', 'oauth2', 'none']:
            errors.append("Geçersiz authentication metodu")
            
        if self.max_context_length and self.max_context_length <= 0:
            errors.append("Maksimum context length pozitif olmalı")
            
        return errors

    def __repr__(self) -> str:
        return f"Model(id={self.id}, name='{self.name}', provider='{self.service_provider}')"

    def __str__(self) -> str:
        return f"{self.name} ({self.service_provider})"
