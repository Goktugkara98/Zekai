# =============================================================================
# CATEGORIES API ROUTES
# =============================================================================
# Kategoriler ve kategoriye göre modeller için API endpoint'leri
# =============================================================================

from flask import Blueprint, jsonify
import logging
from app.services.category_service import CategoryService

logger = logging.getLogger(__name__)

categories_bp = Blueprint('categories_api', __name__, url_prefix='/api/categories')
service = CategoryService()


@categories_bp.route('/', methods=['GET'])
def get_categories():
    result = service.get_all_categories()
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code


@categories_bp.route('/<int:category_id>/models', methods=['GET'])
def get_models_for_category(category_id: int):
    result = service.get_models_by_category(category_id)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code
