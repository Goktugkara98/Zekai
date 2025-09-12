/**
 * Sidebar Controller
 * Sidebar UI kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';

export class SidebarController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.sidebar = null;
        this.modelItems = [];
        this.categoryItems = [];
        this.chatItems = [];
        this.historyItems = [];
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

        // Event listener'ları kur
        this.setupEventListeners();
        
        // State listener'ları kur
        this.setupStateListeners();

        // Collapse işlevselliğini başlat
        this.initCollapse();

        // Model listesini render et (eğer modeller yüklenmişse)
        this.renderModels();

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

        // Bottom links
        const bottomLinks = DOMUtils.$$('.bottom-link');
        bottomLinks.forEach(link => {
            DOMUtils.on(link, 'click', (e) => {
                this.handleBottomLinkClick(e, link);
            });
        });
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

        // Event emit et
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
        
        const historyName = DOMUtils.$('span', item)?.textContent;
        if (!historyName) return;

        // Active class'ı güncelle
        this.historyItems.forEach(history => {
            DOMUtils.removeClass(history, 'active');
        });
        DOMUtils.addClass(item, 'active');

        // Event emit et
        this.eventManager.emit('history:selected', {
            historyName,
            element: item
        });

        console.log('History selected:', historyName);
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

    /**
     * Bottom link click işle
     * @param {Event} e - Click event
     * @param {Element} link - Link element
     */
    handleBottomLinkClick(e, link) {
        e.preventDefault();
        
        const linkText = DOMUtils.$('span', link)?.textContent;
        if (!linkText) return;

        // Event emit et
        this.eventManager.emit('bottom-link:clicked', {
            linkText,
            element: link
        });

        console.log('Bottom link clicked:', linkText);
    }

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

        // Toggle active class
        DOMUtils.toggleClass(header, 'active');
        
        // Toggle content visibility
        if (DOMUtils.toggleClass(content, 'open')) {
            content.style.maxHeight = content.scrollHeight + 'px';
        } else {
            content.style.maxHeight = '0';
        }

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
        
        const modelList = DOMUtils.$('#model-list');
        if (!modelList) {
            console.error('Model list container not found');
            return;
        }

        console.log('Model list container found:', modelList);

        // Mevcut model item'ları temizle
        modelList.innerHTML = '';

        if (!models || models.length === 0) {
            console.log('No models available, showing placeholder');
            modelList.innerHTML = '<div class="no-models">No models available</div>';
            return;
        }

        console.log('Creating model items for', models.length, 'models');

        // Her model için HTML oluştur
        models.forEach(model => {
            const modelItem = this.createModelItem(model);
            modelList.appendChild(modelItem);
        });

        // Model item'ları güncelle
        this.modelItems = DOMUtils.$$('.model-item');
        
        // Event listener'ları yeniden kur
        this.setupModelEventListeners();

        console.log('Model list updated:', models.length, 'models');
    }

    /**
     * Model item HTML'i oluştur
     * @param {Object} model - Model objesi
     * @returns {Element} Model item elementi
     */
    createModelItem(model) {
        const modelItem = DOMUtils.createElement('div', {
            className: 'model-item',
            'data-model-id': model.id,
            'data-model-name': model.model_name || model.name,
            innerHTML: `
                <div class="model-icon" style="background-color: ${model.color}20; color: ${model.color}">
                    <i class="${model.icon}"></i>
                </div>
                <span>${model.name}</span>
            `
        });

        return modelItem;
    }

    /**
     * Model event listener'larını kur
     */
    setupModelEventListeners() {
        this.modelItems.forEach(item => {
            DOMUtils.on(item, 'click', (e) => {
                this.handleModelSelection(e, item);
            });
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
}
