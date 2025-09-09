/**
 * Input Controller
 * Input bar kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Validation } from '../utils/validation.js';
import { Helpers } from '../utils/helpers.js';

export class InputController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.messageInput = null;
        this.sendBtn = null;
        this.attachmentBtn = null;
        this.promptsBtn = null;
        this.layoutBtns = [];
    }

    /**
     * Controller'ı başlat
     */
    async init() {
        // Elementleri seç
        this.messageInput = DOMUtils.$('.message-input');
        this.sendBtn = DOMUtils.$('.send-btn');
        this.attachmentBtn = DOMUtils.$('.attachment-btn');
        this.promptsBtn = DOMUtils.$('.prompts-btn');
        this.layoutBtns = DOMUtils.$$('.layout-btn');

        if (!this.messageInput) {
            console.error('Message input not found');
            return;
        }

        // Event listener'ları kur
        this.setupEventListeners();
        
        // State listener'ları kur
        this.setupStateListeners();

        // Input validasyonu kur
        this.setupValidation();

        console.log('InputController initialized');
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Send button
        if (this.sendBtn) {
            DOMUtils.on(this.sendBtn, 'click', (e) => {
                this.handleSendMessage(e);
            });
        }

        // Message input
        if (this.messageInput) {
            // Enter key
            DOMUtils.on(this.messageInput, 'keydown', (e) => {
                this.handleKeyDown(e);
            });

            // Input change
            DOMUtils.on(this.messageInput, 'input', (e) => {
                this.handleInputChange(e);
            });

            // Focus
            DOMUtils.on(this.messageInput, 'focus', (e) => {
                this.handleInputFocus(e);
            });

            // Blur
            DOMUtils.on(this.messageInput, 'blur', (e) => {
                this.handleInputBlur(e);
            });
        }

        // Attachment button
        if (this.attachmentBtn) {
            DOMUtils.on(this.attachmentBtn, 'click', (e) => {
                this.handleAttachmentClick(e);
            });
        }

        // Prompts button
        if (this.promptsBtn) {
            DOMUtils.on(this.promptsBtn, 'click', (e) => {
                this.handlePromptsClick(e);
            });
        }

        // Layout buttons
        this.layoutBtns.forEach(btn => {
            DOMUtils.on(btn, 'click', (e) => {
                this.handleLayoutButtonClick(e, btn);
            });
        });
    }

    /**
     * State listener'ları kur
     */
    setupStateListeners() {
        // Active model değişikliği
        this.stateManager.subscribe('activeModel', (newModel) => {
            this.updateInputPlaceholder(newModel);
        });

        // Messages değişikliği
        this.stateManager.subscribe('messages', (messages) => {
            this.updateSendButtonState(messages);
        });
    }

    /**
     * Input validasyonu kur
     */
    setupValidation() {
        if (!this.messageInput) return;

        const rules = [
            {
                required: false,
                maxLength: 2000,
                message: 'Mesaj çok uzun (maksimum 2000 karakter)'
            }
        ];

        Validation.validateInput(this.messageInput, rules, (errors, value) => {
            this.handleValidationResult(errors, value);
        });
    }

    /**
     * Send message işle
     * @param {Event} e - Click event
     */
    handleSendMessage(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Mesaj gönder
        this.sendMessage(message);
    }

    /**
     * Key down işle
     * @param {Event} e - Keyboard event
     */
    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSendMessage(e);
        }
    }

    /**
     * Input change işle
     * @param {Event} e - Input event
     */
    handleInputChange(e) {
        // Auto-resize textarea
        this.autoResizeTextarea();
        
        // Send button durumunu güncelle
        this.updateSendButtonState();
    }

    /**
     * Input focus işle
     * @param {Event} e - Focus event
     */
    handleInputFocus(e) {
        DOMUtils.addClass(this.messageInput.parentElement, 'focused');
    }

    /**
     * Input blur işle
     * @param {Event} e - Blur event
     */
    handleInputBlur(e) {
        DOMUtils.removeClass(this.messageInput.parentElement, 'focused');
    }

    /**
     * Attachment click işle
     * @param {Event} e - Click event
     */
    handleAttachmentClick(e) {
        e.preventDefault();
        
        // File input oluştur
        const fileInput = DOMUtils.createElement('input', {
            type: 'file',
            accept: 'image/*,video/*,audio/*,.pdf,.doc,.docx,.txt',
            multiple: true
        });

        DOMUtils.on(fileInput, 'change', (e) => {
            this.handleFileSelection(e);
        });

        fileInput.click();
    }

    /**
     * Prompts click işle
     * @param {Event} e - Click event
     */
    handlePromptsClick(e) {
        e.preventDefault();
        
        // Prompts modal'ı göster
        this.eventManager.emit('modal:show', {
            type: 'prompts',
            data: {}
        });
    }

    /**
     * Layout button click işle
     * @param {Event} e - Click event
     * @param {Element} btn - Button element
     */
    handleLayoutButtonClick(e, btn) {
        e.preventDefault();
        
        const layout = btn.dataset.layout;
        if (!layout) return;

        // Active class'ı güncelle
        this.layoutBtns.forEach(b => {
            DOMUtils.removeClass(b, 'active');
        });
        DOMUtils.addClass(btn, 'active');

        // State'i güncelle
        this.stateManager.setLayout(layout);

        // Event emit et
        this.eventManager.emit('layout:changed', {
            layout,
            element: btn
        });
    }

    /**
     * File selection işle
     * @param {Event} e - Change event
     */
    handleFileSelection(e) {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        // File'ları işle
        files.forEach(file => {
            this.handleFileUpload(file);
        });
    }

    /**
     * File upload işle
     * @param {File} file - File objesi
     */
    handleFileUpload(file) {
        // File validasyonu
        if (!this.validateFile(file)) return;

        // File upload event'i emit et
        this.eventManager.emit('file:upload', {
            file,
            timestamp: Date.now()
        });

        // Notification göster
        this.stateManager.addNotification({
            type: 'success',
            message: `File "${file.name}" uploaded successfully!`
        });
    }

    /**
     * File validasyonu
     * @param {File} file - File objesi
     * @returns {boolean}
     */
    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'video/mp4',
            'audio/mp3',
            'application/pdf',
            'text/plain'
        ];

        if (file.size > maxSize) {
            this.stateManager.addNotification({
                type: 'error',
                message: 'File çok büyük (maksimum 10MB)'
            });
            return false;
        }

        if (!allowedTypes.includes(file.type)) {
            this.stateManager.addNotification({
                type: 'error',
                message: 'Desteklenmeyen file türü'
            });
            return false;
        }

        return true;
    }

    /**
     * Mesaj gönder
     * @param {string} message - Mesaj içeriği
     */
    sendMessage(message) {
        // Mesaj objesi oluştur
        const messageObj = {
            id: Helpers.generateId(),
            content: message,
            isUser: true,
            timestamp: Date.now(),
            model: this.stateManager.getState('activeModel')
        };

        // State'e ekle
        this.stateManager.addMessage(messageObj);

        // Input'u temizle
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Event emit et
        this.eventManager.emit('message:sent', {
            message: messageObj
        });

        // AI response simüle et
        this.simulateAIResponse();
    }

    /**
     * AI response simüle et
     */
    simulateAIResponse() {
        const responses = [
            "Bu çok ilginç bir soru! Size nasıl yardımcı olabilirim?",
            "Anladım. Bu konuda size daha detaylı bilgi verebilirim.",
            "Harika bir nokta! Bu konuyu daha derinlemesine inceleyelim.",
            "Evet, bu konuda size yardımcı olabilirim. Hangi açıdan bakmak istersiniz?",
            "Bu sorunuzu yanıtlamak için biraz daha bilgiye ihtiyacım var."
        ];

        // Typing indicator göster
        this.stateManager.setTyping(true);

        // 2 saniye sonra response gönder
        setTimeout(() => {
            this.stateManager.setTyping(false);

            const response = Helpers.randomChoice(responses);
            const responseObj = {
                id: Helpers.generateId(),
                content: response,
                isUser: false,
                timestamp: Date.now(),
                model: this.stateManager.getState('activeModel')
            };

            this.stateManager.addMessage(responseObj);

            // Event emit et
            this.eventManager.emit('message:received', {
                message: responseObj
            });
        }, 2000);
    }

    /**
     * Auto-resize textarea
     */
    autoResizeTextarea() {
        if (!this.messageInput) return;

        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    /**
     * Input placeholder'ı güncelle
     * @param {string} modelName - Model adı
     */
    updateInputPlaceholder(modelName) {
        if (!this.messageInput) return;

        if (modelName) {
            this.messageInput.placeholder = `Message ${modelName}...`;
        } else {
            this.messageInput.placeholder = 'Select a model to start chatting...';
        }
    }

    /**
     * Send button durumunu güncelle
     * @param {Array} messages - Mesaj listesi
     */
    updateSendButtonState(messages = null) {
        if (!this.sendBtn) return;

        const currentMessages = messages || this.stateManager.getState('messages');
        const hasMessages = currentMessages && currentMessages.length > 0;
        const hasActiveModel = this.stateManager.getState('activeModel');

        if (hasActiveModel) {
            DOMUtils.removeClass(this.sendBtn, 'disabled');
            this.sendBtn.disabled = false;
        } else {
            DOMUtils.addClass(this.sendBtn, 'disabled');
            this.sendBtn.disabled = true;
        }
    }

    /**
     * Validation result işle
     * @param {Array} errors - Hata listesi
     * @param {string} value - Input değeri
     */
    handleValidationResult(errors, value) {
        // Validation hatalarını işle
        if (errors.length > 0) {
            // Hata göster
            this.stateManager.addNotification({
                type: 'error',
                message: errors[0]
            });
        }
    }

    /**
     * Input'u focus et
     */
    focusInput() {
        if (this.messageInput) {
            this.messageInput.focus();
        }
    }

    /**
     * Input'u temizle
     */
    clearInput() {
        if (this.messageInput) {
            this.messageInput.value = '';
            this.autoResizeTextarea();
        }
    }

    /**
     * Controller'ı temizle
     */
    destroy() {
        // Event listener'ları kaldır
        if (this.sendBtn) {
            DOMUtils.off(this.sendBtn, 'click');
        }
        
        if (this.messageInput) {
            DOMUtils.off(this.messageInput, 'keydown');
            DOMUtils.off(this.messageInput, 'input');
            DOMUtils.off(this.messageInput, 'focus');
            DOMUtils.off(this.messageInput, 'blur');
        }
        
        if (this.attachmentBtn) {
            DOMUtils.off(this.attachmentBtn, 'click');
        }
        
        if (this.promptsBtn) {
            DOMUtils.off(this.promptsBtn, 'click');
        }
        
        this.layoutBtns.forEach(btn => {
            DOMUtils.off(btn, 'click');
        });

        console.log('InputController destroyed');
    }
}
