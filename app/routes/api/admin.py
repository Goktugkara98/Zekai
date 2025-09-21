# =============================================================================
# ADMIN API (API)
# =============================================================================
# Admin paneli için JSON tabanlı yönetim endpoint'leri
# =============================================================================

from flask import Blueprint, request, jsonify
import logging
from app.routes.auth_decorators import admin_required
from app.services.user_service import UserService
from app.services.model_category_service import ModelCategoryService
from app.services.category_service import CategoryService

logger = logging.getLogger(__name__)

admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')

user_service = UserService()
mc_service = ModelCategoryService()
category_service = CategoryService()


# -----------------------------
# Users
# -----------------------------
@admin_api_bp.route('/users', methods=['GET'])
@admin_required
def api_list_users():
    result = user_service.list_users()
    return jsonify(result), (200 if result.get('success') else 500)


@admin_api_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def api_get_user(user_id: int):
    result = user_service.get_user(user_id)
    return jsonify(result), (200 if result.get('success') else 404)


@admin_api_bp.route('/users', methods=['POST'])
@admin_required
def api_create_user():
    data = request.get_json(silent=True) or {}
    result = user_service.create_user(data)
    status = 201 if result.get('success') else (400 if 'zorunlu' in (result.get('error') or '') else 500)
    return jsonify(result), status


@admin_api_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id: int):
    data = request.get_json(silent=True) or {}
    # Şifre güncellemesi ayrı endpoint ile yapılır
    data.pop('password', None)
    result = user_service.update_user(user_id, data)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/users/<int:user_id>/password', methods=['PATCH'])
@admin_required
def api_update_user_password(user_id: int):
    data = request.get_json(silent=True) or {}
    new_password = data.get('password')
    result = user_service.update_password(user_id, new_password)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id: int):
    result = user_service.delete_user(user_id)
    return jsonify(result), (200 if result.get('success') else 400)


# -----------------------------
# Categories
# -----------------------------
@admin_api_bp.route('/categories', methods=['GET'])
@admin_required
def api_list_categories():
    result = category_service.get_all_categories()
    return jsonify(result), (200 if result.get('success') else 500)


@admin_api_bp.route('/categories/<int:category_id>', methods=['GET'])
@admin_required
def api_get_category(category_id: int):
    result = category_service.get_category(category_id)
    return jsonify(result), (200 if result.get('success') else 404)


@admin_api_bp.route('/categories', methods=['POST'])
@admin_required
def api_create_category():
    data = request.get_json(silent=True) or {}
    result = category_service.create_category(data)
    status = 201 if result.get('success') else (400 if 'zorunlu' in (result.get('error') or '') else 500)
    return jsonify(result), status


@admin_api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def api_update_category(category_id: int):
    data = request.get_json(silent=True) or {}
    result = category_service.update_category(category_id, data)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def api_delete_category(category_id: int):
    result = category_service.delete_category(category_id)
    return jsonify(result), (200 if result.get('success') else 400)


# -----------------------------
# Model-Category assignments
# -----------------------------
@admin_api_bp.route('/models/<int:model_id>/categories', methods=['GET'])
@admin_required
def api_model_categories_get(model_id: int):
    result = mc_service.get_for_model(model_id)
    return jsonify(result), (200 if result.get('success') else 404)


@admin_api_bp.route('/models/<int:model_id>/categories', methods=['PUT'])
@admin_required
def api_model_categories_replace(model_id: int):
    data = request.get_json(silent=True) or {}
    category_ids = data.get('category_ids') or []
    primary_category_id = data.get('primary_category_id')
    result = mc_service.replace_for_model(model_id, category_ids, primary_category_id)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/models/<int:model_id>/categories/add', methods=['POST'])
@admin_required
def api_model_categories_add(model_id: int):
    data = request.get_json(silent=True) or {}
    category_ids = data.get('category_ids') or []
    result = mc_service.add_for_model(model_id, category_ids)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/models/<int:model_id>/categories/remove', methods=['POST'])
@admin_required
def api_model_categories_remove(model_id: int):
    data = request.get_json(silent=True) or {}
    category_ids = data.get('category_ids') or []
    result = mc_service.remove_for_model(model_id, category_ids)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/models/categories/bulk/replace', methods=['POST'])
@admin_required
def api_model_categories_bulk_replace():
    data = request.get_json(silent=True) or {}
    model_ids = data.get('model_ids') or []
    category_ids = data.get('category_ids') or []
    primary_category_id = data.get('primary_category_id')
    result = mc_service.bulk_replace(model_ids, category_ids, primary_category_id)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/models/categories/bulk/add', methods=['POST'])
@admin_required
def api_model_categories_bulk_add():
    data = request.get_json(silent=True) or {}
    model_ids = data.get('model_ids') or []
    category_ids = data.get('category_ids') or []
    result = mc_service.bulk_add(model_ids, category_ids)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/models/categories/bulk/remove', methods=['POST'])
@admin_required
def api_model_categories_bulk_remove():
    data = request.get_json(silent=True) or {}
    model_ids = data.get('model_ids') or []
    category_ids = data.get('category_ids') or []
    result = mc_service.bulk_remove(model_ids, category_ids)
    return jsonify(result), (200 if result.get('success') else 400)


@admin_api_bp.route('/models/categories/ai/suggest', methods=['POST'])
@admin_required
def api_model_categories_ai_suggest():
    data = request.get_json(silent=True) or {}
    model_ids = data.get('model_ids')
    result = mc_service.ai_suggest(model_ids)
    return jsonify(result), (200 if result.get('success') else 500)


@admin_api_bp.route('/models/categories/ai/apply', methods=['POST'])
@admin_required
def api_model_categories_ai_apply():
    data = request.get_json(silent=True) or {}
    suggestions = data.get('suggestions') or []
    # suggestions: [{ model_id, category_ids, primary_category_id? }]
    ok_all = True
    for s in suggestions:
        try:
            mid = int(s.get('model_id'))
            cids = [int(x) for x in (s.get('category_ids') or [])]
            pcid = s.get('primary_category_id')
            if pcid is not None:
                pcid = int(pcid)
            res = mc_service.replace_for_model(mid, cids, pcid)
            ok_all = ok_all and bool(res.get('success'))
        except Exception:
            ok_all = False
    return jsonify({'success': ok_all}), (200 if ok_all else 400)


# Per-model AI auto-categorization
@admin_api_bp.route('/models/<int:model_id>/categories/auto', methods=['POST'])
@admin_required
def api_model_categories_auto(model_id: int):
    """Auto-determine categories for a single model using AI.
    Returns: { success, data: { category_ids: [int], primary_category_id?: int, reason?: str } }
    """
    try:
        data = request.get_json(silent=True) or {}
        language = (data.get('language') or '').strip() or None
        # Reuse existing suggestion engine for a single model
        sug = mc_service.ai_suggest([model_id], language=language)
        if not sug.get('success'):
            return jsonify({ 'success': False, 'error': sug.get('error', 'AI suggestion failed') }), 500

        suggestions = (sug.get('data') or {}).get('suggestions') or []
        found = None
        for s in suggestions:
            try:
                if int(s.get('model_id')) == int(model_id):
                    found = s
                    break
            except Exception:
                continue

        if not found:
            return jsonify({ 'success': False, 'error': 'Öneri bulunamadı' }), 404

        cat_ids = [int(x) for x in (found.get('category_ids') or [])]
        primary = cat_ids[0] if cat_ids else None
        payload = {
            'category_ids': cat_ids,
            'primary_category_id': primary,
            'reason': found.get('reason')
        }
        return jsonify({ 'success': True, 'data': payload }), 200
    except Exception as e:
        logger.error(f"api_model_categories_auto error: {e}")
        return jsonify({ 'success': False, 'error': 'AI auto-categorization error' }), 500
