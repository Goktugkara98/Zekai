/**
 * Modal Controller
 * Modal ve popup kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';
// Removed mock import to ensure we only show real data from the database
import { i18n } from '../utils/i18n.js';

export class ModalController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.activeModal = null;
        this.modals = new Map();
    }

    /**
     * Assistant suggestions modal
     * options: { query: string, suggestions: [ { model: {...}, confidence, reason } ] }
     */
    createAssistantSuggestionsModal(options = {}) {
        const { query = '', suggestions = [], loading = false } = options;
        const modal = DOMUtils.createElement('div', { className: 'modal-overlay' }, '');

        const renderSuggestion = (s) => {
            const m = s.model || {};
            const name = m.name || m.model_name || 'Model';
            const provider = m.provider || m.provider_name || '';
            const type = m.type || m.model_type || '';
            const logo = m.logoUrl || m.logo_path || null;
            const icon = m.icon || 'fas fa-robot';
            const modelId = m.modelId || m.model_id;
            const confidencePct = Math.round((Number(s.confidence || 0) * 100));
            const reason = (s.reason || '').trim();
            const description = (s.description || s.desc || s.explanation || reason || '').trim();
            const iconHtml = logo ? `<img class="model-logo" src="${logo}" alt="${(name || 'model')} logo" loading="lazy" />` : `<i class="${icon}"></i>`;
            return `
                <div class="suggest-card fade-in" data-model-id="${modelId}" data-model-name="${name}">
                    <div class="card-main">
                        <div class="card-icon">${iconHtml}</div>
                        <div class="card-info">
                            <div class="title-row">
                                <div class="name">${name}</div>
                                <div class="confidence">${confidencePct}%</div>
                            </div>
                            <div class="meta">${provider}${type ? ' • ' + String(type).toUpperCase() : ''}</div>
                            <div class="desc" title="${description}">${description}</div>
                            <div class="chips">
                                ${reason ? `<span class="chip chip-reason">${reason}</span>` : ''}
                                ${provider ? `<span class="chip chip-provider">${provider}</span>` : ''}
                                ${type ? `<span class="chip chip-type">${String(type).toUpperCase()}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="actions">
                        <button class="btn btn-primary start-chat" data-model-id="${modelId}" data-model-name="${name}"><i class="fas fa-comments"></i> ${i18n.t('start_chat')}</button>
                    </div>
                </div>
            `;
        };

        modal.innerHTML = `
            <div class="modal-content assistant-modal">
                <div class="modal-header">
                    <h3>${i18n.t('assistant_title')}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <style>
                        .assistant-modal { transform: translateY(8px) scale(0.98); opacity: 0; transition: transform 160ms ease, opacity 160ms ease; }
                        .assistant-modal.appear { transform: translateY(0) scale(1); opacity: 1; }
                        .assist-query { font-size: 13px; color: var(--muted); margin-bottom: 12px; }
                        .suggest-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; }
                        .assist-loading { display: ${loading ? 'flex' : 'none'}; align-items: center; gap: 10px; padding: 12px; background: var(--surface); border: 1px dashed var(--border); border-radius: 10px; color: var(--muted); margin-bottom: 12px; }
                        .suggest-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 12px; box-shadow: var(--shadow-sm); transition: box-shadow 160ms ease, transform 160ms ease, border-color 160ms ease; display: flex; flex-direction: column; min-height: 168px; }
                        .suggest-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); border-color: var(--primary); }
                        .suggest-card.fade-in { opacity: 0; transform: translateY(4px); }
                        .suggest-card.fade-in.appear { opacity: 1; transform: translateY(0); transition: opacity 200ms ease, transform 200ms ease; }
                        .suggest-card .card-main { display: flex; gap: 12px; align-items: flex-start; flex: 1; }
                        .suggest-card .card-icon { width: 40px; height: 40px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 18px; overflow: hidden; background: transparent; }
                        .suggest-card .card-icon img.model-logo { width: 100%; height: 100%; object-fit: contain; border-radius: 10px; }
                        .suggest-card .card-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
                        .suggest-card .title-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
                        .suggest-card .name { font-weight: 700; color: var(--text); min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .suggest-card .confidence { font-size: 12px; color: var(--primary); font-weight: 700; }
                        .suggest-card .meta { font-size: 12px; color: var(--muted); margin-top: 2px; }
                        .suggest-card .desc { margin-top: 8px; font-size: 13px; color: var(--text); opacity: 0.9; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 36px; }
                        .suggest-card .chips { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
                        .suggest-card .chip { font-size: 11px; line-height: 1; padding: 6px 8px; border-radius: 999px; border: 1px solid var(--border); background: var(--surface-alt); color: var(--text); opacity: 0.86; }
                        .suggest-card .chip-reason { background: var(--surface); border-style: dashed; }
                        .suggest-card .chip-type { text-transform: uppercase; letter-spacing: 0.3px; }
                        .suggest-card .actions { margin-top: 12px; display: flex; }
                        .suggest-card .btn { border: 1px solid var(--border); background: var(--surface); color: var(--text); padding: 10px 14px; border-radius: 10px; cursor: pointer; font-weight: 600; width: 100%; }
                        .suggest-card .btn:hover { background: var(--surface-alt); border-color: var(--primary); }
                        .suggest-card .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; width: 100%; box-shadow: 0 6px 14px rgba(59,130,246,0.18); }
                        .suggest-card .btn-primary:hover { filter: brightness(0.94); box-shadow: 0 8px 18px rgba(59,130,246,0.24); }
                        .suggest-card .btn i { margin-right: 6px; }
                    </style>
                    <div class="assist-query">${i18n.t('assistant_query')} <strong>${Helpers.escapeHtml ? Helpers.escapeHtml(query) : query}</strong></div>
                    <div class="assist-loading"><i class="fas fa-spinner fa-spin"></i> ${i18n.t('assistant_loading')}</div>
                    <div class="suggest-grid">${(suggestions || []).map(renderSuggestion).join('')}</div>
                </div>
            </div>
        `;

        // Store the original query so we can send it after model selection
        try {
            const contentEl = DOMUtils.$('.assistant-modal', modal);
            if (contentEl) {
                contentEl.setAttribute('data-assist-query', query || '');
            }
        } catch (_) {}

        // Animate in
        setTimeout(() => {
            const content = DOMUtils.$('.assistant-modal', modal);
            if (content) DOMUtils.addClass(content, 'appear');
            requestAnimationFrame(() => {
                DOMUtils.$$('.suggest-card.fade-in', modal).forEach(el => DOMUtils.addClass(el, 'appear'));
            });
        }, 10);

        // Close
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => this.closeModal(modal));
        }
        DOMUtils.on(modal, 'click', (e) => { if (e.target === modal) this.closeModal(modal); });

        // Start chat buttons (delegate later too)
        this.bindAssistantStartButtons(modal);

        return modal;
    }

    /** Active chats modal */
    createActiveChatsModal(options = {}) {
        const modal = DOMUtils.createElement('div', { className: 'modal-overlay' }, '');
        modal.innerHTML = `
            <div class="modal-content list-modal">
                <div class="modal-header">
                    <h3>${i18n.t?.('active_chats') || 'Aktif Sohbetler'}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <style>
                        .list-modal { transform: translateY(8px) scale(0.98); opacity: 0; transition: transform 160ms ease, opacity 160ms ease; }
                        .list-modal.appear { transform: translateY(0) scale(1); opacity: 1; }
                        .chat-list-modal { display: flex; flex-direction: column; gap: 8px; }
                        .chat-row-item { display:flex; align-items:center; gap:10px; padding:10px 12px; border:1px solid var(--border); border-radius:10px; background: var(--surface); cursor:pointer; }
                        .chat-row-item:hover { background: var(--surface-alt); border-color: var(--primary); }
                        .chat-row-item .model-icon { width: 28px; height: 28px; border-radius: 8px; display:flex; align-items:center; justify-content:center; overflow:hidden; }
                        .chat-row-item .model-icon img.model-logo { width:100%; height:100%; object-fit: contain; border-radius: 8px; }
                        .chat-row-item .info { display:flex; flex-direction:column; min-width:0; flex:1; }
                        .chat-row-item .name { font-weight:600; color: var(--text); overflow:hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .chat-row-item .preview { font-size:12px; color: var(--muted); overflow:hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .no-models { color: var(--muted); font-size: 12px; padding: 8px 12px; }
                    </style>
                    <div class="chat-list-modal"></div>
                </div>
            </div>
        `;
        setTimeout(() => { DOMUtils.$('.list-modal', modal)?.classList.add('appear'); }, 10);
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) DOMUtils.on(closeBtn, 'click', () => this.closeModal(modal));
        DOMUtils.on(modal, 'click', (e) => { if (e.target === modal) this.closeModal(modal); });

        (async () => {
            const container = DOMUtils.$('.chat-list-modal', modal);
            if (!container) return;
            try {
                const res = await fetch('/api/chats/list?active=true');
                const json = await res.json();
                const list = (json && json.success && Array.isArray(json.chats)) ? json.chats : [];
                if (!list.length) {
                    container.innerHTML = `<div class="no-models">${i18n.t?.('no_active_chats') || 'Aktif sohbet yok'}</div>`;
                    return;
                }
                container.innerHTML = list.map(c => {
                    const code = String(c.chat_id || c.id || '').toString().split('-').pop();
                    const name = c.model_name || c.title || 'Chat';
                    return `
                        <div class="chat-row-item" data-pane-id="${c.chat_id || c.id}">
                            <div class="model-icon"><i class="fas fa-robot"></i></div>
                            <div class="info">
                                <div class="name">${name} <span class="chat-code">#${code}</span></div>
                                <div class="preview"></div>
                            </div>
                        </div>
                    `;
                }).join('');
                // Bind clicks -> restore existing chat pane
                DOMUtils.$$('.chat-row-item', container).forEach(item => {
                    DOMUtils.on(item, 'click', (e) => {
                        const pid = item.getAttribute('data-pane-id');
                        if (!pid) return;
                        this.eventManager.emit('pane:restore-requested', { paneId: pid });
                        this.closeModal(modal);
                    });
                });
            } catch (_) {
                if (container) container.innerHTML = `<div class=\"no-models\">${i18n.t?.('load_failed') || 'Yüklenemedi'}</div>`;
            }
        })();
        return modal;
    }

    /** Chat history modal */
    createChatHistoryModal(options = {}) {
        const modal = DOMUtils.createElement('div', { className: 'modal-overlay' }, '');
        modal.innerHTML = `
            <div class="modal-content list-modal">
                <div class="modal-header">
                    <h3>${i18n.t?.('chat_history') || 'Sohbet Geçmişi'}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <style>
                        .list-modal { transform: translateY(8px) scale(0.98); opacity: 0; transition: transform 160ms ease, opacity 160ms ease; }
                        .list-modal.appear { transform: translateY(0) scale(1); opacity: 1; }
                        .chat-list-modal { display: flex; flex-direction: column; gap: 8px; }
                        .chat-row-item { display:flex; align-items:center; gap:10px; padding:10px 12px; border:1px solid var(--border); border-radius:10px; background: var(--surface); cursor:pointer; }
                        .chat-row-item:hover { background: var(--surface-alt); border-color: var(--primary); }
                        .chat-row-item .model-icon { width: 28px; height: 28px; border-radius: 8px; display:flex; align-items:center; justify-content:center; overflow:hidden; }
                        .chat-row-item .model-icon img.model-logo { width:100%; height:100%; object-fit: contain; border-radius: 8px; }
                        .chat-row-item .info { display:flex; flex-direction:column; min-width:0; flex:1; }
                        .chat-row-item .name { font-weight:600; color: var(--text); overflow:hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .chat-row-item .preview { font-size:12px; color: var(--muted); overflow:hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .no-models { color: var(--muted); font-size: 12px; padding: 8px 12px; }
                    </style>
                    <div class="chat-list-modal"></div>
                </div>
            </div>
        `;
        setTimeout(() => { DOMUtils.$('.list-modal', modal)?.classList.add('appear'); }, 10);
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) DOMUtils.on(closeBtn, 'click', () => this.closeModal(modal));
        DOMUtils.on(modal, 'click', (e) => { if (e.target === modal) this.closeModal(modal); });

        (async () => {
            const container = DOMUtils.$('.chat-list-modal', modal);
            if (!container) return;
            try {
                const res = await fetch('/api/chats/list?active=false');
                const json = await res.json();
                const list = (json && json.success && Array.isArray(json.chats)) ? json.chats : [];
                if (!list.length) {
                    container.innerHTML = `<div class="no-models">${i18n.t?.('no_chat_history') || 'Geçmiş sohbet yok'}</div>`;
                    return;
                }
                container.innerHTML = list.map(c => {
                    const code = String(c.chat_id || c.id || '').toString().split('-').pop();
                    const name = c.model_name || c.title || 'Chat';
                    return `
                        <div class="chat-row-item" data-pane-id="${c.chat_id || c.id}" data-model-name="${name}">
                            <div class="model-icon"><i class="fas fa-robot"></i></div>
                            <div class="info">
                                <div class="name">${name} <span class="chat-code">#${code}</span></div>
                                <div class="preview"></div>
                            </div>
                        </div>
                    `;
                }).join('');
                // Bind clicks -> open read-only history pane
                DOMUtils.$$('.chat-row-item', container).forEach(item => {
                    DOMUtils.on(item, 'click', (e) => {
                        const pid = item.getAttribute('data-pane-id');
                        const modelName = item.getAttribute('data-model-name');
                        if (!pid) return;
                        this.eventManager.emit('history:selected', { paneId: pid, modelName });
                        this.closeModal(modal);
                    });
                });
            } catch (_) {
                if (container) container.innerHTML = `<div class=\"no-models\">${i18n.t?.('load_failed') || 'Yüklenemedi'}</div>`;
            }
        })();
        return modal;
    }

    /**
     * Modelleri yönet modalı (favori toggle ile)
     */
    createModelsBrowserModal(options = {}) {
        const modal = DOMUtils.createElement('div', { className: 'modal-overlay' }, '');

        const state = {
            models: [],
            query: '',
            loading: true
        };

        const getTitle = () => {
            try { return i18n.t('models_manage_title'); } catch (_) { return 'Modelleri Yönet'; }
        };

        const getFavoriteSet = () => new Set(Helpers.getStorage('favorite_models') || []);

        const filterModels = () => {
            const q = (state.query || '').toLowerCase();
            let list = [...state.models];
            if (q) {
                list = list.filter(m => {
                    const name = (m.name || m.model_name || '').toLowerCase();
                    const desc = (m.description || '').toLowerCase();
                    const provider = (m.provider || m.provider_name || '').toLowerCase();
                    const type = (m.type || m.model_type || '').toLowerCase();
                    return name.includes(q) || desc.includes(q) || provider.includes(q) || type.includes(q);
                });
            }
            return list.sort((a, b) => (a.name || a.model_name || '').localeCompare(b.name || b.model_name || ''));
        };

        const renderList = () => {
            const listEl = DOMUtils.$('.models-grid', modal);
            if (!listEl) return;

            const favorites = getFavoriteSet();

            if (state.loading) {
                listEl.innerHTML = `
                    ${Array.from({ length: 8 }).map(() => `
                        <div class="model-card skeleton">
                            <div class="card-header">
                                <div class="card-icon shimmer"></div>
                                <div class="fav-toggle shimmer"></div>
                            </div>
                            <div class="card-body">
                                <div class="sk-line shimmer" style="width: 60%; height: 14px; border-radius: 6px;"></div>
                                <div class="sk-line shimmer" style="width: 40%; height: 12px; margin-top: 8px; border-radius: 6px;"></div>
                                <div class="sk-line shimmer" style="width: 100%; height: 10px; margin-top: 10px; border-radius: 6px;"></div>
                                <div class="sk-line shimmer" style="width: 90%; height: 10px; margin-top: 6px; border-radius: 6px;"></div>
                            </div>
                        </div>
                    `).join('')}
                `;
                return;
            }

            const list = filterModels();

            if (!list.length) {
                let emptyMsg; try { emptyMsg = i18n.t('no_models_found'); } catch (_) { emptyMsg = 'Model bulunamadı'; }
                listEl.innerHTML = `<div class="no-models">${emptyMsg}</div>`;
                return;
            }

            listEl.innerHTML = list.map(m => {
                const displayName = m.name || m.model_name;
                const provider = m.provider_name || m.provider || '';
                const type = (m.model_type || m.type || '').toString().toUpperCase();
                const description = m.description || '';
                const logo = m.logo_path || m.logoUrl || null;
                const iconHtml = logo
                    ? `<img class="model-logo" src="${logo}" alt="${(displayName || 'model')} logo" loading="lazy" />`
                    : `<i class="${m.icon || 'fas fa-robot'}"></i>`;
                const key = m.model_id ? `model-${m.model_id}` : (m.id || '');
                const checked = favorites.has(String(key)) ? 'checked' : '';

                return `
                    <div class="model-card" data-model-key="${key}">
                        <div class="card-header">
                            <div class="card-icon">${iconHtml}</div>
                            <label class="fav-toggle" title="${checked ? (i18n.t?.('model_active') || 'Aktif') : (i18n.t?.('model_inactive') || 'Pasif')}">
                                <input type="checkbox" class="model-enable-toggle" data-model-key="${key}" ${checked}>
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="card-body">
                            <div class="model-name">${displayName}</div>
                            <div class="model-meta">${provider}${type ? ' • ' + type : ''}</div>
                            <div class="model-desc">${description}</div>
                        </div>
                    </div>
                `;
            }).join('');

            DOMUtils.$$('.model-enable-toggle', listEl).forEach(toggle => {
                DOMUtils.on(toggle, 'change', () => {
                    const key = String(toggle.getAttribute('data-model-key'));
                    const current = getFavoriteSet();
                    if (toggle.checked) {
                        current.add(key);
                    } else {
                        current.delete(key);
                    }
                    Helpers.setStorage('favorite_models', [...current]);
                    this.eventManager.emit('models:favorite-updated', { ids: [...current] });
                });
            });

            DOMUtils.$$('img.model-logo', listEl).forEach(img => {
                if (img.complete) img.classList.add('img-loaded');
                else {
                    img.addEventListener('load', () => img.classList.add('img-loaded'));
                    img.addEventListener('error', () => img.classList.add('img-loaded'));
                }
            });
        };

        modal.innerHTML = `
            <div class="modal-content models-manage-modal">
                <div class="modal-header">
                    <h3>${getTitle()}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <style>
                        .models-manage-modal { width: min(1100px, 96vw); margin: 14px; transform: translateY(8px) scale(0.98); opacity: 0; transition: transform 160ms ease, opacity 160ms ease; }
                        .models-manage-modal .modal-body { padding-top: 16px; padding-bottom: 16px; }
                        .models-manage-modal.appear { transform: translateY(0) scale(1); opacity: 1; }
                        .models-manage-toolbar { display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
                        .models-manage-search { flex: 1; min-width: 220px; }
                        .models-manage-search input { width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--border); background: var(--surface); color: var(--text); }
                        .models-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; max-height: 60vh; overflow-y: auto; padding: 8px; }
                        .model-card { display: flex; flex-direction: column; gap: 10px; padding: 14px; border: 1px solid var(--border); border-radius: 16px; background: var(--surface); box-shadow: var(--shadow-sm); transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease; }
                        .model-card:hover { border-color: var(--primary); box-shadow: var(--shadow-md); transform: translateY(-1px); }
                        .model-card .card-header { display: flex; align-items: center; justify-content: space-between; }
                        .model-card .card-icon { width: 44px; height: 44px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; background: var(--surface-alt); color: var(--primary); overflow: hidden; }
                        .model-card .card-icon img.model-logo { width: 100%; height: 100%; object-fit: contain; border-radius: 12px; opacity: 0; transition: opacity 240ms ease; }
                        .model-card .card-icon img.model-logo.img-loaded { opacity: 1; }
                        .model-card .card-body { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
                        .model-card .model-name { font-weight: 700; font-size: 15px; color: var(--text); min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .model-card .model-meta { font-size: 12px; color: var(--muted); }
                        .model-card .model-desc { font-size: 12px; color: var(--text); opacity: 0.9; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
                        .fav-toggle { position: relative; width: 46px; height: 24px; display: inline-flex; align-items: center; cursor: pointer; }
                        .fav-toggle input { display: none; }
                        .toggle-slider { position: relative; width: 100%; height: 100%; background: var(--border); border-radius: 999px; transition: background 160ms ease; }
                        .toggle-slider::after { content: ''; position: absolute; top: 3px; left: 4px; width: 18px; height: 18px; border-radius: 50%; background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.14); transition: transform 160ms ease; }
                        .fav-toggle input:checked + .toggle-slider { background: var(--primary); }
                        .fav-toggle input:checked + .toggle-slider::after { transform: translateX(20px); }
                        .no-models { color: var(--muted); font-size: 12px; padding: 8px 0; text-align: center; }
                        /* Skeleton */
                        @keyframes shimmer { 0% { background-position: -200px 0; } 100% { background-position: 200px 0; } }
                        .shimmer { background: linear-gradient(90deg, rgba(148,163,184,0.18) 25%, rgba(148,163,184,0.28) 37%, rgba(148,163,184,0.18) 63%); background-size: 400px 100%; animation: shimmer 1.2s infinite; }
                        .model-card.skeleton .card-icon { background: var(--surface-alt); }
                    </style>
                    <div class="models-manage-toolbar">
                        <div class="models-manage-search"><input type="text" class="models-manage-search-input" placeholder="Model ara..." /></div>
                    </div>
                    <div class="models-grid"></div>
                </div>
            </div>
        `;

        setTimeout(() => {
            const content = DOMUtils.$('.models-manage-modal', modal);
            if (content) DOMUtils.addClass(content, 'appear');
        }, 10);

        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) DOMUtils.on(closeBtn, 'click', () => this.closeModal(modal));
        DOMUtils.on(modal, 'click', (e) => { if (e.target === modal) this.closeModal(modal); });

        const searchInput = DOMUtils.$('.models-manage-search-input', modal);
        if (searchInput) {
            DOMUtils.on(searchInput, 'input', () => {
                state.query = searchInput.value || '';
                renderList();
            });
        }

        (async () => {
            state.loading = true;
            renderList();
            try {
                const res = await fetch('/api/models');
                const json = await res.json();
                if (json && json.success && Array.isArray(json.data)) {
                    state.models = json.data;
                } else {
                    state.models = [];
                }
            } catch (_) {
                state.models = [];
            }
            state.loading = false;
            renderList();
        })();

        return modal;
    }

    bindAssistantStartButtons(modal) {
        const startBtns = DOMUtils.$$('.start-chat', modal);
        startBtns.forEach(btn => {
            DOMUtils.on(btn, 'click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const modelId = parseInt(btn.getAttribute('data-model-id'));
                const modelName = btn.getAttribute('data-model-name');
                // read original query from modal content
                let initialMessage = '';
                const content = DOMUtils.$('.assistant-modal', modal);
                if (content) {
                    initialMessage = content.getAttribute('data-assist-query') || '';
                }
                this.eventManager.emit('model:selected', { modelName, modelId, initialMessage });
                this.closeModal(modal);
            });
        });
    }

    updateAssistantSuggestions(suggestions = []) {
        const modal = this.activeModal;
        if (!modal) return;
        const content = DOMUtils.$('.assistant-modal', modal);
        if (!content) return;
        // hide loading
        const loadingEl = DOMUtils.$('.assist-loading', content);
        if (loadingEl) loadingEl.style.display = 'none';
        // render suggestions
        const grid = DOMUtils.$('.suggest-grid', content);
        if (!grid) return;
        const renderSuggestion = (s) => {
            const m = (s && s.model) || {};
            const name = m.name || m.model_name || 'Model';
            const provider = m.provider || m.provider_name || '';
            const type = m.type || m.model_type || '';
            const logo = m.logoUrl || m.logo_path || null;
            const icon = m.icon || 'fas fa-robot';
            const modelId = m.modelId || m.model_id;
            const confidencePct = Math.round((Number(s.confidence || 0) * 100));
            const reason = (s.reason || '').trim();
            const description = (s.description || s.desc || s.explanation || reason || '').trim();
            const iconHtml = logo ? `<img class="model-logo" src="${logo}" alt="${(name || 'model')} logo" loading="lazy" />` : `<i class="${icon}"></i>`;
            return `
                <div class="suggest-card fade-in" data-model-id="${modelId}" data-model-name="${name}">
                    <div class="card-main">
                        <div class="card-icon">${iconHtml}</div>
                        <div class="card-info">
                            <div class="title-row">
                                <div class="name">${name}</div>
                                <div class="confidence">${confidencePct}%</div>
                            </div>
                            <div class="meta">${provider}${type ? ' • ' + String(type).toUpperCase() : ''}</div>
                            <div class="desc" title="${description}">${description}</div>
                            <div class="chips">
                                ${reason ? `<span class=\"chip chip-reason\">${reason}</span>` : ''}
                                ${provider ? `<span class=\"chip chip-provider\">${provider}</span>` : ''}
                                ${type ? `<span class=\"chip chip-type\">${String(type).toUpperCase()}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="actions">
                        <button class="btn btn-primary start-chat" data-model-id="${modelId}" data-model-name="${name}"><i class="fas fa-comments"></i> ${i18n.t('start_chat')}</button>
                    </div>
                </div>
            `;
        };
        grid.innerHTML = (suggestions || []).map(renderSuggestion).join('');
        // animate
        requestAnimationFrame(() => {
            DOMUtils.$$('.suggest-card.fade-in', grid).forEach(el => DOMUtils.addClass(el, 'appear'));
        });
        // bind buttons
        this.bindAssistantStartButtons(modal);
    }

    /**
     * Kategori modelleri modal oluştur
     * @param {Object} options - { category: string }
     * @returns {Element}
     */
    createCategoryModelsModal(options = {}) {
        const { category = 'Models', categoryId = null, initialModels = [] } = options;

        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        const favorites = new Set(Helpers.getStorage('favorite_models') || []);

        const renderCards = (list, { animate = true } = {}) => list.map(m => {
            const color = m.color || '#7c3aed';
            const displayName = m.name || m.model_name;
            const modelIdForChat = m.model_id || m.modelId;
            const idStr = m.model_id ? `model-${m.model_id}` : (m.id || '');
            const logo = m.logo_path || m.logoUrl || null;
            const iconHtml = logo
                ? `<img class="model-logo" src="${logo}" alt="${(displayName || 'model')} logo" loading="lazy" />`
                : `<i class="${m.icon || 'fas fa-robot'}"></i>`;
            const provider = m.provider_name || m.provider || '';
            const type = m.model_type || m.type || '';
            const desc = m.description || '';
            return `
                <div class="${animate ? 'model-card fade-in' : 'model-card'}" data-model-id="${modelIdForChat}" data-model-name="${displayName}">
                    <div class="card-header">
                        <div class="card-icon">${iconHtml}</div>
                        <div class="card-titles">
                            <div class="card-title">${displayName}</div>
                            <div class="card-meta">${provider} • ${type}</div>
                        </div>
                        <button class="fav-toggle ${favorites.has(String(idStr)) ? 'is-fav' : ''}" title="${i18n.t('favorite')}" aria-label="${i18n.t('favorite')}" data-id="${idStr}">
                            <i class="fas fa-star"></i>
                        </button>
                    </div>
                    <div class="card-description">${desc}</div>
                    <div class="card-chips">
                        ${provider ? `<span class="chip chip-provider">${provider}</span>` : ''}
                        ${type ? `<span class="chip chip-type">${String(type).toUpperCase()}</span>` : ''}
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-primary start-chat" aria-label="${i18n.t('start_chat')}" data-model-id="${modelIdForChat}" data-model-name="${displayName}">
                            <i class="fas fa-comments"></i> ${i18n.t('start_chat')}
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        const renderSkeleton = (count = 8) => {
            return new Array(count).fill(0).map(() => `
                <div class="model-card skeleton">
                    <div class="card-header">
                        <div class="card-icon shimmer"></div>
                        <div class="card-titles">
                            <div class="sk-line sk-title shimmer"></div>
                            <div class="sk-line sk-meta shimmer"></div>
                        </div>
                        <div class="sk-fav shimmer"></div>
                    </div>
                    <div class="sk-line sk-desc shimmer"></div>
                    <div class="card-chips">
                        <div class="chip sk-chip shimmer"></div>
                        <div class="chip sk-chip shimmer"></div>
                    </div>
                    <div class="sk-actions">
                        <div class="sk-btn shimmer"></div>
                    </div>
                </div>
            `).join('');
        };

        modal.innerHTML = `
            <div class="modal-content category-modal">
                <div class="modal-header">
                    <h3>${i18n.t('category_models_title', { category })}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <style>
                        .category-modal { transform: translateY(8px) scale(0.98); opacity: 0; transition: transform 160ms ease, opacity 160ms ease; }
                        .category-modal.appear { transform: translateY(0) scale(1); opacity: 1; }
                        .category-model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; align-items: start; }
                        .model-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 14px; box-shadow: var(--shadow-sm); min-height: 140px; transition: box-shadow 160ms ease, transform 160ms ease, border-color 160ms ease; }
                        .model-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); border-color: var(--primary); }
                        .model-card.fade-in { opacity: 0; transform: translateY(4px); }
                        .model-card.fade-in.appear { opacity: 1; transform: translateY(0); transition: opacity 200ms ease, transform 200ms ease; }
                        .model-card .card-header { display: flex; align-items: center; gap: 12px; }
                        .model-card .card-icon { width: 40px; height: 40px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 18px; overflow: hidden; background: transparent; }
                        .model-card .card-icon img.model-logo { width: 100%; height: 100%; object-fit: contain; border-radius: 10px; opacity: 0; transition: opacity 240ms ease; }
                        .model-card .card-icon img.model-logo.img-loaded { opacity: 1; }
                        .model-card .card-titles { flex: 1; min-width: 0; display: flex; flex-direction: column; }
                        .model-card .card-title { font-weight: 700; color: var(--text); line-height: 1.2; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                        .model-card .card-meta { font-size: 12px; color: var(--muted); margin-top: 2px; }
                        .model-card .fav-toggle { width: 28px; height: 28px; border: none; background: transparent; border-radius: 6px; color: var(--muted); cursor: pointer; }
                        .model-card .fav-toggle.is-fav { color: var(--warning); }
                        .model-card .card-description { font-size: 13px; color: var(--text); opacity: 0.9; margin: 10px 0 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 38px; }
                        .model-card .card-chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0 10px; }
                        .model-card .chip { font-size: 11px; line-height: 1; padding: 6px 8px; border-radius: 999px; border: 1px solid var(--border); background: var(--surface-alt); color: var(--text); opacity: 0.86; }
                        .model-card .chip-type { text-transform: uppercase; letter-spacing: 0.3px; }
                        .model-card .card-actions { display: flex; gap: 8px; }
                        .model-card .btn { border: 1px solid var(--border); background: var(--surface); color: var(--text); padding: 10px 14px; border-radius: 10px; cursor: pointer; font-weight: 600; }
                        .model-card .btn:hover { background: var(--surface-alt); border-color: var(--primary); }
                        .model-card .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; width: 100%; box-shadow: 0 6px 14px rgba(59,130,246,0.18); }
                        .model-card .btn-primary:hover { filter: brightness(0.94); box-shadow: 0 8px 18px rgba(59,130,246,0.24); }
                        .model-card .btn i { margin-right: 6px; }

                        /* Skeleton Loading */
                        @keyframes shimmer { 0% { background-position: -200px 0; } 100% { background-position: 200px 0; } }
                        .skeleton .shimmer { background: linear-gradient(90deg, rgba(148,163,184,0.18) 25%, rgba(148,163,184,0.28) 37%, rgba(148,163,184,0.18) 63%); background-size: 400px 100%; animation: shimmer 1.2s infinite; }
                        .skeleton { min-height: 140px; }
                        .skeleton .card-icon { width: 40px; height: 40px; border-radius: 10px; }
                        .skeleton .sk-line { height: 12px; border-radius: 6px; }
                        .skeleton .sk-title { width: 60%; height: 16px; margin-bottom: 8px; }
                        .skeleton .sk-meta { width: 40%; height: 12px; }
                        .skeleton .sk-desc { width: 100%; height: 32px; margin: 12px 0; border-radius: 8px; }
                        .skeleton .sk-fav { width: 28px; height: 28px; border-radius: 6px; }
                        .skeleton .sk-chip { width: 80px; height: 20px; border-radius: 999px; }
                        .skeleton .sk-actions { display: flex; }
                        .skeleton .sk-btn { width: 160px; height: 34px; border-radius: 8px; }
                    </style>
                    <div class="category-toolbar">
                        <!-- Future: search/sort controls -->
                    </div>
                    <div class="category-model-grid">${(Array.isArray(initialModels) && initialModels.length) ? renderCards(initialModels) : renderSkeleton(8)}</div>
                </div>
            </div>
        `;

        this.setupCategoryModelsModalEvents(modal);

        // Smooth content animation
        setTimeout(() => {
            const content = DOMUtils.$('.category-modal', modal);
            if (content) DOMUtils.addClass(content, 'appear');
        }, 10);

        // Eğer initialModels varsa, direkt fade-in ve event binding yap
        const gridInit = DOMUtils.$('.category-model-grid', modal);
        if (Array.isArray(initialModels) && initialModels.length && gridInit) {
            requestAnimationFrame(() => {
                DOMUtils.$$('.model-card.fade-in', gridInit).forEach(el => DOMUtils.addClass(el, 'appear'));
            });
            DOMUtils.$$('img.model-logo', gridInit).forEach(img => {
                if (img.complete) img.classList.add('img-loaded');
                else {
                    img.addEventListener('load', () => img.classList.add('img-loaded'));
                    img.addEventListener('error', () => img.classList.add('img-loaded'));
                }
            });
            // Start chat buttons
            const startBtnsInit = DOMUtils.$$('.start-chat', modal);
            startBtnsInit.forEach(btn => {
                DOMUtils.on(btn, 'click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const modelId = parseInt(btn.getAttribute('data-model-id'));
                    const modelName = btn.getAttribute('data-model-name');
                    this.eventManager.emit('model:selected', { modelName, modelId });
                    this.closeModal(modal);
                });
            });
            // Favorite toggles
            const favTogglesInit = DOMUtils.$$('.fav-toggle', modal);
            favTogglesInit.forEach(toggle => {
                DOMUtils.on(toggle, 'click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const id = String(toggle.getAttribute('data-id'));
                    const current = new Set(Helpers.getStorage('favorite_models') || []);
                    if (current.has(id)) current.delete(id); else current.add(id);
                    Helpers.setStorage('favorite_models', [...current]);
                    toggle.classList.toggle('is-fav');
                    this.eventManager.emit('models:favorite-updated', { ids: [...current] });
                });
            });
        }

        // API'den daima taze veri çek ve grid'i güncelle (initialModels varsa, onu hemen gösteriyoruz)
        (async () => {
            try {
                let list = [];
                if (categoryId) {
                    const res = await fetch(`/api/categories/${categoryId}/models`);
                    const json = await res.json();
                    if (json && json.success && Array.isArray(json.data)) {
                        list = json.data;
                    }
                }
                const grid = DOMUtils.$('.category-model-grid', modal);
                if (grid) {
                    if (Array.isArray(list) && list.length) {
                        // Compare existing rendered model IDs with fetched list
                        const existingEls = Array.from(DOMUtils.$$('.model-card', grid) || []);
                        const existingIds = existingEls.map(el => parseInt(el.getAttribute('data-model-id'))).filter(n => !isNaN(n));
                        const fetchedIds = list.map(m => parseInt(m.model_id || m.modelId)).filter(n => !isNaN(n));
                        const sameOrderAndContent = existingIds.length === fetchedIds.length && existingIds.every((v, i) => v === fetchedIds[i]);

                        if (!sameOrderAndContent) {
                            // Update without fade-in to avoid flash
                            grid.innerHTML = renderCards(list, { animate: false });
                            // Ensure images transition nicely without reflow flicker
                            DOMUtils.$$('img.model-logo', grid).forEach(img => {
                                if (img.complete) {
                                    img.classList.add('img-loaded');
                                } else {
                                    img.addEventListener('load', () => img.classList.add('img-loaded'));
                                    img.addEventListener('error', () => img.classList.add('img-loaded'));
                                }
                            });
                            // Start chat buttons
                            const startBtns = DOMUtils.$$('.start-chat', modal);
                            startBtns.forEach(btn => {
                                DOMUtils.on(btn, 'click', (e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    const modelId = parseInt(btn.getAttribute('data-model-id'));
                                    const modelName = btn.getAttribute('data-model-name');
                                    this.eventManager.emit('model:selected', { modelName, modelId });
                                    this.closeModal(modal);
                                });
                            });
                            // Favorite toggles
                            const favToggles = DOMUtils.$$('.fav-toggle', modal);
                            favToggles.forEach(toggle => {
                                DOMUtils.on(toggle, 'click', (e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    const id = String(toggle.getAttribute('data-id'));
                                    const current = new Set(Helpers.getStorage('favorite_models') || []);
                                    if (current.has(id)) current.delete(id); else current.add(id);
                                    Helpers.setStorage('favorite_models', [...current]);
                                    toggle.classList.toggle('is-fav');
                                    this.eventManager.emit('models:favorite-updated', { ids: [...current] });
                                });
                            });
                        }
                    } else {
                        let emptyMsg;
                        try { emptyMsg = i18n.t('no_models_found'); } catch (e) { emptyMsg = 'Model bulunamadı'; }
                        if (!emptyMsg || typeof emptyMsg !== 'string' || /no_models_found/i.test(emptyMsg)) {
                            emptyMsg = 'Model bulunamadı';
                        }
                        grid.innerHTML = `<div class="no-models">${emptyMsg}</div>`;
                    }
                }
            } catch (err) {}
        })();

        return modal;
    }

    /** Category models modal events */
    setupCategoryModelsModalEvents(modal) {
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => this.closeModal(modal));
        }

        // Overlay click closes
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });
    }

    /**
     * Controller'ı başlat
     */
    async init() {
        // Event listener'ları kur
        this.setupEventListeners();
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Modal show event'i
        this.eventManager.on('modal:show', (event) => {
            this.showModal(event.data);
        });

        // Modal hide event'i
        this.eventManager.on('modal:hide', (event) => {
            this.hideModal(event.data);
        });

        // Modal close event'i
        this.eventManager.on('modal:close', () => {
            this.closeActiveModal();
        });

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.closeActiveModal();
            }
        });

        // Assistant suggestions update
        this.eventManager.on('assistant:suggestions:update', (event) => {
            const { suggestions = [] } = event.data || {};
            this.updateAssistantSuggestions(suggestions);
        });

        // Open models browser when user clicks "Pin more" in sidebar
        this.eventManager.on('models:pin-more', () => {
            this.showModal({ type: 'models-browser' });
        });
    }

    /**
     * Modal göster
     * @param {Object} data - Modal data
     */
    showModal(data) {
        const { type, title, content, options = {} } = data;

        // Mevcut modal'ı kapat
        if (this.activeModal) {
            this.closeActiveModal();
        }

        let modal;
        switch (type) {
            case 'prompts':
                modal = this.createPromptsModal();
                break;
            case 'settings':
                modal = this.createSettingsModal();
                break;
            case 'confirm':
                modal = this.createConfirmModal(title, content, options);
                break;
            case 'alert':
                modal = this.createAlertModal(title, content, options);
                break;
            case 'category-models':
                modal = this.createCategoryModelsModal(options);
                break;
            case 'assistant-suggestions':
                modal = this.createAssistantSuggestionsModal(options);
                break;
            case 'models-browser':
                modal = this.createModelsBrowserModal(options);
                break;
            case 'active-chats':
                modal = this.createActiveChatsModal(options);
                break;
            case 'chat-history':
                modal = this.createChatHistoryModal(options);
                break;
            default:
                modal = this.createGenericModal(title, content, options);
        }

        if (modal) {
            this.activeModal = modal;
            document.body.appendChild(modal);
            
            // Animation
            setTimeout(() => {
                DOMUtils.addClass(modal, 'show');
            }, 10);

            // Event emit et
            this.eventManager.emit('modal:shown', {
                type,
                element: modal
            });
        }
    }

    /**
     * Modal gizle
     * @param {Object} data - Modal data
     */
    hideModal(data) {
        const { id } = data;
        const modal = this.modals.get(id);
        
        if (modal) {
            this.closeModal(modal);
        }
    }

    /**
     * Aktif modal'ı kapat
     */
    closeActiveModal() {
        if (this.activeModal) {
            this.closeModal(this.activeModal);
        }
    }

    /**
     * Modal kapat
     * @param {Element} modal - Modal elementi
     */
    closeModal(modal) {
        if (!modal) return;

        DOMUtils.addClass(modal, 'hide');
        
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            
            if (this.activeModal === modal) {
                this.activeModal = null;
            }
        }, 300);

        // Event emit et
        this.eventManager.emit('modal:closed', {
            element: modal
        });
    }

    /**
     * Prompts modal oluştur
     * @returns {Element}
     */
    createPromptsModal() {
        const modal = DOMUtils.createElement('div', { className: 'modal-overlay' }, '');

        // Data
        const categories = [
            { id: 'all', label: i18n.t('all') || 'Tümü' },
            { id: 'creative', label: i18n.t('prompts_creative') || 'Yaratıcı' },
            { id: 'business', label: i18n.t('prompts_business') || 'İş' },
            { id: 'technical', label: i18n.t('prompts_technical') || 'Teknik' },
            { id: 'education', label: i18n.t('prompts_education') || 'Eğitim' },
        ];

        const prompts = [
            {
                title: i18n.t('write_short_story'),
                text: 'Aşağıdaki kriterlere uygun, 600-900 kelimelik özgün bir kısa hikâye yaz: 1) Tema: {Tema}; 2) Anlatıcı: birinci tekil; 3) Atmosfer: {Atmosfer}; 4) Karakterler: en az iki karakter, belirgin motivasyon; 5) Yapı: güçlü açılış, yükselen gerilim, beklenmedik ama mantıklı final; 6) Dil: akıcı, görsel imgelerle zengin, klişelerden kaçın. Hikâye bittiğinde toplam karakter sayısını parantez içinde ver.',
                example: 'Tema: Yalnızlık\nAtmosfer: Yağmurlu İstanbul gecesi\nNot: Finalde ana karakterin yanılgısı ortaya çıksın.',
                category: 'creative',
                desc: 'Tema, atmosfer ve anlatım tercihlerini girerek sinematik bir kısa hikâye üret.',
                icon: 'fas fa-pen-nib'
            },
            {
                title: i18n.t('create_poem'),
                text: 'Serbest ölçüde, {Duygu} duygusunu öne çıkaran 12-16 dizelik bir şiir yaz. Somut imgeler, beklenmedik metaforlar ve iç ses ritmi kullan. Tekrara kaçma, son iki dizeyi vurucu yap.',
                example: 'Duygu: Özlem\nNot: Şehir imgeleri ve gece atmosferi yer alsın.',
                category: 'creative',
                desc: 'Duygu merkezli modern bir şiir için güçlü imgeler ve ritim.',
                icon: 'fas fa-feather'
            },
            {
                title: i18n.t('write_dialogue'),
                text: 'Sahne yönergeleriyle birlikte 2 karakter arasında 2-3 dakikalık bir diyalog yaz. Çatışma net, alt metin güçlü olsun. Mekân: {Mekan}. Duygu yayılımı: gerilimden çözülmeye. Sonda küçük bir twist ekle.',
                example: 'Mekan: Kapanmak üzere olan bir kitapçı\nNot: Karakterlerden biri bir sırrı gizliyor.',
                category: 'creative',
                desc: 'Sahne ve alt metni olan kısa, sinematik bir diyalog.',
                icon: 'fas fa-theater-masks'
            },

            {
                title: i18n.t('write_business_plan'),
                text: 'Aşağıdaki başlıklarla yalın ama kapsamlı bir iş planı yaz: 1) Problem ve fırsat; 2) Çözüm ve değer önerisi; 3) Pazar ve segmentler; 4) Rakip analizi (tablo); 5) Gelir modeli; 6) Go-to-market; 7) OKR ve 90 günlük yol haritası; 8) Riskler ve önlemler. İş: {IsTanimi}.',
                example: 'IsTanimi: Yapay zekâ destekli kişisel finans uygulaması\nNot: Freemium + abonelik modelini değerlendir.',
                category: 'business',
                desc: 'Yatırımcı sunumuna uygun, net bölümlere ayrılmış iş planı.',
                icon: 'fas fa-briefcase'
            },
            {
                title: i18n.t('create_marketing_strategy'),
                text: '{Urun} için 90 günlük pazarlama stratejisi hazırla: 1) Hedef persona(lar); 2) Mesaj çerçeveleri; 3) Kanal kırılımı (Paid/Owned/Earned); 4) İçerik takvimi (2 haftalık tablo); 5) Bütçe tahsisi; 6) KPI seti ve ölçüm planı; 7) Riskler ve A/B test önerileri.',
                example: 'Urun: B2B SaaS proje yönetim aracı\nBütçe: Orta ölçek\nNot: LinkedIn ve içerik pazarlaması öncelikli olsun.',
                category: 'business',
                desc: 'Kanallara ve ölçüme odaklı, uygulanabilir strateji.',
                icon: 'fas fa-bullhorn'
            },
            {
                title: i18n.t('analyze_market'),
                text: '{Sektor} için hızlı pazar analizi yap: TAM/SAM/SOM tahmini, ilk 5 rakip karşılaştırma tablosu, konumlandırma haritası, fırsat-risk matrisi ve 3 öneri.',
                example: 'Sektor: Uzaktan eğitim platformları\nNot: Avrupa pazarı odağı.',
                category: 'business',
                desc: 'Sayılara dayalı, karar destek amaçlı özet analiz.',
                icon: 'fas fa-chart-line'
            },

            {
                title: i18n.t('explain_how_to'),
                text: '{Konu} konusunu öğretici bir rehberle açıkla: önkoşullar, kavramsal çerçeve, adım adım uygulama, yaygın hatalar, kontrol listesi ve ileri okuma.',
                example: 'Konu: JWT tabanlı kimlik doğrulama\nNot: Güvenlik uyarıları ve best practice ekle.',
                category: 'technical',
                desc: 'Adım adım ve pratik ipuçlarıyla teknik rehber.',
                icon: 'fas fa-lightbulb'
            },
            {
                title: i18n.t('write_code_for'),
                text: '{Diller} için {Islev} fonksiyonunu yaz: temiz mimari, yorum satırları, birim testleri ve örnek kullanım ekle. Karmaşıklık ve Big-O analizi belirt.',
                example: 'Diller: Python\nIslev: LRU Cache sınıfı\nNot: pytest ile basit testler.',
                category: 'technical',
                desc: 'Üretim kalitesine yakın, testli örnek kod.',
                icon: 'fas fa-code'
            },
            {
                title: i18n.t('debug_code'),
                text: 'Aşağıdaki hata için hata ayıklama planı yaz ve çözüme yönelik yama öner: 1) Reprodüksiyon adımları; 2) Kök neden analizi; 3) Patch; 4) Test kapsamı; 5) Regresyon önlemi. Kod: \n```\n{Kod}\n```',
                example: 'Kod: TypeError: Cannot read properties of undefined (reading "map")\nBağlam: React 18, useEffect içinde fetch sonrası state güncellemesi',
                category: 'technical',
                desc: 'Sistematik hata ayıklama ve onarım planı.',
                icon: 'fas fa-bug'
            },

            {
                title: i18n.t('teach_me_about'),
                text: '{Konu} konusunu seviyeye uygun bir mini ders olarak anlat: temel kavramlar, örnekler, 3 soruluk quiz, özet ve pratik ödev.',
                example: 'Seviye: Orta\nKonu: Olasılık dağılımları\nNot: Normal ve binom dağılımı odaklı.',
                category: 'education',
                desc: 'Öğretici mini ders formatı, quiz ve ödevle pekiştirme.',
                icon: 'fas fa-book'
            },
            {
                title: i18n.t('create_lesson_plan'),
                text: '{Konu} için 60 dakikalık ders planı yaz: hedefler, materyaller, 3 aşamalı etkinlik akışı, değerlendirme ve farklılaştırma önerileri.',
                example: 'Konu: Doğrusal denklemler\nHedef kitle: 9. sınıf\nNot: Somut örnekler ve görseller kullan.',
                category: 'education',
                desc: 'Uygulanabilir, net adımlı ders planı.',
                icon: 'fas fa-list'
            },
            {
                title: i18n.t('explain_concept'),
                text: 'Karmaşık bir kavramı (ör. {Kavram}) 3 seviyede açıkla: sezgisel anlatım, teknik ayrıntılar, gerçek dünyadan benzetme. Sonunda mini kontrol listesi ver.',
                example: 'Kavram: Transformer mimarisi\nNot: “Attention” sezgisel açıklamalarını güçlendir.',
                category: 'education',
                desc: 'Sezgisel + teknik katmanlı açıklama.',
                icon: 'fas fa-graduation-cap'
            },
        ];

        const renderNavItem = (c, active = c.id === 'all') => `
            <button class="nav-item ${active ? 'active' : ''}" data-category="${c.id}"><span class="dot"></span>${c.label}</button>
        `;

        const renderListItem = (p, idx) => `
            <button class="prompt-list-item ${idx === 0 ? 'selected' : ''}"
                data-index="${idx}"
                data-title="${Helpers.escapeHtml ? Helpers.escapeHtml(p.title) : p.title}"
                data-prompt="${Helpers.escapeHtml ? Helpers.escapeHtml(p.text) : p.text}"
                data-desc="${Helpers.escapeHtml ? Helpers.escapeHtml(p.desc || '') : (p.desc || '')}"
                data-example="${Helpers.escapeHtml ? Helpers.escapeHtml(p.example || '') : (p.example || '')}"
                data-category="${p.category}"
                data-icon="${p.icon}">
                <i class="${p.icon}"></i>
                <span class="title" title="${p.title}">${p.title}</span>
            </button>
        `;

        const navHtml = categories.map(renderNavItem).join('');
        const listHtml = prompts.map((p, i) => renderListItem(p, i)).join('');

        modal.innerHTML = `
            <div class="modal-content prompts-modal">
                <div class="modal-header">
                    <div>
                        <h3>${i18n.t('prompts_modal_title')}</h3>
                        <div class="subtle">Hızlı başlamanız için özenle hazırlanmış örnek istekler. Arayın, filtreleyin ve doğrudan kullanın.</div>
                    </div>
                    <button class="close-btn" aria-label="close">&times;</button>
                </div>
                <div class="modal-body">
                    <style>
                        .prompts-modal { transform: translateY(8px) scale(0.98); opacity: 0; transition: transform 160ms ease, opacity 160ms ease; width: min(1100px, 94vw); }
                        .prompts-modal.appear { transform: translateY(0) scale(1); opacity: 1; }
                        .prompts-layout { display: grid; grid-template-columns: 220px 300px 1fr; gap: 16px; min-height: 560px; }
                        .prompts-nav { border: 1px solid var(--border); border-radius: 12px; padding: 12px; background: var(--surface); height: fit-content; position: sticky; top: 16px; align-self: start; }
                        .nav-item { width: 100%; text-align: left; display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; margin-bottom: 8px; font-weight: 600; }
                        .nav-item .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--muted); display: inline-block; }
                        .nav-item.active { background: var(--primary); border-color: var(--primary); color: #fff; }
                        .nav-item.active .dot { background: #fff; }
                        .prompts-list { border: 1px solid var(--border); border-radius: 12px; background: var(--surface); overflow: hidden; display: flex; flex-direction: column; }
                        .prompts-list .list-toolbar { padding: 10px; border-bottom: 1px solid var(--border); }
                        .prompt-search { width: 100%; min-width: 220px; display: flex; align-items: center; gap: 8px; border: 1px solid var(--border); background: var(--surface); border-radius: 10px; padding: 8px 10px; }
                        .prompt-search i { color: var(--muted); }
                        .prompt-search input { flex: 1; border: none; outline: none; background: transparent; color: var(--text); }
                        .prompt-list-scroll { overflow: auto; padding: 6px; }
                        .prompt-list-item { width: 100%; border: none; background: transparent; display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 10px; cursor: pointer; color: var(--text); text-align: left; }
                        .prompt-list-item i { color: var(--muted); width: 16px; }
                        .prompt-list-item .title { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                        .prompt-list-item:hover { background: var(--surface-alt); }
                        .prompt-list-item.selected { background: rgba(124,58,237,0.12); }

                        .prompts-detail { border: 1px solid var(--border); border-radius: 12px; background: var(--surface); padding: 16px; display: flex; flex-direction: column; }
                        .detail-title { display: flex; align-items: center; gap: 10px; font-weight: 900; font-size: 16px; margin-bottom: 6px; }
                        .detail-desc { color: var(--text); opacity: 0.9; font-size: 13px; margin-bottom: 12px; }
                        .detail-example { background: var(--surface-alt); border: 1px dashed var(--border); border-radius: 10px; padding: 12px; margin-top: 8px; }
                        .detail-example pre { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; white-space: pre-wrap; color: var(--text); opacity: 0.9; }
                        .detail-actions { margin-top: auto; display: flex; gap: 8px; justify-content: flex-end; }
                        .detail-actions .btn { border: 1px solid var(--border); background: var(--surface); color: var(--text); padding: 10px 12px; border-radius: 10px; cursor: pointer; font-weight: 700; }
                        .detail-actions .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; }
                        .prompt-card .btn-primary:hover { filter: brightness(0.95); box-shadow: 0 8px 18px rgba(124,58,237,0.24); }
                        .modal-header .subtle { margin-top: 4px; font-size: 12px; color: var(--muted); }
                        @media (max-width: 1100px) { .prompts-layout { grid-template-columns: 200px 1fr; } .prompts-list { order: 2; } .prompts-detail { order: 3; } }
                        @media (max-width: 800px) { .prompts-layout { grid-template-columns: 1fr; } .prompts-nav { position: relative; top: auto; } }
                    </style>
                    <div class="prompts-layout">
                        <div class="prompts-nav">${navHtml}</div>
                        <div class="prompts-list">
                            <div class="list-toolbar">
                                <div class="prompt-search"><i class="fas fa-search"></i><input type="text" class="prompt-search-input" placeholder="${i18n.t('search') || 'Ara'}..." /></div>
                            </div>
                            <div class="prompt-list-scroll">${listHtml}</div>
                        </div>
                        <div class="prompts-detail">
                            <!-- detail will be rendered dynamically -->
                            <div class="detail-empty" style="color: var(--muted);">Bir öğe seçin</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Animate in
        setTimeout(() => {
            const content = DOMUtils.$('.prompts-modal', modal);
            if (content) DOMUtils.addClass(content, 'appear');
            requestAnimationFrame(() => {
                DOMUtils.$$('.prompt-card.fade-in', modal).forEach(el => DOMUtils.addClass(el, 'appear'));
            });
        }, 10);

        // Bind events
        this.setupPromptsModalEvents(modal);

        // Initialize detail with first selected item
        try {
            const first = DOMUtils.$('.prompt-list-item.selected', modal) || DOMUtils.$('.prompt-list-item', modal);
            if (first) {
                this.renderPromptDetailFromItem(modal, first);
            }
        } catch (_) {}

        return modal;
    }

    /**
     * Prompts modal event'lerini kur
     * @param {Element} modal - Modal elementi
     */
    setupPromptsModalEvents(modal) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });

        // List select -> render detail
        const list = DOMUtils.$('.prompt-list-scroll', modal);
        if (list) {
            DOMUtils.on(list, 'click', (e) => {
                const item = e.target.closest('.prompt-list-item');
                if (!item) return;
                DOMUtils.$$('.prompt-list-item', list).forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                this.renderPromptDetailFromItem(modal, item);
            });
            // Double click to use
            DOMUtils.on(list, 'dblclick', (e) => {
                const item = e.target.closest('.prompt-list-item');
                if (!item) return;
                const prompt = item.getAttribute('data-prompt');
                if (prompt) {
                    this.handlePromptSelection(prompt);
                    this.closeModal(modal);
                }
            });
        }

        // Search filter
        const searchInput = DOMUtils.$('.prompt-search-input', modal);
        if (searchInput) {
            DOMUtils.on(searchInput, 'input', () => {
                this.filterPrompts(modal);
            });
        }

        // Category nav
        const navItems = DOMUtils.$$('.nav-item', modal);
        navItems.forEach(item => {
            DOMUtils.on(item, 'click', (e) => {
                e.preventDefault();
                DOMUtils.$$('.nav-item', modal).forEach(n => n.classList.remove('active'));
                item.classList.add('active');
                this.filterPrompts(modal);
            });
        });
    }

    /** Filter prompts by search text and selected category */
    filterPrompts(modal) {
        const q = (DOMUtils.$('.prompt-search-input', modal)?.value || '').toLowerCase();
        const activeNav = DOMUtils.$('.nav-item.active', modal);
        const cat = activeNav ? activeNav.getAttribute('data-category') : 'all';
        const items = DOMUtils.$$('.prompt-list-item', modal);
        let firstVisible = null;
        items.forEach(item => {
            const title = (item.getAttribute('data-title') || '').toLowerCase();
            const desc = (item.getAttribute('data-desc') || '').toLowerCase();
            const c = item.getAttribute('data-category');
            const matchesText = !q || title.includes(q) || desc.includes(q);
            const matchesCat = !cat || cat === 'all' || c === cat;
            const show = matchesText && matchesCat;
            item.style.display = show ? '' : 'none';
            if (!firstVisible && show) firstVisible = item;
        });
        // Select first visible and render detail
        const list = DOMUtils.$('.prompt-list-scroll', modal);
        if (list) {
            DOMUtils.$$('.prompt-list-item', list).forEach(i => i.classList.remove('selected'));
        }
        if (firstVisible) {
            firstVisible.classList.add('selected');
            this.renderPromptDetailFromItem(modal, firstVisible);
        } else {
            const detail = DOMUtils.$('.prompts-detail', modal);
            if (detail) detail.innerHTML = '<div class="detail-empty" style="color: var(--muted);">Sonuç bulunamadı</div>';
        }
    }

    /** Render detail view from list item dataset */
    renderPromptDetailFromItem(modal, item) {
        const title = item.getAttribute('data-title') || '';
        const prompt = item.getAttribute('data-prompt') || '';
        const desc = item.getAttribute('data-desc') || '';
        const example = item.getAttribute('data-example') || '';
        const icon = item.getAttribute('data-icon') || 'fas fa-bolt';
        const detail = DOMUtils.$('.prompts-detail', modal);
        if (!detail) return;
        detail.innerHTML = `
            <div class="detail-title"><i class="${icon}"></i><span>${title}</span></div>
            <div class="detail-desc">${desc}</div>
            <div class="detail-example"><strong>Örnek</strong><pre>${Helpers.escapeHtml ? Helpers.escapeHtml(example) : example}</pre></div>
            <div class="detail-example" style="margin-top: 12px;"><strong>İstek Metni</strong><pre>${Helpers.escapeHtml ? Helpers.escapeHtml(prompt) : prompt}</pre></div>
            <div class="detail-actions">
                <button class="btn copy-detail"><i class="fas fa-copy"></i> Kopyala</button>
                <button class="btn btn-primary use-detail">${i18n.t('use_prompt') || 'Kullan'}</button>
            </div>
        `;
        // Bind detail buttons
        const copyBtn = DOMUtils.$('.copy-detail', detail);
        if (copyBtn) {
            DOMUtils.on(copyBtn, 'click', async () => {
                try { await navigator.clipboard.writeText(prompt); } catch (_) {}
                this.stateManager.addNotification?.({ type: 'success', message: i18n.t('copied') || 'Kopyalandı' });
            });
        }
        const useBtn = DOMUtils.$('.use-detail', detail);
        if (useBtn) {
            DOMUtils.on(useBtn, 'click', () => {
                this.handlePromptSelection(prompt);
                this.closeModal(modal);
            });
        }
    }

    /**
     * Prompt seçimi işle
     * @param {string} prompt - Prompt metni
     */
    handlePromptSelection(prompt) {
        // Event emit et
        this.eventManager.emit('prompt:selected', {
            prompt
        });

        // Input'a prompt'u ekle
        const messageInput = DOMUtils.$('.message-input');
        if (messageInput) {
            messageInput.value = prompt;
            messageInput.focus();
        }
    }

    /**
     * Settings modal oluştur
     * @returns {Element}
     */
    createSettingsModal() {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${i18n.t('settings_title')}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="settings-section">
                        <h4>${i18n.t('settings_general')}</h4>
                        <div class="setting-item">
                            <label>${i18n.t('settings_theme')}</label>
                            <select class="setting-input" data-setting-key="theme">
                                <option value="light">${i18n.t('theme_light')}</option>
                                <option value="dark">${i18n.t('theme_dark')}</option>
                                <option value="auto">${i18n.t('theme_auto')}</option>
                            </select>
                        </div>
                        <div class="setting-item">
                            <label>${i18n.t('settings_language')}</label>
                            <select class="setting-input" data-setting-key="language">
                                <option value="en">English</option>
                                <option value="tr">Türkçe</option>
                            </select>
                        </div>
                    </div>
                    <div class="settings-section">
                        <h4>${i18n.t('settings_chat')}</h4>
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" class="setting-checkbox" data-setting-key="auto_save_conversations">
                                ${i18n.t('auto_save_conversations')}
                            </label>
                        </div>
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" class="setting-checkbox" data-setting-key="show_typing_indicator">
                                ${i18n.t('show_typing_indicator')}
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">${i18n.t('cancel')}</button>
                    <button class="btn btn-primary" data-action="save">${i18n.t('save')}</button>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupSettingsModalEvents(modal);

        return modal;
    }

    /**
     * Settings modal event'lerini kur
     * @param {Element} modal - Modal elementi
     */
    setupSettingsModalEvents(modal) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });

        // Footer buttons
        const cancelBtn = DOMUtils.$('[data-action="cancel"]', modal);
        const saveBtn = DOMUtils.$('[data-action="save"]', modal);

        if (cancelBtn) {
            DOMUtils.on(cancelBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        if (saveBtn) {
            DOMUtils.on(saveBtn, 'click', () => {
                this.handleSettingsSave(modal);
            });
        }
    }

    /**
     * Settings kaydetme işle
     * @param {Element} modal - Modal elementi
     */
    handleSettingsSave(modal) {
        // Settings'leri topla
        const settings = {};
        
        const selects = DOMUtils.$$('.setting-input[data-setting-key]', modal);
        selects.forEach(select => {
            const key = select.getAttribute('data-setting-key');
            if (key) settings[key] = select.value;
        });

        const checkboxes = DOMUtils.$$('.setting-checkbox[data-setting-key]', modal);
        checkboxes.forEach(checkbox => {
            const key = checkbox.getAttribute('data-setting-key');
            if (key) settings[key] = checkbox.checked;
        });

        // State'e kaydet
        this.stateManager.setPreference('settings', settings);

        // Event emit et
        this.eventManager.emit('settings:saved', {
            settings
        });

        // Modal'ı kapat
        this.closeModal(modal);

        // Notification göster
        this.stateManager.addNotification({
            type: 'success',
            message: i18n.t('settings_saved_success')
        });
    }

    /**
     * Confirm modal oluştur
     * @param {string} title - Modal başlığı
     * @param {string} content - Modal içeriği
     * @param {Object} options - Modal seçenekleri
     * @returns {Element}
     */
    createConfirmModal(title, content, options = {}) {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${content}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">${i18n.t('cancel')}</button>
                    <button class="btn btn-danger" data-action="confirm">${i18n.t('confirm')}</button>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupConfirmModalEvents(modal, options);

        return modal;
    }

    /**
     * Confirm modal event'lerini kur
     * @param {Element} modal - Modal elementi
     * @param {Object} options - Modal seçenekleri
     */
    setupConfirmModalEvents(modal, options) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onCancel) {
                    options.onCancel();
                }
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
                if (options.onCancel) {
                    options.onCancel();
                }
            }
        });

        // Footer buttons
        const cancelBtn = DOMUtils.$('[data-action="cancel"]', modal);
        const confirmBtn = DOMUtils.$('[data-action="confirm"]', modal);

        if (cancelBtn) {
            DOMUtils.on(cancelBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onCancel) {
                    options.onCancel();
                }
            });
        }

        if (confirmBtn) {
            DOMUtils.on(confirmBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onConfirm) {
                    options.onConfirm();
                }
            });
        }
    }

    /**
     * Alert modal oluştur
     * @param {string} title - Modal başlığı
     * @param {string} content - Modal içeriği
     * @param {Object} options - Modal seçenekleri
     * @returns {Element}
     */
    createAlertModal(title, content, options = {}) {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${content}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" data-action="ok">${i18n.t('ok')}</button>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupAlertModalEvents(modal, options);

        return modal;
    }

    /**
     * Alert modal event'lerini kur
     * @param {Element} modal - Modal elementi
     * @param {Object} options - Modal seçenekleri
     */
    setupAlertModalEvents(modal, options) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onOk) {
                    options.onOk();
                }
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
                if (options.onOk) {
                    options.onOk();
                }
            }
        });

        // OK button
        const okBtn = DOMUtils.$('[data-action="ok"]', modal);
        if (okBtn) {
            DOMUtils.on(okBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onOk) {
                    options.onOk();
                }
            });
        }
    }

    /**
     * Generic modal oluştur
     * @param {string} title - Modal başlığı
     * @param {string} content - Modal içeriği
     * @param {Object} options - Modal seçenekleri
     * @returns {Element}
     */
    createGenericModal(title, content, options = {}) {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupGenericModalEvents(modal, options);

        return modal;
    }

    /**
     * Generic modal event'lerini kur
     * @param {Element} modal - Modal elementi
     * @param {Object} options - Modal seçenekleri
     */
    setupGenericModalEvents(modal, options) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });
    }

    /**
     * Controller'ı temizle
     */
    destroy() {
        // Tüm modal'ları kapat
        if (this.activeModal) {
            this.closeActiveModal();
        }

        // Event listener'ları kaldır
        document.removeEventListener('keydown', this.handleEscapeKey);
    }
}
