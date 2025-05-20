# =============================================================================
# MODEL VERİ MODELİ (MODEL DATA MODEL)
# =============================================================================
# Bu dosya, AI (Yapay Zeka) modellerini temsil eden `Model` sınıfını tanımlar.
# Her model bir ID, kategori ID'si, isim, ikon ve API entegrasyonu için
# çeşitli yapılandırma detaylarını içerir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
#
# 2.0 MODEL SINIFI TANIMI (MODEL CLASS DEFINITION)
#     2.1. Yapıcı Metot (__init__)
#     2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
#     2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
# =============================================================================

# =============================================================================
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
# =============================================================================
from typing import Optional, Dict, Any, Union # Tip ipuçları için gerekli modüller
from datetime import datetime # created_at ve updated_at için

# =============================================================================
# 2.0 MODEL SINIFI TANIMI (MODEL CLASS DEFINITION)
# =============================================================================
class Model:
    """
    AI (Yapay Zeka) modeli için veri modelini temsil eder.

    Attributes:
        id (Optional[int]): Modelin benzersiz kimliği.
        category_id (Optional[int]): Modelin ait olduğu kategorinin kimliği.
        name (Optional[str]): Modelin adı.
        icon (Optional[str]): Model için kullanılacak ikonun sınıfı veya yolu (örn: 'fas fa-robot').
        description (Optional[str]): Modelin kısa açıklaması.
        details (Optional[Dict[str, Any]]): Model hakkında daha detaylı JSON formatında bilgi.
        api_url (Optional[str]): Modelin API uç noktası.
        request_method (str): API isteği için HTTP metodu (örn: 'POST', 'GET'). Varsayılan: 'POST'.
        request_headers (Optional[Dict[str, Any]]): API isteği için JSON formatında başlıklar.
        request_body (Optional[Dict[str, Any]]): API isteği için JSON formatında gövde şablonu.
        response_path (Optional[str]): API yanıtından ilgili verinin çekileceği JSON yolu (örn: 'choices.0.message.content').
        api_key (Optional[str]): API anahtarı.
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
                 api_url: Optional[str] = None,
                 request_method: str = 'POST',
                 request_headers: Optional[Dict[str, Any]] = None,
                 request_body: Optional[Dict[str, Any]] = None,
                 response_path: Optional[str] = None,
                 api_key: Optional[str] = None,
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
        self.details = details if details is not None else {} # Varsayılan boş sözlük
        self.api_url = api_url
        self.request_method = request_method
        self.request_headers = request_headers if request_headers is not None else {} # Varsayılan boş sözlük
        self.request_body = request_body if request_body is not None else {} # Varsayılan boş sözlük
        self.response_path = response_path
        self.api_key = api_key
        
        # Tarih alanlarını datetime nesnesine çevir
        if isinstance(created_at, str):
            try:
                self.created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')) if created_at else None
            except ValueError:
                 self.created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S') if created_at else None

        elif isinstance(created_at, datetime):
            self.created_at = created_at
        else:
            self.created_at = None

        if isinstance(updated_at, str):
            try:
                self.updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00')) if updated_at else None
            except ValueError:
                self.updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S') if updated_at else None
        elif isinstance(updated_at, datetime):
            self.updated_at = updated_at
        else:
            self.updated_at = None


    # -------------------------------------------------------------------------
    # 2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
    # -------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """
        Bir sözlük (dictionary) verisinden yeni bir Model nesnesi oluşturur.
        JSON alanları (details, request_headers, request_body) string ise parse eder.

        Args:
            data (Dict[str, Any]): Model verilerini içeren sözlük.

        Returns:
            Model: Sağlanan verilerle oluşturulmuş bir Model nesnesi.
        """
        import json # JSON parse için

        def parse_json_field(field_data: Any) -> Optional[Dict[str, Any]]:
            if isinstance(field_data, str):
                try:
                    return json.loads(field_data)
                except json.JSONDecodeError:
                    # print(f"UYARI: JSON parse hatası alan verisi: {field_data}")
                    return {} # Hata durumunda boş sözlük
            elif isinstance(field_data, dict):
                return field_data
            return {} # Diğer durumlarda boş sözlük

        return cls(
            id=data.get('id'),
            category_id=data.get('category_id'),
            name=data.get('name'),
            icon=data.get('icon'),
            description=data.get('description'),
            details=parse_json_field(data.get('details')),
            api_url=data.get('api_url'),
            request_method=data.get('request_method', 'POST'),
            request_headers=parse_json_field(data.get('request_headers')),
            request_body=parse_json_field(data.get('request_body')),
            response_path=data.get('response_path'),
            api_key=data.get('api_key'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    # -------------------------------------------------------------------------
    # 2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Mevcut Model nesnesini bir sözlüğe dönüştürür.
        JSON alanları (details, request_headers, request_body) string'e çevrilir.
        Tarih alanları ISO formatında string'e çevrilir.

        Returns:
            Dict[str, Any]: Model nesnesinin özelliklerini içeren bir sözlük.
        """
        import json # JSON dump için

        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'details': json.dumps(self.details) if self.details else None,
            'api_url': self.api_url,
            'request_method': self.request_method,
            'request_headers': json.dumps(self.request_headers) if self.request_headers else None,
            'request_body': json.dumps(self.request_body) if self.request_body else None,
            'response_path': self.response_path,
            'api_key': self.api_key, # API anahtarını dönerken dikkatli olunmalı, güvenlik gereksinimlerine göre kaldırılabilir.
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

