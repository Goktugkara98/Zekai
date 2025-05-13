# =============================================================================
# Model Veri Modeli
# =============================================================================

from typing import Optional, Dict, Any, List

class Model:
    """AI modeli veri modeli."""
    
    def __init__(self, id: Optional[int] = None, category_id: Optional[int] = None,
                 name: Optional[str] = None, icon: Optional[str] = None,
                 data_ai_index: Optional[str] = None, api_url: Optional[str] = None,
                 request_method: str = 'POST', request_headers: Optional[str] = None,
                 request_body_template: Optional[str] = None, response_path: Optional[str] = None):
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """Sözlükten bir Model nesnesi oluşturur."""
        return cls(
            id=data.get('id'),
            category_id=data.get('category_id'),
            name=data.get('name'),
            icon=data.get('icon'),
            data_ai_index=data.get('data_ai_index'),
            api_url=data.get('api_url'),
            request_method=data.get('request_method', 'POST'),
            request_headers=data.get('request_headers'),
            request_body_template=data.get('request_body_template'),
            response_path=data.get('response_path')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Model nesnesini sözlüğe dönüştürür."""
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
