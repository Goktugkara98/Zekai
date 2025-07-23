/**
 * Durum Yönetimi Modülü (State Management)
 * =======================================
 * @description Uygulamanın tüm durumunu merkezi olarak yönetir.
 * Diğer modüller durumu okumak ve değiştirmek için bu modülü kullanır.
 */
import { log } from './logger.js';

// Uygulamanın tüm durumunu tutan özel (private) nesne.
const state = {
    chats: [],
    chatHistory: [],
    aiTypes: [],
    allAiCategories: [],
    maxChats: 6
};

/**
 * State modülünü başlatır.
 */
export function initState() {
    log('info', 'State', 'Durum yönetimi başlatıldı.', getState());
}

/**
 * Mevcut durumun bir kopyasını döndürür.
 * @returns {object} Mevcut durum.
 */
export function getState() {
    return JSON.parse(JSON.stringify(state));
}

// --- Getters (Durumu Okuma) ---

export function getChats() { return state.chats; }
export function getChatById(chatId) { return state.chats.find(c => c.id === chatId); }
export function getChatHistory() { return state.chatHistory; }
export function getAiTypes() { return state.aiTypes; }
export function getAiModelById(modelId) { return state.aiTypes.find(m => m.id === modelId); }
export function getAllAiCategories() { return state.allAiCategories; }
export function getMaxChats() { return state.maxChats; }

// --- Setters / Mutations (Durumu Değiştirme) ---

export function setAiTypes(types = []) {
    state.aiTypes = types;
    log('debug', 'State', 'AI tipleri ayarlandı.', types.length);
}

export function setAiCategories(categories = []) {
    state.allAiCategories = categories;
    log('debug', 'State', 'AI kategorileri ayarlandı.', categories.length);
}

export function addChat(chatData) {
    if (state.chats.length < state.maxChats) {
        state.chats.push(chatData);
        return true;
    }
    return false;
}

export function removeChat(chatId) {
    const index = state.chats.findIndex(c => c.id === chatId);
    if (index !== -1) {
        const [removedChat] = state.chats.splice(index, 1);
        return removedChat;
    }
    return null;
}

export function archiveChat(chatData) {
    if (!Array.isArray(state.chatHistory)) {
        state.chatHistory = [];
    }
    chatData.closedTimestamp = Date.now();
    state.chatHistory.unshift(chatData);
    log('debug', 'State', 'Sohbet geçmişe arşivlendi.', chatData.id);
}

export function addMessageToChat(chatId, message) {
    const chat = getChatById(chatId);
    if (chat) {
        chat.messages.push(message);
        chat.lastActivity = Date.now();
        return true;
    }
    return false;
}

export function updateChatModel(chatId, newModelId) {
    const chat = getChatById(chatId);
    if (chat) {
        chat.aiModelId = newModelId;
        return true;
    }
    return false;
}

export function setChatMinimized(chatId, isMinimized) {
    const chat = getChatById(chatId);
    if (chat) {
        chat.isMinimized = isMinimized;
        return true;
    }
    return false;
}
