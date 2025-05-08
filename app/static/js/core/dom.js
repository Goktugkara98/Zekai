/**
 * ZekAI DOM Utilities Module
 * ========================
 * @description DOM element references and manipulation utilities
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. DOM Element References
 *    1.1 Static Elements
 *    1.2 Dynamic Element Getters
 * 
 * 2. DOM Manipulation
 *    2.1 Element Creation
 *    2.2 Style Management
 */

//=============================================================================
// 1. DOM ELEMENT REFERENCES
//=============================================================================

/**
 * 1.1 Static Elements & 1.2 Dynamic Element Getters
 * ----------------------------------------------
 * Cached DOM elements for better performance
 */

const elements = {
    /**
     * Main container elements
     */
    panelArea: document.getElementById('panel-area'),
    welcomeMsg: document.getElementById('welcome-message'),
    themeToggle: document.getElementById('theme-toggle'),
    
    /**
     * Action buttons
     */
    addPanelBtn: document.getElementById('add-panel-btn'),
    removePanelBtn: document.getElementById('remove-panel-btn'),
    welcomeAddBtn: document.getElementById('welcome-add-btn'),
    sendAllBtn: document.getElementById('send-all-btn'),
    addAiBtn: document.getElementById('add-ai-btn'),
    settingsBtn: document.getElementById('settings-btn'),
    helpBtn: document.getElementById('help-btn'),
    
    /**
     * Layout controls
     * @returns {NodeList} Collection of layout button elements
     */
    getLayoutBtns: () => document.querySelectorAll('.layout-btn'),
    
    /**
     * Panel-related elements (dynamic)
     * These methods return live NodeLists that automatically update
     */
    getPanelMinimizeButtons: () => document.querySelectorAll('.btn-panel-minimize'),
    getPanelMaximizeButtons: () => document.querySelectorAll('.btn-panel-maximize'),
    getPanelCloseButtons: () => document.querySelectorAll('.btn-panel-close'),
    getSendButtons: () => document.querySelectorAll('.btn-send'),
    getPanelInputs: () => document.querySelectorAll('.panel-input'),
    getAllPanels: () => document.querySelectorAll('.ai-panel'),
    getAIModelSelects: () => document.querySelectorAll('.ai-model-select')
};

//=============================================================================
// 2. DOM MANIPULATION
//=============================================================================

/**
 * 2.1 Element Creation
 * -----------------
 */

/**
 * Creates a DOM element with specified attributes and content
 * 
 * @param {string} tag - HTML tag name to create
 * @param {object} attrs - Attributes to set on the element (key-value pairs)
 * @param {string|Node} content - Content to append (string for innerHTML or DOM node)
 * @returns {HTMLElement} The created DOM element
 * @example
 * // Create a button with a class and text content
 * const button = createElement('button', { className: 'btn btn-primary', id: 'submit-btn' }, 'Submit');
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
 * 2.2 Style Management
 * -----------------
 */

/**
 * Creates a style element with the provided CSS content and adds it to document head
 * 
 * @param {string} cssContent - CSS rules to add to the document
 * @returns {HTMLStyleElement} The created style element
 * @example
 * // Add custom CSS rules
 * createStyleElement('.custom-panel { border: 1px solid blue; }');
 */
function createStyleElement(cssContent) {
    const style = document.createElement('style');
    style.textContent = cssContent;
    document.head.appendChild(style);
}
