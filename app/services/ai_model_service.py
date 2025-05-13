# =============================================================================
# AI Model Service Module
# =============================================================================
# İçindekiler:
# 1. Imports
# 2. AI Model Yönetimi
#    2.1. Model Detayları Getirme
#    2.2. Kategori ve Model Listeleme
# 3. Yardımcı Fonksiyonlar
#    3.1. Model Ekleme
#    3.2. Tüm Modelleri Getirme
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from app.models.database import AIModelRepository
from typing import Dict, List, Optional, Any

# -----------------------------------------------------------------------------
# 2. AI Model Yönetimi
# -----------------------------------------------------------------------------
# 2.1. Model Detayları Getirme
def get_ai_model_api_details(data_ai_index: str) -> Optional[Dict[str, Any]]:
    """Belirli bir AI modelinin API detaylarını data_ai_index ile getirir."""
    try:
        ai_repo = AIModelRepository()
        model = ai_repo.get_ai_model_by_data_ai_index(data_ai_index)
        
        if not model:
            return None
            
        # Format the response to match the expected structure
        model_details = {
            "name": model["name"],
            "api_url": model["api_url"],
            "data_ai_index": model["data_ai_index"],
            "request_method": model["request_method"],
            "request_headers": model["request_headers"],
            "request_body_template": model["request_body_template"],
            "response_path": model["response_path"]
        }
        
        return model_details
        
    except Exception:
        return None

# 2.2. Kategori ve Model Listeleme
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """Tüm AI kategorilerini ve ilişkili modellerini getirir."""
    try:
        ai_repo = AIModelRepository()
        categories = ai_repo.get_all_ai_categories()
        categories_data = []
        
        for category in categories:
            category_dict = {
                "name": category["name"],
                "icon": category["icon"],
                "models": []
            }
            
            # Fetch models for the current category
            models = ai_repo.get_ai_models_by_category_id(category["id"])
            
            for model in models:
                # Make sure to properly escape any quotes in the API URL to prevent JSON parsing errors
                api_url = model["api_url"]
                if api_url and '"' in api_url:
                    api_url = api_url.replace('"', '\\"')  # Escape double quotes for JSON
                
                category_dict["models"].append({
                    "name": model["name"],
                    "icon": model["icon"],
                    "data_ai_index": model["data_ai_index"],
                    "api_url": api_url
                })
                
            categories_data.append(category_dict)
            
        return categories_data
        
    except Exception:
        return []

# -----------------------------------------------------------------------------
# 3. Yardımcı Fonksiyonlar
# -----------------------------------------------------------------------------
# 3.1. Model Ekleme
def add_ai_model(category_name: str, model_name: str, model_icon: str, 
               data_ai_index: str, api_url: str) -> bool:
    """Veritabanına yeni bir AI modeli ekler."""
    try:
        ai_repo = AIModelRepository()
        
        # Get the category
        category = ai_repo.get_ai_category_by_name(category_name)
        if not category:
            # Create the category if it doesn't exist
            ai_repo.insert_ai_category(category_name, "bi-folder")
            category = ai_repo.get_ai_category_by_name(category_name)
            if not category:
                return False
        
        # Add the model
        result = ai_repo.insert_ai_model(
            category["id"], model_name, model_icon, data_ai_index, api_url
        )
        return result
        
    except Exception:
        return False

# 3.2. Tüm Modelleri Getirme
def get_all_available_models() -> List[Dict[str, Any]]:
    """Tüm mevcut AI modellerini düz bir liste formatında getirir."""
    try:
        ai_repo = AIModelRepository()
        models = ai_repo.get_all_ai_models()
        
        result = []
        for model in models:
            result.append({
                "name": model["name"],
                "icon": model["icon"],
                "data_ai_index": model["data_ai_index"],
                "api_url": model["api_url"]
            })
            
        return result
        
    except Exception:
        return []
