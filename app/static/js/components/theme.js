/**
 * ZekAI Theme Management Module
 * ===========================
 * @description Handles theme preferences, light/dark mode switching
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Theme Management
 *    1.1 Initialization
 *    1.2 Mode Switching
 *    1.3 Event Handlers
 */

//=============================================================================
// 1. THEME MANAGEMENT
//=============================================================================

/**
 * 1.1 Initialization
 * ----------------
 */

/**
 * Initializes theme based on user's saved preference
 * Checks localStorage for previously saved theme setting
 * 
 * @returns {void}
 */
function initTheme() {
    const savedTheme = localStorage.getItem('aiPlatformTheme');
    if (savedTheme === 'dark') {
        enableDarkMode();
    }
}

/**
 * 1.2 Mode Switching
 * ---------------
 */

/**
 * Enables dark mode theme
 * Updates DOM, state, and saves preference to localStorage
 * 
 * @returns {void}
 */
function enableDarkMode() {
    document.body.classList.add('dark-mode');
    elements.themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
    state.isDarkMode = true;
    localStorage.setItem('aiPlatformTheme', 'dark');
}

/**
 * Disables dark mode (switches to light mode)
 * Updates DOM, state, and saves preference to localStorage
 * 
 * @returns {void}
 */
function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    elements.themeToggle.innerHTML = '<i class="bi bi-moon"></i>';
    state.isDarkMode = false;
    localStorage.setItem('aiPlatformTheme', 'light');
}

/**
 * Toggles between light and dark mode
 * Calls the appropriate function based on current state
 * 
 * @returns {void}
 */
function toggleTheme() {
    if (state.isDarkMode) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

/**
 * 1.3 Event Handlers
 * ---------------
 */

/**
 * Sets up event listener for the theme toggle button
 * Attaches click handler to toggle between themes
 * 
 * @returns {void}
 */
function setupThemeToggle() {
    elements.themeToggle.addEventListener('click', toggleTheme);
}
