// --- Main Application Entry Point ---

/**
 * Initialize the application
 */
function init() {
    // Initialize theme
    initTheme();
    
    // Setup event listeners
    setupThemeToggle();
    setupPanelEventListeners();
    setupSendAllMessages();
    setupSidebarHandlers();
    
    // Initialize UI
    updatePanels(state.currentLayout);
    
    // Add responsive features
    initResponsiveFeatures();
    
    // Add dynamic styles
    addDynamicStyles();
}

// Run initialization when DOM is fully loaded
document.addEventListener('DOMContentLoaded', init);
