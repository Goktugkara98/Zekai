# =============================================================================
# İyileştirilmiş Ana Rotalar Modülü (Improved Main Routes Module)
# =============================================================================
# Bu modül, uygulamanın ana kullanıcı arayüzü (HTML) ve temel API (JSON)
# rotalarını tanımlar. Gemini API entegrasyonu sorunları çözülmüş halidir.
#
# İYİLEŞTİRMELER:
# - CORS desteği eklendi
# - Error handling iyileştirildi
# - Response format standardize edildi
# - Logging sistemi eklendi
# - Input validation güçlendirildi
# =============================================================================

import json
import traceback
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    current_app
)
from flask_cors import CORS, cross_origin

# Uygulama özelindeki içe aktarmalar
from app.repositories.model_repository import ModelRepository
from app.services.ai_model_service import fetch_ai_categories_from_db
from app.services.base_ai_service import BaseAIService
from app.models.base import DatabaseConnection

# =============================================================================
# BLUEPRINT TANIMI VE CORS KONFIGÜRASYONU
# =============================================================================
main_bp = Blueprint(
    name='main',
    import_name=__name__,
    template_folder='../templates',
    static_folder='../static'
)

# CORS desteği ekle
CORS(main_bp, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Başarılı API yanıtı oluşturur"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

def create_error_response(error: str, details: str = None, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    """Hata API yanıtı oluşturur"""
    response = {
        "success": False,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details and current_app.debug:
        response["details"] = details
        
    return response, status_code

def validate_chat_request(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Chat request verilerini doğrular"""
    if not data:
        return False, "İstek gövdesi JSON formatında olmalı ve boş olamaz."
    
    model_id = data.get('aiModelId')
    if not model_id:
        return False, "'aiModelId' alanı zorunludur."
    
    try:
        int(model_id)
    except (ValueError, TypeError):
        return False, "'aiModelId' geçerli bir sayı olmalıdır."
    
    chat_message = data.get('chat_message', '').strip()
    chat_history = data.get('history', [])
    
    if not chat_message and not chat_history:
        return False, "'chat_message' veya 'history' alanlarından en az biri dolu olmalıdır."
    
    # Chat history formatını kontrol et
    if chat_history and not isinstance(chat_history, list):
        return False, "'history' alanı bir liste olmalıdır."
    
    for i, msg in enumerate(chat_history):
        if not isinstance(msg, dict):
            return False, f"'history[{i}]' bir sözlük olmalıdır."
        
        if 'role' not in msg or 'content' not in msg:
            return False, f"'history[{i}]' 'role' ve 'content' alanlarını içermelidir."
    
    return True, ""

# =============================================================================
# ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
# =============================================================================

@main_bp.route('/')
def index_page() -> str:
    """
    Ana sayfayı (index.html) AI kategorileriyle birlikte gösterir.
    """
    ai_categories: List[Dict[str, Any]] = []
    page_title: str = "Ana Sayfa"

    try:
        ai_categories = fetch_ai_categories_from_db()
        if not ai_categories:
            flash("AI kategorileri yüklenirken bir sorun oluştu veya hiç kategori bulunamadı.", "warning")
            ai_categories = [{"id": 0, "name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
    except Exception as e:
        logger.error(f"Ana sayfa kategorileri yüklenirken hata: {str(e)}", exc_info=True)
        flash("Sayfa yüklenirken beklenmedik bir sunucu hatası oluştu.", "danger")
        ai_categories = [{"id": 0, "name": "Sunucu Hatası", "icon": "bi-server", "models": []}]

    return render_template('index.html', ai_categories=ai_categories, title=page_title)

# =============================================================================
# API ROTALARI (API ROUTES - JSON)
# =============================================================================

@main_bp.route('/api/send_message', methods=['POST', 'OPTIONS'])
@cross_origin()
def send_message() -> Tuple[str, int]:
    """
    İyileştirilmiş sohbet mesajı işleme endpoint'i.
    
    Request Format:
    {
        "aiModelId": int,
        "chat_message": str (optional),
        "history": [
            {
                "role": "user|assistant",
                "content": str
            }
        ] (optional)
    }
    
    Response Format:
    {
        "success": bool,
        "message": str,
        "data": {
            "response": str,
            "model_id": int,
            "processing_time": float
        },
        "timestamp": str
    }
    """
    start_time = datetime.utcnow()
    db_connection_instance: Optional[DatabaseConnection] = None
    
    try:
        # OPTIONS request için CORS headers döndür
        if request.method == 'OPTIONS':
            return '', 200
        
        # Request verilerini al ve doğrula
        try:
            data = request.get_json(force=True)
        except Exception:
            return create_error_response("Geçersiz JSON formatı.")
        
        # Input validation
        is_valid, error_message = validate_chat_request(data)
        if not is_valid:
            return create_error_response(error_message)
        
        # Verileri çıkar
        model_id = int(data['aiModelId'])
        chat_message = data.get('chat_message', '').strip() or None
        chat_history = data.get('history', [])
        
        logger.info(f"Chat request received - Model ID: {model_id}, Message: {bool(chat_message)}, History: {len(chat_history)} messages")
        
        # Database bağlantısı oluştur
        db_connection_instance = DatabaseConnection()
        model_repository = ModelRepository(db_connection_instance)
        
        # AI servisini başlat
        base_ai_service = BaseAIService(
            model_repository=model_repository,
            config=current_app.config
        )
        
        # Chat isteğini işle
        response_data = base_ai_service.process_chat_request(
            model_id=model_id,
            chat_message=chat_message,
            chat_history=chat_history
        )
        
        # İşlem süresini hesapla
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Yanıtı kontrol et
        if "error" in response_data:
            logger.warning(f"AI service error: {response_data.get('error')}")
            return create_error_response(
                response_data["error"],
                response_data.get("details"),
                response_data.get("status_code", 500)
            )
        
        # Başarılı yanıt
        result_data = {
            "response": response_data.get("response", ""),
            "model_id": model_id,
            "processing_time": processing_time
        }
        
        logger.info(f"Chat request completed successfully - Processing time: {processing_time:.2f}s")
        
        return jsonify(create_success_response(result_data, "Mesaj başarıyla işlendi")), 200
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {str(e)}")
        return create_error_response("Geçersiz JSON formatı.")
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error in send_message: {str(e)}", exc_info=True)
        return create_error_response(
            "Mesaj işlenirken sunucuda beklenmedik bir hata oluştu.",
            str(e) if current_app.debug else None,
            500
        )
        
    finally:
        if db_connection_instance:
            try:
                db_connection_instance.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")

@main_bp.route('/api/health', methods=['GET'])
@cross_origin()
def health_check() -> Tuple[str, int]:
    """
    API sağlık kontrolü endpoint'i
    """
    try:
        # Database bağlantısını test et
        db_connection = DatabaseConnection()
        db_connection.close()
        
        health_data = {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(create_success_response(health_data, "Sistem sağlıklı")), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_error_response("Sistem sağlık kontrolü başarısız", str(e), 503)

@main_bp.route('/api/models', methods=['GET'])
@cross_origin()
def get_models() -> Tuple[str, int]:
    """
    Mevcut AI modellerini listeler
    """
    try:
        ai_categories = fetch_ai_categories_from_db()
        
        models_data = {
            "categories": ai_categories,
            "total_models": sum(len(cat.get('models', [])) for cat in ai_categories)
        }
        
        return jsonify(create_success_response(models_data, "Modeller başarıyla listelendi")), 200
        
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        return create_error_response("Modeller yüklenirken hata oluştu", str(e), 500)

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@main_bp.errorhandler(404)
def not_found(error):
    """404 hata handler'ı"""
    return create_error_response("Endpoint bulunamadı", status_code=404)

@main_bp.errorhandler(405)
def method_not_allowed(error):
    """405 hata handler'ı"""
    return create_error_response("HTTP metodu desteklenmiyor", status_code=405)

@main_bp.errorhandler(500)
def internal_error(error):
    """500 hata handler'ı"""
    logger.error(f"Internal server error: {str(error)}")
    return create_error_response("Sunucu hatası", status_code=500)

