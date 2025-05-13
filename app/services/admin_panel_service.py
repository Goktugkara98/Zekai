# =============================================================================
# Admin Panel Service Module
# =============================================================================
# İçindekiler:
# 1. Imports
# 2. Kimlik Doğrulama Servisleri
#    2.1. Admin Kimlik Doğrulama
#    2.2. Yetkilendirme Decorator
# 3. Kategori Yönetimi Servisleri
#    3.1. Kategori Listeleme
#    3.2. Kategori Detayları
#    3.3. Kategori Oluşturma
#    3.4. Kategori Güncelleme
#    3.5. Kategori Silme
# 4. Model Yönetimi Servisleri
#    4.1. Model Listeleme
#    4.2. Model Detayları
#    4.3. Model Oluşturma
#    4.4. Model Güncelleme
#    4.5. Model Silme
# 5. Yardımcı Fonksiyonlar
#    5.1. İkon Yönetimi
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from app.models.admin_panel_database import AdminRepository
from typing import Dict, List, Optional, Any, Tuple
from flask import session

# -----------------------------------------------------------------------------
# 2. Kimlik Doğrulama Servisleri
# -----------------------------------------------------------------------------
# 2.1. Admin Kimlik Doğrulama
def is_admin_authenticated() -> bool:
    """Admin kimlik doğrulamasını kontrol eder."""
    return session.get('is_admin', False)

# 2.2. Yetkilendirme Decorator
def require_admin_auth(func):
    """Admin kimlik doğrulaması gerektiren fonksiyonlar için decorator."""
    def wrapper(*args, **kwargs):
        if not is_admin_authenticated():
            return False, "Admin authentication required"
        return func(*args, **kwargs)
    return wrapper

# -----------------------------------------------------------------------------
# 3. Kategori Yönetimi Servisleri
# -----------------------------------------------------------------------------
# 3.1. Kategori Listeleme
@require_admin_auth
def get_all_categories() -> List[Dict[str, Any]]:
    """Tüm AI kategorilerini getirir."""
    try:
        admin_repo = AdminRepository()
        categories = admin_repo.ai_repo.get_all_ai_categories()
        return categories
    except Exception:
        return []

@require_admin_auth
# 3.2. Kategori Detayları
def get_category_with_models(category_id: int) -> Tuple[bool, Dict[str, Any]]:
    """Bir kategoriyi ve tüm modellerini getirir."""
    try:
        admin_repo = AdminRepository()
        category = admin_repo.get_category_details(category_id)
        
        if not category:
            return False, {"error": f"Category with ID {category_id} not found"}
            
        return True, category
    except Exception as e:
        return False, {"error": f"Error fetching category details: {str(e)}"}

@require_admin_auth
# 3.3. Kategori Oluşturma
def create_new_category(name: str, icon: str) -> Tuple[bool, Dict[str, Any]]:
    """Yeni bir AI kategorisi oluşturur."""
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.create_category(name, icon)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        return False, {"error": f"Error creating category: {str(e)}"}

@require_admin_auth
# 3.4. Kategori Güncelleme
def update_existing_category(category_id: int, name: str, icon: str) -> Tuple[bool, Dict[str, Any]]:
    """Var olan bir AI kategorisini günceller."""
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.update_category(category_id, name, icon)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        return False, {"error": f"Error updating category: {str(e)}"}

@require_admin_auth
# 3.5. Kategori Silme
def delete_existing_category(category_id: int) -> Tuple[bool, Dict[str, Any]]:
    """Bir AI kategorisini ve ilişkili tüm modellerini siler."""
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.delete_category(category_id)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        return False, {"error": f"Error deleting category: {str(e)}"}

# -----------------------------------------------------------------------------
# 4. Model Yönetimi Servisleri
# -----------------------------------------------------------------------------
# 4.1. Model Listeleme
@require_admin_auth
def get_all_models() -> List[Dict[str, Any]]:
    """Tüm AI modellerini getirir."""
    try:
        admin_repo = AdminRepository()
        models = admin_repo.ai_repo.get_all_ai_models()
        return models
    except Exception:
        return []

@require_admin_auth
# 4.2. Model Detayları
def get_model_details(model_id: int) -> Tuple[bool, Dict[str, Any]]:
    """Bir model hakkında detaylı bilgi getirir."""
    try:
        admin_repo = AdminRepository()
        model = admin_repo.get_model_details(model_id)
        
        if not model:
            return False, {"error": f"Model with ID {model_id} not found"}
            
        return True, model
    except Exception as e:
        return False, {"error": f"Error fetching model details: {str(e)}"}

@require_admin_auth
# 4.3. Model Oluşturma
def create_new_model(category_id: int, name: str, icon: str, 
                    data_ai_index: str, api_url: str, request_method: str = 'POST',
                    request_headers: str = None, request_body_template: str = None,
                    response_path: str = None) -> Tuple[bool, Dict[str, Any]]:
    """Yeni bir AI modeli oluşturur."""
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
        return False, {"error": f"Error creating model: {str(e)}"}

@require_admin_auth
# 4.4. Model Güncelleme
def update_existing_model(model_id: int, category_id: int, name: str, 
                         icon: str, data_ai_index: str, api_url: str,
                         request_method: str = 'POST', request_headers: str = None,
                         request_body_template: str = None, response_path: str = None) -> Tuple[bool, Dict[str, Any]]:
    """Var olan bir AI modelini günceller."""
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
        return False, {"error": f"Error updating model: {str(e)}"}

@require_admin_auth
# 4.5. Model Silme
def delete_existing_model(model_id: int) -> Tuple[bool, Dict[str, Any]]:
    """Bir AI modelini siler."""
    try:
        admin_repo = AdminRepository()
        success, message = admin_repo.delete_model(model_id)
        
        if not success:
            return False, {"error": message}
            
        return True, {"message": message}
    except Exception as e:
        return False, {"error": f"Error deleting model: {str(e)}"}

# -----------------------------------------------------------------------------
# 5. Yardımcı Fonksiyonlar
# -----------------------------------------------------------------------------
# 5.1. İkon Yönetimi
def get_available_icons() -> List[Dict[str, str]]:
    """Admin paneli için kullanılabilir Bootstrap ikonlarını getirir."""
    return [
        {"class": "bi-robot", "name": "Robot"},
        {"class": "bi-cpu", "name": "CPU"},
        {"class": "bi-chat-dots", "name": "Chat"},
        {"class": "bi-lightning", "name": "Lightning"},
        {"class": "bi-stars", "name": "Stars"},
        {"class": "bi-magic", "name": "Magic"},
        {"class": "bi-gear", "name": "Gear"},
        {"class": "bi-code", "name": "Code"},
        {"class": "bi-file-text", "name": "Document"},
        {"class": "bi-search", "name": "Search"},
        {"class": "bi-translate", "name": "Translate"},
        {"class": "bi-magic", "name": "Magic"},
        {"class": "bi-lightning", "name": "Lightning"},
        {"class": "bi-star", "name": "Star"},
        {"class": "bi-folder", "name": "Folder"}
    ]
