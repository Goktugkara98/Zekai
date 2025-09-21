# =============================================================================
# RECOMMENDATIONS API ROUTES
# =============================================================================
# Query understanding and model recommendation using Gemini
# =============================================================================

from flask import Blueprint, request, jsonify
import logging
from app.services.recommendations_service import RecommendationsService

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')
logger = logging.getLogger(__name__)
service = RecommendationsService()


@recommendations_bp.route('/', methods=['POST'])
@recommendations_bp.route('', methods=['POST'])
def recommend_models():
    try:
        payload = request.get_json(silent=True) or {}
        query = (payload.get('query') or '').strip()
        models = payload.get('models') or []
        categories = payload.get('categories') or []

        if not query:
            return jsonify({ 'success': False, 'error': 'query required' }), 400

        result = service.recommend(query=query, models=models, categories=categories)
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return jsonify({ 'success': False, 'error': 'Server error' }), 500
