/**
 * =============================================================================
 * INDEX PAGE JAVASCRIPT
 * =============================================================================
 * Ana sayfa için JavaScript işlevleri.
 * =============================================================================
 */

// Silence all console output on index page
try {
    const noop = () => {};
    ['log','warn','error','debug','info','trace'].forEach(fn => {
        if (typeof console !== 'undefined' && console[fn]) {
            console[fn] = noop;
        }
    });
} catch (_) {}

class IndexPage {
    constructor() {
        this.loginBtn = document.getElementById('login-btn');
        this.registerBtn = document.getElementById('register-btn');
        
        this.init();
    }

    /**
     * Sayfa başlatma işlevi
     */
    init() {
        this.bindEvents();
        this.checkTheme();
        this.addKeyboardSupport();
    }

    /**
     * Event listener'ları bağla
     */
    bindEvents() {
        // Giriş Yap butonu
        if (this.loginBtn) {
            this.loginBtn.addEventListener('click', (e) => {
                this.handleLogin(e);
            });
        }

        // Kayıt Ol butonu
        if (this.registerBtn) {
            this.registerBtn.addEventListener('click', (e) => {
                this.handleRegister(e);
            });
        }

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    /**
     * Giriş yap butonu işlevi
     */
    handleLogin(e) {
        e.preventDefault();
        
        // Button loading state
        this.setButtonLoading(this.loginBtn, true);
        
        // Simulate API call delay
        setTimeout(() => {
            // TODO: Implement actual login logic
            // For now, redirect to chat page
            window.location.href = '/chat';
        }, 500);
    }

    /**
     * Kayıt ol butonu işlevi
     */
    handleRegister(e) {
        e.preventDefault();
        
        // Button loading state
        this.setButtonLoading(this.registerBtn, true);
        
        // Simulate API call delay
        setTimeout(() => {
            // Redirect to register page
            window.location.href = '/auth/register';
        }, 500);
    }

    /**
     * Buton loading durumu
     */
    setButtonLoading(button, isLoading) {
        if (!button) return;
        
        if (isLoading) {
            button.disabled = true;
            const originalText = button.querySelector('span').textContent;
            button.setAttribute('data-original-text', originalText);
            button.querySelector('span').textContent = 'Yükleniyor...';
            
            // Add loading spinner
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-spinner fa-spin';
            }
        } else {
            button.disabled = false;
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.querySelector('span').textContent = originalText;
                button.removeAttribute('data-original-text');
            }
            
            // Restore original icon
            const icon = button.querySelector('i');
            if (icon && button.id === 'login-btn') {
                icon.className = 'fas fa-sign-in-alt';
            } else if (icon && button.id === 'register-btn') {
                icon.className = 'fas fa-user-plus';
            }
        }
    }

    /**
     * Klavye desteği
     */
    addKeyboardSupport() {
        // Tab navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                // Ensure proper tab order
                const focusableElements = document.querySelectorAll('.btn');
                const focusedElement = document.activeElement;
                const focusedIndex = Array.from(focusableElements).indexOf(focusedElement);
                
                if (e.shiftKey) {
                    // Shift + Tab - go backwards
                    if (focusedIndex <= 0) {
                        e.preventDefault();
                        focusableElements[focusableElements.length - 1].focus();
                    }
                } else {
                    // Tab - go forwards
                    if (focusedIndex >= focusableElements.length - 1) {
                        e.preventDefault();
                        focusableElements[0].focus();
                    }
                }
            }
        });
    }

    /**
     * Klavye kısayolları
     */
    handleKeyboard(e) {
        // Enter key on buttons
        if (e.key === 'Enter' && e.target.classList.contains('btn')) {
            e.target.click();
        }
        
        // Keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'l':
                    e.preventDefault();
                    this.loginBtn?.focus();
                    break;
                case 'r':
                    e.preventDefault();
                    this.registerBtn?.focus();
                    break;
            }
        }
    }

    /**
     * Tema kontrolü
     */
    checkTheme() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    /**
     * Sayfa görünürlük değişikliği
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden - pause any ongoing operations
        } else {
            // Page is visible - resume operations
        }
    }

    /**
     * Hata yönetimi
     */
    handleError(error, context) {
        
        // Show user-friendly error message
        const errorMessage = 'Bir hata oluştu. Lütfen tekrar deneyin.';
        
        // Create temporary error notification
        this.showNotification(errorMessage, 'error');
    }

    /**
     * Bildirim göster
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: '1000',
            opacity: '0',
            transform: 'translateX(100%)',
            transition: 'all 0.3s ease-in-out'
        });
        
        // Set background color based on type
        const colors = {
            info: '#3b82f6',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    try {
        new IndexPage();
    } catch (error) {
        // Failed to initialize index page - silently handle
    }
});

// Sayfa görünürlük değişikliği
document.addEventListener('visibilitychange', () => {
    // Handle page visibility changes if needed
});

// Sayfa kapanmadan önce temizlik
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IndexPage;
}
