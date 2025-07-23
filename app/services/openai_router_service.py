import requests
import json
from typing import List, Dict, Any, Tuple, Optional
from flask import current_app

class OpenAIRouterService:
    """
    OpenAI uyumlu API'ler (OpenRouter, Together, vb.) için genel bir hizmet sınıfı.
    Bu sınıf, standart bir OpenAI API istemcisi gibi davranır ancak modelden modele
    değişebilen `api_url` ve `api_key` gibi parametreleri dinamik olarak kullanır.
    """
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.config = config

    def send_chat_request(self, model_entity, chat_message: Optional[str], chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        OpenAI uyumlu bir API'ye sohbet tamamlama isteği gönderir.

        Args:
            model_entity: Model varlığı (API anahtarı, URL'si ve diğer ayarları içerir).
            chat_message: Kullanıcının yeni mesajı.
            chat_history: Önceki sohbet geçmişi.

        Returns:
            Yanıt verisi içeren bir sözlük.
        """
        api_url = getattr(model_entity, 'api_url', 'https://openrouter.ai/api/v1/chat/completions')
        external_model_name = getattr(model_entity, 'external_model_name', None)

        if not self.api_key or not external_model_name:
            return {"error": "API anahtarı veya harici model adı eksik.", "status_code": 400}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # OpenRouter için özel başlıkları ekle
        if 'openrouter.ai' in api_url:
            headers.update({
                "HTTP-Referer": self.config.get('APP_SITE_URL', 'http://localhost'),
                "X-Title": self.config.get('APP_NAME', 'Zekai')
            })

        # Mesajları OpenAI formatına uygun hale getir
        messages = []
        for msg in chat_history:
            messages.append({'role': msg['role'], 'content': msg['content']})
        
        if chat_message:
            messages.append({'role': 'user', 'content': chat_message})

        payload = {
            "model": external_model_name,
            "messages": messages,
            "stream": False # Şimdilik stream desteklenmiyor
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()  # HTTP 2xx olmayan durumlar için hata fırlat

            response_data = response.json()
            # Yanıttan ilk mesajın içeriğini al
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return {"reply": content.strip()}
            else:
                return {"error": f"API yanıtında beklenen 'choices' alanı bulunamadı. Yanıt: {response_data}", "status_code": 500}

        except requests.exceptions.HTTPError as http_err:
            error_message = f"OpenAI Uyumlu API (HTTP Hatası): {http_err.response.status_code} - {http_err.response.text}"
            current_app.logger.error(error_message)
            return {"error": f"API sunucusundan bir hata alındı (Kod: {http_err.response.status_code}). Lütfen daha sonra tekrar deneyin.", "status_code": 500}
        except requests.exceptions.RequestException as req_err:
            error_message = f"OpenAI Uyumlu API (İstek Hatası): {req_err}"
            current_app.logger.error(error_message)
            return {"error": "API sunucusuna bağlanırken bir sorun oluştu. Lütfen ağ bağlantınızı kontrol edin veya daha sonra tekrar deneyin.", "status_code": 500}
        except Exception as e:
            error_message = f"OpenAI Uyumlu API (Beklenmedik Hata): {str(e)}"
            current_app.logger.error(error_message)
            return {"error": "Beklenmedik bir hata oluştu. Lütfen geliştirici ile iletişime geçin.", "status_code": 500}
