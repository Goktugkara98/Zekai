# =============================================================================
# Ana Rotalar Modülü (Main Routes Module)
# =============================================================================
# Bu modül, uygulamanın ana kullanıcı arayüzü ve temel API rotalarını tanımlar.
# Ana sayfa gösterimi ve sohbet API'si gibi işlevleri içerir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from flask import Blueprint, render_template, request, jsonify, flash, current_app
import json # jsonify için veya doğrudan JSON işlemleri için gerekebilir
from typing import Dict, Any, List # Tip ipuçları için

# Veritabanı ve Repolar
from app.models.base import DatabaseConnection
from app.repositories.model_repository import ModelRepository

# Servis Katmanı
from app.services.ai_model_service import fetch_ai_categories_from_db
from app.services.base_ai_service import BaseAIService


# 2. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../templates', # Proje yapınıza göre templates klasörünün doğru yolu
    static_folder='../static' # Proje yapınıza göre static klasörünün doğru yolu
)

# 3. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================

# 3.1. / (GET) - Ana Sayfa
# -----------------------------------------------------------------------------
@main_bp.route('/')
def index_page():
    """Ana sayfayı (index.html) AI kategorileriyle birlikte gösterir."""
    ai_categories: List[Dict[str, Any]] = []
    try:
        # ai_model_service = AIModelService(ModelRepository(db.session)) # Eğer fetch_ai_categories_from_db bir instance metodu ise
        # ai_categories = ai_model_service.fetch_ai_categories_from_db()
        ai_categories = fetch_ai_categories_from_db() # Eğer statik veya modül seviyesinde bir fonksiyon ise
        if not ai_categories:
            flash("AI kategorileri yüklenirken bir sorun oluştu veya hiç kategori bulunamadı. Lütfen daha sonra tekrar deneyin.", "warning")
            ai_categories = [{"name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
    except Exception as e:
        current_app.logger.error(f"Ana sayfa kategorileri yüklenirken hata: {e}")
        flash("Sayfa yüklenirken beklenmedik bir sunucu hatası oluştu.", "danger")
        ai_categories = [{"name": "Sunucu Hatası", "icon": "bi-server", "models": []}]
    
    return render_template('index.html', ai_categories=ai_categories, title="Ana Sayfa")

# 4. API Rotaları (API Routes - JSON)
# =============================================================================


# 4.2. POST /send_message - Sohbet Mesajlarını İşler (Yeni Akış)
# -----------------------------------------------------------------------------
@main_bp.route('/send_message', methods=['POST'])
def send_message():
    """
    Kullanıcıdan gelen mesajı alır, AI modeline BaseAIService aracılığıyla gönderir ve cevabı döndürür.
    İstek Formatı (JSON):
    {
        "model_id": "<model_id>",
        "chat_message": "<kullanicinin_mesaji>",
        "chat_history": [
            {"role": "user", "content": "önceki mesaj"},
            {"role": "assistant", "content": "önceki cevap"}
        ] (opsiyonel)
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

        model_id = data.get('model_id')
        chat_message = data.get('chat_message') # Yeni mesaj
        chat_history = data.get('chat_history', []) # Opsiyonel, konuşma geçmişi

        # model_id ve chat_message (veya chat_history) alanlarından en az biri dolu olmalı.
        # Sadece chat_history ile de istek atılabilir (örneğin "devam et" komutu).
        # Bu kontrolü BaseAIService içinde yapmak daha uygun olabilir.
        if not model_id:
            return jsonify({"error": "model_id alanı zorunludur."}), 400
        if not chat_message and not chat_history: # Eğer yeni mesaj yoksa ve geçmiş de boşsa hata ver
             return jsonify({"error": "chat_message veya chat_history alanlarından en az biri dolu olmalıdır."}), 400


        model_repository = ModelRepository(db.session)
        
        # BaseAIService'i başlat. Yapılandırma ve diğer bağımlılıklar buradan veya app factory'den gelebilir.
        # GoogleAIService gibi spesifik servisler BaseAIService içinde yönetilecek.
        base_ai_service = BaseAIService(
            model_repository=model_repository, 
            config=current_app.config
        )

        response_data = base_ai_service.process_chat_request(
            model_id=str(model_id), # ID'nin string olduğundan emin olalım
            chat_message=chat_message,
            chat_history=chat_history
        )

        # response_data'nın yapısı BaseAIService tarafından belirlenir.
        # Başarılı bir yanıt { "response": "...", "chat_id": "..." } gibi olabilir.
        # Hatalı bir yanıt { "error": "...", "details": "..." } gibi olabilir.
        if "error" in response_data:
             # Hata durumunda uygun HTTP status kodu ile dön. Servis bunu sağlayabilir.
            status_code = response_data.get("status_code", 400 if "error" in response_data else 200)
            return jsonify(response_data), status_code

        return jsonify(response_data)

    except Exception as e:
        current_app.logger.error(f"Mesaj gönderirken genel hata: {e}", exc_info=True)
        import traceback
        return jsonify({"error": "Mesaj işlenirken sunucuda beklenmedik bir hata oluştu.", "details": str(e), "trace": traceback.format_exc()}), 500

# 4.3. POST /mock_gemini_api/... - Sahte Gemini API Yanıtı (Korundu)
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

        mock_response_text = f"Bu, Gemini (gemini-2.0-flash modeli - DİREKT SAHTE YANIT) tarafından mesajınıza verilen sahte bir yanıttır: '{user_text}'"
        
        gemini_like_response = {
            "candidates": [{"content": {"parts": [{"text": mock_response_text}], "role": "model"},
                "finishReason": "STOP", "index": 0,
                "safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }],
            "promptFeedback": {"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]}
        }
        return jsonify(gemini_like_response)

    except (KeyError, IndexError, TypeError) as e:
        current_app.logger.warning(f"Sahte Gemini API'sine geçersiz payload: {e} - Gelen data: {data}")
        return jsonify({"error": "Geçersiz payload formatı. Beklenen: {'contents': [{'parts':[{'text': '...'}]}]}"}), 400
    except Exception as e:
        current_app.logger.error(f"Sahte Gemini API'sinde beklenmedik hata: {e}", exc_info=True)
        return jsonify({"error": "Sahte Gemini API'sinde beklenmedik bir hata oluştu."}), 500

# =============================================================================
# Diğer yardımcı fonksiyonlar veya rotalar buraya eklenebilir.
# =============================================================================
