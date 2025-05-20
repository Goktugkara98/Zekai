# app/services/openrouter_ai_service.py
from app.services.base_ai_service import BaseAIService
from typing import Dict, Any, Optional, List, Tuple
import requests
import json

class OpenRouterAIService(BaseAIService):
    """
    AI Service implementation for OpenRouter.
    (This is a placeholder and needs to be implemented)
    """

    def handle_chat(self,
                    user_message: Optional[str],
                    conversation_history: List[Dict[str, str]],
                    model_details: Dict[str, Any],
                    chat_id: str,
                    use_mock_api: bool
                   ) -> Tuple[str, Dict[str, Any], int, Dict[str, Any], str]:

        model_name_for_log = model_details.get('name', 'OpenRouter Model Misconfigured')
        request_payload_for_log: Dict[str, Any] = {}
        response_json_for_log: Dict[str, Any] = {}
        
        if use_mock_api:
            mock_msg = user_message if user_message else "a message from history"
            ai_response_text = self._generate_mock_response(mock_msg, model_name_for_log)
            response_json_for_log = {"mock_response": True, "choices": [{"message": {"content": ai_response_text}}]}
            return ai_response_text, response_json_for_log, 200, {}, model_name_for_log

        # --- TODO: Implement OpenRouter API Interaction Logic ---
        # 1. Get api_url, api_key from model_details
        #    api_key might be expected in headers for OpenRouter: e.g., "Authorization": f"Bearer {api_key}"
        api_url = model_details.get('api_url') # e.g., "https://openrouter.ai/api/v1/chat/completions"
        api_key = model_details.get('api_key')
        
        if not api_url or not api_key:
            return "Config error: OpenRouter API URL or Key missing.", {}, 500, {}, model_name_for_log

        # 2. Prepare headers (Content-Type, Authorization)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
            # Potentially "HTTP-Referer": your_site_url (if required by OpenRouter)
            # "X-Title": your_app_name (if required by OpenRouter)
        }
        custom_headers_str = model_details.get('request_headers')
        if custom_headers_str:
            try:
                custom_headers = json.loads(custom_headers_str) if isinstance(custom_headers_str, str) else custom_headers_str
                if isinstance(custom_headers, dict):
                    headers.update(custom_headers)
            except json.JSONDecodeError:
                pass # Ignore malformed custom headers

        # 3. Prepare request_body_template and fill it
        #    OpenRouter expects a 'model' field (e.g., "mistralai/mistral-7b-instruct") and 'messages'
        #    Ensure your model_details.request_body_template is set up for this.
        #    Example template: {"model": "model-name-from-db-or-fixed", "messages": "$messages"}
        #    The 'model' field in the payload should be the specific OpenRouter model identifier.
        #    You might need to store this identifier in your database alongside your internal model name.
        
        request_body_template_raw = model_details.get('request_body_template')
        request_body_template_str = json.dumps(request_body_template_raw) if isinstance(request_body_template_raw, dict) \
                                    else (request_body_template_raw if isinstance(request_body_template_raw, str) else None)

        if not request_body_template_str:
            return "Config error: Request body template missing for OpenRouter.", {}, 500, {}, model_name_for_log
        
        final_history_for_payload = list(conversation_history)
        current_turn_user_message_text = user_message
        if user_message:
            final_history_for_payload.append({'role': 'user', 'content': user_message})
        elif final_history_for_payload and final_history_for_payload[-1].get('role') == 'user':
            current_turn_user_message_text = final_history_for_payload[-1].get('content')

        try:
            request_payload_for_log = self._fill_payload_template(
                request_body_template_str,
                final_history_for_payload,
                current_turn_user_message_text
            )
            # OpenRouter might require the model name in the payload, ensure template accommodates this.
            # e.g. if template is {"model": "$model_identifier", "messages": "$messages"}
            # you'd need to replace $model_identifier with actual model name for OpenRouter
            # This might need an adjustment in _fill_payload_template or specific logic here.
            # For now, assuming template directly includes the model or it's handled by _fill_payload_template.

        except ValueError as e:
             return f"OpenRouter Config error: {str(e)}", {}, 500, {}, model_name_for_log


        # 4. Make the HTTP POST request
        try:
            api_http_response = requests.post(api_url, json=request_payload_for_log, headers=headers, timeout=45)
            api_status_code = api_http_response.status_code
            api_http_response.raise_for_status()
            
            # Store the response text to avoid reading it multiple times
            response_text = api_http_response.text
            response_json_for_log = json.loads(response_text)

            # 5. Extract the response text using response_path
            #    e.g., for OpenRouter: "choices.0.message.content"
            response_path = model_details.get('response_path', "choices.0.message.content")
            ai_response_text = str(self._extract_response_by_path(response_json_for_log, response_path))

            if "Response format error:" in ai_response_text:
                 if api_status_code < 300: api_status_code = 502 # Bad Gateway
            elif ai_response_text == "None" or not ai_response_text: # Path led nowhere or empty response
                 ai_response_text = "OpenRouter: Could not extract meaningful response using configured path."
                 if api_status_code < 300: api_status_code = 204 # No Content

            return ai_response_text, response_json_for_log, api_status_code, request_payload_for_log, model_name_for_log

        except requests.exceptions.HTTPError as http_err:
            # Safely get the response text
            try:
                raw_text = http_err.response.text if http_err.response else "N/A"
                status_code = http_err.response.status_code if http_err.response else 500
            except Exception:
                raw_text = "Could not read error response text"
                status_code = 500
                
            err_msg = f"OpenRouter API Error (HTTP {status_code}): {raw_text[:150]}"
            return err_msg, {"error": raw_text}, status_code, request_payload_for_log, model_name_for_log
        except requests.exceptions.RequestException as req_err:
            err_msg = f"OpenRouter connection error: {str(req_err)}"
            return err_msg, {"error": str(req_err)}, 503, request_payload_for_log, model_name_for_log
        except Exception as e:
            err_msg = f"Unexpected error with OpenRouter service: {str(e)}"
            return err_msg, {"error": str(e)}, 500, request_payload_for_log, model_name_for_log
        # --- End of OpenRouter Implementation Placeholder ---