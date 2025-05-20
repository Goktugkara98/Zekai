# =============================================================================
# Ana Rotalar Modülü (Main Routes Module)
# =============================================================================
# Bu modül, uygulamanın ana kullanıcı arayüzü (HTML) ve temel API (JSON)
# rotalarını tanımlar. Ana sayfa gösterimi ve sohbet API'si gibi işlevleri
# içerir.
#
# Yapı:
# 1. İçe Aktarmalar (Imports)
# 2. Blueprint Tanımı (Blueprint Definition)
# 3. Yardımcı Fonksiyonlar (Helper Functions - Eğer varsa)
# 4. Arayüz Rotaları (View Routes - HTML Rendering)
#    4.1. Ana Sayfa
# 5. API Rotaları (API Routes - JSON)
#    5.1. Sohbet Mesajı Gönderme
#    5.2. Sahte (Mock) API Rotaları (Test amaçlı)
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import json
import traceback # Hata ayıklama için
from typing import Dict, Any, List, Tuple # Tip ipuçları için

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    current_app
)

# Uygulama özelindeki içe aktarmalar
# Veritabanı ve Depolar (Repositories)
# Not: DatabaseConnection doğrudan burada kullanılmıyor gibi görünüyor,
#      eğer db.session gibi bir global session nesnesi kullanılıyorsa
#      onun import edildiği yer ve nasıl başlatıldığı önemli.
# from app.models.base import DatabaseConnection # Eğer doğrudan kullanılacaksa
from app.repositories.model_repository import ModelRepository

# Servis Katmanı
from app.services.ai_model_service import fetch_ai_categories_from_db
from app.services.base_ai_service import BaseAIService


# 2. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
# 'main_bp' blueprint'i, bu modüldeki rotaları gruplar.
main_bp = Blueprint(
    name='main',  # Blueprint'in adı
    import_name=__name__,  # Blueprint'in bulunduğu modül
    template_folder='../templates', # HTML şablonlarının yolu (proje kök dizinine göre)
    static_folder='../static'     # Statik dosyaların (CSS, JS, resimler) yolu
)

# 3. Yardımcı Fonksiyonlar (Helper Functions)
# =============================================================================
# Bu bölümde, bu blueprint'e özel yardımcı fonksiyonlar tanımlanabilir.
# Şu an için bu dosyada özel bir yardımcı fonksiyon bulunmuyor.

# 4. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================

# 4.1. Ana Sayfa: / (GET)
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
        # AI kategorilerini servis katmanı aracılığıyla çek
        ai_categories = fetch_ai_categories_from_db()

        if not ai_categories:
            flash("AI kategorileri yüklenirken bir sorun oluştu veya hiç kategori bulunamadı. Lütfen daha sonra tekrar deneyin.", "warning")
            # Kullanıcıya boş bir liste yerine bilgilendirici bir kategori gösterilebilir
            ai_categories = [{"id":0, "name": "Kategoriler Yüklenemedi", "icon": "bi-exclamation-triangle", "models": []}]
    except Exception as e:
        current_app.logger.error(f"Ana sayfa kategorileri yüklenirken hata oluştu: {str(e)}", exc_info=True)
        flash("Sayfa yüklenirken beklenmedik bir sunucu hatası oluştu. Lütfen sistem yöneticisi ile iletişime geçin.", "danger")
        # Hata durumunda kullanıcıya bilgilendirici bir kategori göster
        ai_categories = [{"id":0, "name": "Sunucu Hatası", "icon": "bi-server", "models": []}]

    return render_template('index.html', ai_categories=ai_categories, title=page_title)


# 5. API Rotaları (API Routes - JSON)
# =============================================================================

# 5.1. Sohbet Mesajı Gönderme: /send_message (POST)
# -----------------------------------------------------------------------------
@main_bp.route('/send_message', methods=['POST'])
def send_message() -> Tuple[str, int]:
    """
    Kullanıcıdan gelen sohbet mesajını alır, AI modeline BaseAIService
    aracılığıyla gönderir ve AI'dan gelen cevabı JSON formatında döndürür.

    İstek Formatı (JSON):
    {
        "model_id": "<model_id:str>",
        "chat_message": "<kullanicinin_mesaji:str>",
        "chat_history": [
            {"role": "user", "content": "önceki mesaj"},
            {"role": "assistant", "content": "önceki cevap"}
        ] (opsiyonel:List[Dict[str,str]])
    }

    Başarılı Yanıt Formatı (JSON):
    {
        "response": "<ai_yaniti:str>",
        "chat_id": "<sohbet_id:str>", (opsiyonel)
        ... (servisten dönen diğer alanlar)
    }

    Hata Yanıt Formatı (JSON):
    {
        "error": "<hata_mesaji:str>",
        "details": "<hata_detayi:str>" (opsiyonel)
    }
    """
    print("\n----send_message BAŞLADI----")
    try:
        print("----request.json alınıyor----")
        data: Optional[Dict[str, Any]] = request.json
        print(f"Alınan data: {data}")
        
        if not data:
            print("HATA: İstek gövdesi boş")
            return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

        print("----JSON verilerini çıkarma----")
        model_id: Optional[str] = data.get('model_id')
        chat_message: Optional[str] = data.get('chat_message')
        chat_history: List[Dict[str, str]] = data.get('chat_history', [])
        print(f"model_id: {model_id}")
        print(f"chat_message: {chat_message}")
        print(f"chat_history uzunluğu: {len(chat_history)}")

        # Gerekli alanların kontrolü
        print("----Gerekli alanların kontrolü----")
        if not model_id:
            print("HATA: model_id alanı eksik")
            return jsonify({"error": "'model_id' alanı zorunludur."}), 400
        if not chat_message and not chat_history:
            print("HATA: chat_message ve chat_history her ikisi de boş")
            return jsonify({"error": "'chat_message' veya 'chat_history' alanlarından en az biri dolu olmalıdır."}), 400

        # Veritabanı bağlantısını/session'ını al
        print("----Veritabanı oturumu alınıyor----")
        try:
            # Bu satır, `db` nesnesinin Flask app context'inde `session` attribute'una
            # sahip olduğunu varsayar. Flask-SQLAlchemy gibi eklentilerde bu yaygındır.
            db_session = current_app.extensions['sqlalchemy'].db.session # Örnek bir erişim
            print(f"db_session alındı: {db_session}")
            
            print("====ModelRepository başlatılıyor====")
            model_repository = ModelRepository(db_session)
            print("====ModelRepository başlatıldı====")
        except (AttributeError, KeyError) as db_err:
            print(f"HATA: Veritabanı oturumu alınırken hata: {db_err}")
            current_app.logger.error(f"Veritabanı oturumu alınırken hata: {db_err}")
            return jsonify({"error": "Veritabanı bağlantı hatası.", "details": "Servis konfigürasyonunda sorun olabilir."}), 500


        # AI servisini başlat
        print("====BaseAIService başlatılıyor====")
        print(f"Parametreler: model_repository={model_repository}, config={current_app.config}")
        base_ai_service = BaseAIService(
            model_repository=model_repository,
            config=current_app.config # Flask uygulama yapılandırmasını servise aktar
        )
        print("====BaseAIService başlatıldı====")

        # Sohbet isteğini işle
        print("----process_chat_request çağrılıyor----")
        print(f"Parametreler: model_id={model_id}, chat_message={chat_message}, chat_history={chat_history}")
        response_data: Dict[str, Any] = base_ai_service.process_chat_request(
            model_id=str(model_id), # Model ID'sinin string olduğundan emin ol
            chat_message=chat_message,
            chat_history=chat_history
        )
        print(f"process_chat_request yanıtı: {response_data}")
        print("----process_chat_request tamamlandı----")

        # Yanıtı döndür
        print("----Yanıt hazırlanıyor----")
        status_code: int = response_data.get("status_code", 200 if "error" not in response_data else 400)
        print(f"status_code: {status_code}")
        if "status_code" in response_data: # status_code'u yanıttan çıkaralım, zaten HTTP status olarak kullanılıyor
            del response_data["status_code"]
            print("status_code yanıttan çıkarıldı")

        print(f"Döndürülen yanıt: {response_data}")
        print("----send_message TAMAMLANDI----\n")
        return jsonify(response_data), status_code

    except json.JSONDecodeError:
        current_app.logger.warning(f"Geçersiz JSON formatı /send_message: {request.data}", exc_info=True)
        return jsonify({"error": "Geçersiz JSON formatı."}), 400
    except Exception as e:
        current_app.logger.error(f"/send_message rotasında genel hata: {str(e)}", exc_info=True)
        # Geliştirme ortamında daha detaylı hata bilgisi döndürülebilir
        error_details = {"error": "Mesaj işlenirken sunucuda beklenmedik bir hata oluştu."}
        if current_app.debug: # Sadece debug modunda detaylı hata göster
            error_details["details"] = str(e)
            error_details["trace"] = traceback.format_exc()
        return jsonify(error_details), 500

# 5.2. Sahte (Mock) API Rotaları
# -----------------------------------------------------------------------------
# Bu bölüm, geliştirme ve test süreçlerini kolaylaştırmak için sahte API
# endpoint'lerini içerir.

# 5.2.1. Sahte Gemini API Yanıtı: /mock_gemini_api/... (POST)
# -----------------------------------------------------------------------------
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
def mock_gemini_generate_content_route() -> Tuple[str, int]:
    """
    Geliştirme ve test amaçlı sahte bir Gemini API endpoint'i.
    Google Gemini API'sinin `generateContent` metodunu taklit eder.

    İstek Formatı (JSON):
    {
        "contents": [{"parts":[{"text": "kullanıcı mesajı"}]}]
        ... (diğer Gemini API alanları)
    }

    Yanıt Formatı (JSON):
    Gemini API'sinin gerçek yanıt formatına benzer bir yapı.
    """
    try:
        data: Optional[Dict[str, Any]] = request.json
        if not data:
            return jsonify({"error": "İstek gövdesi JSON formatında olmalı ve boş olamaz."}), 400

        user_text: str = "bir mesaj (payload'dan alınamadı)"
        # Gelen payload'dan kullanıcı metnini güvenli bir şekilde çıkarmaya çalış
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

        # Gemini API'sinin yanıt formatına benzer bir sahte yanıt oluştur
        gemini_like_response: Dict[str, Any] = {
            "candidates": [{
                "content": {
                    "parts": [{"text": mock_response_text}],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0,
                "safetyRatings": [{
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "probability": "NEGLIGIBLE"
                    # Diğer güvenlik kategorileri eklenebilir
                }]
            }],
            "promptFeedback": {
                "safetyRatings": [{
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "probability": "NEGLIGIBLE"
                }]
            }
        }
        return jsonify(gemini_like_response), 200

    except (KeyError, IndexError, TypeError) as e:
        current_app.logger.warning(
            f"Sahte Gemini API'sine geçersiz payload: {str(e)}. Gelen data: {request.data}",
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

# =============================================================================
# Diğer yardımcı fonksiyonlar veya bu blueprint'e ait ek rotalar buraya
# eklenebilir.
# =============================================================================
