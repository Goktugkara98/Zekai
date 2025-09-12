/**
 * Chat Pane Controller
 * Chat panelleri kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';
import { ChatPane } from '../core/chat-pane.js';

export class ChatPaneController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.chatPanesContainer = null;
        this.activePane = null;
        this.chatPanes = new Map(); // paneId -> ChatPane object mapping
        this.chatCounter = 1;
        this.maxPanes = 4; // Maksimum 4 pane
        this.currentLayout = 'single';
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

        // Pane focus event'i
        this.eventManager.on('pane:focus', (event) => {
            this.handlePaneFocus(event.data);
        });

        // Pane close request event'i
        this.eventManager.on('pane:close-requested', (event) => {
            this.handlePaneCloseRequest(event.data);
        });
    }

    /**
     * State listener'ları kur
     */
    setupStateListeners() {
        // Active model değişikliği - kaldırıldı çünkü handleModelSelection'da zaten yapılıyor

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
        console.log('ChatPaneController handleModelSelection data:', data);
        const { modelName, element } = data.data || data;
        
        // Model ID'sini dataset'ten al (integer olarak)
        const modelId = parseInt(element?.dataset?.modelId?.replace('model-', '')) || 1;
        const baseModelId = `model-${modelId}`;
        
        // Aynı model için benzersiz pane ID oluştur
        const paneId = this.generateUniquePaneId(baseModelId);
        
        console.log('Creating pane with modelName:', modelName, 'modelId:', modelId, 'paneId:', paneId);
        
        // Yeni pane oluştur
        this.createChatPane(modelName, paneId, modelId);
    }

    /**
     * Benzersiz pane ID oluştur
     * @param {string} baseModelId - Base model ID
     * @returns {string} Benzersiz pane ID
     */
    generateUniquePaneId(baseModelId) {
        let counter = 1;
        let paneId = `${baseModelId}-${counter}`;
        
        // Benzersiz ID bulana kadar dene
        while (this.chatPanes.has(paneId)) {
            counter++;
            paneId = `${baseModelId}-${counter}`;
        }
        
        return paneId;
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
        this.currentLayout = layout;
        this.applyLayout(layout);
    }

    /**
     * Pane focus işle
     * @param {Object} data - Event data
     */
    handlePaneFocus(data) {
        const { paneId } = data;
        this.activatePane(paneId);
    }

    /**
     * Pane close request işle
     * @param {Object} data - Event data
     */
    handlePaneCloseRequest(data) {
        const { paneId, hasMessages } = data;
        
        // Eğer mesaj yazılmamışsa direkt kapat
        if (!hasMessages) {
            this.closePane(paneId);
            return;
        }

        // Mesaj yazılmışsa onay iste (şimdilik direkt kapat)
        this.closePane(paneId);
    }

    /**
     * Chat pane oluştur
     * @param {string} modelName - Model adı
     * @param {string} paneId - Pane ID (benzersiz)
     * @param {number} modelId - Model ID (integer)
     */
    async createChatPane(modelName, paneId, modelId = 1) {
        // Maksimum pane sayısını kontrol et
        if (this.chatPanes.size >= this.maxPanes) {
            console.warn(`Maximum number of panes (${this.maxPanes}) reached`);
            this.stateManager.addNotification({
                type: 'warning',
                message: `Maximum ${this.maxPanes} chat panes allowed`
            });
            return;
        }

        try {
            // Backend'de chat oluştur
            const chatResponse = await fetch('/api/chat/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model_id: modelId, // Artık integer olarak geliyor
                    title: `${modelName} Chat`
                })
            });

            const chatResult = await chatResponse.json();
            
            if (!chatResult.success) {
                throw new Error(chatResult.error || 'Chat oluşturulamadı');
            }

            // Backend'den gelen chat_id'yi kullan
            const backendChatId = chatResult.chat_id;

            // Yeni ChatPane nesnesi oluştur
            const chatPane = new ChatPane(backendChatId, modelName, modelId, this.eventManager);

            // İlk pane ise empty state'i temizle
            if (this.chatPanes.size === 0) {
                this.chatPanesContainer.innerHTML = '';
            }
            
            // Pane'i container'a ekle
            this.chatPanesContainer.appendChild(chatPane.element);
            
            // Pane'i map'e ekle
            this.chatPanes.set(backendChatId, chatPane);
            
            // Pane'i aktif et
            this.activatePane(backendChatId);

            // Chat counter'ı artır
            this.chatCounter++;

            // Layout'u güncelle
            this.updateLayout();

            // Event emit et
            this.eventManager.emit('pane:created', {
                modelName,
                paneId: backendChatId,
                modelId: modelId,
                element: chatPane.element,
                pane: chatPane,
                totalPanes: this.chatPanes.size
            });

            console.log('Chat pane created:', chatPane.getInfo());
            
        } catch (error) {
            console.error('Chat oluşturma hatası:', error);
            this.stateManager.addNotification({
                type: 'error',
                message: `Chat oluşturulamadı: ${error.message}`
            });
        }
    }

    /**
     * Pane'i aktif et
     * @param {string} paneId - Pane ID
     */
    activatePane(paneId) {
        // Tüm pane'leri deaktive et
        this.chatPanes.forEach((pane, id) => {
            pane.setActive(false);
        });

        // Seçilen pane'i aktif et
        const pane = this.chatPanes.get(paneId);
        if (pane) {
            pane.setActive(true);
            this.activePane = pane;
            
            // Event emit et
            this.eventManager.emit('pane:activated', {
                paneId,
                element: pane.element,
                pane: pane
            });
        }
    }

    /**
     * Tüm pane'leri temizle
     */
    clearAllPanes() {
        this.chatPanes.forEach((pane) => {
            pane.destroy();
        });
        this.chatPanes.clear();
        this.activePane = null;
    }

    /**
     * Layout'u güncelle
     */
    updateLayout() {
        const paneCount = this.chatPanes.size;
        
        // Container class'larını temizle
        this.chatPanesContainer.className = 'chat-panes-container';
        
        // Layout class'ını ekle
        if (paneCount === 1) {
            this.chatPanesContainer.classList.add('single-pane');
        } else if (paneCount === 2) {
            this.chatPanesContainer.classList.add('two-panes');
        } else if (paneCount === 3) {
            this.chatPanesContainer.classList.add('three-panes');
        } else if (paneCount === 4) {
            this.chatPanesContainer.classList.add('four-panes');
        }
    }



    /**
     * Pane kapat
     * @param {string} paneId - Pane ID
     */
    closePane(paneId) {
        const pane = this.chatPanes.get(paneId);
        if (!pane) return;

        // Pane'i map'den kaldır
        this.chatPanes.delete(paneId);

        // Pane'i destroy et
        pane.destroy();

        // Eğer kapatılan pane aktif pane ise
        if (this.activePane === pane) {
            this.activePane = null;

            // Başka pane varsa, ilkini aktif et
            if (this.chatPanes.size > 0) {
                const firstPane = this.chatPanes.values().next().value;
                this.activatePane(firstPane.id);
            } else {
                // Hiç pane kalmadıysa empty state göster
                this.showEmptyState();
            }
        }

        // Layout'u güncelle
        this.updateLayout();

        // Event emit et
        this.eventManager.emit('pane:closed', {
            paneId,
            element: pane.element,
            pane: pane,
            totalPanes: this.chatPanes.size
        });
    }

    /**
     * Empty state'i göster
     */
    showEmptyState() {
        if (!this.chatPanesContainer) return;

        // Sadece pane yoksa empty state göster
        if (this.chatPanes.size === 0) {
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
    }




    /**
     * Mesajları güncelle
     * @param {Array} messages - Mesaj listesi
     */
    updateMessages(messages) {
        if (!this.activePane) return;

        // Mesajları aktif pane'e ekle
        messages.forEach(message => {
            // Mesajı doğru formata çevir
            const formattedMessage = {
                type: message.isUser ? 'user' : 'assistant',
                content: message.content,
                timestamp: message.timestamp
            };
            this.activePane.addMessage(formattedMessage);
        });
    }


    /**
     * Typing indicator'ı güncelle
     * @param {boolean} isTyping - Typing durumu
     */
    updateTypingIndicator(isTyping) {
        if (!this.activePane) return;

        if (isTyping) {
            this.activePane.showTypingIndicator();
        } else {
            this.activePane.hideTypingIndicator();
        }
    }

    /**
     * Scroll to bottom
     */
    scrollToBottom() {
        if (!this.activePane) return;

        const messagesContainer = DOMUtils.$('.pane-messages', this.activePane.element);
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    /**
     * Layout uygula
     * @param {string} layout - Layout adı
     */
    applyLayout(layout) {
        if (!this.chatPanesContainer) return;

        // Layout class'larını kaldır
        this.chatPanesContainer.className = 'chat-panes-container';
        
        // Yeni layout class'ı ekle
        if (layout !== 'single') {
            DOMUtils.addClass(this.chatPanesContainer, layout);
        }

        // Pane sayısına göre layout'u güncelle
        this.updateLayout();

        // Event emit et
        this.eventManager.emit('layout:applied', {
            layout,
            element: this.chatPanesContainer,
            paneCount: this.chatPanes.size
        });
    }

    /**
     * Pane'i temizle
     */
    clearPane() {
        if (this.activePane) {
            // Mesajları temizle
            this.activePane.messages = [];
            this.activePane.hasMessages = false;
            
            // Empty state'i göster
            const messagesContainer = DOMUtils.$('.pane-messages', this.activePane.element);
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-comments"></i>
                        </div>
                        <p>Start a conversation with ${this.activePane.modelName}</p>
                    </div>
                `;
            }
        }
    }

    /**
     * Controller'ı temizle
     */
    destroy() {
        // Tüm pane'leri temizle
        this.clearAllPanes();

        console.log('ChatPaneController destroyed');
    }
}
