# =============================================================================
# İyileştirilmiş Gemini AI Servis Modülü (Improved Gemini AI Service Module)
# =============================================================================
# Bu modül, Google Gemini API'si ile etkileşim kurmak için optimize edilmiş
# servis sınıfı içerir. Debug print'ler kaldırılmış, logging sistemi eklenmiş
# ve mesaj geçmişi yönetimi iyileştirilmiştir.
#
# İYİLEŞTİRMELER:
# - Debug print'ler kaldırıldı
# - Proper logging sistemi eklendi
# - Mesaj geçmişi formatı standardize edildi
# - Error handling iyileştirildi
# - Performance optimizasyonları
# =============================================================================

import google.generativeai as genai
import logging
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.entities.model import Model as AIModelEntity

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

# =============================================================================
# GEMINISERVICE SINIFI (IMPROVED GEMINISERVICE CLASS)
# =============================================================================
class GeminiService:
    """
    Google Gemini API'si ile etkileşim kurmak için optimize edilmiş servis sınıfı.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        GeminiService'i başlatır ve Gemini API'sini yapılandırır.

        Args:
            api_key (str): Gemini API için kullanılacak API anahtarı.
            config (Optional[Dict]): Uygulama yapılandırması.
        """
        self.api_key = api_key
        self.config = config or {}
        self._model_cache = {}  # Model instance'larını cache'le
        
        if not self.api_key:
            raise ValueError("Gemini API anahtarı gereklidir")

        try:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini API başarıyla yapılandırıldı")
        except Exception as e:
            logger.error(f"Gemini API yapılandırma hatası: {str(e)}")
            raise

    def _get_model_instance(self, model_name: str):
        """
        Model instance'ını cache'den alır veya oluşturur.
        
        Args:
            model_name (str): Gemini model adı
            
        Returns:
            GenerativeModel: Gemini model instance'ı
        """
        if model_name not in self._model_cache:
            try:
                self._model_cache[model_name] = genai.GenerativeModel(model_name)
                logger.debug(f"Model instance oluşturuldu: {model_name}")
            except Exception as e:
                logger.error(f"Model instance oluşturma hatası ({model_name}): {str(e)}")
                raise
                
        return self._model_cache[model_name]

    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Chat history'yi Gemini API formatına dönüştürür.
        
        Args:
            chat_history: Frontend'den gelen chat history
            
        Returns:
            List[Dict]: Gemini API formatında history
        """
        formatted_history = []
        
        for message in chat_history:
            try:
                role = message.get('role', '').lower()
                content = message.get('content', '').strip()
                
                if not content:
                    logger.warning("Boş mesaj içeriği atlandı")
                    continue
                
                # Role mapping: assistant -> model
                api_role = 'model' if role == 'assistant' else role
                
                if api_role not in ['user', 'model']:
                    logger.warning(f"Geçersiz role atlandı: {role}")
                    continue
                
                # Parts formatını kontrol et
                parts_content = message.get('parts')
                if not parts_content:
                    parts_content = [content]
                elif not isinstance(parts_content, list):
                    parts_content = [str(parts_content)]
                
                formatted_message = {
                    'role': api_role,
                    'parts': parts_content
                }
                
                formatted_history.append(formatted_message)
                
            except Exception as e:
                logger.warning(f"Mesaj formatlanırken hata (atlandı): {str(e)}")
                continue
        
        logger.debug(f"Chat history formatlandı: {len(formatted_history)} mesaj")
        return formatted_history

    def _validate_request(self, chat_message: Optional[str], chat_history: List[Dict[str, str]]) -> bool:
        """
        Request verilerini doğrular.
        
        Args:
            chat_message: Yeni mesaj
            chat_history: Mesaj geçmişi
            
        Returns:
            bool: Validation sonucu
        """
        if not chat_message and not chat_history:
            logger.error("Hem chat_message hem de chat_history boş")
            return False
            
        if chat_message and not isinstance(chat_message, str):
            logger.error("chat_message string olmalı")
            return False
            
        if chat_history and not isinstance(chat_history, list):
            logger.error("chat_history liste olmalı")
            return False
            
        return True

    def send_chat_request(self, model_entity: 'AIModelEntity', chat_message: Optional[str], chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Bir sohbet isteğini Gemini API'sine gönderir.

        Args:
            model_entity (AIModelEntity): Kullanılacak AI modelinin entity'si.
            chat_message (Optional[str]): Gönderilecek mevcut kullanıcı mesajı.
            chat_history (List[Dict[str, str]]): Konuşmadaki önceki mesajların listesi.

        Returns:
            Dict[str, Any]: Yanıtı veya bir hata mesajını içeren bir sözlük.
        """
        start_time = datetime.utcnow()
        
        try:
            # Input validation
            if not self._validate_request(chat_message, chat_history):
                return {"error": "Geçersiz request parametreleri", "status_code": 400}

            # Model adını belirle
            target_model_name = getattr(model_entity, 'external_model_name', None) or 'gemini-pro'
            
            logger.info(f"Gemini API request başlatıldı - Model: {target_model_name}")
            
            # Model instance'ını al
            model = self._get_model_instance(target_model_name)
            
            # Chat history'yi formatla
            formatted_history = self._format_chat_history(chat_history)
            
            api_response = None
            
            # Chat session ile mesaj gönder
            if formatted_history:
                # Mevcut history ile chat session başlat
                chat_session = model.start_chat(history=formatted_history)
                
                if chat_message:
                    # Yeni mesaj gönder
                    logger.debug(f"Yeni mesaj gönderiliyor: {len(chat_message)} karakter")
                    api_response = chat_session.send_message(chat_message)
                else:
                    # Sadece history varsa, son model mesajını döndür
                    if formatted_history and formatted_history[-1]['role'] == 'model':
                        last_response = "".join(str(p) for p in formatted_history[-1]['parts'])
                        processing_time = (datetime.utcnow() - start_time).total_seconds()
                        logger.info(f"History'den son yanıt döndürüldü - Süre: {processing_time:.2f}s")
                        return {"response": last_response, "status_code": 200}
                    else:
                        return {"error": "Yeni mesaj gönderilmedi ve history'de model yanıtı yok", "status_code": 400}
                        
            elif chat_message:
                # Sadece yeni mesaj varsa, direkt gönder
                logger.debug(f"Tek mesaj gönderiliyor: {len(chat_message)} karakter")
                api_response = model.generate_content(chat_message)
            else:
                return {"error": "İşlenecek girdi bulunamadı", "status_code": 400}

            # API yanıtını kontrol et
            if not api_response:
                logger.error("Gemini API'sinden yanıt alınamadı")
                return {"error": "Gemini API'sinden yanıt alınamadı", "status_code": 500}

            # Yanıt metnini al
            try:
                response_text = api_response.text
                if not response_text:
                    logger.warning("Gemini API boş yanıt döndürdü")
                    return {"error": "Gemini API boş yanıt döndürdü", "status_code": 500}
                    
            except Exception as e:
                logger.error(f"Gemini API yanıt metni alınamadı: {str(e)}")
                return {"error": f"Yanıt metni alınamadı: {str(e)}", "status_code": 500}

            # İşlem süresini hesapla
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Gemini API request tamamlandı - Süre: {processing_time:.2f}s, Yanıt: {len(response_text)} karakter")
            
            return {
                "response": response_text,
                "status_code": 200,
                "processing_time": processing_time
            }

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            error_message = f"Gemini API hatası: {str(e)}"
            
            logger.error(f"Gemini API request hatası - Süre: {processing_time:.2f}s, Hata: {error_message}")
            
            # Specific error handling
            if "quota" in str(e).lower():
                return {"error": "API quota aşıldı", "details": str(e), "status_code": 429}
            elif "authentication" in str(e).lower() or "api key" in str(e).lower():
                return {"error": "API anahtarı geçersiz", "details": str(e), "status_code": 401}
            elif "not found" in str(e).lower():
                return {"error": "Model bulunamadı", "details": str(e), "status_code": 404}
            else:
                return {"error": error_message, "details": str(e), "status_code": 500}

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Model bilgilerini getirir.
        
        Args:
            model_name (str): Model adı
            
        Returns:
            Dict: Model bilgileri
        """
        try:
            model = self._get_model_instance(model_name)
            return {
                "name": model_name,
                "status": "available",
                "cached": model_name in self._model_cache
            }
        except Exception as e:
            logger.error(f"Model bilgisi alınamadı ({model_name}): {str(e)}")
            return {
                "name": model_name,
                "status": "error",
                "error": str(e)
            }

    def clear_cache(self):
        """Model cache'ini temizler."""
        self._model_cache.clear()
        logger.info("Model cache temizlendi")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_gemini_service(api_key: str, config: Optional[Dict[str, Any]] = None) -> GeminiService:
    """
    GeminiService factory function.
    
    Args:
        api_key: Gemini API anahtarı
        config: Konfigürasyon
        
    Returns:
        GeminiService: Yapılandırılmış servis instance'ı
    """
    try:
        return GeminiService(api_key, config)
    except Exception as e:
        logger.error(f"GeminiService oluşturulamadı: {str(e)}")
        raise

