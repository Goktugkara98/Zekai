# =============================================================================
# AI Model Service Module
# =============================================================================
# Contents:
# 1. Imports
# 2. AI Model Management
#    2.1. Model Details Retrieval
#    2.2. Category and Model Listing
# 3. Future Expansion Areas
#    3.1. Model Administration
#    3.2. API Integration
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from app.models.database import AIModelRepository
from typing import Dict, List, Optional, Any

# -----------------------------------------------------------------------------
# 2. AI Model Management
# -----------------------------------------------------------------------------
# 2.1. Model Details Retrieval
def get_ai_model_api_details(data_ai_index: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves API details for a specific AI model by its data_ai_index.
    
    Args:
        data_ai_index: The unique identifier for the AI model
        
    Returns:
        Dictionary containing model details or None if not found
    """
    try:
        print(f"Service Layer: Fetching AI model details for data_ai_index: {data_ai_index}")
        ai_repo = AIModelRepository()
        model = ai_repo.get_ai_model_by_data_ai_index(data_ai_index)
        
        if not model:
            print(f"Service Layer: No model found for data_ai_index: {data_ai_index}")
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
        
        print(f"Service Layer: Found model details: {model_details}")
        return model_details
        
    except Exception as err:
        print(f"Service Layer: Error fetching AI model details: {err}")
        return None

# 2.2. Category and Model Listing
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """
    Retrieves all AI categories with their associated models.
    
    Returns:
        List of dictionaries containing category information and associated models
    """
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
        
    except Exception as err:
        print(f"Service Layer: Error fetching AI categories: {err}")
        return []

# -----------------------------------------------------------------------------
# 3. Future Expansion Areas
# -----------------------------------------------------------------------------
# 3.1. Model Administration
def add_ai_model(category_name: str, model_name: str, model_icon: str, 
               data_ai_index: str, api_url: str) -> bool:
    """
    Adds a new AI model to the database.
    
    Args:
        category_name: Name of the category to add the model to
        model_name: Name of the model
        model_icon: Icon identifier for the model
        data_ai_index: Unique identifier for the model
        api_url: API URL for the model
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ai_repo = AIModelRepository()
        
        # Get the category
        category = ai_repo.get_ai_category_by_name(category_name)
        if not category:
            # Create the category if it doesn't exist
            ai_repo.insert_ai_category(category_name, "bi-folder")
            category = ai_repo.get_ai_category_by_name(category_name)
            if not category:
                print(f"Service Layer: Failed to create category: {category_name}")
                return False
        
        # Add the model
        result = ai_repo.insert_ai_model(
            category["id"], model_name, model_icon, data_ai_index, api_url
        )
        return result
        
    except Exception as err:
        print(f"Service Layer: Error adding AI model: {err}")
        return False

# 3.2. API Integration
def get_all_available_models() -> List[Dict[str, Any]]:
    """
    Retrieves all available AI models in a flat list format.
    
    Returns:
        List of dictionaries containing model information
    """
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
        
    except Exception as err:
        print(f"Service Layer: Error fetching all AI models: {err}")
        return []
