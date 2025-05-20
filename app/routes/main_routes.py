# =============================================================================
# Ana Rotalar Modülü (Main Routes Module)
# =============================================================================
# Bu modül, uygulamanın ana kullanıcı arayüzü ve temel API rotalarını tanımlar.
# Ana sayfa gösterimi ve sohbet API'si gibi işlevleri içerir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Logger Yapılandırması (Logger Configuration)
# 3. Yardımcı Fonksiyon Loglama Aracı (Helper Function Logger)
# 4. Rota Çağrı Logger Dekoratörü (Route Call Logger Decorator)
# 5. Blueprint Tanımı (Blueprint Definition)
# 6. Yardımcı Fonksiyonlar (Utility Functions)
#    6.1. generate_mock_response         : Sahte (mock) AI yanıtı üretir.
#    6.2. extract_response_by_path       : JSON yanıtından belirli bir yola göre veri çıkarır.
# 7. Arayüz Rotaları (View Routes - HTML Rendering)
#    7.1. / (GET)                        : Ana sayfa (index.html).
# 8. API Rotaları (API Routes - JSON)
#    8.1. POST /api/chat/send            : Sohbet mesajlarını işler ve AI yanıtı döndürür.
#    8.2. POST /mock_gemini_api/...      : (Geliştirme/Test) Sahte Gemini API yanıtı üretir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from flask import Blueprint, render_template, request, jsonify, flash
import requests  # Harici API istekleri için
import json      # JSON işleme için
import os        # Ortam değişkenlerini okumak için
from typing import Dict, Any, Optional, List  # Type hints için
import logging   # Logging modülü
import inspect   # Çağrı yığınını incelemek için
import functools # Dekoratörler için

# Servis katmanı ve model importları
from app.services.ai_model_service import (
    get_ai_model_api_details,
    fetch_ai_categories_from_db,
)
try:
    from app.repositories.user_message_repository import UserMessageRepository
except ImportError:
    UserMessageRepository = None
    # logger.error("UserMessageRepository import edilemedi!\n") # Bu log, logger tanımlandıktan sonra olmalı

# 2. Logger Yapılandırması (Logger Configuration)
# =============================================================================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Bu format global kalacak
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__) # main_routes için logger

if UserMessageRepository is None: # Logger tanımlandıktan sonra import hatasını logla
    logger.error("UserMessageRepository import edilemedi! Veritabanı loglaması yapılamayacak.\n")

# 3. Yardımcı Fonksiyon Loglama Aracı (Helper Function Logger)
# =============================================================================
def log_function_call(func_name: str, params_summary: Optional[Dict[str, Any]] = None, module_name: Optional[str] = None):
    """
    Genel bir fonksiyonun çağrıldığını '----' ayırıcıları ile loglar, çağrı kaynağı
    hakkında detayları ve isteğe bağlı olarak parametre özetini içerir.
    """
    qual_name = f"{module_name}.{func_name}" if module_name else func_name
    caller_info_log_str = ""
    try:
        # inspect.stack()[0] -> log_function_call
        # inspect.stack()[1] -> çağıran fonksiyon (örn: generate_mock_response)
        # inspect.stack()[2] -> çağıran fonksiyonu çağıran yer
        caller_frame = inspect.stack()[2]
        caller_function_name = caller_frame.function
        # Sadece dosya adını almak için düzenleme
        caller_filename = os.path.basename(caller_frame.filename)
        caller_lineno = caller_frame.lineno
        caller_info_log_str = f"  └── Called from: {caller_filename} -> {caller_function_name}() -> line {caller_lineno}"
    except IndexError:
        caller_info_log_str = "  └── Caller info: Not available (possibly top-level or direct script call)."
    except Exception as e:
        caller_info_log_str = f"  └── Caller info: Error retrieving - {e}."

    params_log_str = ""
    if params_summary:
        try:
            # Parametrelerin logda çok uzun olmasını engellemek için basit formatlama
            formatted_params = {
                k: (str(v)[:75] + '...' if isinstance(v, str) and len(v) > 75 else v)
                for k, v in params_summary.items()
            }
            params_log_str = f"\n  └── Params: {formatted_params}"
        except Exception as e:
            params_log_str = f"\n  └── Params: Error formatting - {e}"

    logger.debug(
        f"---- Function Invoked: {qual_name}() ----{params_log_str}\n{caller_info_log_str}\n"
    )

# 4. Rota Çağrı Logger Dekoratörü (Route Call Logger Decorator)
# =============================================================================
def log_route_call_enhanced(func):
    """
    Flask rota fonksiyonlarının çağrılarını, istek detaylarını ve
    fonksiyonun başlangıç/bitişini loglayan bir dekoratör.
    '====' ana ayraç, '----' iç adımlar için kullanılır.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        route_name = func.__name__
        # request.path kullanarak tam yolu alalım, request.url yerine
        request_info = f"{request.method} {request.path}"
        log_message_prefix = f"ROUTE: {route_name} ({request_info})"

        logger.info(f"==== START {log_message_prefix} ====\n")
        logger.debug(f"  Request Endpoint: {request.endpoint}\n")
        logger.debug(f"  Full Request URL: {request.url}\n")

        # İstek başlıkları (çok uzun olabileceğinden özet veya önemli olanlar)
        relevant_headers = {
            k: v for k, v in request.headers.items()
            if k.lower() in ['content-type', 'user-agent', 'accept', 'authorization', 'x-forwarded-for']
        }
        logger.debug(f"  Request Headers (Relevant): {relevant_headers}\n")

        if request.method in ['POST', 'PUT', 'PATCH']:
            payload_info = "  Request Payload: "
            if request.is_json:
                try:
                    # silent=True ile parse hatasında None döner, get_json(force=True) data boşsa hata verir.
                    json_payload = request.get_json(silent=True)
                    if json_payload is not None:
                        payload_info += f"JSON = {json.dumps(json_payload, indent=2, ensure_ascii=False)[:500]}" # İlk 500 karakter
                        if len(json.dumps(json_payload)) > 500 : payload_info += "..."
                    else: # JSON bekleniyordu ama parse edilemedi veya boş
                        payload_info += f"Expected JSON but got empty or unparseable. Raw data (first 200 bytes): {request.data[:200]}"
                except Exception as e_json:
                    payload_info += f"Could not parse JSON (silent=True failed or other issue): {e_json}. Raw data (first 200 bytes): {request.data[:200]}"
            elif request.form:
                payload_info += f"Form Data = {request.form.to_dict()}"
            else:
                payload_info += f"Raw Data (first 200 bytes) = {request.data[:200]}"
            logger.debug(payload_info + "\n")

        # Çağıranın Python bağlamı (Flask iç mekanizmaları olabilir)
        try:
            caller_frame = inspect.stack()[1] # wrapper'ı çağıran frame (Flask internal)
            caller_function_name = caller_frame.function
            caller_filename = os.path.basename(caller_frame.filename)
            caller_lineno = caller_frame.lineno
            logger.debug(f"  Python Call Context: {caller_filename} -> {caller_function_name}() @ line {caller_lineno}\n")
        except IndexError:
            logger.debug("  Python Call Context: Info not available.\n")
        except Exception as e_inspect:
            logger.warning(f"  Python Call Context: Error retrieving - {e_inspect}\n")

        logger.debug(f"---- Executing {route_name} Logic ----\n")

        try:
            result = func(*args, **kwargs) # Asıl rota fonksiyonunu çalıştır
            
            status_code_for_log = ""
            response_summary = ""

            if isinstance(result, tuple) and len(result) > 0: # Flask response (data, status, headers)
                if hasattr(result[0], 'get_data'): # Flask Response nesnesi (genellikle jsonify veya render_template sonucu)
                    response_data_sample = result[0].get_data(as_text=True)[:200]
                    if len(result[0].get_data(as_text=True)) > 200: response_data_sample += "..."
                    response_summary = f" -> Response Sample (first 200 chars): {response_data_sample}"
                else: # Basit bir tuple (örn: string, int)
                    response_summary = f" -> Response Data (type): {type(result[0]).__name__}"

                if len(result) > 1 and isinstance(result[1], int):
                    status_code_for_log = f" -> Status: {result[1]}"
                elif hasattr(result[0], 'status_code'): # Eğer ilk eleman Response nesnesi ise
                    status_code_for_log = f" -> Status: {result[0].status_code}"

            elif hasattr(result, 'get_data'): # Doğrudan Flask Response nesnesi döndürülmüşse
                 response_data_sample = result.get_data(as_text=True)[:200]
                 if len(result.get_data(as_text=True)) > 200: response_data_sample += "..."
                 response_summary = f" -> Response Sample (first 200 chars): {response_data_sample}"
                 status_code_for_log = f" -> Status: {result.status_code}"
            elif isinstance(result, str): # Basit string yanıtı
                 response_summary = f" -> Response (string, first 200 chars): {result[:200]}"
                 if len(result) > 200: response_summary += "..."
            
            logger.info(f"---- {route_name} Execution Succeeded{status_code_for_log} ----\n{response_summary}\n")
            return result
        except Exception as e:
            logger.error(f"!!!! ERROR IN {log_message_prefix} !!!!\n  Type: {type(e).__name__}\n  Error: {e}\n", exc_info=True)
            raise
        finally:
            logger.info(f"==== END {log_message_prefix} ====\n") # Sonrasında da bir boşluk için
    return wrapper

# 5. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 6. Yardımcı Fonksiyonlar (Utility Functions)
# =============================================================================

def generate_mock_response(user_message: str) -> str:
    """Gerçek API kullanılamadığında sahte bir yanıt üretir."""
    log_function_call("generate_mock_response", {"user_message": user_message}, __name__)
    response = (f"Bu, mesajınıza sahte bir yanıttır: '{user_message}'. "
                "Gerçek AI servisi şu anda kullanılamıyor.")
    logger.debug(f"  -> Sahte yanıt üretildi: '{response[:50]}...'\n")
    return response

def extract_response_by_path(response_json: Dict, path: str) -> Any:
    """İç içe bir JSON nesnesinden nokta notasyonlu bir yol kullanarak bir değer çıkarır."""
    log_function_call("extract_response_by_path", {"path": path, "json_keys": list(response_json.keys()) if isinstance(response_json, dict) else 'JSON değil veya boş'}, __name__)

    try:
        parts = path.split('.')
        current_data = response_json
        for i, part in enumerate(parts):
            logger.debug(f"  -> Adım {i+1}/{len(parts)}: İşlenen parça='{part}', Mevcut veri tipi='{type(current_data).__name__}'\n")
            if '[' in part and part.endswith(']'):
                key, index_str_with_bracket = part.split('[', 1)
                index_str = index_str_with_bracket[:-1]
                if not index_str.isdigit():
                    logger.warning(f"Geçersiz indeks formatı: '{part}' (yol: '{path}'). Ayıklama durduruluyor.\n")
                    return f"Yanıt formatı hatası: Geçersiz indeks '{index_str}'."
                index = int(index_str)

                if key: # Eğer anahtar varsa, önce anahtarla eriş
                    if not isinstance(current_data, dict) or key not in current_data:
                        logger.warning(f"Anahtar '{key}' bulunamadı (yol: '{path}'). Ayıklama durduruluyor.\n")
                        return f"Yanıt formatı hatası: Anahtar '{key}' bulunamadı."
                    current_data = current_data[key]
                    logger.debug(f"      -> Anahtar '{key}' ile erişildi. Yeni veri tipi='{type(current_data).__name__}'\n")

                if not isinstance(current_data, list) or index >= len(current_data):
                    logger.warning(f"İndeks {index} liste sınırları dışında (yol: '{path}', liste boyutu: {len(current_data) if isinstance(current_data, list) else 'Liste değil'}). Ayıklama durduruluyor.\n")
                    return f"Yanıt formatı hatası: İndeks {index} geçersiz."
                current_data = current_data[index]
                logger.debug(f"      -> İndeks '{index}' ile erişildi. Yeni veri tipi='{type(current_data).__name__}'\n")
            else: # Sadece anahtar
                if not isinstance(current_data, dict) or part not in current_data:
                    logger.warning(f"Anahtar '{part}' bulunamadı (yol: '{path}'). Ayıklama durduruluyor.\n")
                    return f"Yanıt formatı hatası: Anahtar '{part}' bulunamadı."
                current_data = current_data[part]
                logger.debug(f"      -> Anahtar '{part}' ile erişildi. Yeni veri tipi='{type(current_data).__name__}'\n")
        
        logger.info(f"Başarıyla ayıklanan değer (yol: '{path}'). Değer (ilk 100 karakter): '{str(current_data)[:100]}'\n")
        return current_data
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Yanıt '{path}' yolu kullanılarak ayıklanırken hata: {type(e).__name__} - {e}\n", exc_info=True)
        return f"AI yanıtı işlenirken hata (format uyumsuzluğu): {str(e)}"
    except Exception as e:
        logger.critical(f"Yanıt ayıklanırken beklenmedik kritik hata (yol: '{path}'): {e}\n", exc_info=True)
        return "AI yanıtı işlenirken beklenmedik bir hata oluştu."

# 7. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================

# 7.1. / (GET) - Ana Sayfa
# -----------------------------------------------------------------------------
@main_bp.route('/')
@log_route_call_enhanced
def index_page():
    """Ana sayfayı (index.html) AI kategorileriyle birlikte gösterir."""
    logger.info("Ana sayfa (index.html) için içerik hazırlanıyor.\n")
    try:
        ai_categories = fetch_ai_categories_from_db()
        if not ai_categories:
            logger.warning("Veritabanından AI kategorileri alınamadı veya boş. Flash mesajı gösterilecek.\n")
            flash("AI kategorileri yüklenirken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.", "warning")
            ai_categories = [{"name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
        else:
            logger.info(f"{len(ai_categories)} adet AI kategorisi başarıyla yüklendi.\n")

    except Exception as e:
        logger.error(f"Ana sayfa için kategoriler alınırken genel bir hata oluştu: {e}\n", exc_info=True)
        flash("Sayfa yüklenirken beklenmedik bir hata oluştu.", "danger")
        ai_categories = [{"name": "Sunucu Hatası", "icon": "bi-server", "models": []}]
    
    logger.debug("  -> 'index.html' şablonu render ediliyor...\n")
    return render_template('index.html', ai_categories=ai_categories, title="Ana Sayfa")

# 8. API Rotaları (API Routes - JSON)
# =============================================================================

# 8.1. POST /api/chat/send - Sohbet Mesajlarını İşler
# -----------------------------------------------------------------------------
@main_bp.route('/api/chat/send', methods=['POST'])
@log_route_call_enhanced
def handle_chat_message_api():
    """
    Kullanıcıdan gelen sohbet mesajını alır, ilgili AI modeline gönderir,
    yanıtı alır ve kullanıcıya JSON formatında döndürür. Etkileşimi veritabanına kaydeder.
    """
    logger.info("Sohbet mesajı işleme ana mantığı başlatıldı.\n") # Dekoratör zaten ana girişi logluyor.
    data = request.json
    print(data)
    if not data:
        # Bu durum normalde dekoratörde yakalanır veya Flask tarafından 400 Bad Request ile engellenir
        # eğer `request.json` None ise. Yine de ek kontrol.
        logger.warning("İstek gövdesi JSON değil veya boş (beklenmedik durum).\n")
        return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

    user_message = data.get('message')
    ai_model_id_str = data.get('aiModelId')
    chat_id = data.get('chatId')
    conversation_history = data.get('history', [])

    logger.debug(f"  Gelen Veri: user_message='{user_message}', aiModelId='{ai_model_id_str}', chatId='{chat_id}', history_len={len(conversation_history)}\n")

    if not user_message and not conversation_history: # En azından biri olmalı
        logger.warning("Kullanıcı mesajı ve konuşma geçmişi eksik.\n")
        return jsonify({"error": "Kullanıcı mesajı veya konuşma geçmişi eksik."}), 400
    if not ai_model_id_str:
        logger.warning("AI Model ID'si eksik.\n")
        return jsonify({"error": "AI Model ID'si eksik."}), 400
    if not chat_id:
        logger.warning("Sohbet ID'si eksik.\n")
        return jsonify({"error": "Sohbet ID'si eksik."}), 400

    # --- Konuşma Geçmişi Normalleştirme ---
    logger.debug("---- Step: Normalizing Conversation History ----\n")
    normalized_history = []
    if isinstance(conversation_history, list):
        for msg_idx, msg in enumerate(conversation_history):
            if isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content')
                if content is None and 'parts' in msg and isinstance(msg.get('parts'), list) and \
                     len(msg['parts']) > 0 and isinstance(msg['parts'][0], dict) and \
                     'text' in msg['parts'][0]:
                    content = msg['parts'][0]['text']
                
                if role and content is not None: # Hem rol hem içerik varsa ekle
                    normalized_history.append({'role': str(role), 'content': str(content)})
                else:
                    logger.debug(f"  Geçmişteki {msg_idx}. mesaj (role='{role}', content_found={content is not None}) normalleştirme için yetersiz, atlanıyor.\n")
    logger.debug(f"  Normalleştirilmiş konuşma geçmişi ({len(normalized_history)} mesaj).\n") # Detaylı geçmiş logu çok uzun olabilir.
    # --- Konuşma Geçmişi Normalleştirme Sonu ---

    use_mock_api = os.environ.get('USE_MOCK_API', 'false').lower() == 'true'
    logger.info(f"Mock API kullanımı: {use_mock_api}\n")
    
    ai_response_text = "Yanıt alınamadı."
    model_name_for_log = "Bilinmeyen Model"
    request_payload_for_log = {}
    response_json_for_log = {}
    api_status_code = 500 # Varsayılan hata durumu

    try:
        logger.debug(f"---- Step: Fetching AI Model Details (ID: {ai_model_id_str}) ----\n")
        model_details_raw = get_ai_model_api_details(ai_model_id_str)
        
        if hasattr(model_details_raw, 'to_dict'):
            model_details = model_details_raw.to_dict()
        elif isinstance(model_details_raw, dict):
            model_details = model_details_raw
        else:
            model_details = None

        if not model_details or not model_details.get('api_url'):
            logger.error(f"Model ID '{ai_model_id_str}' için API detayları veya URL'si alınamadı/bulunamadı.\n")
            return jsonify({"error": f"AI modeli için yapılandırma bulunamadı: {ai_model_id_str}"}), 500
        
        model_name_for_log = model_details.get('name', 'Yapılandırma Hatası Modeli')
        logger.info(f"  Kullanılacak Model: '{model_name_for_log}' (ID: {ai_model_id_str})\n")

        api_url = model_details.get('api_url')
        api_key = model_details.get('api_key')
        
        # For Google's Gemini API, the API key needs to be in the URL as a query parameter
        if api_url and api_key and 'generativelanguage.googleapis.com' in api_url:
            if '?' in api_url:
                api_url = f"{api_url}&key={api_key}"
            else:
                api_url = f"{api_url}?key={api_key}"
            logger.debug(f"  API URL updated to include API key: {api_url.split('?key=')[0]}?key=***MASKED***\n")
        request_method = model_details.get('request_method', 'POST').upper()
        response_path = model_details.get('response_path')
        if not response_path:
            logger.warning(f"  Model '{model_name_for_log}' için 'response_path' tanımlanmamış. Yanıt ayıklama başarısız olabilir.\n")

        headers_str = model_details.get('request_headers') # Bu DB'den string veya dict gelebilir
        headers = {}
        if headers_str:
            try:
                if isinstance(headers_str, str): headers = json.loads(headers_str)
                elif isinstance(headers_str, dict): headers = headers_str
                if not isinstance(headers, dict):
                    logger.warning(f"  Model başlıkları dict'e çözümlenemedi. Varsayılan kullanılacak. Başlıklar: '{headers_str}'\n")
                    headers = {}
            except json.JSONDecodeError:
                logger.warning(f"  Model başlıkları JSON formatında değil: '{headers_str}'. Varsayılan kullanılacak.\n")
                headers = {}
        
        if not headers.get("Content-Type") and request_method == 'POST':
             headers["Content-Type"] = "application/json"
        logger.debug(f"  Kullanılacak API başlıkları: {headers}\n")

        # --- İstek Gövdesi (Payload) Oluşturma ---
        logger.debug("---- Step: Constructing API Request Payload ----\n")
        request_body_template_raw = model_details.get('request_body_template')
        request_body_template_str = None
        if isinstance(request_body_template_raw, dict):
            request_body_template_str = json.dumps(request_body_template_raw)
        elif isinstance(request_body_template_raw, str):
            request_body_template_str = request_body_template_raw
        
        if not request_body_template_str:
            logger.error(f"  Model '{model_name_for_log}' için istek gövdesi şablonu boş.\n")
            return jsonify({"error": f"Model '{model_name_for_log}' için istek şablonu eksik."}), 500

        logger.debug(f"  Kullanılan istek şablonu (string): {request_body_template_str}\n")
        
        final_history_for_payload = list(normalized_history)
        if user_message:
            current_turn_user_message_obj = {'role': 'user', 'content': user_message}
            # Sadece farklıysa veya geçmiş boşsa ekle
            if not final_history_for_payload or final_history_for_payload[-1] != current_turn_user_message_obj:
                final_history_for_payload.append(current_turn_user_message_obj)
            else:
                logger.debug("  Yeni kullanıcı mesajı zaten konuşma geçmişinin sonunda, tekrar eklenmiyor.\n")
        
        logger.debug(f"  API'ye gönderilecek son mesaj listesi ({len(final_history_for_payload)} mesaj).\n")

        try:
            payload_template_dict = json.loads(request_body_template_str)
            
            def fill_template(template_part, history, last_message_text):
                """Recursively fills the template with actual values.
                Handles special placeholders like $messages, $message, and {user_prompt}."""
                if isinstance(template_part, dict):
                    return {k: fill_template(v, history, last_message_text) for k, v in template_part.items()}
                elif isinstance(template_part, list):
                    # Eğer liste "$messages" içeriyorsa, bu listeyi history ile değiştir.
                    # Bu, [{"role":"user", "content":"$message"}] gibi şablonlara izin vermez,
                    # bunun yerine "$messages" tüm listeyi temsil etmeli.
                    # Örnek: {"messages": "$messages"} -> {"messages": [{"role":"user", ...}]}
                    if len(template_part) == 1 and template_part[0] == "$messages":
                        return history # Tüm geçmişi doğrudan liste olarak ata
                    return [fill_template(item, history, last_message_text) for item in template_part]
                elif isinstance(template_part, str):
                    if template_part == "$messages": # Bu genellikle bir anahtarın değeri olmalı, tek başına değil.
                        # Eğer string değeri "$messages" ise, bunu tüm history ile değiştir.
                        # Bu, template'in {"key_for_history": "$messages"} gibi olmasını bekler.
                        return history
                    elif template_part == "$message":
                        return last_message_text if last_message_text else ""
                    elif isinstance(template_part, str) and "{user_prompt}" in template_part:
                        # Handle Gemini API specific placeholder
                        return template_part.replace("{user_prompt}", last_message_text if last_message_text else "")
                    return template_part
                return template_part

            message_to_send_in_template = user_message
            if not message_to_send_in_template and final_history_for_payload:
                for i in range(len(final_history_for_payload) - 1, -1, -1):
                    if final_history_for_payload[i].get('role') == 'user':
                        message_to_send_in_template = final_history_for_payload[i].get('content')
                        break
            
            if not message_to_send_in_template and not final_history_for_payload:
                 logger.warning("  Payload için ne yeni mesaj ne de geçmişte kullanıcı mesajı bulunamadı.\n")

            request_payload_for_log = fill_template(payload_template_dict, final_history_for_payload, message_to_send_in_template)

        except json.JSONDecodeError as template_err:
            logger.error(f"  İstek gövdesi şablonu JSON formatında değil: {template_err}. Şablon: '{request_body_template_str}'\n", exc_info=True)
            return jsonify({"error": "AI modeli için geçersiz istek şablonu yapılandırması."}), 500
        logger.info(f"  Oluşturulan API istek gövdesi (payload, ilk 200 karakter): {json.dumps(request_payload_for_log, ensure_ascii=False)[:200]}...\n")
        # --- İstek Gövdesi Oluşturma Sonu ---

        if use_mock_api:
            logger.info("---- Step: Using Mock API ----\n")
            ai_response_text = generate_mock_response(user_message if user_message else "geçmişten bir mesaj")
            response_json_for_log = {"mock_response": ai_response_text, "candidates": [{"content": {"parts": [{"text": ai_response_text}]}}]}
            api_status_code = 200
        else:
            logger.info(f"---- Step: Sending Request to Real API (URL: {api_url}, Method: {request_method}) ----\n")
            api_response = None
            try:
                if request_method == 'POST':
                    api_response = requests.post(api_url, json=request_payload_for_log, headers=headers, timeout=30)
                elif request_method == 'GET': # GET için payload params olarak gönderilmeli
                    api_response = requests.get(api_url, params=request_payload_for_log, headers=headers, timeout=30)
                else:
                    logger.error(f"  Desteklenmeyen istek metodu: {request_method}\n")
                    return jsonify({"error": f"Desteklenmeyen istek metodu: {request_method}"}), 400

                api_status_code = api_response.status_code
                logger.info(f"  API yanıt durumu: {api_status_code}\n")
                api_response.raise_for_status()
                
                try:
                    response_json_for_log = api_response.json()
                    logger.debug(f"  API'den gelen ham JSON yanıt (ilk 200 karakter): {json.dumps(response_json_for_log, ensure_ascii=False)[:200]}...\n")
                except json.JSONDecodeError as json_err:
                    logger.error(f"  API yanıtı JSON formatında değil. Yanıt metni (ilk 200): {api_response.text[:200]}...\n", exc_info=True)
                    response_json_for_log = {"error": "API response was not valid JSON", "raw_response": api_response.text}
                    ai_response_text = "API'den gelen yanıt işlenemedi (JSON formatında değil)."
                    if api_status_code < 300: api_status_code = 502
                
                if response_path:
                    extracted_value = extract_response_by_path(response_json_for_log, response_path)
                    if isinstance(extracted_value, str) and "Yanıt formatı hatası:" in extracted_value:
                        logger.warning(f"  Yanıt ayıklama başarısız (path: '{response_path}'). Hata: {extracted_value}\n")
                        ai_response_text = extracted_value
                        if api_status_code < 300 : api_status_code = 502
                    elif extracted_value is not None :
                        ai_response_text = str(extracted_value)
                        logger.info(f"  Yanıt '{response_path}' yolundan başarıyla ayıklandı.\n")
                    else:
                        logger.warning(f"  Yanıt '{response_path}' yolundan ayıklandı ancak sonuç None veya tanımsız.\n")
                        ai_response_text = "AI modelinden anlamlı bir yanıt alınamadı."
                        if api_status_code < 300 : api_status_code = 204
                elif response_json_for_log and isinstance(response_json_for_log, dict) and not response_path: # path yok ama JSON var
                    logger.warning(f"  Model '{model_name_for_log}' için 'response_path' tanımlı değil. Ham JSON yanıt olduğu gibi kullanılmaya çalışılacak.\n")
                    ai_response_text = json.dumps(response_json_for_log, ensure_ascii=False)
                elif not isinstance(response_json_for_log, dict) and not response_path: # path yok, json da dict değil
                     logger.warning(f"  Model '{model_name_for_log}' için 'response_path' tanımlı değil ve yanıt dict değil. Yanıt: {str(response_json_for_log)[:200]}\n")
                     ai_response_text = str(response_json_for_log) # Yanıtın kendisini string olarak al
                else: # response_path yok ve response_json_for_log da uygun değilse
                    logger.error("  Response path tanımlı değil ve API yanıtı işlenemiyor.\n")
                    ai_response_text = "AI yanıtı işlenemedi (yapılandırma eksik)."
                    if api_status_code < 300: api_status_code = 500


            except requests.exceptions.HTTPError as http_err:
                logger.error(f"  API HTTP Hatası (Kod: {api_status_code}): {http_err}\n", exc_info=False) # exc_info=False çünkü raise_for_status zaten detayı verir
                raw_response_text = http_err.response.text if http_err.response else "Yanıt içeriği yok"
                logger.debug(f"     -> Hata Yanıt İçeriği (ilk 200 char): {raw_response_text[:200]}\n")
                ai_response_text = f"AI servisinden hata alındı (Kod: {api_status_code}). Detay: {raw_response_text[:100]}"
                response_json_for_log = {"error_message_from_api": ai_response_text, "status_code": api_status_code, "raw_error_response": raw_response_text}
            except requests.exceptions.RequestException as req_err:
                logger.error(f"  API İstek Hatası (bağlantı, timeout vb.): {req_err}\n", exc_info=True)
                api_status_code = 503
                ai_response_text = f"AI servisine ulaşılamadı: {str(req_err)}"
                response_json_for_log = {"error_message_internal": ai_response_text, "status_code": api_status_code}
            except Exception as e_inner_api:
                logger.critical(f"  API çağrısı ve yanıt işleme sırasında beklenmedik genel hata: {e_inner_api}\n", exc_info=True)
                api_status_code = 500
                ai_response_text = f"AI yanıtı işlenirken beklenmedik bir hata oluştu: {str(e_inner_api)}"
                response_json_for_log = {"error_message_internal": ai_response_text, "status_code": api_status_code}

    except Exception as e_outer:
        logger.critical(f"Sohbet işleyicide (API bloğu dışında) beklenmedik genel hata: {e_outer}\n", exc_info=True)
        api_status_code = 500
        ai_response_text = f"Beklenmedik bir sunucu hatası oluştu: {str(e_outer)}"
        response_json_for_log = {"error_message_critical": ai_response_text, "status_code": api_status_code}

    # --- Veritabanına Loglama ---
    logger.info("---- Step: Logging Interaction to Database ----\n")
    if UserMessageRepository:
        try:
            user_msg_repo = UserMessageRepository()
            prompt_to_log = json.dumps(final_history_for_payload, ensure_ascii=False) if final_history_for_payload else None
            request_json_to_log = json.dumps(request_payload_for_log, ensure_ascii=False) if request_payload_for_log else None
            response_json_to_log = json.dumps(response_json_for_log, ensure_ascii=False) if response_json_for_log else None
            user_message_to_log = user_message if user_message else (final_history_for_payload[-1]['content'] if final_history_for_payload and final_history_for_payload[-1]['role']=='user' else " ")

            log_status = 'error' if api_status_code >= 400 else 'success'
            error_message_to_log = ai_response_text if log_status == 'error' and not use_mock_api else None
            
            logger.debug(f"  Loglanacak veriler: session_id='{chat_id}', user_message='{user_message_to_log[:50]}...', ai_response='{str(ai_response_text)[:50]}...', model='{model_name_for_log}', status='{log_status}'\n")
            
            user_msg_repo.insert_user_message(
                session_id=chat_id, user_message=user_message_to_log,
                ai_response=str(ai_response_text) if ai_response_text else " ",
                ai_model_name=model_name_for_log, prompt=prompt_to_log,
                request_json=request_json_to_log, response_json=response_json_to_log,
                status=log_status, error_message=error_message_to_log
            )
            logger.info(f"  Mesaj, '{chat_id}' ID'li sohbete '{log_status}' durumuyla loglandı.\n")
        except Exception as db_err:
            logger.error(f"  Veritabanına loglama sırasında hata (Sohbet ID: {chat_id}): {db_err}\n", exc_info=True)
    else:
        logger.warning("  UserMessageRepository import edilemediği için veritabanı loglaması atlandı.\n")
    # --- Veritabanına Loglama Sonu ---

    if api_status_code >= 400 and not use_mock_api :
        logger.warning(f"API hatası ({api_status_code}) kullanıcıya döndürülüyor: {ai_response_text}\n")
        return jsonify({"error": ai_response_text, "chatId": chat_id}), api_status_code

    logger.info(f"Başarılı yanıt kullanıcıya gönderiliyor. ChatID: {chat_id}\n")
    return jsonify({"response": str(ai_response_text), "chatId": chat_id})


# 8.2. POST /mock_gemini_api/... - Sahte Gemini API Yanıtı
# -----------------------------------------------------------------------------
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
@log_route_call_enhanced
def mock_gemini_generate_content_route():
    """
    Geliştirme ve test amaçlı sahte bir Gemini API endpoint'i.
    """
    logger.info("Sahte Gemini API (generateContent) ana mantığı çağrıldı.\n")
    data = request.json
    if not data:
        logger.warning("  Sahte Gemini API: İstek gövdesi boş.\n")
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
        logger.debug(f"  Sahte Gemini API: Kullanıcı metni olarak '{user_text}' ayıklandı.\n")

        mock_response_text = f"Bu, Gemini (gemini-2.0-flash modeli - SAHTE YANIT) tarafından mesajınıza verilen sahte bir yanıttır: '{user_text}'"
        logger.debug(f"  Sahte Gemini API: Üretilen yanıt (ilk 100): '{mock_response_text[:100]}...'\n")

        gemini_like_response = {
            "candidates": [{"content": {"parts": [{"text": mock_response_text}], "role": "model"},
                "finishReason": "STOP", "index": 0,
                "safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }],
            "promptFeedback": {"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]}
        }
        logger.info("  Sahte Gemini API yanıtı başarıyla oluşturuldu ve gönderiliyor.\n")
        return jsonify(gemini_like_response)

    except (KeyError, IndexError, TypeError) as e_payload:
        logger.error(f"  Sahte Gemini API - Geçersiz payload formatı: {e_payload}. Gelen data: {data}\n", exc_info=True)
        return jsonify({"error": "Geçersiz payload formatı. Beklenen: {'contents': [{'parts':[{'text': '...'}]}]}"}), 400
    except Exception as e_mock_gemini:
        logger.critical(f"  Sahte Gemini API - Beklenmedik kritik hata: {e_mock_gemini}\n", exc_info=True)
        return jsonify({"error": "Sahte Gemini API'sinde beklenmedik bir hata oluştu."}), 500

# İstenmeyen son log satırı kaldırıldı.
# logger.info("Ana Rotalar Modülü (main_routes.py) tanımlamaları tamamlandı.\n")