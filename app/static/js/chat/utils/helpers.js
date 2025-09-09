/**
 * Helper Utilities
 * Genel yardımcı fonksiyonlar
 */

export class Helpers {
    /**
     * Debounce fonksiyonu
     * @param {Function} func - Çalıştırılacak fonksiyon
     * @param {number} wait - Bekleme süresi (ms)
     * @param {boolean} immediate - Hemen çalıştır mı?
     * @returns {Function}
     */
    static debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    /**
     * Throttle fonksiyonu
     * @param {Function} func - Çalıştırılacak fonksiyon
     * @param {number} limit - Limit süresi (ms)
     * @returns {Function}
     */
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

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

    /**
     * UUID oluştur
     * @returns {string}
     */
    static generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

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

    /**
     * Zaman farkını hesapla
     * @param {Date} date - Tarih objesi
     * @returns {string}
     */
    static timeAgo(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d`;
        if (hours > 0) return `${hours}h`;
        if (minutes > 0) return `${minutes}m`;
        return `${seconds}s`;
    }

    /**
     * String'i capitalize et
     * @param {string} str - String
     * @returns {string}
     */
    static capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    /**
     * String'i truncate et
     * @param {string} str - String
     * @param {number} length - Maksimum uzunluk
     * @param {string} suffix - Son ek
     * @returns {string}
     */
    static truncate(str, length = 50, suffix = '...') {
        if (str.length <= length) return str;
        return str.substring(0, length) + suffix;
    }

    /**
     * Object'i deep clone et
     * @param {Object} obj - Clone edilecek object
     * @returns {Object}
     */
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => Helpers.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = Helpers.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }

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
            console.error('Storage write error:', error);
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
            console.error('Storage read error:', error);
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
            console.error('Storage remove error:', error);
            return false;
        }
    }

    /**
     * URL parametrelerini parse et
     * @param {string} url - URL string
     * @returns {Object}
     */
    static parseURLParams(url = window.location.href) {
        const params = {};
        const urlObj = new URL(url);
        urlObj.searchParams.forEach((value, key) => {
            params[key] = value;
        });
        return params;
    }

    /**
     * Random sayı üret
     * @param {number} min - Minimum değer
     * @param {number} max - Maksimum değer
     * @returns {number}
     */
    static random(min = 0, max = 1) {
        return Math.random() * (max - min) + min;
    }

    /**
     * Random integer üret
     * @param {number} min - Minimum değer
     * @param {number} max - Maksimum değer
     * @returns {number}
     */
    static randomInt(min = 0, max = 10) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    /**
     * Array'den random item seç
     * @param {Array} array - Array
     * @returns {any}
     */
    static randomChoice(array) {
        return array[Math.floor(Math.random() * array.length)];
    }

    /**
     * Sleep fonksiyonu
     * @param {number} ms - Milisaniye
     * @returns {Promise}
     */
    static sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Retry fonksiyonu
     * @param {Function} fn - Çalıştırılacak fonksiyon
     * @param {number} retries - Deneme sayısı
     * @param {number} delay - Gecikme süresi
     * @returns {Promise}
     */
    static async retry(fn, retries = 3, delay = 1000) {
        try {
            return await fn();
        } catch (error) {
            if (retries > 0) {
                await Helpers.sleep(delay);
                return Helpers.retry(fn, retries - 1, delay);
            }
            throw error;
        }
    }
}
