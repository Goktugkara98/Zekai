import mysql.connector
from app.models.database import get_db_connection # Veritabanı bağlantı fonksiyonunu import ediyoruz
import mysql.connector # fetch_ai_categories_from_db için eklendi

def get_ai_model_api_details(data_ai_index):
    conn = get_db_connection()
    if not conn:
        print("Service Layer: Database connection failed.") # Servis katmanında loglama
        return None 

    cursor = conn.cursor(dictionary=True)
    model_details = None

    try:
        print(f"Service Layer: Fetching AI model details for data_ai_index: {data_ai_index}") # Servis katmanında loglama
        cursor.execute("""
            SELECT name, api_url, data_ai_index
            FROM ai_models 
            WHERE data_ai_index = %s
        """, (data_ai_index,))
        model_details = cursor.fetchone() 
        if model_details:
            print(f"Service Layer: Found model details: {model_details}") # Servis katmanında loglama
        else:
            print(f"Service Layer: No model found for data_ai_index: {data_ai_index}") # Servis katmanında loglama
            
    except mysql.connector.Error as err:
        print(f"Service Layer: Error fetching AI model details from MySQL: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return model_details

# Gelecekte buraya AI modelleriyle ilgili başka servis fonksiyonları da eklenebilir.
# Örneğin, tüm modelleri listeleme, model ekleme/güncelleme vb.


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
                SELECT name, icon, data_ai_index, api_url 
                FROM ai_models 
                WHERE category_id = %s 
                ORDER BY id
            """, (category["id"],))
            models = cursor.fetchall()

            for model in models:
                category_dict["models"].append({
                    "name": model["name"],
                    "icon": model["icon"],
                    "data_ai_index": model["data_ai_index"],
                    "api_url": model["api_url"]
                })
            categories_data.append(category_dict)
            
    except mysql.connector.Error as err:
        print(f"Service Layer: Error fetching AI categories from MySQL: {err}") # Log mesajı güncellendi
        # Handle error appropriately
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return categories_data
