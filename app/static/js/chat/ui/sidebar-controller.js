/**
 * Sidebar Controller
 * Sidebar UI kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';
import { i18n } from '../utils/i18n.js';

export class SidebarController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.sidebar = null;
        this.modelItems = [];
        this.categoryItems = [];
        this.chatItems = [];
        this.historyItems = [];
        // Category models cache & promises for prefetch
        this.categoryModelsCache = new Map(); // categoryId -> models[]
        this.categoryModelsPromises = new Map(); // categoryId -> Promise
    }

    /**
     * Kullanıcının chat listelerini backend'den yükle ve render et
     */
    async loadUserChats() {
        const activeListEl = this.activeChatListEl || DOMUtils.$('#active-chat-list');
        const historyListEl = this.historyListEl || DOMUtils.$('#history-list');
        if (!activeListEl && !historyListEl) return;

        // Aktif sohbetleri getir
        try {
            const resActive = await fetch('/api/chats/list?active=true');
            const jsonActive = await resActive.json();
            if (jsonActive && jsonActive.success && Array.isArray(jsonActive.chats)) {
                this.renderActiveChatsFromServer(jsonActive.chats, activeListEl);
            }
        } catch (e) {
            console.warn('Active chats fetch failed:', e);
        }

        // Geçmiş (pasif) sohbetleri getir
        try {
            const resHist = await fetch('/api/chats/list?active=false');
            const jsonHist = await resHist.json();
            if (jsonHist && jsonHist.success && Array.isArray(jsonHist.chats)) {
                this.renderHistoryChatsFromServer(jsonHist.chats, historyListEl);
            }
        } catch (e) {
            console.warn('History chats fetch failed:', e);
        }
    }

    /**
     * Sunucudan gelen aktif sohbet listesini render et
     */
    renderActiveChatsFromServer(chats, container) {
        if (!container) return;
        container.innerHTML = '';
        const list = Array.isArray(chats) ? chats : [];
        list.forEach(chat => {
            const el = this.createChatItemElement(chat, false);
            if (el) container.appendChild(el);
        });
        // Açık bölümde max-height temizle
        try {
            const wrap = container.closest('.collapsible-content');
            if (wrap && wrap.classList.contains('open')) wrap.style.removeProperty('max-height');
        } catch(_) {}
    }

    /**
     * Sunucudan gelen geçmiş sohbet listesini render et
     */
    renderHistoryChatsFromServer(chats, container) {
        if (!container) return;
        container.innerHTML = '';
        const list = Array.isArray(chats) ? chats : [];
        list.forEach(chat => {
            const el = this.createChatItemElement(chat, true);
            if (el) container.appendChild(el);
        });
        try {
            const wrap = container.closest('.collapsible-content');
            if (wrap && wrap.classList.contains('open')) wrap.style.removeProperty('max-height');
        } catch(_) {}
    }

    /**
     * Bir chat objesinden uygun sidebar öğesi oluştur
     * @param {Object} chat - { chat_id, model_name, title, last_message_at, ... }
     * @param {boolean} isHistory - true ise history-item, değilse active chat item
     */
    createChatItemElement(chat, isHistory = false) {
        if (!chat) return null;
        const chatId = chat.chat_id || chat.id || '';
        const modelName = chat.model_name || chat.title || 'Chat';
        const code = String(chatId).split('-').pop();
        const preview = '';

        if (isHistory) {
            return DOMUtils.createElement('div', {
                className: 'history-item',
                'data-pane-id': chatId,
                'data-model-name': modelName,
                innerHTML: `
                    <div class="model-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="chat-info">
                        <div class="chat-row">
                            <div class="chat-name">${modelName}</div>
                            <div class="chat-code">#${code}</div>
                        </div>
                        <div class="chat-preview">${preview}</div>
                    </div>
                `
            });
        }
        // Active chat item
        return DOMUtils.createElement('div', {
            className: 'chat-item',
            'data-pane-id': chatId,
            innerHTML: `
                <div class="model-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="chat-info">
                    <div class="chat-row">
                        <div class="chat-name">${modelName}</div>
                        <div class="chat-code">#${code}</div>
                    </div>
                    <div class="chat-preview">${preview}</div>
                </div>
            `
        });
    }

    /**
     * Controller'ı başlat
     */
    async init() {
        this.sidebar = DOMUtils.$('.chat-sidebar');
        if (!this.sidebar) {
            console.error('Sidebar element not found');
            return;
        }

        // Elementleri seç
        this.modelItems = DOMUtils.$$('.model-item');
        this.categoryItems = DOMUtils.$$('.category-item');
        this.chatItems = DOMUtils.$$('.chat-item');
        this.historyItems = DOMUtils.$$('.history-item');
        // Active/History liste elementleri
        this.activeChatListEl = DOMUtils.$('#active-chat-list');
        this.historyListEl = DOMUtils.$('#history-list');
        // Active chat state
        this.activeChats = new Map(); // paneId -> {name, preview, time}

        // Event listener'ları kur
        this.setupEventListeners();
        
        // State listener'ları kur
        this.setupStateListeners();

        // Collapse işlevselliğini başlat
        this.initCollapse();

        // Model listesini render et (eğer modeller yüklenmişse)
        this.renderModels();

        // Kategorileri backend'den yükle
        this.renderCategories();

        // Profil kartını başlat
        this.initProfileCard();

        // Kullanıcıya ait sohbetleri yükle (aktif ve geçmiş)
        try {
            await this.loadUserChats();
        } catch (e) {
            console.warn('Failed to load user chats:', e);
        }

        console.log('SidebarController initialized');
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Model event listener'ları renderModels'da kurulacak
        // setupModelEventListeners() metodunu kullan

        // Category seçimi
        this.categoryItems.forEach(item => {
            DOMUtils.on(item, 'click', (e) => {
                this.handleCategorySelection(e, item);
            });
        });

        // Chat seçimi
        this.chatItems.forEach(item => {
            DOMUtils.on(item, 'click', (e) => {
                this.handleChatSelection(e, item);
            });
        });

        // History seçimi
        this.historyItems.forEach(item => {
            DOMUtils.on(item, 'click', (e) => {
                this.handleHistorySelection(e, item);
            });
        });

        // Pin More Models butonu
        const pinMoreBtn = DOMUtils.$('.pin-more-btn');
        if (pinMoreBtn) {
            DOMUtils.on(pinMoreBtn, 'click', (e) => {
                this.handlePinMoreModels(e);
            });
        }

        // Bottom links removed (Affiliates/Support/Settings)

        // Active chats click (restore)
        if (this.activeChatListEl) {
            DOMUtils.on(this.activeChatListEl, 'click', (e) => {
                const item = e.target.closest && e.target.closest('.chat-item');
                if (!item) return;
                this.handleActiveChatClick(e, item);
            });
        }

        // History clicks (read-only open) - delegated
        if (this.historyListEl) {
            DOMUtils.on(this.historyListEl, 'click', (e) => {
                const item = e.target.closest && e.target.closest('.history-item');
                if (!item) return;
                this.handleHistorySelection(e, item);
            });
        }
    }

    /**
     * State listener'ları kur
     */
    setupStateListeners() {
        // Active model değişikliği
        this.stateManager.subscribe('activeModel', (newModel, oldModel) => {
            this.updateActiveModel(newModel, oldModel);
        });

        // Sidebar collapsed durumu
        this.stateManager.subscribe('sidebarCollapsed', (collapsed) => {
            this.toggleSidebarCollapsed(collapsed);
        });

        // Model service'den models yüklendiğinde render et
        this.eventManager.on('models:loaded', () => {
            this.renderModels();
        });

        // Favoriler güncellenince listeyi yenile
        this.eventManager.on('models:favorite-updated', () => {
            this.renderModels();
        });

        // Bir kullanıcı mesaj gönderdiğinde Active Chats'e ekle/güncelle
        this.eventManager.on('pane:message-sent', (event) => {
            const { pane, message } = event.data || {};
            if (!pane) return;
            this.addOrUpdateActiveChat(pane, message);
        });

        // AI yanıtı geldiğinde önizlemeyi güncelle
        this.eventManager.on('pane:ai-response-received', (event) => {
            const { pane, response } = event.data || {};
            if (!pane) return;
            this.addOrUpdateActiveChat(pane, response);
        });

        // Minimize edilirse ve sohbet başlamışsa Active Chats'te görünür
        this.eventManager.on('pane:minimized', (event) => {
            const { pane } = event.data || {};
            if (!pane) return;
            // History'den açılanlar Active Chats'e eklenmesin
            if (pane.hasUserMessage && !pane.fromHistory) {
                this.addOrUpdateActiveChat(pane);
            }
        });

        // Restore edilince sadece aktifliği vurgula (listeden kaldırma yok)
        this.eventManager.on('pane:restored', (event) => {
            const { paneId } = event.data || {};
            this.highlightActiveChat(paneId);
        });

        // Pane kapandıysa; başlamışsa History'ye ekle, Active'ten kaldır
        this.eventManager.on('pane:closed', (event) => {
            const { pane } = event.data || {};
            if (!pane) return;
            this.removeActiveChat(pane.id);
            // History'den açılanı tekrar history'e ekleme
            if (pane.hasUserMessage && !pane.fromHistory) {
                this.addHistoryEntry(pane);
            }
        });
    }

    /**
     * Collapse işlevselliğini başlat
     */
    initCollapse() {
        const sectionHeaders = DOMUtils.$$('.section-header');
        
        sectionHeaders.forEach(header => {
            DOMUtils.on(header, 'click', (e) => {
                this.handleCollapseToggle(e, header);
            });
        });
    }

    /**
     * Model seçimi işle
     * @param {Event} e - Click event
     * @param {Element} item - Model item
     */
    handleModelSelection(e, item) {
        e.preventDefault();
        
        const modelName = DOMUtils.$('span', item)?.textContent;
        if (!modelName) return;

        // Active class'ı güncelle
        this.modelItems.forEach(model => {
            DOMUtils.removeClass(model, 'active');
        });
        DOMUtils.addClass(item, 'active');

        // State'i güncelle
        this.stateManager.setActiveModel(modelName);

        // Event emit et
        this.eventManager.emit('model:selected', {
            modelName,
            element: item
        });

        console.log('Model selected:', modelName);
    }

    /**
     * Category seçimi işle
     * @param {Event} e - Click event
     * @param {Element} item - Category item
     */
    handleCategorySelection(e, item) {
        e.preventDefault();
        
        const categoryName = DOMUtils.$('span', item)?.textContent;
        if (!categoryName) return;

        // Active class'ı güncelle
        this.categoryItems.forEach(category => {
            DOMUtils.removeClass(category, 'active');
        });
        DOMUtils.addClass(item, 'active');

        // Event emit et (sadece seçim bilgisi)
        this.eventManager.emit('category:selected', {
            categoryName,
            element: item
        });
        console.log('Category selected:', categoryName);
    }

    /**
     * Chat seçimi işle
     * @param {Event} e - Click event
     * @param {Element} item - Chat item
     */
    handleChatSelection(e, item) {
        e.preventDefault();
        
        const chatName = DOMUtils.$('.chat-name', item)?.textContent;
        if (!chatName) return;

        // Active class'ı güncelle
        this.chatItems.forEach(chat => {
            DOMUtils.removeClass(chat, 'active');
        });
        DOMUtils.addClass(item, 'active');

        // Event emit et
        this.eventManager.emit('chat:selected', {
            chatName,
            element: item
        });

        console.log('Chat selected:', chatName);
    }

    /**
     * History seçimi işle
     * @param {Event} e - Click event
     * @param {Element} item - History item
     */
    handleHistorySelection(e, item) {
        e.preventDefault();
        const paneId = item.getAttribute('data-pane-id');
        const modelName = item.getAttribute('data-model-name') || DOMUtils.$('span', item)?.textContent;
        if (!paneId) return;

        // Active class'ı güncelle (dinamik liste)
        try {
            const items = this.historyListEl ? this.historyListEl.querySelectorAll('.history-item') : [];
            items.forEach(el => el.classList.remove('active'));
        } catch(_) {}
        item.classList.add('active');

        // Event emit et
        this.eventManager.emit('history:selected', {
            paneId,
            modelName,
            element: item
        });

        console.log('History selected:', paneId, modelName);
    }

    /**
     * Pin More Models işle
     * @param {Event} e - Click event
     */
    handlePinMoreModels(e) {
        e.preventDefault();
        
        // Event emit et
        this.eventManager.emit('models:pin-more', {
            element: e.target
        });

        console.log('Pin More Models clicked');
    }

    // Old bottom link handler removed

    /**
     * Collapse toggle işle
     * @param {Event} e - Click event
     * @param {Element} header - Section header
     */
    handleCollapseToggle(e, header) {
        e.preventDefault();
        
        const targetId = header.dataset.target;
        const content = DOMUtils.$(`#${targetId}`);
        const icon = DOMUtils.$('.collapse-icon', header);
        
        if (!content) return;

        // Toggle active/open classes only; no inline heights
        DOMUtils.toggleClass(header, 'active');
        DOMUtils.toggleClass(content, 'open');
        // Clear legacy inline style to avoid stale heights
        try { content.style.removeProperty('max-height'); } catch(_) {}

        // Event emit et
        this.eventManager.emit('sidebar:collapse-toggle', {
            targetId,
            isOpen: content.classList.contains('open'),
            element: header
        });
    }

    /**
     * Active model'i güncelle
     * @param {string} newModel - Yeni model
     * @param {string} oldModel - Eski model
     */
    updateActiveModel(newModel, oldModel) {
        // Eski model'i deaktive et
        if (oldModel) {
            const oldItem = Array.from(this.modelItems).find(item => 
                DOMUtils.$('span', item)?.textContent === oldModel
            );
            if (oldItem) {
                DOMUtils.removeClass(oldItem, 'active');
            }
        }

        // Yeni model'i aktif et
        if (newModel) {
            const newItem = Array.from(this.modelItems).find(item => 
                DOMUtils.$('span', item)?.textContent === newModel
            );
            if (newItem) {
                DOMUtils.addClass(newItem, 'active');
            }
        }
    }

    /**
     * Sidebar collapsed durumunu güncelle
     * @param {boolean} collapsed - Collapsed durumu
     */
    toggleSidebarCollapsed(collapsed) {
        if (collapsed) {
            DOMUtils.addClass(this.sidebar, 'collapsed');
        } else {
            DOMUtils.removeClass(this.sidebar, 'collapsed');
        }
    }

    /**
     * Sidebar'ı toggle et
     */
    toggleSidebar() {
        const currentState = this.stateManager.getState('sidebarCollapsed');
        this.stateManager.setSidebarCollapsed(!currentState);
    }

    /**
     * Model listesini render et
     */
    async renderModels() {
        try {
            // Model service'den modelleri al
            const modelService = window.ZekaiApp?.services?.modelService;
            if (!modelService) {
                console.warn('ModelService not available');
                return;
            }

            const models = modelService.getModels({ available: true });
            console.log('Rendering models:', models);
            this.updateModelList(models);
        } catch (error) {
            console.error('Error rendering models:', error);
        }
    }

    /**
     * Model listesini güncelle
     * @param {Array} models - Model listesi
     */
    updateModelList(models) {
        console.log('updateModelList called with:', models);

        const favList = DOMUtils.$('#favorite-model-list');
        const allList = DOMUtils.$('#all-model-list');
        if (!favList || !allList) {
            console.error('Favorite or All model list containers not found');
            return;
        }

        // Temizle
        favList.innerHTML = '';
        allList.innerHTML = '';

        if (!models || models.length === 0) {
            favList.innerHTML = `<div class="no-models">${i18n.t('no_favorite_models')}</div>`;
            allList.innerHTML = `<div class="no-models">${i18n.t('no_models_found')}</div>`;
            return;
        }

        const favoriteIds = new Set(this.getFavoriteModelIds());

        // Modelleri alfabetik sıraya koy (performans maliyeti minimal)
        const sorted = [...models].sort((a, b) => (a.name || '').localeCompare(b.name || ''));

        // Her model için HTML oluştur
        sorted.forEach(model => {
            const isFav = favoriteIds.has(String(model.id));
            const allItem = this.createModelItem(model, isFav);
            allList.appendChild(allItem);

            if (isFav) {
                const favItem = this.createModelItem(model, true);
                favList.appendChild(favItem);
            }
        });

        // Model item'ları güncelle (hem favoriler hem tüm listede)
        this.modelItems = DOMUtils.$$('.model-item');

        // Event listener'ları yeniden kur
        this.setupModelEventListeners();

        // Favoriler bölümü boşsa küçük bir bilgi göster
        if (!favList.children.length) {
            favList.innerHTML = `<div class="no-models">${i18n.t('fav_hint')}</div>`;
        }

        console.log('Model lists updated:', sorted.length, 'models');
    }

    /**
     * Model item HTML'i oluştur
     * @param {Object} model - Model objesi
     * @returns {Element} Model item elementi
     */
    createModelItem(model, isFavorite = false) {
        const hasLogo = !!model.logoUrl;
        const iconHtml = hasLogo
            ? `<img class="model-logo" src="${model.logoUrl}" alt="${(model.name || 'model')} logo" />`
            : `<i class="${model.icon}"></i>`;

        const modelItem = DOMUtils.createElement('div', {
            className: 'model-item',
            'data-model-id': model.id,
            'data-model-name': model.model_name || model.name,
            innerHTML: `
                <div class="model-icon">
                    ${iconHtml}
                </div>
                <span>${model.name}</span>
                <button class="fav-toggle${isFavorite ? ' is-fav' : ''}" aria-label="${i18n.t('favorite')}" title="${i18n.t('favorite')}" data-model-id="${model.id}">
                    <i class="fas fa-star"></i>
                </button>
            `
        });

        return modelItem;
    }

    /**
     * Kategorileri backend'den yükle ve render et
     */
    async renderCategories() {
        try {
            const container = DOMUtils.$('.category-list');
            if (!container) return;
            container.innerHTML = `<div class="no-models">${i18n.t('categories_loading')}</div>`;

            const res = await fetch('/api/categories/');
            const json = await res.json();
            if (!json.success) {
                container.innerHTML = `<div class="no-models">${i18n.t('categories_failed')}</div>`;
                return;
            }

            const cats = Array.isArray(json.data) ? json.data : [];
            if (!cats.length) {
                container.innerHTML = `<div class="no-models">${i18n.t('categories_empty')}</div>`;
                return;
            }

            container.innerHTML = '';
            cats.forEach(cat => {
                const item = DOMUtils.createElement('div', {
                    className: 'category-item',
                    'data-category-id': cat.category_id,
                    'data-category-name': cat.name,
                    innerHTML: `
                        <i class="fas fa-folder"></i>
                        <span>${cat.name}</span>
                    `
                });
                DOMUtils.on(item, 'click', async (e) => {
                    this.handleCategorySelection(e, item);
                    // Modal açmadan önce veriyi hazırla
                    const categoryName = cat.name;
                    const categoryId = cat.category_id;
                    if (!this.categoryModelsCache.has(categoryId)) {
                        item.classList.add('loading');
                        try {
                            await this.prefetchCategoryModels(categoryId);
                        } finally {
                            item.classList.remove('loading');
                        }
                    }
                    const initialModels = this.categoryModelsCache.get(categoryId) || [];
                    this.eventManager.emit('modal:show', {
                        type: 'category-models',
                        title: i18n.t('category_models_title', { category: categoryName }),
                        options: { category: categoryName, categoryId, initialModels }
                    });
                });
                container.appendChild(item);
                // Prefetch models for this category in background
                this.prefetchCategoryModels(cat.category_id);
            });
        } catch (e) {
            console.error('Kategoriler yüklenemedi', e);
        }
    }

    /**
     * Kategori modellerini arka planda önceden yükle ve cache'e koy
     */
    async prefetchCategoryModels(categoryId) {
        if (!categoryId) return;
        if (this.categoryModelsCache.has(categoryId)) return; // already cached
        if (this.categoryModelsPromises.has(categoryId)) return; // in-flight
        const promise = (async () => {
            try {
                const res = await fetch(`/api/categories/${categoryId}/models`);
                const json = await res.json();
                if (json && json.success && Array.isArray(json.data)) {
                    this.categoryModelsCache.set(categoryId, json.data);
                } else {
                    this.categoryModelsCache.set(categoryId, []);
                }
            } catch (err) {
                this.categoryModelsCache.set(categoryId, []);
            } finally {
                this.categoryModelsPromises.delete(categoryId);
            }
        })();
        this.categoryModelsPromises.set(categoryId, promise);
        await promise;
    }

    /** Favori model ID'lerini getir */
    getFavoriteModelIds() {
        const ids = Helpers.getStorage('favorite_models');
        return Array.isArray(ids) ? ids : [];
    }

    /** Favori model ID'lerini kaydet */
    setFavoriteModelIds(ids) {
        Helpers.setStorage('favorite_models', ids);
    }

    /** Favori durumunu değiştir */
    toggleFavorite(modelId) {
        const ids = new Set(this.getFavoriteModelIds());
        if (ids.has(modelId)) {
            ids.delete(modelId);
        } else {
            ids.add(modelId);
        }
        this.setFavoriteModelIds([...ids]);
        this.renderModels();
    }

    /**
     * Model event listener'larını kur
     */
    setupModelEventListeners() {
        this.modelItems.forEach(item => {
            // Model seçimi
            DOMUtils.on(item, 'click', (e) => {
                // Favori toggle'a tıklanırsa seçim yapma
                const target = e.target;
                if (target && (target.closest && target.closest('.fav-toggle'))) return;
                this.handleModelSelection(e, item);
            });

            // Favori toggle
            const favBtn = item.querySelector('.fav-toggle');
            if (favBtn) {
                DOMUtils.on(favBtn, 'click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const id = String(favBtn.getAttribute('data-model-id'));
                    this.toggleFavorite(id);
                });
            }
        });
    }

    /**
     * Chat listesini güncelle
     * @param {Array} chats - Chat listesi
     */
    updateChatList(chats) {
        // Bu fonksiyon dinamik chat listesi için kullanılabilir
        console.log('Updating chat list:', chats);
    }

    /**
     * History listesini güncelle
     * @param {Array} history - History listesi
     */
    updateHistoryList(history) {
        // Bu fonksiyon dinamik history listesi için kullanılabilir
        console.log('Updating history list:', history);
    }

    /** Active chat item tıklandığında restore isteği gönder */
    handleActiveChatClick(e, item) {
        e.preventDefault();
        const paneId = item.getAttribute('data-pane-id');
        if (!paneId) return;
        this.eventManager.emit('pane:restore-requested', { paneId });
        this.highlightActiveChat(paneId);
    }

    /** Active Chats: ekle veya güncelle */
    addOrUpdateActiveChat(pane, lastText = null) {
        if (!this.activeChatListEl || !pane) return;
        // Sadece kullanıcı mesajı varsa listede yer almalı
        if (!pane.hasUserMessage) return;

        const paneId = pane.id;
        const existing = this.activeChatListEl.querySelector(`.chat-item[data-pane-id="${paneId}"]`);
        const meta = this.getModelMeta(pane);
        const preview = (typeof lastText === 'string' ? lastText : (pane.messages[pane.messages.length - 1]?.content || ''))
            .toString().slice(0, 80);
        const code = String(paneId).split('-').pop();

        if (existing) {
            // Güncelle
            const previewEl = existing.querySelector('.chat-preview');
            if (previewEl) previewEl.textContent = preview;
            // Her yeni aktivitede en üste taşı
            this.activeChatListEl.prepend(existing);
        } else {
            // Oluştur
            const item = DOMUtils.createElement('div', {
                className: 'chat-item',
                'data-pane-id': paneId,
                innerHTML: `
                    <div class="model-icon">
                        ${meta.logoUrl ? `<img class="model-logo" src="${meta.logoUrl}" alt="${(pane.modelName || 'model')} logo" />` : `<i class="${meta.icon || 'fas fa-robot'}"></i>`}
                    </div>
                    <div class="chat-info">
                        <div class="chat-row">
                            <div class="chat-name">${pane.modelName}</div>
                            <div class="chat-code">#${code}</div>
                        </div>
                        <div class="chat-preview">${preview}</div>
                    </div>
                `
            });
            this.activeChatListEl.prepend(item);
        }

        // State'i sakla
        this.activeChats.set(paneId, {
            name: pane.modelName,
            preview,
            time: Date.now()
        });

        // Section açıksa, inline maxHeight'i temizle ki güncel içerik görünsün
        try {
            const container = this.activeChatListEl.closest('.collapsible-content');
            if (container && container.classList.contains('open')) {
                container.style.removeProperty('max-height');
            }
        } catch(_) {}
    }

    /** Active Chats: kaldır */
    removeActiveChat(paneId) {
        if (!this.activeChatListEl) return;
        const el = this.activeChatListEl.querySelector(`.chat-item[data-pane-id="${paneId}"]`);
        if (el) el.remove();
        this.activeChats.delete(paneId);
    }

    /** History: ekle (basit düz liste) */
    addHistoryEntry(pane) {
        if (!this.historyListEl || !pane) return;
        const last = pane.messages[pane.messages.length - 1];
        const preview = (last?.content || '').toString().slice(0, 80);
        const meta = this.getModelMeta(pane);
        const code = String(pane.id).split('-').pop();

        const item = DOMUtils.createElement('div', {
            className: 'history-item',
            'data-pane-id': pane.id,
            'data-model-name': pane.modelName,
            innerHTML: `
                <div class="model-icon">
                    ${meta.logoUrl ? `<img class="model-logo" src="${meta.logoUrl}" alt="${(pane.modelName || 'model')} logo" />` : `<i class="${meta.icon || 'fas fa-robot'}"></i>`}
                </div>
                <div class="chat-info">
                    <div class="chat-row">
                        <div class="chat-name">${pane.modelName}</div>
                        <div class="chat-code">#${code}</div>
                    </div>
                    <div class="chat-preview">${preview}</div>
                </div>
            `
        });
        this.historyListEl.prepend(item);

        // Section açıksa, inline maxHeight'i temizle ki güncel içerik görünsün
        try {
            const container = this.historyListEl.closest('.collapsible-content');
            if (container && container.classList.contains('open')) {
                container.style.removeProperty('max-height');
            }
        } catch(_) {}
    }

    /** Aktif chat item'ı görsel olarak vurgula */
    highlightActiveChat(paneId) {
        if (!this.activeChatListEl) return;
        const items = this.activeChatListEl.querySelectorAll('.chat-item');
        items.forEach(i => i.classList.remove('active'));
        const target = this.activeChatListEl.querySelector(`.chat-item[data-pane-id="${paneId}"]`);
        if (target) target.classList.add('active');
    }

    /** Model meta bilgisi */
    getModelMeta(pane) {
        try {
            const modelService = window.ZekaiApp?.services?.modelService;
            const models = modelService?.models || [];
            const idStr = `model-${pane.modelId}`;
            const found = models.find(m => m.modelId === pane.modelId || m.id === idStr || (m.name || '').toLowerCase() === (pane.modelName || '').toLowerCase());
            return found || {};
        } catch (e) {
            return {};
        }
    }

    /**
     * Controller'ı temizle
     */
    destroy() {
        // Event listener'ları kaldır
        this.modelItems.forEach(item => {
            DOMUtils.off(item, 'click');
        });
        
        this.categoryItems.forEach(item => {
            DOMUtils.off(item, 'click');
        });
        
        this.chatItems.forEach(item => {
            DOMUtils.off(item, 'click');
        });
        
        this.historyItems.forEach(item => {
            DOMUtils.off(item, 'click');
        });

        console.log('SidebarController destroyed');
    }

    /**
     * Profil kartını başlat ve ayarları bağla
     */
    initProfileCard() {
        const card = DOMUtils.$('.profile-card');
        if (!card) return;

        // Profil bilgisi: Sunucu-temelli (template) bilgiye öncelik ver
        const defaultProfile = { name: 'Zekai User', email: 'user@example.com' };
        const storedProfile = Helpers.getStorage('profile_mock', null);

        const nameEl = DOMUtils.$('#profile-name');
        const emailEl = DOMUtils.$('#profile-email');
        const avatarEl = DOMUtils.$('#profile-avatar');

        const currentName = (nameEl && (nameEl.textContent || '').trim()) || '';
        const currentEmail = (emailEl && (emailEl.textContent || '').trim()) || '';
        const hasServerProfile = !!currentEmail && currentEmail !== defaultProfile.email;
        const profile = hasServerProfile
            ? { name: currentName || defaultProfile.name, email: currentEmail }
            : (storedProfile || defaultProfile);

        if (nameEl) nameEl.textContent = profile.name || defaultProfile.name;
        if (emailEl) emailEl.textContent = profile.email || defaultProfile.email;
        if (avatarEl) {
            const initials = (profile.name || defaultProfile.name)
                .split(/\s+/)
                .map(p => p[0])
                .slice(0, 2)
                .join('')
                .toUpperCase();
            avatarEl.textContent = initials || 'ZU';
        }

        // Settings load
        const defaults = { darkMode: false, notifications: true, language: 'tr' };
        const settings = Object.assign({}, defaults, Helpers.getStorage('user_settings', defaults) || {});

        const toggleDark = DOMUtils.$('#toggle-darkmode');
        const toggleNotif = DOMUtils.$('#toggle-notifications');
        const selectLang = DOMUtils.$('#select-language');
        const logoutBtn = DOMUtils.$('#btn-logout');
        const header = DOMUtils.$('.profile-header', card);

        // Apply stored settings to UI
        if (toggleDark) toggleDark.checked = !!settings.darkMode;
        if (toggleNotif) toggleNotif.checked = !!settings.notifications;
        if (selectLang) selectLang.value = settings.language || 'tr';

        // Apply theme to document
        try {
            if (settings.darkMode) {
                document.body.classList.add('dark-theme');
            } else {
                document.body.classList.remove('dark-theme');
            }
        } catch (_) {}

        // Restore open/closed state (default: closed)
        try {
            const openStored = Helpers.getStorage('profile_card_open', false);
            card.classList.toggle('open', !!openStored);
        } catch (_) {
            // leave closed by default
        }

        // Events
        if (header) {
            DOMUtils.on(header, 'click', () => {
                const nextOpen = !card.classList.contains('open');
                card.classList.toggle('open', nextOpen);
                try { Helpers.setStorage('profile_card_open', nextOpen); } catch (_) {}
            });
        }

        if (toggleDark) {
            DOMUtils.on(toggleDark, 'change', () => {
                const newVal = !!toggleDark.checked;
                settings.darkMode = newVal;
                Helpers.setStorage('user_settings', settings);
                try {
                    document.body.classList.toggle('dark-theme', newVal);
                } catch (_) {}
                this.stateManager.addNotification?.({
                    type: 'info',
                    message: newVal ? i18n.t('dark_mode_on') : i18n.t('dark_mode_off')
                });
            });
        }

        if (toggleNotif) {
            DOMUtils.on(toggleNotif, 'change', () => {
                const newVal = !!toggleNotif.checked;
                settings.notifications = newVal;
                Helpers.setStorage('user_settings', settings);
                this.stateManager.addNotification?.({
                    type: 'success',
                    message: newVal ? i18n.t('notifications_on') : i18n.t('notifications_off')
                });
            });
        }

        if (selectLang) {
            DOMUtils.on(selectLang, 'change', () => {
                const val = selectLang.value || 'tr';
                settings.language = val;
                Helpers.setStorage('user_settings', settings);
                this.stateManager.addNotification?.({
                    type: 'info',
                    message: i18n.t('language_changed', { lang: (val || 'tr').toUpperCase() })
                });
                // İleride: i18n sistemi bağlanırsa event yayınlanabilir
                this.eventManager.emit('settings:language-changed', { language: val });
            });
        }

        if (logoutBtn) {
            DOMUtils.on(logoutBtn, 'click', (e) => {
                e.preventDefault();
                // Sunucu tarafında oturumu kapat
                try {
                    window.location.href = '/auth/logout';
                } catch (_) {
                    // Yedek: sayfayı yenile
                    window.location.assign('/auth/logout');
                }
            });
        }

        // Admin: profil ayarlarına Admin Panel bağlantısı ekle
        try {
            fetch('/auth/check-auth')
                .then(res => res.ok ? res.json() : null)
                .then(data => {
                    if (!data || !data.authenticated || !data.user || !data.user.is_admin) return;
                    const settingsWrap = DOMUtils.$('.profile-settings', card);
                    if (!settingsWrap) return;
                    // Eğer daha önce eklenmişse tekrar ekleme
                    if (settingsWrap.querySelector('.admin-link')) return;
                    const adminLink = DOMUtils.createElement('a', {
                        className: 'setting-item admin-link',
                        href: '/admin/',
                        innerHTML: `
                            <div class="setting-label">
                                <i class="fas fa-gauge-high"></i>
                                <span>Admin Paneli</span>
                            </div>
                        `
                    });
                    // Logout butonundan önce ekle
                    const logoutParent = logoutBtn ? logoutBtn.parentElement : null;
                    if (logoutParent && logoutBtn) {
                        settingsWrap.insertBefore(adminLink, logoutBtn);
                    } else {
                        settingsWrap.appendChild(adminLink);
                    }
                })
                .catch(() => {});
        } catch (_) {}
    }
}
