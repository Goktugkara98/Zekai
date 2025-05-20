# app/services/base_ai_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import requests
import json
import os

class BaseAIService(ABC):
    """
    Abstract base class for AI service providers.
    Each specific AI service (e.g., Google, OpenRouter) should inherit from this class
    and implement its abstract methods.
    """

    def _generate_mock_response(self, user_message: str, model_name: str = "MockModel") -> str:
        """Generates a mock AI response when the actual API is not used."""
        return (f"This is a mock response from {model_name} for your message: '{user_message}'. "
                "The actual AI service is currently configured for mock responses.")

    def _extract_response_by_path(self, response_json: Dict, path: str) -> Any:
        """
        Extracts a value from a nested JSON object using a dot-notated path.
        Moved from main_routes.py.
        """
        try:
            parts = path.split('.')
            current_data = response_json
            for part in parts:
                if part.isdigit() and isinstance(current_data, list):
                    index = int(part)
                    if index >= len(current_data):
                        return f"Response format error: Index {index} out of bounds."
                    current_data = current_data[index]
                elif '[' in part and part.endswith(']'): # Handles keys with list access like 'candidates[0]'
                    key, index_str_with_bracket = part.split('[', 1)
                    index_str = index_str_with_bracket[:-1]
                    if not index_str.isdigit():
                        return f"Response format error: Invalid index '{index_str}'."
                    index = int(index_str)

                    if key: # If there's a key before the bracket
                        if not isinstance(current_data, dict) or key not in current_data:
                            return f"Response format error: Key '{key}' not found."
                        current_data = current_data[key]

                    if not isinstance(current_data, list) or index >= len(current_data):
                        return f"Response format error: Index {index} out of bounds for list."
                    current_data = current_data[index]
                else:
                    if not isinstance(current_data, dict) or part not in current_data:
                        return f"Response format error: Key '{part}' not found."
                    current_data = current_data[part]
            return current_data
        except (KeyError, IndexError, TypeError) as e:
            return f"Error processing AI response (format mismatch): {str(e)}"
        except Exception as e:
            return "Unexpected error while processing AI response."


    @abstractmethod
    def handle_chat(self,
                    user_message: Optional[str],
                    conversation_history: List[Dict[str, str]],
                    model_details: Dict[str, Any],
                    chat_id: str,
                    use_mock_api: bool
                   ) -> Tuple[str, Dict[str, Any], int, Dict[str, Any], str]:
        """
        Handles the chat interaction for a specific AI provider.

        Args:
            user_message (Optional[str]): The current message from the user.
            conversation_history (List[Dict[str, str]]): The history of the conversation.
            model_details (Dict[str, Any]): Configuration details for the AI model.
                                            (api_url, api_key, request_body_template, etc.)
            chat_id (str): The ID of the current chat session.
            use_mock_api (bool): Flag to indicate if a mock response should be generated.

        Returns:
            Tuple containing:
                - ai_response_text (str): The processed text response from the AI.
                - response_json_for_log (Dict[str, Any]): The full JSON response from AI for logging.
                - api_status_code (int): The HTTP status code from the AI API call.
                - request_payload_for_log (Dict[str, Any]): The payload sent to the AI API.
                - model_name_for_log (str): The name of the model used.
        """
        pass

    def _fill_payload_template(self,
                               template_str: Optional[str],
                               history: List[Dict[str, str]],
                               last_user_message: Optional[str]) -> Dict[str, Any]:
        """
        Fills the request body template with conversation history and the last user message.
        """
        if not template_str:
            raise ValueError("Request body template string is missing.")

        try:
            template_dict = json.loads(template_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in request body template.")

        def fill_template_recursive(template_part: Any, full_history: List[Dict[str, str]], current_message: Optional[str]) -> Any:
            if isinstance(template_part, dict):
                return {k: fill_template_recursive(v, full_history, current_message) for k, v in template_part.items()}
            elif isinstance(template_part, list):
                # Special handling for "$messages" placeholder in a list context
                if len(template_part) == 1 and template_part[0] == "$messages":
                    return full_history
                return [fill_template_recursive(item, full_history, current_message) for item in template_part]
            elif isinstance(template_part, str):
                if template_part == "$messages":
                    return full_history
                if template_part == "$message":
                    return current_message if current_message else ""
                # Legacy placeholder, prefer $message or $messages for clarity
                if "{user_prompt}" in template_part:
                    return template_part.replace("{user_prompt}", current_message if current_message else "")
                return template_part
            return template_part

        return fill_template_recursive(template_dict, history, last_user_message)