/**
 * Assistant Service
 * Bottom bar assistant: recommend models for a free-form query
 */

import { i18n } from '../utils/i18n.js';

export class AssistantService {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
    }

    async init() {
        // no-op for now
        return true;
    }

    /**
     * Recommend models using backend assistant API
     * @param {string} query
     * @returns {{ suggestions: Array }}
     */
    async recommend(query) {
        try {
            const modelService = window.ZekaiApp?.services?.modelService;
            const models = Array.isArray(modelService?.models) ? modelService.models : [];

            // fetch categories dynamically
            const catRes = await fetch('/api/categories/');
            const catJson = await catRes.json();
            const categories = (catJson && catJson.success && Array.isArray(catJson.data)) ? catJson.data : [];

            // compact models to avoid leaking sensitive data like api keys
            const compactModels = models.map(m => ({
                model_id: m.modelId ?? m.model_id,
                model_name: m.model_name ?? m.name,
                provider_name: m.provider,
                model_type: m.type,
                categories: Array.isArray(m.categories) ? m.categories.map(c => ({ category_id: c.category_id, name: c.name })) : []
            }));

            const compactCategories = Array.isArray(categories) ? categories.map(c => ({ category_id: c.category_id, name: c.name })) : [];

            const payload = { query, models: compactModels, categories: compactCategories };

            const res = await fetch('/api/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (!json.success) {
                // API failed, will use fallback logic below
            }

            let suggestions = Array.isArray(json.data?.suggestions) ? json.data.suggestions : [];

            // Enrich with full model objects from client cache
            const indexById = new Map();
            models.forEach(m => {
                const idNum = m.modelId || m.model_id || null;
                if (idNum != null) indexById.set(Number(idNum), m);
            });

            let enriched = suggestions.map(s => {
                const model = indexById.get(Number(s.model_id)) || null;
                return { ...s, model };
            }).filter(s => !!s.model);

            // Fallback: if no valid suggestions, pick top N available models
            if (!enriched.length) {
                const fallback = models
                    .filter(m => m.isAvailable !== false)
                    .slice(0, 6)
                    .map((m, idx) => ({
                        model_id: m.modelId || m.model_id,
                        confidence: 0.5 - (idx * 0.05),
                        reason: i18n.t('general_purpose'),
                        model: m
                    }));
                enriched = fallback;
            }

            return { success: true, suggestions: enriched };
        } catch (e) {
            // Fallback on unexpected error as well
            try {
                const modelService = window.ZekaiApp?.services?.modelService;
                const models = Array.isArray(modelService?.models) ? modelService.models : [];
                const fallback = models.filter(m => m.isAvailable !== false).slice(0, 6).map((m, idx) => ({
                    model_id: m.modelId || m.model_id,
                    confidence: 0.45 - (idx * 0.05),
                    reason: i18n.t('general_purpose_offline'),
                    model: m
                }));
                if (fallback.length) return { success: true, suggestions: fallback };
            } catch(_) {}
            return { success: false, error: e.message || i18n.t('assistant_error') };
        }
    }
}
