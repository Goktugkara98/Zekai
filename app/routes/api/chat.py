# =============================================================================
# CHAT API ROUTES
# =============================================================================
# Bu dosya, chat ile ilgili API endpoint'lerini tanımlar.
# =============================================================================

from flask import Blueprint, request, jsonify
import logging
from app.services.chat_service import ChatService
from app.services.gemini_service import GeminiService
from app.database.db_connection import execute_query

# Blueprint oluştur
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Servisleri başlat
chat_service = ChatService()
gemini_service = GeminiService()

logger = logging.getLogger(__name__)

@chat_bp.route('/create', methods=['POST'])
def create_chat():
    """
    Yeni chat oluştur
    
    Request Body:
        {
            "model_id": int,
            "title": str (opsiyonel)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body gerekli"
            }), 400
        
        model_id = data.get('model_id')
        title = data.get('title')
        
        if not model_id:
            return jsonify({
                "success": False,
                "error": "model_id gerekli"
            }), 400
        
        # Chat oluştur
        result = chat_service.create_chat(model_id, title)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Chat oluşturma API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """
    Chat bilgilerini al
    
    URL Parameters:
        chat_id: Chat ID'si
    """
    try:
        result = chat_service.get_chat(chat_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Chat alma API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    """
    Chat mesajlarını al
    
    URL Parameters:
        chat_id: Chat ID'si
        
    Query Parameters:
        limit: Maksimum mesaj sayısı (varsayılan: 50)
        offset: Başlangıç offset'i (varsayılan: 0)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = chat_service.get_chat_messages(chat_id, limit, offset)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Mesaj alma API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/<chat_id>/send', methods=['POST'])
def send_message(chat_id):
    """
    Mesaj gönder ve AI yanıtı al
    
    URL Parameters:
        chat_id: Chat ID'si
        
    Request Body:
        {
            "message": str,
            "model_id": int
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body gerekli"
            }), 400
        
        message = data.get('message')
        model_id = data.get('model_id')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "message gerekli"
            }), 400
        
        if not model_id:
            return jsonify({
                "success": False,
                "error": "model_id gerekli"
            }), 400
        
        # Model bilgilerini ve API anahtarını al
        model_sql = "SELECT model_name, provider_name, api_key FROM models WHERE model_id = %s"
        model_result = execute_query(model_sql, (model_id,), fetch=True)
        
        if not model_result:
            return jsonify({
                "success": False,
                "error": "Model bulunamadı"
            }), 404
        
        model_data = model_result[0]
        model_name = model_data["model_name"]
        provider_name = model_data["provider_name"]
        api_key = model_data["api_key"]
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Model için API anahtarı tanımlanmamış"
            }), 400
        
        # Mesajı gönder
        result = chat_service.send_message(chat_id, message, model_id, api_key)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Mesaj gönderme API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/list', methods=['GET'])
def get_user_chats():
    """
    Kullanıcının chat'lerini al
    
    Query Parameters:
        limit: Maksimum chat sayısı (varsayılan: 20)
        offset: Başlangıç offset'i (varsayılan: 0)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = chat_service.get_user_chats(limit, offset)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Chat listesi alma API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/<chat_id>/delete', methods=['DELETE'])
def delete_chat(chat_id):
    """
    Chat'i sil
    
    URL Parameters:
        chat_id: Chat ID'si
    """
    try:
        result = chat_service.delete_chat(chat_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Chat silme API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/gemini/test/<model_id>', methods=['POST'])
def test_gemini_connection(model_id):
    """
    Gemini API bağlantısını test et
    
    URL Parameters:
        model_id: Model ID'si
    """
    try:
        # Model bilgilerini ve API anahtarını al
        model_sql = "SELECT model_name, api_key FROM models WHERE model_id = %s"
        model_result = execute_query(model_sql, (model_id,), fetch=True)
        
        if not model_result:
            return jsonify({
                "success": False,
                "error": "Model bulunamadı"
            }), 404
        
        model_name = model_result[0]["model_name"]
        api_key = model_result[0]["api_key"]
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Model için API anahtarı tanımlanmamış"
            }), 400
        
        # Gemini bağlantısını test et
        gemini_service.set_api_key(api_key)
        gemini_service.set_model(model_name)
        result = gemini_service.test_connection()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Gemini test API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500

@chat_bp.route('/gemini/models', methods=['GET'])
def get_gemini_models():
    """
    Kullanılabilir Gemini modellerini listele
    """
    try:
        models = gemini_service.get_available_models()
        
        return jsonify({
            "success": True,
            "models": models
        }), 200
        
    except Exception as e:
        logger.error(f"Gemini modelleri alma API hatası: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Sunucu hatası: {str(e)}"
        }), 500
