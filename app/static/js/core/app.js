/**
 * ZekAI Application Core
 * =====================
 * @description Ana uygulama başlatıcı ve modül koordinatörü
 * @version 1.0.1
 * @author ZekAI Team
 */

const ZekAIApp = (function() {
    'use strict';

    // Uygulama durumu
    let isInitialized = false;
    let initializationPromise = null;

    /**
     * Uygulamayı başlatır
     * @returns {Promise} Başlatma promise'i
     */
    async function initialize() {
        if (isInitialized) {
            Logger.warn('ZekAIApp', 'Application already initialized');
            return;
        }

        if (initializationPromise) {
            Logger.info('ZekAIApp', 'Initialization already in progress, waiting...');
            return initializationPromise;
        }

        initializationPromise = performInitialization();
        return initializationPromise;
    }

    /**
     * Gerçek başlatma işlemini yapar
     * @returns {Promise} Başlatma promise'i
     */
    async function performInitialization() {
        Logger.info('ZekAIApp', 'Starting ZekAI application initialization...');
        Logger.time('AppInitialization');

        try {
            // 1. Core modülleri başlat
            await initializeCoreModules();

            // 2. State'i başlat
            await initializeState();

            // 3. UI Manager'ı başlat
            await initializeUIManager();

            // 4. Handler'ları başlat
            await initializeHandlers();

            // 5. Component'leri başlat
            await initializeComponents();

            // 6. İlk render'ı yap
            await performInitialRender();

            // 7. Son ayarları yap
            await finalizeInitialization();

            isInitialized = true;
            Logger.timeEnd('AppInitialization');
            Logger.info('ZekAIApp', 'ZekAI application initialized successfully');

            EventBus.emit('app:initialized');

        } catch (error) {
            Logger.error('ZekAIApp', 'Application initialization failed', error);
            await handleInitializationError(error);
            throw error;
        }
    }

    /**
     * Core modülleri başlatır
     */
    async function initializeCoreModules() {
        Logger.info('ZekAIApp', 'Initializing core modules...');

        // Logger konfigürasyonu
        Logger.configure({
            enabled: true,
            level: window.DEBUG_LOG_ACTIVE ? 'debug' : 'info',
            showTimestamp: true,
            showContext: true
        });

        Logger.info('ZekAIApp', 'Core modules initialized');
    }

    /**
     * State'i başlatır
     */
    async function initializeState() {
        Logger.info('ZekAIApp', 'Initializing state...');

        // Mevcut window.state ile merge et
        const existingState = window.state || {};
        
        // AI modellerini düzleştir
        const allAiCategories = existingState.allAiCategories || [];
        const aiTypes = allAiCategories.flatMap(category => 
            (category.models || []).map(model => ({
                ...model,
                categoryId: category.id,
                categoryName: category.name,
                categoryIcon: category.icon
            }))
        );
        
        StateManager.initialize({
            chats: existingState.chats || [],
            chatHistory: existingState.chatHistory || [],
            aiTypes: aiTypes,
            allAiCategories: allAiCategories,
            maxChats: 6,
            isDarkMode: false,
            activeChat: null,
            ui: {
                sidebarCollapsed: false,
                welcomeScreenVisible: true,
                isMobile: window.innerWidth < 768,
                isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
                isDesktop: window.innerWidth >= 1024
            }
        });

        // State validasyonu
        if (!StateManager.validate()) {
            throw new Error('State validation failed');
        }

        Logger.info('ZekAIApp', 'State initialized successfully', { 
            aiModelsCount: aiTypes.length,
            categoriesCount: allAiCategories.length 
        });
    }

    /**
     * UI Manager'ı başlatır
     */
    async function initializeUIManager() {
        Logger.info('ZekAIApp', 'Initializing UI Manager...');

        const elementsInitialized = UIManager.initializeElements();
        if (!elementsInitialized) {
            throw new Error('Failed to initialize UI elements');
        }

        Logger.info('ZekAIApp', 'UI Manager initialized successfully');
    }

    /**
     * Handler'ları başlatır
     */
    async function initializeHandlers() {
        Logger.info('ZekAIApp', 'Initializing handlers...');

        // Chat handler'ları
        ChatHandlers.initialize();

        // UI handler'ları
        UIHandlers.initialize();

        // Tema'yı başlat
        UIHandlers.initializeTheme();

        // Accordion event'leri
        UIHandlers.setupAccordionEvents();

        // Responsive event'leri
        UIHandlers.setupResponsiveEvents();

        // Keyboard shortcut'ları
        UIHandlers.setupKeyboardShortcuts();

        Logger.info('ZekAIApp', 'Handlers initialized successfully');
    }

    /**
     * Component'leri başlatır
     */
    async function initializeComponents() {
        Logger.info('ZekAIApp', 'Initializing components...');

        // Model selector'ı ayarla
        ModelSelector.setupSidebarModelSelectors();

        Logger.info('ZekAIApp', 'Components initialized successfully');
    }

    /**
     * İlk render'ı yapar
     */
    async function performInitialRender() {
        Logger.info('ZekAIApp', 'Performing initial render...');

        // Chat'leri render et
        UIManager.renderChats();

        // Dropdown'ları render et
        UIManager.renderActiveChatsDropdown();

        // Geçmişi render et
        UIManager.renderChatHistory();

        Logger.info('ZekAIApp', 'Initial render completed');
    }

    /**
     * Son ayarları yapar
     */
    async function finalizeInitialization() {
        Logger.info('ZekAIApp', 'Finalizing initialization...');

        // Global error handler'ları ayarla
        setupGlobalErrorHandlers();

        // Performance monitoring
        setupPerformanceMonitoring();

        // State change listener'ları
        setupStateChangeListeners();

        Logger.info('ZekAIApp', 'Initialization finalized');
    }

    /**
     * Global error handler'ları ayarlar
     */
    function setupGlobalErrorHandlers() {
        window.onerror = function(message, source, lineno, colno, error) {
            Logger.error('GlobalError', 'Uncaught error occurred', {
                message,
                source,
                lineno,
                colno,
                error: error ? {
                    name: error.name,
                    message: error.message,
                    stack: error.stack
                } : null
            });
            return false;
        };

        window.onunhandledrejection = function(event) {
            Logger.error('GlobalPromiseRejection', 'Unhandled promise rejection', {
                reason: event.reason,
                promise: event.promise
            });
        };

        Logger.debug('ZekAIApp', 'Global error handlers setup');
    }

    /**
     * Performance monitoring ayarlar
     */
    function setupPerformanceMonitoring() {
        // Memory usage monitoring (development only)
        if (window.DEBUG_LOG_ACTIVE) {
            setInterval(() => {
                if (performance.memory) {
                    const memInfo = {
                        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                        limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
                    };
                    
                    if (memInfo.used > 50) { // 50MB üzerinde uyar
                        Logger.warn('Performance', 'High memory usage detected', memInfo);
                    }
                }
            }, 30000); // 30 saniyede bir kontrol et
        }

        Logger.debug('ZekAIApp', 'Performance monitoring setup');
    }

    /**
     * State change listener'ları ayarlar
     */
    function setupStateChangeListeners() {
        // Chat'ler değiştiğinde UI'ı güncelle - FLASH EFEKTİNİ ÖNLEMEK İÇİN OPTİMİZE EDİLDİ
        StateManager.subscribe('chats', (newChats, oldChats) => {
            Logger.debug('ZekAIApp', 'Chats changed, updating UI', {
                oldCount: oldChats ? oldChats.length : 0,
                newCount: newChats ? newChats.length : 0
            });
            
            // Flash efektini önlemek için daha uzun debounce süresi
            clearTimeout(window._chatRenderTimeout);
            window._chatRenderTimeout = setTimeout(() => {
                // Sadece gerçekten değişiklik varsa render et
                const currentChats = StateManager.getState('chats');
                if (JSON.stringify(currentChats) !== JSON.stringify(oldChats)) {
                    UIManager.renderChats();
                    
                    // Dropdown'ı ayrı bir timeout ile render et
                    clearTimeout(window._dropdownRenderTimeout);
                    window._dropdownRenderTimeout = setTimeout(() => {
                        UIManager.renderActiveChatsDropdown();
                    }, 50);
                }
            }, 200); // 200ms debounce
        });

        // Chat geçmişi değiştiğinde UI'ı güncelle
        StateManager.subscribe('chatHistory', (newHistory, oldHistory) => {
            Logger.debug('ZekAIApp', 'Chat history changed, updating UI', {
                oldCount: oldHistory ? oldHistory.length : 0,
                newCount: newHistory ? newHistory.length : 0
            });
            
            clearTimeout(window._historyRenderTimeout);
            window._historyRenderTimeout = setTimeout(() => {
                // Sadece gerçekten değişiklik varsa render et
                const currentHistory = StateManager.getState('chatHistory');
                if (JSON.stringify(currentHistory) !== JSON.stringify(oldHistory)) {
                    UIManager.renderChatHistory();
                }
            }, 150);
        });

        Logger.debug('ZekAIApp', 'State change listeners setup');
    }

    /**
     * Başlatma hatasını handle eder
     * @param {Error} error - Hata objesi
     */
    async function handleInitializationError(error) {
        Logger.error('ZekAIApp', 'Handling initialization error', error);

        // Kullanıcıya hata mesajı göster
        const errorContainer = document.body;
        if (errorContainer) {
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background-color: #dc3545;
                color: white;
                padding: 15px;
                text-align: center;
                z-index: 9999;
                font-family: Arial, sans-serif;
            `;
            errorDiv.innerHTML = `
                <strong>Uygulama Başlatma Hatası:</strong> 
                ${error.message || 'Bilinmeyen hata oluştu'}
                <br>
                <small>Lütfen sayfayı yenileyin veya destek ekibiyle iletişime geçin.</small>
            `;
            errorContainer.prepend(errorDiv);
        }

        // Hata raporlama (gelecekte implement edilebilir)
        // await reportError(error);
    }

    /**
     * Uygulamayı yeniden başlatır
     */
    async function restart() {
        Logger.info('ZekAIApp', 'Restarting application...');

        isInitialized = false;
        initializationPromise = null;

        // State'i sıfırla
        StateManager.reset();

        // Event listener'ları temizle
        EventBus.clear();

        // Dropdown'ları kapat
        ModelSelector.closeAllDropdowns();

        // Timeout'ları temizle
        clearTimeout(window._chatRenderTimeout);
        clearTimeout(window._dropdownRenderTimeout);
        clearTimeout(window._historyRenderTimeout);

        // Yeniden başlat
        await initialize();

        Logger.info('ZekAIApp', 'Application restarted successfully');
    }

    /**
     * Uygulama durumunu döndürür
     * @returns {object} Uygulama durumu
     */
    function getStatus() {
        return {
            isInitialized,
            initializationInProgress: !!initializationPromise && !isInitialized,
            state: StateManager.getSnapshot(),
            stats: ChatManager.getStats(),
            eventListeners: EventBus.getListeners()
        };
    }

    /**
     * Debug bilgilerini döndürür
     * @returns {object} Debug bilgileri
     */
    function getDebugInfo() {
        return {
            version: '1.0.1',
            status: getStatus(),
            performance: performance.memory ? {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            } : null,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
    }

    // Public API
    return {
        initialize,
        restart,
        getStatus,
        getDebugInfo,
        get isInitialized() { return isInitialized; }
    };
})();

// Global olarak erişilebilir yap
window.ZekAIApp = ZekAIApp;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZekAIApp;
}

