import mysql.connector
from models.database import get_db_connection # Veritabanı bağlantı fonksiyonunu import ediyoruz

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
