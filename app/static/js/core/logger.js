/**
 * ZekAI Logger Module
 * ==================
 * @description Gelişmiş loglama sistemi
 * @version 1.0.0
 * @author ZekAI Team
 */

const Logger = (function() {
    'use strict';

    // Log seviyeleri
    const LOG_LEVELS = {
        debug:  { priority: 0, color: 'color:#9E9E9E;', prefix: 'DEBUG' },
        info:   { priority: 1, color: 'color:#2196F3;', prefix: 'INFO ' },
        action: { priority: 2, color: 'color:#4CAF50;', prefix: 'ACTION'},
        warn:   { priority: 3, color: 'color:#FFC107;', prefix: 'WARN ' },
        error:  { priority: 4, color: 'color:#F44336;', prefix: 'ERROR'}
    };

    // Konfigürasyon
    let config = {
        enabled: true,
        level: 'debug',
        showTimestamp: true,
        showContext: true,
        maxGroupSize: 5
    };

    /**
     * Konfigürasyonu günceller
     * @param {object} newConfig - Yeni konfigürasyon
     */
    function configure(newConfig) {
        config = { ...config, ...newConfig };
    }

    /**
     * Ana log fonksiyonu
     * @param {string} level - Log seviyesi
     * @param {string} context - Bağlam bilgisi
     * @param {string} message - Log mesajı
     * @param {...*} details - Ek detaylar
     */
    function log(level, context, message, ...details) {
        if (!config.enabled) return;
        
        const levelConfig = LOG_LEVELS[level] || LOG_LEVELS['info'];
        const activeLevelConfig = LOG_LEVELS[config.level] || LOG_LEVELS['debug'];
        
        // Seviye kontrolü
        if (levelConfig.priority < activeLevelConfig.priority) return;

        const timestamp = config.showTimestamp ? 
            new Date().toISOString().substr(11, 12) : '';
        
        const contextStr = config.showContext ? `[${context}]` : '';
        const logPrefix = `%c[${timestamp}] [${levelConfig.prefix}] ${contextStr}`;
        
        const hasObjects = details.some(arg => typeof arg === 'object' && arg !== null);

        if (details.length > 0) {
            if (hasObjects || message.length > 50 || details.length > config.maxGroupSize) {
                console.groupCollapsed(logPrefix, levelConfig.color, message);
                details.forEach(detail => {
                    if (typeof detail === 'object' && detail !== null) {
                        console.dir(detail);
                    } else {
                        console.log(detail);
                    }
                });
                console.groupEnd();
            } else {
                console.log(logPrefix, levelConfig.color, message, ...details);
            }
        } else {
            console.log(logPrefix, levelConfig.color, message);
        }
    }

    /**
     * Debug log
     */
    function debug(context, message, ...details) {
        log('debug', context, message, ...details);
    }

    /**
     * Info log
     */
    function info(context, message, ...details) {
        log('info', context, message, ...details);
    }

    /**
     * Action log
     */
    function action(context, message, ...details) {
        log('action', context, message, ...details);
    }

    /**
     * Warning log
     */
    function warn(context, message, ...details) {
        log('warn', context, message, ...details);
    }

    /**
     * Error log
     */
    function error(context, message, ...details) {
        log('error', context, message, ...details);
    }

    /**
     * Performance ölçümü başlatır
     * @param {string} label - Ölçüm etiketi
     */
    function time(label) {
        console.time(`[PERF] ${label}`);
    }

    /**
     * Performance ölçümünü bitirir
     * @param {string} label - Ölçüm etiketi
     */
    function timeEnd(label) {
        console.timeEnd(`[PERF] ${label}`);
    }

    /**
     * Grup başlatır
     * @param {string} title - Grup başlığı
     */
    function group(title) {
        console.group(title);
    }

    /**
     * Katlanabilir grup başlatır
     * @param {string} title - Grup başlığı
     */
    function groupCollapsed(title) {
        console.groupCollapsed(title);
    }

    /**
     * Grubu bitirir
     */
    function groupEnd() {
        console.groupEnd();
    }

    /**
     * Tablo formatında log
     * @param {array|object} data - Tablo verisi
     */
    function table(data) {
        console.table(data);
    }

    // Public API
    return {
        configure,
        log,
        debug,
        info,
        action,
        warn,
        error,
        time,
        timeEnd,
        group,
        groupCollapsed,
        groupEnd,
        table,
        LOG_LEVELS
    };
})();

// Global olarak erişilebilir yap
window.Logger = Logger;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Logger;
}

