/**
 * State Manager
 * Uygulama durumu yönetimi
 */

import { Helpers } from '../utils/helpers.js';

export class StateManager {
    constructor() {
        this.state = {
            // UI State
            activeModel: null,
            activeChat: null,
            sidebarCollapsed: false,
            currentLayout: 'single',
            
            // Chat State
            messages: [],
            isTyping: false,
            chatHistory: [],
            
            // User State
            user: null,
            preferences: {},
            
            // App State
            isLoading: false,
            error: null,
            notifications: []
        };
        
        this.listeners = new Map();
        this.storageKey = 'zekai_chat_state';
        
        // State'i storage'dan yükle
        this.loadState();
    }

    /**
     * State'i güncelle
     * @param {string} key - State key
     * @param {any} value - Yeni değer
     * @param {boolean} persist - Storage'a kaydet mi?
     */
    setState(key, value, persist = true) {
        const oldValue = this.state[key];
        this.state[key] = value;
        
        // Listener'ları tetikle
        this.notifyListeners(key, value, oldValue);
        
        // Storage'a kaydet
        if (persist) {
            this.saveState();
        }
    }

    /**
     * State'i al
     * @param {string} key - State key
     * @returns {any}
     */
    getState(key) {
        return this.state[key];
    }

    /**
     * Tüm state'i al
     * @returns {Object}
     */
    getAllState() {
        return { ...this.state };
    }

    /**
     * State listener ekle
     * @param {string} key - State key
     * @param {Function} callback - Callback fonksiyonu
     * @returns {Function} - Unsubscribe fonksiyonu
     */
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        
        this.listeners.get(key).add(callback);
        
        // Unsubscribe fonksiyonu döndür
        return () => {
            this.listeners.get(key)?.delete(callback);
        };
    }

    /**
     * Listener'ları tetikle
     * @param {string} key - State key
     * @param {any} newValue - Yeni değer
     * @param {any} oldValue - Eski değer
     */
    notifyListeners(key, newValue, oldValue) {
        const keyListeners = this.listeners.get(key);
        if (keyListeners) {
            keyListeners.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }
    }

    /**
     * State'i storage'a kaydet
     */
    saveState() {
        const stateToSave = {
            activeModel: this.state.activeModel,
            currentLayout: this.state.currentLayout,
            user: this.state.user,
            preferences: this.state.preferences,
            chatHistory: this.state.chatHistory
        };
        
        Helpers.setStorage(this.storageKey, stateToSave);
    }

    /**
     * State'i storage'dan yükle
     */
    loadState() {
        const savedState = Helpers.getStorage(this.storageKey, {});
        
        if (savedState.activeModel) {
            this.state.activeModel = savedState.activeModel;
        }
        
        if (savedState.currentLayout) {
            this.state.currentLayout = savedState.currentLayout;
        }
        
        if (savedState.user) {
            this.state.user = savedState.user;
        }
        
        if (savedState.preferences) {
            this.state.preferences = savedState.preferences;
        }
        
        if (savedState.chatHistory) {
            this.state.chatHistory = savedState.chatHistory;
        }
    }

    /**
     * State'i temizle
     */
    clearState() {
        this.state = {
            activeModel: null,
            activeChat: null,
            sidebarCollapsed: false,
            currentLayout: 'single',
            messages: [],
            isTyping: false,
            chatHistory: [],
            user: null,
            preferences: {},
            isLoading: false,
            error: null,
            notifications: []
        };
        
        this.saveState();
    }

    /**
     * Model seç
     * @param {string} modelName - Model adı
     */
    selectModel(modelName) {
        this.setState('activeModel', modelName);
        this.setState('activeChat', null);
        this.setState('messages', []);
    }

    /**
     * Chat başlat
     * @param {string} chatId - Chat ID
     */
    startChat(chatId) {
        this.setState('activeChat', chatId);
    }

    /**
     * Mesaj ekle
     * @param {Object} message - Mesaj objesi
     */
    addMessage(message) {
        const messages = [...this.state.messages, message];
        this.setState('messages', messages);
    }

    /**
     * Mesajları temizle
     */
    clearMessages() {
        this.setState('messages', []);
    }

    /**
     * Typing durumunu güncelle
     * @param {boolean} isTyping - Typing durumu
     */
    setTyping(isTyping) {
        this.setState('isTyping', isTyping);
    }

    /**
     * Layout değiştir
     * @param {string} layout - Layout adı
     */
    setLayout(layout) {
        this.setState('currentLayout', layout);
    }

    /**
     * Sidebar durumunu değiştir
     * @param {boolean} collapsed - Collapsed durumu
     */
    setSidebarCollapsed(collapsed) {
        this.setState('sidebarCollapsed', collapsed);
    }

    /**
     * Hata ekle
     * @param {string} error - Hata mesajı
     */
    setError(error) {
        this.setState('error', error);
    }

    /**
     * Hatayı temizle
     */
    clearError() {
        this.setState('error', null);
    }

    /**
     * Notification ekle
     * @param {Object} notification - Notification objesi
     */
    addNotification(notification) {
        const notifications = [...this.state.notifications, {
            id: Helpers.generateId(),
            timestamp: Date.now(),
            ...notification
        }];
        this.setState('notifications', notifications);
    }

    /**
     * Notification kaldır
     * @param {string} id - Notification ID
     */
    removeNotification(id) {
        const notifications = this.state.notifications.filter(n => n.id !== id);
        this.setState('notifications', notifications);
    }

    /**
     * Tüm notification'ları temizle
     */
    clearNotifications() {
        this.setState('notifications', []);
    }

    /**
     * Loading durumunu güncelle
     * @param {boolean} isLoading - Loading durumu
     */
    setLoading(isLoading) {
        this.setState('isLoading', isLoading);
    }

    /**
     * User bilgilerini güncelle
     * @param {Object} user - User objesi
     */
    setUser(user) {
        this.setState('user', user);
    }

    /**
     * Preference güncelle
     * @param {string} key - Preference key
     * @param {any} value - Preference value
     */
    setPreference(key, value) {
        const preferences = { ...this.state.preferences, [key]: value };
        this.setState('preferences', preferences);
    }

    /**
     * Chat history'ye ekle
     * @param {Object} chat - Chat objesi
     */
    addToHistory(chat) {
        const chatHistory = [chat, ...this.state.chatHistory];
        this.setState('chatHistory', chatHistory);
    }

    /**
     * Chat history'den kaldır
     * @param {string} chatId - Chat ID
     */
    removeFromHistory(chatId) {
        const chatHistory = this.state.chatHistory.filter(c => c.id !== chatId);
        this.setState('chatHistory', chatHistory);
    }
}
