# =============================================================================
# ADMIN PAGES (Pages)
# =============================================================================
# Admin paneli sayfa rotaları (HTML render)
# =============================================================================

from flask import Blueprint, render_template
from app.routes.auth_decorators import admin_required
from app.services.user_service import UserService
from app.services.model_service import ModelService
from app.services.category_service import CategoryService
from app.services.branding_service import BrandingService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

user_service = UserService()
model_service = ModelService()
category_service = CategoryService()


@admin_bp.route('/')
@admin_required
def dashboard():
    try:
        users = user_service.list_users()
        models = model_service.get_all_models()
        user_count = users.get('count', 0) if users.get('success') else 0
        model_count = models.get('count', 0) if models.get('success') else 0
        # Ek metrikler
        admin_count = 0
        active_model_count = 0
        recent_users = []
        provider_by_type = {}
        provider_by_name = {}
        try:
            if users.get('success'):
                data_users = users.get('data') or []
                admin_count = sum(1 for u in data_users if u.get('is_admin'))
                # Son girişe göre ilk 5 kullanıcı (varsa), yoksa created_at'a göre
                def user_sort_key(u):
                    return u.get('last_login') or u.get('created_at') or ''
                recent_users = sorted(data_users, key=user_sort_key, reverse=True)[:5]
        except Exception:
            admin_count = 0
        try:
            if models.get('success'):
                data_models = models.get('data') or []
                active_model_count = sum(1 for m in data_models if m.get('is_active'))
                # Sağlayıcı istatistikleri
                for m in data_models:
                    pt = (m.get('provider_type') or 'other').lower()
                    pn = (m.get('provider_name') or 'other').lower()
                    provider_by_type[pt] = provider_by_type.get(pt, 0) + 1
                    provider_by_name[pn] = provider_by_name.get(pn, 0) + 1
        except Exception:
            active_model_count = 0

        return render_template(
            'admin/dashboard.html',
            user_count=user_count,
            model_count=model_count,
            admin_count=admin_count,
            active_model_count=active_model_count,
            recent_users=recent_users,
            provider_by_type=provider_by_type,
            provider_by_name=provider_by_name,
        )
    except Exception as e:
        return "Admin paneli yüklenirken hata oluştu", 500


@admin_bp.route('/users')
@admin_required
def users_page():
    try:
        result = user_service.list_users()
        users = result.get('data', []) if result.get('success') else []
        return render_template('admin/users.html', users=users)
    except Exception as e:
        return "Kullanıcı listesi yüklenirken hata oluştu", 500


@admin_bp.route('/models')
@admin_required
def models_page():
    try:
        result = model_service.get_all_models()
        models = result.get('data', []) if result.get('success') else []
        cats_result = category_service.get_all_categories()
        categories = cats_result.get('data', []) if cats_result.get('success') else []
        return render_template('admin/models.html', models=models, categories=categories)
    except Exception as e:
        return "Model listesi yüklenirken hata oluştu", 500


@admin_bp.route('/categories')
@admin_required
def categories_page():
    try:
        result = category_service.get_all_categories()
        categories = result.get('data', []) if result.get('success') else []
        return render_template('admin/categories.html', categories=categories)
    except Exception as e:
        return "Kategori listesi yüklenirken hata oluştu", 500


@admin_bp.route('/branding')
@admin_required
def branding_page():
    try:
        settings = BrandingService.get_settings()
        return render_template('admin/branding.html', branding=settings)
    except Exception:
        return "Branding sayfası yüklenirken hata oluştu", 500
