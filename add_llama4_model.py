from app.models.database import AIModelRepository, DatabaseConnection
import json

def add_llama4_model():
    """Add Llama-4-Maverick model from OpenRouter to the database."""
    try:
        # Create a database connection that we'll manage manually
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # Create repository with our managed connection
        repo = AIModelRepository(db_conn)
        
        # Get the General AI category ID (assuming it exists)
        categories = repo.get_all_ai_categories()
        general_ai_category_id = None
        
        for category in categories:
            if category['name'] == 'General AI':
                general_ai_category_id = category['id']
                break
        
        if not general_ai_category_id:
            print("Error: 'General AI' category not found. Creating it...")
            repo.insert_ai_category('General AI', 'bi-robot')
            categories = repo.get_all_ai_categories()
            for category in categories:
                if category['name'] == 'General AI':
                    general_ai_category_id = category['id']
                    break
        
        # Check if model already exists
        model_data_ai_index = 'llama4-maverick'
        existing_model = repo.get_ai_model_by_data_ai_index(model_data_ai_index)
        
        if existing_model:
            print(f"Model with data_ai_index '{model_data_ai_index}' already exists: {existing_model}")
            return
            
        # OpenRouter Llama-4-Maverick Model configuration
        model_name = "Llama-4 Maverick (Vision)"
        model_icon = "bi-eye"
        model_api_url = "https://openrouter.ai/api/v1/chat/completions"
        model_request_method = "POST"
        
        # Headers configuration - replace with your actual API key
        headers = {
            "Authorization": "Bearer <OPENROUTER_API_KEY>",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://zekai.app",
            "X-Title": "Zekai AI"
        }
        model_request_headers = json.dumps(headers)
        
        # Request body template - Note: This is a special template for vision models
        # $message will be replaced with the user's text message
        # For image processing, we'll need to modify the frontend to handle image uploads
        request_body = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "$message"
                        }
                        # Note: Image content would need to be added dynamically
                        # by the frontend or backend when an image is uploaded
                    ]
                }
            ]
        }
        model_request_body_template = json.dumps(request_body)
        
        # Response path for extracting the AI's response
        model_response_path = 'choices[0].message.content'
        
        # Insert the model
        repo.insert_ai_model(
            general_ai_category_id,
            model_name,
            model_icon,
            model_data_ai_index,
            model_api_url,
            model_request_method,
            model_request_headers,
            model_request_body_template,
            model_response_path
        )
        
        # Verify the insertion
        new_model = repo.get_ai_model_by_data_ai_index(model_data_ai_index)
        print(f"Llama-4-Maverick model added successfully: {new_model}")
        print("NOTE: This model supports vision capabilities, but the current system only supports text inputs.")
        print("To fully utilize this model's capabilities, you'll need to modify the frontend and backend to handle image uploads.")
        
    except Exception as e:
        print(f"Error adding Llama-4-Maverick model: {e}")
    finally:
        # Make sure to close the database connection
        if 'db_conn' in locals() and db_conn:
            db_conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    add_llama4_model()
