/**
 * Chat Component Module
 * Manages AI chat windows, layouts, and interactions
 */

// --- LOGGING SYSTEM ---
window.DEBUG_LOG = true; // Set to false to silence logs
const LOG_LEVELS = ['debug', 'info', 'action', 'warn', 'error'];
function log(level, msg, ...args) {
    if (!window.DEBUG_LOG) return;
    if (!LOG_LEVELS.includes(level)) level = 'info';
    const ts = new Date().toISOString().substr(11, 8);
    const colorMap = {
        debug: 'color:#888',
        info: 'color:#2196F3',
        action: 'color:#4CAF50',
        warn: 'color:#FFC107',
        error: 'color:#F44336',
    };
    const style = colorMap[level] || '';
    console.log(`%c[${ts}] [${level.toUpperCase()}] ${msg}`, style, ...args);
}

/**
 * ChatManager - Handles all chat operations
 */
const ChatManager = (function() {
    // Private state
    const state = {
        chats: [],
        maxChats: 6, // Updated to support up to 6 chats
        aiTypes: [
            { id: 0, name: 'GPT-4 Turbo', icon: 'bi bi-cpu' },
            { id: 1, name: 'Translation AI', icon: 'bi bi-translate' },
            { id: 2, name: 'Image Generator', icon: 'bi bi-brush' }
        ]
    };

    // Initialize state from global state if exists
    if (window.state) {
        window.state.chats = state.chats;
        window.state.aiTypes = state.aiTypes;
    } else {
        window.state = { 
            chats: state.chats,
            aiTypes: state.aiTypes
        };
    }

    // --- DOM ELEMENTS ---
    let elements = {};

    /**
     * Initialize DOM element references
     */
    function initElements() {
        elements = {
            chatContainer: document.getElementById('chat-container'),
            welcomeScreen: document.getElementById('welcome-screen'),
            welcomeNewChatBtn: document.getElementById('welcome-new-chat-btn'),
            newChatBtn: document.getElementById('new-chat-btn'),
            clearChatsBtn: document.getElementById('clear-chats-btn'),
            activeChatsDropdownTrigger: document.getElementById('active-chats-dropdown-trigger'),
            activeChatsDropdownMenu: document.getElementById('active-chats-dropdown-menu'),
            activeChatsList: document.getElementById('active-chats-list')
        };

        if (!elements.chatContainer) {
            log('error', 'Chat container element not found');
            return false;
        }
        
        return true;
    }

    // --- CHAT ELEMENT FACTORIES ---
    /**
     * Create a new chat window element
     * @param {Object} chatData - Chat data object
     * @returns {HTMLElement} - Chat window element
     */
    function createChatElement(chatData) {
        log('debug', 'Creating chat element', chatData);
        
        // Get AI type info
        const aiType = state.aiTypes[chatData.aiType] || { 
            name: `AI ${chatData.aiType}`, 
            icon: 'bi bi-cpu' 
        };
        
        const chatWindow = document.createElement('div');
        chatWindow.className = 'chat-window';
        chatWindow.setAttribute('data-chat-id', chatData.id);
        
        // Determine if model selection should be locked (if there are messages from the user)
        const isModelLocked = chatData.messages && chatData.messages.some(msg => msg.isUser);
        const modelSelectionClass = isModelLocked ? 'model-locked' : 'model-changeable';
        const modelSelectionTitle = isModelLocked ? 'Model locked - conversation already started' : 'Click to change AI model';
        
        // Create chat HTML
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-title ${modelSelectionClass}" title="${modelSelectionTitle}">
                    <i class="${aiType.icon}"></i>
                    <span>${aiType.name}</span>
                    ${!isModelLocked ? '<i class="bi bi-chevron-down model-selector-icon"></i>' : 
                      '<i class="bi bi-lock-fill model-locked-icon"></i>'}
                </div>
                <div class="chat-controls">
                    <button class="chat-control-btn chat-close-btn" title="Close Chat">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
            <div class="chat-messages">
                ${chatData.messages && chatData.messages.length > 0 ? 
                    chatData.messages.map(msg => createMessageHTML(msg)).join('') : 
                    createWelcomeMessageHTML(aiType.name)
                }
            </div>
            <div class="chat-input-container">
                <div class="chat-input-group">
                    <input type="text" class="chat-input" placeholder="Type your message...">
                    <button class="chat-send-btn">
                        <i class="bi bi-send"></i>
                    </button>
                </div>
            </div>
        `;
        
        return chatWindow;
    }

    /**
     * Create HTML for a chat message
     * @param {Object} message - Message data object
     * @param {boolean} isFirstAIMessage - Whether this is the first AI message in the conversation
     * @param {string} aiName - Name of the AI model (only used for first AI message)
     * @returns {string} - Message HTML
     */
    function createMessageHTML(message, isFirstAIMessage = false, aiName = '') {
        const messageClass = message.isUser ? 'user-message' : 'ai-message';
        const timestamp = new Date(message.timestamp || Date.now()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // For the first AI message, include the model name
        let messageContent = message.text;
        if (!message.isUser && isFirstAIMessage && aiName) {
            messageContent = `<div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>${messageContent}`;
        }
        
        return `
            <div class="message ${messageClass}">
                <div class="message-content">
                    ${messageContent}
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
    }

    /**
     * Create HTML for the welcome message
     * @param {string} aiName - Name of the AI
     * @returns {string} - Welcome message HTML
     */
    function createWelcomeMessageHTML(aiName) {
        return `
            <div class="message ai-message">
                <div class="message-content">
                    <div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>
                    <p>Hello! I'm ${aiName}. How can I assist you today?</p>
                </div>
                <div class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
            </div>
        `;
    }

    // --- RENDER FUNCTIONS ---
    /**
     * Render all chat windows
     */
    function renderChats() {
        log('debug', 'Rendering chats. Current state:', JSON.parse(JSON.stringify(state.chats)));
        
        if (!elements.chatContainer) {
            log('error', 'Cannot render chats: chat container not found');
            return;
        }
        
        // Clear container
        elements.chatContainer.innerHTML = '';
        
        // Show welcome screen if no chats
        if (state.chats.length === 0) {
            elements.chatContainer.appendChild(elements.welcomeScreen);
            return;
        }
        
        // Hide welcome screen
        if (elements.welcomeScreen.parentNode) {
            elements.welcomeScreen.parentNode.removeChild(elements.welcomeScreen);
        }
        
        // Determine layout based on number of chats
        let layoutClass;
        switch (state.chats.length) {
            case 1:
                layoutClass = 'layout-1'; // 1 chat: full width
                break;
            case 2:
                layoutClass = 'layout-2'; // 2 chats: split left/right
                break;
            case 3:
                layoutClass = 'layout-3'; // 3 chats: top half split into 2, bottom is full width
                break;
            case 4:
                layoutClass = 'layout-4'; // 4 chats: equal 2x2 grid
                break;
            case 5:
                layoutClass = 'layout-5'; // 5 chats: top row has 3, bottom row has 2
                break;
            case 6:
                layoutClass = 'layout-6'; // 6 chats: equal 3x2 grid
                break;
            default:
                layoutClass = 'layout-6'; // For more than 6 chats (though we limit to maxChats)
                break;
        }
        
        // Add layout class to container
        elements.chatContainer.className = `flex-grow-1 d-flex flex-wrap ${layoutClass}`;
        
        // Render each chat
        state.chats.forEach(chatData => {
            const chatElement = createChatElement(chatData);
            elements.chatContainer.appendChild(chatElement);
            setupChatControls(chatElement);
        });
        renderActiveChatsDropdown(); // Renamed
    }

    // Layout is now determined automatically based on number of chats

    // --- ACTIVE CHATS DROPDOWN ---
    /**
     * Render the active chats dropdown
     */
    function renderActiveChatsDropdown() {
        if (!elements.activeChatsList || !elements.activeChatsDropdownMenu || !elements.activeChatsDropdownTrigger) {
            log('warn', 'Active chats dropdown elements not found');
            return;
        }

        elements.activeChatsList.innerHTML = ''; // Clear current list

        if (state.chats.length === 0) {
            elements.activeChatsDropdownTrigger.classList.add('disabled');
            elements.activeChatsDropdownMenu.classList.remove('show'); // Ensure menu is collapsed via Bootstrap
            const noChatsLi = document.createElement('li');
            noChatsLi.className = 'list-group-item text-muted';
            noChatsLi.textContent = 'No active chats';
            noChatsLi.style.paddingLeft = '1rem';
            elements.activeChatsList.appendChild(noChatsLi);
            // Also update the chevron if it's managed by aria-expanded
            elements.activeChatsDropdownTrigger.setAttribute('aria-expanded', 'false');
            return;
        }
        
        elements.activeChatsDropdownTrigger.classList.remove('disabled');

        state.chats.forEach(chatData => {
            const aiType = state.aiTypes[chatData.aiType] || { name: `AI ${chatData.aiType}`, icon: 'bi bi-cpu' };
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex align-items-center justify-content-between';
            listItem.setAttribute('data-chat-id', chatData.id);
            listItem.style.paddingLeft = '1rem';
            listItem.style.paddingRight = '1rem';

            if (chatData.messages && chatData.messages.length > 0) {
                listItem.classList.add('active-chat-item--started');
            } else {
                const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                if (chatWindow) {
                    listItem.classList.add('active-chat-item--rendered-inactive');
                }
            }

            listItem.innerHTML = `
                <span class="d-flex align-items-center">
                    <i class="${aiType.icon} me-2"></i>
                    <span>${aiType.name}</span>
                </span>
            `;
            // TODO: Add click listener to focus/switch to this chat window
            elements.activeChatsList.appendChild(listItem);
        });
    }

    // --- EVENT HANDLERS ---
    /**
     * Set up event handlers for a chat window
     * @param {HTMLElement} chatElement - Chat window element
     */
    function setupChatControls(chatElement) {
        if (!chatElement) {
            log('error', 'Cannot setup chat controls: chat element is null');
            return;
        }
        
        const chatId = chatElement.getAttribute('data-chat-id');
        
        // Close button
        const closeBtn = chatElement.querySelector('.chat-close-btn');
        if (closeBtn) {
            closeBtn.onclick = (e) => {
                e.stopPropagation();
                log('action', 'Close chat button clicked', chatId);
                removeChat(chatId);
            };
        }
        
        // Model selection via chat title
        const chatTitle = chatElement.querySelector('.chat-title');
        if (chatTitle && chatTitle.classList.contains('model-changeable')) {
            chatTitle.onclick = (e) => {
                e.stopPropagation();
                log('action', 'Chat title clicked for model selection', chatId);
                showModelDropdown(chatId, chatTitle);
            };
        }
        
        // Send button
        const sendBtn = chatElement.querySelector('.chat-send-btn');
        const inputField = chatElement.querySelector('.chat-input');
        
        if (sendBtn && inputField) {
            sendBtn.onclick = () => {
                if (inputField.value.trim()) {
                    log('action', 'Send button clicked', chatId);
                    sendMessage(chatId, inputField.value);
                    inputField.value = '';
                }
            };
            
            inputField.onkeypress = (e) => {
                if (e.key === 'Enter' && inputField.value.trim()) {
                    log('action', 'Enter key pressed in chat input', chatId);
                    sendMessage(chatId, inputField.value);
                    inputField.value = '';
                }
            };
        }
    }

    /**
     * Set up global event handlers
     */
    function setupGlobalHandlers() {
        if (!elements.welcomeNewChatBtn || !elements.newChatBtn || !elements.clearChatsBtn) {
            log('warn', 'Some control elements not found');
            return;
        }
        
        // Welcome screen new chat button
        elements.welcomeNewChatBtn.onclick = () => {
            log('action', 'Welcome screen new chat button clicked');
            addChat();
        };
        
        // Control bar new chat button
        elements.newChatBtn.onclick = () => {
            log('action', 'New chat button clicked');
            addChat();
        };
        
        // Clear all chats button
        elements.clearChatsBtn.onclick = () => {
            log('action', 'Clear all chats button clicked');
            clearAllChats();
        };
    }

    // --- CHAT ACTIONS ---
    /**
     * Add a new chat
     * @param {number} aiType - AI type index
     * @returns {string} - New chat ID
     */
    function addChat(aiType = 0) {
        log('action', 'Adding new chat', aiType);
        
        if (state.chats.length >= state.maxChats) {
            log('warn', 'Maximum number of chats reached');
            alert(`Maximum of ${state.maxChats} chats allowed. Please close one first.`);
            return null;
        }
        
        const chatId = `chat-${Date.now()}`;
        state.chats.push({
            id: chatId,
            aiType: aiType,
            messages: [],
            createdAt: Date.now(),
            lastActivity: Date.now()
        });
        
        renderChats();
        renderActiveChatsDropdown(); // Renamed

        // Automatically open the active chats dropdown
        const dropdownMenu = elements.activeChatsDropdownMenu;
        if (dropdownMenu && !dropdownMenu.classList.contains('show')) {
            const dropdownInstance = new bootstrap.Collapse(dropdownMenu);
            dropdownInstance.show();
        }

        return chatId;
    }

    /**
     * Remove a chat
     * @param {string} chatId - Chat ID to remove
     */
    function removeChat(chatId) {
        log('action', 'Removing chat', chatId);
        
        const index = state.chats.findIndex(chat => chat.id === chatId);
        if (index !== -1) {
            state.chats.splice(index, 1);
            renderChats();
            renderActiveChatsDropdown(); // Renamed
        }
    }

    /**
     * Clear all chats
     */
    function clearAllChats() {
        log('action', 'Clearing all chats');
        
        if (state.chats.length === 0) return;
        
        if (confirm('Are you sure you want to clear all chats?')) {
            state.chats = [];
            renderChats();
            renderActiveChatsDropdown(); // Renamed
        }
    }

    /**
     * Send a message in a chat
     * @param {string} chatId - Chat ID
     * @param {string} text - Message text
     */
    function sendMessage(chatId, text) {
        log('action', 'Sending message', chatId, text);
        
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) return;
        
        // Add user message
        const userMessage = {
            isUser: true,
            text: text,
            timestamp: Date.now()
        };
        chat.messages.push(userMessage);
        chat.lastActivity = Date.now();
        
        // Get AI type info for the response
        const aiType = state.aiTypes[chat.aiType] || { name: `AI ${chat.aiType}`, icon: 'bi bi-cpu' };
        
        // Check if this is the first message in the chat
        const isFirstMessage = chat.messages.length === 1; // We just added the user message, so length is 1
        
        // Update chat window with new message
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer) {
                const messageElement = document.createElement('div');
                messageElement.innerHTML = createMessageHTML(userMessage);
                messagesContainer.appendChild(messageElement.firstElementChild);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // Update chat title to show locked state if this is the first message
                if (isFirstMessage) {
                    const chatTitle = chatElement.querySelector('.chat-title');
                    if (chatTitle) {
                        chatTitle.classList.remove('model-changeable');
                        chatTitle.classList.add('model-locked');
                        chatTitle.title = 'Model locked - conversation already started';
                        
                        // Replace chevron with lock icon
                        const selectorIcon = chatTitle.querySelector('.model-selector-icon');
                        if (selectorIcon) {
                            const lockIcon = document.createElement('i');
                            lockIcon.className = 'bi bi-lock-fill model-locked-icon';
                            chatTitle.replaceChild(lockIcon, selectorIcon);
                        }
                        
                        // Remove click handler
                        chatTitle.onclick = null;
                    }
                }
            }
        }
        
        // Simulate AI response (replace with actual API call)
        setTimeout(() => {
            const aiResponse = getAIResponse(text, chat.aiType);
            const aiMessage = {
                isUser: false,
                text: aiResponse,
                timestamp: Date.now()
            };
            chat.messages.push(aiMessage);
            chat.lastActivity = Date.now();
            
            // Update chat window with AI response
            if (chatElement) {
                const messagesContainer = chatElement.querySelector('.chat-messages');
                if (messagesContainer) {
                    const messageElement = document.createElement('div');
                    // Pass isFirstAIMessage=true for the first AI response
                    messageElement.innerHTML = createMessageHTML(aiMessage, isFirstMessage, aiType.name);
                    messagesContainer.appendChild(messageElement.firstElementChild);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }
            renderActiveChatsDropdown(); // Renamed
        }, 1000);
    }

    /**
     * Get a simulated AI response
     * @param {string} userMessage - User message
     * @param {number} aiType - AI type index
     * @returns {string} - AI response
     */
    function getAIResponse(userMessage, aiType) {
        // This is a placeholder. In a real app, you would call your AI API here.
        const responses = {
            0: [ // GPT-4 Turbo
                "I understand what you're asking. Let me think about that...",
                "That's an interesting question. Here's what I know about it...",
                "Based on my knowledge, I can tell you that...",
                "I'd be happy to help with that. Here's some information..."
            ],
            1: [ // Translation AI
                "Here's the translation you requested...",
                "I've translated that for you. The result is...",
                "In the target language, that would be..."
            ],
            2: [ // Image Generator
                "I've created an image based on your description. [Image would appear here]",
                "Here's a visual representation of what you described. [Image would appear here]",
                "I've generated this image for you. [Image would appear here]"
            ]
        };
        
        const aiResponses = responses[aiType] || responses[0];
        return aiResponses[Math.floor(Math.random() * aiResponses.length)];
    }

    /**
     * Show the model selection dropdown
     * @param {string} chatId - Chat ID
     * @param {HTMLElement} titleElement - The chat title element that was clicked
     */
    function showModelDropdown(chatId, titleElement) {
        log('action', 'Showing model dropdown', chatId);
        
        // Remove any existing dropdowns
        document.querySelectorAll('.model-dropdown').forEach(dropdown => {
            dropdown.parentNode.removeChild(dropdown);
        });
        
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) return;
        
        // Create dropdown element
        const dropdown = document.createElement('div');
        dropdown.className = 'model-dropdown';
        
        // Create options for each AI type
        const options = state.aiTypes.map((type, index) => {
            const isSelected = index === chat.aiType;
            return `
                <div class="model-option ${isSelected ? 'selected' : ''}" data-type="${index}">
                    <i class="${type.icon}"></i>
                    <span>${type.name}</span>
                    ${isSelected ? '<i class="bi bi-check-lg ms-auto"></i>' : ''}
                </div>
            `;
        }).join('');
        
        dropdown.innerHTML = options;
        
        // Add dropdown to the DOM
        elements.chatContainer.appendChild(dropdown); // Append to chatContainer

        // Position the dropdown absolutely relative to the titleElement
        const titleRect = titleElement.getBoundingClientRect();
        const containerRect = elements.chatContainer.getBoundingClientRect();

        dropdown.style.position = 'absolute'; // Ensure position is absolute
        dropdown.style.top = `${titleRect.bottom - containerRect.top + elements.chatContainer.scrollTop}px`;
        dropdown.style.left = `${titleRect.left - containerRect.left + elements.chatContainer.scrollLeft}px`;
        // width and z-index are handled by CSS
        
        // Show dropdown with animation
        setTimeout(() => {
            dropdown.classList.add('show');
        }, 10);
        
        // Add click handlers to options
        dropdown.querySelectorAll('.model-option').forEach(option => {
            option.onclick = (e) => {
                e.stopPropagation();
                const typeIndex = parseInt(option.getAttribute('data-type'));
                changeAIModel(chatId, typeIndex);
                dropdown.classList.remove('show');
                setTimeout(() => {
                    if (dropdown.parentNode) {
                        dropdown.parentNode.removeChild(dropdown);
                    }
                }, 300);
            };
        });
        
        // Close dropdown when clicking outside
        const closeDropdown = (e) => {
            if (!dropdown.contains(e.target) && e.target !== titleElement) {
                dropdown.classList.remove('show');
                setTimeout(() => {
                    if (dropdown.parentNode) {
                        dropdown.parentNode.removeChild(dropdown);
                    }
                }, 300);
                document.removeEventListener('click', closeDropdown);
            }
        };
        
        document.addEventListener('click', closeDropdown);
    }
    
    /**
     * Change the AI model for a chat
     * @param {string} chatId - Chat ID
     * @param {number} newTypeIndex - Index of the new AI type
     */
    function changeAIModel(chatId, newTypeIndex) {
        log('action', 'Changing AI model', chatId, newTypeIndex);
        
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) return;
        
        // Check if chat has messages (model should be locked)
        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('warn', 'Cannot change model: chat already has messages', chatId);
            alert('Cannot change AI model: conversation has already started.');
            return;
        }
        
        // Validate new type index
        if (isNaN(newTypeIndex) || newTypeIndex < 0 || newTypeIndex >= state.aiTypes.length) {
            log('error', 'Invalid AI type index', newTypeIndex);
            return;
        }
        
        // Update the chat's AI type
        chat.aiType = newTypeIndex;
        
        // Re-render the chat window
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            const aiType = state.aiTypes[chat.aiType];
            
            // Update chat title
            const chatTitle = chatElement.querySelector('.chat-title');
            if (chatTitle) {
                const iconElement = chatTitle.querySelector('i:first-child');
                const nameElement = chatTitle.querySelector('span');
                
                if (iconElement) iconElement.className = aiType.icon;
                if (nameElement) nameElement.textContent = aiType.name;
            }
            
            // Update welcome message if no messages yet
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer && (!chat.messages || chat.messages.length === 0)) {
                messagesContainer.innerHTML = createWelcomeMessageHTML(aiType.name);
            }
        } else {
            // If chat element not found, re-render all chats
            renderChats();
        }
        renderActiveChatsDropdown(); // Added to update dropdown after model change
    }

    // Layout is now automatically determined based on number of chats

    /**
     * Initialize the chat manager
     */
    function init() {
        log('info', 'Initializing ChatManager');
        
        if (!initElements()) {
            log('error', 'Failed to initialize ChatManager: required elements not found');
            return;
        }
        
        setupGlobalHandlers();
        renderChats();
        
        log('info', 'ChatManager initialized successfully');
    }

    // --- PUBLIC API ---
    return {
        init,
        addChat,
        removeChat,
        clearAllChats,
        sendMessage,
        changeAIModel
    };
})();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add chat.css to the document if not already included
    if (!document.querySelector('link[href*="chat.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/components/chat.css';
        document.head.appendChild(link);
    }
    
    // Initialize ChatManager
    ChatManager.init();
});
