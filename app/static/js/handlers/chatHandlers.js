/**
 * ZekAI Chat Handlers Module
 * =========================
 * @description Chat ile ilgili tüm event handler'lar
 * @version 1.0.1
 * @author ZekAI Team
 */

const ChatHandlers = (function() {
    'use strict';

    /**
     * Event handler'ları başlatır
     */
    function initialize() {
        Logger.info('ChatHandlers', 'Initializing chat event handlers...');
        
        setupChatOperationHandlers();
        setupMessageHandlers();
        setupUIInteractionHandlers();
        setupBroadcastHandlers();
        
        Logger.info('ChatHandlers', 'Chat event handlers initialized successfully');
    }

    /**
     * Chat operasyon handler'larını ayarlar
     */
    function setupChatOperationHandlers() {
        // Chat oluşturma
        EventBus.on('chat:create:requested', handleChatCreateRequest);
        
        // Chat kapatma
        EventBus.on('chat:close:requested', handleChatCloseRequest);
        
        // Chat minimize etme
        EventBus.on('chat:minimize:requested', handleChatMinimizeRequest);
        
        // Chat restore etme
        EventBus.on('chat:restore:requested', handleChatRestoreRequest);
        
        // Chat odaklama
        EventBus.on('chat:focus:requested', handleChatFocusRequest);
        
        // Tüm chat'leri temizleme
        EventBus.on('chats:clear:requested', handleClearChatsRequest);
        
        Logger.debug('ChatHandlers', 'Chat operation handlers setup complete');
    }

    /**
     * Mesaj handler'larını ayarlar
     */
    function setupMessageHandlers() {
        // Mesaj gönderme
        EventBus.on('chat:message:send:requested', handleMessageSendRequest);
        
        // Mesaj gönderme başladı
        EventBus.on('chat:message:sending', handleMessageSending);
        
        // Mesaj gönderildi
        EventBus.on('chat:message:sent', handleMessageSent);
        
        // Mesaj hatası
        EventBus.on('chat:message:error', handleMessageError);
        
        Logger.debug('ChatHandlers', 'Message handlers setup complete');
    }

    /**
     * UI etkileşim handler'larını ayarlar
     */
    function setupUIInteractionHandlers() {
        // Chat oluşturuldu
        EventBus.on('chat:created', handleChatCreated);
        
        // Chat kaldırıldı
        EventBus.on('chat:removed', handleChatRemoved);
        
        // Chat minimize edildi
        EventBus.on('chat:minimized', handleChatMinimized);
        
        // Chat restore edildi
        EventBus.on('chat:restored', handleChatRestored);
        
        // Model değiştirildi
        EventBus.on('chat:model:changed', handleModelChanged);
        
        Logger.debug('ChatHandlers', 'UI interaction handlers setup complete');
    }

    /**
     * Broadcast handler'larını ayarlar
     */
    function setupBroadcastHandlers() {
        // Broadcast gönderme
        EventBus.on('broadcast:send:requested', handleBroadcastSendRequest);
        
        // Broadcast tamamlandı
        EventBus.on('chat:broadcast:completed', handleBroadcastCompleted);
        
        Logger.debug('ChatHandlers', 'Broadcast handlers setup complete');
    }

    // =============================================================================
    // CHAT OPERATION HANDLERS
    // =============================================================================

    /**
     * Chat oluşturma isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatCreateRequest(data) {
        Logger.action('ChatHandlers', 'Handling chat create request', data);
        
        try {
            const chatId = ChatManager.createChat(data.aiModelId, data.initialMessages);
            Logger.info('ChatHandlers', `Chat created successfully: ${chatId}`);
        } catch (error) {
            Logger.error('ChatHandlers', 'Failed to create chat', error);
            alert(error.message || 'Sohbet oluşturulamadı.');
        }
    }

    /**
     * Chat kapatma isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatCloseRequest(data) {
        Logger.action('ChatHandlers', 'Handling chat close request', data);
        
        const { chatId } = data;
        const chat = ChatManager.getChat(chatId);
        
        if (!chat) {
            Logger.warn('ChatHandlers', `Chat not found for close request: ${chatId}`);
            return;
        }

        const hasUserMessages = chat.messages && chat.messages.some(msg => msg.isUser);
        
        if (hasUserMessages) {
            if (confirm("Bu sohbeti kapatmak istediğinizden emin misiniz? Konuşma geçmişe kaydedilecek.")) {
                ChatManager.removeChat(chatId, true);
            }
        } else {
            ChatManager.removeChat(chatId, false);
        }
    }

    /**
     * Chat minimize isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatMinimizeRequest(data) {
        Logger.action('ChatHandlers', 'Handling chat minimize request', data);
        
        const { chatId } = data;
        ChatManager.minimizeChat(chatId);
    }

    /**
     * Chat restore isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatRestoreRequest(data) {
        Logger.action('ChatHandlers', 'Handling chat restore request', data);
        
        const { chatId } = data;
        ChatManager.restoreChat(chatId);
    }

    /**
     * Chat odaklama isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatFocusRequest(data) {
        Logger.action('ChatHandlers', 'Handling chat focus request', data);
        
        const { chatId } = data;
        UIManager.focusChat(chatId);
    }

    /**
     * Chat'leri temizleme isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleClearChatsRequest(data) {
        Logger.action('ChatHandlers', 'Handling clear chats request', data);
        
        const chats = StateManager.getState('chats');
        const startedChatsCount = chats.filter(chat => 
            chat.messages && chat.messages.some(msg => msg.isUser)
        ).length;
        const unstartedChatsCount = chats.length - startedChatsCount;

        if (unstartedChatsCount > 0) {
            if (confirm(`${unstartedChatsCount} adet henüz başlanmamış sohbeti kapatmak istediğinizden emin misiniz?`)) {
                const cleared = ChatManager.clearAllChats(false);
                if (cleared > 0) {
                    Logger.info('ChatHandlers', `${cleared} unstarted chats cleared`);
                }
            }
        } else if (chats.length > 0) {
            if (confirm(`Tüm (${chats.length}) sohbetleri kapatmak ve geçmişe taşımak istediğinizden emin misiniz?`)) {
                const cleared = ChatManager.clearAllChats(true);
                if (cleared > 0) {
                    Logger.info('ChatHandlers', `${cleared} chats cleared and moved to history`);
                }
            }
        } else {
            alert('Temizlenecek sohbet yok.');
        }
    }

    // =============================================================================
    // MESSAGE HANDLERS
    // =============================================================================

    /**
     * Mesaj gönderme isteği handler'ı
     * @param {object} data - Event verisi
     */
    async function handleMessageSendRequest(data) {
        Logger.action('ChatHandlers', 'Handling message send request', data);
        
        const { chatId, message } = data;
        
        try {
            await ChatManager.sendMessage(chatId, message);
        } catch (error) {
            Logger.error('ChatHandlers', `Failed to send message to chat ${chatId}`, error);
            // Hata zaten ChatManager tarafından handle edildi
        }
    }

    /**
     * Mesaj gönderme başladı handler'ı
     * @param {object} data - Event verisi
     */
    function handleMessageSending(data) {
        Logger.debug('ChatHandlers', 'Message sending started', data);
        
        const { chatId, message } = data;
        
        // Loading mesajı ekle
        const aiTypes = StateManager.getState('aiTypes');
        const chat = ChatManager.getChat(chatId);
        const aiModel = aiTypes.find(m => m.id === chat.aiModelId);
        const aiName = aiModel ? aiModel.name : 'AI';
        
        const loadingElement = UIManager.addLoadingMessage(chatId, aiName);
        
        // Loading element'i chat'e kaydet (daha sonra değiştirmek için)
        if (chat) {
            chat._loadingElement = loadingElement;
        }
    }

    /**
     * Mesaj gönderildi handler'ı
     * @param {object} data - Event verisi
     */
    function handleMessageSent(data) {
        Logger.debug('ChatHandlers', 'Message sent successfully', data);
        
        const { chatId, userMessage, aiMessage, isFirstUserMessage } = data;
        const chat = ChatManager.getChat(chatId);
        
        if (chat && chat._loadingElement) {
            // Loading mesajını gerçek AI mesajıyla değiştir
            const aiTypes = StateManager.getState('aiTypes');
            const aiModel = aiTypes.find(m => m.id === chat.aiModelId);
            const aiName = aiModel ? aiModel.name : 'AI';
            
            const messageHTML = MessageRenderer.createMessageHTML(
                aiMessage, 
                chat.messages.filter(m => !m.isUser).length === 1, // İlk AI mesajı mı?
                aiName, 
                chat.aiModelId
            );
            
            UIManager.replaceLoadingMessage(chat._loadingElement, messageHTML);
            delete chat._loadingElement;
        }
        
        // İlk kullanıcı mesajıysa dropdown'ları güncelle - FLASH EFEKTİNİ ÖNLEMEK İÇİN OPTİMİZE EDİLDİ
        if (isFirstUserMessage) {
            // Debounce ile dropdown güncelleme
            clearTimeout(window._messageDropdownUpdateTimeout);
            window._messageDropdownUpdateTimeout = setTimeout(() => {
                UIManager.renderActiveChatsDropdown();
            }, 100);
        }
    }

    /**
     * Mesaj hatası handler'ı
     * @param {object} data - Event verisi
     */
    function handleMessageError(data) {
        Logger.error('ChatHandlers', 'Message error occurred', data);
        
        const { chatId, error, errorMessage } = data;
        const chat = ChatManager.getChat(chatId);
        
        if (chat && chat._loadingElement) {
            // Loading mesajını hata mesajıyla değiştir
            const errorHTML = MessageRenderer.createMessageHTML(
                errorMessage,
                false,
                'Sistem',
                chat.aiModelId
            );
            
            UIManager.replaceLoadingMessage(chat._loadingElement, errorHTML);
            delete chat._loadingElement;
        }
    }

    // =============================================================================
    // UI INTERACTION HANDLERS
    // =============================================================================

    /**
     * Chat oluşturuldu handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatCreated(data) {
        Logger.info('ChatHandlers', 'Chat created, updating UI', data);
        
        // UI render'ı StateManager subscription'ı tarafından handle edilecek
        // Burada sadece focus işlemi yapıyoruz
        setTimeout(() => {
            UIManager.focusChat(data.id);
        }, 300); // Flash efektini önlemek için daha uzun bekleme
    }

    /**
     * Chat kaldırıldı handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatRemoved(data) {
        Logger.info('ChatHandlers', 'Chat removed, updating UI', data);
        
        // UI render'ı StateManager subscription'ı tarafından handle edilecek
        // Burada ek işlem gerekmez
    }

    /**
     * Chat minimize edildi handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatMinimized(data) {
        Logger.info('ChatHandlers', 'Chat minimized, updating UI', data);
        
        // UI render'ı StateManager subscription'ı tarafından handle edilecek
        // Burada ek işlem gerekmez
    }

    /**
     * Chat restore edildi handler'ı
     * @param {object} data - Event verisi
     */
    function handleChatRestored(data) {
        Logger.info('ChatHandlers', 'Chat restored, updating UI', data);
        
        // UI render'ı StateManager subscription'ı tarafından handle edilecek
        // Restore edilen chat'e odaklan
        setTimeout(() => {
            UIManager.focusChat(data.chatId);
        }, 300); // Flash efektini önlemek için daha uzun bekleme
    }

    /**
     * Model değiştirildi handler'ı
     * @param {object} data - Event verisi
     */
    function handleModelChanged(data) {
        Logger.info('ChatHandlers', 'Model changed, updating UI', data);
        
        // Dropdown'ı güncelle - FLASH EFEKTİNİ ÖNLEMEK İÇİN OPTİMİZE EDİLDİ
        clearTimeout(window._modelChangeDropdownTimeout);
        window._modelChangeDropdownTimeout = setTimeout(() => {
            UIManager.renderActiveChatsDropdown();
        }, 150);
    }

    // =============================================================================
    // BROADCAST HANDLERS
    // =============================================================================

    /**
     * Broadcast gönderme isteği handler'ı
     * @param {object} data - Event verisi
     */
    async function handleBroadcastSendRequest(data) {
        Logger.action('ChatHandlers', 'Handling broadcast send request', data);
        
        const { message } = data;
        
        if (!message || message.trim() === '') {
            alert('Lütfen bir mesaj yazın.');
            return;
        }
        
        try {
            const result = await ChatManager.sendBroadcastMessage(message);
            Logger.info('ChatHandlers', 'Broadcast completed', result);
        } catch (error) {
            Logger.error('ChatHandlers', 'Broadcast failed', error);
            alert(error.message || 'Yayın mesajı gönderilemedi.');
        }
    }

    /**
     * Broadcast tamamlandı handler'ı
     * @param {object} data - Event verisi
     */
    function handleBroadcastCompleted(data) {
        Logger.info('ChatHandlers', 'Broadcast completed', data);
        
        const { successful, failed, total } = data;
        
        if (failed > 0) {
            alert(`Yayın tamamlandı. Başarılı: ${successful}, Başarısız: ${failed}`);
        } else {
            Logger.info('ChatHandlers', `Broadcast sent to ${successful} chats successfully`);
        }
    }

    // Public API
    return {
        initialize
    };
})();

// Global olarak erişilebilir yap
window.ChatHandlers = ChatHandlers;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatHandlers;
}

