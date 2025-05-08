/**
 * ZekAI Core Configuration Module
 * ============================
 * @description Central configuration settings for the ZekAI platform
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Application Settings
 *    1.1 General Configuration
 *    1.2 Animation Settings
 *    1.3 Storage Keys
 * 
 * 2. AI Models
 *    2.1 Model Definitions
 * 
 * 3. Global State
 *    3.1 Application State
 */

//=============================================================================
// 1. APPLICATION SETTINGS
//=============================================================================

/**
 * 1.1 General Configuration
 * ----------------------
 * Core settings that control application behavior
 */
const config = {
    // Maximum number of panels that can be open simultaneously
    maxPanels: 6,
    
    // Default layout configuration (1-6)
    defaultLayout: 1,
    
    /**
     * 1.2 Animation Settings
     * -------------------
     * Timing configurations for animations
     */
    animations: {
        // Delay between panel operations (ms)
        panelDelay: 50,
        
        // Delay before showing AI response (ms)
        responseDelay: 1500
    },
    
    /**
     * 1.3 Storage Keys
     * -------------
     * Keys used for localStorage
     */
    storage: {
        // Key for storing theme preference
        themeKey: 'aiPlatformTheme'
    }
};

//=============================================================================
// 2. AI MODELS
//=============================================================================

/**
 * 2.1 Model Definitions
 * ------------------
 * Available AI model types with their display properties
 */
const aiTypes = [
    { id: 'gpt4', name: 'GPT-4 Turbo', icon: 'bi bi-cpu' },
    { id: 'vision', name: 'Vision Model', icon: 'bi bi-eye' },
    { id: 'speech', name: 'Speech Model', icon: 'bi bi-mic' },
    { id: 'translate', name: 'Translation AI', icon: 'bi bi-translate' },
    { id: 'image', name: 'Image Generator', icon: 'bi bi-brush' }
];

//=============================================================================
// 3. GLOBAL STATE
//=============================================================================

/**
 * 3.1 Application State
 * ------------------
 * Global state object for tracking application status
 */
const state = {
    // Current number of open panels
    panelCount: 0,
    
    // Current layout configuration (1-6)
    currentLayout: 1,
    
    // Current theme mode
    isDarkMode: false,
    
    // Available AI types - use window.state if available, otherwise use static definition
    aiTypes: typeof window !== 'undefined' && window.state && window.state.aiTypes && 
             window.state.aiTypes.length > 0 ? window.state.aiTypes : aiTypes
};

// Log available AI types for debugging
console.log('config.js - state.aiTypes initialized:', JSON.stringify(state.aiTypes, null, 2));
