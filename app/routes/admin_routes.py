# =============================================================================
# Admin Panel Routes Module
# =============================================================================
# Contents:
# 1. Imports
# 2. Blueprint Definition
# 3. Authentication
#    3.1. admin_login_required (Decorator)
# 4. View Routes (HTML Rendering)
#    4.1. /login (GET, POST) - Admin Login Page
#    4.2. /logout (GET) - Admin Logout
#    4.3. / (GET) - Admin Panel Main Page (Dashboard)
#    4.4. /messages (GET) - List User Messages
# 5. Category API Routes (JSON)
#    5.1. GET /api/categories - Get All Categories
#    5.2. GET /api/categories/count - Get Category Count
#    5.3. GET /api/categories/<int:category_id> - Get Specific Category
#    5.4. POST /api/categories - Create New Category
#    5.5. PUT /api/categories/<int:category_id> - Update Category
# 6. Model API Routes (JSON)
#    (Further routes to be defined based on full file content)
# 7. Utility API Routes (JSON)
#    (Further routes to be defined based on full file content, e.g., for icons)
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
import os
from werkzeug.security import check_password_hash, generate_password_hash

from app.services.admin_panel_service import (
    is_admin_authenticated, get_all_categories, get_category_with_models,
    create_new_category, update_existing_category, delete_existing_category, # delete_existing_category might be used later
    get_all_models, get_model_details, create_new_model,
    update_existing_model, delete_existing_model, get_available_icons # These services suggest more routes exist
)
from app.models.database import AIModelRepository # Used for /messages route

# -----------------------------------------------------------------------------
# 2. Blueprint Definition
# -----------------------------------------------------------------------------
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -----------------------------------------------------------------------------
# 3. Authentication
# -----------------------------------------------------------------------------

# 3.1. admin_login_required (Decorator)
# -----------------------------------------------------------------------------
def admin_login_required(f):
    """
    Decorator to ensure that the admin is logged in.
    Redirects to the login page if the admin is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            flash('You need to be logged in as an administrator to access this page.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------------------------------------------------------
# 4. View Routes (HTML Rendering)
# -----------------------------------------------------------------------------

# 4.1. /login (GET, POST) - Admin Login Page
# -----------------------------------------------------------------------------
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if is_admin_authenticated():
        return redirect(url_for('admin.panel')) # Redirect if already logged in
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Admin credentials
        # In a production environment, ensure ADMIN_USERNAME and especially a hashed password
        # are securely managed (e.g., via environment variables or a secure config).
        # Avoid hardcoding passwords directly in the code.
        admin_username_env = os.environ.get('ADMIN_USERNAME', 'admin')
        # IMPORTANT: The password 'zekaiadmin' is hardcoded here for development.
        # This is a security risk in production. Use hashed passwords and secure storage.
        admin_password_hardcoded = 'zekaiadmin' 

        if username == admin_username_env and password == admin_password_hardcoded: # Replace with password_hash check in production
            session['is_admin'] = True
            flash('You have been logged in as administrator.', 'success')
            return redirect(url_for('admin.panel'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin_login.html', title='Admin Login')

# 4.2. /logout (GET) - Admin Logout
# -----------------------------------------------------------------------------
@admin_bp.route('/logout')
@admin_login_required
def logout():
    """Admin logout."""
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

# 4.3. / (GET) - Admin Panel Main Page (Dashboard)
# -----------------------------------------------------------------------------
@admin_bp.route('/')
@admin_login_required
def panel():
    """Admin panel main page (Dashboard)."""
    # Logic for the main admin panel page can be added here.
    # For now, it just renders a template.
    return render_template('admin_panel.html', title='Admin Panel')

# 4.4. /messages (GET) - List User Messages
# -----------------------------------------------------------------------------
@admin_bp.route('/messages')
@admin_login_required # Ensures only logged-in admins can access
def list_messages():
    """Displays a paginated list of user messages."""
    try:
        # Note: AIModelRepository is used directly here.
        # Consider moving this logic to admin_panel_service for consistency.
        ai_repo = AIModelRepository()
        
        # Get pagination parameters (with default values)
        page = request.args.get('page', 1, type=int)
        per_page = 25 # Number of messages to display per page
        offset = (page - 1) * per_page

        messages = ai_repo.get_all_user_messages(limit=per_page, offset=offset)

        # TODO: Implement total message count for better pagination (e.g., showing total pages).
        # total_messages = ai_repo.get_user_messages_count() 
        # total_pages = (total_messages + per_page - 1) // per_page

    except Exception as e:
        flash(f'An error occurred while fetching messages: {str(e)}', 'danger')
        messages = []
        # Log: f"Error fetching messages for admin panel: {e}"

    # Ensure the template name 'admin/messages.html' is correct.
    return render_template('admin/messages.html', 
                           title='User Messages', 
                           messages=messages, 
                           current_page=page, 
                           per_page=per_page) # Pass per_page for pagination controls in template

# -----------------------------------------------------------------------------
# 5. Category API Routes (JSON)
# -----------------------------------------------------------------------------

# 5.1. GET /api/categories - Get All Categories
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['GET'])
@admin_login_required
def api_get_categories():
    """API endpoint to get all categories, including a count of models in each."""
    categories_data = get_all_categories() # Assuming this service function returns a list of dicts
    
    # The service should ideally return model_count directly if it's a common need.
    # If get_all_categories already includes models, this loop might be simplified or moved to the service.
    for category in categories_data:
        if 'models' in category and isinstance(category['models'], list):
            category['model_count'] = len(category['models'])
        else:
            category['model_count'] = 0 # Default if no models key or not a list
    
    return jsonify({
        'success': True,
        'categories': categories_data
    })

# 5.2. GET /api/categories/count - Get Category Count
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/count', methods=['GET'])
@admin_login_required
def api_get_category_count():
    """API endpoint to get the total number of categories."""
    categories_data = get_all_categories() 
    return jsonify({
        'success': True,
        'count': len(categories_data)
    })

# 5.3. GET /api/categories/<int:category_id> - Get Specific Category
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['GET'])
@admin_login_required
def api_get_category(category_id: int):
    """API endpoint to get a specific category with its associated models."""
    success, data = get_category_with_models(category_id)
    
    if success:
        return jsonify({
            'success': True,
            'category': data # 'data' here is expected to be the category dictionary
        })
    else:
        return jsonify({
            'success': False,
            'error': data.get('error', 'Failed to get category details.') # Provide a default error message
        }), 404 # Not Found

# 5.4. POST /api/categories - Create New Category
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['POST'])
@admin_login_required
def api_create_category():
    """API endpoint to create a new category."""
    data = request.json
    
    if not data or 'name' not in data or not data['name'].strip(): # Added strip to check for empty names
        return jsonify({
            'success': False,
            'error': 'Missing or invalid required fields: name is required.'
        }), 400 # Bad Request
    
    # Icon can be optional or have a default in the service
    category_name = data['name'].strip()
    category_icon = data.get('icon', '') # Use .get for optional fields

    success, result = create_new_category(category_name, category_icon)
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Category created successfully.'),
            'category_id': result.get('id') # Return the new category ID
        }), 201 # Created
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to create category.')
        }), 400 # Bad Request (or 409 Conflict if name exists, 500 for server error)

# 5.5. PUT /api/categories/<int:category_id> - Update Category
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@admin_login_required
def api_update_category(category_id: int):
    """API endpoint to update an existing category."""
    data = request.json
    
    if not data or 'name' not in data or not data['name'].strip():
        return jsonify({
            'success': False,
            'error': 'Missing or invalid required fields: name is required.'
        }), 400 # Bad Request
        
    category_name = data['name'].strip()
    category_icon = data.get('icon', '') # Icon can be optional

    success, result = update_existing_category(category_id, category_name, category_icon)
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Category updated successfully.')
        }) # Default 200 OK
    else:
        # Distinguish between 404 Not Found and 400 Bad Request/500 Server Error
        error_message = result.get('error', 'Failed to update category.')
        status_code = 400
        if "not found" in error_message.lower():
            status_code = 404
        return jsonify({
            'success': False,
            'error': error_message
        }), status_code

@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@admin_login_required
def api_delete_category(category_id: int):
    """API endpoint to delete a category."""
    success, result = delete_existing_category(category_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Category deleted successfully.')
        }) # Default 200 OK
    else:
        error_message = result.get('error', 'Failed to delete category.')
        status_code = 400
        if "not found" in error_message.lower():
            status_code = 404
        return jsonify({
            'success': False,
            'error': error_message
        }), status_code

# -----------------------------------------------------------------------------
# 6. Model API Routes (JSON)
# -----------------------------------------------------------------------------

# 6.1. GET /api/models - Get All Models
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['GET'])
@admin_login_required
def api_get_models():
    """API endpoint to get all models."""
    models = get_all_models() # This service likely returns a list of model dicts
    return jsonify({
        'success': True,
        'models': models
    })

# 6.2. GET /api/models/count - Get Model Count
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/count', methods=['GET'])
@admin_login_required
def api_get_model_count():
    """API endpoint to get the total number of models."""
    models = get_all_models()
    return jsonify({
        'success': True,
        'count': len(models)
    })

# 6.3. GET /api/models/<int:model_id> - Get Specific Model
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['GET'])
@admin_login_required
def api_get_model(model_id: int):
    """API endpoint to get a specific model by its ID."""
    success, data = get_model_details(model_id)
    
    if success:
        return jsonify({
            'success': True,
            'model': data # 'data' here is the model dictionary
        })
    else:
        return jsonify({
            'success': False,
            'error': data.get('error', 'Failed to get model details.')
        }), 404 # Not Found

# 6.4. POST /api/models - Create New Model
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['POST'])
@admin_login_required
def api_create_model():
    """API endpoint to create a new model."""
    data = request.json
    
    # Basic validation for required fields
    required_fields = ['name', 'category_id', 'api_url', 'description', 'details']
    if not data or not all(field in data and data[field] for field in required_fields):
        missing_or_empty = [field for field in required_fields if not data or field not in data or not data[field]]
        return jsonify({
            'success': False,
            'error': f'Missing or empty required fields: {", ".join(missing_or_empty)}.'
        }), 400 # Bad Request

    model_name = data['name'].strip()
    category_id = data['category_id'] # Should be validated as int by the service or here
    api_url = data['api_url'].strip()
    description = data['description'].strip()
    details = data['details'] # Can be complex, service should handle its structure
    
    # Optional fields
    icon = data.get('icon', '') # Default to empty string if not provided
    image_filename = data.get('image_filename', '')

    success, result = create_new_model(
        name=model_name,
        category_id=category_id,
        api_url=api_url,
        description=description,
        details=details,
        icon=icon,
        image_filename=image_filename
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Model created successfully.'),
            'model_id': result.get('id') # Return the new model ID
        }), 201 # Created
    else:
        error_message = result.get('error', 'Failed to create model.')
        status_code = 400 # Default bad request
        if "already exists" in error_message.lower():
            status_code = 409 # Conflict
        elif "category not found" in error_message.lower():
            status_code = 400 # Or 404 if category_id is the only issue
        return jsonify({
            'success': False,
            'error': error_message
        }), status_code

# 6.5. PUT /api/models/<int:model_id> - Update Model
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
@admin_login_required
def api_update_model(model_id: int):
    """API endpoint to update an existing model."""
    data = request.json
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body cannot be empty.'
        }), 400

    # Fields that can be updated (all are optional in PUT, but at least one should be present)
    # Service layer should handle partial updates correctly.
    name = data.get('name', '').strip() if data.get('name') else None
    category_id = data.get('category_id')
    api_url = data.get('api_url', '').strip() if data.get('api_url') else None
    description = data.get('description', '').strip() if data.get('description') else None
    details = data.get('details')
    icon = data.get('icon', '').strip() if data.get('icon') else None
    image_filename = data.get('image_filename', '').strip() if data.get('image_filename') else None

    # Check if any data was actually provided for update
    if all(val is None for val in [name, category_id, api_url, description, details, icon, image_filename]):
        return jsonify({
            'success': False,
            'error': 'No fields provided for update.'
        }), 400

    success, result = update_existing_model(
        model_id=model_id,
        name=name,
        category_id=category_id,
        api_url=api_url,
        description=description,
        details=details,
        icon=icon,
        image_filename=image_filename
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': result.get('message', 'Model updated successfully.')
        }) # Default 200 OK
    else:
        error_message = result.get('error', 'Failed to update model.')
        status_code = 400
        if "not found" in error_message.lower():
            status_code = 404
        elif "category not found" in error_message.lower():
            status_code = 400
        return jsonify({
            'success': False,
            'error': error_message
        }), status_code

# 6.6. DELETE /api/models/<int:model_id> - Delete Model
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
@admin_login_required
def api_delete_model(model_id: int):
    """API endpoint to delete a model."""
    success, data = delete_existing_model(model_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': data.get('message', 'Model deleted successfully')
        })
    else:
        return jsonify({
            'success': False,
            'error': data.get('error', 'Failed to delete model')
        }), 400 # Bad Request

# 6.7. POST /api/models/<int:model_id>/duplicate - Duplicate Model
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>/duplicate', methods=['POST'])
@admin_login_required
def api_duplicate_model(model_id: int):
    """API endpoint to duplicate a model."""
    admin_repo = AdminRepository()
    success, message, new_model_id = admin_repo.model_repo.duplicate_model(model_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'id': new_model_id
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

# -----------------------------------------------------------------------------
# 7. Utility API Routes (JSON)
# -----------------------------------------------------------------------------

# 7.1. GET /api/icons - Get Available Icons
# -----------------------------------------------------------------------------
@admin_bp.route('/api/icons', methods=['GET'])
@admin_login_required
def api_get_icons():
    """API endpoint to get a list of available icons."""
    success, data = get_available_icons()
    
    if success:
        return jsonify({
            'success': True,
            'icons': data['icons']
        })
    else:
        return jsonify({
            'success': False,
            'error': data.get('error', 'Failed to retrieve icon list.')
        }), 500

# 7.2. POST /api/logout - AJAX Logout (Alternative to view logout)
# -----------------------------------------------------------------------------
@admin_bp.route('/api/logout', methods=['POST']) # Changed to POST as it changes state
@admin_login_required
def api_logout():
    """API endpoint for AJAX logout."""
    session.pop('is_admin', None)
    return jsonify({
        'success': True,
        'message': 'You have been successfully logged out.'
    })
