# =============================================================================
# Admin Rotaları Modülü (Admin Routes Module)
# =============================================================================
# Bu modül, uygulamanın yönetici paneli arayüzü (HTML) ve ilgili API (JSON)
# rotalarını tanımlar. Kullanıcı, kategori, AI modeli yönetimi ve genel
# ayarlar gibi işlevleri içerir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 BLUEPRINT TANIMI (BLUEPRINT DEFINITION)
# 3.0 SERVİS ÖRNEKLERİ (SERVICE INSTANCES)
# 4.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
#     (Bu dosyada özel bir yardımcı fonksiyon bulunmamaktadır)
# 5.0 ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
#     5.1. dashboard_page         : Yönetici paneli ana sayfasını (dashboard) gösterir.
#     5.2. users_page             : Kullanıcı yönetimi sayfasını gösterir.
#     5.3. categories_page        : Kategori yönetimi sayfasını gösterir.
#     5.4. models_page            : AI Modeli yönetimi sayfasını gösterir.
#     5.5. settings_page          : Genel ayarlar sayfasını gösterir.
# 6.0 API ROTALARI (API ROUTES - JSON)
#     6.1. Kategori API'leri
#          6.1.1. api_add_category    : Yeni bir kategori ekler.
#          6.1.2. api_delete_category : Bir kategoriyi siler.
#          6.1.3. api_update_category : Bir kategoriyi günceller.
#     6.2. AI Model API'leri
#          6.2.1. api_add_model       : Yeni bir AI modeli ekler.
#          6.2.2. api_delete_model    : Bir AI modelini siler.
#          6.2.3. api_update_model    : Bir AI modelini günceller.
# 7.0 VERİTABANI OTURUMU YÖNETİMİ NOTLARI (DATABASE SESSION MANAGEMENT NOTES)
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
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
# from app.models.base import db_session # Servisler aracılığıyla yönetilmesi tercih edilir.

# =============================================================================
# 2.0 BLUEPRINT TANIMI (BLUEPRINT DEFINITION)
# =============================================================================
admin_bp = Blueprint(
    name='admin_bp',
    import_name=__name__,
    template_folder='../templates',
    url_prefix='/admin'
)

# =============================================================================
# 3.0 SERVİS ÖRNEKLERİ (SERVICE INSTANCES)
# =============================================================================
category_service = CategoryService()
model_service = AIModelService()
user_service = UserService()
dashboard_service = DashboardService()
settings_service = SettingsService()

# =============================================================================
# 4.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# =============================================================================
# Bu bölümde, bu blueprint'e özel yardımcı fonksiyonlar tanımlanabilir.
# Şu an için bu dosyada özel bir yardımcı fonksiyon bulunmuyor.

# =============================================================================
# 5.0 ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
# =============================================================================

# -----------------------------------------------------------------------------
# 5.1. Yönetici paneli ana sayfasını (dashboard) gösterir (dashboard_page)
#      Rotalar: /admin/ veya /admin/dashboard (GET)
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
        return render_template('admin_dashboard/admin_dashboard.html',
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

# -----------------------------------------------------------------------------
# 5.2. Kullanıcı yönetimi sayfasını gösterir (users_page)
#      Rota: /admin/users (GET)
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

# -----------------------------------------------------------------------------
# 5.3. Kategori yönetimi sayfasını gösterir (categories_page)
#      Rota: /admin/categories (GET)
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

# -----------------------------------------------------------------------------
# 5.4. AI Modeli yönetimi sayfasını gösterir (models_page)
#      Rota: /admin/models (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/models')
def models_page() -> str:
    """AI Modeli yönetimi sayfasını gösterir."""
    page_title: str = "AI Model Yönetimi"
    current_page_identifier: str = "models"
    try:
        models_data: List[Dict[str, Any]] = model_service.get_all_models_for_display()
        all_categories: List[Dict[str, Any]] = category_service.get_all_categories_for_display()
        page_content_data = {"models": models_data, "categories": all_categories}
        print(page_content_data)
        return render_template('admin_dashboard/admin_models.html',
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=page_content_data)
    except Exception as e:
        current_app.logger.error(f"Admin AI modelleri sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"AI Modelleri yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard/admin_dashboard.html',
                               title="Hata - AI Modelleri",
                               current_page=current_page_identifier,
                               page_data={"models": [], "categories": []})

# -----------------------------------------------------------------------------
# 5.5. Genel ayarlar sayfasını gösterir (settings_page)
#      Rota: /admin/settings (GET)
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

# =============================================================================
# 6.0 API ROTALARI (API ROUTES - JSON)
# =============================================================================

# -----------------------------------------------------------------------------
# 6.1. Kategori API'leri
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 6.1.1. Yeni bir kategori ekler (api_add_category)
#        Rota: /admin/api/categories (POST)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['POST'])
def api_add_category() -> Tuple[str, int]:
    """
    Yeni bir kategori ekler.
    İstek Formatı (JSON): {"name": "Kategori Adı", "description": "Açıklama (opsiyonel)"}
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
    except ValueError as ve:
        current_app.logger.warning(f"Kategori eklenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        return jsonify({'success': False, 'message': str(ve)}), 409 # Conflict
    except Exception as e:
        current_app.logger.error(f"Kategori eklerken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori eklenirken sunucuda bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.1.2. Bir kategoriyi siler (api_delete_category)
#        Rota: /admin/api/categories/<int:category_id> (DELETE)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id: int) -> Tuple[str, int]:
    """Belirtilen ID'ye sahip kategoriyi siler."""
    try:
        category_service.delete_category(category_id)
        return jsonify({'success': True, 'message': 'Kategori başarıyla silindi.'}), 200
    except ValueError as ve:
        current_app.logger.warning(f"Kategori (ID: {category_id}) silinirken hata: {str(ve)}")
        return jsonify({'success': False, 'message': str(ve)}), 404 # Not Found or Conflict
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) silinirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori silinirken sunucuda bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.1.3. Bir kategoriyi günceller (api_update_category)
#        Rota: /admin/api/categories/<int:category_id> (PUT)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
def api_update_category(category_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip kategoriyi günceller.
    İstek Formatı (JSON): {"name": "Yeni Ad", "description": "Yeni Açıklama (opsiyonel)"}
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or not data.get('name') or not str(data['name']).strip():
            return jsonify({'success': False, 'message': 'Kategori adı zorunludur ve boş olamaz.'}), 400

        updated_category: Dict[str, Any] = category_service.update_category(
            category_id=category_id,
            name=str(data['name']).strip(),
            description=str(data.get('description', '')).strip()
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla güncellendi.', 'category': updated_category}), 200
    except ValueError as ve:
        current_app.logger.warning(f"Kategori (ID: {category_id}) güncellenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        status_code = 404 if "bulunamadı" in str(ve).lower() else 409
        return jsonify({'success': False, 'message': str(ve)}), status_code
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) güncellenirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori güncellenirken sunucuda bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.2. AI Model API'leri
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 6.2.1. Yeni bir AI modeli ekler (api_add_model)
#        Rota: /admin/api/models (POST)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['POST'])
def api_add_model() -> Tuple[str, int]:
    """
    Yeni bir AI modeli ekler.
    İstek Formatı (JSON): Modelin tüm alanlarını içerebilir.
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'İstek gövdesi boş olamaz.'}), 400

        required_fields = ['name', 'category_id', 'service_provider', 'external_model_name'] # Temel zorunlu alanlar
        missing_fields = [field for field in required_fields if not data.get(field) or (isinstance(data.get(field), str) and not str(data.get(field)).strip())]

        if 'category_id' in data and (not isinstance(data['category_id'], int) or data['category_id'] <=0):
             missing_fields.append("category_id (geçerli bir sayı olmalı)")


        if missing_fields:
            return jsonify({'success': False, 'message': f"Eksik veya geçersiz zorunlu alanlar: {', '.join(missing_fields)}"}), 400

        # Servis tüm data'yı alır ve kendi içinde validasyon yapar.
        new_model: Dict[str, Any] = model_service.add_model_via_dict(data) # Servis metodunun adı varsayımsal
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla eklendi.', 'model': new_model}), 201
    except ValueError as ve:
        current_app.logger.warning(f"AI Modeli eklenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        current_app.logger.error(f"AI Modeli eklerken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'AI Modeli eklenirken sunucuda bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.2.2. Bir AI modelini getirir (api_get_model)
#        Rota: /admin/api/models/<int:model_id> (GET)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['GET'])
def api_get_model(model_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip AI modelini getirir.
    """
    try:
        model = model_service.get_model_by_id(model_id)
        if not model:
            return jsonify({'success': False, 'message': f'ID: {model_id} olan model bulunamadı.'}), 404
        return jsonify({'success': True, 'model': model}), 200
    except Exception as e:
        current_app.logger.error(f"Model bilgisi alınırken hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Model bilgisi alınırken bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.2.3. Bir AI modelini siler (api_delete_model)
#        Rota: /admin/api/models/<int:model_id> (DELETE)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
def api_delete_model(model_id: int) -> Tuple[str, int]:
    """Belirtilen ID'ye sahip AI modelini siler."""
    try:
        model_service.delete_model(model_id)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla silindi.'}), 200
    except ValueError as ve:
        current_app.logger.warning(f"AI Modeli (ID: {model_id}) silinirken hata: {str(ve)}")
        return jsonify({'success': False, 'message': str(ve)}), 404
    except Exception as e:
        current_app.logger.error(f"AI Modeli (ID: {model_id}) silinirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'AI Modeli silinirken sunucuda bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.2.3. Bir AI modelini günceller (api_update_model)
#        Rota: /admin/api/models/<int:model_id> (PUT)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
def api_update_model(model_id: int) -> Tuple[str, int]:
    """
    Belirtilen ID'ye sahip AI modelini günceller.
    İstek Formatı (JSON): Güncellenmek istenen alanları içeren bir sözlük.
    """
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Güncelleme verisi boş olamaz.'}), 400

        updated_model: Dict[str, Any] = model_service.update_model_via_dict(model_id, data) # Servis metodunun adı varsayımsal
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla güncellendi.', 'model': updated_model}), 200
    except ValueError as ve:
        current_app.logger.warning(f"AI Modeli (ID: {model_id}) güncellenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        status_code = 404 if "bulunamadı" in str(ve).lower() else 400
        return jsonify({'success': False, 'message': str(ve)}), status_code
    except Exception as e:
        current_app.logger.error(f"AI Modeli (ID: {model_id}) güncellenirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'AI Modeli güncellenirken sunucuda bir hata oluştu.'}), 500

# =============================================================================
# 7.0 VERİTABANI OTURUMU YÖNETİMİ NOTLARI (DATABASE SESSION MANAGEMENT NOTES)
# =============================================================================
# Flask uygulamanızda db_session'ın her request sonunda kaldırıldığından emin olun.
# Bu genellikle ana uygulama dosyanızda (örn: app/main.py veya app/__init__.py)
# @app.teardown_appcontext dekoratörü ile yapılır.
# Örnek:
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     from app.models.base import db_session # Import burada yapılmalı
#     if db_session:
#         db_session.remove()
# Bu koddaki servislerin (CategoryService, AIModelService vb.) veritabanı
# oturumunu nasıl aldıkları ve yönettikleri, projenin genel yapısına bağlıdır.
