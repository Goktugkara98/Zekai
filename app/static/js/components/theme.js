/**
 * Theme management module for handling light/dark mode
 */

/**
 * Initialize theme based on user preference
 */
function initTheme() {
    const savedTheme = localStorage.getItem('aiPlatformTheme');
    if (savedTheme === 'dark') {
        enableDarkMode();
    }
}

/**
 * Enable dark mode
 */
function enableDarkMode() {
    document.body.classList.add('dark-mode');
    elements.themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
    state.isDarkMode = true;
    localStorage.setItem('aiPlatformTheme', 'dark');
}

/**
 * Disable dark mode
 */
function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    elements.themeToggle.innerHTML = '<i class="bi bi-moon"></i>';
    state.isDarkMode = false;
    localStorage.setItem('aiPlatformTheme', 'light');
}

/**
 * Toggle between light and dark mode
 */
function toggleTheme() {
    if (state.isDarkMode) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

/**
 * Setup theme toggle button event listener
 */
function setupThemeToggle() {
    elements.themeToggle.addEventListener('click', toggleTheme);
}
