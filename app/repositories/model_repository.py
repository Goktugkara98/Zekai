# =============================================================================
# Model Repository
# =============================================================================
# Contents:
# 1. Imports
# 2. ModelRepository Class
#    2.1. __init__ (Implicit from BaseRepository)
#    2.2. create_model
#    2.3. update_model
#    2.4. delete_model
#    2.5. get_model_by_id
#    2.6. get_model_by_data_ai_index
#    2.7. get_models_by_category_id
#    2.8. get_all_models
#    2.9. Helper Methods
#         2.9.1. _validate_model_input
# =============================================================================

# 1. Imports
# =============================================================================
from app.models.base import BaseRepository, DatabaseConnection # Added DatabaseConnection for completeness
from app.models.entities import Model
from typing import List, Optional, Tuple
from mysql.connector import Error
import re

# 2. ModelRepository Class
# =============================================================================
class ModelRepository(BaseRepository):
    """Repository class for model operations."""

    # 2.1. __init__ is implicitly inherited from BaseRepository.

    # 2.2. create_model
    # -------------------------------------------------------------------------
    def create_model(self, category_id: int, name: str, icon: str, data_ai_index: str,
                     api_url: str, request_method: str = 'POST', request_headers: str = None,
                     request_body_template: str = None, response_path: str = None) -> Tuple[bool, str, Optional[int]]:
        """Creates a new model."""
        try:
            # Validate inputs
            is_valid, message = self._validate_model_input(
                category_id, name, icon, data_ai_index, api_url
            )
            if not is_valid:
                return False, message, None

            # Check if category exists
            query_check_category = "SELECT id FROM ai_categories WHERE id = %s"
            category = self.fetch_one(query_check_category, (category_id,))
            if not category:
                return False, f"Category with ID {category_id} not found", None

            # Check if data_ai_index already exists
            query_check_index = "SELECT id FROM ai_models WHERE data_ai_index = %s"
            existing_model = self.fetch_one(query_check_index, (data_ai_index,))
            if existing_model:
                return False, f"A model with data_ai_index '{data_ai_index}' already exists", None

            # Set default values
            if request_headers is None:
                request_headers = '{"Content-Type": "application/json"}'
            if request_body_template is None:
                request_body_template = '{"contents": [{"parts":[{"text": "$message"}]}]}'
            if response_path is None:
                response_path = 'candidates[0].content.parts[0].text'

            # Create the model
            query_insert_model = """
                INSERT INTO ai_models
                (category_id, name, icon, data_ai_index, api_url, request_method, request_headers, request_body_template, response_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            model_id = self.insert(query_insert_model, (
                category_id, name, icon, data_ai_index, api_url, request_method,
                request_headers, request_body_template, response_path
            ))

            return True, f"Model '{name}' created successfully", model_id

        except Error as e:
            return False, f"Database error: {str(e)}", None

    # 2.3. update_model
    # -------------------------------------------------------------------------
    def update_model(self, model_id: int, category_id: int, name: str, icon: str,
                     data_ai_index: str, api_url: str, request_method: str = 'POST',
                     request_headers: str = None, request_body_template: str = None,
                     response_path: str = None) -> Tuple[bool, str]:
        """Updates an existing model."""
        try:
            # Validate model ID
            if not model_id or not isinstance(model_id, int):
                return False, "A valid model ID is required"

            # Validate other inputs
            is_valid, message = self._validate_model_input(
                category_id, name, icon, data_ai_index, api_url
            )
            if not is_valid:
                return False, message

            # Check if model exists
            query_check_model = "SELECT id, data_ai_index FROM ai_models WHERE id = %s"
            model_data = self.fetch_one(query_check_model, (model_id,))
            if not model_data:
                return False, f"Model with ID {model_id} not found"

            current_data_ai_index = model_data['data_ai_index']

            # Check if category exists
            query_check_category = "SELECT id FROM ai_categories WHERE id = %s"
            category = self.fetch_one(query_check_category, (category_id,))
            if not category:
                return False, f"Category with ID {category_id} not found"

            # Check if data_ai_index is being changed and if the new one already exists for another model
            if data_ai_index != current_data_ai_index:
                query_check_new_index = "SELECT id FROM ai_models WHERE data_ai_index = %s AND id != %s"
                existing_model_with_new_index = self.fetch_one(query_check_new_index, (data_ai_index, model_id))
                if existing_model_with_new_index:
                    return False, f"Another model with data_ai_index '{data_ai_index}' already exists"

            # Set default values if None
            if request_headers is None:
                request_headers = '{"Content-Type": "application/json"}'
            if request_body_template is None:
                request_body_template = '{"contents": [{"parts":[{"text": "$message"}]}]}'
            if response_path is None:
                response_path = 'candidates[0].content.parts[0].text'

            # Update the model
            query_update_model = """
                UPDATE ai_models
                SET category_id = %s, name = %s, icon = %s, data_ai_index = %s, api_url = %s,
                    request_method = %s, request_headers = %s, request_body_template = %s, response_path = %s
                WHERE id = %s
            """
            rows_affected = self.execute_query(query_update_model, (
                category_id, name, icon, data_ai_index, api_url, request_method,
                request_headers, request_body_template, response_path, model_id
            ))

            if rows_affected == 0:
                return True, f"No changes made to model '{name}'. Data might be the same." # Changed to True as no error occurred

            return True, f"Model '{name}' updated successfully"

        except Error as e:
            return False, f"Database error: {str(e)}"

    # 2.4. delete_model
    # -------------------------------------------------------------------------
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """Deletes a model."""
        try:
            if not model_id or not isinstance(model_id, int):
                return False, "A valid model ID is required"

            # Check if model exists to get its name for the message
            query_check_model = "SELECT name FROM ai_models WHERE id = %s"
            model_data = self.fetch_one(query_check_model, (model_id,))
            if not model_data:
                return False, f"Model with ID {model_id} not found"
            model_name = model_data['name']

            # Delete the model
            query_delete_model = "DELETE FROM ai_models WHERE id = %s"
            self.execute_query(query_delete_model, (model_id,))

            return True, f"Model '{model_name}' deleted successfully"

        except Error as e:
            return False, f"Database error: {str(e)}"

    # 2.5. get_model_by_id
    # -------------------------------------------------------------------------
    def get_model_by_id(self, model_id: int) -> Optional[Model]:
        """Retrieves a model by its ID."""
        query = "SELECT * FROM ai_models WHERE id = %s"
        result = self.fetch_one(query, (model_id,))
        return Model.from_dict(result) if result else None

    # 2.6. get_model_by_data_ai_index
    # -------------------------------------------------------------------------
    def get_model_by_data_ai_index(self, data_ai_index: str) -> Optional[Model]:
        """Retrieves a model by its data_ai_index."""
        query = "SELECT * FROM ai_models WHERE data_ai_index = %s"
        result = self.fetch_one(query, (data_ai_index,))
        return Model.from_dict(result) if result else None

    # 2.7. get_models_by_category_id
    # -------------------------------------------------------------------------
    def get_models_by_category_id(self, category_id: int) -> List[Model]:
        """Retrieves models by their category ID."""
        query = "SELECT * FROM ai_models WHERE category_id = %s ORDER BY id"
        results = self.fetch_all(query, (category_id,))
        return [Model.from_dict(row) for row in results]

    # 2.8. get_all_models
    # -------------------------------------------------------------------------
    def get_all_models(self) -> List[Model]:
        """Retrieves all models, ordered by category_id and then id."""
        query = "SELECT * FROM ai_models ORDER BY category_id, id"
        results = self.fetch_all(query)
        return [Model.from_dict(row) for row in results]

    # 2.9. Helper Methods
    # -------------------------------------------------------------------------
    # 2.9.1. _validate_model_input
    def _validate_model_input(self, category_id: int, name: str, icon: str,
                             data_ai_index: str, api_url: str) -> Tuple[bool, str]:
        """Validates model input fields."""
        if not category_id or not isinstance(category_id, int):
            return False, "A valid category ID is required"
        if not name or len(name) > 255:
            return False, "Model name is required and must be less than 255 characters"
        if not icon or len(icon) > 255:
            return False, "Model icon is required and must be less than 255 characters"
        if not data_ai_index or len(data_ai_index) > 50: # Max length for data_ai_index is 50
            return False, "data_ai_index is required and must be less than 50 characters"
        if not re.match(r'^[a-zA-Z0-9_-]+$', data_ai_index): # Alphanumeric, underscore, hyphen
            return False, "data_ai_index can only contain letters, numbers, underscores, and hyphens"
        if not api_url or len(api_url) > 2048: # Max length for api_url, assuming a larger limit for URLs
            return False, "API URL is required and must be less than 2048 characters" # Adjusted length for API URL
        return True, ""
