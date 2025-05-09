from flask import Blueprint, render_template, request, jsonify
import requests # requests importu eklendi
from services.ai_model_service import get_ai_model_api_details, fetch_ai_categories_from_db # Birleşik import

main_bp = Blueprint('main_bp', __name__)

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
    user_message = data.get('message')
    ai_model_id = data.get('aiModelId')
    chat_id = data.get('chatId')
    conversation_history = data.get('history', []) # Konuşma geçmişini al, yoksa boş liste

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
        if ai_model_id == GEMINI_MODEL_DATA_AI_INDEX:
            model_details = get_ai_model_api_details(ai_model_id)
            if not model_details or not model_details.get('api_url'):
                print(f"Error: Could not retrieve API key for model ID: {ai_model_id}")
                return jsonify({"error": f"Configuration not found for AI model ID: {ai_model_id}"}), 500 

            gemini_api_key = model_details.get('api_url')
            # GERÇEK GEMINI API URL'i
            actual_gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent?key={gemini_api_key}"
            
            # Gemini API payload'unu oluştur
            if conversation_history:
                # Eğer konuşma geçmişi varsa, onu kullan (en son mesaj zaten history içinde)
                payload = {"contents": conversation_history}
            else:
                # Geriye dönük uyumluluk veya history yoksa, sadece son mesajı kullan
                payload = {
                    "contents": [{
                        "parts":[{"text": user_message}]
                    }]
                }
            
            headers = {
                'Content-Type': 'application/json'
            }

            print(f"Sending request to ACTUAL Gemini API: {actual_gemini_url} with payload: {payload}")
            response = requests.post(actual_gemini_url, json=payload, headers=headers)
            response.raise_for_status()
            
            response_json = response.json()
            print(f"Received response from ACTUAL Gemini API: {response_json}")
            
            ai_response_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            
        else:
            simulated_ai_name = f"Simulated AI for {ai_model_id}"
            ai_response_text = f"This is a simulated response from {simulated_ai_name} to: '{user_message}'"
            if "trigger error" in user_message.lower():
                pass 

        return jsonify({"aiResponse": ai_response_text})

    except requests.exceptions.HTTPError as http_err:
        print(f"ACTUAL Gemini API HTTP error: {http_err} - Response text: {http_err.response.text if http_err.response else 'No response text available'}")
        return jsonify({"error": f"Error communicating with AI service: {str(http_err)}"}), 503
    except requests.exceptions.RequestException as req_err: 
        print(f"ACTUAL Gemini API Request error: {req_err}")
        return jsonify({"error": f"Failed to communicate with AI service: {str(req_err)}"}), 503
    except (KeyError, IndexError) as e: 
        print(f"Error parsing ACTUAL Gemini API response: {e} - JSON response might not be available or was malformed.")
        return jsonify({"error": "Error processing AI response format."}), 500
    except Exception as e: 
        print(f"An unexpected error occurred in handle_chat_message: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

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
