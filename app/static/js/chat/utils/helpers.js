/**
 * Helper Utilities
 * Genel yardımcı fonksiyonlar
 */

export class Helpers {
    // removed unused: debounce, throttle

    /**
     * Random ID oluştur
     * @param {number} length - ID uzunluğu
     * @returns {string}
     */
    static generateId(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }

    // removed unused: generateUUID

    /**
     * Tarih formatla
     * @param {Date} date - Tarih objesi
     * @param {string} format - Format string
     * @returns {string}
     */
    static formatDate(date, format = 'DD/MM/YYYY HH:mm') {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        
        return format
            .replace('DD', day)
            .replace('MM', month)
            .replace('YYYY', year)
            .replace('HH', hours)
            .replace('mm', minutes);
    }

    // removed unused: timeAgo

    // removed unused: capitalize

    // removed unused: truncate

    // removed unused: deepClone

    /**
     * Local storage'a güvenli yazma
     * @param {string} key - Key
     * @param {any} value - Value
     * @returns {boolean}
     */
static setStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Local storage'dan güvenli okuma
     * @param {string} key - Key
     * @param {any} defaultValue - Default value
     * @returns {any}
     */
    static getStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            return defaultValue;
        }
    }

    /**
     * Local storage'dan silme
     * @param {string} key - Key
     * @returns {boolean}
     */
    static removeStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            return false;
        }
    }

    // removed unused: parseURLParams

    // removed unused: random, randomInt

    /**
     * Array'den random item seç
     * @param {Array} array - Array
     * @returns {any}
     */
    static randomChoice(array) {
        return array[Math.floor(Math.random() * array.length)];
    }

    /**
     * Basit HTML escape
     * @param {string} str
     * @returns {string}
     */
    static escapeHtml(str) {
        if (str === undefined || str === null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
