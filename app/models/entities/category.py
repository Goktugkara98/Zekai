# =============================================================================
# Kategori Veri Modeli
# =============================================================================

from typing import Optional, Dict, Any, List

class Category:
    """AI kategorisi veri modeli."""
    
    def __init__(self, id: Optional[int] = None, name: Optional[str] = None, 
                 icon: Optional[str] = None):
        self.id = id
        self.name = name
        self.icon = icon
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Sözlükten bir Category nesnesi oluşturur."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            icon=data.get('icon')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Category nesnesini sözlüğe dönüştürür."""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }
