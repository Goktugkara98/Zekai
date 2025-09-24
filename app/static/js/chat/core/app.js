/**
 * Main App Controller
 * Ana uygulama koordinatörü
 */

import { StateManager } from './state-manager.js';
import { EventManager } from './event-manager.js';
import { SidebarController } from '../ui/sidebar-controller.js';
import { ChatPaneController } from '../ui/chat-pane-controller.js';
import { InputController } from '../ui/input-controller.js';
import { ModalController } from '../ui/modal-controller.js';
import { MessageService } from '../data/message-service.js';
import { ModelService } from '../data/model-service.js';
import { AssistantService } from '../data/assistant-service.js';
import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';
import { i18n } from '../utils/i18n.js';

export class App {
    constructor() {
        this.stateManager = new StateManager();
        this.eventManager = new EventManager();
        this.controllers = {};
        this.services = {};
        this.isInitialized = false;
    }

    /**
     * Uygulamayı başlat
     */
    async init() {
        if (this.isInitialized) {
            return;
        }

        try {
            // Initialize i18n before services/controllers
            try { i18n.init(); } catch (_) {}
            
            // Servisleri başlat
            await this.initServices();
            
            // Controller'ları başlat
            await this.initControllers();
            
            // Event listener'ları kur
            this.setupEventListeners();
            
            // State listener'ları kur
            this.setupStateListeners();
            
            // Uygulama hazır
            this.isInitialized = true;
            this.eventManager.emit('app:ready');
            
            // Apply translations to the whole document once initialized
            try { i18n.apply(document); } catch (_) {}
            
            // Auto-open 4 panes on first load (pinned models preferred)
            try { await this.autoOpenInitialPanes(); } catch (_) {}
            
        } catch (error) {
            this.stateManager.setError(i18n.t('app_init_failed'));
        }
    }

    /**
     * Servisleri başlat
     */
    async initServices() {
        this.services.messageService = new MessageService(this.stateManager, this.eventManager);
        this.services.modelService = new ModelService(this.stateManager, this.eventManager);
        this.services.assistantService = new AssistantService(this.stateManager, this.eventManager);
        
        // Servisleri başlat
        await Promise.all([
            this.services.messageService.init(),
            this.services.modelService.init(),
            this.services.assistantService.init()
        ]);
    }

    /**
     * Controller'ları başlat
     */
    async initControllers() {
        this.controllers.sidebar = new SidebarController(this.stateManager, this.eventManager);
        this.controllers.chatPane = new ChatPaneController(this.stateManager, this.eventManager);
        this.controllers.input = new InputController(this.stateManager, this.eventManager);
        this.controllers.modal = new ModalController(this.stateManager, this.eventManager);
        
        // Controller'ları başlat
        await Promise.all([
            this.controllers.sidebar.init(),
            this.controllers.chatPane.init(),
            this.controllers.input.init(),
            this.controllers.modal.init()
        ]);
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Global error handling
        window.addEventListener('error', (event) => {
            this.stateManager.setError(i18n.t('unexpected_error'));
        });

        // Unhandled promise rejection
        window.addEventListener('unhandledrejection', (event) => {
            this.stateManager.setError(i18n.t('unexpected_error'));
        });

        // Visibility change (tab değişimi)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.eventManager.emit('app:hidden');
            } else {
                this.eventManager.emit('app:visible');
            }
        });

        // Online/offline durumu
        window.addEventListener('online', () => {
            this.eventManager.emit('app:online');
            this.stateManager.addNotification({
                type: 'success',
                message: i18n.t('internet_online')
            });
        });

        window.addEventListener('offline', () => {
            this.eventManager.emit('app:offline');
            this.stateManager.addNotification({
                type: 'warning',
                message: i18n.t('internet_offline')
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });

        // Model selection event
        this.eventManager.on('model:selected', (data) => {
            this.handleModelSelection(data);
        });

        // Language change: Sidebar emits 'settings:language-changed'
        this.eventManager.on('settings:language-changed', (event) => {
            const { language } = event.data || {};
            if (!language) return;
            try {
                i18n.setLanguage(language);
                i18n.apply(document);
            } catch (_) {}
        });
    }

    /**
     * State listener'ları kur
     */
    setupStateListeners() {
        // Error state listener
        this.stateManager.subscribe('error', (error) => {
            if (error) {
                this.showError(error);
            }
        });

        // Loading state listener
        this.stateManager.subscribe('isLoading', (isLoading) => {
            this.toggleLoading(isLoading);
        });

        // Notification listener
        this.stateManager.subscribe('notifications', (notifications) => {
            this.showNotifications(notifications);
        });
    }

    /**
     * Model seçimi işle
     * @param {Object} data - Model seçim verisi
     */
    handleModelSelection(data) {
        const { modelName } = data.data || data;
        
        // Chat pane oluşturma işlemi chat pane controller'da yapılıyor
        // Burada sadece state'i güncelle
        
        // State'i güncelle
        this.stateManager.setActiveModel(modelName);
    }

    /**
     * Keyboard shortcuts
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K - Focus input
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const input = DOMUtils.$('.message-input');
            if (input) {
                input.focus();
            }
        }

        // Escape - Close modals
        if (event.key === 'Escape') {
            this.eventManager.emit('modal:close');
        }

        // Ctrl/Cmd + / - Show shortcuts
        if ((event.ctrlKey || event.metaKey) && event.key === '/') {
            event.preventDefault();
            this.eventManager.emit('shortcuts:show');
        }
    }

    /**
     * Hata göster
     * @param {string} error - Hata mesajı
     */
    showError(error) {
        // Toast notification göster
        this.stateManager.addNotification({
            type: 'error',
            message: error,
            duration: 5000
        });
    }

    /**
     * Loading durumunu göster/gizle
     * @param {boolean} isLoading - Loading durumu
     */
    toggleLoading(isLoading) {
        const body = document.body;
        if (isLoading) {
            DOMUtils.addClass(body, 'loading');
        } else {
            DOMUtils.removeClass(body, 'loading');
        }
    }

    /**
     * Notification'ları göster
     * @param {Array} notifications - Notification listesi
     */
    showNotifications(notifications) {
        // Son eklenen notification'ı göster
        const lastNotification = notifications[notifications.length - 1];
        if (lastNotification) {
            this.showToast(lastNotification);
        }
    }

    /**
     * Toast notification göster
     * @param {Object} notification - Notification objesi
     */
    showToast(notification) {
        const toast = DOMUtils.createElement('div', {
            className: `toast toast-${notification.type}`,
            innerHTML: `
                <div class="toast-content">
                    <i class="toast-icon fas fa-${this.getToastIcon(notification.type)}"></i>
                    <span class="toast-message">${notification.message}</span>
                    <button class="toast-close">&times;</button>
                </div>
            `
        });

        // Toast'ı body'ye ekle
        document.body.appendChild(toast);

        // Close button event
        const closeBtn = DOMUtils.$('.toast-close', toast);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.removeToast(toast, notification.id);
            });
        }

        // Auto remove
        const duration = notification.duration || 3000;
        setTimeout(() => {
            this.removeToast(toast, notification.id);
        }, duration);

        // Animation
        setTimeout(() => {
            DOMUtils.addClass(toast, 'show');
        }, 100);
    }

    /**
     * Toast'ı kaldır
     * @param {Element} toast - Toast elementi
     * @param {string} notificationId - Notification ID
     */
    removeToast(toast, notificationId) {
        DOMUtils.addClass(toast, 'hide');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            if (notificationId) {
                this.stateManager.removeNotification(notificationId);
            }
        }, 300);
    }

    /**
     * Toast icon'u al
     * @param {string} type - Notification type
     * @returns {string}
     */
    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Uygulamayı temizle
     */
    destroy() {
        // Controller'ları temizle
        Object.values(this.controllers).forEach(controller => {
            if (controller.destroy) {
                controller.destroy();
            }
        });

        // Servisleri temizle
        Object.values(this.services).forEach(service => {
            if (service.destroy) {
                service.destroy();
            }
        });

        // Event manager'ı temizle
        this.eventManager.clear();

        // State'i temizle
        this.stateManager.clearState();

        this.isInitialized = false;
    }

    /**
     * App instance'ı al
     * @returns {App}
     */
    static getInstance() {
        if (!App.instance) {
            App.instance = new App();
        }
        return App.instance;
    }

    /**
     * Auto-open up to 4 chat panes on initial load using pinned models if any.
     */
    async autoOpenInitialPanes() {
        try {
            const chatPaneCtrl = this.controllers?.chatPane;
            const modelService = this.services?.modelService;
            if (!chatPaneCtrl || !modelService) return;
            if ((chatPaneCtrl.chatPanes?.size || 0) > 0) return; // already opened by user

            const allModels = Array.isArray(modelService.models) ? modelService.models : [];
            if (!allModels.length) return;

            // Read pinned IDs from localStorage
            let favIds = [];
            try { favIds = Helpers.getStorage('favorite_models') || []; } catch (_) { favIds = []; }
            const favSet = new Set(favIds.map(String));

            const pinned = allModels.filter(m => m.isAvailable && favSet.has(String(m.id)));
            const others = allModels.filter(m => m.isAvailable && !favSet.has(String(m.id)));
            const selection = [...pinned, ...others].slice(0, 4);

            // Emit selection in sequence to create panes
            for (const m of selection) {
                this.eventManager.emit('model:selected', { modelName: m.name, modelId: m.modelId });
                // Small delay to avoid race on layout updates
                await new Promise(r => setTimeout(r, 50));
            }
            // Notify UI that auto-open is complete (for preloader coordination)
            this.eventManager.emit('panes:auto-opened', { count: selection.length });
        } catch (_) {}
    }
}

// Global app instance
window.ZekaiApp = App.getInstance();
