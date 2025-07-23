/**
 * ZekAI UI Handlers Module
 * =======================
 * @description UI ile ilgili event handler'lar
 * @version 1.0.0
 * @author ZekAI Team
 */

const UIHandlers = (function() {
    'use strict';

    /**
     * Event handler'ları başlatır
     */
    function initialize() {
        Logger.info('UIHandlers', 'Initializing UI event handlers...');
        
        setupButtonHandlers();
        setupBroadcastHandlers();
        setupHistoryHandlers();
        setupThemeHandlers();
        
        Logger.info('UIHandlers', 'UI event handlers initialized successfully');
    }

    /**
     * Buton handler'larını ayarlar
     */
    function setupButtonHandlers() {
        // Yeni chat butonları
        const welcomeNewChatBtn = document.getElementById('welcome-new-chat-btn');
        const newChatBtn = document.getElementById('new-chat-btn');
        
        if (welcomeNewChatBtn) {
            welcomeNewChatBtn.onclick = handleNewChatClick;
        }
        
        if (newChatBtn) {
            newChatBtn.onclick = handleNewChatClick;
        }

        // Chat'leri temizle butonu
        const clearChatsBtn = document.getElementById('clear-chats-btn');
        if (clearChatsBtn) {
            clearChatsBtn.onclick = handleClearChatsClick;
        }

        Logger.debug('UIHandlers', 'Button handlers setup complete');
    }

    /**
     * Broadcast handler'larını ayarlar
     */
    function setupBroadcastHandlers() {
        const broadcastMessageInput = document.getElementById('broadcast-message-input');
        const sendBroadcastBtn = document.getElementById('send-broadcast-btn');

        if (sendBroadcastBtn && broadcastMessageInput) {
            const broadcastHandler = () => handleBroadcastSend(broadcastMessageInput);
            
            sendBroadcastBtn.addEventListener('click', broadcastHandler);
            
            broadcastMessageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    broadcastHandler();
                }
            });
        }

        Logger.debug('UIHandlers', 'Broadcast handlers setup complete');
    }

    /**
     * Geçmiş handler'larını ayarlar
     */
    function setupHistoryHandlers() {
        // Chat geçmişi restore istekleri
        EventBus.on('chat:history:restore:requested', handleHistoryRestoreRequest);
        
        // Chat geçmişi görüntüleme istekleri
        EventBus.on('chat:history:view:requested', handleHistoryViewRequest);

        Logger.debug('UIHandlers', 'History handlers setup complete');
    }

    /**
     * Tema handler'larını ayarlar
     */
    function setupThemeHandlers() {
        const themeToggleBtn = document.getElementById('theme-toggle');
        
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', handleThemeToggle);
        }

        Logger.debug('UIHandlers', 'Theme handlers setup complete');
    }

    // =============================================================================
    // BUTTON HANDLERS
    // =============================================================================

    /**
     * Yeni chat butonu click handler'ı
     * @param {Event} event - Click eventi
     */
    function handleNewChatClick(event) {
        event.preventDefault();
        Logger.action('UIHandlers', 'New chat button clicked');
        
        EventBus.emit('chat:create:requested', {});
    }

    /**
     * Chat'leri temizle butonu click handler'ı
     * @param {Event} event - Click eventi
     */
    function handleClearChatsClick(event) {
        event.preventDefault();
        Logger.action('UIHandlers', 'Clear chats button clicked');
        
        EventBus.emit('chats:clear:requested', {});
    }

    // =============================================================================
    // BROADCAST HANDLERS
    // =============================================================================

    /**
     * Broadcast gönderme handler'ı
     * @param {HTMLInputElement} inputElement - Input elementi
     */
    function handleBroadcastSend(inputElement) {
        const message = inputElement.value.trim();
        
        if (message === '') {
            alert('Lütfen bir mesaj yazın.');
            return;
        }

        const activeChats = ChatManager.getActiveChats();
        if (activeChats.length === 0) {
            alert('Aktif sohbet yok.');
            return;
        }

        Logger.action('UIHandlers', 'Broadcasting message', { message, chatCount: activeChats.length });
        
        EventBus.emit('broadcast:send:requested', { message });
        
        // Input'u temizle
        inputElement.value = '';
    }

    // =============================================================================
    // HISTORY HANDLERS
    // =============================================================================

    /**
     * Geçmişten restore isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleHistoryRestoreRequest(data) {
        Logger.action('UIHandlers', 'History restore requested', data);
        
        const { chatId, chat } = data;
        
        // Şu an için basit bir alert göster
        // Gelecekte gerçek restore işlemi implement edilebilir
        alert(`'${chat.id.slice(-4)}' ID'li sohbeti geri yükleme henüz tam olarak uygulanmadı.`);
        
        Logger.info('UIHandlers', 'Chat restore data', chat);
    }

    /**
     * Geçmiş görüntüleme isteği handler'ı
     * @param {object} data - Event verisi
     */
    function handleHistoryViewRequest(data) {
        Logger.action('UIHandlers', 'History view requested', data);
        
        const { chatId, chat } = data;
        
        // Şu an için basit bir alert göster
        // Gelecekte modal veya ayrı sayfa ile geçmiş görüntülenebilir
        const aiTypes = StateManager.getState('aiTypes');
        const aiModel = aiTypes.find(ai => ai.id === chat.aiModelId);
        const aiName = aiModel ? aiModel.name : 'Bilinmeyen AI';
        
        alert(`'${aiName}' sohbetinin geçmişini görüntüleme henüz uygulanmadı.`);
        
        Logger.info('UIHandlers', 'Chat history messages', chat.messages);
    }

    // =============================================================================
    // THEME HANDLERS
    // =============================================================================

    /**
     * Tema değiştirme handler'ı
     * @param {Event} event - Click eventi
     */
    function handleThemeToggle(event) {
        event.preventDefault();
        Logger.action('UIHandlers', 'Theme toggle clicked');
        
        const isDarkMode = StateManager.getState('isDarkMode');
        
        if (isDarkMode) {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    }

    /**
     * Koyu modu etkinleştirir
     */
    function enableDarkMode() {
        document.body.classList.add('dark-mode');
        
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
        }
        
        StateManager.setState('isDarkMode', true);
        localStorage.setItem('aiPlatformTheme', 'dark');
        
        Logger.info('UIHandlers', 'Dark mode enabled');
        EventBus.emit('theme:changed', { isDarkMode: true });
    }

    /**
     * Koyu modu devre dışı bırakır
     */
    function disableDarkMode() {
        document.body.classList.remove('dark-mode');
        
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="bi bi-moon"></i>';
        }
        
        StateManager.setState('isDarkMode', false);
        localStorage.setItem('aiPlatformTheme', 'light');
        
        Logger.info('UIHandlers', 'Dark mode disabled');
        EventBus.emit('theme:changed', { isDarkMode: false });
    }

    /**
     * Temayı başlatır
     */
    function initializeTheme() {
        const savedTheme = localStorage.getItem('aiPlatformTheme');
        
        if (savedTheme === 'dark') {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
        
        Logger.info('UIHandlers', `Theme initialized: ${savedTheme || 'light'}`);
    }

    // =============================================================================
    // UTILITY FUNCTIONS
    // =============================================================================

    /**
     * Accordion menü event'lerini ayarlar
     */
    function setupAccordionEvents() {
        const aiCategoriesAccordion = document.getElementById('aiCategoriesAccordion');
        
        if (aiCategoriesAccordion && typeof bootstrap !== 'undefined') {
            const collapseElements = aiCategoriesAccordion.querySelectorAll('.collapse');
            
            collapseElements.forEach(collapseEl => {
                const header = collapseEl.previousElementSibling;
                const chevron = header ? header.querySelector('.category-chevron') : null;
                
                if (chevron) {
                    collapseEl.addEventListener('show.bs.collapse', () => {
                        chevron.classList.remove('bi-chevron-down');
                        chevron.classList.add('bi-chevron-up');
                    });
                    
                    collapseEl.addEventListener('hide.bs.collapse', () => {
                        chevron.classList.remove('bi-chevron-up');
                        chevron.classList.add('bi-chevron-down');
                    });
                }
            });
            
            Logger.debug('UIHandlers', 'Accordion events setup complete');
        }
    }

    /**
     * Responsive event'leri ayarlar
     */
    function setupResponsiveEvents() {
        // Pencere boyutu değişikliklerini dinle
        window.addEventListener('resize', handleWindowResize);
        
        // Başlangıçta bir kez çalıştır
        handleWindowResize();
        
        Logger.debug('UIHandlers', 'Responsive events setup complete');
    }

    /**
     * Pencere boyutu değişikliği handler'ı
     */
    function handleWindowResize() {
        const windowWidth = window.innerWidth;
        
        // Mobil/tablet/desktop durumlarını handle et
        if (windowWidth < 768) {
            // Mobil
            StateManager.setState('ui.isMobile', true);
            StateManager.setState('ui.isTablet', false);
            StateManager.setState('ui.isDesktop', false);
        } else if (windowWidth < 1024) {
            // Tablet
            StateManager.setState('ui.isMobile', false);
            StateManager.setState('ui.isTablet', true);
            StateManager.setState('ui.isDesktop', false);
        } else {
            // Desktop
            StateManager.setState('ui.isMobile', false);
            StateManager.setState('ui.isTablet', false);
            StateManager.setState('ui.isDesktop', true);
        }
        
        EventBus.emit('window:resized', { 
            width: windowWidth, 
            height: window.innerHeight 
        });
    }

    /**
     * Keyboard shortcut'ları ayarlar
     */
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', handleKeyboardShortcut);
        Logger.debug('UIHandlers', 'Keyboard shortcuts setup complete');
    }

    /**
     * Keyboard shortcut handler'ı
     * @param {KeyboardEvent} event - Keyboard eventi
     */
    function handleKeyboardShortcut(event) {
        // Ctrl/Cmd + N: Yeni chat
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            EventBus.emit('chat:create:requested', {});
            return;
        }
        
        // Ctrl/Cmd + Shift + C: Chat'leri temizle
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
            event.preventDefault();
            EventBus.emit('chats:clear:requested', {});
            return;
        }
        
        // Ctrl/Cmd + D: Tema değiştir
        if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
            event.preventDefault();
            handleThemeToggle(event);
            return;
        }
        
        // Escape: Dropdown'ları kapat
        if (event.key === 'Escape') {
            ModelSelector.closeAllDropdowns();
            return;
        }
    }

    // Public API
    return {
        initialize,
        initializeTheme,
        setupAccordionEvents,
        setupResponsiveEvents,
        setupKeyboardShortcuts,
        enableDarkMode,
        disableDarkMode
    };
})();

// Global olarak erişilebilir yap
window.UIHandlers = UIHandlers;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIHandlers;
}

