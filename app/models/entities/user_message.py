# =============================================================================
# Kullanıcı Mesajı Veri Modeli
# =============================================================================

from typing import Optional, Dict, Any, List
from datetime import datetime

class UserMessage:
    """Kullanıcı mesajı veri modeli."""
    
    def __init__(self, id: Optional[int] = None, session_id: Optional[str] = None,
                 user_id: Optional[str] = None, user_message: Optional[str] = None,
                 prompt: Optional[str] = None, ai_response: Optional[str] = None,
                 ai_model_name: Optional[str] = None, model_params: Optional[str] = None,
                 request_json: Optional[str] = None, response_json: Optional[str] = None,
                 tokens: Optional[int] = None, duration: Optional[float] = None,
                 error_message: Optional[str] = None, status: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        self.user_message = user_message
        self.prompt = prompt
        self.ai_response = ai_response
        self.ai_model_name = ai_model_name
        self.model_params = model_params
        self.request_json = request_json
        self.response_json = response_json
        self.tokens = tokens
        self.duration = duration
        self.error_message = error_message
        self.status = status
        self.timestamp = timestamp
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMessage':
        """Sözlükten bir UserMessage nesnesi oluşturur."""
        return cls(
            id=data.get('id'),
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            user_message=data.get('user_message'),
            prompt=data.get('prompt'),
            ai_response=data.get('ai_response'),
            ai_model_name=data.get('ai_model_name'),
            model_params=data.get('model_params'),
            request_json=data.get('request_json'),
            response_json=data.get('response_json'),
            tokens=data.get('tokens'),
            duration=data.get('duration'),
            error_message=data.get('error_message'),
            status=data.get('status'),
            timestamp=data.get('timestamp')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """UserMessage nesnesini sözlüğe dönüştürür."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_message': self.user_message,
            'prompt': self.prompt,
            'ai_response': self.ai_response,
            'ai_model_name': self.ai_model_name,
            'model_params': self.model_params,
            'request_json': self.request_json,
            'response_json': self.response_json,
            'tokens': self.tokens,
            'duration': self.duration,
            'error_message': self.error_message,
            'status': self.status,
            'timestamp': self.timestamp
        }
