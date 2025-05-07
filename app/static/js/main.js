// --- Main Application Entry Point ---

// Global state and elements (can be extended)
window.state = window.state || {}; // Ensure state object exists
window.elements = {}; // To be populated on DOMContentLoaded
window.config = window.config || { 
    maxChats: 4,
    defaultLayout: 1
}; // Default configuration

/**
 * Populates the window.elements object with frequently used DOM elements.
 */
function populateDOMElements() {
    console.log('[main.js] Populating DOM elements...');
    
    // Core UI elements
    window.elements.sidebar = document.getElementById('sidebar');
    window.elements.themeToggleBtn = document.getElementById('theme-toggle');
    
    // Chat-related elements
    window.elements.chatContainer = document.getElementById('chat-container');
    window.elements.welcomeScreen = document.getElementById('welcome-screen');
    window.elements.welcomeNewChatBtn = document.getElementById('welcome-new-chat-btn');
    window.elements.newChatBtn = document.getElementById('new-chat-btn');
    window.elements.clearChatsBtn = document.getElementById('clear-chats-btn');
    window.elements.layoutBtns = document.querySelectorAll('.layout-btn');
    
    // Log if critical elements are missing
    if (!window.elements.sidebar) {
        console.warn('[main.js] #sidebar element not found.');
    }
    
    if (!window.elements.chatContainer) {
        console.error('[main.js] #chat-container element not found! Chat functionality will not work.');
    }
    
    console.log('[main.js] DOM elements populated:', window.elements);
}

/**
 * Sets up global event listeners for the application.
 * (e.g., for buttons outside the dynamic panel area)
 */
function setupGlobalEventListeners() {
    console.log('[main.js] Setting up global event listeners...');

    // Example: Send all messages button
    if (window.elements.sendAllBtn) {
        // window.elements.sendAllBtn.addEventListener('click', () => { ... });
        console.log('[main.js] #send-all-btn found. Listener setup can be added here.');
    }

    // Add other global listeners as needed
}

/**
 * Placeholder for setupPanelEventListeners function
 */
function setupPanelEventListeners() {
    console.log('[main.js] setupPanelEventListeners is a placeholder and does not perform any actions.');
}

/**
 * Initialize the application
 */
function init() {
    console.log('[main.js] Initializing application...');
    // Populate DOM elements first
    populateDOMElements();

    // Initialize theme
    if (typeof initTheme === 'function') {
        initTheme();
    } else {
        console.warn('[main.js] initTheme function not found.');
    }
    
    // Setup theme toggle
    if (typeof setupThemeToggle === 'function') {
        setupThemeToggle();
    } else {
        console.warn('[main.js] setupThemeToggle function not found.');
    }

    // Initialize ChatManager
    if (window.ChatManager && typeof window.ChatManager.init === 'function') {
        console.log('[main.js] Initializing ChatManager...');
        window.ChatManager.init();
    } else {
        console.warn('[main.js] ChatManager.init not found or not a function.');
    }

    // Setup global event listeners
    setupGlobalEventListeners(); 

    // Setup sidebar handlers
    if (typeof setupSidebarHandlers === 'function') {
        setupSidebarHandlers();
    } else {
        console.warn('[main.js] setupSidebarHandlers function not found.');
    }

    // Initialize responsive features
    if (typeof initResponsiveFeatures === 'function') {
        initResponsiveFeatures();
    } else {
        console.warn('[main.js] initResponsiveFeatures function not found.');
    }
    
    // Add dynamic styles
    if (typeof addDynamicStyles === 'function') {
        addDynamicStyles();
    } else {
        console.warn('[main.js] addDynamicStyles function not found.');
    }

    console.log('[main.js] Application initialization sequence finished.');
}

// Run initialization when DOM is fully loaded
document.addEventListener('DOMContentLoaded', init);
