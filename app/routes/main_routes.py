# =============================================================================
# Ana Rotalar Modülü (Main Routes Module)
# =============================================================================
# Bu modül, uygulamanın ana kullanıcı arayüzü (HTML) ve temel API (JSON)
# rotalarını tanımlar. Ana sayfa gösterimi ve sohbet API'si gibi işlevleri
# içerir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 BLUEPRINT TANIMI (BLUEPRINT DEFINITION)
# 3.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
#     (Bu dosyada özel bir yardımcı fonksiyon bulunmamaktadır)
# 4.0 ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
#     4.1. index_page                     : Ana sayfayı gösterir.
# 5.0 API ROTALARI (API ROUTES - JSON)
#     5.1. send_message                   : Sohbet mesajını işler ve AI yanıtını döndürür.
#     5.2. Sahte (Mock) API Rotaları (Test Amaçlı)
#          5.2.1. mock_gemini_generate_content_route : Sahte Gemini API yanıtı üretir.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
import json
import traceback # Hata ayıklama için
from typing import Dict, Any, List, Tuple, Optional # Tip ipuçları için

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    current_app
)

# Uygulama özelindeki içe aktarmalar
from app.repositories.model_repository import ModelRepository
from app.services.ai_model_service import fetch_ai_categories_from_db # Kategori ve model listeleme servisi
from app.services.base_ai_service import BaseAIService # Ana AI işleme servisi
from app.models.base import DatabaseConnection # Veritabanı bağlantısı için

# =============================================================================
# 2.0 BLUEPRINT TANIMI (BLUEPRINT DEFINITION)
# =============================================================================
main_bp = Blueprint(
    name='main',
    import_name=__name__,
    template_folder='../templates',
    static_folder='../static'
)

# =============================================================================
# 3.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# =============================================================================
# Bu bölümde, bu blueprint'e özel yardımcı fonksiyonlar tanımlanabilir.
# Şu an için bu dosyada özel bir yardımcı fonksiyon bulunmuyor.

# =============================================================================
# 4.0 ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
# =============================================================================

# -----------------------------------------------------------------------------
# 4.1. Ana sayfayı gösterir (index_page)
#      Rota: / (GET)
# -----------------------------------------------------------------------------
@main_bp.route('/')
def index_page() -> str:
    """
    Ana sayfayı (index.html) AI kategorileriyle birlikte gösterir.
    Kategoriler veritabanından çekilir ve şablona gönderilir.
    Hata durumunda kullanıcıya bilgi mesajı gösterilir ve loglama yapılır.
    """
    ai_categories: List[Dict[str, Any]] = []
    page_title: str = "Ana Sayfa"

    try:
        ai_categories = fetch_ai_categories_from_db()
        if not ai_categories:
            flash("AI kategorileri yüklenirken bir sorun oluştu veya hiç kategori bulunamadı. Lütfen daha sonra tekrar deneyin.", "warning")
            ai_categories = [{"id":0, "name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
    except Exception as e:
        current_app.logger.error(f"Ana sayfa kategorileri yüklenirken hata oluştu: {str(e)}", exc_info=True)
        flash("Sayfa yüklenirken beklenmedik bir sunucu hatası oluştu. Lütfen sistem yöneticisi ile iletişime geçin.", "danger")
        ai_categories = [{"id":0, "name": "Sunucu Hatası", "icon": "bi-server", "models": []}]

    return render_template('index.html', ai_categories=ai_categories, title=page_title)

# =============================================================================
# 5.0 API ROTALARI (API ROUTES - JSON)
# =============================================================================

# -----------------------------------------------------------------------------
# 5.1. Sohbet mesajını işler ve AI yanıtını döndürür (send_message)
#      Rota: /send_message (POST)
# -----------------------------------------------------------------------------
@main_bp.route('/send_message', methods=['POST'])
def send_message() -> Tuple[str, int]:
    """
    Kullanıcıdan gelen sohbet mesajını alır, AI modeline BaseAIService
    aracılığıyla gönderir ve AI'dan gelen cevabı JSON formatında döndürür.
    """
    db_connection_instance: Optional[DatabaseConnection] = None
    try:
        data: Optional[Dict[str, Any]] = request.json
        if not data:
            return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

        model_id_str: Optional[str] = data.get('aiModelId') # Frontend'den string olarak gelebilir
        chat_message: Optional[str] = data.get('chat_message')
        chat_history: List[Dict[str, str]] = data.get('history', [])

        if not model_id_str: # Model ID'si string veya int olabilir, int'e çevirmeye çalışacağız
            return jsonify({"error": "'aiModelId' alanı zorunludur."}), 400

        try:
            model_id_int = int(model_id_str) # Integer'a çevirmeyi dene
        except ValueError:
            return jsonify({"error": "'aiModelId' geçerli bir sayı olmalıdır."}), 400


        if not chat_message and not chat_history: # Mesaj veya geçmişten en az biri olmalı
            return jsonify({"error": "'chat_message' veya 'chat_history' alanlarından en az biri dolu olmalıdır."}), 400

        db_connection_instance = DatabaseConnection() # Her istek için yeni bağlantı
        model_repository = ModelRepository(db_connection_instance)

        base_ai_service = BaseAIService(
            model_repository=model_repository,
            config=current_app.config
        )

        response_data: Dict[str, Any] = base_ai_service.process_chat_request(
            model_id=model_id_int, # Artık integer
            chat_message=chat_message,
            chat_history=chat_history
        )

        status_code: int = response_data.get("status_code", 200 if "error" not in response_data else 400)
        if "status_code" in response_data:
            del response_data["status_code"]

        return jsonify(response_data), status_code

    except json.JSONDecodeError:
        current_app.logger.warning(f"Geçersiz JSON formatı /send_message: {request.data.decode(errors='ignore')}", exc_info=True)
        return jsonify({"error": "Geçersiz JSON formatı."}), 400
    except Exception as e:
        current_app.logger.error(f"/send_message rotasında genel hata: {str(e)}", exc_info=True)
        error_details = {"error": "Mesaj işlenirken sunucuda beklenmedik bir hata oluştu."}
        if current_app.debug:
            error_details["details"] = str(e)
            error_details["trace"] = traceback.format_exc()
        return jsonify(error_details), 500
    finally:
        if db_connection_instance: # Bağlantı örneği oluşturulduysa kapat
            db_connection_instance.close()


# -----------------------------------------------------------------------------
# 5.2. Sahte (Mock) API Rotaları (Test Amaçlı)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 5.2.1. Sahte Gemini API yanıtı üretir (mock_gemini_generate_content_route)
#        Rota: /mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent (POST)
# -----------------------------------------------------------------------------
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
def mock_gemini_generate_content_route() -> Tuple[str, int]:
    """
    Geliştirme ve test amaçlı sahte bir Gemini API endpoint'i.
    Google Gemini API'sinin `generateContent` metodunu taklit eder.
    """
    try:
        data: Optional[Dict[str, Any]] = request.json
        if not data:
            return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

        user_text: str = "bir mesaj (payload'dan alınamadı)"
        if (isinstance(data.get("contents"), list) and
                data["contents"] and
                isinstance(data["contents"][-1], dict) and
                isinstance(data["contents"][-1].get("parts"), list) and
                data["contents"][-1]["parts"] and
                isinstance(data["contents"][-1]["parts"][0], dict) and
                "text" in data["contents"][-1]["parts"][0]):
            user_text = data["contents"][-1]["parts"][0]["text"]

        mock_response_text: str = (
            f"Bu, Gemini (gemini-2.0-flash modeli - SAHTE YANIT) tarafından "
            f"mesajınıza ('{user_text}') verilen sahte bir yanıttır."
        )

        gemini_like_response: Dict[str, Any] = {
            "candidates": [{
                "content": {
                    "parts": [{"text": mock_response_text}],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0,
                "safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }],
            "promptFeedback": {
                "safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }
        }
        return jsonify(gemini_like_response), 200

    except (KeyError, IndexError, TypeError) as e:
        current_app.logger.warning(
            f"Sahte Gemini API'sine geçersiz payload: {str(e)}. Gelen data: {request.data.decode(errors='ignore')}",
            exc_info=True
        )
        return jsonify({
            "error": "Geçersiz payload formatı.",
            "expected_format_example": "{'contents': [{'parts':[{'text': '...'}]}]}"
        }), 400
    except Exception as e:
        current_app.logger.error(
            f"Sahte Gemini API'sinde beklenmedik hata: {str(e)}",
            exc_info=True
        )
        return jsonify({"error": "Sahte Gemini API'sinde beklenmedik bir sunucu hatası oluştu."}), 500
