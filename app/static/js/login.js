/**
 * =============================================================================
 * LOGIN PAGE JAVASCRIPT
 * =============================================================================
 * Giriş yap sayfası için JavaScript işlevleri.
 * Form validasyonu, AJAX istekleri ve kullanıcı etkileşimleri.
 * =============================================================================
 */

// Silence all console output on login page
try {
    const noop = () => {};
    ['log','warn','error','debug','info','trace'].forEach(fn => {
        if (typeof console !== 'undefined' && console[fn]) {
            console[fn] = noop;
        }
    });
} catch (_) {}

class LoginPage {
    constructor() {
        this.form = document.getElementById('login-form');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.passwordToggle = document.getElementById('password-toggle');
        this.loginBtn = document.getElementById('login-btn');
        this.rememberMe = document.getElementById('remember-me');
        this.forgotPassword = document.getElementById('forgot-password');
        
        this.init();
    }

    /**
     * Sayfa başlatma işlevi
     */
    init() {
        this.bindEvents();
        this.checkAuthStatus();
        this.loadSavedCredentials();
        this.addKeyboardSupport();
    }

    /**
     * Event listener'ları bağla
     */
    bindEvents() {
        // Form submit
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                this.handleSubmit(e);
            });
        }

        // Password toggle
        if (this.passwordToggle) {
            this.passwordToggle.addEventListener('click', (e) => {
                this.togglePasswordVisibility(e);
            });
        }

        // Input validations
        if (this.emailInput) {
            this.emailInput.addEventListener('blur', () => {
                this.validateEmail();
            });
            this.emailInput.addEventListener('input', () => {
                this.clearError('email');
            });
        }

        if (this.passwordInput) {
            this.passwordInput.addEventListener('blur', () => {
                this.validatePassword();
            });
            this.passwordInput.addEventListener('input', () => {
                this.clearError('password');
            });
        }

        // Forgot password
        if (this.forgotPassword) {
            this.forgotPassword.addEventListener('click', (e) => {
                this.handleForgotPassword(e);
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    /**
     * Form submit işlevi
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        // Form validasyonu
        if (!this.validateForm()) {
            return;
        }

        // Button loading state
        this.setButtonLoading(true);

        try {
            // Form verilerini al
            const formData = {
                email: this.emailInput.value.trim(),
                password: this.passwordInput.value,
                remember_me: this.rememberMe.checked
            };

            // AJAX isteği gönder
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                // Başarılı giriş
                this.showSuccessMessage(result.message);
                
                // Credentials'ları kaydet (remember me ise)
                if (formData.remember_me) {
                    this.saveCredentials(formData.email);
                } else {
                    this.clearSavedCredentials();
                }

                // Yönlendirme
                setTimeout(() => {
                    window.location.href = result.redirect_url || '/chat';
                }, 1000);

            } else {
                // Hata mesajı göster
                this.showErrorMessage(result.message);
            }

        } catch (error) {
            this.showErrorMessage('Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.');
        } finally {
            this.setButtonLoading(false);
        }
    }

    /**
     * Şifre görünürlüğünü değiştir
     */
    togglePasswordVisibility(e) {
        e.preventDefault();
        
        const icon = this.passwordToggle.querySelector('i');
        
        if (this.passwordInput.type === 'password') {
            this.passwordInput.type = 'text';
            icon.className = 'fas fa-eye-slash';
        } else {
            this.passwordInput.type = 'password';
            icon.className = 'fas fa-eye';
        }
    }

    /**
     * Form validasyonu
     */
    validateForm() {
        let isValid = true;

        // Email validasyonu
        if (!this.validateEmail()) {
            isValid = false;
        }

        // Password validasyonu
        if (!this.validatePassword()) {
            isValid = false;
        }

        return isValid;
    }

    /**
     * Email validasyonu
     */
    validateEmail() {
        const email = this.emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!email) {
            this.showFieldError('email', 'E-posta adresi gereklidir');
            return false;
        }

        if (!emailRegex.test(email)) {
            this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
            return false;
        }

        this.clearError('email');
        return true;
    }

    /**
     * Password validasyonu
     */
    validatePassword() {
        const password = this.passwordInput.value;

        if (!password) {
            this.showFieldError('password', 'Şifre gereklidir');
            return false;
        }

        if (password.length < 6) {
            this.showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
            return false;
        }

        this.clearError('password');
        return true;
    }

    /**
     * Alan hatası göster
     */
    showFieldError(fieldName, message) {
        const errorElement = document.getElementById(`${fieldName}-error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }

        // Input'a error class ekle
        const inputElement = document.getElementById(fieldName);
        if (inputElement) {
            inputElement.style.borderColor = 'var(--error-color)';
        }
    }

    /**
     * Alan hatasını temizle
     */
    clearError(fieldName) {
        const errorElement = document.getElementById(`${fieldName}-error`);
        if (errorElement) {
            errorElement.classList.remove('show');
        }

        // Input'tan error class kaldır
        const inputElement = document.getElementById(fieldName);
        if (inputElement) {
            inputElement.style.borderColor = '';
        }
    }

    /**
     * Başarı mesajı göster
     */
    showSuccessMessage(message) {
        this.showFlashMessage(message, 'success');
    }

    /**
     * Hata mesajı göster
     */
    showErrorMessage(message) {
        this.showFlashMessage(message, 'error');
    }

    /**
     * Flash mesaj göster
     */
    showFlashMessage(message, type) {
        const flashContainer = document.getElementById('flash-messages');
        if (!flashContainer) return;

        // Önceki mesajları temizle
        flashContainer.innerHTML = '';

        // Yeni mesaj oluştur
        const flashMessage = document.createElement('div');
        flashMessage.className = `flash-message flash-${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
        flashMessage.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;

        flashContainer.appendChild(flashMessage);

        // 5 saniye sonra kaldır
        setTimeout(() => {
            if (flashMessage.parentNode) {
                flashMessage.parentNode.removeChild(flashMessage);
            }
        }, 5000);
    }

    /**
     * Button loading durumu
     */
    setButtonLoading(isLoading) {
        if (!this.loginBtn) return;

        if (isLoading) {
            this.loginBtn.disabled = true;
            this.loginBtn.classList.add('loading');
            this.loginBtn.querySelector('span').textContent = 'Giriş yapılıyor...';
        } else {
            this.loginBtn.disabled = false;
            this.loginBtn.classList.remove('loading');
            this.loginBtn.querySelector('span').textContent = 'Giriş Yap';
        }
    }

    /**
     * Kimlik doğrulama durumunu kontrol et
     */
    async checkAuthStatus() {
        try {
            const response = await fetch('/auth/check-auth');
            const result = await response.json();

            if (result.authenticated) {
                // Zaten giriş yapılmış, chat sayfasına yönlendir
                window.location.href = '/chat';
            }
        } catch (error) {
            // Auth status check failed - silently handle
        }
    }

    /**
     * Kaydedilmiş credentials'ları yükle
     */
    loadSavedCredentials() {
        const savedEmail = localStorage.getItem('zekai_remembered_email');
        if (savedEmail && this.emailInput) {
            this.emailInput.value = savedEmail;
            this.rememberMe.checked = true;
        }
    }

    /**
     * Credentials'ları kaydet
     */
    saveCredentials(email) {
        localStorage.setItem('zekai_remembered_email', email);
    }

    /**
     * Kaydedilmiş credentials'ları temizle
     */
    clearSavedCredentials() {
        localStorage.removeItem('zekai_remembered_email');
    }

    /**
     * Şifremi unuttum işlevi
     */
    handleForgotPassword(e) {
        e.preventDefault();
        alert('Şifremi unuttum özelliği yakında eklenecek!');
    }

    /**
     * Klavye desteği
     */
    addKeyboardSupport() {
        // Tab navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const focusableElements = document.querySelectorAll(
                    'input, button, a, [tabindex]:not([tabindex="-1"])'
                );
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
        // Enter key on form
        if (e.key === 'Enter' && this.form && !this.loginBtn.disabled) {
            this.handleSubmit(e);
        }
        
        // Escape key - clear errors
        if (e.key === 'Escape') {
            this.clearError('email');
            this.clearError('password');
        }
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    try {
        new LoginPage();
    } catch (error) {
        // Failed to initialize login page - silently handle
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LoginPage;
}
