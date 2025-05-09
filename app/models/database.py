import mysql.connector
from app.config import DB_CONFIG # DB_CONFIG'i app.config'den import et

# IMPORTANT: Update these with your actual MySQL connection details
# DB_CONFIG = { # Bu blok kaldırılacak
#     'host': 'localhost',
#     'user': 'root',  # Replace with your MySQL username
#     'password': '',  # Replace with your MySQL password
#     'database': 'zekai'  # Replace with your database name
# }

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        # In a real application, you might want to handle this more gracefully
        return None

def initialize_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )

        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # SQL to create ai_categories table
        create_categories_table_sql = """
        CREATE TABLE IF NOT EXISTS ai_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            icon VARCHAR(255)
        );
        """
        cursor.execute(create_categories_table_sql)
        print("Table 'ai_categories' ensured.")

        # SQL to create ai_models table
        create_models_table_sql = """
        CREATE TABLE IF NOT EXISTS ai_models (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT,
            name VARCHAR(255) NOT NULL,
            icon VARCHAR(255),
            data_ai_index VARCHAR(50) UNIQUE NOT NULL,
            api_url VARCHAR(255) NOT NULL,
            FOREIGN KEY (category_id) REFERENCES ai_categories(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_models_table_sql)
        print("Table 'ai_models' ensured.")
        try:
            print("DEBUG: Describing ai_models table schema after creation...")
            cursor.execute("DESCRIBE ai_models;")
            schema = cursor.fetchall()
            print(f"DEBUG: Schema for ai_models: {schema}")
        except Exception as e:
            print(f"DEBUG: Error describing ai_models: {e}")

        # --- Add default/initial data ---
        # General AI Category
        general_ai_category_name = "General AI"
        general_ai_category_icon = "bi-robot"
        cursor.execute("""
            INSERT IGNORE INTO ai_categories (name, icon) 
            VALUES (%s, %s)
        """, (general_ai_category_name, general_ai_category_icon))
        conn.commit() # Commit after insert
        print(f"Ensured category: {general_ai_category_name}")

        # Get the ID of the General AI category (or the one just inserted)
        cursor.execute("SELECT id FROM ai_categories WHERE name = %s", (general_ai_category_name,))
        category_row = cursor.fetchone()
        if category_row:
            general_ai_category_id = category_row['id']

            # Gemini Model
            gemini_model_name = "Gemini 2.0 Flash"
            gemini_model_icon = "bi-gem"
            gemini_model_data_ai_index = "5"
            gemini_model_api_url = "AIzaSyACRnbM9cr02QfaPqUOUQH-Mr2ySBcuBo4"
            print(f"DEBUG: Attempting to insert into ai_models. Category ID: {general_ai_category_id}, Name: {gemini_model_name}, Icon: {gemini_model_icon}, Index: {gemini_model_data_ai_index}, API URL: {gemini_model_api_url}")
            cursor.execute("""
                INSERT IGNORE INTO ai_models (category_id, name, icon, data_ai_index, api_url) 
                VALUES (%s, %s, %s, %s, %s)
            """, (general_ai_category_id, gemini_model_name, gemini_model_icon, gemini_model_data_ai_index, gemini_model_api_url))
            conn.commit() # Commit after insert
            print(f"Ensured model: {gemini_model_name} under {general_ai_category_name}")
        else:
            print(f"Could not find or create category '{general_ai_category_name}' to add Gemini model.")

    except mysql.connector.Error as err:
        print(f"Error during database initialization or data seeding: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
