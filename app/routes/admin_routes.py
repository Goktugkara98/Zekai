# =============================================================================
# Admin Panel Routes Module
# =============================================================================
# Contents:
# 1. Imports
# 2. Authentication Middleware
# 3. View Routes
# 4. Category API Routes
# 5. Model API Routes
# 6. Utility API Routes
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from app.services.admin_panel_service import (
    is_admin_authenticated, get_all_categories, get_category_with_models,
    create_new_category, update_existing_category, delete_existing_category,
    get_all_models, get_model_details, create_new_model,
    update_existing_model, delete_existing_model, get_available_icons
)
from app.models.database import AIModelRepository # Import repository
from functools import wraps
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Create blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -----------------------------------------------------------------------------
# 2. Authentication Middleware
# -----------------------------------------------------------------------------
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            flash('You need to be logged in as an administrator to access this page.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------------------------------------------------------
# 3. View Routes
# -----------------------------------------------------------------------------
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if is_admin_authenticated():
        return redirect(url_for('admin.panel'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Get admin credentials from environment variables or config
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        
        # For development purposes, use hardcoded credentials
        # In production, you should use environment variables for security
        if username == admin_username and password == 'zekaiadmin':
            session['is_admin'] = True
            flash('You have been logged in as administrator.', 'success')
            return redirect(url_for('admin.panel'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_login_required
def panel():
    """Admin panel main page"""
    return render_template('admin_panel.html')

# Kullanıcı Mesajlarını Listeleme Rotası
@admin_bp.route('/messages')
@admin_login_required # Login gerekliliğini ekle
def list_messages():
    try:
        ai_repo = AIModelRepository()
        # Sayfalama için parametreleri al (varsayılan değerlerle)
        page = request.args.get('page', 1, type=int)
        per_page = 25 # Sayfa başına gösterilecek mesaj sayısı (artırıldı)
        offset = (page - 1) * per_page

        messages = ai_repo.get_all_user_messages(limit=per_page, offset=offset)

        # TODO: Toplam mesaj sayısını alıp sayfalama bilgisi eklemek daha iyi olur.

    except Exception as e:
        flash(f'Mesajları getirirken bir hata oluştu: {e}', 'danger')
        messages = []

    # Şablon adının doğru olduğundan emin ol: 'admin/messages.html'
    return render_template('admin/messages.html', title='Kullanıcı Mesajları', messages=messages, current_page=page, per_page=per_page)


# -----------------------------------------------------------------------------
# 4. Category API Routes
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['GET'])
@admin_login_required
def api_get_categories():
    """API endpoint to get all categories"""
    categories = get_all_categories()
    
    # Add model count to each category
    for category in categories:
        if 'models' in category:
            category['model_count'] = len(category['models'])
    
    return jsonify({
        'success': True,
        'categories': categories
    })

@admin_bp.route('/api/categories/count', methods=['GET'])
@admin_login_required
def api_get_category_count():
    """API endpoint to get category count"""
    categories = get_all_categories()
    return jsonify({
        'success': True,
        'count': len(categories)
    })

@admin_bp.route('/api/categories/<int:category_id>', methods=['GET'])
@admin_login_required
def api_get_category(category_id):
    """API endpoint to get a specific category with its models"""
    success, data = get_category_with_models(category_id)
    
    if success:
        return jsonify({
            'success': True,
            'category': data
        })
    else:
        return jsonify({
            'success': False,
            'error': data.get('error', 'Failed to get category')
        }), 404

@admin_bp.route('/api/categories', methods=['POST'])
@admin_login_required
def api_create_category():
    """API endpoint to create a new category"""
    data = request.json
    
    if not data or 'name' not in data or 'icon' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    success, result = create_new_category(data['name'], data['icon'])
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Category created successfully')
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to create category')
        }), 400

@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@admin_login_required
def api_update_category(category_id):
    """API endpoint to update a category"""
    data = request.json
    
    if not data or 'name' not in data or 'icon' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    success, result = update_existing_category(category_id, data['name'], data['icon'])
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Category updated successfully')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to update category')
        }), 400

@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@admin_login_required
def api_delete_category(category_id):
    """API endpoint to delete a category"""
    success, result = delete_existing_category(category_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Category deleted successfully')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to delete category')
        }), 400

# -----------------------------------------------------------------------------
# 5. Model API Routes
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['GET'])
@admin_login_required
def api_get_models():
    """API endpoint to get all models"""
    models = get_all_models()
    return jsonify({
        'success': True,
        'models': models
    })

@admin_bp.route('/api/models/count', methods=['GET'])
@admin_login_required
def api_get_model_count():
    """API endpoint to get model count"""
    models = get_all_models()
    return jsonify({
        'success': True,
        'count': len(models)
    })

@admin_bp.route('/api/models/<int:model_id>', methods=['GET'])
@admin_login_required
def api_get_model(model_id):
    """API endpoint to get a specific model"""
    success, data = get_model_details(model_id)
    
    if success:
        return jsonify({
            'success': True,
            'model': data
        })
    else:
        return jsonify({
            'success': False,
            'error': data.get('error', 'Failed to get model')
        }), 404

@admin_bp.route('/api/models', methods=['POST'])
@admin_login_required
def api_create_model():
    """API endpoint to create a new model"""
    data = request.json
    
    required_fields = ['category_id', 'name', 'icon', 'data_ai_index', 'api_url']
    if not data or not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    # Get optional fields with defaults
    request_method = data.get('request_method', 'POST')
    request_headers = data.get('request_headers')
    request_body_template = data.get('request_body_template')
    response_path = data.get('response_path')
    
    success, result = create_new_model(
        data['category_id'], 
        data['name'], 
        data['icon'], 
        data['data_ai_index'], 
        data['api_url'],
        request_method,
        request_headers,
        request_body_template,
        response_path
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Model created successfully')
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to create model')
        }), 400

@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
@admin_login_required
def api_update_model(model_id):
    """API endpoint to update a model"""
    data = request.json
    
    required_fields = ['category_id', 'name', 'icon', 'data_ai_index', 'api_url']
    if not data or not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    # Get optional fields with defaults
    request_method = data.get('request_method', 'POST')
    request_headers = data.get('request_headers')
    request_body_template = data.get('request_body_template')
    response_path = data.get('response_path')
    
    success, result = update_existing_model(
        model_id,
        data['category_id'], 
        data['name'], 
        data['icon'], 
        data['data_ai_index'], 
        data['api_url'],
        request_method,
        request_headers,
        request_body_template,
        response_path
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Model updated successfully')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to update model')
        }), 400

@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
@admin_login_required
def api_delete_model(model_id):
    """API endpoint to delete a model"""
    success, result = delete_existing_model(model_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Model deleted successfully')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to delete model')
        }), 400

# -----------------------------------------------------------------------------
# 6. Utility API Routes
# -----------------------------------------------------------------------------
@admin_bp.route('/api/icons', methods=['GET'])
@admin_login_required
def api_get_icons():
    """API endpoint to get available icons"""
    icons = get_available_icons()
    return jsonify({
        'success': True,
        'icons': icons
    })

@admin_bp.route('/api/admin/logout', methods=['POST'])
def api_logout():
    """API endpoint for AJAX logout"""
    session.pop('is_admin', None)
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })
