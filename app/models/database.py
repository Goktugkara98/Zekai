# =============================================================================
# Database Module
# =============================================================================
# Contents:
# 1. Imports
# 2. Database Connection
#    2.1. Initialization and Connection Management
#    2.2. Table Management
# 3. AI Model Repository
#    3.1. Initialization and Connection Management
#    3.2. Table Management
#    3.3. AI Category Operations
#    3.4. AI Model Operations
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
import mysql.connector
from mysql.connector import Error
from app.config import DB_CONFIG

# -----------------------------------------------------------------------------
# 2. Database Connection
# -----------------------------------------------------------------------------
class DatabaseConnection:
    # -------------------------------------------------------------------------
    # 2.1. Initialization and Connection Management
    # -------------------------------------------------------------------------
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_config = DB_CONFIG
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.cursor = None
        self.connection = None
    
    def _ensure_connection(self):
        if not self.connection or not self.cursor:
            self.connect()
    
    # -------------------------------------------------------------------------
    # 2.2. Table Management
    # -------------------------------------------------------------------------
    def create_all_tables(self):
        self._ensure_connection()
        
        ai_repo = AIModelRepository(self)
        
        ai_repo.create_ai_categories_table()
        ai_repo.create_ai_models_table()
        ai_repo.create_user_messages_table() # Ensure user_messages table exists
        ai_repo.seed_initial_data()

# -----------------------------------------------------------------------------
# 3. AI Model Repository
# -----------------------------------------------------------------------------
class AIModelRepository:
    # -------------------------------------------------------------------------
    # 3.1. Initialization and Connection Management
    # -------------------------------------------------------------------------
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
    
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
    # 3.2. Table Management
    # -------------------------------------------------------------------------
    def create_ai_categories_table(self):
        self._ensure_connection()
        try:
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    icon VARCHAR(255)
                );
            """)
            self.db.connection.commit()
            print("Table 'ai_categories' ensured.")
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"Error creating ai_categories table: {e}")
            raise
    
    def create_ai_models_table(self):
        self._ensure_connection()
        try:
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category_id INT,
                    name VARCHAR(255) NOT NULL,
                    icon VARCHAR(255),
                    data_ai_index VARCHAR(50) UNIQUE NOT NULL,
                    api_url VARCHAR(255) NOT NULL,
                    request_method VARCHAR(10) DEFAULT 'POST',
                    request_headers TEXT,
                    request_body_template TEXT,
                    response_path TEXT,
                    FOREIGN KEY (category_id) REFERENCES ai_categories(id) ON DELETE CASCADE
                );
            """)
            self.db.connection.commit()
            print("Table 'ai_models' ensured.")
            
            # Debug: Describe table schema
            try:
                self.db.cursor.execute("DESCRIBE ai_models;")
                schema = self.db.cursor.fetchall()
                print(f"DEBUG: Schema for ai_models: {schema}")
            except Exception as e:
                print(f"DEBUG: Error describing ai_models: {e}")
                
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"Error creating ai_models table: {e}")
            raise
    
    def create_user_messages_table(self):
        """Creates the user_messages table if it doesn't exist."""
        self._ensure_connection()
        try:
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255), /* Add session ID */
                    user_message TEXT,
                    ai_response TEXT,
                    ai_model_name VARCHAR(255), /* Track which model responded */
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.db.connection.commit()
            print("Table 'user_messages' ensured.")
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"Error creating user_messages table: {e}")
            raise
    
    # -------------------------------------------------------------------------
    # 3.3. AI Category Operations
    # -------------------------------------------------------------------------
    def insert_ai_category(self, name, icon):
        try:
            self._ensure_connection()
            self.db.cursor.execute("""
                INSERT IGNORE INTO ai_categories (name, icon) 
                VALUES (%s, %s)
            """, (name, icon))
            self.db.connection.commit()
            return True
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"Error inserting AI category: {e}")
            raise
        finally:
            self._close_if_owned()
    
    def get_ai_category_by_name(self, name):
        try:
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id, name, icon 
                FROM ai_categories 
                WHERE name = %s
            """, (name,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error getting AI category: {e}")
            return None
        finally:
            self._close_if_owned()
    
    def get_all_ai_categories(self):
        try:
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id, name, icon 
                FROM ai_categories 
                ORDER BY id
            """)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error getting all AI categories: {e}")
            return []
        finally:
            self._close_if_owned()
    
    # -------------------------------------------------------------------------
    # 3.4. AI Model Operations
    # -------------------------------------------------------------------------
    def insert_ai_model(self, category_id, name, icon, data_ai_index, api_url, 
                     request_method='POST', request_headers=None, request_body_template=None, response_path=None):
        try:
            self._ensure_connection()
            # Set default values if not provided
            if request_headers is None:
                request_headers = '{"Content-Type": "application/json"}'
            
            if request_body_template is None:
                request_body_template = '{"contents": [{"parts":[{"text": "$message"}]}]}'
                
            if response_path is None:
                response_path = 'candidates[0].content.parts[0].text'
                
            self.db.cursor.execute("""
                INSERT IGNORE INTO ai_models 
                (category_id, name, icon, data_ai_index, api_url, request_method, request_headers, request_body_template, response_path) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (category_id, name, icon, data_ai_index, api_url, request_method, request_headers, request_body_template, response_path))
            self.db.connection.commit()
            return True
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"Error inserting AI model: {e}")
            raise
        finally:
            self._close_if_owned()
    
    def get_ai_model_by_data_ai_index(self, data_ai_index):
        try:
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id, category_id, name, icon, data_ai_index, api_url, 
                       request_method, request_headers, request_body_template, response_path 
                FROM ai_models 
                WHERE data_ai_index = %s
            """, (data_ai_index,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error getting AI model: {e}")
            return None
        finally:
            self._close_if_owned()
    
    def get_ai_models_by_category_id(self, category_id):
        try:
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id, name, icon, data_ai_index, api_url,
                       request_method, request_headers, request_body_template, response_path 
                FROM ai_models 
                WHERE category_id = %s 
                ORDER BY id
            """, (category_id,))
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error getting AI models by category: {e}")
            return []
        finally:
            self._close_if_owned()
    
    def get_all_ai_models(self):
        try:
            self._ensure_connection()
            self.db.cursor.execute("""
                SELECT id, category_id, name, icon, data_ai_index, api_url,
                       request_method, request_headers, request_body_template, response_path 
                FROM ai_models 
                ORDER BY category_id, id
            """)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error getting all AI models: {e}")
            return []
        finally:
            self._close_if_owned()
    
    # -------------------------------------------------------------------------
    # 3.5. User Message Operations
    # -------------------------------------------------------------------------
    def insert_user_message(self, session_id, user_message, ai_response, ai_model_name):
        """Inserts a user message and its corresponding AI response into the database."""
        try:
            self._ensure_connection()
            # Basic handling for potentially None values
            session_id = session_id or "UNKNOWN"
            user_message = user_message or ""
            ai_response = ai_response or ""
            ai_model_name = ai_model_name or "UNKNOWN"

            self.db.cursor.execute("""
                INSERT INTO user_messages (session_id, user_message, ai_response, ai_model_name)
                VALUES (%s, %s, %s, %s)
            """, (session_id, user_message, ai_response, ai_model_name))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"Error inserting user message: {e}")
            # Consider logging the error instead of just printing
            raise # Re-raise after rollback attempt
        # Connection closing is handled by the context or _close_if_owned

    def get_all_user_messages(self, limit=100, offset=0):
        """Fetches user messages, ordered by timestamp descending."""
        try:
            self._ensure_connection()
            # Basic validation/sanitization for limit/offset
            limit = max(1, int(limit))
            offset = max(0, int(offset))
            query = """
                SELECT id, session_id, user_message, ai_response, ai_model_name, timestamp
                FROM user_messages
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """
            self.db.cursor.execute(query, (limit, offset))
            results = self.db.cursor.fetchall()
            return results
        except Error as e:
            print(f"Error getting all user messages: {e}")
            return []
        # Connection closing is handled by the context or _close_if_owned
    
    # -------------------------------------------------------------------------
    # 3.6. Data Seeding
    # -------------------------------------------------------------------------
    def seed_initial_data(self):
        try:
            self._ensure_connection()
            
            # General AI Category
            general_ai_category_name = "General AI"
            general_ai_category_icon = "bi-robot"
            
            # Insert category
            self.insert_ai_category(general_ai_category_name, general_ai_category_icon)
            print(f"Ensured category: {general_ai_category_name}")
            
            # Get the category ID
            category = self.get_ai_category_by_name(general_ai_category_name)
            if category:
                general_ai_category_id = category['id']
                
                # Gemini Model
                gemini_model_name = "Gemini Pro"
                gemini_model_icon = "bi-gem"
                gemini_model_data_ai_index = "5"
                gemini_model_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyACRnbM9cr02QfaPqUOUQH-Mr2ySBcuBo4"
                gemini_request_method = "POST"
                gemini_request_headers = '{"Content-Type": "application/json"}'
                gemini_request_body_template = '{"contents": [{"parts":[{"text": "$message"}]}]}'
                gemini_response_path = 'candidates[0].content.parts[0].text'
                
                # Insert model if it doesn't exist
                existing_model = self.get_ai_model_by_data_ai_index(gemini_model_data_ai_index)
                if not existing_model:
                    self.insert_ai_model(
                        general_ai_category_id, 
                        gemini_model_name, 
                        gemini_model_icon, 
                        gemini_model_data_ai_index, 
                        gemini_model_api_url,
                        gemini_request_method,
                        gemini_request_headers,
                        gemini_request_body_template,
                        gemini_response_path
                    )
                    print(f"Ensured model: {gemini_model_name}")
            else:
                print(f"Could not find or create category '{general_ai_category_name}' to add Gemini model.")
                
        except Error as e:
            print(f"Error during data seeding: {e}")
            if self.db.connection:
                self.db.connection.rollback()
        finally:
            self._close_if_owned()

# -----------------------------------------------------------------------------
# Legacy functions for backward compatibility
# -----------------------------------------------------------------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def initialize_database():
    db_conn = DatabaseConnection()
    try:
        db_conn.create_all_tables()
    except Exception as e:
        print(f"Error during database initialization: {e}")
    finally:
        db_conn.close()
