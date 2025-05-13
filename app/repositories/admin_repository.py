# =============================================================================
# Admin Repository
# =============================================================================
# Contents:
# 1. Imports
# 2. AdminRepository Class
#    2.1. __init__
#    2.2. Category Management
#         2.2.1. create_category
#         2.2.2. update_category
#         2.2.3. delete_category
#         2.2.4. get_category_details
#         2.2.5. get_all_categories_with_models
#    2.3. Model Management
#         2.3.1. create_model
#         2.3.2. update_model
#         2.3.3. delete_model
#         2.3.4. get_model_details
#    2.4. Admin Panel Statistics
#         2.4.1. get_admin_dashboard_stats
#    2.5. Icon Management
#         2.5.1. get_available_icons
# =============================================================================

# 1. Imports
# =============================================================================
from app.models.base import BaseRepository, DatabaseConnection
from app.repositories.category_repository import CategoryRepository
from app.repositories.model_repository import ModelRepository
from app.models.entities import Category, Model
from typing import List, Optional, Tuple, Dict, Any
from mysql.connector import Error

# 2. AdminRepository Class
# =============================================================================
class AdminRepository(BaseRepository):
    """Repository class for admin panel operations."""
    
    # 2.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        super().__init__(db_connection)
        self.category_repo = CategoryRepository(self.db)
        self.model_repo = ModelRepository(self.db)
    
    # 2.2. Category Management
    # -------------------------------------------------------------------------
    # 2.2.1. create_category
    def create_category(self, name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
        """Creates a new category."""
        return self.category_repo.create_category(name, icon)
    
    # 2.2.2. update_category
    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """Updates an existing category."""
        return self.category_repo.update_category(category_id, name, icon)
    
    # 2.2.3. delete_category
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """Deletes a category and all associated models."""
        return self.category_repo.delete_category(category_id)
    
    # 2.2.4. get_category_details
    def get_category_details(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves category details and associated models."""
        category = self.category_repo.get_category_by_id(category_id)
        if not category:
            return None
        
        models = self.model_repo.get_models_by_category_id(category_id)
        
        return {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "models": [model.to_dict() for model in models]
        }
    
    # 2.2.5. get_all_categories_with_models
    def get_all_categories_with_models(self) -> List[Dict[str, Any]]:
        """Retrieves all categories and their associated models."""
        categories = self.category_repo.get_all_categories()
        result = []
        
        for category_data in categories: 
            models = self.model_repo.get_models_by_category_id(category_data.id)
            result.append({
                "id": category_data.id,
                "name": category_data.name,
                "icon": category_data.icon,
                "models": [model.to_dict() for model in models],
                "model_count": len(models)
            })
        
        return result
    
    # 2.3. Model Management
    # -------------------------------------------------------------------------
    # 2.3.1. create_model
    def create_model(self, category_id: int, name: str, icon: str, data_ai_index: str, 
                     api_url: str, request_method: str = 'POST', request_headers: str = None, 
                     request_body_template: str = None, response_path: str = None) -> Tuple[bool, str, Optional[int]]:
        """Creates a new model."""
        return self.model_repo.create_model(
            category_id, name, icon, data_ai_index, api_url, 
            request_method, request_headers, request_body_template, response_path
        )
    
    # 2.3.2. update_model
    def update_model(self, model_id: int, category_id: int, name: str, icon: str, 
                     data_ai_index: str, api_url: str, request_method: str = 'POST', 
                     request_headers: str = None, request_body_template: str = None, 
                     response_path: str = None) -> Tuple[bool, str]:
        """Updates an existing model."""
        return self.model_repo.update_model(
            model_id, category_id, name, icon, data_ai_index, api_url, 
            request_method, request_headers, request_body_template, response_path
        )
    
    # 2.3.3. delete_model
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """Deletes a model."""
        return self.model_repo.delete_model(model_id)
    
    # 2.3.4. get_model_details
    def get_model_details(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves model details."""
        model = self.model_repo.get_model_by_id(model_id)
        if not model:
            return None
        
        category = self.category_repo.get_category_by_id(model.category_id)
        model_dict = model.to_dict()
        
        if category:
            model_dict['category_name'] = category.name
        else:
            model_dict['category_name'] = 'Unknown' # For cases where category might be missing
        
        return model_dict
    
    # 2.4. Admin Panel Statistics
    # -------------------------------------------------------------------------
    # 2.4.1. get_admin_dashboard_stats
    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        """Retrieves statistics for the admin dashboard."""
        stats = {
            'category_count': 0,
            'model_count': 0,
            'categories': [],
            'models': []
        }
        
        query_category_count = "SELECT COUNT(*) as count FROM ai_categories"
        result_category_count = self.fetch_one(query_category_count)
        stats['category_count'] = result_category_count['count'] if result_category_count else 0
        
        query_model_count = "SELECT COUNT(*) as count FROM ai_models"
        result_model_count = self.fetch_one(query_model_count)
        stats['model_count'] = result_model_count['count'] if result_model_count else 0
        
        query_categories = "SELECT id, name, icon FROM ai_categories ORDER BY id DESC LIMIT 5"
        results_categories = self.fetch_all(query_categories)
        stats['categories'] = [Category.from_dict(row).to_dict() for row in results_categories]
        
        query_models = """
            SELECT m.*, c.name as category_name 
            FROM ai_models m
            JOIN ai_categories c ON m.category_id = c.id
            ORDER BY m.id DESC LIMIT 5
        """
        results_models = self.fetch_all(query_models)
        
        models_data = []
        for row in results_models:
            model_dict_from_row = {k: v for k, v in row.items() if k != 'category_name'}
            model_instance = Model.from_dict(model_dict_from_row)
            model_data_item = model_instance.to_dict()
            model_data_item['category_name'] = row['category_name']
            models_data.append(model_data_item)
        
        stats['models'] = models_data
        
        return stats
    
    # 2.5. Icon Management
    # -------------------------------------------------------------------------
    # 2.5.1. get_available_icons
    def get_available_icons(self) -> List[Dict[str, str]]:
        """Retrieves available Bootstrap icons."""
        icons = [
            {"class": "bi-robot", "name": "Robot"},
            {"class": "bi-gem", "name": "Gem"},
            {"class": "bi-cpu", "name": "CPU"},
            {"class": "bi-lightning", "name": "Lightning"},
            {"class": "bi-stars", "name": "Stars"},
            {"class": "bi-magic", "name": "Magic"},
            {"class": "bi-chat-dots", "name": "Chat"},
            {"class": "bi-brain", "name": "Brain"},
            {"class": "bi-lightbulb", "name": "Lightbulb"},
            {"class": "bi-gear", "name": "Gear"},
            {"class": "bi-tools", "name": "Tools"},
            {"class": "bi-code", "name": "Code"},
            {"class": "bi-translate", "name": "Translate"},
            {"class": "bi-image", "name": "Image"},
            {"class": "bi-music-note", "name": "Music"},
            {"class": "bi-film", "name": "Film"},
            {"class": "bi-pencil", "name": "Pencil"},
            {"class": "bi-book", "name": "Book"},
            {"class": "bi-globe", "name": "Globe"},
            {"class": "bi-search", "name": "Search"}
        ]
        return icons
