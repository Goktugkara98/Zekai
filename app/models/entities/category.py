# =============================================================================
# KATEGORİ VERİ MODELİ (CATEGORY DATA MODEL)
# =============================================================================
# Bu dosya, AI (Yapay Zeka) kategorilerini temsil eden `Category` sınıfını
# tanımlar. Her kategori bir ID, isim ve ikon bilgisi içerebilir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
#
# 2.0 CATEGORY SINIFI TANIMI (CATEGORY CLASS DEFINITION)
#     2.1. Yapıcı Metot (__init__)
#     2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
#     2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
# =============================================================================

# =============================================================================
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
# =============================================================================
from typing import Optional, Dict, Any # Tip ipuçları için gerekli modüller

# =============================================================================
# 2.0 CATEGORY SINIFI TANIMI (CATEGORY CLASS DEFINITION)
# =============================================================================
class Category:
    """
    AI (Yapay Zeka) kategorisi için veri modelini temsil eder.

    Attributes:
        id (Optional[int]): Kategorinin benzersiz kimliği.
        name (Optional[str]): Kategorinin adı.
        icon (Optional[str]): Kategori için kullanılacak ikonun sınıfı veya yolu.
    """

    # -------------------------------------------------------------------------
    # 2.1. Yapıcı Metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, id: Optional[int] = None, name: Optional[str] = None,
                 icon: Optional[str] = None):
        """
        Category sınıfının yapıcı metodu.

        Args:
            id (Optional[int]): Kategorinin kimliği. Varsayılan: None.
            name (Optional[str]): Kategorinin adı. Varsayılan: None.
            icon (Optional[str]): Kategori ikonu. Varsayılan: None.
        """
        self.id = id
        self.name = name
        self.icon = icon

    # -------------------------------------------------------------------------
    # 2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
    # -------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """
        Bir sözlük (dictionary) verisinden yeni bir Category nesnesi oluşturur.

        Args:
            data (Dict[str, Any]): Kategori verilerini içeren sözlük.
                                   Beklenen anahtarlar: 'id', 'name', 'icon'.

        Returns:
            Category: Sağlanan verilerle oluşturulmuş bir Category nesnesi.
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            icon=data.get('icon')
        )

    # -------------------------------------------------------------------------
    # 2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Mevcut Category nesnesini bir sözlüğe dönüştürür.

        Returns:
            Dict[str, Any]: Kategori nesnesinin özelliklerini içeren bir sözlük.
        """
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }
