/**
 * Gelişmiş Günlükleme Sistemi Modülü
 * =================================
 * @description Konsola seviyeli ve formatlı loglar basar.
 */

const LOG_LEVELS = {
    debug:  { priority: 0, color: 'color:#9E9E9E;', prefix: 'DEBUG' },
    info:   { priority: 1, color: 'color:#2196F3;', prefix: 'INFO ' },
    action: { priority: 2, color: 'color:#4CAF50;', prefix: 'ACTION'},
    warn:   { priority: 3, color: 'color:#FFC107;', prefix: 'WARN ' },
    error:  { priority: 4, color: 'color:#F44336;', prefix: 'ERROR'}
};

let settings = {
    isActive: true,
    level: 'debug'
};

/**
 * Logger'ı yapılandırır.
 * @param {boolean} isActive Loglama aktif mi?
 * @param {string} level Gösterilecek minimum log seviyesi.
 */
export function initLogger(isActive = true, level = 'debug') {
    settings.isActive = isActive;
    settings.level = level;
    console.log('%c[Logger] Başlatıldı. Seviye:', 'color:#4CAF50;', level);
}

/**
 * Konsola formatlı bir mesaj yazar.
 * @param {'debug'|'info'|'action'|'warn'|'error'} level Log seviyesi.
 * @param {string} context Logun kaynağı (örn: 'ChatService').
 * @param {string} message Ana log mesajı.
 * @param {...any} details Loglanacak ek objeler veya veriler.
 */
export function log(level, context, message, ...details) {
    if (!settings.isActive) return;

    const levelConfig = LOG_LEVELS[level] || LOG_LEVELS['info'];
    const activeLevelConfig = LOG_LEVELS[settings.level] || LOG_LEVELS['debug'];

    if (levelConfig.priority < activeLevelConfig.priority) return;

    const timestamp = new Date().toISOString().substr(11, 12);
    const logPrefix = `%c[${timestamp}] [${levelConfig.prefix}] [${context}]`;
    const hasObjects = details.some(arg => typeof arg === 'object' && arg !== null);

    if (details.length > 0) {
        if (hasObjects || message.length > 50 || details.length > 1) {
            console.groupCollapsed(logPrefix, levelConfig.color, message);
            details.forEach(detail => console.dir(detail) || console.log(detail));
            console.groupEnd();
        } else {
            console.log(logPrefix, levelConfig.color, message, ...details);
        }
    } else {
        console.log(logPrefix, levelConfig.color, message);
    }
}
