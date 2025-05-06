/**
 * Message handling module for simulating AI responses
 */

/**
 * Simulate an AI response to a user message
 * @param {HTMLElement} panel - The panel element to add the message to
 * @param {string} message - The user message text
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
    setTimeout(() => {
        aiMsg.querySelector('.message-content').innerHTML = `This is a simulated response to: "${message}"`;
    }, config.animations.responseDelay);
}

/**
 * Setup the send-to-all-panels functionality
 */
function setupSendAllMessages() {
    document.getElementById('send-all-btn').onclick = () => {
        const message = prompt('Enter message to send to all panels:');
        if (message && message.trim()) {
            document.querySelectorAll('.ai-panel').forEach(panel => {
                simulateResponse(panel, message);
            });
        }
    };
}
