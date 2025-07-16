import requests
import json
from typing import List, Dict, Any, Tuple
from flask import current_app
from app.services.base_ai_service import BaseAIService

class OpenAIRouterService(BaseAIService):
    def __init__(self, model_config=None, config=None):
        super().__init__(model_config=model_config)
        self.config = config

    """
    OpenAI uyumlu API'ler (OpenRouter, Together, vb.) için genel bir hizmet sınıfı.
    Bu sınıf, standart bir OpenAI API istemcisi gibi davranır ancak modelden modele
    değişebilen `api_url` ve `api_key` gibi parametreleri dinamik olarak kullanır.
    """

    def send_chat_request(self, messages: List[Dict[str, str]], model_config: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        OpenAI uyumlu bir API'ye sohbet tamamlama isteği gönderir.

        Args:
            messages: Kullanıcı ve asistan mesajlarını içeren bir liste.
            model_config: Modelin API anahtarı, URL'si ve diğer ayarlarını içeren sözlük.

        Returns:
            (başarı_durumu, yanıt_içeriği) şeklinde bir tuple.
        """
        api_key = model_config.get('api_key')
        api_url = model_config.get('api_url', 'https://openrouter.ai/api/v1/chat/completions') # Varsayılan URL
        external_model_name = model_config.get('external_model_name')

        if not api_key or not external_model_name:
            return False, "API anahtarı veya harici model adı eksik."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # OpenRouter için özel başlıkları ekle
        if 'openrouter.ai' in api_url:
            headers.update({
                "HTTP-Referer": self.config.get('APP_SITE_URL', 'http://localhost'),
                "X-Title": self.config.get('APP_NAME', 'Zekai')
            })

        # Mesajları OpenAI formatına uygun hale getir
        formatted_messages = [{'role': msg['role'], 'content': msg['content']} for msg in messages]

        payload = {
            "model": external_model_name,
            "messages": formatted_messages,
            "stream": False # Şimdilik stream desteklenmiyor
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()  # HTTP 2xx olmayan durumlar için hata fırlat

            response_data = response.json()
            # Yanıttan ilk mesajın içeriğini al
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return True, content.strip()
            else:
                return False, f"API yanıtında beklenen 'choices' alanı bulunamadı. Yanıt: {response_data}"

        except requests.exceptions.HTTPError as http_err:
            error_message = f"OpenAI Uyumlu API (HTTP Hatası): {http_err.response.status_code} - {http_err.response.text}"
            current_app.logger.error(error_message)
            return False, f"API sunucusundan bir hata alındı (Kod: {http_err.response.status_code}). Lütfen daha sonra tekrar deneyin."
        except requests.exceptions.RequestException as req_err:
            error_message = f"OpenAI Uyumlu API (İstek Hatası): {req_err}"
            current_app.logger.error(error_message)
            return False, "API sunucusuna bağlanırken bir sorun oluştu. Lütfen ağ bağlantınızı kontrol edin veya daha sonra tekrar deneyin."
        except Exception as e:
            error_message = f"OpenAI Uyumlu API (Beklenmedik Hata): {str(e)}"
            current_app.logger.error(error_message)
            return False, "Beklenmedik bir hata oluştu. Lütfen geliştirici ile iletişime geçin."
