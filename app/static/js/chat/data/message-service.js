/**
 * Message Service
 * Mesaj işlemleri ve CRUD operasyonları
 */

import { Helpers } from '../utils/helpers.js';

export class MessageService {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.messages = [];
        this.storageKey = 'zekai_messages';
    }

    /**
     * Servisi başlat
     */
    async init() {
        // Mesajları storage'dan yükle
        this.loadMessages();
        
        // Event listener'ları kur
        this.setupEventListeners();

        console.log('MessageService initialized');
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Mesaj gönderme event'i
        this.eventManager.on('message:sent', (event) => {
            this.handleMessageSent(event.data);
        });

        // Mesaj alma event'i
        this.eventManager.on('message:received', (event) => {
            this.handleMessageReceived(event.data);
        });

        // Mesaj silme event'i
        this.eventManager.on('message:delete', (event) => {
            this.handleMessageDelete(event.data);
        });

        // Mesaj temizleme event'i
        this.eventManager.on('messages:clear', () => {
            this.clearMessages();
        });
    }

    /**
     * Mesaj gönderme işle
     * @param {Object} data - Event data
     */
    handleMessageSent(data) {
        const { message } = data;
        this.addMessage(message);
    }

    /**
     * Mesaj alma işle
     * @param {Object} data - Event data
     */
    handleMessageReceived(data) {
        const { message } = data;
        this.addMessage(message);
    }

    /**
     * Mesaj silme işle
     * @param {Object} data - Event data
     */
    handleMessageDelete(data) {
        const { messageId } = data;
        this.deleteMessage(messageId);
    }

    /**
     * Mesaj ekle
     * @param {Object} message - Mesaj objesi
     */
    addMessage(message) {
        // Mesaj ID'si yoksa oluştur
        if (!message.id) {
            message.id = Helpers.generateId();
        }

        // Timestamp yoksa ekle
        if (!message.timestamp) {
            message.timestamp = Date.now();
        }

        // Mesajı listeye ekle
        this.messages.push(message);

        // State'i güncelle
        this.stateManager.setState('messages', [...this.messages]);

        // Storage'a kaydet
        this.saveMessages();

        // Event emit et
        this.eventManager.emit('message:added', {
            message,
            totalMessages: this.messages.length
        });
    }

    /**
     * Mesaj sil
     * @param {string} messageId - Mesaj ID
     */
    deleteMessage(messageId) {
        const index = this.messages.findIndex(msg => msg.id === messageId);
        if (index === -1) return;

        const deletedMessage = this.messages.splice(index, 1)[0];

        // State'i güncelle
        this.stateManager.setState('messages', [...this.messages]);

        // Storage'a kaydet
        this.saveMessages();

        // Event emit et
        this.eventManager.emit('message:deleted', {
            message: deletedMessage,
            totalMessages: this.messages.length
        });
    }

    /**
     * Tüm mesajları temizle
     */
    clearMessages() {
        this.messages = [];

        // State'i güncelle
        this.stateManager.setState('messages', []);

        // Storage'ı temizle
        Helpers.removeStorage(this.storageKey);

        // Event emit et
        this.eventManager.emit('messages:cleared');
    }

    /**
     * Mesajları al
     * @param {Object} filters - Filtreler
     * @returns {Array}
     */
    getMessages(filters = {}) {
        let filteredMessages = [...this.messages];

        // Model filtresi
        if (filters.model) {
            filteredMessages = filteredMessages.filter(msg => msg.model === filters.model);
        }

        // Kullanıcı filtresi
        if (filters.isUser !== undefined) {
            filteredMessages = filteredMessages.filter(msg => msg.isUser === filters.isUser);
        }

        // Tarih filtresi
        if (filters.startDate) {
            filteredMessages = filteredMessages.filter(msg => msg.timestamp >= filters.startDate);
        }

        if (filters.endDate) {
            filteredMessages = filteredMessages.filter(msg => msg.timestamp <= filters.endDate);
        }

        // Arama filtresi
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            filteredMessages = filteredMessages.filter(msg => 
                msg.content.toLowerCase().includes(searchTerm)
            );
        }

        // Sıralama
        if (filters.sortBy) {
            filteredMessages.sort((a, b) => {
                if (filters.sortBy === 'timestamp') {
                    return filters.sortOrder === 'desc' ? b.timestamp - a.timestamp : a.timestamp - b.timestamp;
                }
                if (filters.sortBy === 'content') {
                    return filters.sortOrder === 'desc' ? 
                        b.content.localeCompare(a.content) : 
                        a.content.localeCompare(b.content);
                }
                return 0;
            });
        }

        // Limit
        if (filters.limit) {
            filteredMessages = filteredMessages.slice(0, filters.limit);
        }

        return filteredMessages;
    }

    /**
     * Mesaj sayısını al
     * @param {Object} filters - Filtreler
     * @returns {number}
     */
    getMessageCount(filters = {}) {
        return this.getMessages(filters).length;
    }

    /**
     * Mesaj istatistiklerini al
     * @returns {Object}
     */
    getMessageStats() {
        const totalMessages = this.messages.length;
        const userMessages = this.messages.filter(msg => msg.isUser).length;
        const assistantMessages = this.messages.filter(msg => !msg.isUser).length;
        
        const modelStats = {};
        this.messages.forEach(msg => {
            if (msg.model) {
                modelStats[msg.model] = (modelStats[msg.model] || 0) + 1;
            }
        });

        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const todayMessages = this.messages.filter(msg => 
            new Date(msg.timestamp) >= today
        ).length;

        return {
            totalMessages,
            userMessages,
            assistantMessages,
            modelStats,
            todayMessages
        };
    }

    /**
     * Mesajları export et
     * @param {Object} options - Export seçenekleri
     * @returns {string}
     */
    exportMessages(options = {}) {
        const { format = 'json', filters = {} } = options;
        const messages = this.getMessages(filters);

        switch (format) {
            case 'json':
                return JSON.stringify(messages, null, 2);
            case 'csv':
                return this.exportToCSV(messages);
            case 'txt':
                return this.exportToTXT(messages);
            default:
                return JSON.stringify(messages, null, 2);
        }
    }

    /**
     * CSV formatında export
     * @param {Array} messages - Mesaj listesi
     * @returns {string}
     */
    exportToCSV(messages) {
        const headers = ['ID', 'Content', 'Is User', 'Model', 'Timestamp'];
        const rows = messages.map(msg => [
            msg.id,
            `"${msg.content.replace(/"/g, '""')}"`,
            msg.isUser,
            msg.model || '',
            Helpers.formatDate(msg.timestamp, 'YYYY-MM-DD HH:mm:ss')
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * TXT formatında export
     * @param {Array} messages - Mesaj listesi
     * @returns {string}
     */
    exportToTXT(messages) {
        return messages.map(msg => {
            const timestamp = Helpers.formatDate(msg.timestamp, 'YYYY-MM-DD HH:mm:ss');
            const sender = msg.isUser ? 'User' : 'Assistant';
            return `[${timestamp}] ${sender}: ${msg.content}`;
        }).join('\n');
    }

    /**
     * Mesajları storage'dan yükle
     */
    loadMessages() {
        const savedMessages = Helpers.getStorage(this.storageKey, []);
        this.messages = savedMessages;
    }

    /**
     * Mesajları storage'a kaydet
     */
    saveMessages() {
        Helpers.setStorage(this.storageKey, this.messages);
    }

    /**
     * Mesaj arama
     * @param {string} query - Arama sorgusu
     * @returns {Array}
     */
    searchMessages(query) {
        if (!query.trim()) return [];

        const searchTerm = query.toLowerCase();
        return this.messages.filter(msg => 
            msg.content.toLowerCase().includes(searchTerm)
        );
    }

    /**
     * Mesaj kategorilerini al
     * @returns {Array}
     */
    getMessageCategories() {
        const categories = new Set();
        
        this.messages.forEach(msg => {
            if (msg.category) {
                categories.add(msg.category);
            }
        });

        return Array.from(categories);
    }

    /**
     * Mesaj etiketlerini al
     * @returns {Array}
     */
    getMessageTags() {
        const tags = new Set();
        
        this.messages.forEach(msg => {
            if (msg.tags && Array.isArray(msg.tags)) {
                msg.tags.forEach(tag => tags.add(tag));
            }
        });

        return Array.from(tags);
    }

    /**
     * Mesajı güncelle
     * @param {string} messageId - Mesaj ID
     * @param {Object} updates - Güncellemeler
     */
    updateMessage(messageId, updates) {
        const index = this.messages.findIndex(msg => msg.id === messageId);
        if (index === -1) return false;

        this.messages[index] = { ...this.messages[index], ...updates };

        // State'i güncelle
        this.stateManager.setState('messages', [...this.messages]);

        // Storage'a kaydet
        this.saveMessages();

        // Event emit et
        this.eventManager.emit('message:updated', {
            message: this.messages[index],
            totalMessages: this.messages.length
        });

        return true;
    }

    /**
     * Mesajı favorilere ekle/çıkar
     * @param {string} messageId - Mesaj ID
     */
    toggleFavorite(messageId) {
        const message = this.messages.find(msg => msg.id === messageId);
        if (!message) return false;

        const isFavorite = message.isFavorite || false;
        return this.updateMessage(messageId, { isFavorite: !isFavorite });
    }

    /**
     * Favori mesajları al
     * @returns {Array}
     */
    getFavoriteMessages() {
        return this.messages.filter(msg => msg.isFavorite);
    }

    /**
     * Servisi temizle
     */
    destroy() {
        // Event listener'ları kaldır
        this.eventManager.off('message:sent');
        this.eventManager.off('message:received');
        this.eventManager.off('message:delete');
        this.eventManager.off('messages:clear');

        console.log('MessageService destroyed');
    }
}
