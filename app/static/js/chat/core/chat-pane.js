/**
 * Chat Pane Class
 * Her chat penceresi için nesne yönetimi
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';
import { i18n } from '../utils/i18n.js';

export class ChatPane {
    constructor(id, modelName, modelId, eventManager) {
        this.id = id;
        this.modelName = modelName;
        this.modelId = modelId;
        this.eventManager = eventManager;
        this.isActive = false;
        this.hasMessages = false;
        this.hasUserMessage = false; // kullanıcı mesajı gönderildi mi?
        this.readOnly = false; // kapanmış sohbet görüntüleme modu
        this.messages = [];
        this.fromHistory = false; // history'den açıldı mı?
        this.element = null;
        this.createdAt = Date.now();
        this.lastActivity = null;
        this.voiceActive = false; // ses kaydı açık mı
        this.recognition = null; // SpeechRecognition örneği
        
        // Pane elementini oluştur
        this.createElement();
    }

    /** Model meta bilgilerini servis üzerinden getir */
    getModelMeta() {
        try {
            const modelService = window.ZekaiApp?.services?.modelService;
            const models = modelService?.models || [];
            const idStr = `model-${this.modelId}`;
            const found = models.find(m => m.modelId === this.modelId || m.id === idStr || (m.name || '').toLowerCase() === (this.modelName || '').toLowerCase());
            if (!found) return {};
            return { icon: found.icon, color: found.color, provider: found.provider, logoUrl: found.logoUrl };
        } catch (e) {
            return {};
        }
    }

    /** Minimize ikonunu güncelle (+/-) */
    updateMinimizeIcon() {
        const btn = DOMUtils.$('.minimize-btn', this.element);
        if (!btn) return;
        const icon = DOMUtils.$('i', btn);
        if (!icon) return;
        const isMin = this.element.classList.contains('minimized');
        icon.className = isMin ? 'fas fa-plus' : 'fas fa-minus';
    }

    /**
     * İlk karşılama mesajını ekle (mock)
     */
    addWelcomeMessage() {
        const welcome = this.generateWelcomeGreeting();
        this.addMessage({
            type: 'assistant',
            content: welcome,
            timestamp: Date.now()
        });
    }

    /**
     * Model adına göre karşılama mesajı üret
     * @returns {string}
     */
    generateWelcomeGreeting() {
        const name = (this.modelName || '').toLowerCase();
        if (name.includes('gemini')) {
            return i18n.t('welcome_gemini');
        }
        if (name.includes('gpt') || name.includes('chatgpt')) {
            return i18n.t('welcome_gpt');
        }
        if (name.includes('claude')) {
            return i18n.t('welcome_claude');
        }
        if (name.includes('deepseek')) {
            return i18n.t('welcome_deepseek');
        }
        return i18n.t('welcome_generic', { model: this.modelName });
    }

    async openHistoryPane(paneId, fallbackModelName = 'Chat') {
        let modelName = fallbackModelName;
        let modelId = 1;
        let messages = [];

        const snapshot = this.closedChatSnapshots.get(paneId);
        if (snapshot) {
            modelName = snapshot.modelName || fallbackModelName;
            modelId = snapshot.modelId || 1;
            messages = Array.isArray(snapshot.messages) ? snapshot.messages : [];
        } else {
            // Sunucudan chat bilgisi ve mesajları yükle
            try {
                const [chatRes, msgRes] = await Promise.all([
                    fetch(`/api/chats/${paneId}`),
                    fetch(`/api/chats/${paneId}/messages?limit=100`)
                ]);
                const chatJson = await chatRes.json();
                const msgJson = await msgRes.json();
                if (chatJson && chatJson.success && chatJson.chat) {
                    modelName = chatJson.chat.model_name || fallbackModelName;
                    modelId = chatJson.chat.model_id || 1;
                }
                if (msgJson && msgJson.success && Array.isArray(msgJson.messages)) {
                    messages = msgJson.messages.map(m => ({
                        type: m.is_user ? 'user' : 'assistant',
                        content: m.content,
                        timestamp: m.timestamp ? Date.parse(m.timestamp) : Date.now()
                    }));
                }
            } catch (e) {
                console.warn('History load failed, using empty messages', e);
                messages = [];
            }
        }

        // Read-only pane oluştur
        this.readOnly = true;
        this.modelName = modelName;
        this.modelId = modelId;
        this.messages = messages;
        this.fromHistory = true;
        this.createElement();
        this.renderMessagesFromSnapshot(messages);
    }

    /**
     * Pane elementini oluştur
     */
    createElement() {
        // Try to resolve model metadata (icon/color/provider)
        const meta = this.getModelMeta();
        const iconClass = meta.icon || 'fas fa-robot';
        const iconColor = meta.color || 'var(--primary)';

        this.element = DOMUtils.createElement('div', {
            className: 'chat-pane',
            'data-pane-id': String(this.id),
            'data-model-id': String(this.modelId),
            'data-model-name': this.modelName,
            'data-started': 'false'
        });

        const chatNumber = (typeof this.id === 'string' && this.id.includes('-'))
            ? this.id.split('-').pop()
            : String(this.id);

        this.element.innerHTML = `
            <div class="pane-header">
                <div class="pane-title-section">
                    <div class="model-info">
                        <div class="model-icon">
                            ${meta.logoUrl ? `<img class="model-logo" src="${meta.logoUrl}" alt="${this.modelName} logo" />` : `<i class="${iconClass}"></i>`}
                        </div>
                        <div class="model-details">
                            <span class="model-name">${this.modelName}</span>
                            <span class="chat-number">${i18n.t('chat_number', { num: chatNumber })}</span>
                        </div>
                    </div>
                </div>
                <div class="pane-controls">
                    <button class="control-btn minimize-btn" title="${i18n.t('minimize')}">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="control-btn close-btn" title="${i18n.t('close')}">
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
                        <p>${i18n.t('start_with_model', { model: this.modelName })}</p>
                    </div>
                </div>
                <div class="pane-input-area">
                    <div class="pane-input-container">
                        <textarea class="pane-input" placeholder="${i18n.t('type_message')}" rows="1"></textarea>
                        <button class="voice-btn" type="button" title="${i18n.t?.('voice_input') || 'Sesle Yaz'}">
                            <i class="fas fa-microphone"></i>
                        </button>
                        <button class="pane-send-btn" type="button">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupEventListeners();

        // Yeni açılan sohbet için karşılama mesajı ekle (mock)
        if (!this.fromHistory) {
            this.addWelcomeMessage();
        }
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
                    return;
                }
                // Ctrl+K -> input temizle
                if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
                    e.preventDefault();
                    input.value = '';
                    this.autoResizeTextarea(input);
                    return;
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

        // Voice Input
        const voiceBtn = DOMUtils.$('.voice-btn', this.element);
        if (voiceBtn) {
            this.initVoiceInput(voiceBtn);
        }
    }

    /**
     * Mesaj gönderme işle
     * @param {Event} e - Event
     */
    handleSendMessage(e) {
        e.preventDefault();
        e.stopPropagation();
        if (this.readOnly) {
            // Read-only modda gönderim engellenir
            return;
        }
        
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
        
        // Use button class instead of icon to avoid mismatch after toggle
        if (btn.classList.contains('minimize-btn')) {
            this.toggleMinimize();
            this.updateMinimizeIcon();
            return;
        }
        if (btn.classList.contains('close-btn')) {
            this.close();
            return;
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
        if (message && message.type === 'user') {
            this.hasUserMessage = true;
            if (this.element) {
                this.element.setAttribute('data-started', 'true');
            }
        }
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

    /** Snapshot mesajlarını yükle ve render et (welcome mesajını ez) */
    renderMessagesFromSnapshot(messages = []) {
        // State'i güncelle
        this.messages = [];
        this.hasMessages = false;
        this.hasUserMessage = messages.some(m => m.type === 'user');
        this.lastActivity = Date.now();

        const messagesContainer = DOMUtils.$('.pane-messages', this.element);
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }

        messages.forEach(m => {
            this.addMessage(m);
        });
    }

    /** Read-only modu aç/kapat, input'u devre dışı bırak */
    setReadOnly(flag = true) {
        this.readOnly = !!flag;
        if (!this.element) return;
        if (this.readOnly) {
            this.element.classList.add('read-only');
        } else {
            this.element.classList.remove('read-only');
        }
        const input = DOMUtils.$('.pane-input', this.element);
        const sendBtn = DOMUtils.$('.pane-send-btn', this.element);
        if (input) {
            input.disabled = this.readOnly;
            if (this.readOnly) {
                input.setAttribute('placeholder', i18n.t('readonly_placeholder'));
            } else {
                input.setAttribute('placeholder', i18n.t('type_message'));
            }
        }
        if (sendBtn) {
            sendBtn.disabled = this.readOnly;
            sendBtn.setAttribute('aria-disabled', this.readOnly ? 'true' : 'false');
        }
        // Voice button durumu
        const voiceBtn = DOMUtils.$('.voice-btn', this.element);
        if (voiceBtn) {
            voiceBtn.disabled = this.readOnly;
            voiceBtn.setAttribute('aria-disabled', this.readOnly ? 'true' : 'false');
        }
    }

    /**
     * Sesle yazma başlat/durdur ayarla
     */
    initVoiceInput(voiceBtn) {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
            DOMUtils.on(voiceBtn, 'click', (e) => {
                e.preventDefault();
                this.stateManager?.addNotification?.({ type: 'warning', message: 'Tarayıcı ses tanıma desteklemiyor.' });
            });
            return;
        }

        this.recognition = new SR();
        this.recognition.lang = 'tr-TR';
        this.recognition.interimResults = true;
        this.recognition.continuous = false;

        this.recognition.onresult = (event) => {
            const input = DOMUtils.$('.pane-input', this.element);
            if (!input) return;
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            input.value = ((input.value || '') + (input.value ? ' ' : '') + transcript).trim();
            this.autoResizeTextarea(input);
        };

        this.recognition.onend = () => {
            this.voiceActive = false;
            const icon = DOMUtils.$('i', voiceBtn);
            if (icon) icon.className = 'fas fa-microphone';
        };

        DOMUtils.on(voiceBtn, 'click', (e) => {
            e.preventDefault();
            if (this.readOnly) return;
            if (this.voiceActive) {
                try { this.recognition.stop(); } catch (_) {}
                this.voiceActive = false;
                const icon = DOMUtils.$('i', voiceBtn);
                if (icon) icon.className = 'fas fa-microphone';
                return;
            }
            try {
                this.recognition.start();
                this.voiceActive = true;
                const icon = DOMUtils.$('i', voiceBtn);
                if (icon) icon.className = 'fas fa-microphone-slash';
            } catch (err) {
                this.stateManager?.addNotification?.({ type: 'error', message: 'Ses tanıma başlatılamadı.' });
            }
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
        
        // İçeriği hazırla: asistan için Markdown, kullanıcı için düz metin
        const raw = String(message.content ?? '');
        let safeHtml = '';
        if (message.type === 'assistant') {
            try {
                // Configure marked (idempotent)
                try {
                    if (window.marked && typeof window.marked.setOptions === 'function') {
                        window.marked.setOptions({ breaks: true, gfm: true });
                    }
                } catch (_) {}
                const html = (window.marked && typeof window.marked.parse === 'function')
                    ? window.marked.parse(raw)
                    : raw
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/\n/g, '<br>');
                safeHtml = (window.DOMPurify && typeof window.DOMPurify.sanitize === 'function')
                    ? window.DOMPurify.sanitize(html)
                    : html;
            } catch (e) {
                safeHtml = raw
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\n/g, '<br>');
            }
        } else {
            // Kullanıcı mesajı: düz metni güvenli şekilde göster
            safeHtml = raw
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\n/g, '<br>');
        }

        const contentEl = DOMUtils.createElement('div', { className: 'message-content' });
        const textEl = DOMUtils.createElement('div', { className: 'message-text' });
        const timeEl = DOMUtils.createElement('div', { className: 'message-time' });

        textEl.innerHTML = safeHtml;
        timeEl.textContent = time;

        contentEl.appendChild(textEl);
        contentEl.appendChild(timeEl);
        messageDiv.appendChild(contentEl);

        return messageDiv;
    }
    
    async getAIResponse(userMessage) {
        // Typing indicator göster
        this.showTypingIndicator();
        
        try {
            // Backend'e mesaj gönder
            const response = await fetch(`/api/chats/${this.id}/send`, {
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
                    content: i18n.t('error_prefix', { msg: result.error }),
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
                content: i18n.t('connection_error', { msg: error.message }),
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
            hasMessages: this.hasMessages,
            hasUserMessage: this.hasUserMessage,
            fromHistory: this.fromHistory
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
