/**
 * Chat Pane Class
 * Her chat penceresi için nesne yönetimi
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';

export class ChatPane {
    constructor(id, modelName, modelId, eventManager) {
        this.id = id;
        this.modelName = modelName;
        this.modelId = modelId;
        this.eventManager = eventManager;
        this.isActive = false;
        this.hasMessages = false;
        this.messages = [];
        this.element = null;
        this.createdAt = Date.now();
        this.lastActivity = null;
        
        // Pane elementini oluştur
        this.createElement();
    }

    /**
     * Pane elementini oluştur
     */
    createElement() {
        this.element = DOMUtils.createElement('div', {
            className: 'chat-pane',
            'data-pane-id': this.id,
            'data-model-id': this.modelId,
            'data-model-name': this.modelName
        });

        this.element.innerHTML = `
            <div class="pane-header">
                <div class="pane-title-section">
                    <div class="model-info">
                        <div class="model-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="model-details">
                            <span class="model-name">${this.modelName}</span>
                            <span class="chat-number">Chat #${this.id.split('-').pop()}</span>
                        </div>
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
                <div class="pane-messages" id="messages-${this.id}">
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-comments"></i>
                        </div>
                        <p>Start a conversation with ${this.modelName}</p>
                    </div>
                </div>
                <div class="pane-input-area">
                    <div class="pane-input-container">
                        <textarea class="pane-input" placeholder="Type your message..." rows="1"></textarea>
                        <button class="pane-send-btn" type="button">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupEventListeners();
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        const input = DOMUtils.$('.pane-input', this.element);
        const sendBtn = DOMUtils.$('.pane-send-btn', this.element);
        const controlBtns = DOMUtils.$$('.control-btn', this.element);
        const header = DOMUtils.$('.pane-header', this.element);

        // Send button ve input events
        if (sendBtn) {
            DOMUtils.on(sendBtn, 'click', (e) => {
                this.handleSendMessage(e);
            });
        }

        if (input) {
            // Enter key press
            DOMUtils.on(input, 'keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage(e);
                }
            });

            // Auto resize textarea
            DOMUtils.on(input, 'input', () => {
                this.autoResizeTextarea(input);
            });

            // Focus event - pane'i aktif et
            DOMUtils.on(input, 'focus', () => {
                this.eventManager.emit('pane:focus', {
                    paneId: this.id,
                    pane: this
                });
            });
        }

        // Control buttons
        controlBtns.forEach(btn => {
            DOMUtils.on(btn, 'click', (e) => {
                this.handleControlButtonClick(e, btn);
            });
        });

        // Header click - pane'i aktif et
        if (header) {
            DOMUtils.on(header, 'click', (e) => {
                this.eventManager.emit('pane:focus', {
                    paneId: this.id,
                    pane: this
                });
            });
        }
    }

    /**
     * Mesaj gönderme işle
     * @param {Event} e - Event
     */
    handleSendMessage(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const input = DOMUtils.$('.pane-input', this.element);
        const message = input.value.trim();
        
        if (!message) return;

        // Mesajı pane'e ekle
        this.addMessage({
            type: 'user',
            content: message,
            timestamp: Date.now()
        });

        // Input'u temizle
        input.value = '';
        this.autoResizeTextarea(input);

        // Pane'i aktif et
        this.setActive(true);

        // Event emit et
        this.eventManager.emit('pane:message-sent', {
            paneId: this.id,
            message: message,
            pane: this
        });

        // AI yanıtını al
        this.getAIResponse(message);
    }

    /**
     * Control button click işle
     * @param {Event} e - Click event
     * @param {Element} btn - Button element
     */
    handleControlButtonClick(e, btn) {
        e.preventDefault();
        e.stopPropagation();
        
        const icon = DOMUtils.$('i', btn);
        if (!icon) return;

        const iconClass = icon.className;
        
        if (iconClass.includes('minus')) {
            this.toggleMinimize();
        } else if (iconClass.includes('times')) {
            this.close();
        }
    }

    /**
     * Pane'e mesaj ekle
     * @param {Object} message - Mesaj objesi
     */
    addMessage(message) {
        // Mesajı listeye ekle
        this.messages.push(message);
        this.hasMessages = true;
        this.lastActivity = Date.now();

        // Empty state'i kaldır
        const messagesContainer = DOMUtils.$('.pane-messages', this.element);
        const emptyState = DOMUtils.$('.empty-state', messagesContainer);
        if (emptyState) {
            emptyState.remove();
        }

        // Mesaj elementini oluştur ve ekle
        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Event emit et
        this.eventManager.emit('pane:message-added', {
            paneId: this.id,
            message: message,
            pane: this
        });
    }

    /**
     * Mesaj elementi oluştur
     * @param {Object} message - Mesaj objesi
     * @returns {Element} Mesaj elementi
     */
    createMessageElement(message) {
        const messageDiv = DOMUtils.createElement('div', {
            className: `message ${message.type === 'user' ? 'user-message' : 'assistant-message'}`
        });
        
        // Timestamp'i güvenli şekilde işle
        let time;
        if (message.timestamp) {
            if (message.timestamp instanceof Date) {
                time = message.timestamp.toLocaleTimeString();
            } else if (typeof message.timestamp === 'number') {
                time = new Date(message.timestamp).toLocaleTimeString();
            } else {
                time = new Date().toLocaleTimeString();
            }
        } else {
            time = new Date().toLocaleTimeString();
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${message.content || ''}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        return messageDiv;
    }

    /**
     * AI yanıtını al (backend'den)
     * @param {string} userMessage - Kullanıcı mesajı
     */
    async getAIResponse(userMessage) {
        // Typing indicator göster
        this.showTypingIndicator();
        
        try {
            // Backend'e mesaj gönder
            const response = await fetch(`/api/chat/${this.id}/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: this.id,
                    message: userMessage,
                    model_id: this.modelId
                })
            });
            
            const result = await response.json();
            
            // Typing indicator'ı gizle
            this.hideTypingIndicator();
            
            if (result.success) {
                // AI yanıtını ekle
                this.addMessage({
                    type: 'assistant',
                    content: result.ai_response,
                    timestamp: Date.now()
                });
                
                // Event emit et
                this.eventManager.emit('pane:ai-response-received', {
                    paneId: this.id,
                    response: result.ai_response,
                    pane: this
                });
            } else {
                // Hata mesajı göster
                this.addMessage({
                    type: 'assistant',
                    content: `Hata: ${result.error}`,
                    timestamp: Date.now()
                });
                
                // Event emit et
                this.eventManager.emit('pane:ai-error', {
                    paneId: this.id,
                    error: result.error,
                    pane: this
                });
            }
            
        } catch (error) {
            // Typing indicator'ı gizle
            this.hideTypingIndicator();
            
            // Hata mesajı göster
            this.addMessage({
                type: 'assistant',
                content: `Bağlantı hatası: ${error.message}`,
                timestamp: Date.now()
            });
            
            // Event emit et
            this.eventManager.emit('pane:ai-error', {
                paneId: this.id,
                error: error.message,
                pane: this
            });
        }
    }

    /**
     * AI yanıtı oluştur
     * @param {string} userMessage - Kullanıcı mesajı
     * @returns {string} AI yanıtı
     */
    generateAIResponse(userMessage) {
        const responses = {
            'gemini-2.5-flash': [
                `Merhaba! Gemini 2.5 Flash olarak size yardımcı olmaktan mutluluk duyarım. "${userMessage}" konusunda size nasıl yardımcı olabilirim?`,
                `Harika bir soru! "${userMessage}" hakkında detaylı bilgi verebilirim. Bu konuda özellikle hangi alanı merak ediyorsunuz?`,
                `Çok ilginç! "${userMessage}" konusunda size yardımcı olabilirim. Bu alanda deneyimim var ve size en iyi şekilde rehberlik edebilirim.`,
                `Anladım! "${userMessage}" hakkında konuşmak istiyorsunuz. Bu konuda size nasıl yardımcı olabilirim? Hangi açıdan yaklaşmak istersiniz?`
            ],
            'chatgpt-4': [
                `Merhaba! ChatGPT-4 olarak buradayım. "${userMessage}" konusunda size yardımcı olmaya hazırım. Bu konuda ne öğrenmek istiyorsunuz?`,
                `Çok güzel bir soru! "${userMessage}" hakkında kapsamlı bir açıklama yapabilirim. Hangi perspektiften yaklaşmak istersiniz?`,
                `Harika! "${userMessage}" konusunda size rehberlik edebilirim. Bu alanda geniş bir bilgi birikimim var.`,
                `Anladım! "${userMessage}" hakkında konuşalım. Size nasıl yardımcı olabilirim? Bu konuda özel olarak ne merak ediyorsunuz?`
            ],
            'claude-3': [
                `Selam! Claude 3 olarak size hizmet vermekten mutluluk duyarım. "${userMessage}" konusunda size nasıl yardımcı olabilirim?`,
                `Mükemmel bir konu! "${userMessage}" hakkında detaylı bilgi paylaşabilirim. Bu konuda hangi açıdan yaklaşmak istersiniz?`,
                `Çok ilginç! "${userMessage}" konusunda size rehberlik edebilirim. Bu alanda deneyimim var ve size en iyi şekilde yardımcı olabilirim.`,
                `Harika! "${userMessage}" hakkında konuşmak istiyorsunuz. Bu konuda size nasıl yardımcı olabilirim? Hangi yönden başlamak istersiniz?`
            ]
        };
        
        const modelResponses = responses[this.modelName.toLowerCase()] || responses['gemini-2.5-flash'];
        const randomResponse = modelResponses[Math.floor(Math.random() * modelResponses.length)];
        
        return randomResponse;
    }

    /**
     * Typing indicator göster
     */
    showTypingIndicator() {
        const messagesContainer = DOMUtils.$('.pane-messages', this.element);
        if (!messagesContainer) return;
        
        const typingDiv = DOMUtils.createElement('div', {
            className: 'message assistant-message typing-indicator',
            id: `typing-${this.id}`
        });
        
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Typing indicator gizle
     */
    hideTypingIndicator() {
        const typingElement = document.getElementById(`typing-${this.id}`);
        if (typingElement) {
            typingElement.remove();
        }
    }

    /**
     * Textarea otomatik boyutlandırma
     * @param {Element} textarea - Textarea elementi
     */
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    /**
     * Pane'i aktif et
     * @param {boolean} active - Aktif durumu
     */
    setActive(active) {
        this.isActive = active;
        
        if (active) {
            DOMUtils.addClass(this.element, 'active');
        } else {
            DOMUtils.removeClass(this.element, 'active');
        }

        // Event emit et
        this.eventManager.emit('pane:active-changed', {
            paneId: this.id,
            isActive: active,
            pane: this
        });
    }

    /**
     * Pane'i minimize/restore et
     */
    toggleMinimize() {
        const isMinimized = this.element.classList.contains('minimized');
        
        if (isMinimized) {
            DOMUtils.removeClass(this.element, 'minimized');
            this.eventManager.emit('pane:restored', {
                paneId: this.id,
                pane: this
            });
        } else {
            DOMUtils.addClass(this.element, 'minimized');
            this.eventManager.emit('pane:minimized', {
                paneId: this.id,
                pane: this
            });
        }
    }

    /**
     * Pane'i kapat
     */
    close() {
        // Eğer mesaj yazılmamışsa aktif olarak işaretleme
        if (!this.hasMessages) {
            this.isActive = false;
        }

        // Event emit et
        this.eventManager.emit('pane:close-requested', {
            paneId: this.id,
            pane: this,
            hasMessages: this.hasMessages
        });
    }

    /**
     * Pane'i DOM'dan kaldır
     */
    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
        
        // Event emit et
        this.eventManager.emit('pane:destroyed', {
            paneId: this.id,
            pane: this
        });
    }

    /**
     * Pane bilgilerini al
     * @returns {Object} Pane bilgileri
     */
    getInfo() {
        return {
            id: this.id,
            modelName: this.modelName,
            modelId: this.modelId,
            isActive: this.isActive,
            hasMessages: this.hasMessages,
            messageCount: this.messages.length,
            createdAt: this.createdAt,
            lastActivity: this.lastActivity
        };
    }

    /**
     * Pane'i güncelle
     * @param {Object} updates - Güncellemeler
     */
    update(updates) {
        Object.assign(this, updates);
        
        // Event emit et
        this.eventManager.emit('pane:updated', {
            paneId: this.id,
            updates: updates,
            pane: this
        });
    }

}
