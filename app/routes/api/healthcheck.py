# =============================================================================
# HEALTHCHECK API ROUTES
# =============================================================================
# Sistem sağlık kontrolü için API endpoint'leri
# =============================================================================

from flask import Blueprint, jsonify
import logging
from app.services.health_service import HealthService

logger = logging.getLogger(__name__)

# Health API Blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/health')

health_service = HealthService()

@health_bp.route('/', methods=['GET'])
@health_bp.route('', methods=['GET'])
def health_check():
    """
    API sağlık kontrolü.
    """
    result = health_service.check_health()
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code
