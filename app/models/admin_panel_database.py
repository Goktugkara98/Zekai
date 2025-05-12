# =============================================================================
# Admin Panel Database Module
# =============================================================================
# Contents:
# 1. Imports
# 2. Admin Repository
#    2.1. Initialization and Connection Management
#    2.2. Category Management
#    2.3. Model Management
#    2.4. Validation Functions
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
import mysql.connector
from mysql.connector import Error
from app.models.database import DatabaseConnection, AIModelRepository
from typing import Dict, List, Optional, Any, Tuple
import re

# -----------------------------------------------------------------------------
# 2. Admin Repository
# -----------------------------------------------------------------------------
class AdminRepository:
    # -------------------------------------------------------------------------
    # 2.1. Initialization and Connection Management
    # -------------------------------------------------------------------------
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
        self.ai_repo = AIModelRepository(self.db)
    
    def _ensure_connection(self):
        if not hasattr(self.db, '_ensure_connection'):
            if not self.db.connection or not self.db.cursor:
                self.db.connect()
        else:
            self.db._ensure_connection()
    
    def _close_if_owned(self):
        if self.own_connection:
            self.db.close()
    
    # -------------------------------------------------------------------------
    # 2.2. Category Management
    # -------------------------------------------------------------------------
    def create_category(self, name: str, icon: str) -> Tuple[bool, str]:
        """
        Creates a new AI category.
        
        Args:
            name: The name of the category
            icon: The icon identifier for the category
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if not name or len(name) > 255:
                return False, "Category name is required and must be less than 255 characters"
            
            if not icon or len(icon) > 255:
                return False, "Category icon is required and must be less than 255 characters"
            
            # Check if category already exists
            existing = self.ai_repo.get_ai_category_by_name(name)
            if existing:
                return False, f"Category '{name}' already exists"
            
            # Create the category
            self._ensure_connection()
            self.db.cursor.execute("""
                INSERT INTO ai_categories (name, icon) 
                VALUES (%s, %s)
            """, (name, icon))
            self.db.connection.commit()
            
            return True, f"Category '{name}' created successfully"
            
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            self._close_if_owned()
    
    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """
        Updates an existing AI category.
        
        Args:
            category_id: The ID of the category to update
            name: The new name of the category
            icon: The new icon identifier for the category
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if not category_id or not isinstance(category_id, int):
                return False, "Valid category ID is required"
                
            if not name or len(name) > 255:
                return False, "Category name is required and must be less than 255 characters"
            
            if not icon or len(icon) > 255:
                return False, "Category icon is required and must be less than 255 characters"
            
            # Check if category exists
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id FROM ai_categories WHERE id = %s
            """, (category_id,))
            if not self.db.cursor.fetchone():
                return False, f"Category with ID {category_id} not found"
            
            # Check if name already exists for another category
            self.db.cursor.execute("""
                SELECT id FROM ai_categories WHERE name = %s AND id != %s
            """, (name, category_id))
            if self.db.cursor.fetchone():
                return False, f"Another category with name '{name}' already exists"
            
            # Update the category
            self.db.cursor.execute("""
                UPDATE ai_categories 
                SET name = %s, icon = %s 
                WHERE id = %s
            """, (name, icon, category_id))
            self.db.connection.commit()
            
            if self.db.cursor.rowcount == 0:
                return False, f"No changes made to category with ID {category_id}"
                
            return True, f"Category updated successfully"
            
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            self._close_if_owned()
    
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """
        Deletes an AI category and all associated models.
        
        Args:
            category_id: The ID of the category to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if not category_id or not isinstance(category_id, int):
                return False, "Valid category ID is required"
            
            # Check if category exists
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT name FROM ai_categories WHERE id = %s
            """, (category_id,))
            category = self.db.cursor.fetchone()
            if not category:
                return False, f"Category with ID {category_id} not found"
            
            category_name = category['name']
            
            # Count associated models
            self.db.cursor.execute("""
                SELECT COUNT(*) as model_count FROM ai_models WHERE category_id = %s
            """, (category_id,))
            model_count = self.db.cursor.fetchone()['model_count']
            
            # Delete the category (will cascade delete models due to foreign key)
            self.db.cursor.execute("""
                DELETE FROM ai_categories WHERE id = %s
            """, (category_id,))
            self.db.connection.commit()
            
            return True, f"Category '{category_name}' and {model_count} associated models deleted successfully"
            
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            self._close_if_owned()
    
    def get_category_details(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets detailed information about a category including its models.
        
        Args:
            category_id: The ID of the category
            
        Returns:
            Dictionary with category details and models, or None if not found
        """
        try:
            self._ensure_connection()
            
            # Get category info
            self.db.cursor.execute("""
                SELECT id, name, icon 
                FROM ai_categories 
                WHERE id = %s
            """, (category_id,))
            category = self.db.cursor.fetchone()
            
            if not category:
                return None
                
            # Get models for this category
            models = self.ai_repo.get_ai_models_by_category_id(category_id)
            
            return {
                "id": category["id"],
                "name": category["name"],
                "icon": category["icon"],
                "models": models
            }
            
        except Error as e:
            print(f"Error getting category details: {e}")
            return None
        finally:
            self._close_if_owned()
    
    # -------------------------------------------------------------------------
    # 2.3. Model Management
    # -------------------------------------------------------------------------
    def create_model(self, category_id: int, name: str, icon: str, 
                     data_ai_index: str, api_url: str, request_method: str = 'POST',
                     request_headers: str = None, request_body_template: str = None,
                     response_path: str = None) -> Tuple[bool, str]:
        """
        Creates a new AI model.
        
        Args:
            category_id: The ID of the category for this model
            name: The name of the model
            icon: The icon identifier for the model
            data_ai_index: The unique data-ai-index value
            api_url: The API URL for the model
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            validation_result = self._validate_model_input(
                category_id, name, icon, data_ai_index, api_url
            )
            if not validation_result[0]:
                return validation_result
            
            # Check if category exists
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id FROM ai_categories WHERE id = %s
            """, (category_id,))
            if not self.db.cursor.fetchone():
                return False, f"Category with ID {category_id} not found"
            
            # Check if data_ai_index already exists
            self.db.cursor.execute("""
                SELECT id FROM ai_models WHERE data_ai_index = %s
            """, (data_ai_index,))
            if self.db.cursor.fetchone():
                return False, f"Model with data_ai_index '{data_ai_index}' already exists"
            
            # Set default values if not provided
            if request_headers is None:
                request_headers = '{"Content-Type": "application/json"}'
            
            if request_body_template is None:
                request_body_template = '{"contents": [{"parts":[{"text": "$message"}]}]}'
                
            if response_path is None:
                response_path = 'candidates[0].content.parts[0].text'
                
            # Create the model
            self.db.cursor.execute("""
                INSERT INTO ai_models 
                (category_id, name, icon, data_ai_index, api_url, request_method, request_headers, request_body_template, response_path) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (category_id, name, icon, data_ai_index, api_url, request_method, request_headers, request_body_template, response_path))
            self.db.connection.commit()
            
            return True, f"Model '{name}' created successfully"
            
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            self._close_if_owned()
    
    def update_model(self, model_id: int, category_id: int, name: str, 
                     icon: str, data_ai_index: str, api_url: str, request_method: str = 'POST',
                     request_headers: str = None, request_body_template: str = None,
                     response_path: str = None) -> Tuple[bool, str]:
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
            Tuple of (success, message)
        """
        try:
            # Validate model_id
            if not model_id or not isinstance(model_id, int):
                return False, "Valid model ID is required"
                
            # Validate other inputs
            validation_result = self._validate_model_input(
                category_id, name, icon, data_ai_index, api_url
            )
            if not validation_result[0]:
                return validation_result
            
            # Check if model exists
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id, data_ai_index FROM ai_models WHERE id = %s
            """, (model_id,))
            model = self.db.cursor.fetchone()
            if not model:
                return False, f"Model with ID {model_id} not found"
            
            current_data_ai_index = model['data_ai_index']
            
            # Check if category exists
            self.db.cursor.execute("""
                SELECT id FROM ai_categories WHERE id = %s
            """, (category_id,))
            if not self.db.cursor.fetchone():
                return False, f"Category with ID {category_id} not found"
            
            # Check if data_ai_index already exists for another model
            if data_ai_index != current_data_ai_index:
                self.db.cursor.execute("""
                    SELECT id FROM ai_models WHERE data_ai_index = %s AND id != %s
                """, (data_ai_index, model_id))
                if self.db.cursor.fetchone():
                    return False, f"Another model with data_ai_index '{data_ai_index}' already exists"
            
            # Set default values if not provided
            if request_headers is None:
                request_headers = '{"Content-Type": "application/json"}'
            
            if request_body_template is None:
                request_body_template = '{"contents": [{"parts":[{"text": "$message"}]}]}'
                
            if response_path is None:
                response_path = 'candidates[0].content.parts[0].text'
                
            # Update the model
            self.db.cursor.execute("""
                UPDATE ai_models 
                SET category_id = %s, name = %s, icon = %s, data_ai_index = %s, api_url = %s,
                    request_method = %s, request_headers = %s, request_body_template = %s, response_path = %s 
                WHERE id = %s
            """, (category_id, name, icon, data_ai_index, api_url, request_method, request_headers, 
                  request_body_template, response_path, model_id))
            self.db.connection.commit()
            
            if self.db.cursor.rowcount == 0:
                return False, f"No changes made to model with ID {model_id}"
                
            return True, f"Model '{name}' updated successfully"
            
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            self._close_if_owned()
    
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """
        Deletes an AI model.
        
        Args:
            model_id: The ID of the model to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if not model_id or not isinstance(model_id, int):
                return False, "Valid model ID is required"
            
            # Check if model exists
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT name FROM ai_models WHERE id = %s
            """, (model_id,))
            model = self.db.cursor.fetchone()
            if not model:
                return False, f"Model with ID {model_id} not found"
            
            model_name = model['name']
            
            # Delete the model
            self.db.cursor.execute("""
                DELETE FROM ai_models WHERE id = %s
            """, (model_id,))
            self.db.connection.commit()
            
            return True, f"Model '{model_name}' deleted successfully"
            
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            self._close_if_owned()
    
    def get_model_details(self, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets detailed information about a model.
        
        Args:
            model_id: The ID of the model
            
        Returns:
            Dictionary with model details, or None if not found
        """
        try:
            self._ensure_connection()
            
            self.db.cursor.execute("""
                SELECT m.id, m.category_id, m.name, m.icon, m.data_ai_index, m.api_url, c.name as category_name
                FROM ai_models m
                JOIN ai_categories c ON m.category_id = c.id
                WHERE m.id = %s
            """, (model_id,))
            
            model = self.db.cursor.fetchone()
            return model
            
        except Error as e:
            print(f"Error getting model details: {e}")
            return None
        finally:
            self._close_if_owned()
    
    # -------------------------------------------------------------------------
    # 2.4. Validation Functions
    # -------------------------------------------------------------------------
    def _validate_model_input(self, category_id: int, name: str, icon: str, 
                             data_ai_index: str, api_url: str, request_method: str = None,
                             request_headers: str = None, request_body_template: str = None,
                             response_path: str = None) -> Tuple[bool, str]:
        """
        Validates input data for model creation/update.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not category_id or not isinstance(category_id, int):
            return False, "Valid category ID is required"
            
        if not name or len(name) > 255:
            return False, "Model name is required and must be less than 255 characters"
        
        if not icon or len(icon) > 255:
            return False, "Model icon is required and must be less than 255 characters"
        
        if not data_ai_index or len(data_ai_index) > 50:
            return False, "data_ai_index is required and must be less than 50 characters"
        
        # Validate data_ai_index format (alphanumeric)
        if not re.match(r'^[a-zA-Z0-9_-]+$', data_ai_index):
            return False, "data_ai_index must contain only letters, numbers, underscores, and hyphens"
        
        if not api_url or len(api_url) > 255:
            return False, "API URL is required and must be less than 255 characters"
        
        return True, ""
