# app/routes/admin_routes.py

from flask import Blueprint, render_template, request, jsonify, flash
from app.services.admin_dashboard_services import (
    CategoryService, 
    AIModelService,
    UserService,
    DashboardService,
    SettingsService
)
# db_session artık doğrudan route'larda kullanılmayacak, servisler yönetecek.
# from app.models.base import db_session 

admin_bp = Blueprint('admin_bp', __name__, template_folder='../templates', url_prefix='/admin')

# Servislerin örneklerini oluştur
category_service = CategoryService()
model_service = AIModelService()
user_service = UserService()
dashboard_service = DashboardService()
settings_service = SettingsService()

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    try:
        stats = dashboard_service.get_dashboard_stats()
        return render_template('admin_dashboard.html',
                               title="Admin Paneli - Dashboard",
                               current_page="dashboard",
                               page_data=stats)
    except Exception as e:
        # Hata durumunda kullanıcıya bir mesaj gösterilebilir veya loglanabilir.
        flash(f"Dashboard yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html', title="Hata", current_page="dashboard", page_data={})


@admin_bp.route('/users')
def users_page():
    try:
        users_data = user_service.get_all_users_for_display()
        return render_template('admin_dashboard.html',
                               title="Kullanıcı Yönetimi",
                               current_page="users",
                               page_data=users_data)
    except Exception as e:
        flash(f"Kullanıcılar yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html', title="Hata", current_page="users", page_data=[])

@admin_bp.route('/categories')
def categories_page():
    try:
        categories_data = category_service.get_all_categories_for_display()
        return render_template('admin_dashboard.html',
                               title="Kategori Yönetimi",
                               current_page="categories",
                               page_data=categories_data)
    except Exception as e:
        flash(f"Kategoriler yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html', title="Hata", current_page="categories", page_data=[])


@admin_bp.route('/models')
def models_page():
    try:
        models_data = model_service.get_all_models_for_display()
        # AI Modeli ekleme/düzenleme formu için kategorileri de gönderelim
        all_categories = category_service.get_all_categories_for_display() # Sadece id ve name yeterli olabilir
        return render_template('admin_dashboard.html',
                               title="AI Model Yönetimi",
                               current_page="models",
                               page_data={"models": models_data, "categories": all_categories})
    except Exception as e:
        flash(f"AI Modelleri yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html', title="Hata", current_page="models", page_data={"models": [], "categories": []})


@admin_bp.route('/settings')
def settings_page():
    try:
        settings_data = settings_service.get_settings_for_display()
        return render_template('admin_dashboard.html',
                               title="Ayarlar",
                               current_page="settings",
                               page_data=settings_data)
    except Exception as e:
        flash(f"Ayarlar yüklenirken bir hata oluştu: {str(e)}", "danger")
        return render_template('admin_dashboard.html', title="Hata", current_page="settings", page_data={})


# --- API Endpoints ---

@admin_bp.route('/api/categories', methods=['POST'])
def api_add_category():
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'success': False, 'message': 'Kategori adı gerekli.'}), 400
        
        new_category = category_service.add_category(
            name=data['name'],
            description=data.get('description')
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla eklendi.', 'category': new_category}), 201
    except ValueError as ve: # Servis tarafından fırlatılan özel hatalar
        return jsonify({'success': False, 'message': str(ve)}), 409 # Conflict or Bad Request
    except Exception as e:
        # Log error e
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}), 500

@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    try:
        category_service.delete_category(category_id)
        return jsonify({'success': True, 'message': 'Kategori başarıyla silindi.'})
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 404 # Not Found or Conflict
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}), 500

@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
def api_update_category(category_id):
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'success': False, 'message': 'Kategori adı gerekli.'}), 400
        
        updated_category = category_service.update_category(
            category_id=category_id,
            name=data['name'],
            description=data.get('description')
        )
        return jsonify({'success': True, 'message': 'Kategori başarıyla güncellendi.', 'category': updated_category})
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 404 # Not Found or Conflict
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}), 500


@admin_bp.route('/api/models', methods=['POST'])
def api_add_model():
    try:
        data = request.get_json()
        # Gerekli alanların validasyonu (name, category_id vb.)
        if not data or not data.get('name') or data.get('category_id') is None:
            return jsonify({'success': False, 'message': 'Model adı ve kategori ID gerekli.'}), 400
        
        new_model = model_service.add_model(
            name=data['name'],
            category_id=data['category_id'],
            description=data.get('description'),
            api_url=data.get('api_url'),
            status=data.get('status', 'active')
        )
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla eklendi.', 'model': new_model}), 201
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400 # Bad request (örn. kategori yok)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}), 500

@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
def api_delete_model(model_id):
    try:
        model_service.delete_model(model_id)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla silindi.'})
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}), 500

@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
def api_update_model(model_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Güncelleme verisi boş olamaz.'}), 400
        
        updated_model = model_service.update_model(model_id, data)
        return jsonify({'success': True, 'message': 'AI Modeli başarıyla güncellendi.', 'model': updated_model})
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400 # Veya 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}), 500

# Flask uygulamanızda db_session'ın her request sonunda kaldırıldığından emin olun.
# Bu genellikle ana uygulama dosyanızda (örn: app/main.py veya app/__init__.py) şöyle yapılır:
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     from app.models.base import db_session # Import burada yapılmalı
#     db_session.remove()
# Eğer bu yapılandırma zaten varsa, servislerdeki db_session.remove() çağrıları gereksiz olabilir.
# Ancak, her bir servis metodunun kendi işlemini tamamladıktan sonra session'ı kapatması,
# özellikle uzun süren request'lerde veya farklı thread'lerde sorunları önleyebilir.
# Bu projenin yapısına göre en uygun olanı seçilmelidir.
