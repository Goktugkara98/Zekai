/**
 * Validation Utilities
 * Form validasyonu ve input kontrolü
 */

export class Validation {
    /**
     * Email validasyonu
     * @param {string} email - Email adresi
     * @returns {boolean}
     */
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * URL validasyonu
     * @param {string} url - URL
     * @returns {boolean}
     */
    static isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Telefon numarası validasyonu
     * @param {string} phone - Telefon numarası
     * @returns {boolean}
     */
    static isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }

    /**
     * Minimum uzunluk kontrolü
     * @param {string} str - String
     * @param {number} min - Minimum uzunluk
     * @returns {boolean}
     */
    static minLength(str, min) {
        return str && str.length >= min;
    }

    /**
     * Maksimum uzunluk kontrolü
     * @param {string} str - String
     * @param {number} max - Maksimum uzunluk
     * @returns {boolean}
     */
    static maxLength(str, max) {
        return str && str.length <= max;
    }

    /**
     * Boş string kontrolü
     * @param {string} str - String
     * @returns {boolean}
     */
    static isNotEmpty(str) {
        return str && str.trim().length > 0;
    }

    /**
     * Sadece harf kontrolü
     * @param {string} str - String
     * @returns {boolean}
     */
    static isAlpha(str) {
        const alphaRegex = /^[a-zA-Z\s]+$/;
        return alphaRegex.test(str);
    }

    /**
     * Sadece sayı kontrolü
     * @param {string} str - String
     * @returns {boolean}
     */
    static isNumeric(str) {
        const numericRegex = /^\d+$/;
        return numericRegex.test(str);
    }

    /**
     * Alphanumeric kontrolü
     * @param {string} str - String
     * @returns {boolean}
     */
    static isAlphaNumeric(str) {
        const alphaNumericRegex = /^[a-zA-Z0-9]+$/;
        return alphaNumericRegex.test(str);
    }

    /**
     * Şifre güçlülük kontrolü
     * @param {string} password - Şifre
     * @returns {Object} - {isValid: boolean, score: number, feedback: string[]}
     */
    static validatePassword(password) {
        const feedback = [];
        let score = 0;

        if (password.length < 8) {
            feedback.push('En az 8 karakter olmalı');
        } else {
            score += 1;
        }

        if (!/[a-z]/.test(password)) {
            feedback.push('En az bir küçük harf içermeli');
        } else {
            score += 1;
        }

        if (!/[A-Z]/.test(password)) {
            feedback.push('En az bir büyük harf içermeli');
        } else {
            score += 1;
        }

        if (!/\d/.test(password)) {
            feedback.push('En az bir rakam içermeli');
        } else {
            score += 1;
        }

        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            feedback.push('En az bir özel karakter içermeli');
        } else {
            score += 1;
        }

        return {
            isValid: score >= 4,
            score: score,
            feedback: feedback
        };
    }

    /**
     * Form validasyonu
     * @param {Object} formData - Form verisi
     * @param {Object} rules - Validasyon kuralları
     * @returns {Object} - {isValid: boolean, errors: Object}
     */
    static validateForm(formData, rules) {
        const errors = {};
        let isValid = true;

        Object.keys(rules).forEach(field => {
            const value = formData[field];
            const fieldRules = rules[field];
            const fieldErrors = [];

            fieldRules.forEach(rule => {
                if (rule.required && !Validation.isNotEmpty(value)) {
                    fieldErrors.push(rule.message || `${field} gerekli`);
                } else if (value && rule.minLength && !Validation.minLength(value, rule.minLength)) {
                    fieldErrors.push(rule.message || `En az ${rule.minLength} karakter olmalı`);
                } else if (value && rule.maxLength && !Validation.maxLength(value, rule.maxLength)) {
                    fieldErrors.push(rule.message || `En fazla ${rule.maxLength} karakter olmalı`);
                } else if (value && rule.email && !Validation.isValidEmail(value)) {
                    fieldErrors.push(rule.message || 'Geçerli bir email adresi girin');
                } else if (value && rule.phone && !Validation.isValidPhone(value)) {
                    fieldErrors.push(rule.message || 'Geçerli bir telefon numarası girin');
                } else if (value && rule.url && !Validation.isValidURL(value)) {
                    fieldErrors.push(rule.message || 'Geçerli bir URL girin');
                } else if (value && rule.alpha && !Validation.isAlpha(value)) {
                    fieldErrors.push(rule.message || 'Sadece harf içermeli');
                } else if (value && rule.numeric && !Validation.isNumeric(value)) {
                    fieldErrors.push(rule.message || 'Sadece sayı içermeli');
                } else if (value && rule.alphaNumeric && !Validation.isAlphaNumeric(value)) {
                    fieldErrors.push(rule.message || 'Sadece harf ve sayı içermeli');
                } else if (value && rule.custom && !rule.custom(value)) {
                    fieldErrors.push(rule.message || 'Geçersiz değer');
                }
            });

            if (fieldErrors.length > 0) {
                errors[field] = fieldErrors;
                isValid = false;
            }
        });

        return { isValid, errors };
    }

    /**
     * Real-time input validasyonu
     * @param {HTMLInputElement} input - Input elementi
     * @param {Array} rules - Validasyon kuralları
     * @param {Function} callback - Callback fonksiyonu
     */
    static validateInput(input, rules, callback) {
        if (!input) return;

        const validate = () => {
            const value = input.value;
            const errors = [];

            rules.forEach(rule => {
                if (rule.required && !Validation.isNotEmpty(value)) {
                    errors.push(rule.message || 'Bu alan gerekli');
                } else if (value && rule.minLength && !Validation.minLength(value, rule.minLength)) {
                    errors.push(rule.message || `En az ${rule.minLength} karakter olmalı`);
                } else if (value && rule.maxLength && !Validation.maxLength(value, rule.maxLength)) {
                    errors.push(rule.message || `En fazla ${rule.maxLength} karakter olmalı`);
                } else if (value && rule.email && !Validation.isValidEmail(value)) {
                    errors.push(rule.message || 'Geçerli bir email adresi girin');
                } else if (value && rule.custom && !rule.custom(value)) {
                    errors.push(rule.message || 'Geçersiz değer');
                }
            });

            callback(errors, value);
        };

        // Event listeners
        input.addEventListener('input', validate);
        input.addEventListener('blur', validate);
        input.addEventListener('focus', validate);

        // İlk validasyon
        validate();
    }

    /**
     * Sanitize string
     * @param {string} str - String
     * @returns {string}
     */
    static sanitize(str) {
        if (typeof str !== 'string') return '';
        return str
            .replace(/[<>]/g, '') // HTML tag'leri kaldır
            .replace(/javascript:/gi, '') // JavaScript kaldır
            .replace(/on\w+=/gi, '') // Event handler'ları kaldır
            .trim();
    }

    /**
     * XSS koruması
     * @param {string} str - String
     * @returns {string}
     */
    static escapeHtml(str) {
        if (typeof str !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}
