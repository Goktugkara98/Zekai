/**
 * Core configuration settings for the AI Platform
 */
const config = {
    maxPanels: 6,
    defaultLayout: 1,
    animations: {
        panelDelay: 50,
        responseDelay: 1500
    },
    storage: {
        themeKey: 'aiPlatformTheme'
    }
};

// AI model types
const aiTypes = [
    { name: 'GPT-4 Turbo', icon: 'bi bi-cpu' },
    { name: 'Vision Model', icon: 'bi bi-eye' },
    { name: 'Speech Model', icon: 'bi bi-mic' },
    { name: 'Translation AI', icon: 'bi bi-translate' },
    { name: 'Image Generator', icon: 'bi bi-brush' }
];

// Global state management
const state = {
    panelCount: 0,
    currentLayout: 1,
    isDarkMode: false,
    aiTypes: aiTypes
};
