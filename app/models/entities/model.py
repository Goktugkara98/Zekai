# =============================================================================
# MODEL VERİ MODELİ (MODEL DATA MODEL) - REVİZE EDİLMİŞ
# =============================================================================
# Bu dosya, AI (Yapay Zeka) modellerini temsil eden `Model` sınıfını tanımlar.
# Yeni mimariye uygun olarak `service_provider`, `external_model_name`,
# `prompt_template` ve `status` gibi alanlar eklenmiştir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
#
# 2.0 MODEL SINIFI TANIMI (MODEL CLASS DEFINITION)
#     2.1. __init__              : Yapıcı Metot.
#     2.2. _parse_datetime       : Tarih-saat dizgisini ayrıştıran yardımcı metot.
#     2.3. from_dict             : Sözlükten Nesne Oluşturma (Class Method).
#     2.4. to_dict               : Nesneyi Sözlüğe Dönüştürme (Instance Method).
# =============================================================================

# =============================================================================
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
# =============================================================================
from typing import Optional, Dict, Any, Union
from datetime import datetime
import json # JSON işlemleri için

# =============================================================================
# 2.0 MODEL SINIFI TANIMI (MODEL CLASS DEFINITION)
# =============================================================================
class Model:
    """
    AI (Yapay Zeka) modeli için veri modelini temsil eder.

    Attributes:
        id (Optional[int]): Modelin benzersiz kimliği.
        category_id (Optional[int]): Modelin ait olduğu kategorinin kimliği.
        name (Optional[str]): Modelin kullanıcı dostu adı.
        icon (Optional[str]): Model için kullanılacak ikonun sınıfı veya yolu.
        description (Optional[str]): Modelin kısa açıklaması.
        details (Optional[Dict[str, Any]]): Model hakkında daha detaylı JSON formatında bilgi (örn: parametre limitleri).
        service_provider (Optional[str]): Hangi AI servisi sağlayıcısının kullanılacağını belirtir
                                          (örn: 'openai', 'google_gemini_sdk', 'gemini_via_openai_sdk', 'custom_rest', 'openrouter').
        external_model_name (Optional[str]): Servis sağlayıcısının kendi içindeki spesifik model adı
                                             (örn: 'gpt-4o', 'gemini-1.5-pro-latest', 'mistralai/Mistral-7B-Instruct-v0.1').
        api_url (Optional[str]): Modelin API uç noktası (özellikle 'custom_rest' veya 'openai' kütüphanesi ile farklı base_url için).
        request_method (str): API isteği için HTTP metodu (örn: 'POST', 'GET'). Varsayılan: 'POST'.
        request_headers (Optional[Dict[str, Any]]): API isteği için JSON formatında başlıklar ('custom_rest' için önemli).
        request_body (Optional[Dict[str, Any]]): API isteği için JSON formatında gövde şablonu ('custom_rest' için önemli).
                                                  Placeholder'lar içerebilir (örn: {"prompt": "{user_message}"}).
        response_path (Optional[str]): API yanıtından ilgili verinin çekileceği JSON yolu ('custom_rest' için önemli).
        api_key (Optional[str]): API anahtarı.
                                 İleride doğrudan saklamak yerine güvenli bir referans (örn: ortam değişkeni adı, secret manager ID)
                                 tutulması daha güvenli olacaktır. Şimdilik geliştirme kolaylığı için doğrudan tutuluyor.
        prompt_template (Optional[str]): Model için kullanılacak varsayılan prompt şablonu.
                                         Placeholder'lar içerebilir (örn: "Kullanıcı sorusu: {user_message}\nYanıt:").
        status (str): Modelin durumu (örn: 'active', 'inactive', 'beta'). Varsayılan: 'active'.
        created_at (Optional[datetime]): Oluşturulma tarihi.
        updated_at (Optional[datetime]): Güncellenme tarihi.
    """

    # -------------------------------------------------------------------------
    # 2.1. Yapıcı Metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self,
                 id: Optional[int] = None,
                 category_id: Optional[int] = None,
                 name: Optional[str] = None,
                 icon: Optional[str] = None,
                 description: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 service_provider: Optional[str] = None,
                 external_model_name: Optional[str] = None,
                 api_url: Optional[str] = None,
                 request_method: str = 'POST',
                 request_headers: Optional[Dict[str, Any]] = None,
                 request_body: Optional[Dict[str, Any]] = None,
                 response_path: Optional[str] = None,
                 api_key: Optional[str] = None,
                 prompt_template: Optional[str] = None,
                 status: str = 'active',
                 created_at: Optional[Union[datetime, str]] = None,
                 updated_at: Optional[Union[datetime, str]] = None):
        """
        Model sınıfının yapıcı metodu.
        """
        self.id = id
        self.category_id = category_id
        self.name = name
        self.icon = icon
        self.description = description
        self.details = details if details is not None else {}
        self.service_provider = service_provider
        self.external_model_name = external_model_name
        self.api_url = api_url
        self.request_method = request_method
        self.request_headers = request_headers if request_headers is not None else {}
        self.request_body = request_body if request_body is not None else {}
        self.response_path = response_path
        self.api_key = api_key
        self.prompt_template = prompt_template
        self.status = status
        self.created_at = self._parse_datetime(created_at)
        self.updated_at = self._parse_datetime(updated_at)

    # -------------------------------------------------------------------------
    # 2.2. Tarih-saat dizgisini ayrıştıran yardımcı metot (_parse_datetime)
    # -------------------------------------------------------------------------
    def _parse_datetime(self, value: Optional[Union[datetime, str]]) -> Optional[datetime]:
        """
        Verilen bir string veya datetime nesnesini datetime nesnesine dönüştürür.
        ISO formatını ve '%Y-%m-%d %H:%M:%S' formatını destekler.

        Args:
            value (Optional[Union[datetime, str]]): Dönüştürülecek değer.

        Returns:
            Optional[datetime]: Başarılı olursa datetime nesnesi, aksi halde None.
        """
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        elif isinstance(value, datetime):
            return value
        return None

    # -------------------------------------------------------------------------
    # 2.3. Sözlükten Nesne Oluşturma (from_dict - Class Method)
    # -------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """
        Bir sözlük (dictionary) verisinden yeni bir Model nesnesi oluşturur.
        JSON alanları (details, request_headers, request_body) string ise parse eder.
        """
        def parse_json_field(field_data: Any) -> Optional[Dict[str, Any]]:
            if isinstance(field_data, str):
                try:
                    return json.loads(field_data)
                except json.JSONDecodeError:
                    return {}
            elif isinstance(field_data, dict):
                return field_data
            return {}

        return cls(
            id=data.get('id'),
            category_id=data.get('category_id'),
            name=data.get('name'),
            icon=data.get('icon'),
            description=data.get('description'),
            details=parse_json_field(data.get('details')),
            service_provider=data.get('service_provider'),
            external_model_name=data.get('external_model_name'),
            api_url=data.get('api_url'),
            request_method=data.get('request_method', 'POST'),
            request_headers=parse_json_field(data.get('request_headers')),
            request_body=parse_json_field(data.get('request_body')),
            response_path=data.get('response_path'),
            api_key=data.get('api_key'),
            prompt_template=data.get('prompt_template'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    # -------------------------------------------------------------------------
    # 2.4. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
    # -------------------------------------------------------------------------
    def to_dict(self, for_database: bool = False) -> Dict[str, Any]:
        """
        Mevcut Model nesnesini bir sözlüğe dönüştürür.
        JSON alanları (details, request_headers, request_body) string'e çevrilir (eğer for_database True ise).
        Tarih alanları ISO formatında string'e çevrilir.

        Args:
            for_database (bool): Eğer True ise, JSON alanları string olarak formatlanır (veritabanı için).
                                 False ise, Python dict olarak bırakılır.

        Returns:
            Dict[str, Any]: Model nesnesinin özelliklerini içeren bir sözlük.
        """
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'details': self.details,
            'service_provider': self.service_provider,
            'external_model_name': self.external_model_name,
            'api_url': self.api_url,
            'request_method': self.request_method,
            'request_headers': self.request_headers,
            'request_body': self.request_body,
            'response_path': self.response_path,
            'api_key': self.api_key,
            'prompt_template': self.prompt_template,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if for_database:
            if data['details'] is not None:
                data['details'] = json.dumps(self.details)
            if data['request_headers'] is not None:
                data['request_headers'] = json.dumps(self.request_headers)
            if data['request_body'] is not None:
                data['request_body'] = json.dumps(self.request_body)
        
        return data
