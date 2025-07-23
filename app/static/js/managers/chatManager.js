/**
 * ZekAI Chat Manager Module
 * ========================
 * @description Chat operasyonları ve iş mantığı
 * @version 1.0.0
 * @author ZekAI Team
 */

const ChatManager = (function() {
    'use strict';

    /**
     * Yeni chat oluşturur
     * @param {number} aiModelId - AI Model ID
     * @param {array} initialMessages - Başlangıç mesajları
     * @returns {string} Chat ID
     */
    function createChat(aiModelId, initialMessages = []) {
        Logger.action('ChatManager', 'Creating new chat', { aiModelId, initialMessages });

        try {
            const chats = StateManager.getState('chats') || [];
            const maxChats = StateManager.getState('maxChats') || 6;
            const aiTypes = StateManager.getState('aiTypes') || [];
            
            // Log available models for debugging
            Logger.debug('ChatManager', 'Available AI Models:', { 
                count: aiTypes.length,
                modelIds: aiTypes.map(m => m.id)
            });

            // Maksimum chat kontrolü
            const activeVisibleChats = chats.filter(c => c && !c.isMinimized);
            if (activeVisibleChats.length >= maxChats) {
                const errorMsg = `Maksimum ${maxChats} sohbet paneline ulaşıldı.`;
                Logger.warn('ChatManager', errorMsg);
                throw new Error(errorMsg);
            }

            // AI Model validasyonu
            let finalAiModelId = aiModelId ? Number(aiModelId) : null;
            
            // Eğer model ID verilmişse, geçerli mi kontrol et
            if (finalAiModelId) {
                const modelExists = aiTypes.some(m => m.id === finalAiModelId);
                if (!modelExists) {
                    Logger.warn('ChatManager', `Invalid AI Model ID: ${finalAiModelId}. Available IDs: ${aiTypes.map(m => m.id).join(', ')}`);
                    finalAiModelId = null;
                }
            }
            
            // Hala geçerli bir model yoksa, ilk modeli kullan
            if (!finalAiModelId && aiTypes.length > 0) {
                finalAiModelId = aiTypes[0].id;
                Logger.info('ChatManager', `Using default AI model: ${finalAiModelId}`);
            }

            if (!finalAiModelId) {
                const errorMsg = 'Kullanılabilir AI modeli bulunamadı. Lütfen sistem yöneticinize başvurun.';
                Logger.error('ChatManager', errorMsg);
                throw new Error(errorMsg);
            }

            return createNewChat(finalAiModelId, initialMessages);
        
        } catch (error) {
            Logger.error('ChatManager', 'Error in createChat', error);
            throw error; // Re-throw to be handled by the caller
        }
    }

    function createNewChat(finalAiModelId, initialMessages) {
        // Yeni chat objesi oluştur
        const newChat = {
            id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            aiModelId: Number(finalAiModelId),
            messages: [...initialMessages],
            createdAt: Date.now(),
            lastActivity: Date.now(),
            isMinimized: false
        };

        // State'i güncelle
        const currentChats = StateManager.getState('chats') || [];
        const updatedChats = [...currentChats, newChat];
        StateManager.setState('chats', updatedChats);

        Logger.info('ChatManager', `Chat created successfully: ${newChat.id}`, newChat);
        EventBus.emit('chat:created', newChat);

        return newChat.id;
    }

    /**
     * Chat'i kaldırır
     * @param {string} chatId - Chat ID
     * @param {boolean} saveToHistory - Geçmişe kaydet mi?
     */
    function removeChat(chatId, saveToHistory = true) {
        Logger.action('ChatManager', `Removing chat: ${chatId}`, { saveToHistory });

        const chats = StateManager.getState('chats');
        const chat = chats.find(c => c.id === chatId);

        if (!chat) {
            Logger.warn('ChatManager', `Chat not found: ${chatId}`);
            return;
        }

        // Geçmişe kaydet
        if (saveToHistory && chat.messages && chat.messages.some(msg => msg.isUser)) {
            const chatHistory = StateManager.getState('chatHistory');
            const historicalChat = {
                ...chat,
                closedTimestamp: Date.now()
            };
            
            chatHistory.unshift(historicalChat);
            StateManager.setState('chatHistory', chatHistory);
            
            Logger.info('ChatManager', `Chat saved to history: ${chatId}`);
        }

        // Chat'i kaldır
        const updatedChats = chats.filter(c => c.id !== chatId);
        StateManager.setState('chats', updatedChats);

        Logger.info('ChatManager', `Chat removed: ${chatId}`);
        EventBus.emit('chat:removed', { chatId, chat });
    }

    /**
     * Tüm chat'leri temizler
     * @param {boolean} includeStartedChats - Başlamış chat'leri de dahil et
     */
    function clearAllChats(includeStartedChats = false) {
        Logger.action('ChatManager', 'Clearing all chats', { includeStartedChats });

        const chats = StateManager.getState('chats');
        const chatsToRemove = chats.filter(chat => {
            const hasUserMessages = chat.messages && chat.messages.some(msg => msg.isUser);
            return includeStartedChats || !hasUserMessages;
        });

        if (chatsToRemove.length === 0) {
            Logger.info('ChatManager', 'No chats to clear');
            return 0;
        }

        chatsToRemove.forEach(chat => {
            removeChat(chat.id, includeStartedChats);
        });

        Logger.info('ChatManager', `Cleared ${chatsToRemove.length} chats`);
        EventBus.emit('chats:cleared', { count: chatsToRemove.length, includeStartedChats });

        return chatsToRemove.length;
    }

    /**
     * Chat'e mesaj ekler
     * @param {string} chatId - Chat ID
     * @param {string} text - Mesaj metni
     * @param {boolean} isUser - Kullanıcı mesajı mı?
     * @param {object} options - Ek seçenekler
     */
    function addMessage(chatId, text, isUser = true, options = {}) {
        const chats = StateManager.getState('chats');
        const chat = chats.find(c => c.id === chatId);

        if (!chat) {
            Logger.error('ChatManager', `Chat not found: ${chatId}`);
            return;
        }

        const message = {
            isUser,
            text,
            timestamp: Date.now(),
            ...options
        };

        chat.messages.push(message);
        chat.lastActivity = Date.now();

        // State'i güncelle
        StateManager.setState('chats', chats);

        Logger.debug('ChatManager', `Message added to chat ${chatId}`, message);
        EventBus.emit('chat:message:added', { chatId, message });

        return message;
    }

    /**
     * Mesaj gönderir
     * @param {string} chatId - Chat ID
     * @param {string} text - Mesaj metni
     */
    async function sendMessage(chatId, text) {
        Logger.action('ChatManager', `Sending message to chat ${chatId}`);

        const chat = getChat(chatId);
        if (!chat) {
            throw new Error(`Chat bulunamadı: ${chatId}`);
        }

        // Kullanıcı mesajını ekle
        const userMessage = addMessage(chatId, text, true);
        const isFirstUserMessage = chat.messages.filter(m => m.isUser).length === 1;

        EventBus.emit('chat:message:sending', { chatId, message: userMessage });

        try {
            // Konuşma geçmişini hazırla (son mesaj hariç)
            const conversationHistory = chat.messages
                .slice(0, -1)
                .filter(msg => msg.text && String(msg.text).trim() !== '')
                .map(msg => ({
                    role: msg.isUser ? 'user' : 'model',
                    parts: [{ text: String(msg.text).trim() }]
                }));

            // API'ye gönder
            const response = await APIManager.sendMessage(
                chatId,
                chat.aiModelId,
                text,
                conversationHistory
            );

            if (!response.response || typeof response.response !== 'string') {
                throw new Error("AI'dan geçersiz yanıt formatı.");
            }

            // AI yanıtını ekle ve state'i güncelle
            const aiMessage = addMessage(chatId, response.response, false);
            
            // State'i güncelle
            const chats = StateManager.getState('chats');
            const chatIndex = chats.findIndex(c => c.id === chatId);
            
            if (chatIndex !== -1) {
                // Chat'i güncelle
                const updatedChat = { ...chats[chatIndex] };
                
                // Eğer mesaj zaten eklenmediyse ekle
                const messageExists = updatedChat.messages.some(m => 
                    m.timestamp === aiMessage.timestamp && m.text === aiMessage.text
                );
                
                if (!messageExists) {
                    updatedChat.messages = [...updatedChat.messages, aiMessage];
                    updatedChat.lastActivity = Date.now();
                    
                    // State'i güncelle
                    const updatedChats = [...chats];
                    updatedChats[chatIndex] = updatedChat;
                    StateManager.setState('chats', updatedChats);
                    
                    Logger.debug('ChatManager', `AI response added to chat state: ${chatId}`, aiMessage);
                }
            }

            Logger.info('ChatManager', `Message sent and response received for chat ${chatId}`);
            EventBus.emit('chat:message:sent', { 
                chatId, 
                userMessage, 
                aiMessage, 
                isFirstUserMessage 
            });

            return { userMessage, aiMessage };

        } catch (error) {
            Logger.error('ChatManager', `Failed to send message to chat ${chatId}`, error);
            
            // Hata mesajı ekle
            const errorMessage = addMessage(
                chatId,
                `Üzgünüm, bir sorun oluştu: ${error.message || 'Bilinmeyen sunucu hatası'}`,
                false,
                { isError: true }
            );

            EventBus.emit('chat:message:error', { chatId, error, errorMessage });
            throw error;
        }
    }

    /**
     * Broadcast mesaj gönderir
     * @param {string} message - Gönderilecek mesaj
     */
    async function sendBroadcastMessage(message) {
        Logger.action('ChatManager', 'Sending broadcast message', { message });

        const chats = StateManager.getState('chats');
        const activeChats = chats.filter(chat => !chat.isMinimized);

        if (activeChats.length === 0) {
            throw new Error('Aktif sohbet yok.');
        }

        const broadcastMessage = `📢 **YAYIN:** ${message}`;
        const promises = activeChats.map(chat => 
            sendMessage(chat.id, broadcastMessage).catch(error => {
                Logger.error('ChatManager', `Broadcast failed for chat ${chat.id}`, error);
                return { error, chatId: chat.id };
            })
        );

        const results = await Promise.allSettled(promises);
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const failed = results.length - successful;

        Logger.info('ChatManager', `Broadcast completed. Success: ${successful}, Failed: ${failed}`);
        EventBus.emit('chat:broadcast:completed', { successful, failed, total: results.length });

        return { successful, failed, total: results.length };
    }

    /**
     * Chat'in AI modelini değiştirir
     * @param {string} chatId - Chat ID
     * @param {number} newAiModelId - Yeni AI Model ID
     * @returns {object} Güncellenmiş chat objesi
     */
    function changeAIModel(chatId, newAiModelId) {
        Logger.action('ChatManager', `Changing AI model for chat ${chatId}`, { newAiModelId });

        const chats = StateManager.getState('chats');
        const chatIndex = chats.findIndex(c => c.id === chatId);
        
        if (chatIndex === -1) {
            throw new Error(`Chat bulunamadı: ${chatId}`);
        }

        const chat = chats[chatIndex];
        const oldModelId = chat.aiModelId;

        // Model validasyonu
        const aiTypes = StateManager.getState('aiTypes');
        const newModel = aiTypes.find(m => m.id === Number(newAiModelId));

        if (!newModel) {
            throw new Error(`Geçersiz AI Modeli: ${newAiModelId}`);
        }

        // Chat'i güncelle
        const updatedChat = {
            ...chat,
            aiModelId: Number(newAiModelId),
            lastActivity: Date.now()
        };

        // State'i güncelle
        const updatedChats = [...chats];
        updatedChats[chatIndex] = updatedChat;
        StateManager.setState('chats', updatedChats);

        Logger.info('ChatManager', `AI model changed for chat ${chatId}`, { 
            oldModelId,
            newModelId: newAiModelId 
        });

        EventBus.emit('chat:model:changed', { 
            chatId, 
            oldModelId, 
            newModelId: Number(newAiModelId),
            newModel 
        });

        return updatedChat;
    }

    /**
     * Chat'i minimize eder
     * @param {string} chatId - Chat ID
     */
    function minimizeChat(chatId) {
        const chat = getChat(chatId);
        if (chat) {
            chat.isMinimized = true;
            const chats = StateManager.getState('chats');
            StateManager.setState('chats', chats);
            
            Logger.info('ChatManager', `Chat minimized: ${chatId}`);
            EventBus.emit('chat:minimized', { chatId });
        }
    }

    /**
     * Chat'i restore eder
     * @param {string} chatId - Chat ID
     */
    function restoreChat(chatId) {
        const chat = getChat(chatId);
        if (chat) {
            chat.isMinimized = false;
            const chats = StateManager.getState('chats');
            StateManager.setState('chats', chats);
            
            Logger.info('ChatManager', `Chat restored: ${chatId}`);
            EventBus.emit('chat:restored', { chatId });
        }
    }

    /**
     * Chat'i getirir
     * @param {string} chatId - Chat ID
     * @returns {object|null} Chat objesi
     */
    function getChat(chatId) {
        const chats = StateManager.getState('chats');
        return chats.find(c => c.id === chatId) || null;
    }

    /**
     * Aktif chat'leri getirir
     * @returns {array} Aktif chat'ler
     */
    function getActiveChats() {
        const chats = StateManager.getState('chats');
        return chats.filter(c => !c.isMinimized);
    }

    /**
     * Chat istatistiklerini getirir
     * @returns {object} İstatistikler
     */
    function getStats() {
        const chats = StateManager.getState('chats');
        const chatHistory = StateManager.getState('chatHistory');
        
        return {
            totalChats: chats.length,
            activeChats: chats.filter(c => !c.isMinimized).length,
            minimizedChats: chats.filter(c => c.isMinimized).length,
            startedChats: chats.filter(c => c.messages && c.messages.some(m => m.isUser)).length,
            historyCount: chatHistory.length,
            totalMessages: chats.reduce((sum, chat) => sum + (chat.messages ? chat.messages.length : 0), 0)
        };
    }

    // Public API
    return {
        createChat,
        removeChat,
        clearAllChats,
        addMessage,
        sendMessage,
        sendBroadcastMessage,
        changeAIModel,
        minimizeChat,
        restoreChat,
        getChat,
        getActiveChats,
        getStats
    };
})();

// Global olarak erişilebilir yap
window.ChatManager = ChatManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatManager;
}

