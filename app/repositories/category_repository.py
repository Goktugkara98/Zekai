# =============================================================================
# Category Repository
# =============================================================================
# Contents:
# 1. Imports
# 2. CategoryRepository Class
#    2.1. __init__ (Implicit from BaseRepository)
#    2.2. create_category
#    2.3. update_category
#    2.4. delete_category
#    2.5. get_category_by_id
#    2.6. get_category_by_name
#    2.7. get_all_categories
# =============================================================================

# 1. Imports
# =============================================================================
from app.models.base import BaseRepository, DatabaseConnection # Added DatabaseConnection for completeness, though not directly used in this snippet
from app.models.entities import Category
from typing import List, Optional, Tuple
from mysql.connector import Error

# 2. CategoryRepository Class
# =============================================================================
class CategoryRepository(BaseRepository):
    """Repository class for category operations."""
    
    # 2.1. __init__ is implicitly inherited from BaseRepository and doesn't need to be redefined
    #      if no additional initialization specific to CategoryRepository is needed.
    
    # 2.2. create_category
    # -------------------------------------------------------------------------
    def create_category(self, name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
        """Creates a new category."""
        try:
            if not name or len(name) > 255:
                return False, "Category name is required and must be less than 255 characters", None
            
            if not icon or len(icon) > 255:
                return False, "Category icon is required and must be less than 255 characters", None
            
            # Check if a category with the same name already exists
            existing = self.get_category_by_name(name)
            if existing:
                return False, f"A category named '{name}' already exists", None
            
            # Create the category
            query = "INSERT INTO ai_categories (name, icon) VALUES (%s, %s)"
            category_id = self.insert(query, (name, icon))
            
            return True, f"Category '{name}' created successfully", category_id
            
        except Error as e:
            return False, f"Database error: {str(e)}", None
    
    # 2.3. update_category
    # -------------------------------------------------------------------------
    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """Updates an existing category."""
        try:
            if not category_id or not isinstance(category_id, int):
                return False, "A valid category ID is required"
                
            if not name or len(name) > 255:
                return False, "Category name is required and must be less than 255 characters"
            
            if not icon or len(icon) > 255:
                return False, "Category icon is required and must be less than 255 characters"
            
            # Check if the category exists
            category = self.get_category_by_id(category_id)
            if not category:
                return False, f"Category with ID {category_id} not found"
            
            # Check if another category with the same name exists
            query = "SELECT id FROM ai_categories WHERE name = %s AND id != %s"
            existing = self.fetch_one(query, (name, category_id))
            if existing:
                return False, f"Another category named '{name}' already exists"
            
            # Update the category
            query = "UPDATE ai_categories SET name = %s, icon = %s WHERE id = %s"
            rows_affected = self.execute_query(query, (name, icon, category_id))
            
            if rows_affected == 0: # No changes made, possibly same data
                return True, f"No changes made to category with ID {category_id}. Data might be the same."
                
            return True, "Category updated successfully"
            
        except Error as e:
            return False, f"Database error: {str(e)}"
    
    # 2.4. delete_category
    # -------------------------------------------------------------------------
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """Deletes a category and all associated models (due to foreign key cascade)."""
        try:
            if not category_id or not isinstance(category_id, int):
                return False, "A valid category ID is required"
            
            # Check if the category exists
            category = self.get_category_by_id(category_id)
            if not category:
                return False, f"Category with ID {category_id} not found"
            
            category_name = category.name
            
            # Get the count of associated models (for the message, actual deletion is handled by cascade)
            query_model_count = "SELECT COUNT(*) as model_count FROM ai_models WHERE category_id = %s"
            result_model_count = self.fetch_one(query_model_count, (category_id,))
            model_count = result_model_count['model_count'] if result_model_count else 0
            
            # Delete the category (associated models will be deleted by database cascade rule if set up)
            query_delete_category = "DELETE FROM ai_categories WHERE id = %s"
            self.execute_query(query_delete_category, (category_id,))
            
            return True, f"Category '{category_name}' and its {model_count} associated model(s) deleted successfully"
            
        except Error as e:
            return False, f"Database error: {str(e)}"
    
    # 2.5. get_category_by_id
    # -------------------------------------------------------------------------
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieves a category by its ID."""
        query = "SELECT id, name, icon FROM ai_categories WHERE id = %s"
        result = self.fetch_one(query, (category_id,))
        return Category.from_dict(result) if result else None
    
    # 2.6. get_category_by_name
    # -------------------------------------------------------------------------
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Retrieves a category by its name."""
        query = "SELECT id, name, icon FROM ai_categories WHERE name = %s"
        result = self.fetch_one(query, (name,))
        return Category.from_dict(result) if result else None
    
    # 2.7. get_all_categories
    # -------------------------------------------------------------------------
    def get_all_categories(self) -> List[Category]:
        """Retrieves all categories, ordered by ID."""
        query = "SELECT id, name, icon FROM ai_categories ORDER BY id"
        results = self.fetch_all(query)
        return [Category.from_dict(row) for row in results]
