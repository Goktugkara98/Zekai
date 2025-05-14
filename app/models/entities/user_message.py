# =============================================================================
# KULLANICI MESAJI VERİ MODELİ (USER MESSAGE DATA MODEL)
# =============================================================================
# Bu dosya, kullanıcılar ve AI (Yapay Zeka) arasındaki etkileşimleri
# (mesajları) temsil eden `UserMessage` sınıfını tanımlar. Her mesaj,
# kullanıcı girdisi, AI yanıtı, kullanılan model, zaman damgaları ve
# diğer meta verileri içerir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
#
# 2.0 USERMESSAGE SINIFI TANIMI (USERMESSAGE CLASS DEFINITION)
#     2.1. Yapıcı Metot (__init__)
#     2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
#     2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
# =============================================================================

# =============================================================================
# 1.0 GEREKLİ İÇE AKTARMALAR (REQUIRED IMPORTS)
# =============================================================================
from typing import Optional, Dict, Any # Tip ipuçları için gerekli modüller
from datetime import datetime # Zaman damgası için datetime modülü

# =============================================================================
# 2.0 USERMESSAGE SINIFI TANIMI (USERMESSAGE CLASS DEFINITION)
# =============================================================================
class UserMessage:
    """
    Kullanıcı mesajlaşma etkileşimleri için veri modelini temsil eder.

    Attributes:
        id (Optional[int]): Mesajın benzersiz kimliği.
        session_id (Optional[str]): Sohbet oturumunun kimliği.
        user_id (Optional[str]): Kullanıcının kimliği.
        user_message (Optional[str]): Kullanıcının gönderdiği orijinal mesaj.
        prompt (Optional[str]): AI modeline gönderilen (muhtemelen işlenmiş) prompt.
        ai_response (Optional[str]): AI modelinden alınan yanıt.
        ai_model_name (Optional[str]): Kullanılan AI modelinin adı.
        model_params (Optional[str]): Model için kullanılan parametrelerin JSON string'i.
        request_json (Optional[str]): AI modeline gönderilen tam isteğin JSON string'i.
        response_json (Optional[str]): AI modelinden alınan tam yanıtın JSON string'i.
        tokens (Optional[int]): İstek/yanıt için harcanan token sayısı.
        duration (Optional[float]): İsteğin işlenme süresi (saniye cinsinden).
        error_message (Optional[str]): İşlem sırasında bir hata oluştuysa hata mesajı.
        status (Optional[str]): Mesajın durumu (örn: 'başarılı', 'hata').
        timestamp (Optional[datetime]): Mesajın oluşturulduğu zaman damgası.
    """

    # -------------------------------------------------------------------------
    # 2.1. Yapıcı Metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, id: Optional[int] = None, session_id: Optional[str] = None,
                 user_id: Optional[str] = None, user_message: Optional[str] = None,
                 prompt: Optional[str] = None, ai_response: Optional[str] = None,
                 ai_model_name: Optional[str] = None, model_params: Optional[str] = None,
                 request_json: Optional[str] = None, response_json: Optional[str] = None,
                 tokens: Optional[int] = None, duration: Optional[float] = None,
                 error_message: Optional[str] = None, status: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        """
        UserMessage sınıfının yapıcı metodu.
        """
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
        self.timestamp = timestamp if timestamp else datetime.now() # Varsayılan olarak şimdiki zaman

    # -------------------------------------------------------------------------
    # 2.2. Sözlükten Nesne Oluşturma (from_dict - Class Method)
    # -------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMessage':
        """
        Bir sözlük (dictionary) verisinden yeni bir UserMessage nesnesi oluşturur.
        Zaman damgası (timestamp) string ise datetime nesnesine dönüştürülür.

        Args:
            data (Dict[str, Any]): UserMessage verilerini içeren sözlük.

        Returns:
            UserMessage: Sağlanan verilerle oluşturulmuş bir UserMessage nesnesi.
        """
        timestamp_data = data.get('timestamp')
        parsed_timestamp = None
        if isinstance(timestamp_data, str):
            try:
                # ISO formatı ve boşluklu format için denemeler
                if 'T' in timestamp_data and '.' in timestamp_data:
                    parsed_timestamp = datetime.fromisoformat(timestamp_data.split('.')[0]) # Mikrosaniyeleri at
                elif 'T' in timestamp_data:
                     parsed_timestamp = datetime.fromisoformat(timestamp_data)
                else:
                    parsed_timestamp = datetime.strptime(timestamp_data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Eğer bilinen formatlardan biri değilse veya None ise, None olarak kalır
                # veya loglama yapılabilir.
                pass
        elif isinstance(timestamp_data, datetime):
            parsed_timestamp = timestamp_data

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
            timestamp=parsed_timestamp
        )

    # -------------------------------------------------------------------------
    # 2.3. Nesneyi Sözlüğe Dönüştürme (to_dict - Instance Method)
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Mevcut UserMessage nesnesini bir sözlüğe dönüştürür.
        Zaman damgası (timestamp) ISO formatında string'e dönüştürülür.

        Returns:
            Dict[str, Any]: UserMessage nesnesinin özelliklerini içeren bir sözlük.
        """
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
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
