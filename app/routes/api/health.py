# =============================================================================
# HEALTH API ROUTES
# =============================================================================
# Bu dosya, sistem sağlık kontrolü için API endpoint'lerini tanımlar.
# =============================================================================

from flask import Blueprint, jsonify
import logging
from app.services.health_service import HealthService

logger = logging.getLogger(__name__)

# Health API Blueprint oluştur
health_bp = Blueprint('health_api', __name__, url_prefix='/api/health')

# HealthService instance'ı oluştur
health_service = HealthService()

@health_bp.route('/', methods=['GET'])
def health_check():
    """
    API sağlık kontrolü.
    """
    result = health_service.check_health()
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code
