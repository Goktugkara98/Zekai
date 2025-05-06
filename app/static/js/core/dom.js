/**
 * DOM element references and basic DOM manipulation utilities
 */

// Cache DOM elements for better performance
const elements = {
    // Main elements
    panelArea: document.getElementById('panel-area'),
    welcomeMsg: document.getElementById('welcome-message'),
    themeToggle: document.getElementById('theme-toggle'),
    
    // Buttons
    addPanelBtn: document.getElementById('add-panel-btn'),
    removePanelBtn: document.getElementById('remove-panel-btn'),
    welcomeAddBtn: document.getElementById('welcome-add-btn'),
    sendAllBtn: document.getElementById('send-all-btn'),
    addAiBtn: document.getElementById('add-ai-btn'),
    settingsBtn: document.getElementById('settings-btn'),
    helpBtn: document.getElementById('help-btn'),
    
    // Get all layout buttons
    getLayoutBtns: () => document.querySelectorAll('.layout-btn'),
    
    // Panel-related elements (dynamic)
    getPanelMinimizeButtons: () => document.querySelectorAll('.btn-panel-minimize'),
    getPanelMaximizeButtons: () => document.querySelectorAll('.btn-panel-maximize'),
    getPanelCloseButtons: () => document.querySelectorAll('.btn-panel-close'),
    getSendButtons: () => document.querySelectorAll('.btn-send'),
    getPanelInputs: () => document.querySelectorAll('.panel-input'),
    getAllPanels: () => document.querySelectorAll('.ai-panel'),
    getAIModelSelects: () => document.querySelectorAll('.ai-model-select')
};

/**
 * Creates a DOM element with specified attributes and content
 * @param {string} tag - HTML tag name
 * @param {object} attrs - Attributes to set on the element
 * @param {string|Node} content - Content to append (string or DOM node)
 * @returns {HTMLElement} - The created element
 */
function createElement(tag, attrs = {}, content = null) {
    const element = document.createElement(tag);
    
    // Set attributes
    Object.entries(attrs).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'innerHTML') {
            element.innerHTML = value;
        } else {
            element.setAttribute(key, value);
        }
    });
    
    // Add content if provided
    if (content) {
        if (typeof content === 'string') {
            element.innerHTML = content;
        } else {
            element.appendChild(content);
        }
    }
    
    return element;
}

/**
 * Creates a style element with the provided CSS content
 * @param {string} cssContent - CSS rules to add
 */
function createStyleElement(cssContent) {
    const style = document.createElement('style');
    style.textContent = cssContent;
    document.head.appendChild(style);
}
