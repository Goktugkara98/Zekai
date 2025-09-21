# =============================================================================
# CHATS API ROUTES
# =============================================================================
# Chat ile ilgili API endpoint'leri
# =============================================================================

from flask import Blueprint, request, jsonify
import logging
from app.services.chat_service import ChatService
from app.services.providers.gemini import GeminiService
from app.database.db_connection import execute_query
from app.services.auth_service import AuthService
from app.database.repositories.chat_repository import ChatRepository

# Blueprint oluştur
chats_bp = Blueprint('chats', __name__, url_prefix='/api/chats')

# Servisleri başlat
chat_service = ChatService()
gemini_service = GeminiService()

logger = logging.getLogger(__name__)

@chats_bp.route('/create', methods=['POST'])
def create_chat():
    try:
        if not AuthService.is_authenticated():
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        user = AuthService.get_current_user()
        if not user or not user.get('is_active'):
            return jsonify({"success": False, "error": "Hesap aktif değil"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body gerekli"}), 400

        model_id = data.get('model_id')
        title = data.get('title')
        if not model_id:
            return jsonify({"success": False, "error": "model_id gerekli"}), 400

        result = chat_service.create_chat(model_id, title, user_id=user['user_id'])
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Chat oluşturma API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500

@chats_bp.route('/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    try:
        if not AuthService.is_authenticated():
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        user = AuthService.get_current_user()
        if not user:
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        result = chat_service.get_chat(chat_id, user_id=user['user_id'])
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except Exception as e:
        logger.error(f"Chat alma API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500

@chats_bp.route('/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    try:
        if not AuthService.is_authenticated():
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        user = AuthService.get_current_user()
        if not user:
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        result = chat_service.get_chat_messages(chat_id, limit, offset, user_id=user['user_id'])
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except Exception as e:
        logger.error(f"Mesaj alma API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500

@chats_bp.route('/<chat_id>/send', methods=['POST'])
def send_message(chat_id):
    try:
        if not AuthService.is_authenticated():
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        user = AuthService.get_current_user()
        if not user or not user.get('is_active'):
            return jsonify({"success": False, "error": "Hesap aktif değil"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body gerekli"}), 400

        message = data.get('message')
        model_id = data.get('model_id')
        if not message:
            return jsonify({"success": False, "error": "message gerekli"}), 400
        if not model_id:
            return jsonify({"success": False, "error": "model_id gerekli"}), 400

        chat_result = chat_service.get_chat(chat_id, user_id=user['user_id'])
        if not chat_result.get('success'):
            return jsonify({"success": False, "error": "Chat bulunamadı veya erişim yok"}), 404

        chat_obj = chat_result.get('chat') or {}
        chat_model_id = chat_obj.get('model_id')
        if not chat_model_id:
            return jsonify({"success": False, "error": "Chat için model atanmadı"}), 400

        model_id = chat_model_id

        model_sql = "SELECT model_name, provider_name, api_key FROM models WHERE model_id = %s"
        model_result = execute_query(model_sql, (model_id,), fetch=True)
        if not model_result:
            return jsonify({"success": False, "error": "Model bulunamadı"}), 404

        model_data = model_result[0]
        model_name = model_data["model_name"]
        provider_name = model_data["provider_name"]
        api_key = model_data["api_key"]
        if not api_key:
            return jsonify({"success": False, "error": "Model için API anahtarı tanımlanmamış"}), 400

        result = chat_service.send_message(chat_id, message, model_id, api_key, user_id=user['user_id'])
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Mesaj gönderme API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500

@chats_bp.route('/list', methods=['GET'])
def get_user_chats():
    try:
        if not AuthService.is_authenticated():
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        user = AuthService.get_current_user()
        if not user:
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        active_param = request.args.get('active', default='true').lower()
        if active_param in ('true', '1', 'yes'): active = True
        elif active_param in ('false', '0', 'no'): active = False
        else: active = None

        result = chat_service.get_user_chats(user_id=user['user_id'], active=active, limit=limit, offset=offset)
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Chat listesi alma API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500

@chats_bp.route('/gemini/test/<model_id>', methods=['POST'])
def test_gemini_connection(model_id):
    try:
        model_sql = "SELECT model_name, api_key FROM models WHERE model_id = %s"
        model_result = execute_query(model_sql, (model_id,), fetch=True)
        if not model_result:
            return jsonify({"success": False, "error": "Model bulunamadı"}), 404

        model_name = model_result[0]["model_name"]
        api_key = model_result[0]["api_key"]
        if not api_key:
            return jsonify({"success": False, "error": "Model için API anahtarı tanımlanmamış"}), 400

        gemini_service.set_api_key(api_key)
        gemini_service.set_model(model_name)
        result = gemini_service.test_connection()
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Gemini test API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500

@chats_bp.route('/gemini/models', methods=['GET'])
def get_gemini_models():
    try:
        models = gemini_service.get_available_models()
        return jsonify({"success": True, "models": models}), 200
    except Exception as e:
        logger.error(f"Gemini modelleri alma API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500


@chats_bp.route('/<chat_id>/delete', methods=['DELETE'])
def soft_delete_chat(chat_id):
    """
    Bir sohbeti pasif hale getirir (is_active = FALSE).
    Frontend, X ile kapatırken bu endpoint'i çağırır.
    """
    try:
        # Kimlik doğrulama
        if not AuthService.is_authenticated():
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        user = AuthService.get_current_user()
        if not user:
            return jsonify({"success": False, "error": "Yetkisiz"}), 401

        # Sohbet kullanıcının mı kontrol et
        chat = ChatRepository.get_chat(chat_id, user_id=user['user_id'])
        if not chat:
            return jsonify({"success": False, "error": "Chat bulunamadı veya erişim yok"}), 404

        # Pasif hale getir
        ok = ChatRepository.set_active(chat_id, False)
        if ok:
            return jsonify({"success": True, "chat_id": chat_id, "is_active": False}), 200
        else:
            return jsonify({"success": False, "error": "Chat güncellenemedi"}), 400
    except Exception as e:
        logger.error(f"Chat soft delete API hatası: {str(e)}")
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"}), 500
