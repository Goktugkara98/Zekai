# =============================================================================
# Admin Panel Service Module
# =============================================================================
# Contents:
# 1. Imports
# 2. Authentication Services
# 3. Category Management Services
# 4. Model Management Services
# 5. Utility Functions
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from app.models.admin_panel_database import AdminRepository
from typing import Dict, List, Optional, Any, Tuple
from flask import session

# -----------------------------------------------------------------------------
# 2. Authentication Services
# -----------------------------------------------------------------------------
def is_admin_authenticated() -> bool:
    """
    Checks if the current user is authenticated as an admin.
    
    Returns:
        True if authenticated as admin, False otherwise
    """
    return session.get('is_admin', False)

def require_admin_auth(func):
    """
    Decorator to require admin authentication for a function.
    
    Args:
        func: The function to decorate
        
    Returns:
        Wrapped function that checks admin authentication
    """
    def wrapper(*args, **kwargs):
        if not is_admin_authenticated():
            return False, "Admin authentication required"
        return func(*args, **kwargs)
    return wrapper

# -----------------------------------------------------------------------------
# 3. Category Management Services
# -----------------------------------------------------------------------------
@require_admin_auth
def get_all_categories() -> List[Dict[str, Any]]:
    """
    Retrieves all AI categories.
    
    Returns:
        List of category dictionaries
    """
    try:
        admin_repo = AdminRepository()
        categories = admin_repo.ai_repo.get_all_ai_categories()
        return categories
    except Exception as e:
        print(f"Service Layer: Error fetching all categories: {e}")
        return []

@require_admin_auth
def get_category_with_models(category_id: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Retrieves a category with all its models.
    
    Args:
        category_id: The ID of the category
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        category = admin_repo.get_category_details(category_id)
        
        if not category:
            return False, {"error": f"Category with ID {category_id} not found"}
            
        return True, category
    except Exception as e:
        print(f"Service Layer: Error fetching category details: {e}")
        return False, {"error": f"Error fetching category details: {str(e)}"}

@require_admin_auth
def create_new_category(name: str, icon: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Creates a new AI category.
    
    Args:
        name: The name of the category
        icon: The icon identifier for the category
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.create_category(name, icon)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        print(f"Service Layer: Error creating category: {e}")
        return False, {"error": f"Error creating category: {str(e)}"}

@require_admin_auth
def update_existing_category(category_id: int, name: str, icon: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Updates an existing AI category.
    
    Args:
        category_id: The ID of the category to update
        name: The new name of the category
        icon: The new icon identifier for the category
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.update_category(category_id, name, icon)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        print(f"Service Layer: Error updating category: {e}")
        return False, {"error": f"Error updating category: {str(e)}"}

@require_admin_auth
def delete_existing_category(category_id: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Deletes an AI category and all associated models.
    
    Args:
        category_id: The ID of the category to delete
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.delete_category(category_id)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        print(f"Service Layer: Error deleting category: {e}")
        return False, {"error": f"Error deleting category: {str(e)}"}

# -----------------------------------------------------------------------------
# 4. Model Management Services
# -----------------------------------------------------------------------------
@require_admin_auth
def get_all_models() -> List[Dict[str, Any]]:
    """
    Retrieves all AI models.
    
    Returns:
        List of model dictionaries
    """
    try:
        admin_repo = AdminRepository()
        models = admin_repo.ai_repo.get_all_ai_models()
        return models
    except Exception as e:
        print(f"Service Layer: Error fetching all models: {e}")
        return []

@require_admin_auth
def get_model_details(model_id: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Retrieves detailed information about a model.
    
    Args:
        model_id: The ID of the model
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        model = admin_repo.get_model_details(model_id)
        
        if not model:
            return False, {"error": f"Model with ID {model_id} not found"}
            
        return True, model
    except Exception as e:
        print(f"Service Layer: Error fetching model details: {e}")
        return False, {"error": f"Error fetching model details: {str(e)}"}

@require_admin_auth
def create_new_model(category_id: int, name: str, icon: str, 
                    data_ai_index: str, api_url: str, request_method: str = 'POST',
                    request_headers: str = None, request_body_template: str = None,
                    response_path: str = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Creates a new AI model.
    
    Args:
        category_id: The ID of the category for this model
        name: The name of the model
        icon: The icon identifier for the model
        data_ai_index: The unique data-ai-index value
        api_url: The API URL for the model
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.create_model(
            category_id, name, icon, data_ai_index, api_url,
            request_method, request_headers, request_body_template, response_path
        )
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        print(f"Service Layer: Error creating model: {e}")
        return False, {"error": f"Error creating model: {str(e)}"}

@require_admin_auth
def update_existing_model(model_id: int, category_id: int, name: str, 
                         icon: str, data_ai_index: str, api_url: str,
                         request_method: str = 'POST', request_headers: str = None,
                         request_body_template: str = None, response_path: str = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Updates an existing AI model.
    
    Args:
        model_id: The ID of the model to update
        category_id: The ID of the category for this model
        name: The name of the model
        icon: The icon identifier for the model
        data_ai_index: The unique data-ai-index value
        api_url: The API URL for the model
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.update_model(
            model_id, category_id, name, icon, data_ai_index, api_url,
            request_method, request_headers, request_body_template, response_path
        )
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        print(f"Service Layer: Error updating model: {e}")
        return False, {"error": f"Error updating model: {str(e)}"}

@require_admin_auth
def delete_existing_model(model_id: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Deletes an AI model.
    
    Args:
        model_id: The ID of the model to delete
        
    Returns:
        Tuple of (success, data)
    """
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.delete_model(model_id)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        print(f"Service Layer: Error deleting model: {e}")
        return False, {"error": f"Error deleting model: {str(e)}"}

# -----------------------------------------------------------------------------
# 5. Utility Functions
# -----------------------------------------------------------------------------
def get_available_icons() -> List[Dict[str, str]]:
    """
    Returns a list of available Bootstrap icons for use in the admin panel.
    
    Returns:
        List of icon dictionaries with name and class
    """
    # Common Bootstrap icons that might be useful for AI categories/models
    return [
        {"name": "Robot", "class": "bi-robot"},
        {"name": "Gem", "class": "bi-gem"},
        {"name": "CPU", "class": "bi-cpu"},
        {"name": "Brain", "class": "bi-brain"},
        {"name": "Chat", "class": "bi-chat-dots"},
        {"name": "Code", "class": "bi-code-square"},
        {"name": "Image", "class": "bi-image"},
        {"name": "Music", "class": "bi-music-note"},
        {"name": "Video", "class": "bi-camera-video"},
        {"name": "Document", "class": "bi-file-text"},
        {"name": "Search", "class": "bi-search"},
        {"name": "Translate", "class": "bi-translate"},
        {"name": "Magic", "class": "bi-magic"},
        {"name": "Lightning", "class": "bi-lightning"},
        {"name": "Star", "class": "bi-star"},
        {"name": "Folder", "class": "bi-folder"}
    ]
