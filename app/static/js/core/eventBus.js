/**
 * ZekAI Event Bus Module
 * =====================
 * @description Modüller arası iletişim için merkezi event sistemi
 * @version 1.0.0
 * @author ZekAI Team
 */

const EventBus = (function() {
    'use strict';

    // Event listener'ları saklamak için Map
    const listeners = new Map();

    /**
     * Event dinleyici ekler
     * @param {string} event - Event adı
     * @param {function} callback - Çağrılacak fonksiyon
     * @param {object} context - this context (opsiyonel)
     */
    function on(event, callback, context = null) {
        if (!listeners.has(event)) {
            listeners.set(event, []);
        }
        
        listeners.get(event).push({
            callback,
            context,
            once: false
        });
    }

    /**
     * Tek seferlik event dinleyici ekler
     * @param {string} event - Event adı
     * @param {function} callback - Çağrılacak fonksiyon
     * @param {object} context - this context (opsiyonel)
     */
    function once(event, callback, context = null) {
        if (!listeners.has(event)) {
            listeners.set(event, []);
        }
        
        listeners.get(event).push({
            callback,
            context,
            once: true
        });
    }

    /**
     * Event dinleyici kaldırır
     * @param {string} event - Event adı
     * @param {function} callback - Kaldırılacak fonksiyon
     */
    function off(event, callback) {
        if (!listeners.has(event)) return;
        
        const eventListeners = listeners.get(event);
        const index = eventListeners.findIndex(listener => listener.callback === callback);
        
        if (index !== -1) {
            eventListeners.splice(index, 1);
        }
        
        // Eğer hiç listener kalmadıysa event'i sil
        if (eventListeners.length === 0) {
            listeners.delete(event);
        }
    }

    /**
     * Event tetikler
     * @param {string} event - Event adı
     * @param {*} data - Event ile gönderilecek veri
     */
    function emit(event, data = null) {
        if (!listeners.has(event)) return;
        
        const eventListeners = [...listeners.get(event)]; // Kopya oluştur
        
        eventListeners.forEach(listener => {
            try {
                if (listener.context) {
                    listener.callback.call(listener.context, data);
                } else {
                    listener.callback(data);
                }
                
                // Tek seferlik listener'ı kaldır
                if (listener.once) {
                    off(event, listener.callback);
                }
            } catch (error) {
                console.error(`[EventBus] Error in event '${event}':`, error);
            }
        });
    }

    /**
     * Tüm listener'ları temizler
     */
    function clear() {
        listeners.clear();
    }

    /**
     * Belirli bir event'in listener'larını temizler
     * @param {string} event - Event adı
     */
    function clearEvent(event) {
        listeners.delete(event);
    }

    /**
     * Debug için mevcut listener'ları listeler
     */
    function getListeners() {
        const result = {};
        listeners.forEach((value, key) => {
            result[key] = value.length;
        });
        return result;
    }

    // Public API
    return {
        on,
        once,
        off,
        emit,
        clear,
        clearEvent,
        getListeners
    };
})();

// Global olarak erişilebilir yap
window.EventBus = EventBus;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventBus;
}

