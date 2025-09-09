// Chat Interface JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat interface
    initializeChat();
    initializeLayoutControls();
    initializeInputHandling();
    initializeSidebar();
});

// Initialize chat functionality
function initializeChat() {
    const messageInput = document.querySelector('.message-input');
    
    // Auto-resize textarea
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
}

// Initialize layout controls
function initializeLayoutControls() {
    // Layout controls are now just visual - no functionality
    // They represent different pane layouts but don't change anything for now
}

// Initialize input handling
function initializeInputHandling() {
    const messageInput = document.querySelector('.message-input');
    const attachmentBtn = document.querySelector('.attachment-btn');
    const promptsBtn = document.querySelector('.prompts-btn');
    
    // File attachment handling
    if (attachmentBtn) {
        attachmentBtn.addEventListener('click', function() {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*,video/*,audio/*,.pdf,.doc,.docx,.txt';
            fileInput.multiple = true;
            
            fileInput.addEventListener('change', function(e) {
                const files = Array.from(e.target.files);
                handleFileUpload(files);
            });
            
            fileInput.click();
        });
    }
    
    // Prompts button
    if (promptsBtn) {
        promptsBtn.addEventListener('click', function() {
            showPromptsModal();
        });
    }
    
    function handleFileUpload(files) {
        files.forEach(file => {
            console.log('File uploaded:', file.name, file.type, file.size);
            // Here you would typically upload the file to your server
            // For now, we'll just show a notification
            showNotification(`File "${file.name}" uploaded successfully!`);
        });
    }
    
    function showPromptsModal() {
        // Create prompts modal
        const modal = document.createElement('div');
        modal.className = 'prompts-modal';
        modal.innerHTML = `
            <div class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Prompts</h3>
                        <button class="close-btn">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="prompt-categories">
                            <div class="prompt-category">
                                <h4>Creative Writing</h4>
                                <div class="prompt-item" data-prompt="Write a short story about...">Write a short story about...</div>
                                <div class="prompt-item" data-prompt="Create a poem about...">Create a poem about...</div>
                            </div>
                            <div class="prompt-category">
                                <h4>Business</h4>
                                <div class="prompt-item" data-prompt="Write a business plan for...">Write a business plan for...</div>
                                <div class="prompt-item" data-prompt="Create a marketing strategy for...">Create a marketing strategy for...</div>
                            </div>
                            <div class="prompt-category">
                                <h4>Technical</h4>
                                <div class="prompt-item" data-prompt="Explain how to...">Explain how to...</div>
                                <div class="prompt-item" data-prompt="Write code for...">Write code for...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('.close-btn').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                modal.remove();
            }
        });
        
        // Prompt selection
        modal.querySelectorAll('.prompt-item').forEach(item => {
            item.addEventListener('click', function() {
                const prompt = this.dataset.prompt;
                const messageInput = document.querySelector('.message-input');
                if (messageInput) {
                    messageInput.value = prompt;
                    messageInput.focus();
                }
                modal.remove();
            });
        });
    }
}

// Initialize sidebar
function initializeSidebar() {
    const modelItems = document.querySelectorAll('.model-item');
    const chatPanesContainer = document.querySelector('.chat-panes-container');
    
    // Initialize collapse functionality
    initializeCollapse();
    
    // Model selection
    modelItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            modelItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get model info
            const modelName = this.querySelector('span').textContent;
            const modelIcon = this.querySelector('.model-icon').innerHTML;
            
            // Create chat pane
            createChatPane(modelName, modelIcon);
        });
    });
    
    function createChatPane(modelName, modelIcon) {
        // Clear existing content
        chatPanesContainer.innerHTML = '';
        
        // Create new chat pane
        const chatPane = document.createElement('div');
        chatPane.className = 'chat-pane';
        chatPane.innerHTML = `
            <div class="pane-header">
                <div class="pane-controls">
                    <button class="control-btn">
                        <i class="fas fa-expand-arrows-alt"></i>
                    </button>
                    <button class="control-btn">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <button class="control-btn">
                        <i class="fas fa-globe"></i>
                    </button>
                </div>
                <div class="pane-title">
                    <span>${modelName}</span>
                    <i class="fas fa-chevron-down"></i>
                    <i class="fas fa-globe"></i>
                </div>
                <div class="pane-controls">
                    <button class="control-btn">
                        <i class="fas fa-expand-arrows-alt"></i>
                    </button>
                    <button class="control-btn">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                </div>
            </div>
            <div class="pane-content">
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-comments"></i>
                    </div>
                    <p>Start a conversation with ${modelName}</p>
                </div>
            </div>
        `;
        
        chatPanesContainer.appendChild(chatPane);
        
        // Update chat functionality for the new pane
        initializeChatForPane(chatPane);
    }
    
    function initializeChatForPane(pane) {
        const messageInput = document.querySelector('.message-input');
        const sendBtn = document.querySelector('.send-btn');
        const paneContent = pane.querySelector('.pane-content');
        
        // Send message functionality
        if (sendBtn) {
            sendBtn.onclick = function() {
                sendMessageToPane(pane);
            };
        }
        
        // Enter key to send message
        if (messageInput) {
            messageInput.onkeydown = function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessageToPane(pane);
                }
            };
        }
        
        function sendMessageToPane(targetPane) {
            const messageInput = document.querySelector('.message-input');
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessageToPane(targetPane, message, true);
            
            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';
            
            // Simulate AI response
            simulateAIResponseToPane(targetPane);
        }
        
        function addMessageToPane(pane, message, isUser = false) {
            const paneContent = pane.querySelector('.pane-content');
            const emptyState = paneContent.querySelector('.empty-state');
            
            // Remove empty state if it exists
            if (emptyState) {
                emptyState.remove();
            }
            
            // Create message element
            const messageElement = document.createElement('div');
            messageElement.className = `message ${isUser ? 'user' : 'assistant'} fade-in`;
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.textContent = message;
            
            const messageTime = document.createElement('div');
            messageTime.className = 'message-time';
            messageTime.textContent = new Date().toLocaleTimeString('tr-TR', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            messageElement.appendChild(messageContent);
            messageElement.appendChild(messageTime);
            paneContent.appendChild(messageElement);
            
            // Scroll to bottom
            paneContent.scrollTop = paneContent.scrollHeight;
        }
        
        function simulateAIResponseToPane(pane) {
            const responses = [
                "Bu çok ilginç bir soru! Size nasıl yardımcı olabilirim?",
                "Anladım. Bu konuda size daha detaylı bilgi verebilirim.",
                "Harika bir nokta! Bu konuyu daha derinlemesine inceleyelim.",
                "Evet, bu konuda size yardımcı olabilirim. Hangi açıdan bakmak istersiniz?",
                "Bu sorunuzu yanıtlamak için biraz daha bilgiye ihtiyacım var."
            ];
            
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            
            // Add typing indicator
            const paneContent = pane.querySelector('.pane-content');
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message assistant typing-indicator';
            typingIndicator.innerHTML = `
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            paneContent.appendChild(typingIndicator);
            paneContent.scrollTop = paneContent.scrollHeight;
            
            // Remove typing indicator and add response after delay
            setTimeout(() => {
                const typingIndicator = pane.querySelector('.typing-indicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
                addMessageToPane(pane, randomResponse, false);
            }, 2000);
        }
    }
}

// Initialize collapse functionality
function initializeCollapse() {
    const sectionHeaders = document.querySelectorAll('.section-header');
    
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const content = document.getElementById(targetId);
            const icon = this.querySelector('.collapse-icon');
            
            // Toggle active class
            this.classList.toggle('active');
            
            // Toggle content visibility
            if (content.classList.contains('open')) {
                content.classList.remove('open');
                content.style.maxHeight = '0';
            } else {
                content.classList.add('open');
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
}

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Add CSS for modal
const style = document.createElement('style');
style.textContent = `
    .prompts-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 2000;
    }
    
    .modal-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .modal-content {
        background: white;
        border-radius: 12px;
        max-width: 600px;
        width: 100%;
        max-height: 80vh;
        overflow: hidden;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    .modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .modal-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #111827;
    }
    
    .close-btn {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6b7280;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
    }
    
    .close-btn:hover {
        background: #f3f4f6;
        color: #374151;
    }
    
    .modal-body {
        padding: 20px;
        max-height: 60vh;
        overflow-y: auto;
    }
    
    .prompt-categories {
        display: flex;
        flex-direction: column;
        gap: 24px;
    }
    
    .prompt-category h4 {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 600;
        color: #374151;
    }
    
    .prompt-item {
        padding: 12px 16px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 8px;
        font-size: 14px;
        color: #374151;
    }
    
    .prompt-item:hover {
        background: #f3f4f6;
        border-color: #d1d5db;
    }
    
    .model-item.active {
        background: #3b82f6;
        color: white;
    }
    
    .model-item.active .model-icon {
        background: rgba(255, 255, 255, 0.2);
    }
`;
document.head.appendChild(style);
