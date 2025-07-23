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
        baseURL: 'http://localhost:5000',
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

            console.log('Sending request to:', fullURL, 'with options:', {
                method: finalOptions.method,
                headers: finalOptions.headers,
                body: finalOptions.body ? JSON.parse(finalOptions.body) : null,
                signal: 'AbortController signal set',
                timeout: finalOptions.timeout
            });

            const response = await fetch(fullURL, {
                ...finalOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            console.log('Received response:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                ok: response.ok,
                redirected: response.redirected,
                type: response.type,
                url: response.url
            });

            if (!response.ok) {
                let errorBody;
                try {
                    errorBody = await response.text();
                    // Try to parse as JSON, if it fails, keep as text
                    try {
                        errorBody = JSON.parse(errorBody);
                    } catch (e) {
                        // Not JSON, keep as text
                    }
                } catch (e) {
                    errorBody = 'Could not parse error response';
                }

                const error = new APIError(
                    `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    response
                );
                
                error.responseBody = errorBody;
                console.error('API Error Response:', {
                    status: response.status,
                    statusText: response.statusText,
                    url: fullURL,
                    response: errorBody,
                    headers: Object.fromEntries(response.headers.entries())
                });
                
                throw error;
            }

            const data = await response.json();
            Logger.debug('APIManager', `Response from ${fullURL}`, data);

            return data;
        } catch (error) {
            console.error('Request Error Details:', {
                url: fullURL,
                method: finalOptions.method,
                error: {
                    name: error.name,
                    message: error.message,
                    stack: error.stack,
                    isAbortError: error.name === 'AbortError',
                    isNetworkError: error.message.includes('Failed to fetch') || 
                                  error.message.includes('NetworkError') ||
                                  error.message.includes('fetch failed')
                },
                requestOptions: {
                    method: finalOptions.method,
                    headers: finalOptions.headers,
                    body: finalOptions.body ? JSON.parse(finalOptions.body) : null
                }
            });
            
            Logger.error('APIManager', `Request failed: ${fullURL}`, error);
            
            // Enhance the error with more context
            const enhancedError = new Error(`Request to ${url} failed: ${error.message}`);
            enhancedError.originalError = error;
            enhancedError.url = fullURL;
            enhancedError.method = finalOptions.method;
            
            if (error.name === 'AbortError') {
                enhancedError.message = `Request to ${url} timed out after ${finalOptions.timeout}ms`;
            } else if (error.message.includes('Failed to fetch')) {
                enhancedError.message = `Network error: Could not connect to ${url}. Please check your internet connection.`;
            }
            
            throw enhancedError;
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
            // Log detailed error information
            console.error('Request Error Details:', {
                url,
                options,
                error: {
                    name: error.name,
                    message: error.message,
                    status: error.status,
                    response: error.response,
                    stack: error.stack
                },
                remainingAttempts: attempts - 1
            });

            if (attempts > 1 && shouldRetry(error)) {
                Logger.warn('APIManager', `Retrying request to ${url}. Attempts left: ${attempts - 1}`);
                await delay(config.retryDelay);
                return requestWithRetry(url, options, attempts - 1);
            }
            
            // Enhance the error with more context before throwing
            const enhancedError = new Error(`Request failed after ${config.retryAttempts} attempts: ${error.message}`);
            enhancedError.originalError = error;
            enhancedError.url = url;
            enhancedError.options = options;
            throw enhancedError;
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
            const response = await requestWithRetry('/api/send_message', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            EventBus.emit('api:message:sent', { chatId, response });
            return response;
        } catch (error) {
            // Log detailed error information
            console.error('API Error Details:', {
                message: error.message,
                status: error.status,
                response: error.response,
                stack: error.stack
            });
            
            // Emit the error event with more details
            EventBus.emit('api:message:error', { 
                chatId, 
                error: {
                    message: error.message,
                    status: error.status,
                    response: error.response
                } 
            });
            
            // Re-throw the error with more context
            const enhancedError = new Error(`Failed to send message: ${error.message}`);
            enhancedError.originalError = error;
            enhancedError.chatId = chatId;
            throw enhancedError;
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

