/**
 * DOM Utilities
 * DOM manipülasyonu ve element seçimi için yardımcı fonksiyonlar
 */

export class DOMUtils {
    /**
     * Element seçici - querySelector wrapper
     * @param {string} selector - CSS selector
     * @param {Element} parent - Parent element (opsiyonel)
     * @returns {Element|null}
     */
    static $(selector, parent = document) {
        return parent.querySelector(selector);
    }

    /**
     * Tüm elementleri seç - querySelectorAll wrapper
     * @param {string} selector - CSS selector
     * @param {Element} parent - Parent element (opsiyonel)
     * @returns {NodeList}
     */
    static $$(selector, parent = document) {
        return parent.querySelectorAll(selector);
    }

    /**
     * Element oluştur
     * @param {string} tag - HTML tag
     * @param {Object} attributes - Element attributes
     * @param {string} content - Element content
     * @returns {Element}
     */
    static createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        // Attributes ekle
        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });
        
        // Content ekle
        if (content) {
            element.textContent = content;
        }
        
        return element;
    }

    /**
     * Class ekle
     * @param {Element} element - Target element
     * @param {string} className - Class name
     */
    static addClass(element, className) {
        if (element) {
            element.classList.add(className);
        }
    }

    /**
     * Class kaldır
     * @param {Element} element - Target element
     * @param {string} className - Class name
     */
    static removeClass(element, className) {
        if (element) {
            element.classList.remove(className);
        }
    }

    /**
     * Class toggle
     * @param {Element} element - Target element
     * @param {string} className - Class name
     * @returns {boolean} - Class var mı?
     */
    static toggleClass(element, className) {
        if (element) {
            return element.classList.toggle(className);
        }
        return false;
    }

    /**
     * Element göster
     * @param {Element} element - Target element
     */
    // removed unused method: show()

    /**
     * Element gizle
     * @param {Element} element - Target element
     */
    // removed unused method: hide()

    /**
     * Element'e event listener ekle
     * @param {Element} element - Target element
     * @param {string} event - Event type
     * @param {Function} handler - Event handler
     * @param {Object} options - Event options
     */
    static on(element, event, handler, options = {}) {
        if (element) {
            element.addEventListener(event, handler, options);
        }
    }

    /**
     * Element'ten event listener kaldır
     * @param {Element} element - Target element
     * @param {string} event - Event type
     * @param {Function} handler - Event handler
     */
    static off(element, event, handler) {
        if (element) {
            element.removeEventListener(event, handler);
        }
    }

    /**
     * Element'in parent'ını bul
     * @param {Element} element - Target element
     * @param {string} selector - Parent selector
     * @returns {Element|null}
     */
    // removed unused method: closest()

    /**
     * Element'in child'larını temizle
     * @param {Element} element - Target element
     */
    // removed unused method: clear()

    /**
     * Element'e HTML ekle
     * @param {Element} element - Target element
     * @param {string} html - HTML content
     */
    // removed unused method: appendHTML()

    /**
     * Element'in pozisyonunu al
     * @param {Element} element - Target element
     * @returns {Object} - {top, left, width, height}
     */
    // removed unused method: getPosition()

    /**
     * Scroll to element
     * @param {Element} element - Target element
     * @param {Object} options - Scroll options
     */
    // removed unused method: scrollTo()
}
