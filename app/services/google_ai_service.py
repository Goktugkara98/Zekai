# app/services/google_ai_service.py
from app.services.base_ai_service import BaseAIService
from typing import Dict, Any, Optional, List, Tuple
import requests
import json
import os

class GoogleAIService(BaseAIService):
    """
    AI Service implementation for Google AI models (e.g., Gemini).
    """

    def handle_chat(self,
                    user_message: Optional[str],
                    conversation_history: List[Dict[str, str]],
                    model_details: Dict[str, Any],
                    chat_id: str, # chat_id is not directly used by the service but passed for consistency
                    use_mock_api: bool
                   ) -> Tuple[str, Dict[str, Any], int, Dict[str, Any], str]:
        """
        Handles chat interaction with Google AI.
        """
        ai_response_text = "Response could not be obtained."
        model_name_for_log = model_details.get('name', 'Google Model Misconfigured')
        request_payload_for_log: Dict[str, Any] = {}
        response_json_for_log: Dict[str, Any] = {}
        api_status_code = 500

        api_url = model_details.get('api_url')
        api_key = model_details.get('api_key')

        if not api_url:
            return "Configuration error: API URL missing for Google model.", {}, 500, {}, model_name_for_log

        # Append API key to URL for Google's typical pattern
        if api_key and 'generativelanguage.googleapis.com' in api_url:
            api_url = f"{api_url}{'&' if '?' in api_url else '?'}key={api_key}"

        request_method = model_details.get('request_method', 'POST').upper()
        response_path = model_details.get('response_path') # e.g., "candidates.0.content.parts.0.text"
        
        headers_str = model_details.get('request_headers')
        headers: Dict[str, str] = {}
        if headers_str:
            try:
                if isinstance(headers_str, str): headers = json.loads(headers_str)
                elif isinstance(headers_str, dict): headers = headers_str
                if not isinstance(headers, dict): headers = {}
            except json.JSONDecodeError:
                headers = {} # Default to empty if malformed
        
        if not headers.get("Content-Type") and request_method == 'POST':
             headers["Content-Type"] = "application/json" # Default for POST

        request_body_template_raw = model_details.get('request_body_template')
        request_body_template_str = json.dumps(request_body_template_raw) if isinstance(request_body_template_raw, dict) \
                                    else (request_body_template_raw if isinstance(request_body_template_raw, str) else None)

        if not request_body_template_str:
            return "Configuration error: Request body template missing for Google model.", {}, 500, {}, model_name_for_log

        final_history_for_payload = list(conversation_history) # Ensure a mutable copy
        current_turn_user_message_text = user_message

        if user_message:
            # Ensure the current user message is the last 'user' turn in the history for the payload
            current_turn_user_message_obj = {'role': 'user', 'content': user_message}
            # Add if not already the last message or if history is empty
            if not final_history_for_payload or final_history_for_payload[-1] != current_turn_user_message_obj:
                 final_history_for_payload.append(current_turn_user_message_obj)
        elif final_history_for_payload:
            # If no new user_message, the last message in history (if 'user') is considered current
            for i in range(len(final_history_for_payload) - 1, -1, -1):
                if final_history_for_payload[i].get('role') == 'user':
                    current_turn_user_message_text = final_history_for_payload[i].get('content')
                    break
        
        try:
            request_payload_for_log = self._fill_payload_template(
                request_body_template_str,
                final_history_for_payload, # Send the complete history including current turn
                current_turn_user_message_text # This is the $message or {user_prompt}
            )
        except ValueError as e:
             return f"Configuration error: {str(e)}", {}, 500, {}, model_name_for_log


        if use_mock_api:
            ai_response_text = self._generate_mock_response(
                current_turn_user_message_text if current_turn_user_message_text else "a message from history",
                model_name_for_log
            )
            # Mimic a typical Google Gemini response structure for the mock
            response_json_for_log = {
                "mock_response": True,
                "candidates": [{"content": {"parts": [{"text": ai_response_text}], "role": "model"}}]
            }
            api_status_code = 200
        else:
            try:
                api_http_response = None
                if request_method == 'POST':
                    api_http_response = requests.post(api_url, json=request_payload_for_log, headers=headers, timeout=30)
                elif request_method == 'GET': # Though less common for chat
                    api_http_response = requests.get(api_url, params=request_payload_for_log, headers=headers, timeout=30)
                else:
                    return f"Unsupported request method: {request_method}", {}, 400, request_payload_for_log, model_name_for_log

                api_status_code = api_http_response.status_code
                api_http_response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

                # Store the response text to avoid reading it multiple times
                response_text = api_http_response.text
                
                try:
                    response_json_for_log = json.loads(response_text)
                except json.JSONDecodeError:
                    response_json_for_log = {"error": "API response not valid JSON", "raw_response": response_text}
                    ai_response_text = "API response was not valid JSON."
                    if api_status_code < 300: api_status_code = 502 # Bad Gateway if parsing failed on seemingly OK response
                
                if response_path and isinstance(response_json_for_log, dict):
                    extracted_value = self._extract_response_by_path(response_json_for_log, response_path)
                    if isinstance(extracted_value, str) and "Response format error:" in extracted_value:
                        ai_response_text = extracted_value # Error message from extractor
                        if api_status_code < 300: api_status_code = 502
                    elif extracted_value is not None:
                        ai_response_text = str(extracted_value)
                    else: # Path given, but no value found or path was incorrect for the structure
                        ai_response_text = "Could not extract meaningful response using configured path."
                        if api_status_code < 300: api_status_code = 204 # No Content if path led nowhere
                elif isinstance(response_json_for_log, dict) and not response_path: # No path, return full JSON string
                    ai_response_text = json.dumps(response_json_for_log, ensure_ascii=False)
                elif not isinstance(response_json_for_log, dict) and not response_path: # Not a dict, no path
                     ai_response_text = str(response_json_for_log)
                elif api_status_code >= 300 and ai_response_text == "Response could not be obtained.": # Error and no specific message yet
                     ai_response_text = f"API Error: Status {api_status_code}. Raw: {response_text[:100]}"


            except requests.exceptions.HTTPError as http_err:
                # Safely get the response text
                try:
                    raw_response_text = http_err.response.text if http_err.response else "No content in error response"
                except Exception:
                    raw_response_text = "Could not read error response text"
                ai_response_text = f"AI service error (HTTP {api_status_code}). Details: {raw_response_text[:150]}"
                response_json_for_log = {"error_message_from_api": ai_response_text, "status_code": api_status_code, "raw_error_response": raw_response_text}
            except requests.exceptions.RequestException as req_err: # Timeout, ConnectionError, etc.
                api_status_code = 503 # Service Unavailable
                ai_response_text = f"Could not reach AI service: {str(req_err)}"
                response_json_for_log = {"error_message_internal": ai_response_text, "status_code": api_status_code}
            except Exception as e_inner_api: # Other unexpected errors during API call
                api_status_code = 500
                ai_response_text = f"Unexpected error processing AI request: {str(e_inner_api)}"
                response_json_for_log = {"error_message_internal": ai_response_text, "status_code": api_status_code}
                
        return ai_response_text, response_json_for_log, api_status_code, request_payload_for_log, model_name_for_log