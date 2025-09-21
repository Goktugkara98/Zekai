# =============================================================================
# RECOMMENDATIONS SERVICE
# =============================================================================
# Uses Gemini to analyze a free-form query and recommend models from our catalog.
# =============================================================================

import json
import logging
from typing import Dict, Any, List

from app.services.providers.gemini import GeminiService
from app.database.db_connection import execute_query

logger = logging.getLogger(__name__)


class RecommendationsService:
    def __init__(self):
        self.gemini = GeminiService()

    def _ensure_gemini_credentials(self) -> bool:
        try:
            # Prefer explicit gemini 2.5 flash, else fallback to any gemini flash
            row = execute_query(
                """
                SELECT model_name, api_key
                FROM models
                WHERE (LOWER(model_name) LIKE 'gemini-2.5-flash%' OR LOWER(model_name) LIKE 'gemini-2.0-flash%' OR LOWER(provider_name)='google')
                      AND api_key IS NOT NULL AND api_key <> ''
                ORDER BY CASE WHEN LOWER(model_name) LIKE 'gemini-2.5-flash%' THEN 0 ELSE 1 END, model_id ASC
                LIMIT 1
                """,
                fetch=True
            )
            if not row:
                logger.error("No Gemini API key found in models table")
                return False
            model_name = row[0]['model_name']
            api_key = row[0]['api_key']
            self.gemini.set_api_key(api_key)
            self.gemini.set_model(model_name)
            # Make responses more deterministic for recommendations
            self.gemini.set_parameters(temperature=0.2)
            return True
        except Exception as e:
            logger.error(f"Failed to ensure Gemini credentials: {e}")
            return False

    def recommend(self, query: str, models: List[Dict[str, Any]], categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not query:
            return { 'success': False, 'error': 'query required' }

        if not self._ensure_gemini_credentials():
            return { 'success': False, 'error': 'Gemini API key not configured' }

        # Reduce models payload to essentials to keep prompt compact
        compact_models = []
        for m in models or []:
            try:
                categories = []
                raw_cats = m.get('categories')
                if isinstance(raw_cats, list):
                    for c in raw_cats:
                        if isinstance(c, dict):
                            categories.append({
                                'category_id': c.get('category_id'),
                                'name': c.get('name')
                            })

                compact_models.append({
                    'model_id': m.get('model_id') or m.get('modelId'),
                    'model_name': m.get('model_name') or m.get('name'),
                    'provider': m.get('provider_name') or m.get('provider'),
                    'type': m.get('model_type') or m.get('type'),
                    'categories': categories
                })
            except Exception:
                continue

        compact_categories = []
        for c in categories or []:
            try:
                compact_categories.append({
                    'category_id': c.get('category_id'),
                    'name': c.get('name')
                })
            except Exception:
                continue

        system_prompt = (
            "You are a routing assistant. Given a user query and a catalog of AI models\n"
            "(with provider, type, and categories), recommend 3-6 models that would best\n"
            "answer the query. Always return STRICT JSON with this exact schema:\n\n"
            "{\n"
            "  \"suggestions\": [\n"
            "    { \"model_id\": number, \"confidence\": number, \"reason\": string, \"description\": string }\n"
            "  ]\n"
            "}\n\n"
            "Rules:\n"
            "- Only use model_id from the provided list.\n"
            "- confidence is 0..1.\n"
            "- reason is a very short phrase (3-7 words).\n"
            "- description is 1 concise sentence tailored to the user's query.\n"
            "- Do not include anything else than the JSON object."
        )

        payload = {
            'catalog': {
                'models': compact_models,
                'categories': compact_categories
            },
            'user_query': query
        }

        try:
            result = self.gemini.generate_content(
                prompt=json.dumps(payload, ensure_ascii=False),
                system_prompt=system_prompt
            )
            if not result.get('success'):
                return { 'success': False, 'error': result.get('error', 'Generation failed') }

            text = result.get('content') or ''
            parsed = self._safe_parse_json(text)
            if not parsed:
                return { 'success': False, 'error': 'Model returned unparseable response' }

            suggestions = parsed.get('suggestions') or []
            # normalize entries
            out = []
            for s in suggestions:
                try:
                    out.append({
                        'model_id': int(s.get('model_id')),
                        'confidence': float(s.get('confidence', 0)),
                        'reason': str(s.get('reason') or '')[:300],
                        'description': str(s.get('description') or s.get('desc') or s.get('explanation') or '')[:500]
                    })
                except Exception:
                    continue

            return { 'success': True, 'data': { 'suggestions': out }, 'count': len(out) }
        except Exception as e:
            logger.error(f"Recommendations error: {e}")
            return { 'success': False, 'error': 'Assistant error' }

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}
        # Try direct
        try:
            return json.loads(text)
        except Exception:
            pass
        # Try to extract outermost JSON object
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                snippet = text[start:end+1]
                return json.loads(snippet)
        except Exception:
            return {}
        return {}
