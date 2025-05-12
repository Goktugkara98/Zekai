from app.models.database import AIModelRepository, DatabaseConnection
import json

def add_deephermes_model():
    """Add DeepHermes model from OpenRouter to the database."""
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
        model_data_ai_index = 'deephermes-3-mistral'
        existing_model = repo.get_ai_model_by_data_ai_index(model_data_ai_index)
        
        if existing_model:
            print(f"Model with data_ai_index '{model_data_ai_index}' already exists: {existing_model}")
            return
            
        # OpenRouter DeepHermes Model configuration
        model_name = "DeepHermes 3 Mistral"
        model_icon = "bi-chat-dots"
        model_api_url = "https://openrouter.ai/api/v1/chat/completions"
        model_request_method = "POST"
        
        # Headers configuration
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "OpenRouter"
        }
        model_request_headers = json.dumps(headers)
        
        # Request body template
        request_body = {
            "model": "nousresearch/deephermes-3-mistral-24b-preview:free",
            "messages": [
                {
                    "role": "user",
                    "content": "$message"
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
        print(f"DeepHermes model added successfully: {new_model}")
        
    except Exception as e:
        print(f"Error adding DeepHermes model: {e}")
    finally:
        # Make sure to close the database connection
        if 'db_conn' in locals() and db_conn:
            db_conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    add_deephermes_model()
