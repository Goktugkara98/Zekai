# =============================================================================
# MODELS API ROUTES
# =============================================================================
# Bu dosya, models tablosu için API endpoint'lerini tanımlar.
# =============================================================================

from flask import Blueprint, request, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.database.repositories.model_repository import ModelRepository
from app.services.model_service import ModelService
from app.routes.auth_decorators import admin_required

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


@models_bp.route('/<int:model_id>/icon', methods=['POST'])
@admin_required
def upload_model_icon(model_id: int):
    """
    Model ikonu yükler ve models.logo_path alanına kaydeder.
    Kabul: multipart/form-data, dosya alan adı: 'icon' veya 'file'
    Dönüş: { success, logo_path }
    """
    try:
        # Dosya al
        file = request.files.get('icon') or request.files.get('file')
        if not file:
            return jsonify({"success": False, "error": "Dosya bulunamadı"}), 400

        # Uzantı kontrol
        filename = secure_filename(file.filename or '')
        if not filename:
            return jsonify({"success": False, "error": "Geçersiz dosya adı"}), 400

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
            return jsonify({"success": False, "error": "Sadece png, jpg, jpeg, svg, webp desteklenir"}), 400

        # Kaydetme yolu
        # Bu dosya: app/routes/api/models.py -> üst iki klasör -> static/img/icons
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'img', 'icons'))
        os.makedirs(base_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"model_{model_id}_{timestamp}{ext}"
        fs_path = os.path.join(base_dir, new_name)
        file.save(fs_path)

        # Web yolu
        web_path = f"/static/img/icons/{new_name}"

        # DB güncelle
        ok = ModelRepository.update_model(model_id, { 'logo_path': web_path })
        if not ok:
            return jsonify({"success": False, "error": "Veritabanı güncellenemedi"}), 500

        return jsonify({"success": True, "logo_path": web_path}), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Yükleme hatası"}), 500


@models_bp.route('/icons', methods=['GET'])
@admin_required
def list_model_icons():
    """
    Yüklü mevcut ikonları listeler.
    Dönüş: { success, data: [ { path, name } ] }
    """
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'img', 'icons'))
        if not os.path.isdir(base_dir):
            return jsonify({"success": True, "data": []}), 200
        allowed_ext = {'.png', '.jpg', '.jpeg', '.svg', '.webp'}
        items = []
        for fname in os.listdir(base_dir):
            ext = os.path.splitext(fname)[1].lower()
            if ext in allowed_ext:
                items.append({
                    'path': f"/static/img/icons/{fname}",
                    'name': fname
                })
        # İsteğe bağlı: ada göre sıralama
        items.sort(key=lambda x: x['name'].lower())
        return jsonify({"success": True, "data": items, "count": len(items)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": "İkonlar listelenemedi"}), 500

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
