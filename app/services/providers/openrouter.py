# =============================================================================
# OPENROUTER SERVICE (Providers)
# =============================================================================
# OpenRouter entegrasyonu. app.services.providers altına taşındı.
# =============================================================================

import logging
import requests
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class OpenRouterService:
    """OpenRouter API servisi"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = None
        self.site_url = "https://zekai.ai"  # Optional
        self.site_name = "Zekai AI"  # Optional
        
    def set_api_key(self, api_key: str):
        self.api_key = api_key
        
    def set_model(self, model: str):
        self.model = model
        
    def set_site_info(self, site_url: str = None, site_name: str = None):
        if site_url:
            self.site_url = site_url
        if site_name:
            self.site_name = site_name
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            if not self.api_key:
                return {"success": False, "error": "API anahtarı tanımlanmamış"}
            test_result = self.generate_content(prompt="Test", conversation_history=[])
            return {"success": test_result["success"], "message": "OpenRouter bağlantısı başarılı" if test_result["success"] else "Bağlantı hatası", "error": test_result.get("error")}
        except Exception as e:
            logger.error(f"OpenRouter bağlantı testi hatası: {str(e)}")
            return {"success": False, "error": f"Bağlantı testi hatası: {str(e)}"}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        try:
            if not self.api_key:
                return []
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            models = []
            for model in data.get("data", []):
                models.append({
                    "id": model.get("id"),
                    "name": model.get("name"),
                    "description": model.get("description", ""),
                    "context_length": model.get("context_length", 0),
                    "pricing": model.get("pricing", {}),
                    "provider": "OpenRouter"
                })
            return models
        except Exception as e:
            logger.error(f"OpenRouter modelleri alma hatası: {str(e)}")
            return []
    
    def generate_content(self, prompt: str, conversation_history: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        try:
            if not self.api_key:
                return {"success": False, "error": "API anahtarı tanımlanmamış"}
            if not self.model:
                return {"success": False, "error": "Model tanımlanmamış"}
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg.get("is_user", True) else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            messages.append({"role": "user", "content": prompt})
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name
            }
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "top_p": kwargs.get("top_p", 0.9),
                "frequency_penalty": kwargs.get("frequency_penalty", 0),
                "presence_penalty": kwargs.get("presence_penalty", 0)
            }
            data = {k: v for k, v in data.items() if v is not None}
            response = requests.post(url=url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                return {
                    "success": True,
                    "content": content,
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    },
                    "model": self.model,
                    "provider": "OpenRouter"
                }
            else:
                return {"success": False, "error": "Geçersiz yanıt formatı"}
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API isteği hatası: {str(e)}")
            return {"success": False, "error": f"API isteği hatası: {str(e)}"}
        except Exception as e:
            logger.error(f"OpenRouter içerik oluşturma hatası: {str(e)}")
            return {"success": False, "error": f"İçerik oluşturma hatası: {str(e)}"}
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        try:
            models = self.get_available_models()
            for model in models:
                if model["id"] == model_name or model["name"] == model_name:
                    return model
            return {}
        except Exception as e:
            logger.error(f"Model bilgisi alma hatası: {str(e)}")
            return {}
    
    def validate_model(self, model_name: str) -> bool:
        try:
            model_info = self.get_model_info(model_name)
            return bool(model_info)
        except Exception as e:
            logger.error(f"Model doğrulama hatası: {str(e)}")
            return False
