# =============================================================================
# PROVIDER VERİ MODELİ (PROVIDER DATA MODEL)
# =============================================================================
# Bu dosya, AI sağlayıcılarını temsil eden `Provider` sınıfını tanımlar.
# OpenRouter, OpenAI, Anthropic, Google gibi farklı AI sağlayıcılarının
# merkezi yönetimini sağlar.
# =============================================================================

from typing import Optional, Dict, Any, Union, List
from datetime import datetime
import json

class Provider:
    """
    AI sağlayıcılarını temsil eden sınıf.
    
    Attributes:
        id (Optional[int]): Sağlayıcının benzersiz kimliği
        name (str): Sağlayıcının sistem adı (örn: 'openrouter', 'openai')
        display_name (str): Kullanıcı dostu görünen ad
        base_url (str): API base URL'i
        api_version (Optional[str]): API versiyonu
        auth_type (str): Authentication tipi
        default_headers (Optional[Dict[str, Any]]): Varsayılan HTTP header'ları
        rate_limits (Optional[Dict[str, Any]]): Rate limiting konfigürasyonu
        supported_features (Optional[List[str]]): Desteklenen özellikler
        pricing_info (Optional[Dict[str, Any]]): Pricing bilgileri
        status (str): Sağlayıcı durumu
        configuration (Optional[Dict[str, Any]]): Ek konfigürasyon
        created_at (Optional[datetime]): Oluşturulma tarihi
        updated_at (Optional[datetime]): Güncellenme tarihi
    """

    def __init__(self,
                 id: Optional[int] = None,
                 name: Optional[str] = None,
                 display_name: Optional[str] = None,
                 base_url: Optional[str] = None,
                 api_version: Optional[str] = None,
                 auth_type: str = 'bearer_token',
                 default_headers: Optional[Dict[str, Any]] = None,
                 rate_limits: Optional[Dict[str, Any]] = None,
                 supported_features: Optional[List[str]] = None,
                 pricing_info: Optional[Dict[str, Any]] = None,
                 status: str = 'active',
                 configuration: Optional[Dict[str, Any]] = None,
                 created_at: Optional[Union[datetime, str]] = None,
                 updated_at: Optional[Union[datetime, str]] = None):
        """
        Provider sınıfının constructor'ı.
        """
        self.id = id
        self.name = name
        self.display_name = display_name or name
        self.base_url = base_url
        self.api_version = api_version
        self.auth_type = auth_type
        self.default_headers = default_headers if default_headers is not None else {}
        self.rate_limits = rate_limits if rate_limits is not None else {}
        self.supported_features = supported_features if supported_features is not None else []
        self.pricing_info = pricing_info if pricing_info is not None else {}
        self.status = status
        self.configuration = configuration if configuration is not None else {}
        self.created_at = self._parse_datetime(created_at)
        self.updated_at = self._parse_datetime(updated_at)

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
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Provider':
        """
        Dictionary'den Provider instance'ı oluşturur.
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            display_name=data.get('display_name'),
            base_url=data.get('base_url'),
            api_version=data.get('api_version'),
            auth_type=data.get('auth_type', 'bearer_token'),
            default_headers=data.get('default_headers'),
            rate_limits=data.get('rate_limits'),
            supported_features=data.get('supported_features'),
            pricing_info=data.get('pricing_info'),
            status=data.get('status', 'active'),
            configuration=data.get('configuration'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Provider instance'ını dictionary'e dönüştürür.
        """
        result = {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'base_url': self.base_url,
            'api_version': self.api_version,
            'auth_type': self.auth_type,
            'default_headers': self.default_headers,
            'rate_limits': self.rate_limits,
            'supported_features': self.supported_features,
            'pricing_info': self.pricing_info,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            result['configuration'] = self.configuration
            
        return result

    def supports_feature(self, feature: str) -> bool:
        """
        Belirtilen özelliğin desteklenip desteklenmediğini kontrol eder.
        """
        return feature in self.supported_features

    def get_rate_limit(self, limit_type: str) -> Optional[int]:
        """
        Belirtilen rate limit tipini döndürür.
        """
        return self.rate_limits.get(limit_type)

    def validate(self) -> List[str]:
        """
        Provider konfigürasyonunu validate eder.
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Sağlayıcı adı gereklidir")
            
        if not self.base_url or not self.base_url.strip():
            errors.append("Base URL gereklidir")
            
        if self.auth_type not in ['bearer_token', 'api_key', 'oauth2', 'none']:
            errors.append("Geçersiz authentication tipi")
            
        if self.status not in ['active', 'inactive', 'maintenance', 'deprecated']:
            errors.append("Geçersiz status değeri")
            
        return errors

    def __repr__(self) -> str:
        return f"Provider(id={self.id}, name='{self.name}', status='{self.status}')"

    def __str__(self) -> str:
        return f"{self.display_name} ({self.name})"


class ModelProvider:
    """
    Model-Provider ilişkisini temsil eden junction sınıfı.
    
    Attributes:
        id (Optional[int]): İlişkinin benzersiz kimliği
        model_id (int): Model ID'si
        provider_id (int): Provider ID'si
        provider_model_name (str): Sağlayıcıdaki model adı
        priority (int): Öncelik sırası (1 = en yüksek)
        is_primary (bool): Birincil sağlayıcı mı
        specific_config (Optional[Dict[str, Any]]): Özel konfigürasyon
        status (str): İlişki durumu
        created_at (Optional[datetime]): Oluşturulma tarihi
        updated_at (Optional[datetime]): Güncellenme tarihi
    """

    def __init__(self,
                 id: Optional[int] = None,
                 model_id: Optional[int] = None,
                 provider_id: Optional[int] = None,
                 provider_model_name: Optional[str] = None,
                 priority: int = 1,
                 is_primary: bool = False,
                 specific_config: Optional[Dict[str, Any]] = None,
                 status: str = 'active',
                 created_at: Optional[Union[datetime, str]] = None,
                 updated_at: Optional[Union[datetime, str]] = None):
        """
        ModelProvider sınıfının constructor'ı.
        """
        self.id = id
        self.model_id = model_id
        self.provider_id = provider_id
        self.provider_model_name = provider_model_name
        self.priority = priority
        self.is_primary = is_primary
        self.specific_config = specific_config if specific_config is not None else {}
        self.status = status
        self.created_at = self._parse_datetime(created_at)
        self.updated_at = self._parse_datetime(updated_at)

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
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelProvider':
        """
        Dictionary'den ModelProvider instance'ı oluşturur.
        """
        return cls(
            id=data.get('id'),
            model_id=data.get('model_id'),
            provider_id=data.get('provider_id'),
            provider_model_name=data.get('provider_model_name'),
            priority=data.get('priority', 1),
            is_primary=data.get('is_primary', False),
            specific_config=data.get('specific_config'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        ModelProvider instance'ını dictionary'e dönüştürür.
        """
        return {
            'id': self.id,
            'model_id': self.model_id,
            'provider_id': self.provider_id,
            'provider_model_name': self.provider_model_name,
            'priority': self.priority,
            'is_primary': self.is_primary,
            'specific_config': self.specific_config,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def validate(self) -> List[str]:
        """
        ModelProvider konfigürasyonunu validate eder.
        """
        errors = []
        
        if not self.model_id:
            errors.append("Model ID gereklidir")
            
        if not self.provider_id:
            errors.append("Provider ID gereklidir")
            
        if not self.provider_model_name or not self.provider_model_name.strip():
            errors.append("Sağlayıcı model adı gereklidir")
            
        if self.priority < 1:
            errors.append("Öncelik 1'den küçük olamaz")
            
        if self.status not in ['active', 'inactive', 'deprecated']:
            errors.append("Geçersiz status değeri")
            
        return errors

    def __repr__(self) -> str:
        return f"ModelProvider(model_id={self.model_id}, provider_id={self.provider_id}, priority={self.priority})"

    def __str__(self) -> str:
        return f"Model {self.model_id} -> Provider {self.provider_id} ({self.provider_model_name})"

