/**
 * ZekAI Responsive Design Module
 * ===========================
 * @description Utilities for handling responsive design and mobile adaptations
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Mobile UI Components
 *    1.1 Mobile Menu
 * 
 * 2. Responsive Handlers
 *    2.1 Initialization
 *    2.2 Window Resize
 */

//=============================================================================
// 1. MOBILE UI COMPONENTS
//=============================================================================

/**
 * 1.1 Mobile Menu
 * ------------
 */

/**
 * Creates and attaches a mobile menu toggle button for small screens
 * Adds the button to the document body and sets up click handler
 * 
 * @returns {HTMLElement} The created toggle button element
 */
function createMobileMenuToggle() {
    // Create toggle button with appropriate styling and icon
    const toggleBtn = createElement('button', {
        className: 'btn btn-icon mobile-menu-toggle',
        innerHTML: '<i class="bi bi-list"></i>',
        title: 'Toggle Menu',
        'aria-label': 'Toggle Navigation Menu',
        'data-toggle': 'sidebar'
    });
    
    // Add to document
    document.body.appendChild(toggleBtn);
    
    // Set up click handler to toggle sidebar visibility
    toggleBtn.onclick = () => {
        const sidebar = document.getElementById('sidebar');
        
        if (!sidebar) {
            console.warn('Sidebar element not found in DOM');
            return;
        }
        
        sidebar.classList.toggle('show');
        
        // Update aria attributes for accessibility
        const isExpanded = sidebar.classList.contains('show');
        toggleBtn.setAttribute('aria-expanded', isExpanded.toString());
        
        // Update icon based on state
        toggleBtn.innerHTML = isExpanded ? 
            '<i class="bi bi-x"></i>' : 
            '<i class="bi bi-list"></i>';
    };
    
    console.log('Mobile menu toggle created');
    return toggleBtn;
}

//=============================================================================
// 2. RESPONSIVE HANDLERS
//=============================================================================

/**
 * 2.1 Initialization
 * ---------------
 */

/**
 * Initializes responsive features based on current screen size
 * Sets up event listeners for window resize events
 * 
 * @returns {void}
 */
function initResponsiveFeatures() {
    // Define breakpoint for mobile view
    const MOBILE_BREAKPOINT = 768; // pixels
    
    // Store current viewport state
    window.zekaiViewport = {
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: window.innerWidth < MOBILE_BREAKPOINT
    };
    
    // Create mobile menu toggle if on small screen
    if (window.zekaiViewport.isMobile) {
        createMobileMenuToggle();
    }
    
    // Add window resize listener with debounce for performance
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleWindowResize, 250); // Debounce resize events
    });
    
    console.log(`Responsive features initialized. Current viewport: ${window.innerWidth}px`);
}

/**
 * 2.2 Window Resize
 * --------------
 */

/**
 * Handles window resize events to adapt UI for different screen sizes
 * Adds or removes mobile components as needed
 * 
 * @returns {void}
 */
function handleWindowResize() {
    // Define breakpoint for mobile view
    const MOBILE_BREAKPOINT = 768; // pixels
    
    // Update viewport state
    const isMobile = window.innerWidth < MOBILE_BREAKPOINT;
    const wasAlreadyMobile = window.zekaiViewport?.isMobile;
    
    // Update global viewport object
    window.zekaiViewport = {
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: isMobile
    };
    
    // Check if mobile toggle button exists
    const toggleExists = document.querySelector('.mobile-menu-toggle');
    
    // Add toggle if we're on mobile and it doesn't exist
    if (isMobile && !toggleExists) {
        createMobileMenuToggle();
        console.log('Switched to mobile view');
    } 
    // Remove toggle if we're not on mobile but it exists
    else if (!isMobile && toggleExists) {
        toggleExists.remove();
        
        // Also ensure sidebar is visible when switching to desktop
        const sidebar = document.getElementById('sidebar');
        if (sidebar && !sidebar.classList.contains('show')) {
            sidebar.classList.add('show');
        }
        
        console.log('Switched to desktop view');
    }
    
    // Trigger custom event for other components to respond to viewport changes
    if (isMobile !== wasAlreadyMobile) {
        window.dispatchEvent(new CustomEvent('zekaiViewportChange', {
            detail: window.zekaiViewport
        }));
    }
}
