/**
 * ZekAI API Manager Module
 * =======================
 * @description Tüm API çağrıları ve HTTP işlemleri
 * @version 1.0.0
 * @author ZekAI Team
 */

const APIManager = (function() {
    'use strict';

    // API konfigürasyonu
    const config = {
        baseURL: '',
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000
    };

    /**
     * HTTP isteği gönderir
     * @param {string} url - İstek URL'i
     * @param {object} options - İstek seçenekleri
     * @returns {Promise} API yanıtı
     */
    async function request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout: config.timeout
        };

        const finalOptions = { ...defaultOptions, ...options };
        const fullURL = config.baseURL + url;

        Logger.debug('APIManager', `${finalOptions.method} ${fullURL}`, finalOptions);

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);

            const response = await fetch(fullURL, {
                ...finalOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new APIError(
                    `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    response
                );
            }

            const data = await response.json();
            Logger.debug('APIManager', `Response from ${fullURL}`, data);

            return data;
        } catch (error) {
            Logger.error('APIManager', `Request failed: ${fullURL}`, error);
            throw error;
        }
    }

    /**
     * Retry mekanizması ile istek gönderir
     * @param {string} url - İstek URL'i
     * @param {object} options - İstek seçenekleri
     * @param {number} attempts - Kalan deneme sayısı
     * @returns {Promise} API yanıtı
     */
    async function requestWithRetry(url, options = {}, attempts = config.retryAttempts) {
        try {
            return await request(url, options);
        } catch (error) {
            if (attempts > 1 && shouldRetry(error)) {
                Logger.warn('APIManager', `Retrying request to ${url}. Attempts left: ${attempts - 1}`);
                await delay(config.retryDelay);
                return requestWithRetry(url, options, attempts - 1);
            }
            throw error;
        }
    }

    /**
     * Hata durumunda retry yapılıp yapılmayacağını belirler
     * @param {Error} error - Hata objesi
     * @returns {boolean} Retry yapılsın mı?
     */
    function shouldRetry(error) {
        // Network hataları ve 5xx server hataları için retry yap
        if (error.name === 'AbortError') return false;
        if (error instanceof APIError) {
            return error.status >= 500;
        }
        return true; // Network hataları için
    }

    /**
     * Belirtilen süre kadar bekler
     * @param {number} ms - Bekleme süresi (milisaniye)
     * @returns {Promise} Bekleme promise'i
     */
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Chat mesajı gönderir
     * @param {string} chatId - Chat ID
     * @param {number} aiModelId - AI Model ID
     * @param {string} message - Mesaj
     * @param {array} history - Konuşma geçmişi
     * @returns {Promise} API yanıtı
     */
    async function sendMessage(chatId, aiModelId, message, history = []) {
        const payload = {
            chatId,
            aiModelId,
            chat_message: message,
            history
        };

        EventBus.emit('api:message:sending', { chatId, message });

        try {
            const response = await requestWithRetry('/send_message', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            EventBus.emit('api:message:sent', { chatId, response });
            return response;
        } catch (error) {
            EventBus.emit('api:message:error', { chatId, error });
            throw error;
        }
    }

    /**
     * AI modellerini getirir
     * @returns {Promise} AI modelleri listesi
     */
    async function getAIModels() {
        try {
            const response = await requestWithRetry('/api/ai-models');
            EventBus.emit('api:models:loaded', response);
            return response;
        } catch (error) {
            EventBus.emit('api:models:error', error);
            throw error;
        }
    }

    /**
     * AI kategorilerini getirir
     * @returns {Promise} AI kategorileri listesi
     */
    async function getAICategories() {
        try {
            const response = await requestWithRetry('/api/ai-categories');
            EventBus.emit('api:categories:loaded', response);
            return response;
        } catch (error) {
            EventBus.emit('api:categories:error', error);
            throw error;
        }
    }

    /**
     * Chat geçmişini getirir
     * @param {string} chatId - Chat ID
     * @returns {Promise} Chat geçmişi
     */
    async function getChatHistory(chatId) {
        try {
            const response = await requestWithRetry(`/api/chat/${chatId}/history`);
            return response;
        } catch (error) {
            Logger.error('APIManager', `Failed to get chat history for ${chatId}`, error);
            throw error;
        }
    }

    /**
     * Chat'i kaydeder
     * @param {object} chatData - Chat verisi
     * @returns {Promise} Kaydetme sonucu
     */
    async function saveChat(chatData) {
        try {
            const response = await requestWithRetry('/api/chat/save', {
                method: 'POST',
                body: JSON.stringify(chatData)
            });
            return response;
        } catch (error) {
            Logger.error('APIManager', 'Failed to save chat', error);
            throw error;
        }
    }

    /**
     * Chat'i siler
     * @param {string} chatId - Chat ID
     * @returns {Promise} Silme sonucu
     */
    async function deleteChat(chatId) {
        try {
            const response = await requestWithRetry(`/api/chat/${chatId}`, {
                method: 'DELETE'
            });
            return response;
        } catch (error) {
            Logger.error('APIManager', `Failed to delete chat ${chatId}`, error);
            throw error;
        }
    }

    /**
     * Konfigürasyonu günceller
     * @param {object} newConfig - Yeni konfigürasyon
     */
    function configure(newConfig) {
        Object.assign(config, newConfig);
        Logger.info('APIManager', 'Configuration updated', config);
    }

    // Public API
    return {
        configure,
        request,
        requestWithRetry,
        sendMessage,
        getAIModels,
        getAICategories,
        getChatHistory,
        saveChat,
        deleteChat
    };
})();

/**
 * API Error sınıfı
 */
class APIError extends Error {
    constructor(message, status, response) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.response = response;
    }
}

// Global olarak erişilebilir yap
window.APIManager = APIManager;
window.APIError = APIError;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIManager, APIError };
}

