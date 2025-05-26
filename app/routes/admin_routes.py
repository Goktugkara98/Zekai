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
# 5.0 ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
# 6.0 API ROTALARI (API ROUTES - JSON)
#     6.1. Kategori API'leri
#          6.1.1. api_add_category    : Yeni bir kategori ekler.
#          6.1.2. api_delete_category : Bir kategoriyi siler.
#          6.1.3. api_update_category : Bir kategoriyi günceller.
#          6.1.4. api_get_category    : Bir kategoriyi ID ile getirir. (YENİ)
#     6.2. AI Model API'leri
#          6.2.1. api_add_model       : Yeni bir AI modeli ekler.
#          6.2.2. api_get_model       : Bir AI modelini ID ile getirir.
#          6.2.3. api_delete_model    : Bir AI modelini siler.
#          6.2.4. api_update_model    : Bir AI modelini günceller.
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

from app.services.admin_dashboard_services import (
    CategoryService,
    AIModelService,
    UserService,
    DashboardService,
    SettingsService
)

# =============================================================================
# 2.0 BLUEPRINT TANIMI (BLUEPRINT DEFINITION)
# =============================================================================
admin_bp = Blueprint(
    name='admin_bp',
    import_name=__name__,
    template_folder='../templates', # Şablon klasör yolu doğru olmalı
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
# 5.0 ARAYÜZ ROTALARI (VIEW ROUTES - HTML RENDERING)
# =============================================================================

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard_page() -> str:
    page_title: str = "Admin Paneli - Dashboard"
    current_page_identifier: str = "dashboard"
    try:
        stats: Dict[str, Any] = dashboard_service.get_dashboard_stats()
        return render_template('admin_dashboard/admin_dashboard.html', # Ana şablon
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=stats)
    except Exception as e:
        current_app.logger.error(f"Admin dashboard yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Dashboard yüklenirken bir hata oluştu: {str(e)}", "danger")
        # Hata durumunda da ana şablonu ve boş page_data'yı render et
        return render_template('admin_dashboard/admin_dashboard.html',
                               title="Hata - Dashboard",
                               current_page=current_page_identifier,
                               page_data={})

@admin_bp.route('/users')
def users_page() -> str:
    page_title: str = "Kullanıcı Yönetimi"
    current_page_identifier: str = "users"
    try:
        users_data: List[Dict[str, Any]] = user_service.get_all_users_for_display()
        # Kullanıcılar için ayrı bir HTML dosyası varsa, onu render et
        # Örnek: return render_template('admin_dashboard/admin_users.html', ...)
        # Şimdilik admin_dashboard.html'i page_data ile kullanıyoruz
        return render_template('admin_dashboard/admin_dashboard.html', # Veya admin_users.html
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data={"users": users_data, "message": "Kullanıcı yönetimi sayfası yakında..."}) # Örnek page_data
    except Exception as e:
        current_app.logger.error(f"Admin kullanıcılar sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Kullanıcılar yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard/admin_dashboard.html',
                               title="Hata - Kullanıcılar",
                               current_page=current_page_identifier,
                               page_data={"users": []})

@admin_bp.route('/categories')
def categories_page() -> str:
    page_title: str = "Kategori Yönetimi"
    current_page_identifier: str = "categories"
    try:
        categories_data: List[Dict[str, Any]] = category_service.get_all_categories_for_display()
        page_content_data = {"categories": categories_data}
        return render_template('admin_dashboard/admin_categories.html', # Kategoriye özel HTML
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=page_content_data)
    except Exception as e:
        current_app.logger.error(f"Admin kategoriler sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Kategoriler yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard/admin_dashboard.html', # Hata durumunda ana dashboard
                               title="Hata - Kategoriler",
                               current_page=current_page_identifier,
                               page_data={"categories": []})

@admin_bp.route('/models')
def models_page() -> str:
    page_title: str = "AI Model Yönetimi"
    current_page_identifier: str = "models"
    try:
        models_data: List[Dict[str, Any]] = model_service.get_all_models_for_display()
        all_categories: List[Dict[str, Any]] = category_service.get_all_categories_for_display()
        page_content_data = {"models": models_data, "categories": all_categories}
        return render_template('admin_dashboard/admin_models.html', # Modele özel HTML
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data=page_content_data)
    except Exception as e:
        current_app.logger.error(f"Admin AI modelleri sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"AI Modelleri yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard/admin_dashboard.html', # Hata durumunda ana dashboard
                               title="Hata - AI Modelleri",
                               current_page=current_page_identifier,
                               page_data={"models": [], "categories": []})

@admin_bp.route('/settings')
def settings_page() -> str:
    page_title: str = "Ayarlar"
    current_page_identifier: str = "settings"
    try:
        settings_data: Dict[str, Any] = settings_service.get_settings_for_display()
         # Ayarlar için ayrı bir HTML dosyası varsa, onu render et
        # Örnek: return render_template('admin_dashboard/admin_settings.html', ...)
        return render_template('admin_dashboard/admin_dashboard.html', # Veya admin_settings.html
                               title=page_title,
                               current_page=current_page_identifier,
                               page_data={"settings": settings_data, "message": "Ayarlar sayfası yakında..."}) # Örnek page_data
    except Exception as e:
        current_app.logger.error(f"Admin ayarlar sayfası yüklenirken hata: {str(e)}", exc_info=True)
        flash(f"Ayarlar yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard/admin_dashboard.html',
                               title="Hata - Ayarlar",
                               current_page=current_page_identifier,
                               page_data={})

# =============================================================================
# 6.0 API ROTALARI (API ROUTES - JSON)
# =============================================================================

# -----------------------------------------------------------------------------
# 6.1. Kategori API'leri
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['POST'])
def api_add_category() -> Tuple[Any, int]: # jsonify otomatik olarak str döndürür
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or not data.get('name') or not str(data['name']).strip():
            return jsonify({'success': False, 'message': 'Kategori adı zorunludur ve boş olamaz.'}), 400

        new_category: Dict[str, Any] = category_service.add_category(
            name=str(data['name']).strip(),
            description=str(data.get('description', '')).strip(),
            icon=str(data.get('icon', '')).strip() or None, # icon eklendi
            # status=str(data.get('status', 'active')).strip() # status eklendi, CategoryService'de de handle edilmeli
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla eklendi.', 'category': new_category}), 201
    except ValueError as ve:
        current_app.logger.warning(f"Kategori eklenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        return jsonify({'success': False, 'message': str(ve)}), 409
    except Exception as e:
        current_app.logger.error(f"Kategori eklerken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori eklenirken sunucuda bir hata oluştu.'}), 500

@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id: int) -> Tuple[Any, int]:
    try:
        category_service.delete_category(category_id)
        return jsonify({'success': True, 'message': 'Kategori başarıyla silindi.'}), 200
    except ValueError as ve:
        current_app.logger.warning(f"Kategori (ID: {category_id}) silinirken hata: {str(ve)}")
        return jsonify({'success': False, 'message': str(ve)}), 404
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) silinirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori silinirken sunucuda bir hata oluştu.'}), 500

@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
def api_update_category(category_id: int) -> Tuple[Any, int]:
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or not data.get('name') or not str(data['name']).strip():
            return jsonify({'success': False, 'message': 'Kategori adı zorunludur ve boş olamaz.'}), 400

        updated_category: Dict[str, Any] = category_service.update_category(
            category_id=category_id,
            name=str(data['name']).strip(),
            description=str(data.get('description', '')).strip(), # Eğer description güncellenmeyecekse None gönderilebilir
            icon=str(data.get('icon', '')).strip() or None, # icon eklendi
            # status=str(data.get('status', 'active')).strip() # status eklendi
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla güncellendi.', 'category': updated_category}), 200
    except ValueError as ve:
        current_app.logger.warning(f"Kategori (ID: {category_id}) güncellenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        status_code = 404 if "bulunamadı" in str(ve).lower() else 409
        return jsonify({'success': False, 'message': str(ve)}), status_code
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) güncellenirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori güncellenirken sunucuda bir hata oluştu.'}), 500

# YENİ EKLENEN ROTA: Bir kategoriyi ID ile getirme
@admin_bp.route('/api/categories/<int:category_id>', methods=['GET'])
def api_get_category(category_id: int) -> Tuple[Any, int]:
    """Belirtilen ID'ye sahip kategoriyi getirir."""
    try:
        category_data = category_service.get_category_by_id_for_display(category_id)
        if not category_data:
            return jsonify({'success': False, 'message': f'ID: {category_id} olan kategori bulunamadı.'}), 404
        return jsonify({'success': True, 'category': category_data}), 200
    except Exception as e:
        current_app.logger.error(f"Kategori (ID: {category_id}) bilgisi alınırken hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Kategori bilgisi alınırken bir hata oluştu.'}), 500

# -----------------------------------------------------------------------------
# 6.2. AI Model API'leri
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['POST'])
def api_add_model() -> Tuple[Any, int]:
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'İstek gövdesi boş olamaz.'}), 400

        required_fields = ['name', 'category_id', 'service_provider', 'external_model_name']
        missing_fields = [field for field in required_fields if not data.get(field) or (isinstance(data.get(field), str) and not str(data.get(field)).strip())]
        if 'category_id' in data and (not isinstance(data['category_id'], int) or data['category_id'] <=0):
             missing_fields.append("category_id (geçerli bir sayı olmalı)")
        if missing_fields:
            return jsonify({'success': False, 'message': f"Eksik veya geçersiz zorunlu alanlar: {', '.join(missing_fields)}"}), 400

        new_model: Dict[str, Any] = model_service.add_model_via_dict(data)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla eklendi.', 'model': new_model}), 201
    except ValueError as ve:
        current_app.logger.warning(f"AI Modeli eklenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        current_app.logger.error(f"AI Modeli eklerken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'AI Modeli eklenirken sunucuda bir hata oluştu.'}), 500

@admin_bp.route('/api/models/<int:model_id>', methods=['GET'])
def api_get_model(model_id: int) -> Tuple[Any, int]:
    try:
        # Model servisinde API key olmadan getiren bir metot olmalı
        model = model_service.get_model_by_id(model_id, include_api_key=False)
        if not model: # Model Dict veya None dönebilir.
            return jsonify({'success': False, 'message': f'ID: {model_id} olan model bulunamadı.'}), 404
        return jsonify({'success': True, 'model': model}), 200
    except Exception as e:
        current_app.logger.error(f"Model (ID: {model_id}) bilgisi alınırken hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Model bilgisi alınırken bir hata oluştu.'}), 500

@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
def api_delete_model(model_id: int) -> Tuple[Any, int]:
    try:
        model_service.delete_model(model_id)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla silindi.'}), 200
    except ValueError as ve:
        current_app.logger.warning(f"AI Modeli (ID: {model_id}) silinirken hata: {str(ve)}")
        return jsonify({'success': False, 'message': str(ve)}), 404
    except Exception as e:
        current_app.logger.error(f"AI Modeli (ID: {model_id}) silinirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'AI Modeli silinirken sunucuda bir hata oluştu.'}), 500

@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
def api_update_model(model_id: int) -> Tuple[Any, int]:
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Güncelleme verisi boş olamaz.'}), 400

        updated_model: Dict[str, Any] = model_service.update_model_via_dict(model_id, data)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla güncellendi.', 'model': updated_model}), 200
    except ValueError as ve:
        current_app.logger.warning(f"AI Modeli (ID: {model_id}) güncellenirken hata: {str(ve)}. Gelen veri: {request.data.decode(errors='ignore')}")
        status_code = 404 if "bulunamadı" in str(ve).lower() else 400
        return jsonify({'success': False, 'message': str(ve)}), status_code
    except Exception as e:
        current_app.logger.error(f"AI Modeli (ID: {model_id}) güncellenirken beklenmedik hata: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'AI Modeli güncellenirken sunucuda bir hata oluştu.'}), 500

