# =============================================================================
# API PACKAGE
# =============================================================================
# Bu paket, API endpoint'lerini içerir.
# =============================================================================

from .models import models_bp
from .healthcheck import health_bp
from .chats import chats_bp
from .categories import categories_bp
from .recommendations import recommendations_bp
from .admin import admin_api_bp

__all__ = [
    'models_bp',
    'health_bp',
    'chats_bp',
    'categories_bp',
    'recommendations_bp',
    'admin_api_bp',
]
