/**
 * ZekAI Message Handling Module
 * ===========================
 * @description Handles message creation, simulation, and AI responses
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Message Operations
 *    1.1 Response Simulation
 *    1.2 Broadcast Messages
 * 
 * 2. Utility Functions
 *    2.1 Element Creation
 * 
 * 3. Configuration
 *    3.1 Animation Settings
 */

//=============================================================================
// 1. MESSAGE OPERATIONS
//=============================================================================

/**
 * 1.1 Response Simulation
 * ---------------------
 */

/**
 * Simulates an AI response to a user message with typing animation
 * 
 * @param {HTMLElement} panel - The panel element to add the message to
 * @param {string} message - The user message text to respond to
 * @returns {void}
 */
function simulateResponse(panel, message) {
    const contentArea = panel.querySelector('.panel-content');
    
    // Create user message
    const userMsg = createElement('div', {
        className: 'message user-message',
        innerHTML: `<div class="message-content">${message}</div>`
    });
    
    contentArea.innerHTML = '';
    contentArea.appendChild(userMsg);
    
    // Simulate AI thinking
    const aiMsg = createElement('div', {
        className: 'message ai-message',
        innerHTML: `
            <div class="message-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `
    });
    
    contentArea.appendChild(aiMsg);
    
    // After delay, show AI response
    // Generate a more realistic response based on the message content
    const responses = [
        `I understand your message about "${message.substring(0, 20)}${message.length > 20 ? '...' : ''}". How can I assist further?`,
        `Thank you for sharing that. Based on "${message.substring(0, 15)}${message.length > 15 ? '...' : ''}", I would suggest...`,
        `I've analyzed your input: "${message.substring(0, 20)}${message.length > 20 ? '...' : ''}". Here's what I think...`
    ];
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    
    // After delay, show AI response with typing effect
    setTimeout(() => {
        aiMsg.querySelector('.message-content').innerHTML = randomResponse;
    }, config.animations.responseDelay);
}

/**
 * 1.2 Broadcast Messages
 * -------------------
 */

/**
 * Sets up the broadcast functionality to send messages to all panels
 * Attaches click handler to the send-all button
 * 
 * @returns {void}
 */
function setupSendAllMessages() {
    const sendAllBtn = document.getElementById('send-all-btn');
    
    if (!sendAllBtn) {
        console.warn('Send-all button not found in the DOM');
        return;
    }
    
    sendAllBtn.onclick = () => {
        // Get message from user with improved prompt
        const message = prompt('Enter a message to broadcast to all AI panels:');
        
        // Validate message
        if (message && message.trim()) {
            // Count active panels
            const panels = document.querySelectorAll('.ai-panel');
            const panelCount = panels.length;
            
            if (panelCount === 0) {
                alert('No active AI panels found to send messages to.');
                return;
            }
            
            console.log(`Broadcasting message to ${panelCount} panels: "${message}"`);
            
            // Send to all panels
            panels.forEach(panel => {
                simulateResponse(panel, message);
            });
        }
    };
}

//=============================================================================
// 2. UTILITY FUNCTIONS
//=============================================================================

/**
 * 2.1 Element Creation
 * -----------------
 */

/**
 * Creates a DOM element with specified attributes
 * 
 * @param {string} tag - HTML tag name
 * @param {Object} attributes - Key-value pairs of attributes to set
 * @returns {HTMLElement} The created element
 */
function createElement(tag, attributes = {}) {
    const element = document.createElement(tag);
    
    Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'innerHTML') {
            element.innerHTML = value;
        } else {
            element.setAttribute(key, value);
        }
    });
    
    return element;
}

//=============================================================================
// 3. CONFIGURATION
//=============================================================================

/**
 * 3.1 Animation Settings
 * -------------------
 */

/**
 * Configuration settings for animations and timing
 */
const config = {
    animations: {
        responseDelay: 1500, // Milliseconds to wait before showing AI response
        typingSpeed: 50      // Milliseconds per character for typing effect
    }
};

// Initialize message functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    setupSendAllMessages();
});
