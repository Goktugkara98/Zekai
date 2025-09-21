# =============================================================================
# GEMINI AI SERVICE (Providers)
# =============================================================================
# Google Gemini entegrasyonu. app.services.providers altına taşındı.
# =============================================================================

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class GeminiService:
    """
    Google Gemini AI ile haberleşme servisi
    """
    
    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.api_key = None
        self.model_name = "gemini-2.5-flash"
        self.max_tokens = 8192
        self.temperature = 0.7
        self.top_p = 0.9
        self.top_k = 40
        
    def set_api_key(self, api_key: str):
        """
        API anahtarını ayarla
        """
        self.api_key = api_key
        
    def set_model(self, model_name: str):
        """
        Model adını ayarla
        """
        self.model_name = model_name
        
    def set_parameters(self, max_tokens: int = None, temperature: float = None, 
                      top_p: float = None, top_k: int = None):
        """
        Model parametrelerini ayarla
        """
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p
        if top_k is not None:
            self.top_k = top_k
            
        # silent update; no logging
    
    def generate_content(self, prompt: str, system_prompt: str = None, 
                        conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Gemini'den içerik üret
        """
        if not self.api_key:
            raise ValueError("API anahtarı ayarlanmamış")
            
        try:
            # Konuşma geçmişini hazırla
            contents = []
            
            # Sistem mesajı varsa ekle
            if system_prompt:
                contents.append({
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Anladım, sistem talimatlarını aldım."}]
                })
            
            # Konuşma geçmişini ekle
            if conversation_history:
                for message in conversation_history:
                    role = "user" if message.get("is_user", True) else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": message.get("content", "")}] 
                    })
            
            # Mevcut mesajı ekle
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
            
            # API isteği hazırla
            url = f"{self.base_url}/models/{self.model_name}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": self.max_tokens,
                    "temperature": self.temperature,
                    "topP": self.top_p,
                    "topK": self.top_k
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                ]
            }
            
            # silent request; no logging
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                
                if "content" in candidate and "parts" in candidate["content"]:
                    generated_text = candidate["content"]["parts"][0].get("text", "")
                    
                    return {
                        "success": True,
                        "content": generated_text,
                        "model": self.model_name,
                        "usage": result.get("usageMetadata", {}),
                        "finish_reason": candidate.get("finishReason", "STOP"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"success": False, "error": "Geçersiz yanıt formatı", "raw_response": result}
            else:
                return {"success": False, "error": "Yanıt alınamadı", "raw_response": result}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "API isteği zaman aşımına uğradı"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"API isteği hatası: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Beklenmeyen hata: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Gemini API bağlantısını test et"""
        if not self.api_key:
            return {"success": False, "error": "API anahtarı ayarlanmamış"}
            
        try:
            result = self.generate_content("Merhaba, nasılsın?")
            if result.get("success"):
                return {"success": True, "message": "Gemini API bağlantısı başarılı", "model": self.model_name}
            else:
                return {"success": False, "error": result.get("error", "Bilinmeyen hata")}
        except Exception as e:
            return {"success": False, "error": f"Bağlantı testi hatası: {str(e)}"}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Kullanılabilir modelleri listele"""
        return [
            {"name": "gemini-2.0-flash-exp", "display_name": "Gemini 2.0 Flash (Experimental)", "description": "En yeni ve hızlı model", "max_tokens": 8192},
            {"name": "gemini-1.5-flash", "display_name": "Gemini 1.5 Flash", "description": "Hızlı ve verimli model", "max_tokens": 8192},
            {"name": "gemini-1.5-pro", "display_name": "Gemini 1.5 Pro", "description": "Gelişmiş yeteneklere sahip model", "max_tokens": 8192},
        ]
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Model bilgilerini al"""
        if not model_name:
            model_name = self.model_name
        models = self.get_available_models()
        for model in models:
            if model["name"] == model_name:
                return model
        return {"name": model_name, "display_name": model_name, "description": "Bilinmeyen model", "max_tokens": 8192}
