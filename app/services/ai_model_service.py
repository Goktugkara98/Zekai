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
from app.repositories.model_repository import ModelRepository
from app.repositories.category_repository import CategoryRepository
from typing import Dict, List, Optional, Any

# -----------------------------------------------------------------------------
# 2. AI Model Yönetimi
# -----------------------------------------------------------------------------
# 2.1. Model Detayları Getirme
def get_ai_model_api_details(model_identifier: str) -> Optional[Dict[str, Any]]:
    """Belirli bir AI modelinin API detaylarını model_id veya data_ai_index ile getirir.
    
    Args:
        model_identifier (str): Model ID'si veya data_ai_index değeri
        
    Returns:
        Optional[Dict[str, Any]]: Model detayları veya bulunamazsa None
    """
    try:
        ai_repo = ModelRepository()
        model = None
        
        # Önce model_id olarak dene
        try:
            model_id = int(model_identifier)
            model = ai_repo.get_model_by_id(model_id)
        except (ValueError, TypeError):
            # Eğer model_id olarak çevrilemezse, data_ai_index olarak dene
            model = ai_repo.get_model_by_data_ai_index(model_identifier)
            
            # Eğer bulunamazsa ve model_identifier sayısal değilse, 'txt_' öneki olmadan dene
            if not model and model_identifier.startswith('txt_'):
                try:
                    model_id = int(model_identifier.replace('txt_', ''))
                    model = ai_repo.get_model_by_id(model_id)
                except (ValueError, TypeError):
                    pass
        
        if not model:
            return None
            
        # Format the response to match the expected structure
        model_details = {
            "name": model["name"],
            "api_url": model["api_url"],
            "data_ai_index": model["data_ai_index"],
            "request_method": model.get("request_method", "POST"),  # Varsayılan POST
            "request_headers": model.get("request_headers", {}),  # Varsayılan boş
            "request_body_template": model.get("request_body_template", ""),  # Varsayılan boş
            "response_path": model.get("response_path", "")  # Varsayılan boş
        }
        
        return model_details
        
    except Exception as e:
        # print(f"HATA: Model detayları alınırken: {e}")
        return None

# 2.2. Kategori ve Model Listeleme
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """Tüm AI kategorilerini ve ilişkili modellerini getirir."""
    try:
        print("DEBUG: fetch_ai_categories_from_db başlatılıyor")
        category_repo = CategoryRepository()
        model_repo = ModelRepository()
        
        categories = category_repo.get_all_categories()
        print(f"DEBUG: {len(categories)} kategori bulundu")
        
        categories_data = []
        for i, category in enumerate(categories):
            print(f"DEBUG: Kategori {i+1}/{len(categories)} işleniyor: {category.name} (ID: {category.id})")
            
            category_dict = {
                "id": category.id,
                "name": category.name,
                "icon": category.icon,
                "models": []  # Boş models listesi oluştur
            }
            
            # Fetch models for the current category
            models = model_repo.get_models_by_category_id(category.id)
            print(f"DEBUG: Kategori '{category.name}' için {len(models)} model bulundu")
            
            for j, model in enumerate(models):
                print(f"DEBUG: Model {j+1}/{len(models)} işleniyor: {model.name} (ID: {model.id})")
                
                # Make sure to properly escape any quotes in the API URL to prevent JSON parsing errors
                api_url = model.api_url
                if api_url and '"' in api_url:
                    api_url = api_url.replace('"', '\\"')  # Escape double quotes for JSON

                model_dict = {
                    "id": model.id,
                    "name": model.name,
                    "icon": model.icon,
                    "api_url": api_url
                }
                
                print(f"DEBUG: Model verisi: {model_dict}")
                category_dict["models"].append(model_dict)
                
            categories_data.append(category_dict)
            print(f"DEBUG: Kategori '{category.name}' verisi: {category_dict}")
            
        print(f"DEBUG: Toplam {len(categories_data)} kategori verisi döndürülüyor")
        return categories_data
        
    except Exception as e:
        print(f"HATA: fetch_ai_categories_from_db içinde: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

# -----------------------------------------------------------------------------
# 3. Yardımcı Fonksiyonlar
# -----------------------------------------------------------------------------
# 3.1. Model Ekleme
def add_ai_model(category_name: str, model_name: str, model_icon: str, 
               data_ai_index: str, api_url: str) -> bool:
    """Veritabanına yeni bir AI modeli ekler."""
    try:
        model_repo = ModelRepository()
        
        # Get the category
        category = model_repo.get_category_by_name(category_name)
        if not category:
            # Create the category if it doesn't exist
            model_repo.insert_category(category_name, "bi-folder")
            category = model_repo.get_category_by_name(category_name)
            if not category:
                return False
        
        # Add the model
        result = model_repo.create_model(
            category["id"], model_name, model_icon, data_ai_index, api_url
        )
        return result
        
    except Exception:
        return False

# 3.2. Tüm Modelleri Getirme
def get_all_available_models() -> List[Dict[str, Any]]:
    """Tüm mevcut AI modellerini düz bir liste formatında getirir."""
    try:
        model_repo = ModelRepository()
        models = model_repo.get_all_models()
        
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
