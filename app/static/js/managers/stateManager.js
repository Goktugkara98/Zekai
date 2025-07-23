/**
 * ZekAI State Manager Module
 * =========================
 * @description Merkezi state yönetimi ve reactive updates
 * @version 1.0.1
 * @author ZekAI Team
 */

const StateManager = (function() {
    'use strict';

    // Global state
    let state = {};
    
    // Subscriber'lar
    let subscribers = {};
    
    // State değişiklik geçmişi (debug için)
    let changeHistory = [];
    
    // Batch update için
    let batchUpdateTimeout = null;
    let pendingUpdates = new Map();

    /**
     * State'i başlatır
     * @param {object} initialState - Başlangıç state'i
     */
    function initialize(initialState = {}) {
        Logger.info('StateManager', 'Initializing state manager...');
        
        state = deepClone(initialState);
        subscribers = {};
        changeHistory = [];
        
        Logger.info('StateManager', 'State manager initialized', { 
            stateKeys: Object.keys(state),
            stateSize: JSON.stringify(state).length 
        });
    }

    /**
     * State değerini alır
     * @param {string} key - State anahtarı (dot notation destekli)
     * @returns {any} State değeri
     */
    function getState(key) {
        if (!key) return deepClone(state);
        
        const keys = key.split('.');
        let current = state;
        
        for (const k of keys) {
            if (current === null || current === undefined) return undefined;
            current = current[k];
        }
        
        return deepClone(current);
    }

    /**
     * State değerini ayarlar
     * @param {string} key - State anahtarı (dot notation destekli)
     * @param {any} value - Yeni değer
     * @param {boolean} silent - Subscriber'ları tetikleme
     */
    function setState(key, value, silent = false) {
        if (!key) {
            Logger.error('StateManager', 'setState called without key');
            return;
        }

        const oldValue = getState(key);
        
        // Değer değişmemişse işlem yapma - FLASH EFEKTİNİ ÖNLEMEK İÇİN
        if (deepEqual(oldValue, value)) {
            Logger.debug('StateManager', `State not changed for key: ${key}`);
            return;
        }

        const keys = key.split('.');
        let current = state;
        
        // Nested object'leri oluştur
        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (current[k] === null || typeof current[k] !== 'object') {
                current[k] = {};
            }
            current = current[k];
        }
        
        const lastKey = keys[keys.length - 1];
        current[lastKey] = deepClone(value);
        
        // Change history'ye ekle (debug için)
        if (changeHistory.length > 100) {
            changeHistory.shift(); // İlk elemanı kaldır
        }
        
        changeHistory.push({
            timestamp: Date.now(),
            key,
            oldValue: deepClone(oldValue),
            newValue: deepClone(value)
        });
        
        Logger.debug('StateManager', `State updated: ${key}`, { 
            oldValue: oldValue, 
            newValue: value 
        });

        // Subscriber'ları tetikle (batch update ile)
        if (!silent) {
            batchNotifySubscribers(key, value, oldValue);
        }
    }

    /**
     * Batch update ile subscriber'ları bilgilendirir
     * @param {string} key - State anahtarı
     * @param {any} newValue - Yeni değer
     * @param {any} oldValue - Eski değer
     */
    function batchNotifySubscribers(key, newValue, oldValue) {
        // Pending updates'e ekle
        pendingUpdates.set(key, { newValue, oldValue });
        
        // Batch timeout'u ayarla
        if (batchUpdateTimeout) {
            clearTimeout(batchUpdateTimeout);
        }
        
        batchUpdateTimeout = setTimeout(() => {
            // Tüm pending updates'i işle
            const updates = new Map(pendingUpdates);
            pendingUpdates.clear();
            batchUpdateTimeout = null;
            
            updates.forEach((update, updateKey) => {
                notifySubscribers(updateKey, update.newValue, update.oldValue);
            });
        }, 50); // 50ms batch delay - flash efektini önlemek için
    }

    /**
     * Subscriber'ları bilgilendirir
     * @param {string} key - State anahtarı
     * @param {any} newValue - Yeni değer
     * @param {any} oldValue - Eski değer
     */
    function notifySubscribers(key, newValue, oldValue) {
        const keySubscribers = subscribers[key] || [];
        
        keySubscribers.forEach(callback => {
            try {
                callback(newValue, oldValue, key);
            } catch (error) {
                Logger.error('StateManager', `Subscriber error for key: ${key}`, error);
            }
        });
        
        Logger.debug('StateManager', `Notified ${keySubscribers.length} subscribers for key: ${key}`);
    }

    /**
     * State değişikliklerini dinler
     * @param {string} key - State anahtarı
     * @param {function} callback - Callback fonksiyonu
     * @returns {function} Unsubscribe fonksiyonu
     */
    function subscribe(key, callback) {
        if (typeof callback !== 'function') {
            Logger.error('StateManager', 'Subscribe callback must be a function');
            return () => {};
        }

        if (!subscribers[key]) {
            subscribers[key] = [];
        }
        
        subscribers[key].push(callback);
        
        Logger.debug('StateManager', `Subscribed to key: ${key}. Total subscribers: ${subscribers[key].length}`);
        
        // Unsubscribe fonksiyonu döndür
        return function unsubscribe() {
            const index = subscribers[key].indexOf(callback);
            if (index > -1) {
                subscribers[key].splice(index, 1);
                Logger.debug('StateManager', `Unsubscribed from key: ${key}. Remaining subscribers: ${subscribers[key].length}`);
            }
        };
    }

    /**
     * Tüm subscriber'ları kaldırır
     * @param {string} key - State anahtarı (opsiyonel)
     */
    function unsubscribeAll(key) {
        if (key) {
            delete subscribers[key];
            Logger.debug('StateManager', `All subscribers removed for key: ${key}`);
        } else {
            subscribers = {};
            Logger.debug('StateManager', 'All subscribers removed');
        }
    }

    /**
     * State'i sıfırlar
     */
    function reset() {
        Logger.info('StateManager', 'Resetting state manager...');
        
        state = {};
        subscribers = {};
        changeHistory = [];
        
        // Batch update'i temizle
        if (batchUpdateTimeout) {
            clearTimeout(batchUpdateTimeout);
            batchUpdateTimeout = null;
        }
        pendingUpdates.clear();
        
        Logger.info('StateManager', 'State manager reset complete');
    }

    /**
     * State'in snapshot'ını alır
     * @returns {object} State snapshot'ı
     */
    function getSnapshot() {
        return {
            state: deepClone(state),
            subscribers: Object.keys(subscribers).reduce((acc, key) => {
                acc[key] = subscribers[key].length;
                return acc;
            }, {}),
            changeHistoryCount: changeHistory.length,
            lastChanges: changeHistory.slice(-5) // Son 5 değişiklik
        };
    }

    /**
     * State'i validate eder
     * @returns {boolean} Validation sonucu
     */
    function validate() {
        try {
            // Temel validasyonlar
            if (typeof state !== 'object') {
                Logger.error('StateManager', 'State must be an object');
                return false;
            }

            // Required fields kontrolü
            const requiredFields = ['chats', 'chatHistory', 'aiTypes'];
            for (const field of requiredFields) {
                if (!Array.isArray(state[field])) {
                    Logger.error('StateManager', `Required field '${field}' must be an array`);
                    return false;
                }
            }

            // Chat validation
            if (state.chats) {
                for (const chat of state.chats) {
                    if (!chat.id || typeof chat.id !== 'string') {
                        Logger.error('StateManager', 'Each chat must have a valid string ID');
                        return false;
                    }
                    
                    if (typeof chat.aiModelId !== 'number') {
                        Logger.error('StateManager', 'Each chat must have a valid aiModelId');
                        return false;
                    }
                }
            }

            Logger.debug('StateManager', 'State validation passed');
            return true;

        } catch (error) {
            Logger.error('StateManager', 'State validation error', error);
            return false;
        }
    }

    /**
     * State'i localStorage'a kaydeder
     * @param {string} key - localStorage anahtarı
     */
    function saveToLocalStorage(key = 'zekaiState') {
        try {
            const stateToSave = {
                ...state,
                timestamp: Date.now()
            };
            
            localStorage.setItem(key, JSON.stringify(stateToSave));
            Logger.info('StateManager', `State saved to localStorage with key: ${key}`);
            
        } catch (error) {
            Logger.error('StateManager', 'Failed to save state to localStorage', error);
        }
    }

    /**
     * State'i localStorage'dan yükler
     * @param {string} key - localStorage anahtarı
     * @returns {boolean} Yükleme başarılı mı?
     */
    function loadFromLocalStorage(key = 'zekaiState') {
        try {
            const savedState = localStorage.getItem(key);
            if (!savedState) {
                Logger.info('StateManager', 'No saved state found in localStorage');
                return false;
            }
            
            const parsedState = JSON.parse(savedState);
            delete parsedState.timestamp; // Timestamp'i kaldır
            
            // Mevcut state ile merge et
            state = { ...state, ...parsedState };
            
            Logger.info('StateManager', `State loaded from localStorage with key: ${key}`);
            return true;
            
        } catch (error) {
            Logger.error('StateManager', 'Failed to load state from localStorage', error);
            return false;
        }
    }

    /**
     * State change history'sini döndürür
     * @param {number} limit - Döndürülecek maksimum kayıt sayısı
     * @returns {array} Change history
     */
    function getChangeHistory(limit = 10) {
        return changeHistory.slice(-limit);
    }

    /**
     * Deep clone utility
     * @param {any} obj - Klonlanacak obje
     * @returns {any} Klonlanmış obje
     */
    function deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj);
        if (obj instanceof Array) return obj.map(item => deepClone(item));
        if (typeof obj === 'object') {
            const cloned = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    cloned[key] = deepClone(obj[key]);
                }
            }
            return cloned;
        }
        return obj;
    }

    /**
     * Deep equality check utility
     * @param {any} obj1 - İlk obje
     * @param {any} obj2 - İkinci obje
     * @returns {boolean} Eşit mi?
     */
    function deepEqual(obj1, obj2) {
        if (obj1 === obj2) return true;
        
        if (obj1 == null || obj2 == null) return obj1 === obj2;
        
        if (typeof obj1 !== typeof obj2) return false;
        
        if (typeof obj1 !== 'object') return obj1 === obj2;
        
        if (Array.isArray(obj1) !== Array.isArray(obj2)) return false;
        
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);
        
        if (keys1.length !== keys2.length) return false;
        
        for (const key of keys1) {
            if (!keys2.includes(key)) return false;
            if (!deepEqual(obj1[key], obj2[key])) return false;
        }
        
        return true;
    }

    // Public API
    return {
        initialize,
        getState,
        setState,
        subscribe,
        unsubscribeAll,
        reset,
        getSnapshot,
        validate,
        saveToLocalStorage,
        loadFromLocalStorage,
        getChangeHistory
    };
})();

// Global olarak erişilebilir yap
window.StateManager = StateManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StateManager;
}

