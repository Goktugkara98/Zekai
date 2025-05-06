/**
 * Responsive design utilities
 */

/**
 * Create mobile menu toggle button for small screens
 */
function createMobileMenuToggle() {
    const toggleBtn = createElement('button', {
        className: 'btn btn-icon mobile-menu-toggle',
        innerHTML: '<i class="bi bi-list"></i>',
        title: 'Toggle Menu'
    });
    
    document.body.appendChild(toggleBtn);
    
    toggleBtn.onclick = () => {
        document.getElementById('sidebar').classList.toggle('show');
    };
}

/**
 * Check screen size and initialize mobile features if needed
 */
function initResponsiveFeatures() {
    // Create mobile menu toggle for small screens
    if (window.innerWidth < 768) {
        createMobileMenuToggle();
    }
    
    // Add window resize listener to handle responsive changes
    window.addEventListener('resize', handleWindowResize);
}

/**
 * Handle window resize events
 */
function handleWindowResize() {
    const isMobile = window.innerWidth < 768;
    const toggleExists = document.querySelector('.mobile-menu-toggle');
    
    if (isMobile && !toggleExists) {
        createMobileMenuToggle();
    } else if (!isMobile && toggleExists) {
        toggleExists.remove();
    }
}
