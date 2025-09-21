# =============================================================================
# MODELS API ROUTES
# =============================================================================
# Bu dosya, models tablosu için API endpoint'lerini tanımlar.
# =============================================================================

from flask import Blueprint, request, jsonify
import logging
from app.services.model_service import ModelService
from app.routes.auth_decorators import admin_required

logger = logging.getLogger(__name__)

# Models API Blueprint oluştur
models_bp = Blueprint('models_api', __name__, url_prefix='/api/models')

# ModelService instance'ı oluştur
model_service = ModelService()

@models_bp.route('/', methods=['GET'])
def get_models():
    """
    Tüm modelleri getirir.
    """
    result = model_service.get_all_models()
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code

@models_bp.route('/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """
    ID'ye göre model getirir.
    """
    result = model_service.get_model_by_id(model_id)
    status_code = 200 if result['success'] else (404 if 'bulunamadı' in result.get('error', '') else 500)
    return jsonify(result), status_code

@models_bp.route('/', methods=['POST'])
@admin_required
def create_new_model():
    """
    Yeni model oluşturur.
    """
    data = request.get_json()
    result = model_service.create_model(data)
    status_code = 201 if result['success'] else (400 if 'gereklidir' in result.get('error', '') else 500)
    return jsonify(result), status_code

@models_bp.route('/<int:model_id>', methods=['PUT'])
@admin_required
def update_existing_model(model_id):
    """
    Model günceller.
    """
    data = request.get_json()
    result = model_service.update_model(model_id, data)
    status_code = 200 if result['success'] else (400 if 'gönderilmedi' in result.get('error', '') else 500)
    return jsonify(result), status_code

@models_bp.route('/<int:model_id>', methods=['DELETE'])
@admin_required
def delete_existing_model(model_id):
    """
    Model siler.
    """
    result = model_service.delete_model(model_id)
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code
