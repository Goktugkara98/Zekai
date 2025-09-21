/**
 * Chat Pane Controller
 * Chat panelleri kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';
import { ChatPane } from '../core/chat-pane.js';
import { i18n } from '../utils/i18n.js';

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
        this.closedChatSnapshots = new Map(); // paneId -> { modelName, modelId, messages }
        this.pendingVisibleAdds = 0; // eşzamanlı eklemeler için slot rezervasyonu
    }

    /**
     * Controller'ı başlat
     */
    async init() {
        this.chatPanesContainer = DOMUtils.$('.chat-panes-container');
        if (!this.chatPanesContainer) {
            return;
        }

        // Event listener'ları kur
        this.setupEventListeners();
        
        // State listener'ları kur
        this.setupStateListeners();

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

        // Pane restore request (from Active Chats)
        this.eventManager.on('pane:restore-requested', (event) => {
            const { paneId } = event.data || {};
            if (!paneId) return;
            this.restorePane(paneId);
        });

        // Minimize/restore -> layout'u güncelle
        this.eventManager.on('pane:minimized', () => {
            this.updateLayout();
        });
        this.eventManager.on('pane:restored', () => {
            this.updateLayout();
        });

        // History item selected: open read-only pane
        this.eventManager.on('history:selected', (event) => {
            const { paneId, modelName } = event.data || {};
            if (!paneId) return;
            this.openHistoryPane(paneId, modelName);
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
        let { modelName, element, modelId: providedModelId, initialMessage } = data.data || data;
        // Fallback: try reading initial message from assistant modal attribute
        if (!initialMessage || !String(initialMessage).trim().length) {
            try {
                const contentEl = document.querySelector('.assistant-modal');
                if (contentEl) {
                    const q = contentEl.getAttribute('data-assist-query') || '';
                    if (q && q.trim().length) initialMessage = q;
                }
            } catch (_) {}
        }
        
        // Model ID'sini öncelikle doğrudan datadan al, yoksa dataset'ten çöz
        let modelId = 1;
        if (providedModelId !== undefined && providedModelId !== null) {
            if (typeof providedModelId === 'string') {
                const parsed = parseInt(String(providedModelId).replace('model-', ''));
                modelId = isNaN(parsed) ? 1 : parsed;
            } else if (typeof providedModelId === 'number') {
                modelId = providedModelId;
            }
        } else {
            modelId = parseInt(element?.dataset?.modelId?.replace('model-', '')) || 1;
        }
        const baseModelId = `model-${modelId}`;
        
        // Aynı model için benzersiz pane ID oluştur
        const paneId = this.generateUniquePaneId(baseModelId);
        
        
        // Yeni pane oluştur
        this.createChatPane(modelName, paneId, modelId, initialMessage);
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
     * Minimize durumundan geri getir ve aktive et
     * @param {string} paneId
     */
    restorePane(paneId) {
        const pane = this.chatPanes.get(paneId);
        if (!pane) {
            // Pane yoksa backend'den yükleyip oluştur
            this.openExistingChatFromBackend(paneId);
            return;
        }
        let reserved = false;
        if (pane.element && pane.element.classList.contains('minimized')) {
            if (!this.reserveVisibleSlot()) {
                this.stateManager.addNotification?.({
                    type: 'warning',
                    message: i18n.t('max_panes_warning', { count: this.maxPanes })
                });
                return;
            }
            reserved = true;
            pane.element.classList.remove('minimized');
            try { pane.updateMinimizeIcon && pane.updateMinimizeIcon(); } catch (_) {}
            this.eventManager.emit('pane:restored', { paneId, pane });
        }
        this.activatePane(paneId);
        try {
            pane.element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
        } catch (_) {}
        if (reserved) this.releaseVisibleSlot();
        this.updateLayout();
    }

    /**
     * Backend'de var olan bir chat'i yükleyip normal (interaktif) pane olarak aç
     */
    async openExistingChatFromBackend(chatId) {
        if (!this.reserveVisibleSlot()) {
            this.stateManager.addNotification?.({
                type: 'warning',
                message: i18n.t('max_panes_warning', { count: this.maxPanes })
            });
            return;
        }
        let reserved = true;

        try {
            const [chatRes, msgRes] = await Promise.all([
                fetch(`/api/chats/${chatId}`),
                fetch(`/api/chats/${chatId}/messages?limit=100`)
            ]);
            const chatJson = await chatRes.json();
            const msgJson = await msgRes.json();

            if (!chatJson || !chatJson.success || !chatJson.chat) {
                throw new Error('Chat bulunamadı');
            }

            const modelName = chatJson.chat.model_name || 'Chat';
            const modelId = chatJson.chat.model_id || 1;
            const messages = (msgJson && msgJson.success && Array.isArray(msgJson.messages))
                ? msgJson.messages.map(m => ({
                    type: m.is_user ? 'user' : 'assistant',
                    content: m.content,
                    timestamp: m.timestamp ? Date.parse(m.timestamp) : Date.now()
                }))
                : [];

            // İlk pane ise empty state'i temizle
            if (this.chatPanes.size === 0) {
                this.chatPanesContainer.innerHTML = '';
            }

            // Pane oluştur ve mesajları yükle
            const chatPane = new ChatPane(chatId, modelName, modelId, this.eventManager);
            this.chatPanesContainer.appendChild(chatPane.element);
            this.chatPanes.set(chatId, chatPane);
            chatPane.fromHistory = false;
            chatPane.renderMessagesFromSnapshot(messages);

            // Aktifleştir ve layout güncelle
            this.activatePane(chatId);
            this.updateLayout();

            // Görünür > max ise minimize et
            if (this.getVisiblePaneCount() > this.maxPanes) {
                chatPane.element.classList.add('minimized');
                try { chatPane.updateMinimizeIcon && chatPane.updateMinimizeIcon(); } catch(_) {}
                this.updateLayout();
                this.stateManager.addNotification?.({
                    type: 'info',
                    message: i18n.t('limit_auto_minimized', { count: this.maxPanes })
                });
            }
        } catch (e) {
            this.stateManager.addNotification?.({ type: 'error', message: i18n.t('chat_load_failed') });
        } finally {
            if (reserved) this.releaseVisibleSlot();
        }
    }

    /**
     * History'den read-only pane aç
     */
    async openHistoryPane(paneId, fallbackModelName = 'Chat') {
        if (this.chatPanes.has(paneId)) {
            this.activatePane(paneId);
            return;
        }
        let reserved = false;
        if (!this.reserveVisibleSlot()) {
            this.stateManager.addNotification?.({
                type: 'warning',
                message: i18n.t('max_panes_warning', { count: this.maxPanes })
            });
            return;
        }
        reserved = true;

        const snapshot = this.closedChatSnapshots.get(paneId);
        let modelName = fallbackModelName;
        let modelId = 1;
        let messages = [];
        if (snapshot) {
            modelName = snapshot.modelName || fallbackModelName;
            modelId = snapshot.modelId || 1;
            messages = Array.isArray(snapshot.messages) ? snapshot.messages : [];
        } else {
            // Sunucudan chat ve mesajları yükle
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
            } catch (e) {}
        }

        if (this.chatPanes.size === 0) {
            this.chatPanesContainer.innerHTML = '';
        }

        if (this.getVisiblePaneCount() >= this.maxPanes) {
            this.stateManager.addNotification?.({
                type: 'warning',
                message: i18n.t('max_panes_warning', { count: this.maxPanes })
            });
            if (reserved) this.releaseVisibleSlot();
            return;
        }

        const chatPane = new ChatPane(paneId, modelName, modelId, this.eventManager);
        this.chatPanesContainer.appendChild(chatPane.element);
        this.chatPanes.set(paneId, chatPane);

        chatPane.fromHistory = true;
        chatPane.setReadOnly(true);
        chatPane.renderMessagesFromSnapshot(messages);

        this.activatePane(paneId);
        this.updateLayout();

        if (this.getVisiblePaneCount() > this.maxPanes) {
            chatPane.element.classList.add('minimized');
            try { chatPane.updateMinimizeIcon && chatPane.updateMinimizeIcon(); } catch(_) {}
            this.updateLayout();
            this.stateManager.addNotification?.({
                type: 'info',
                message: i18n.t('limit_auto_minimized', { count: this.maxPanes })
            });
        }

        this.eventManager.emit('pane:created', {
            modelName,
            paneId,
            modelId,
            element: chatPane.element,
            pane: chatPane,
            totalPanes: this.chatPanes.size
        });

        if (reserved) this.releaseVisibleSlot();
    }

    /**
     * Görünür (minimize olmayan) pane sayısını getir
     */
    getVisiblePaneCount() {
        if (!this.chatPanesContainer) return 0;
        const allEls = Array.from(this.chatPanesContainer.querySelectorAll('.chat-pane'));
        return allEls.filter(el => !el.classList.contains('minimized')).length;
    }

    /**
     * Görünür slot rezervasyonu (pending eklemeler)
     */
    reserveVisibleSlot() {
        const current = this.getVisiblePaneCount() + this.pendingVisibleAdds;
        if (current >= this.maxPanes) return false;
        this.pendingVisibleAdds += 1;
        return true;
    }

    /**
     * Rezervasyonu bırak
     */
    releaseVisibleSlot() {
        this.pendingVisibleAdds = Math.max(0, this.pendingVisibleAdds - 1);
    }

    /**
     * Chat pane oluştur
     * @param {string} modelName - Model adı
     * @param {string} paneId - Pane ID (benzersiz)
     * @param {number} modelId - Model ID (integer)
     */
    async createChatPane(modelName, paneId, modelId = 1, initialMessage = '') {
        // Slot rezervasyonu (eşzamanlı oluşturmalarda limiti koru)
        if (!this.reserveVisibleSlot()) {
            this.stateManager.addNotification?.({
                type: 'warning',
                message: i18n.t('max_panes_warning', { count: this.maxPanes })
            });
            return;
        }

        try {
            // Backend'de chat oluştur
            const chatResponse = await fetch('/api/chats/create', {
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

            // Son kontrol: şu an görünür pane sayısı limitte mi?
            if (this.getVisiblePaneCount() >= this.maxPanes) {
                this.stateManager.addNotification?.({
                    type: 'warning',
                    message: i18n.t('max_panes_warning', { count: this.maxPanes })
                });
                return;
            }

            // Yeni ChatPane nesnesi oluştur
            const chatPane = new ChatPane(backendChatId, modelName, modelId, this.eventManager);

            // İlk pane ise empty state'i temizle
            if (this.chatPanes.size === 0) {
                this.chatPanesContainer.innerHTML = '';
            }
            // Pane'i container'a ekle
            this.chatPanesContainer.appendChild(chatPane.element);

            // Map'e ekle
            this.chatPanes.set(backendChatId, chatPane);
            // Chat counter'ı artır
            this.chatCounter++;

            // Layout'u güncelle
            this.updateLayout();

            // Güvenlik: eğer görünür > max olduysa, yeni eklenen pane'i otomatik minimize et
            if (this.getVisiblePaneCount() > this.maxPanes) {
                chatPane.element.classList.add('minimized');
                try { chatPane.updateMinimizeIcon && chatPane.updateMinimizeIcon(); } catch(_) {}
                this.updateLayout();
                this.stateManager.addNotification?.({
                    type: 'info',
                    message: i18n.t('limit_auto_minimized', { count: this.maxPanes })
                });
            }

            // Event emit et
            this.eventManager.emit('pane:created', {
                modelName,
                paneId: backendChatId,
                modelId: modelId,
                element: chatPane.element,
                pane: chatPane,
                totalPanes: this.chatPanes.size
            });

            
            // Eğer assistant modalından geldi ve ilk mesaj varsa, hemen gönder
            if (initialMessage && String(initialMessage).trim().length) {
                try {
                    // Pane'i aktive et
                    this.activatePane(backendChatId);
                    // Kullanıcı mesajını ekle ve AI yanıtını tetikle
                    chatPane.addMessage({ type: 'user', content: initialMessage, timestamp: Date.now() });
                    chatPane.getAIResponse(initialMessage);
                } catch (e) {}
            }
            
        } catch (error) {
            this.stateManager.addNotification({
                type: 'error',
                message: i18n.t('chat_create_failed', { error: error.message })
            });
        } finally {
            // Slot rezervasyonunu bırak (pane görünür olarak eklendiyse görünür sayaç artık DOM'da)
            this.releaseVisibleSlot();
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
        if (!this.chatPanesContainer) return;
        // Mevcut DOM sırasını al
        const allEls = Array.from(this.chatPanesContainer.querySelectorAll('.chat-pane'));
        const visibleEls = allEls.filter(el => !el.classList.contains('minimized'));
        const minimizedEls = allEls.filter(el => el.classList.contains('minimized'));

        // Görünürleri önce yerleştir, minimize olanları sona ata
        [...visibleEls, ...minimizedEls].forEach(el => {
            if (el.parentNode === this.chatPanesContainer) {
                this.chatPanesContainer.appendChild(el);
            }
        });

        let visibleCount = visibleEls.length;

        // Güvenlik ağı: görünür > max ise fazlaları minimize et
        if (visibleCount > this.maxPanes) {
            const extras = visibleEls.slice(this.maxPanes);
            extras.forEach(el => {
                el.classList.add('minimized');
                const paneId = el.getAttribute('data-pane-id');
                const paneObj = this.chatPanes.get(paneId);
                try { paneObj && paneObj.updateMinimizeIcon && paneObj.updateMinimizeIcon(); } catch(_) {}
            });
            // Yeniden hesapla görünürleri
            const refreshed = Array.from(this.chatPanesContainer.querySelectorAll('.chat-pane'))
                .filter(el => !el.classList.contains('minimized'));
            visibleCount = refreshed.length;
        }

        // Container class'larını temizle
        this.chatPanesContainer.className = 'chat-panes-container';

        // Layout class'ını ekle (görünür pane sayısına göre)
        if (visibleCount === 1) {
            this.chatPanesContainer.classList.add('single-pane');
        } else if (visibleCount === 2) {
            this.chatPanesContainer.classList.add('two-panes');
        } else if (visibleCount === 3) {
            this.chatPanesContainer.classList.add('three-panes');
        } else if (visibleCount >= 4) {
            this.chatPanesContainer.classList.add('four-panes');
        }

        // Eğer görünür pane yoksa (hepsi minimize) karşılama ekranını göster; aksi halde kaldır
        try {
            const existingEmpty = this.chatPanesContainer.querySelector('.empty-chat-state');
            if (visibleCount === 0) {
                if (!existingEmpty) {
                    const empty = document.createElement('div');
                    empty.className = 'empty-chat-state';
                    empty.innerHTML = `
                        <h2>zekai</h2>
                        <p data-i18n="app_welcome_desc">${i18n.t('app_welcome_desc')}</p>
                    `;
                    // Karşılama içeriklerini en başa ekle
                    this.chatPanesContainer.prepend(empty);
                    // i18n uygula
                    try { window.ZekaiI18n?.apply(empty); } catch (_) {}
                }
            } else {
                if (existingEmpty) existingEmpty.remove();
            }
        } catch (_) {}
    }



    /**
     * Pane kapat
     * @param {string} paneId - Pane ID
     */
    closePane(paneId) {
        const pane = this.chatPanes.get(paneId);
        if (!pane) return;

        // Backend: chat'i pasif (is_active = 0) yap (history'den açılan zaten pasif olabilir)
        if (!pane.fromHistory) {
            (async () => {
                try {
                    const res = await fetch(`/api/chats/${paneId}/delete`, { method: 'DELETE' });
                    if (!res.ok) {
                    } else {
                        // Optionally inspect response
                        try { await res.json(); } catch (_) {}
                    }
                } catch (e) {}
            })();
        }

        // Snapshot'ı sadece sohbet başlamışsa sakla (kapanan sohbeti read-only göstermek için)
        // History'den açılan pane'i tekrar snapshot'lama
        if (!pane.fromHistory && pane.hasUserMessage) {
            try {
                this.closedChatSnapshots.set(paneId, {
                    modelName: pane.modelName,
                    modelId: pane.modelId,
                    messages: [...pane.messages]
                });
            } catch (e) {}
        }

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
                <h2>zekai</h2>
                <p data-i18n="app_welcome_desc">${i18n.t('app_welcome_desc')}</p>
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
                        <p>${i18n.t('start_with_model', { model: this.activePane.modelName })}</p>
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

    }
}
