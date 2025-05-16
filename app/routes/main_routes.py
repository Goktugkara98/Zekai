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
import requests # Harici API istekleri için
import json     # JSON işleme için
import os       # Ortam değişkenlerini okumak için
from typing import Dict, Any, Optional, List  # Type hints için

# Servis katmanı ve model importları
from app.services.ai_model_service import (
    get_ai_model_api_details,  # Model API detaylarını getirmek için
    fetch_ai_categories_from_db,  # Tüm AI kategorilerini getirmek için
    get_all_available_models  # Tüm modelleri getirmek için
)


# 2. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
main_bp = Blueprint(
    'main',  # Blueprint adı 'main_bp' yerine 'main' olarak kısaltılabilir veya projenize uygun bir ad verilebilir.
    __name__,
    template_folder='templates', # Ana şablonların bulunduğu klasör (varsayılan)
    static_folder='static'       # Ana statik dosyaların bulunduğu klasör (varsayılan)
)
# print("DEBUG: Main Blueprint oluşturuldu.")

# 3. Yardımcı Fonksiyonlar (Utility Functions)
# =============================================================================

def generate_mock_response(user_message: str) -> str:
    """
    Gerçek API kullanılamadığında sahte bir yanıt üretir.
    Args:
        user_message (str): Kullanıcının yanıt verilecek mesajı.
    Returns:
        str: Sahte bir yanıt dizesi.
    """
    # print(f"DEBUG: Sahte yanıt üretiliyor: '{user_message}' için")
    return (f"Bu, mesajınıza sahte bir yanıttır: '{user_message}'. "
            "Gerçek AI servisi şu anda kullanılamıyor.")

def extract_response_by_path(response_json: Dict, path: str) -> Any:
    """
    İç içe bir JSON nesnesinden nokta notasyonlu bir yol kullanarak bir değer çıkarır.
    Dizi indeksleri için 'anahtar[indeks]' formatını kullanın.
    Args:
        response_json (Dict): İçinden veri çıkarılacak JSON yanıtı.
        path (str): Değere giden yol, örn: 'candidates[0].content.parts[0].text'.
    Returns:
        Any: Çıkarılan değer veya çıkarma başarısız olursa varsayılan bir mesaj/None.
    """
    # print(f"DEBUG: Yanıt ayıklanıyor: path='{path}', response_json anahtarları: {list(response_json.keys()) if isinstance(response_json, dict) else 'JSON değil'}")
    try:
        parts = path.split('.')
        current_data = response_json
        for part in parts:
            if '[' in part and part.endswith(']'):
                key, index_str_with_bracket = part.split('[', 1)
                index_str = index_str_with_bracket[:-1] # Son ']' karakterini kaldır
                if not index_str.isdigit():
                    # print(f"HATA: Geçersiz indeks formatı: '{part}' yolda: '{path}'")
                    return f"Yanıt formatı hatası: Geçersiz indeks '{index_str}'."
                index = int(index_str)

                if key: # Eğer anahtar varsa (örn: 'candidates[0]')
                    if not isinstance(current_data, dict) or key not in current_data:
                        # print(f"HATA: Anahtar '{key}' bulunamadı, path: '{path}'")
                        return f"Yanıt formatı hatası: Anahtar '{key}' bulunamadı."
                    current_data = current_data[key]

                if not isinstance(current_data, list) or index >= len(current_data):
                    # print(f"HATA: İndeks {index} liste sınırları dışında, path: '{path}', liste boyutu: {len(current_data) if isinstance(current_data, list) else 'Liste değil'}")
                    return f"Yanıt formatı hatası: İndeks {index} geçersiz."
                current_data = current_data[index]
            else: # Normal anahtar (örn: 'content')
                if not isinstance(current_data, dict) or part not in current_data:
                    # print(f"HATA: Anahtar '{part}' bulunamadı, path: '{path}'")
                    return f"Yanıt formatı hatası: Anahtar '{part}' bulunamadı."
                current_data = current_data[part]
        # print(f"DEBUG: Başarıyla ayıklanan değer: {current_data}")
        return current_data
    except (KeyError, IndexError, TypeError) as e:
        # print(f"HATA: Yanıt '{path}' yolu kullanılarak ayıklanırken hata: {e}")
        return f"AI yanıtı işlenirken hata (format uyumsuzluğu): {str(e)}"
    except Exception as e:
        # print(f"HATA: Yanıt ayıklanırken beklenmedik hata: {e}")
        return "AI yanıtı işlenirken beklenmedik bir hata oluştu."


# 4. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================

# 4.1. / (GET) - Ana Sayfa
# -----------------------------------------------------------------------------
@main_bp.route('/')
def index_page(): # Fonksiyon adı index -> index_page
    """Ana sayfayı (index.html) AI kategorileriyle birlikte gösterir."""
    # print("DEBUG: Ana sayfa (/) isteği alındı.")
    try:
        # ai_categories = get_all_active_categories_with_models() # Önerilen servis fonksiyonu
        ai_categories = fetch_ai_categories_from_db() # Orijinaldeki gibi bırakıldı
        if not ai_categories:
            # print("UYARI: Veritabanından AI kategorileri alınamadı. Örnek veri kullanılacak veya hata mesajı gösterilecek.")
            flash("AI kategorileri yüklenirken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.", "warning")
            ai_categories = [{"name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
    except Exception as e:
        # print(f"HATA: Ana sayfa için kategoriler alınırken: {e}")
        flash("Sayfa yüklenirken beklenmedik bir hata oluştu.", "danger")
        ai_categories = [{"name": "Sunucu Hatası", "icon": "bi-server", "models": []}]

    return render_template('index.html', ai_categories=ai_categories, title="Ana Sayfa")

# 5. API Rotaları (API Routes - JSON)
# =============================================================================

# 5.1. POST /api/chat/send - Sohbet Mesajlarını İşler
# -----------------------------------------------------------------------------
@main_bp.route('/api/chat/send', methods=['POST'])
def handle_chat_message_api(): # Fonksiyon adı handle_chat_message -> handle_chat_message_api
    """
    Kullanıcıdan gelen sohbet mesajını alır, ilgili AI modeline gönderir,
    yanıtı alır ve kullanıcıya JSON formatında döndürür. Etkileşimi veritabanına kaydeder.
    """
    # print("DEBUG: /api/chat/send isteği alındı.")
    data = request.json
    if not data:
        return jsonify({"error": "İstek gövdesi boş olamaz (JSON bekleniyor)."}), 400

    user_message = data.get('message')
    ai_model_id_str = data.get('aiModelId') # Frontend'den string olarak gelebilir
    chat_id = data.get('chatId') # Oturum/konuşma takibi için
    conversation_history = data.get('history', [])

    # print(f"DEBUG: Gelen veri: user_message='{user_message}', aiModelId='{ai_model_id_str}', chatId='{chat_id}', history_len={len(conversation_history)}")

    if not user_message and not conversation_history: # En azından bir mesaj veya geçmiş olmalı
        return jsonify({"error": "Kullanıcı mesajı veya konuşma geçmişi eksik."}), 400
    if not ai_model_id_str:
        return jsonify({"error": "AI Model ID'si eksik."}), 400
    if not chat_id:
        return jsonify({"error": "Sohbet ID'si eksik."}), 400

    # --- Konuşma Geçmişi Normalleştirme Başlangıcı ---
    normalized_history = []
    if isinstance(conversation_history, list):
        for msg in conversation_history:
            if isinstance(msg, dict):
                role = msg.get('role')
                content = None
                if 'content' in msg: # Doğrudan content anahtarı
                    content = msg['content']
                elif 'parts' in msg and isinstance(msg.get('parts'), list) and \
                     len(msg['parts']) > 0 and isinstance(msg['parts'][0], dict) and \
                     'text' in msg['parts'][0]: # Gemini formatı
                    content = msg['parts'][0]['text']
                # Diğer olası formatlar buraya eklenebilir

                if role and content is not None: # Hem rol hem de içerik geçerli olmalı
                    normalized_history.append({'role': str(role), 'content': str(content)})
                else:
                    pass # print(f"UYARI: Geçersiz formatta geçmiş mesajı atlanıyor: {msg}")
    # --- Konuşma Geçmişi Normalleştirme Sonu ---
    # print(f"DEBUG: Normalleştirilmiş geçmiş: {normalized_history}")


    # Ortam değişkeninden mock API kullanımını kontrol et
    use_mock_api = os.environ.get('USE_MOCK_API', 'false').lower() == 'true'
    ai_response_text = ""
    model_name_for_log = "Bilinmeyen Model"
    request_payload_for_log = {}
    response_json_for_log = {}
    api_status_code = 200 # Başarılı API çağrısı için varsayılan

    try:
        # model_details = get_ai_model_api_details_by_id(ai_model_id_str) # Önerilen servis
        model_details = get_ai_model_api_details(ai_model_id_str) # Orijinaldeki gibi
        if not model_details or not model_details.get('api_url'):
            # print(f"HATA: Model ID için API detayları alınamadı: {ai_model_id_str}")
            return jsonify({"error": f"AI modeli için yapılandırma bulunamadı: {ai_model_id_str}"}), 500
        
        model_name_for_log = model_details.get('name', 'Yapılandırma Hatası Modeli')
        api_url = model_details.get('api_url')
        request_method = model_details.get('request_method', 'POST').upper()
        response_path = model_details.get('response_path', 'candidates[0].content.parts[0].text') # Varsayılan Gemini yolu

        try:
            headers = json.loads(model_details.get('request_headers', '{}'))
            if not isinstance(headers, dict): headers = {}
        except json.JSONDecodeError:
            headers = {"Content-Type": "application/json"} # Varsayılan
        if not headers.get("Content-Type"): # Eğer Content-Type yoksa ekle
             headers["Content-Type"] = "application/json"


        # --- İstek Gövdesi (Payload) Oluşturma Mantığı ---
        request_body_template_str = model_details.get('request_body_template', '{"contents": [{"parts":[{"text": "$message"}]}]}')
        # print(f"DEBUG: Kullanılan istek şablonu: {request_body_template_str}")
        
        # Son kullanıcı mesajını geçmişe ekle (eğer zaten ekli değilse)
        current_turn_user_message_obj = {'role': 'user', 'content': user_message}
        if user_message and (not normalized_history or normalized_history[-1] != current_turn_user_message_obj) :
            final_history_for_payload = normalized_history + [current_turn_user_message_obj]
        else:
            final_history_for_payload = normalized_history # Kullanıcı mesajı zaten geçmişin sonundaysa tekrar ekleme
            if user_message:
                 pass # print("UYARI: Mevcut kullanıcı mesajı zaten konuşma geçmişinin sonunda. Tekrar eklenmiyor.")


        try:
            payload_template = json.loads(request_body_template_str)
            # $messages (liste olarak) veya $message (string olarak) değiştirme
            if "$messages" in request_body_template_str: # "$messages" (tırnak içinde) ise string replace
                messages_json_string = json.dumps(final_history_for_payload)
                # print(f"DEBUG: $messages için JSON dizesi: {messages_json_string}")
                temp_payload_str = request_body_template_str.replace('"$messages"', messages_json_string)
                request_payload_for_log = json.loads(temp_payload_str)
            elif isinstance(payload_template, dict) and \
                 any(isinstance(v, str) and v == '$messages' for v in payload_template.values()): # Değer olarak $messages ise
                for key, value in payload_template.items():
                    if isinstance(value, str) and value == '$messages':
                        payload_template[key] = final_history_for_payload
                        break
                request_payload_for_log = payload_template
            elif "$message" in request_body_template_str: # Sadece son mesajı kullan
                 # Eğer user_message boşsa ve geçmiş varsa, geçmişteki son kullanıcı mesajını al
                message_to_send = user_message
                if not message_to_send and final_history_for_payload:
                    # Geçmişteki son 'user' rolündeki mesajı bul
                    for i in range(len(final_history_for_payload) - 1, -1, -1):
                        if final_history_for_payload[i].get('role') == 'user':
                            message_to_send = final_history_for_payload[i].get('content')
                            break
                if not message_to_send: # Hala mesaj yoksa hata ver
                    return jsonify({"error": "Gönderilecek mesaj bulunamadı (ne yeni mesaj ne de geçmişte kullanıcı mesajı)."}), 400

                temp_payload_str = request_body_template_str.replace('$message', json.dumps(message_to_send)) # Mesajı JSON string olarak ekle
                request_payload_for_log = json.loads(temp_payload_str)
            else: # Bilinmeyen şablon, varsayılan Gemini yapısını kullanmaya çalış
                # print("UYARI: Şablonda bilinen bir yer tutucu ($message veya $messages) bulunamadı. Varsayılan yapı kullanılıyor.")
                request_payload_for_log = {"contents": final_history_for_payload} # Gemini formatına uygun

        except json.JSONDecodeError as template_err:
            # print(f"HATA: İstek gövdesi şablonu JSON formatında değil: {template_err}")
            return jsonify({"error": "AI modeli için geçersiz istek şablonu yapılandırması."}), 500
        # --- İstek Gövdesi Oluşturma Sonu ---
        # print(f"DEBUG: Oluşturulan istek gövdesi: {request_payload_for_log}")

        if use_mock_api:
            # print("DEBUG: Mock API kullanılıyor...")
            ai_response_text = generate_mock_response(user_message if user_message else "geçmişten bir mesaj")
            response_json_for_log = {"mock_response": ai_response_text} # Mock yanıt için log
        else:
            # print(f"DEBUG: Gerçek API'ye istek gönderiliyor: URL={api_url}, Metot={request_method}")
            api_response = None
            if request_method == 'POST':
                api_response = requests.post(api_url, json=request_payload_for_log, headers=headers, timeout=30)
            elif request_method == 'GET': # GET için payload params olarak gönderilmeli
                api_response = requests.get(api_url, params=request_payload_for_log, headers=headers, timeout=30)
            else:
                return jsonify({"error": f"Desteklenmeyen istek metodu: {request_method}"}), 400

            api_status_code = api_response.status_code
            api_response.raise_for_status() # HTTP hataları için exception fırlatır (4xx, 5xx)
            response_json_for_log = api_response.json()
            # print(f"DEBUG: API'den gelen yanıt (JSON): {response_json_for_log}")
            ai_response_text = extract_response_by_path(response_json_for_log, response_path)
            if not isinstance(ai_response_text, str): # Eğer extract_response_by_path hata mesajı döndürdüyse
                 # print(f"UYARI: Yanıt ayıklama başarısız oldu, ham yanıt kullanılacak veya hata mesajı: {ai_response_text}")
                 # Bu durumda ai_response_text zaten bir hata mesajı içeriyor olabilir.
                 # Eğer API'den başarılı bir yanıt alındı ama path yanlışsa, bu durumu loglamak önemli.
                 if api_status_code < 300 : # Başarılı API çağrısı ama path hatası
                      pass # ai_response_text zaten hata mesajını içeriyor.
                 else: # API hatası ve path hatası (bu durum pek olası değil, raise_for_status öncesinde yakalanırdı)
                      ai_response_text = f"API Hatası ({api_status_code}) ve Yanıt Ayrıştırma Hatası: {ai_response_text}"


    except requests.exceptions.HTTPError as http_err:
        # print(f"HATA: API HTTP Hatası: {http_err}, Durum Kodu: {api_status_code}")
        # print(f"HATA: İstek Detayları: URL='{api_url}', Metot='{request_method}', Payload='{request_payload_for_log}'")
        # print(f"HATA: Yanıt Başlıkları: {http_err.response.headers if http_err.response else 'Yok'}")
        # print(f"HATA: Yanıt İçeriği: {http_err.response.text if http_err.response else 'Yok'}")
        ai_response_text = f"AI servisinden hata alındı (Kod: {api_status_code}). Detay: {http_err.response.text if http_err.response and http_err.response.text else str(http_err)}"
        response_json_for_log = {"error": ai_response_text, "status_code": api_status_code}
        # Mock API fallback denemesi (opsiyonel)
        # ai_response_text = generate_mock_response(user_message if user_message else "geçmişten bir mesaj")
        # response_json_for_log = {"mock_error_fallback": ai_response_text}
    except requests.exceptions.RequestException as req_err: # Bağlantı hatası, timeout vb.
        # print(f"HATA: API İstek Hatası: {req_err}")
        api_status_code = 503 # Service Unavailable gibi
        ai_response_text = f"AI servisine ulaşılamadı: {str(req_err)}"
        response_json_for_log = {"error": ai_response_text, "status_code": api_status_code}
    except Exception as e:
        # print(f"HATA: Sohbet işleyicide beklenmedik genel hata: {e}")
        api_status_code = 500 # Internal Server Error
        ai_response_text = f"Beklenmedik bir sunucu hatası oluştu: {str(e)}"
        response_json_for_log = {"error": ai_response_text, "status_code": api_status_code}

    # --- Veritabanına Loglama ---
    try:
        # UserMessageRepository doğrudan kullanılıyor. Servis katmanı üzerinden yapılması daha iyi olabilir.
        user_msg_repo = UserMessageRepository()
        user_msg_repo.insert_user_message(
            session_id=chat_id,
            user_message=user_message if user_message else " ", # Boş string yerine bir boşluk
            ai_response=ai_response_text if ai_response_text else " ",
            ai_model_name=model_name_for_log,
            prompt=json.dumps(final_history_for_payload) if final_history_for_payload else None, # Tam prompt/geçmiş
            request_json=json.dumps(request_payload_for_log) if request_payload_for_log else None,
            response_json=json.dumps(response_json_for_log) if response_json_for_log else None,
            status='error' if api_status_code >= 400 else 'success',
            error_message=ai_response_text if api_status_code >=400 and not use_mock_api else None
            # tokens ve duration gibi alanlar API yanıtından alınabilirse eklenebilir.
        )
        # print(f"DEBUG: Mesaj '{chat_id}' ID'li sohbete loglandı. Durum: {'error' if api_status_code >= 400 else 'success'}")
    except Exception as db_err:
        # print(f"HATA: Veritabanına loglama sırasında hata (Sohbet ID: {chat_id}): {db_err}")
        # Bu hata kullanıcıya yansıtılmamalı, sadece sunucu tarafında loglanmalı.
        pass
    # --- Veritabanına Loglama Sonu ---

    if api_status_code >= 400 and not use_mock_api : # Eğer API hatası varsa ve mock kullanılmıyorsa
        return jsonify({"error": ai_response_text, "chatId": chat_id}), api_status_code

    return jsonify({"response": ai_response_text, "chatId": chat_id})


# 5.2. POST /mock_gemini_api/... - Sahte Gemini API Yanıtı
# -----------------------------------------------------------------------------
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
def mock_gemini_generate_content_route(): # Fonksiyon adı mock_gemini_generate_content -> ..._route
    """
    Geliştirme ve test amaçlı sahte bir Gemini API endpoint'i.
    Gelen isteğe göre standart bir Gemini API yanıt formatında sahte içerik üretir.
    """
    # print("DEBUG: Sahte Gemini API (/mock_gemini_api/...) isteği alındı.")
    data = request.json
    if not data:
        return jsonify({"error": "İstek gövdesi boş olamaz (JSON bekleniyor)."}), 400

    try:
        # Gelen payload'dan metni ayıkla (basit bir varsayım)
        user_text = "bir mesaj" # Varsayılan
        if "contents" in data and isinstance(data["contents"], list) and \
           len(data["contents"]) > 0 and "parts" in data["contents"][0] and \
           isinstance(data["contents"][0]["parts"], list) and \
           len(data["contents"][0]["parts"]) > 0 and "text" in data["contents"][0]["parts"][0]:
            user_text = data["contents"][0]["parts"][0]["text"]

        mock_response_text = f"Bu, Gemini (gemini-2.0-flash modeli - SAHTE YANIT) tarafından mesajınıza verilen sahte bir yanıttır: '{user_text}'"

        gemini_like_response = {
            "candidates": [{
                "content": {"parts": [{"text": mock_response_text}], "role": "model"},
                "finishReason": "STOP", "index": 0,
                "safetyRatings": [
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
                ]
            }],
            "promptFeedback": {"safetyRatings": [
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
            ]}
        }
        # print(f"DEBUG: Sahte Gemini API yanıtı: {gemini_like_response}")
        return jsonify(gemini_like_response)

    except (KeyError, IndexError, TypeError) as e:
        # print(f"HATA: Sahte Gemini API - Geçersiz payload formatı: {e}")
        return jsonify({"error": "Geçersiz payload formatı. Beklenen: {'contents': [{'parts':[{'text': '...'}]}]}"}), 400
    except Exception as e:
        # print(f"HATA: Sahte Gemini API - Beklenmedik hata: {e}")
        return jsonify({"error": "Sahte Gemini API'sinde beklenmedik bir hata oluştu."}), 500

# Blueprint'i Flask uygulamasına kaydetmek için bu dosyanın __init__.py'da
# veya ana uygulama dosyasında import edilmesi ve register_blueprint() ile kaydedilmesi gerekir.
# Örnek: from .main_routes import main_bp; app.register_blueprint(main_bp)

