/**
 * ZekAI Dynamic Styles Module
 * ========================
 * @description Dynamic CSS styles generation and management
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Style Management
 *    1.1 Dynamic CSS Injection
 */

//=============================================================================
// 1. STYLE MANAGEMENT
//=============================================================================

/**
 * 1.1 Dynamic CSS Injection
 * ----------------------
 */

/**
 * Adds dynamic CSS styles to the document head
 * Includes styles for panels, messages, animations, and responsive design
 * 
 * @returns {void}
 */
function addDynamicStyles() {
    // Create CSS for dynamic components and animations
    const dynamicCSS = `
        /**
         * Panel Animations and Transitions
         * ------------------------------
         */
        .ai-panel {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        .ai-panel.panel-visible {
            opacity: 1;
            transform: translateY(0);
        }
        .message {
            display: flex;
            margin-bottom: 1rem;
            padding: 0.5rem;
            border-radius: 0.5rem;
            max-width: 80%;
        }
        .user-message {
            margin-left: auto;
            background-color: var(--primary-light);
            color: white;
        }
        .ai-message {
            margin-right: auto;
            background-color: var(--gray-100);
        }
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.5rem;
        }
        .message-content {
            padding: 0.5rem;
        }
        .typing-indicator {
            display: flex;
            align-items: center;
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            background-color: var(--gray-400);
            display: block;
            margin: 0 2px;
            animation: typing 1s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes typing {
            0% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0); }
        }
        .ai-panel.minimized .panel-body {
            display: none !important;
        }
        .ai-panel.maximized {
            position: fixed;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            width: auto;
            height: auto;
            z-index: 1050;
            max-width: none;
            transform: none !important;
        }
        .mobile-menu-toggle {
            display: none;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1040;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: var(--primary);
            color: white;
            box-shadow: var(--box-shadow-md);
        }
        @media (max-width: 767px) {
            .mobile-menu-toggle {
                display: flex;
            }
        }
        /* Dark mode styles */
        body.dark-mode {
            background-color: var(--gray-900);
            color: var(--gray-100);
        }
        body.dark-mode #sidebar {
            background-color: var(--gray-800);
            border-color: var(--gray-700);
        }
        body.dark-mode .sidebar-header,
        body.dark-mode .sidebar-footer {
            border-color: var(--gray-700);
        }
        body.dark-mode #ai-list .list-group-item {
            color: var(--gray-300);
        }
        body.dark-mode #ai-list .list-group-item:hover:not(.active) {
            background-color: var(--gray-700);
            color: white;
        }
        body.dark-mode main {
            background-color: var(--gray-800);
        }
        body.dark-mode .ai-panel {
            background-color: var(--gray-800);
            border-color: var(--gray-700);
        }
        body.dark-mode .panel-header {
            border-color: var(--gray-700);
        }
        body.dark-mode #control-bar {
            background-color: var(--gray-800);
            border-color: var(--gray-700);
        }
        body.dark-mode .btn-control {
            background-color: var(--gray-700);
            border-color: var(--gray-600);
            color: var(--gray-200);
        }
        body.dark-mode .btn-icon {
            background-color: var(--gray-700);
            color: var(--gray-300);
        }
        body.dark-mode .ai-message {
            background-color: var(--gray-700);
            color: var(--gray-200);
        }
        body.dark-mode .form-control {
            background-color: var(--gray-700);
            border-color: var(--gray-600);
            color: var(--gray-200);
        }
        body.dark-mode .form-control::placeholder {
            color: var(--gray-400);
        }
    `;
    
    createStyleElement(dynamicCSS);
}
