# =============================================================================
# Admin Rotaları Modülü (Admin Routes Module)
# =============================================================================
# Bu modül, uygulamanın yönetici paneli arayüzü (HTML) ve ilgili API (JSON)
# rotalarını tanımlar. Kullanıcı, kategori, AI modeli yönetimi ve genel
# ayarlar gibi işlevleri içerir.
#
# Yapı:
# 1. İçe Aktarmalar (Imports)
# 2. Blueprint Tanımı (Blueprint Definition)
# 3. Servis Örnekleri (Service Instances)
# 4. Yardımcı Fonksiyonlar (Helper Functions - Eğer varsa)
# 5. Arayüz Rotaları (View Routes - HTML Rendering)
#    5.1. Dashboard
#    5.2. Kullanıcı Yönetimi
#    5.3. Kategori Yönetimi
#    5.4. AI Model Yönetimi
#    5.5. Ayarlar
# 6. API Rotaları (API Routes - JSON)
#    6.1. Kategori API'leri (Ekle, Sil, Güncelle)
#    6.2. AI Model API'leri (Ekle, Sil, Güncelle)
# 7. Veritabanı Oturumu Yönetimi Notları
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import traceback # Hata ayıklama için
from typing import Dict, Any, Tuple, Optional, List # Tip ipuçları için

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    current_app
)

# Uygulama özelindeki servislerin içe aktarılması
from app.services.admin_dashboard_services import (
    CategoryService,
    AIModelService,
    UserService,
    DashboardService,
    SettingsService
)
# Not: db_session'ın doğrudan route'larda kullanılmaması ve servisler
# aracılığıyla yönetilmesi iyi bir pratiktir. Orijinal koddaki yorum korunmuştur.
# from app.models.base import db_session

# 2. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
# 'admin_bp' blueprint'i, yönetici paneli ile ilgili rotaları gruplar.
admin_bp = Blueprint(
    name='admin_bp',  # Blueprint'in adı
    import_name=__name__,  # Blueprint'in bulunduğu modül
    template_folder='../templates', # HTML şablonlarının yolu
    url_prefix='/admin'  # Bu blueprint'teki tüm rotalar '/admin' ön ekiyle başlar
)

# 3. Servis Örnekleri (Service Instances)
# =============================================================================
# İlgili servislerin örnekleri, bu modüldeki rotalar tarafından kullanılmak üzere oluşturulur.
# Bu, servislerin state-less (durumsuz) olduğu varsayımına dayanır.
# Eğer servisler request bazlı state tutuyorsa, her request için yeniden oluşturulmaları gerekebilir.
category_service = CategoryService()
model_service = AIModelService()
user_service = UserService()
dashboard_service = DashboardService()
settings_service = SettingsService()

# 4. Yardımcı Fonksiyonlar (Helper Functions)
# =============================================================================
# Bu bölümde, bu blueprint'e özel yardımcı fonksiyonlar tanımlanabilir.
# Şu an için bu dosyada özel bir yardımcı fonksiyon bulunmuyor.


# 5. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================
# Bu rotalar, yönetici paneli için HTML sayfalarını render eder.
# Hepsi genellikle aynı 'admin_dashboard.html' şablonunu farklı verilerle kullanır.

# 5.1. Dashboard: /admin/ veya /admin/dashboard (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard_page() -> str:
    """
    Yönetici panelinin ana sayfasını (dashboard) gösterir.
    Genel istatistikleri ve bilgileri içerir.
    """
    page_title: str = "Admin Paneli - Dashboard"
    current_page_identifier: str = "dashboard"
    try:
        stats: Dict[str, Any] = dashboard_service.get_dashboard_stats()
        return render_template('admin_dashboard.html',
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=stats)
    except Exception as e:
        current_app.logger.error(f"Admin dashboard yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Dashboard yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html',
                               title="Hata - Dashboard",
                               current_page=current_page_identifier,
                               page_data={})

# 5.2. Kullanıcı Yönetimi: /admin/users (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/users')
def users_page() -> str:
    """Kullanıcı yönetimi sayfasını gösterir."""
    page_title: str = "Kullanıcı Yönetimi"
    current_page_identifier: str = "users"
    try:
        users_data: List[Dict[str, Any]] = user_service.get_all_users_for_display()
        return render_template('admin_dashboard.html',
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=users_data)
    except Exception as e:
        current_app.logger.error(f"Admin kullanıcılar sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Kullanıcılar yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html',
                               title="Hata - Kullanıcılar",
                               current_page=current_page_identifier,
                               page_data=[])

# 5.3. Kategori Yönetimi: /admin/categories (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/categories')
def categories_page() -> str:
    """Kategori yönetimi sayfasını gösterir."""
    page_title: str = "Kategori Yönetimi"
    current_page_identifier: str = "categories"
    try:
        categories_data: List[Dict[str, Any]] = category_service.get_all_categories_for_display()
        return render_template('admin_dashboard.html',
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=categories_data)
    except Exception as e:
        current_app.logger.error(f"Admin kategoriler sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Kategoriler yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html',
                               title="Hata - Kategoriler",
                               current_page=current_page_identifier,
                               page_data=[])

# 5.4. AI Model Yönetimi: /admin/models (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/models')
def models_page() -> str:
    """AI Modeli yönetimi sayfasını gösterir."""
    page_title: str = "AI Model Yönetimi"
    current_page_identifier: str = "models"
    try:
        models_data: List[Dict[str, Any]] = model_service.get_all_models_for_display()
        # AI Modeli ekleme/düzenleme formu için kategorileri de gönderelim
        all_categories: List[Dict[str, Any]] = category_service.get_all_categories_for_display()
        page_content_data = {"models": models_data, "categories": all_categories}
        return render_template('admin_dashboard.html',
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=page_content_data)
    except Exception as e:
        current_app.logger.error(f"Admin AI modelleri sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"AI Modelleri yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html',
                               title="Hata - AI Modelleri",
                               current_page=current_page_identifier,
                               page_data={"models": [], "categories": []})

# 5.5. Ayarlar: /admin/settings (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/settings')
def settings_page() -> str:
    """Genel ayarlar sayfasını gösterir."""
    page_title: str = "Ayarlar"
    current_page_identifier: str = "settings"
    try:
        settings_data: Dict[str, Any] = settings_service.get_settings_for_display()
        return render_template('admin_dashboard.html',
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=settings_data)
    except Exception as e:
        current_app.logger.error(f"Admin ayarlar sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Ayarlar yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html',
                               title="Hata - Ayarlar",
                               current_page=current_page_identifier,
                               page_data={})

# 6. API Rotaları (API Routes - JSON)
# =============================================================================
# Bu rotalar, yönetici panelindeki CRUD işlemleri için JSON tabanlı API sağlar.

# 6.1. Kategori API'leri
# -----------------------------------------------------------------------------

# 6.1.1. Kategori Ekle: /admin/api/categories (POST)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['POST'])
def api_add_category() -> Tuple[str, int]:
    """
    Yeni bir kategori ekler.
    İstek Formatı (JSON): {"name": "Kategori Adı", "description": "Açıklama (opsiyonel)"}
    Başarılı Yanıt (JSON, 201): {"success": true, "message": "...", "category": {...}}
    Hata Yanıtı (JSON, 400/409/500): {"success": false, "message": "..."}
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or not data.get('name') or not str(data['name']).strip():
            return jsonify({'success': False, 'message': 'Kategori adı zorunludur ve boş olamaz.'}), 400

        new_category: Dict[str, Any] = category_service.add_category(
            name=str(data['name']).strip(),
            description=str(data.get('description', '')).strip()
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla eklendi.', 'category': new_category}), 201
    except ValueError as ve: # Servis tarafından beklenen bir hata (örn: isim zaten var)
        current_app.logger.warning(f"Kategori eklenirken hata: {str(ve)}. Gelen veri: {data}")
        return jsonify({'success': False, 'message': str(ve)}), 409 # Conflict
    except Exception as e:
        current_app.logger.error(f"Kategori eklerken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Kategori eklenirken sunucuda bir hata oluştu.'}), 500

# 6.1.2. Kategori Sil: /admin/api/categories/<int:category_id> (DELETE)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip kategoriyi siler.
    Başarılı Yanıt (JSON, 200): {"success": true, "message": "..."}
    Hata Yanıtı (JSON, 404/500): {"success": false, "message": "..."}
    """
    try:
        category_service.delete_category(category_id)
        return jsonify({'success': True, 'message': 'Kategori başarıyla silindi.'}), 200
    except ValueError as ve: # Servis tarafından beklenen bir hata (örn: kategori bulunamadı, bağlı modeller var)
        current_app.logger.warning(f"Kategori (ID: {category_id}) silinirken hata: {str(ve)}")
        return jsonify({'success': False, 'message': str(ve)}), 404 # Not Found or Conflict
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) silinirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Kategori silinirken sunucuda bir hata oluştu.'}), 500

# 6.1.3. Kategori Güncelle: /admin/api/categories/<int:category_id> (PUT)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
def api_update_category(category_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip kategoriyi günceller.
    İstek Formatı (JSON): {"name": "Yeni Ad", "description": "Yeni Açıklama (opsiyonel)"}
    Başarılı Yanıt (JSON, 200): {"success": true, "message": "...", "category": {...}}
    Hata Yanıtı (JSON, 400/404/409/500): {"success": false, "message": "..."}
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or not data.get('name') or not str(data['name']).strip(): # En azından isim güncellenmeli
            return jsonify({'success': False, 'message': 'Kategori adı zorunludur ve boş olamaz.'}), 400

        updated_category: Dict[str, Any] = category_service.update_category(
            category_id=category_id,
            name=str(data['name']).strip(),
            description=str(data.get('description', '')).strip() # None ise boş string
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla güncellendi.', 'category': updated_category}), 200
    except ValueError as ve: # Servis tarafından beklenen hata (örn: bulunamadı, isim zaten var)
        current_app.logger.warning(f"Kategori (ID: {category_id}) güncellenirken hata: {str(ve)}. Gelen veri: {data}")
        # Hatanın içeriğine göre 404 veya 409 döndürülebilir
        status_code = 404 if "bulunamadı" in str(ve).lower() else 409
        return jsonify({'success': False, 'message': str(ve)}), status_code
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) güncellenirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Kategori güncellenirken sunucuda bir hata oluştu.'}), 500


# 6.2. AI Model API'leri
# -----------------------------------------------------------------------------

# 6.2.1. AI Model Ekle: /admin/api/models (POST)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['POST'])
def api_add_model() -> Tuple[str, int]:
    """
    Yeni bir AI modeli ekler.
    İstek Formatı (JSON): {
        "name": "Model Adı", "category_id": 1, "api_url": "http://...",
        "description": "...", "api_method": "POST", "api_key": "...",
        "request_headers": {}, "request_body": {}, "response_path": "...",
        "status": "active", "icon": "bi-..."
    }
    Başarılı Yanıt (JSON, 201): {"success": true, "message": "...", "model": {...}}
    Hata Yanıtı (JSON, 400/500): {"success": false, "message": "..."}
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'İstek gövdesi boş olamaz.'}), 400

        # Zorunlu alanların kontrolü
        required_fields = ['name', 'category_id', 'api_url']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'success': False, 'message': f"Eksik zorunlu alanlar: {', '.join(missing_fields)}"}), 400
        if not str(data['name']).strip() or not str(data['api_url']).strip():
             return jsonify({'success': False, 'message': "Model adı ve API URL boş olamaz."}), 400
        if not isinstance(data['category_id'], int) or data['category_id'] <=0:
            return jsonify({'success': False, 'message': "Geçerli bir kategori ID'si girilmelidir."}), 400


        # Servise tüm alanları gönder, servis kendi içinde daha detaylı validasyon yapabilir.
        new_model: Dict[str, Any] = model_service.add_model(
            name=str(data['name']).strip(),
            category_id=data['category_id'],
            description=str(data.get('description', '')).strip(),
            api_url=str(data['api_url']).strip(),
            api_method=str(data.get('api_method', 'POST')).upper().strip(),
            api_key=data.get('api_key'), # String veya None olabilir
            request_headers=data.get('request_headers', {}), # Dict olmalı
            request_body=data.get('request_body', {}),       # Dict olmalı
            response_path=data.get('response_path'),         # String veya None olabilir
            status=str(data.get('status', 'active')).lower().strip(),
            icon=data.get('icon')                            # String veya None olabilir
        )
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla eklendi.', 'model': new_model}), 201
    except ValueError as ve: # Servisten gelen validasyon hatası (örn: kategori yok, URL geçersiz)
        current_app.logger.warning(f"AI Modeli eklenirken hata: {str(ve)}. Gelen veri: {data}")
        return jsonify({'success': False, 'message': str(ve)}), 400 # Bad Request
    except Exception as e:
        current_app.logger.error(f"AI Modeli eklerken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'AI Modeli eklenirken sunucuda bir hata oluştu.'}), 500

# 6.2.2. AI Model Sil: /admin/api/models/<int:model_id> (DELETE)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
def api_delete_model(model_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip AI modelini siler.
    Başarılı Yanıt (JSON, 200): {"success": true, "message": "..."}
    Hata Yanıtı (JSON, 404/500): {"success": false, "message": "..."}
    """
    try:
        model_service.delete_model(model_id)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla silindi.'}), 200
    except ValueError as ve: # Model bulunamadı
        current_app.logger.warning(f"AI Modeli (ID: {model_id}) silinirken hata: {str(ve)}")
        return jsonify({'success': False, 'message': str(ve)}), 404 # Not Found
    except Exception as e:
        current_app.logger.error(f"AI Modeli (ID: {model_id}) silinirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'AI Modeli silinirken sunucuda bir hata oluştu.'}), 500

# 6.2.3. AI Model Güncelle: /admin/api/models/<int:model_id> (PUT)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
def api_update_model(model_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip AI modelini günceller.
    İstek Formatı (JSON): Güncellenmek istenen alanları içeren bir sözlük.
                         Örn: {"name": "Yeni Model Adı", "description": "Yeni açıklama"}
    Başarılı Yanıt (JSON, 200): {"success": true, "message": "...", "model": {...}}
    Hata Yanıtı (JSON, 400/404/500): {"success": false, "message": "..."}
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data: # Güncellenecek hiçbir veri gönderilmediyse
            return jsonify({'success': False, 'message': 'Güncelleme verisi boş olamaz.'}), 400

        # Servis, data içindeki geçerli alanları alıp güncelleme yapacaktır.
        updated_model: Dict[str, Any] = model_service.update_model(model_id, data)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla güncellendi.', 'model': updated_model}), 200
    except ValueError as ve: # Model bulunamadı veya geçersiz veri
        current_app.logger.warning(f"AI Modeli (ID: {model_id}) güncellenirken hata: {str(ve)}. Gelen veri: {data}")
        status_code = 404 if "bulunamadı" in str(ve).lower() else 400
        return jsonify({'success': False, 'message': str(ve)}), status_code
    except Exception as e:
        current_app.logger.error(f"AI Modeli (ID: {model_id}) güncellenirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'AI Modeli güncellenirken sunucuda bir hata oluştu.'}), 500

# 7. Veritabanı Oturumu Yönetimi Notları
# =============================================================================
# Flask uygulamanızda db_session'ın her request sonunda kaldırıldığından emin olun.
# Bu genellikle ana uygulama dosyanızda (örn: app/main.py veya app/__init__.py)
# @app.teardown_appcontext dekoratörü ile yapılır:
#
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     from app.models.base import db_session # Import burada yapılmalı
#     if db_session: # Oturumun var olup olmadığını kontrol et
#         db_session.remove()
#
# Eğer bu tür bir merkezi oturum yönetimi zaten varsa, servislerdeki
# db_session.remove() çağrıları gereksiz olabilir veya çakışmalara yol açabilir.
# Projenizin veritabanı oturum yönetimi stratejisine göre en uygun olanı seçilmelidir.
# Servislerin kendi oturumlarını yönetmesi (örn: context manager ile) veya
# merkezi bir oturumun enjekte edilmesi yaygın yaklaşımlardır.
# Bu koddaki servislerin (CategoryService, AIModelService vb.) veritabanı
# oturumunu nasıl aldıkları ve yönettikleri önemlidir.
# Orijinal kodda servislerin örnekleri global olarak oluşturulduğundan,
# oturum yönetimine özellikle dikkat edilmelidir.
