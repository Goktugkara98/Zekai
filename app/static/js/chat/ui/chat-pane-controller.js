/**
 * Chat Pane Controller
 * Chat panelleri kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';

export class ChatPaneController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.chatPanesContainer = null;
        this.activePane = null;
        this.chatCounter = 1;
    }

    /**
     * Controller'ı başlat
     */
    async init() {
        this.chatPanesContainer = DOMUtils.$('.chat-panes-container');
        if (!this.chatPanesContainer) {
            console.error('Chat panes container not found');
            return;
        }

        // Event listener'ları kur
        this.setupEventListeners();
        
        // State listener'ları kur
        this.setupStateListeners();

        console.log('ChatPaneController initialized');
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Model seçimi event'i
        this.eventManager.on('model:selected', (event) => {
            this.handleModelSelection(event.data);
        });

        // Chat seçimi event'i
        this.eventManager.on('chat:selected', (event) => {
            this.handleChatSelection(event.data);
        });

        // Layout değişikliği event'i
        this.eventManager.on('layout:changed', (event) => {
            this.handleLayoutChange(event.data);
        });
    }

    /**
     * State listener'ları kur
     */
    setupStateListeners() {
        // Active model değişikliği
        this.stateManager.subscribe('activeModel', (newModel) => {
            if (newModel) {
                this.createChatPane(newModel);
            }
        });

        // Messages değişikliği
        this.stateManager.subscribe('messages', (messages) => {
            this.updateMessages(messages);
        });

        // Typing durumu
        this.stateManager.subscribe('isTyping', (isTyping) => {
            this.updateTypingIndicator(isTyping);
        });
    }

    /**
     * Model seçimi işle
     * @param {Object} data - Event data
     */
    handleModelSelection(data) {
        const { modelName } = data;
        this.createChatPane(modelName);
    }

    /**
     * Chat seçimi işle
     * @param {Object} data - Event data
     */
    handleChatSelection(data) {
        const { chatName } = data;
        // Chat yükleme işlemi burada yapılabilir
        console.log('Loading chat:', chatName);
    }

    /**
     * Layout değişikliği işle
     * @param {Object} data - Event data
     */
    handleLayoutChange(data) {
        const { layout } = data;
        this.applyLayout(layout);
    }

    /**
     * Chat pane oluştur
     * @param {string} modelName - Model adı
     */
    createChatPane(modelName) {
        // Mevcut pane'i temizle
        DOMUtils.clear(this.chatPanesContainer);

        // Yeni pane oluştur
        const chatPane = DOMUtils.createElement('div', {
            className: 'chat-pane'
        }, '');

        chatPane.innerHTML = `
            <div class="pane-header">
                <div class="pane-title-section">
                    <div class="model-info">
                        <span class="model-name">${modelName}</span>
                        <span class="chat-number">Chat #${this.chatCounter}</span>
                    </div>
                </div>
                <div class="pane-controls">
                    <button class="control-btn minimize-btn" title="Minimize">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="control-btn close-btn" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="pane-content">
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-comments"></i>
                    </div>
                    <p>Start a conversation with ${modelName}</p>
                </div>
            </div>
        `;

        // Chat counter'ı artır
        this.chatCounter++;

        this.chatPanesContainer.appendChild(chatPane);
        this.activePane = chatPane;

        // Pane event listener'ları kur
        this.setupPaneEventListeners(chatPane);

        // Event emit et
        this.eventManager.emit('pane:created', {
            modelName,
            element: chatPane
        });
    }

    /**
     * Pane event listener'ları kur
     * @param {Element} pane - Chat pane
     */
    setupPaneEventListeners(pane) {
        const controlBtns = DOMUtils.$$('.control-btn', pane);
        controlBtns.forEach(btn => {
            DOMUtils.on(btn, 'click', (e) => {
                this.handleControlButtonClick(e, btn);
            });
        });
    }

    /**
     * Control button click işle
     * @param {Event} e - Click event
     * @param {Element} btn - Button element
     */
    handleControlButtonClick(e, btn) {
        e.preventDefault();
        
        const icon = DOMUtils.$('i', btn);
        if (!icon) return;

        const iconClass = icon.className;
        
        if (iconClass.includes('minus')) {
            this.handleMinimizePane();
        } else if (iconClass.includes('times')) {
            this.handleClosePane();
        }
    }

    /**
     * Pane küçültme işle
     */
    handleMinimizePane() {
        if (!this.activePane) return;

        // Eğer zaten minimize ise restore et
        if (this.activePane.classList.contains('minimized')) {
            this.handleRestorePane();
        } else {
            // Pane'i küçült
            DOMUtils.addClass(this.activePane, 'minimized');
            
            // Event emit et
            this.eventManager.emit('pane:minimized', {
                element: this.activePane
            });

            console.log('Pane minimized');
        }
    }

    /**
     * Pane restore işle
     */
    handleRestorePane() {
        if (!this.activePane) return;

        // Pane'i restore et
        DOMUtils.removeClass(this.activePane, 'minimized');
        
        // Event emit et
        this.eventManager.emit('pane:restored', {
            element: this.activePane
        });

        console.log('Pane restored');
    }

    /**
     * Pane kapatma işle
     */
    handleClosePane() {
        if (!this.activePane) return;

        // Pane'i kapat
        this.closePane(this.activePane);
        
        // Event emit et
        this.eventManager.emit('pane:closed', {
            element: this.activePane
        });

        console.log('Pane closed');
    }

    /**
     * Pane kapat
     * @param {Element} pane - Pane elementi
     */
    closePane(pane) {
        if (!pane) return;

        // Pane'i container'dan kaldır
        if (pane.parentNode) {
            pane.parentNode.removeChild(pane);
        }

        // Active pane'i temizle
        this.activePane = null;

        // Empty state'i göster
        this.showEmptyState();
    }

    /**
     * Empty state'i göster
     */
    showEmptyState() {
        if (!this.chatPanesContainer) return;

        this.chatPanesContainer.innerHTML = `
            <div class="empty-chat-state">
                <div class="empty-chat-icon">
                    <i class="fas fa-comments"></i>
                </div>
                <h2>Welcome to Zekai.ai</h2>
                <p>Select a model from the sidebar to start chatting</p>
            </div>
        `;
    }

    /**
     * Chat pane oluştur
     * @param {string} modelName - Model adı
     */
    createChatPane(modelName) {
        if (!this.chatPanesContainer) return;

        // Mevcut içeriği temizle
        this.chatPanesContainer.innerHTML = '';

        // Yeni pane oluştur
        const chatPane = DOMUtils.createElement('div', {
            className: 'chat-pane'
        }, '');

        chatPane.innerHTML = `
            <div class="pane-header">
                <div class="pane-title-section">
                    <div class="model-info">
                        <span class="model-name">${modelName}</span>
                        <span class="chat-number">Chat #${this.chatCounter}</span>
                    </div>
                </div>
                <div class="pane-controls">
                    <button class="control-btn minimize-btn" title="Minimize">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="control-btn close-btn" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="pane-content">
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-comments"></i>
                    </div>
                    <p>Start a conversation with ${modelName}</p>
                </div>
            </div>
        `;

        // Chat counter'ı artır
        this.chatCounter++;

        this.chatPanesContainer.appendChild(chatPane);
        this.activePane = chatPane;

        // Pane event listener'ları kur
        this.setupPaneEventListeners(chatPane);

        // Event emit et
        this.eventManager.emit('pane:created', {
            element: chatPane,
            modelName: modelName
        });

        console.log(`Chat pane created for ${modelName}`);
    }


    /**
     * Mesajları güncelle
     * @param {Array} messages - Mesaj listesi
     */
    updateMessages(messages) {
        if (!this.activePane) return;

        const paneContent = DOMUtils.$('.pane-content', this.activePane);
        if (!paneContent) return;

        // Empty state'i kaldır
        const emptyState = DOMUtils.$('.empty-state', paneContent);
        if (emptyState) {
            emptyState.remove();
        }

        // Mesajları ekle
        messages.forEach(message => {
            this.addMessageToPane(message);
        });

        // Scroll to bottom
        this.scrollToBottom();
    }

    /**
     * Pane'e mesaj ekle
     * @param {Object} message - Mesaj objesi
     */
    addMessageToPane(message) {
        if (!this.activePane) return;

        const paneContent = DOMUtils.$('.pane-content', this.activePane);
        if (!paneContent) return;

        const messageElement = DOMUtils.createElement('div', {
            className: `message ${message.isUser ? 'user' : 'assistant'} fade-in`
        }, '');

        messageElement.innerHTML = `
            <div class="message-content">${message.content}</div>
            <div class="message-time">${Helpers.formatDate(message.timestamp, 'HH:mm')}</div>
        `;

        paneContent.appendChild(messageElement);
    }

    /**
     * Typing indicator'ı güncelle
     * @param {boolean} isTyping - Typing durumu
     */
    updateTypingIndicator(isTyping) {
        if (!this.activePane) return;

        const paneContent = DOMUtils.$('.pane-content', this.activePane);
        if (!paneContent) return;

        // Mevcut typing indicator'ı kaldır
        const existingIndicator = DOMUtils.$('.typing-indicator', paneContent);
        if (existingIndicator) {
            existingIndicator.remove();
        }

        if (isTyping) {
            // Yeni typing indicator ekle
            const typingIndicator = DOMUtils.createElement('div', {
                className: 'message assistant typing-indicator'
            }, '');

            typingIndicator.innerHTML = `
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;

            paneContent.appendChild(typingIndicator);
            this.scrollToBottom();
        }
    }

    /**
     * Scroll to bottom
     */
    scrollToBottom() {
        if (!this.activePane) return;

        const paneContent = DOMUtils.$('.pane-content', this.activePane);
        if (paneContent) {
            paneContent.scrollTop = paneContent.scrollHeight;
        }
    }

    /**
     * Layout uygula
     * @param {string} layout - Layout adı
     */
    applyLayout(layout) {
        // Layout class'larını kaldır
        this.chatPanesContainer.className = 'chat-panes-container';
        
        // Yeni layout class'ı ekle
        if (layout !== 'single') {
            DOMUtils.addClass(this.chatPanesContainer, layout);
        }

        // Event emit et
        this.eventManager.emit('layout:applied', {
            layout,
            element: this.chatPanesContainer
        });
    }

    /**
     * Pane'i temizle
     */
    clearPane() {
        if (this.activePane) {
            const paneContent = DOMUtils.$('.pane-content', this.activePane);
            if (paneContent) {
                paneContent.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-comments"></i>
                        </div>
                        <p>Start a conversation</p>
                    </div>
                `;
            }
        }
    }

    /**
     * Controller'ı temizle
     */
    destroy() {
        // Event listener'ları kaldır
        if (this.activePane) {
            const controlBtns = DOMUtils.$$('.control-btn', this.activePane);
            controlBtns.forEach(btn => {
                DOMUtils.off(btn, 'click');
            });
        }

        console.log('ChatPaneController destroyed');
    }
}
