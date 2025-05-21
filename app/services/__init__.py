# app/services/__init__.py
from typing import Optional, Dict, Any
from app.services.base_ai_service import BaseAIService
from app.services.openai_service import OpenAIService
from app.services.openrouter_ai_service import OpenRouterAIService
# Import other services as you create them
# from .your_other_ai_service import YourOtherAIService

# --- AI Service Registry ---
# Maps a provider_type string (ideally from your database model_details)
# to the corresponding service class.
AI_SERVICE_REGISTRY = {
    "openai": OpenAIService,
    "openrouter": OpenRouterAIService,
    # "google": GoogleAIService, # Example for future
    # "anthropic": AnthropicService, # Example for future
}

def get_ai_service(model_details: Dict[str, Any]) -> Optional[BaseAIService]:
    """
    Factory function to get an AI service instance based on model details.

    Args:
        model_details (Dict[str, Any]): Dictionary containing details of the AI model,
                                         including 'provider_type' or 'api_url' for inference.

    Returns:
        Optional[BaseAIService]: An instance of the appropriate AI service, or None if not found/supported.
    """
    provider_type = model_details.get('provider_type')
    api_url = model_details.get('api_url', '').lower()

    if not provider_type:
        # Infer provider_type if not explicitly set (less reliable)
        if 'generativelanguage.googleapis.com' in api_url:
            provider_type = 'openai'
        elif 'openrouter.ai' in api_url:
            provider_type = 'openrouter'
        # Add more inferences here if needed
        else:
            # Fallback or default if no provider_type and cannot infer
            # For now, let's assume if it's not google or openrouter by URL, we don't know.
            # Depending on your setup, you might want a default service or to raise an error.
            print(f"Warning: provider_type not specified for model ID {model_details.get('id')} and could not be inferred from URL: {api_url}") # Log this
            return None


    ServiceClass = AI_SERVICE_REGISTRY.get(provider_type.lower() if provider_type else None)

    if ServiceClass:
        return ServiceClass()  # Instantiate and return the service
    else:
        print(f"Error: No AI service found for provider_type: {provider_type} (Model ID: {model_details.get('id')})") # Log this
        return None