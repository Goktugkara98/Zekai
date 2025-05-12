from flask import Blueprint, render_template, request, jsonify
import requests # requests importu eklendi
import json
import os
from services.ai_model_service import get_ai_model_api_details, fetch_ai_categories_from_db # Birleşik import
from app.models.database import AIModelRepository # Veritabanı deposunu import et

main_bp = Blueprint('main_bp', __name__)

def generate_mock_response(user_message):
    """
    Generates a mock response for when the real API is unavailable.
    
    Args:
        user_message: The user's message to respond to
        
    Returns:
        A mock response string
    """
    # Create a simple mock response
    return f"This is a mock response to your message: '{user_message}'. The real AI service is currently unavailable."


def extract_response_by_path(response_json, path):
    """
    Extracts a value from a nested JSON object using a dot-notation path.
    For array indices, use the format 'key[index]'.
    
    Args:
        response_json: The JSON response to extract from
        path: The path to the value, e.g., 'candidates[0].content.parts[0].text'
        
    Returns:
        The extracted value or a default message if extraction fails
    """
    try:
        # Split the path by dots
        parts = path.split('.')
        result = response_json
        
        for part in parts:
            # Check if we have an array index notation
            if '[' in part and ']' in part:
                key, index_str = part.split('[', 1)
                index = int(index_str.split(']')[0])
                
                # Get the array by key, then the element by index
                if key:
                    result = result[key][index]
                else:
                    result = result[index]
            else:
                # Regular key
                result = result[part]
                
        return result
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error extracting response using path '{path}': {e}")
        return f"Error processing AI response: {str(e)}"
    except Exception as e:
        print(f"Unexpected error extracting response: {e}")
        return "An unexpected error occurred processing the AI response."


@main_bp.route('/')
def index():
    ai_categories = fetch_ai_categories_from_db()
    if not ai_categories:
        # Fallback or error message if data couldn't be fetched
        print("Warning: Could not fetch AI categories from the database. Using sample data.")
        # You could provide some default static data here if needed, or an error message
        # For now, let's use the previous sample data as a fallback for demonstration
        ai_categories = [
            {"name": "Error Fetching Categories", "icon": "bi-exclamation-triangle", "models": []}
        ]
    return render_template('index.html', ai_categories=ai_categories)


# YENİ CHAT API ROUTE'U
@main_bp.route('/api/chat/send', methods=['POST'])
def handle_chat_message():
    data = request.json
    user_message = data.get('message')
    ai_model_id = data.get('aiModelId')
    chat_id = data.get('chatId')
    conversation_history = data.get('history', []) # Konuşma geçmişini al, yoksa boş liste

    # --- History Normalization Start ---
    normalized_history = []
    for msg in conversation_history:
        role = msg.get('role')
        content = None
        # Try to extract content from 'content' key first
        if 'content' in msg:
            content = msg['content']
        # If not found, try extracting from 'parts[0].text' (Gemini format)
        elif 'parts' in msg and isinstance(msg['parts'], list) and len(msg['parts']) > 0 and 'text' in msg['parts'][0]:
            content = msg['parts'][0]['text']
        # Add other potential legacy formats here if needed
        
        # Only add message if role and content are valid
        if role and content is not None:
            normalized_history.append({'role': role, 'content': content})
        else:
            print(f"WARN: Skipping malformed history message: {msg}")
    # --- History Normalization End ---


    if not user_message:
        return jsonify({"error": "User message is missing"}), 400
    if not ai_model_id:
        return jsonify({"error": "AI Model ID is missing"}), 400

    print(f"Received message for AI Model {ai_model_id} (Chat ID: {chat_id}): {user_message}")
    if conversation_history:
        print(f"Received conversation history with {len(conversation_history)} messages.")

    # Gemini modeli için data_ai_index "5" olarak varsayıyoruz (database.py'deki gibi)
    GEMINI_MODEL_DATA_AI_INDEX = "5"

    try:
        # Get model details from database
        model_details = get_ai_model_api_details(ai_model_id)
        if not model_details or not model_details.get('api_url'):
            print(f"Error: Could not retrieve API details for model ID: {ai_model_id}")
            return jsonify({"error": f"Configuration not found for AI model ID: {ai_model_id}"}), 500 
            
        # Check if we should use the mock API (for testing or when real API is down)
        use_mock_api = os.environ.get('USE_MOCK_API', 'false').lower() == 'true'

        # Extract API details
        api_url = model_details.get('api_url')
        request_method = model_details.get('request_method', 'POST')
        
        # Parse request headers
        try:
            import json
            headers = json.loads(model_details.get('request_headers', '{"Content-Type": "application/json"}'))
        except json.JSONDecodeError as e:
            print(f"Error parsing request headers: {e}")
            headers = {"Content-Type": "application/json"}
        
        # Prepare request body using template
        request_body_template = model_details.get('request_body_template', '{"contents": [{"parts":[{"text": "$message"}]}]}')
        
        # --- Payload Construction Logic ---
        payload = None
        # Identify Gemini model (using a simple check on the default template for now)
        # TODO: A more robust way would be to add a flag to the database or check a specific part of the api_url
        is_gemini_model = (request_body_template == '{"contents": [{"parts":[{"text": "$message"}]}]}') 

        if is_gemini_model and conversation_history: # Special handling for Gemini with history, even if template is simple
            print("Handling Gemini model with history using manual payload construction.")
            gemini_contents_list = []
            for msg in normalized_history:
                gemini_contents_list.append({"role": msg['role'], "parts": [{"text": msg['content']}]})
            # Check if the last message in history is the same as the current user message
            # Avoid adding the current user message if it's already the last item in history
            if not normalized_history or normalized_history[-1].get('role') != 'user' or normalized_history[-1].get('content') != user_message:
                 gemini_contents_list.append({"role": "user", "parts": [{"text": user_message}]})
            else:
                 print("WARN: Current user message seems to be already included in the history received from frontend. Not adding it again for Gemini.")

            payload = {"contents": gemini_contents_list} # Construct payload directly
            print(f"Constructed payload for Gemini (manual history): {payload}")

        elif '"$messages"' in request_body_template: # OpenRouter String Replacement
            print("Template uses $messages placeholder (string replacement).")
            # Check if the last message in history is the same as the current user message
            if not normalized_history or normalized_history[-1].get('role') != 'user' or normalized_history[-1].get('content') != user_message:
                messages_list = normalized_history + [{"role": "user", "content": user_message}]
            else:
                print("WARN: Current user message seems to be already included in the history received from frontend. Not adding it again for OpenRouter (String).")
                messages_list = normalized_history # Use history as is

            messages_json_string = json.dumps(messages_list)
            final_payload_string = request_body_template.replace('"$messages"', messages_json_string)
            try:
                payload = json.loads(final_payload_string)
                print(f"Constructed payload with history (string replacement): {payload}")
            except json.JSONDecodeError as e:
                print(f"Error parsing final payload string after $messages replacement: {e}")
                return jsonify({"error": "Failed to construct payload with history"}), 500
        
        elif '$messages' in request_body_template: # OpenRouter Object Replacement (value is "$messages")
            print("Template uses $messages placeholder (object replacement).")
            # Check if the last message in history is the same as the current user message
            if not normalized_history or normalized_history[-1].get('role') != 'user' or normalized_history[-1].get('content') != user_message:
                messages_list = normalized_history + [{'role': 'user', 'content': user_message}]
            else:
                print("WARN: Current user message seems to be already included in the history received from frontend. Not adding it again for OpenRouter (Object).")
                messages_list = normalized_history # Use history as is
                
            try:
                payload_template = json.loads(request_body_template)
                payload = payload_template
                found_placeholder = False
                for key, value in payload.items():
                    if isinstance(value, str) and value == '$messages':
                        payload[key] = messages_list
                        found_placeholder = True
                        break
                if not found_placeholder:
                     print("Warning: $messages placeholder logic failed. Using basic fallback.")
                     payload = {"messages": messages_list} 
                print(f"Constructed payload with history (object replacement): {payload}")
            except json.JSONDecodeError as e:
                print(f"Error parsing request body template with $messages: {e}")
                return jsonify({"error": "Invalid request body template format"}), 500

        elif '$message' in request_body_template: # Fallback for simple $message placeholder (used by Gemini if no history or handled above)
            print("Template uses $message placeholder.")
            try:
                # This will now also apply to Gemini when the special history case isn't met
                payload = json.loads(request_body_template.replace('$message', user_message))
                print(f"Constructed payload with single message: {payload}")
            except json.JSONDecodeError as e:
                print(f"Error parsing request body template with $message: {e}")
                payload = {"contents": [{"parts":[{"text": user_message}]}]} # Default Gemini-like fallback
                print(f"Using fallback payload for single message: {payload}")
        else:
            # Default payload if no known placeholder is found 
            print("No known placeholder found in template. Using default structure.")
            payload = {"contents": [{"parts":[{"text": user_message}]}]}
            print(f"Constructed default payload: {payload}")

        if payload is None:
             print("Error: Payload could not be constructed.")
             return jsonify({"error": "Failed to construct request payload"}), 500
        
        # Check if we should use the mock API
        if use_mock_api:
            print("Using mock API as requested by environment variable...")
            ai_response_text = generate_mock_response(user_message)
        else:
            # Make the real API request
            print(f"Sending request to API: {api_url} with method: {request_method}, headers: {headers}, payload: {payload}")
            
            try:
                if request_method.upper() == 'POST':
                    response = requests.post(api_url, json=payload, headers=headers)
                elif request_method.upper() == 'GET':
                    response = requests.get(api_url, params=payload, headers=headers)
                else:
                    return jsonify({"error": f"Unsupported request method: {request_method}"}), 400
                    
                response.raise_for_status()
                response_json = response.json()
                print(f"Received response from API: {response_json}")
                
                # Extract response using the response path
                response_path = model_details.get('response_path', 'candidates[0].content.parts[0].text')
                ai_response_text = extract_response_by_path(response_json, response_path)
            except Exception as api_err:
                print(f"Error with real API, falling back to mock: {api_err}")
                ai_response_text = generate_mock_response(user_message)

        # Prepare the final response structure
        response_data = {"response": ai_response_text, "chatId": chat_id}

        # --- Log to Database ---
        try:
            ai_repo = AIModelRepository() # Assumes default constructor works
            ai_repo.insert_user_message(
                session_id=chat_id, # Using chat_id as session identifier
                user_message=user_message,
                ai_response=ai_response_text,
                ai_model_name=model_details.get('name', 'Unknown Model') if model_details else 'Config Error Model'
            )
            print(f"Successfully logged message for chat {chat_id} to database.")
        except Exception as db_err:
            print(f"DATABASE LOGGING ERROR for chat {chat_id}: {db_err}")
            # Decide if failure to log should prevent the user response. Probably not.
        # --- End Log to Database ---

        return jsonify(response_data)

    except requests.exceptions.HTTPError as http_err:
        error_response = http_err.response.text if http_err.response else 'No response text available'
        print(f"API HTTP error: {http_err} - Response status: {http_err.response.status_code if http_err.response else 'N/A'} - Response text: {error_response}")
        print(f"Request URL: {api_url}")
        print(f"Request method: {request_method}")
        print(f"Request headers: {headers}")
        print(f"Request payload: {payload}")
        
        # Try to use mock API as fallback
        try:
            print("Attempting to use mock API as fallback...")
            mock_response = generate_mock_response(user_message)
            return jsonify({"aiResponse": mock_response, "usedMockApi": True})
        except Exception as mock_err:
            print(f"Mock API fallback also failed: {mock_err}")
            ai_response = f"Error calling external API: {str(http_err)}" # Define ai_response here for logging

            # --- Log Error to Database ---
            try:
                ai_repo = AIModelRepository()
                # Try to get model name even on error if model_details was fetched earlier
                model_name = model_details.get('name', 'Unknown Model') if 'model_details' in locals() and model_details else 'Config Error Model'
                ai_repo.insert_user_message(
                    session_id=chat_id,
                    user_message=user_message,
                    ai_response=ai_response, # Log the error message
                    ai_model_name=model_name
                )
                print(f"Successfully logged ERROR message for chat {chat_id} to database.")
            except Exception as db_err:
                print(f"DATABASE LOGGING ERROR (during API error) for chat {chat_id}: {db_err}")
            # --- End Log Error to Database ---

            return jsonify({"error": ai_response}), 500 # Return the error message

    except requests.exceptions.RequestException as req_err: 
        print(f"API Request error: {req_err}")
        print(f"Request URL: {api_url}")
        print(f"Request method: {request_method}")
        print(f"Request headers: {headers}")
        print(f"Request payload: {payload}")
        
        ai_response = f"Failed to communicate with AI service: {str(req_err)}" # Define ai_response here for logging

        # --- Log Error to Database ---
        try:
            ai_repo = AIModelRepository()
            # Try to get model name even on error if model_details was fetched earlier
            model_name = model_details.get('name', 'Unknown Model') if 'model_details' in locals() and model_details else 'Config Error Model'
            ai_repo.insert_user_message(
                session_id=chat_id,
                user_message=user_message,
                ai_response=ai_response, # Log the error message
                ai_model_name=model_name
            )
            print(f"Successfully logged ERROR message for chat {chat_id} to database.")
        except Exception as db_err:
            print(f"DATABASE LOGGING ERROR (during API error) for chat {chat_id}: {db_err}")
        # --- End Log Error to Database ---

        return jsonify({"error": ai_response}), 500 # Return the error message

    except (KeyError, IndexError) as e: 
        print(f"Error parsing ACTUAL Gemini API response: {e} - JSON response might not be available or was malformed.")
        ai_response = f"Error processing AI response format: {str(e)}" # Define ai_response here for logging

        # --- Log Error to Database ---
        try:
            ai_repo = AIModelRepository()
            # Try to get model name even on error if model_details was fetched earlier
            model_name = model_details.get('name', 'Unknown Model') if 'model_details' in locals() and model_details else 'Config Error Model'
            ai_repo.insert_user_message(
                session_id=chat_id,
                user_message=user_message,
                ai_response=ai_response, # Log the error message
                ai_model_name=model_name
            )
            print(f"Successfully logged ERROR message for chat {chat_id} to database.")
        except Exception as db_err:
            print(f"DATABASE LOGGING ERROR (during API error) for chat {chat_id}: {db_err}")
        # --- End Log Error to Database ---

        return jsonify({"error": ai_response}), 500 # Return the error message

    except Exception as e: 
        print(f"An unexpected error occurred in chat handler: {e}")
        ai_response = f"An unexpected error occurred: {str(e)}" # Define ai_response here for logging

        # --- Log Error to Database ---
        try:
            ai_repo = AIModelRepository()
            # Try to get model name even on error if model_details was fetched earlier
            model_name = model_details.get('name', 'Unknown Model') if 'model_details' in locals() and model_details else 'Config Error Model'
            ai_repo.insert_user_message(
                session_id=chat_id,
                user_message=user_message,
                ai_response=ai_response, # Log the error message
                ai_model_name=model_name
            )
            print(f"Successfully logged UNEXPECTED ERROR message for chat {chat_id} to database.")
        except Exception as db_err:
            print(f"DATABASE LOGGING ERROR (during unexpected error) for chat {chat_id}: {db_err}")
        # --- End Log Error to Database ---

        return jsonify({"error": ai_response}), 500 # Return the error message

# YENİ SAHTE GEMINI API ROTASI
@main_bp.route('/mock_gemini_api/v1beta/models/gemini-2.0-flash:generateContent', methods=['POST'])
def mock_gemini_generate_content():
    # API anahtarını URL'den alabiliriz (isteğe bağlı, şimdilik kullanmıyoruz)
    # api_key = request.args.get('key') 
    # print(f"Mock Gemini API called with key: {api_key}")

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    
    try:
        # Gelen payload'dan metni ayıkla
        user_text = data["contents"][0]["parts"][0]["text"]
        
        # Sahte bir yanıt oluştur
        mock_response_text = f"This is a MOCK response from Gemini (gemini-2.0-flash) to your message: '{user_text}'"
        
        gemini_like_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": mock_response_text}
                        ],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0,
                    "safetyRatings": [
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
                    ]
                }
            ],
            "promptFeedback": {
                "safetyRatings": [
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
                ]
            }
        }
        return jsonify(gemini_like_response)

    except (KeyError, IndexError, TypeError) as e:
        print(f"Mock Gemini API: Invalid payload format - {e}")
        return jsonify({"error": "Invalid payload format. Expected {'contents': [{'parts':[{'text': '...'}]}]}"}), 400
    except Exception as e:
        print(f"Mock Gemini API: An unexpected error occurred - {e}")
        return jsonify({"error": "An unexpected error occurred in mock Gemini API."}), 500
