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
from typing import Optional, Dict, Any # Tip ipuçları için gerekli modüller

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
        icon (Optional[str]): Model için kullanılacak ikonun sınıfı veya yolu.
        data_ai_index (Optional[str]): Modelin arayüzde tanımlanması için kullanılan özel bir indeks.
        api_url (Optional[str]): Modelin API uç noktası.
        request_method (str): API isteği için HTTP metodu (örn: 'POST', 'GET'). Varsayılan: 'POST'.
        request_headers (Optional[str]): API isteği için JSON formatında başlıklar.
        request_body_template (Optional[str]): API isteği için JSON formatında gövde şablonu.
        response_path (Optional[str]): API yanıtından ilgili verinin çekileceği JSON yolu (örn: 'choices.0.text').
    """

    # -------------------------------------------------------------------------
    # 2.1. Yapıcı Metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, id: Optional[int] = None, category_id: Optional[int] = None,
                 name: Optional[str] = None, icon: Optional[str] = None,
                 data_ai_index: Optional[str] = None, api_url: Optional[str] = None,
                 request_method: str = 'POST', request_headers: Optional[str] = None,
                 request_body_template: Optional[str] = None, response_path: Optional[str] = None):
        """
        Model sınıfının yapıcı metodu.

        Args:
            id (Optional[int]): Model kimliği.
            category_id (Optional[int]): Kategori kimliği.
            name (Optional[str]): Model adı.
            icon (Optional[str]): Model ikonu.
            data_ai_index (Optional[str]): Modelin UI'daki data-ai-index değeri.
            api_url (Optional[str]): API uç noktası.
            request_method (str): HTTP istek metodu. Varsayılan: 'POST'.
            request_headers (Optional[str]): JSON formatında istek başlıkları.
            request_body_template (Optional[str]): JSON formatında istek gövde şablonu.
            response_path (Optional[str]): Yanıttan veri çekme yolu.
        """
        self.id = id
        self.category_id = category_id
        self.name = name
        self.icon = icon
        self.data_ai_index = data_ai_index
        self.api_url = api_url
        self.request_method = request_method
        self.request_headers = request_headers
        self.request_body_template = request_body_template
        self.response_path = response_path

    # -------------------------------------------------------------------------
    # 2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
    # -------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """
        Bir sözlük (dictionary) verisinden yeni bir Model nesnesi oluşturur.

        Args:
            data (Dict[str, Any]): Model verilerini içeren sözlük.

        Returns:
            Model: Sağlanan verilerle oluşturulmuş bir Model nesnesi.
        """
        return cls(
            id=data.get('id'),
            category_id=data.get('category_id'),
            name=data.get('name'),
            icon=data.get('icon'),
            data_ai_index=data.get('data_ai_index'),
            api_url=data.get('api_url'),
            request_method=data.get('request_method', 'POST'), # Varsayılan değer 'POST'
            request_headers=data.get('request_headers'),
            request_body_template=data.get('request_body_template'),
            response_path=data.get('response_path')
        )

    # -------------------------------------------------------------------------
    # 2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Mevcut Model nesnesini bir sözlüğe dönüştürür.

        Returns:
            Dict[str, Any]: Model nesnesinin özelliklerini içeren bir sözlük.
        """
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'icon': self.icon,
            'data_ai_index': self.data_ai_index,
            'api_url': self.api_url,
            'request_method': self.request_method,
            'request_headers': self.request_headers,
            'request_body_template': self.request_body_template,
            'response_path': self.response_path
        }
