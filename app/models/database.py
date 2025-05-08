import mysql.connector

# IMPORTANT: Update these with your actual MySQL connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'zekai'  # Replace with your database name
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        # In a real application, you might want to handle this more gracefully
        return None

def fetch_ai_categories_from_db():
    conn = get_db_connection()
    if not conn:
        return [] # Return empty list if connection failed

    cursor = conn.cursor(dictionary=True)
    categories_data = []

    try:
        # Fetch all categories
        cursor.execute("SELECT id, name, icon FROM ai_categories ORDER BY id")
        categories = cursor.fetchall()

        for category in categories:
            category_dict = {
                "name": category["name"],
                "icon": category["icon"],
                "models": []
            }

            # Fetch models for the current category
            cursor.execute("""
                SELECT name, icon, data_ai_index 
                FROM ai_models 
                WHERE category_id = %s 
                ORDER BY id
            """, (category["id"],))
            models = cursor.fetchall()

            for model in models:
                category_dict["models"].append({
                    "name": model["name"],
                    "icon": model["icon"],
                    "data_ai_index": model["data_ai_index"]
                })
            categories_data.append(category_dict)
            
    except mysql.connector.Error as err:
        print(f"Error fetching data from MySQL: {err}")
        # Handle error appropriately
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return categories_data

def initialize_database():
    try:
        # Connect to the MySQL server (without specifying a database initially to check/create it)
        # However, for simplicity in this step, we'll assume the database 'zekai' exists
        # and we're just ensuring tables are created.
        # A more robust solution would create the database if it doesn't exist.
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
            # database=DB_CONFIG['database'] # Connect without specific DB first to create it
        )
        cursor = conn.cursor(dictionary=True)
        
        # Create database if it doesn't exist
        # cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        # print(f"Database {DB_CONFIG['database']} ensured.")
        # conn.database = DB_CONFIG['database'] # Switch to the database
        
        # For now, let's assume the database 'zekai' is created and we connect directly.
        # If you face issues with 'zekai' DB not existing, uncomment above and adjust.
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
            FOREIGN KEY (category_id) REFERENCES ai_categories(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_models_table_sql)
        print("Table 'ai_models' ensured.")

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
            cursor.execute("""
                INSERT IGNORE INTO ai_models (category_id, name, icon, data_ai_index) 
                VALUES (%s, %s, %s, %s)
            """, (general_ai_category_id, gemini_model_name, gemini_model_icon, gemini_model_data_ai_index))
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
