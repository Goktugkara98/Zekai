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
import requests  # Harici API istekleri için
import json      # JSON işleme için
import os        # Ortam değişkenlerini okumak için
from typing import Dict, Any, Optional, List  # Type hints için

# Servis katmanı ve model importları
from app.services.ai_model_service import (
    get_ai_model_api_details,
    fetch_ai_categories_from_db,
)
try:
    from app.repositories.user_message_repository import UserMessageRepository
except ImportError:
    UserMessageRepository = None
    # UserMessageRepository import edilemezse, veritabanı kaydı yapılamayacaktır.
    # Bu durum, ilgili fonksiyonlarda kontrol edilir.

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
    Kullanıcıdan gelen sohbet mesajını alır, ilgili AI modeline gönderir,
    yanıtı alır ve kullanıcıya JSON formatında döndürür. Etkileşimi veritabanına kaydeder.
    """
    data = request.json
    if not data:
        return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

    user_message = data.get('message')
    ai_model_id_str = data.get('aiModelId')
    chat_id = data.get('chatId')
    conversation_history = data.get('history', [])

    if not user_message and not conversation_history:
        return jsonify({"error": "Kullanıcı mesajı veya konuşma geçmişi eksik."}), 400
    if not ai_model_id_str:
        return jsonify({"error": "AI Model ID'si eksik."}), 400
    if not chat_id:
        return jsonify({"error": "Sohbet ID'si eksik."}), 400

    normalized_history = []
    if isinstance(conversation_history, list):
        for msg in conversation_history:
            if isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content')
                if content is None and 'parts' in msg and isinstance(msg.get('parts'), list) and \
                     len(msg['parts']) > 0 and isinstance(msg['parts'][0], dict) and \
                     'text' in msg['parts'][0]:
                    content = msg['parts'][0]['text']
                if role and content is not None:
                    normalized_history.append({'role': str(role), 'content': str(content)})

    use_mock_api = os.environ.get('USE_MOCK_API', 'false').lower() == 'true'
    
    ai_response_text = "Yanıt alınamadı."
    model_name_for_log = "Bilinmeyen Model"
    request_payload_for_log = {}
    response_json_for_log = {}
    api_status_code = 500

    try:
        model_details_raw = get_ai_model_api_details(ai_model_id_str)
        model_details = model_details_raw.to_dict() if hasattr(model_details_raw, 'to_dict') \
                        else (model_details_raw if isinstance(model_details_raw, dict) else None)

        if not model_details or not model_details.get('api_url'):
            return jsonify({"error": f"AI modeli için yapılandırma bulunamadı: {ai_model_id_str}"}), 500
        
        model_name_for_log = model_details.get('name', 'Yapılandırma Hatası Modeli')
        api_url = model_details.get('api_url')
        api_key = model_details.get('api_key')
        
        if api_url and api_key and 'generativelanguage.googleapis.com' in api_url:
            api_url = f"{api_url}{'&' if '?' in api_url else '?'}key={api_key}"
        
        request_method = model_details.get('request_method', 'POST').upper()
        response_path = model_details.get('response_path')
        
        headers_str = model_details.get('request_headers')
        headers = {}
        if headers_str:
            try:
                if isinstance(headers_str, str): headers = json.loads(headers_str)
                elif isinstance(headers_str, dict): headers = headers_str
                if not isinstance(headers, dict): headers = {}
            except json.JSONDecodeError:
                headers = {}
        
        if not headers.get("Content-Type") and request_method == 'POST':
             headers["Content-Type"] = "application/json"

        request_body_template_raw = model_details.get('request_body_template')
        request_body_template_str = json.dumps(request_body_template_raw) if isinstance(request_body_template_raw, dict) \
                                    else (request_body_template_raw if isinstance(request_body_template_raw, str) else None)
        
        if not request_body_template_str:
            return jsonify({"error": f"Model '{model_name_for_log}' için istek şablonu eksik."}), 500

        final_history_for_payload = list(normalized_history)
        if user_message:
            current_turn_user_message_obj = {'role': 'user', 'content': user_message}
            if not final_history_for_payload or final_history_for_payload[-1] != current_turn_user_message_obj:
                final_history_for_payload.append(current_turn_user_message_obj)
        
        try:
            payload_template_dict = json.loads(request_body_template_str)
            
            def fill_template(template_part, history, last_message_text):
                if isinstance(template_part, dict):
                    return {k: fill_template(v, history, last_message_text) for k, v in template_part.items()}
                elif isinstance(template_part, list):
                    if len(template_part) == 1 and template_part[0] == "$messages":
                        return history
                    return [fill_template(item, history, last_message_text) for item in template_part]
                elif isinstance(template_part, str):
                    if template_part == "$messages": return history
                    if template_part == "$message": return last_message_text if last_message_text else ""
                    if "{user_prompt}" in template_part:
                        return template_part.replace("{user_prompt}", last_message_text if last_message_text else "")
                    return template_part
                return template_part

            message_to_send_in_template = user_message
            if not message_to_send_in_template and final_history_for_payload:
                for i in range(len(final_history_for_payload) - 1, -1, -1):
                    if final_history_for_payload[i].get('role') == 'user':
                        message_to_send_in_template = final_history_for_payload[i].get('content')
                        break
            
            request_payload_for_log = fill_template(payload_template_dict, final_history_for_payload, message_to_send_in_template)

        except json.JSONDecodeError:
            return jsonify({"error": "AI modeli için geçersiz istek şablonu yapılandırması."}), 500

        if use_mock_api:
            ai_response_text = generate_mock_response(user_message if user_message else "geçmişten bir mesaj")
            response_json_for_log = {"mock_response": ai_response_text, "candidates": [{"content": {"parts": [{"text": ai_response_text}]}}]}
            api_status_code = 200
        else:
            api_response = None
            try:
                if request_method == 'POST':
                    api_response = requests.post(api_url, json=request_payload_for_log, headers=headers, timeout=30)
                elif request_method == 'GET':
                    api_response = requests.get(api_url, params=request_payload_for_log, headers=headers, timeout=30)
                else:
                    return jsonify({"error": f"Desteklenmeyen istek metodu: {request_method}"}), 400

                api_status_code = api_response.status_code
                api_response.raise_for_status()
                
                try:
                    response_json_for_log = api_response.json()
                except json.JSONDecodeError:
                    response_json_for_log = {"error": "API response was not valid JSON", "raw_response": api_response.text}
                    ai_response_text = "API'den gelen yanıt işlenemedi (JSON formatında değil)."
                    if api_status_code < 300: api_status_code = 502 # Bad Gateway
                
                if response_path and isinstance(response_json_for_log, dict): # response_path sadece dict ise anlamlı
                    extracted_value = extract_response_by_path(response_json_for_log, response_path)
                    if isinstance(extracted_value, str) and "Yanıt formatı hatası:" in extracted_value:
                        ai_response_text = extracted_value
                        if api_status_code < 300 : api_status_code = 502 # Bad Gateway
                    elif extracted_value is not None :
                        ai_response_text = str(extracted_value)
                    else:
                        ai_response_text = "AI modelinden anlamlı bir yanıt alınamadı."
                        if api_status_code < 300 : api_status_code = 204 # No Content
                elif isinstance(response_json_for_log, dict) and not response_path:
                    ai_response_text = json.dumps(response_json_for_log, ensure_ascii=False)
                elif not isinstance(response_json_for_log, dict) and not response_path:
                     ai_response_text = str(response_json_for_log)
                elif not response_path and api_status_code < 300 and ai_response_text == "Yanıt alınamadı.":
                    # Path yok, başarılı yanıt, ama JSON da düzgün ayıklanamadıysa veya response_json_for_log dict değilse
                     ai_response_text = "API yanıtı alındı ancak içerik ayıklanamadı (path eksik)."
                elif api_status_code >= 300 and ai_response_text == "Yanıt alınamadı.": # Hata durumu ve henüz özel mesaj yoksa
                     ai_response_text = f"API Hatası: {api_status_code}"


            except requests.exceptions.HTTPError as http_err:
                raw_response_text = http_err.response.text if http_err.response else "Yanıt içeriği yok"
                ai_response_text = f"AI servisinden hata alındı (Kod: {api_status_code}). Detay: {raw_response_text[:100]}"
                response_json_for_log = {"error_message_from_api": ai_response_text, "status_code": api_status_code, "raw_error_response": raw_response_text}
            except requests.exceptions.RequestException as req_err:
                api_status_code = 503 # Service Unavailable
                ai_response_text = f"AI servisine ulaşılamadı: {str(req_err)}"
                response_json_for_log = {"error_message_internal": ai_response_text, "status_code": api_status_code}
            except Exception as e_inner_api:
                api_status_code = 500
                ai_response_text = f"AI yanıtı işlenirken beklenmedik bir hata oluştu: {str(e_inner_api)}"
                response_json_for_log = {"error_message_internal": ai_response_text, "status_code": api_status_code}

    except Exception as e_outer:
        api_status_code = 500
        ai_response_text = f"Beklenmedik bir sunucu hatası oluştu: {str(e_outer)}"
        response_json_for_log = {"error_message_critical": ai_response_text, "status_code": api_status_code}

    if UserMessageRepository:
        try:
            user_msg_repo = UserMessageRepository()
            prompt_to_log = json.dumps(final_history_for_payload, ensure_ascii=False) if final_history_for_payload else None
            request_json_to_log = json.dumps(request_payload_for_log, ensure_ascii=False) if request_payload_for_log else None
            response_json_to_log = json.dumps(response_json_for_log, ensure_ascii=False) if response_json_for_log else None
            user_message_to_log = user_message if user_message else (final_history_for_payload[-1]['content'] if final_history_for_payload and final_history_for_payload[-1]['role']=='user' else " ")

            log_status = 'error' if api_status_code >= 400 else 'success'
            error_message_to_log = ai_response_text if log_status == 'error' and not use_mock_api else None
            
            user_msg_repo.insert_user_message(
                session_id=chat_id, user_message=user_message_to_log,
                ai_response=str(ai_response_text) if ai_response_text else " ",
                ai_model_name=model_name_for_log, prompt=prompt_to_log,
                request_json=request_json_to_log, response_json=response_json_to_log,
                status=log_status, error_message=error_message_to_log
            )
        except Exception:
            # Veritabanına loglama hatası kullanıcıya yansıtılmamalı,
            # ancak gerçek bir uygulamada bu hata izlenmelidir.
            pass

    if api_status_code >= 400 and not use_mock_api :
        return jsonify({"error": ai_response_text, "chatId": chat_id}), api_status_code

    return jsonify({"response": str(ai_response_text), "chatId": chat_id})


# 5.2. POST /mock_gemini_api/... - Sahte Gemini API Yanıtı
# -----------------------------------------------------------------------------
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
def mock_gemini_generate_content_route():
    """
    Geliştirme ve test amaçlı sahte bir Gemini API endpoint'i.
    """
    data = request.json
    if not data:
        return jsonify({"error": "İstek gövdesi boş olamaz (JSON bekleniyor)."}), 400

    try:
        user_text = "bir mesaj (payload'dan alınamadı)"
        if "contents" in data and isinstance(data["contents"], list) and \
           len(data["contents"]) > 0 and isinstance(data["contents"][-1], dict) and \
           "parts" in data["contents"][-1] and \
           isinstance(data["contents"][-1]["parts"], list) and \
           len(data["contents"][-1]["parts"]) > 0 and isinstance(data["contents"][-1]["parts"][0], dict) and \
           "text" in data["contents"][-1]["parts"][0]:
            user_text = data["contents"][-1]["parts"][0]["text"]

        mock_response_text = f"Bu, Gemini (gemini-2.0-flash modeli - SAHTE YANIT) tarafından mesajınıza verilen sahte bir yanıttır: '{user_text}'"
        
        gemini_like_response = {
            "candidates": [{"content": {"parts": [{"text": mock_response_text}], "role": "model"},
                "finishReason": "STOP", "index": 0,
                "safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }],
            "promptFeedback": {"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]}
        }
        return jsonify(gemini_like_response)

    except (KeyError, IndexError, TypeError):
        return jsonify({"error": "Geçersiz payload formatı. Beklenen: {'contents': [{'parts':[{'text': '...'}]}]}"}), 400
    except Exception:
        # Bu hata da gerçek bir uygulamada izlenmelidir.
        return jsonify({"error": "Sahte Gemini API'sinde beklenmedik bir hata oluştu."}), 500