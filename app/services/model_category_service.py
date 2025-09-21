# =============================================================================
# MODEL-CATEGORY SERVICE
# =============================================================================
# Model <-> Category atamalarını yönetir, toplu işlemler ve AI destekli öneriler
# =============================================================================

import logging
import json
from typing import Dict, Any, List, Optional
from app.database.repositories.model_category_repository import ModelCategoryRepository
from app.database.repositories.model_repository import ModelRepository
from app.database.repositories.category_repository import CategoryRepository
from app.services.recommendations_service import RecommendationsService

logger = logging.getLogger(__name__)


class ModelCategoryService:
    def __init__(self):
        self.recommender = RecommendationsService()

    # --------- Single model operations ---------
    def get_for_model(self, model_id: int) -> Dict[str, Any]:
        try:
            cat_ids = ModelCategoryRepository.get_category_ids_by_model(model_id)
            model = ModelRepository.get_model_by_id(model_id) or {}
            primary = model.get('primary_category_id')
            return { 'success': True, 'data': { 'model_id': model_id, 'category_ids': cat_ids, 'primary_category_id': primary } }
        except Exception as e:
            logger.error(f"get_for_model error: {e}")
            return { 'success': False, 'error': 'Atamalar getirilemedi' }

    def replace_for_model(self, model_id: int, category_ids: List[int], primary_category_id: Optional[int] = None) -> Dict[str, Any]:
        try:
            ok = ModelCategoryRepository.replace_model_categories(model_id, category_ids or [], primary_category_id)
            return { 'success': True } if ok else { 'success': False, 'error': 'Güncelleme başarısız' }
        except Exception as e:
            logger.error(f"replace_for_model error: {e}")
            return { 'success': False, 'error': 'Güncelleme başarısız' }

    def add_for_model(self, model_id: int, category_ids: List[int]) -> Dict[str, Any]:
        try:
            ok = ModelCategoryRepository.add_model_categories(model_id, category_ids or [])
            return { 'success': True } if ok else { 'success': False, 'error': 'Ekleme başarısız' }
        except Exception as e:
            logger.error(f"add_for_model error: {e}")
            return { 'success': False, 'error': 'Ekleme başarısız' }

    def remove_for_model(self, model_id: int, category_ids: List[int]) -> Dict[str, Any]:
        try:
            ok = ModelCategoryRepository.remove_model_categories(model_id, category_ids or [])
            return { 'success': True } if ok else { 'success': False, 'error': 'Silme başarısız' }
        except Exception as e:
            logger.error(f"remove_for_model error: {e}")
            return { 'success': False, 'error': 'Silme başarısız' }

    # --------- Bulk operations ---------
    def bulk_replace(self, model_ids: List[int], category_ids: List[int], primary_category_id: Optional[int] = None) -> Dict[str, Any]:
        if not model_ids:
            return { 'success': False, 'error': 'model_ids gerekli' }
        try:
            ok = ModelCategoryRepository.bulk_replace(model_ids, category_ids or [], primary_category_id)
            return { 'success': True } if ok else { 'success': False, 'error': 'Toplu güncelleme başarısız' }
        except Exception as e:
            logger.error(f"bulk_replace error: {e}")
            return { 'success': False, 'error': 'Toplu güncelleme başarısız' }

    def bulk_add(self, model_ids: List[int], category_ids: List[int]) -> Dict[str, Any]:
        if not model_ids:
            return { 'success': False, 'error': 'model_ids gerekli' }
        try:
            ok_all = True
            for mid in model_ids:
                ok = ModelCategoryRepository.add_model_categories(mid, category_ids or [])
                ok_all = ok_all and ok
            return { 'success': ok_all }
        except Exception as e:
            logger.error(f"bulk_add error: {e}")
            return { 'success': False, 'error': 'Toplu ekleme başarısız' }

    def bulk_remove(self, model_ids: List[int], category_ids: List[int]) -> Dict[str, Any]:
        if not model_ids:
            return { 'success': False, 'error': 'model_ids gerekli' }
        try:
            ok_all = True
            for mid in model_ids:
                ok = ModelCategoryRepository.remove_model_categories(mid, category_ids or [])
                ok_all = ok_all and ok
            return { 'success': ok_all }
        except Exception as e:
            logger.error(f"bulk_remove error: {e}")
            return { 'success': False, 'error': 'Toplu silme başarısız' }

    # --------- AI-assisted suggestions ---------
    def ai_suggest(self, model_ids: Optional[List[int]] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """Seçili modeller için kategori önerisi üretir ve öneriyi döner.
        Dönüş: {success, data: { suggestions: [ { model_id, category_ids:[int], reason } ] }}
        """
        try:
            # Model ve kategori verisini hazırla
            all_models = ModelRepository.get_all_models_with_categories()
            categories = CategoryRepository.get_all_categories()
            if model_ids:
                models = [m for m in all_models if int(m.get('model_id')) in set(model_ids)]
            else:
                models = all_models

            # Gemini'den kategori önerisi iste
            payload_models = []
            for m in models:
                payload_models.append({
                    'model_id': m.get('model_id'),
                    'model_name': m.get('model_name'),
                    'provider_name': m.get('provider_name'),
                    'provider_type': m.get('provider_type'),
                    'model_type': m.get('model_type'),
                    'categories': m.get('categories') or []
                })

            system_prompt = (
                "You are a taxonomy assistant. Given a list of AI models and the available categories, "
                "suggest the most appropriate categories for each model. If a content language is provided, "
                "take it into account (e.g., Turkish vs English model focus). Always return STRICT JSON with this schema:\n\n"
                "{\n  \"suggestions\": [\n    { \"model_id\": number, \"category_ids\": [number], \"reason\": string }\n  ]\n}\n\n"
                "Rules:\n- Only use category_id values from the provided categories list.\n- There is NO UPPER LIMIT on the number of categories. Include ALL categories that apply (minimum 1).\n- reason is a short phrase (max 10 words).\n- Do not include anything except the JSON object."
            )

            request_payload = {
                'models': payload_models,
                'categories': [{ 'category_id': c.get('category_id'), 'name': c.get('name') } for c in categories],
                'language': (language or '').strip() if language else None
            }

            # Ensure Gemini credentials via recommender service
            self.recommender._ensure_gemini_credentials()
            result = self.recommender.gemini.generate_content(
                prompt=json.dumps(request_payload, ensure_ascii=False),
                system_prompt=system_prompt
            )
            if not result.get('success'):
                return { 'success': False, 'error': result.get('error', 'AI generation failed') }

            text = result.get('content') or ''
            parsed = self.recommender._safe_parse_json(text)
            if not parsed:
                return { 'success': False, 'error': 'AI response parse failed' }

            out = []
            for s in (parsed.get('suggestions') or []):
                try:
                    item = {
                        'model_id': int(s.get('model_id')),
                        'category_ids': [int(x) for x in (s.get('category_ids') or [])],
                        'reason': str(s.get('reason') or '')[:300]
                    }
                    try:
                        logger.debug(f"AI suggest -> model_id={item['model_id']} category_count={len(item['category_ids'])}")
                    except Exception:
                        pass
                    out.append(item)
                except Exception:
                    continue

            return { 'success': True, 'data': { 'suggestions': out }, 'count': len(out) }
        except Exception as e:
            logger.error(f"ai_suggest error: {e}")
            return { 'success': False, 'error': 'AI suggestion error' }

