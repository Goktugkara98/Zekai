/**
 * Event Manager
 * Event yönetimi ve custom events
 */

export class EventManager {
    constructor() {
        this.events = new Map();
        this.globalListeners = new Map();
    }

    /**
     * Event listener ekle
     * @param {string} eventName - Event adı
     * @param {Function} callback - Callback fonksiyonu
     * @param {Object} options - Event options
     * @returns {Function} - Unsubscribe fonksiyonu
     */
    on(eventName, callback, options = {}) {
        if (!this.events.has(eventName)) {
            this.events.set(eventName, new Set());
        }
        
        const listener = {
            callback,
            options,
            id: this.generateListenerId()
        };
        
        this.events.get(eventName).add(listener);
        
        // Unsubscribe fonksiyonu döndür
        return () => this.off(eventName, listener.id);
    }

    /**
     * Event listener kaldır
     * @param {string} eventName - Event adı
     * @param {string|Function} listenerId - Listener ID veya callback
     */
    off(eventName, listenerId) {
        const eventListeners = this.events.get(eventName);
        if (!eventListeners) return;
        
        if (typeof listenerId === 'string') {
            // ID ile kaldır
            for (const listener of eventListeners) {
                if (listener.id === listenerId) {
                    eventListeners.delete(listener);
                    break;
                }
            }
        } else if (typeof listenerId === 'function') {
            // Callback ile kaldır
            for (const listener of eventListeners) {
                if (listener.callback === listenerId) {
                    eventListeners.delete(listener);
                    break;
                }
            }
        }
        
        // Eğer hiç listener kalmadıysa event'i sil
        if (eventListeners.size === 0) {
            this.events.delete(eventName);
        }
    }

    /**
     * Event tetikle
     * @param {string} eventName - Event adı
     * @param {any} data - Event data
     * @param {Object} options - Event options
     */
    emit(eventName, data = null, options = {}) {
        const eventListeners = this.events.get(eventName);
        if (!eventListeners) return;
        
        const event = {
            name: eventName,
            data,
            timestamp: Date.now(),
            ...options
        };
        
        // Listeners'ı çalıştır
        eventListeners.forEach(listener => {
            try {
                if (listener.options.once) {
                    // Once listener'ı kaldır
                    eventListeners.delete(listener);
                }
                
                listener.callback(event);
            } catch (error) {
                console.error(`Event listener error for ${eventName}:`, error);
            }
        });
    }

    /**
     * Once event listener (sadece bir kez çalışır)
     * @param {string} eventName - Event adı
     * @param {Function} callback - Callback fonksiyonu
     * @returns {Function} - Unsubscribe fonksiyonu
     */
    once(eventName, callback) {
        return this.on(eventName, callback, { once: true });
    }

    /**
     * Event'i kaldır
     * @param {string} eventName - Event adı
     */
    removeEvent(eventName) {
        this.events.delete(eventName);
    }

    /**
     * Tüm event'leri temizle
     */
    clear() {
        this.events.clear();
        this.globalListeners.clear();
    }

    /**
     * Event listener ID oluştur
     * @returns {string}
     */
    generateListenerId() {
        return `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Global event listener ekle
     * @param {string} selector - CSS selector
     * @param {string} eventName - Event adı
     * @param {Function} callback - Callback fonksiyonu
     * @param {Object} options - Event options
     * @returns {Function} - Unsubscribe fonksiyonu
     */
    delegate(selector, eventName, callback, options = {}) {
        const handler = (e) => {
            const target = e.target.closest(selector);
            if (target) {
                callback(e, target);
            }
        };
        
        document.addEventListener(eventName, handler, options);
        
        // Global listener'ı kaydet
        const listenerId = this.generateListenerId();
        this.globalListeners.set(listenerId, {
            eventName,
            handler,
            options
        });
        
        // Unsubscribe fonksiyonu döndür
        return () => {
            document.removeEventListener(eventName, handler, options);
            this.globalListeners.delete(listenerId);
        };
    }

    /**
     * Custom event oluştur ve tetikle
     * @param {string} eventName - Event adı
     * @param {any} detail - Event detail
     * @param {Object} options - Event options
     */
    dispatchCustomEvent(eventName, detail = null, options = {}) {
        const event = new CustomEvent(eventName, {
            detail,
            bubbles: true,
            cancelable: true,
            ...options
        });
        
        document.dispatchEvent(event);
    }

    /**
     * Event listener sayısını al
     * @param {string} eventName - Event adı
     * @returns {number}
     */
    getListenerCount(eventName) {
        const eventListeners = this.events.get(eventName);
        return eventListeners ? eventListeners.size : 0;
    }

    /**
     * Tüm event'leri listele
     * @returns {Array}
     */
    getEventNames() {
        return Array.from(this.events.keys());
    }

    /**
     * Event listener'ları listele
     * @param {string} eventName - Event adı
     * @returns {Array}
     */
    getListeners(eventName) {
        const eventListeners = this.events.get(eventName);
        return eventListeners ? Array.from(eventListeners) : [];
    }

    /**
     * Event'i pause et
     * @param {string} eventName - Event adı
     */
    pauseEvent(eventName) {
        const eventListeners = this.events.get(eventName);
        if (eventListeners) {
            eventListeners.forEach(listener => {
                listener.paused = true;
            });
        }
    }

    /**
     * Event'i resume et
     * @param {string} eventName - Event adı
     */
    resumeEvent(eventName) {
        const eventListeners = this.events.get(eventName);
        if (eventListeners) {
            eventListeners.forEach(listener => {
                listener.paused = false;
            });
        }
    }

    /**
     * Event'i throttle et
     * @param {string} eventName - Event adı
     * @param {number} delay - Throttle delay
     */
    throttleEvent(eventName, delay = 100) {
        let lastEmit = 0;
        const originalEmit = this.emit.bind(this);
        
        this.emit = (name, data, options) => {
            if (name === eventName) {
                const now = Date.now();
                if (now - lastEmit >= delay) {
                    lastEmit = now;
                    originalEmit(name, data, options);
                }
            } else {
                originalEmit(name, data, options);
            }
        };
    }

    /**
     * Event'i debounce et
     * @param {string} eventName - Event adı
     * @param {number} delay - Debounce delay
     */
    debounceEvent(eventName, delay = 300) {
        let timeoutId;
        const originalEmit = this.emit.bind(this);
        
        this.emit = (name, data, options) => {
            if (name === eventName) {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    originalEmit(name, data, options);
                }, delay);
            } else {
                originalEmit(name, data, options);
            }
        };
    }
}
