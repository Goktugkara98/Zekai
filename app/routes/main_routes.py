# =============================================================================
# Ana Rotalar Modülü (Main Routes Module)
# =============================================================================
# Bu modül, uygulamanın ana kullanıcı arayüzü ve temel API rotalarını tanımlar.
# Ana sayfa gösterimi ve sohbet API'si gibi işlevleri içerir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Blueprint Tanımı (Blueprint Definition)
# 3. Yardımcı Fonksiyonlar (Utility Functions)
#    3.1. generate_mock_response         : Sahte (mock) AI yanıtı üretir.
#    3.2. extract_response_by_path       : JSON yanıtından belirli bir yola göre veri çıkarır.
# 4. Arayüz Rotaları (View Routes - HTML Rendering)
#    4.1. / (GET)                        : Ana sayfa (index.html).
# 5. API Rotaları (API Routes - JSON)
#    5.1. POST /api/chat/send            : Sohbet mesajlarını işler ve AI yanıtı döndürür.
#    5.2. POST /mock_gemini_api/...      : (Geliştirme/Test) Sahte Gemini API yanıtı üretir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from flask import Blueprint, render_template, request, jsonify, flash
# requests importu artık servislerde olacak, buradan kaldırılabilir veya kalabilir (eğer başka yerde kullanılıyorsa)
# import requests
import json
import os
from typing import Dict, Any, Optional, List

# Servis katmanı ve model importları
from app.services.ai_model_service import (
    get_ai_model_api_details,
    fetch_ai_categories_from_db,
)
# AI Service Factory
from app.services import base_ai_service # <<< YENİ IMPORT

try:
    from app.repositories.user_message_repository import UserMessageRepository
except ImportError:
    UserMessageRepository = None

# 2. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 3. Yardımcı Fonksiyonlar (Utility Functions)
# =============================================================================

# generate_mock_response ve extract_response_by_path fonksiyonları BaseAIService'e taşındı.
# Ancak, bu fonksiyonlar hala burada kullanılıyorsa, aşağıda tutulabilir.

def generate_mock_response(user_message: str) -> str:
    """Gerçek API kullanılamadığında sahte bir yanıt üretir."""
    response = (f"Bu, mesajınıza sahte bir yanıttır: '{user_message}'. "
                "Gerçek AI servisi şu anda kullanılamıyor.")
    return response

def extract_response_by_path(response_json: Dict, path: str) -> Any:
    """İç içe bir JSON nesnesinden nokta notasyonlu bir yol kullanarak bir değer çıkarır."""
    try:
        parts = path.split('.')
        current_data = response_json
        for part in parts:
            if part.isdigit() and isinstance(current_data, list):
                index = int(part)
                if index >= len(current_data):
                    return f"Yanıt formatı hatası: İndeks {index} geçersiz."
                current_data = current_data[index]
            elif '[' in part and part.endswith(']'):
                key, index_str_with_bracket = part.split('[', 1)
                index_str = index_str_with_bracket[:-1]
                if not index_str.isdigit():
                    return f"Yanıt formatı hatası: Geçersiz indeks '{index_str}'."
                index = int(index_str)

                if key:
                    if not isinstance(current_data, dict) or key not in current_data:
                        return f"Yanıt formatı hatası: Anahtar '{key}' bulunamadı."
                    current_data = current_data[key]

                if not isinstance(current_data, list) or index >= len(current_data):
                    return f"Yanıt formatı hatası: İndeks {index} geçersiz."
                current_data = current_data[index]
            else:
                if not isinstance(current_data, dict) or part not in current_data:
                    return f"Yanıt formatı hatası: Anahtar '{part}' bulunamadı."
                current_data = current_data[part]
        return current_data
    except (KeyError, IndexError, TypeError) as e:
        return f"AI yanıtı işlenirken hata (format uyumsuzluğu): {str(e)}"
    except Exception as e:
        # Beklenmedik hatalar için genel bir mesaj döndürülür.
        # Bu hataların ayrıca loglanması veya izlenmesi gerekebilir.
        return "AI yanıtı işlenirken beklenmedik bir hata oluştu."

# 4. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================

# 4.1. / (GET) - Ana Sayfa
# -----------------------------------------------------------------------------
@main_bp.route('/')
def index_page():
    """Ana sayfayı (index.html) AI kategorileriyle birlikte gösterir."""
    ai_categories = []
    try:
        ai_categories = fetch_ai_categories_from_db()
        if not ai_categories:
            flash("AI kategorileri yüklenirken bir sorun oluştu veya hiç kategori bulunamadı. Lütfen daha sonra tekrar deneyin.", "warning")
            # Kullanıcıya boş bir liste yerine bilgilendirici bir kategori gösterilebilir
            ai_categories = [{"name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
    except Exception:
        # Gerçek uygulamada bu hata loglanmalıdır.
        flash("Sayfa yüklenirken beklenmedik bir sunucu hatası oluştu.", "danger")
        ai_categories = [{"name": "Sunucu Hatası", "icon": "bi-server", "models": []}]
    
    return render_template('index.html', ai_categories=ai_categories, title="Ana Sayfa")

# 5. API Rotaları (API Routes - JSON)
# =============================================================================

# 5.1. POST /api/chat/send - Sohbet Mesajlarını İşler
# -----------------------------------------------------------------------------
@main_bp.route('/api/chat/send', methods=['POST'])
def handle_chat_message_api():
    """
    Kullanıcıdan gelen sohbet mesajını alır, ilgili AI modelinin servisine yönlendirir,
    yanıtı alır ve kullanıcıya JSON formatında döndürür. Etkileşimi veritabanına kaydeder.
    """
    data = request.json
    if not data:
        return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

    user_message = data.get('message') # Optional, history might be primary
    ai_model_id_str = data.get('aiModelId')
    chat_id = data.get('chatId')
    conversation_history_raw = data.get('history', []) #

    if not ai_model_id_str:
        return jsonify({"error": "AI Model ID'si eksik."}), 400 #
    if not chat_id:
        return jsonify({"error": "Sohbet ID'si eksik."}), 400 #
    # Mesaj boş olabilir eğer sadece geçmiş ile devam ediliyorsa, bu kontrolü servise bırakalım.
    # if not user_message and not conversation_history_raw:
    #     return jsonify({"error": "Kullanıcı mesajı veya konuşma geçmişi eksik."}), 400

    # Normalize conversation history from frontend
    normalized_history: List[Dict[str, str]] = []
    if isinstance(conversation_history_raw, list):
        for msg in conversation_history_raw:
            if isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content') # Frontend should send 'content'
                # Fallback for older format if 'parts' is still sent from client
                if content is None and 'parts' in msg and isinstance(msg.get('parts'), list) and \
                     len(msg['parts']) > 0 and isinstance(msg['parts'][0], dict) and \
                     'text' in msg['parts'][0]:
                    content = msg['parts'][0]['text'] #
                
                if role and content is not None: # Ensure content is not None
                    normalized_history.append({'role': str(role), 'content': str(content)})
    
    # Get AI model details (this should now ideally include 'provider_type')
    try:
        model_details_raw = get_ai_model_api_details(ai_model_id_str) #
        model_details = model_details_raw.to_dict() if hasattr(model_details_raw, 'to_dict') \
                        else (model_details_raw if isinstance(model_details_raw, dict) else None)

        if not model_details or not model_details.get('api_url'): # api_url is crucial
            return jsonify({"error": f"AI modeli için yapılandırma bulunamadı veya eksik: {ai_model_id_str}"}), 500
    except Exception as e_fetch_model:
        # Log this error server-side
        print(f"Error fetching model details for {ai_model_id_str}: {str(e_fetch_model)}")
        return jsonify({"error": f"AI modeli yapılandırması alınırken sunucu hatası: {ai_model_id_str}"}), 500

    # Get the appropriate AI service instance
    ai_service = get_ai_service(model_details)

    if not ai_service:
        error_msg = f"Belirtilen AI modeli için uygun servis bulunamadı (ID: {ai_model_id_str}, Provider: {model_details.get('provider_type', 'Bilinmiyor')})."
        # Log this critical error
        print(error_msg)
        return jsonify({"error": error_msg }), 501 # 501 Not Implemented

    use_mock_api = os.environ.get('USE_MOCK_API', 'false').lower() == 'true' #
    
    ai_response_text = "Yanıt alınamadı."
    model_name_for_log = model_details.get('name', "Yapılandırma Hatası Modeli") #
    request_payload_for_log = {}
    response_json_for_log = {}
    api_status_code = 500

    try:
        # Delegate to the specific AI service's handle_chat method
        ai_response_text, response_json_for_log, api_status_code, \
        request_payload_for_log, model_name_for_log = ai_service.handle_chat(
            user_message=user_message, # Can be None if only history is used
            conversation_history=normalized_history,
            model_details=model_details,
            chat_id=chat_id,
            use_mock_api=use_mock_api
        )

    except Exception as e_service_call:
        # This catches unexpected errors from within the service call itself
        # or if the service call is not properly implemented.
        print(f"Critical error during AI service call for model {model_name_for_log}: {str(e_service_call)}")
        api_status_code = 500
        ai_response_text = f"AI servisiyle iletişimde beklenmedik bir sunucu hatası oluştu: {str(e_service_call)}"
        response_json_for_log = {"error_message_critical_service_call": ai_response_text, "status_code": api_status_code}

    # Log the interaction to the database
    if UserMessageRepository:
        try:
            user_msg_repo = UserMessageRepository() #
            
            # Determine the primary message sent by the user for logging
            logged_user_message = user_message
            if not logged_user_message and normalized_history:
                # Find the last user message from history if current message is empty
                for i in range(len(normalized_history) - 1, -1, -1):
                    if normalized_history[i].get('role') == 'user':
                        logged_user_message = normalized_history[i].get('content')
                        break
            if not logged_user_message: # Fallback if still no message
                logged_user_message = " " # Ensure not None for DB

            prompt_to_log = json.dumps(normalized_history, ensure_ascii=False) if normalized_history else None
            request_json_to_log = json.dumps(request_payload_for_log, ensure_ascii=False) if request_payload_for_log else None
            response_json_to_log = json.dumps(response_json_for_log, ensure_ascii=False) if response_json_for_log else None
            
            log_status = 'error' if api_status_code >= 400 else 'success'
            error_message_to_log = ai_response_text if log_status == 'error' and not (use_mock_api and api_status_code == 200) else None
            
            user_msg_repo.insert_user_message(
                session_id=chat_id, user_message=str(logged_user_message),
                ai_response=str(ai_response_text) if ai_response_text else " ",
                ai_model_name=str(model_name_for_log), prompt=prompt_to_log,
                request_json=request_json_to_log, response_json=response_json_to_log,
                status=log_status, error_message=error_message_to_log
            ) #
        except Exception as e_db_log:
            # Veritabanına loglama hatası kullanıcıya yansıtılmamalı,
            # ancak gerçek bir uygulamada bu hata izlenmelidir.
            print(f"Database logging failed for chat {chat_id}: {str(e_db_log)}")
            pass

    if api_status_code >= 400 and not (use_mock_api and api_status_code == 200): # Don't return error for successful mock
        return jsonify({"error": ai_response_text, "chatId": chat_id}), api_status_code

    return jsonify({"response": str(ai_response_text), "chatId": chat_id})


# 5.2. POST /mock_gemini_api/... - Sahte Gemini API Yanıtı
# -----------------------------------------------------------------------------
# This mock endpoint can remain if you use it for direct testing of the mock API behavior
# or if your frontend is hardcoded to hit this for specific mock scenarios.
# Otherwise, the 'use_mock_api' flag handled by the services should cover general mocking.
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
def mock_gemini_generate_content_route():
    """
    Geliştirme ve test amaçlı sahte bir Gemini API endpoint'i.
    Bu, doğrudan bu URL'ye yapılan istekleri mocklar.
    Genel mocklama artık servisler içinde `use_mock_api` ile de yönetiliyor.
    """
    data = request.json
    if not data:
        return jsonify({"error": "İstek gövdesi boş olamaz (JSON bekleniyor)."}), 400 #

    try:
        user_text = "bir mesaj (payload'dan alınamadı)"
        if "contents" in data and isinstance(data["contents"], list) and \
           len(data["contents"]) > 0 and isinstance(data["contents"][-1], dict) and \
           "parts" in data["contents"][-1] and \
           isinstance(data["contents"][-1]["parts"], list) and \
           len(data["contents"][-1]["parts"]) > 0 and isinstance(data["contents"][-1]["parts"][0], dict) and \
           "text" in data["contents"][-1]["parts"][0]:
            user_text = data["contents"][-1]["parts"][0]["text"] #

        mock_response_text = f"Bu, Gemini (gemini-2.0-flash modeli - DİREKT SAHTE YANIT) tarafından mesajınıza verilen sahte bir yanıttır: '{user_text}'" #
        
        gemini_like_response = {
            "candidates": [{"content": {"parts": [{"text": mock_response_text}], "role": "model"}, #
                "finishReason": "STOP", "index": 0,
                "safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }],
            "promptFeedback": {"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]}
        }
        return jsonify(gemini_like_response) #

    except (KeyError, IndexError, TypeError): #
        return jsonify({"error": "Geçersiz payload formatı. Beklenen: {'contents': [{'parts':[{'text': '...'}]}]}"}), 400 #
    except Exception:
        return jsonify({"error": "Sahte Gemini API'sinde beklenmedik bir hata oluştu."}), 500 #
