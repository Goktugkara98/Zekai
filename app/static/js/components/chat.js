/**
 * ZekAI Chat Component Module
 * ===========================
 * @description Manages AI chat windows, layouts, and user interactions
 * @version 1.0.0
 * @author ZekAI Team
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Core System
 *    1.1 Logging System
 *    1.2 State Management
 *    1.3 DOM Elements
 *    1.4 Initialization
 * 
 * 2. UI Components
 *    2.1 Chat Element Factories
 *    2.2 Message HTML Generators
 * 
 * 3. Rendering Functions
 *    3.1 Chat Windows
 *    3.2 Active Chats Dropdown
 *    3.3 Chat History
 * 
 * 4. Event Handlers
 *    4.1 Chat Controls
 *    4.2 Global Handlers
 * 
 * 5. Chat Operations
 *    5.1 Chat Management (Add/Remove/Clear)
 *    5.2 Messaging System
 *    5.3 Broadcast Messages
 * 
 * 6. AI Model Management
 *    6.1 Response Generation
 *    6.2 Model Selection
 * 
 * 7. Public API
 *    7.1 Exposed Methods
 *    7.2 DOM Ready Handlers
 */

//=============================================================================
// 1. CORE SYSTEM
//=============================================================================

/**
 * 1.1 Logging System
 * ------------------
 * Provides debug, info, action, warn, and error level logging
 */
window.DEBUG_LOG = true; // Set to false to silence logs
const LOG_LEVELS = ['debug', 'info', 'action', 'warn', 'error'];

/**
 * Logs a message with timestamp and color-coding based on level
 * @param {string} level - Log level (debug|info|action|warn|error)
 * @param {string} msg - Message to log
 * @param {...any} args - Additional arguments to log
 */
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
 * ChatManager - Main module that handles all chat operations
 * @namespace ChatManager
 */
const ChatManager = (function() {
    /**
     * 1.2 State Management
     * ------------------
     * Private state for managing chats, history, and configuration
     */
    const state = {
        chats: [],         // Active chat windows
        chatHistory: [],   // Closed chats with messages
        maxChats: 6        // Maximum number of concurrent chat windows
    };

    // Initialize global state or use existing
    if (window.state) {
        if (!window.state.chats) window.state.chats = state.chats;
        if (!window.state.chatHistory) window.state.chatHistory = state.chatHistory;
        if (!window.state.aiTypes) window.state.aiTypes = [];
    } else {
        window.state = { 
            chats: state.chats,
            chatHistory: state.chatHistory,
            aiTypes: [] // Will be populated by index.html
        };
    }

    /**
     * 1.3 DOM Elements
     * ---------------
     * References to important DOM elements
     */
    let elements = {};

    /**
     * Initializes all required DOM element references
     * @returns {boolean} True if all critical elements found, false otherwise
     */
    function initElements() {
        elements = {
            // Main container
            chatContainer: document.getElementById('chat-container'),
            welcomeScreen: document.getElementById('welcome-screen'),
            
            // Control buttons
            welcomeNewChatBtn: document.getElementById('welcome-new-chat-btn'),
            newChatBtn: document.getElementById('new-chat-btn'),
            clearChatsBtn: document.getElementById('clear-chats-btn'),
            
            // Active chats dropdown
            activeChatsDropdownTrigger: document.getElementById('active-chats-dropdown-trigger'),
            activeChatsDropdownMenu: document.getElementById('active-chats-dropdown-menu'),
            activeChatsList: document.getElementById('active-chats-list'),
            
            // Broadcast functionality
            broadcastMessageInput: document.getElementById('broadcast-message-input'),
            sendBroadcastBtn: document.getElementById('send-broadcast-btn'),
            
            // Chat history
            chatHistoryTrigger: document.getElementById('chat-history-trigger'),
            chatHistoryMenu: document.getElementById('chat-history-menu'),
            chatHistoryList: document.getElementById('chat-history-list'),
        };

        if (!elements.chatContainer) {
            log('error', 'Chat container element not found');
            return false;
        }
        
        return true;
    }

    //=============================================================================
    // 2. UI COMPONENTS
    //=============================================================================

    /**
     * 2.1 Chat Element Factories
     * -------------------------
     */
    
    /**
     * Creates a new chat window DOM element
     * @param {Object} chatData - Chat data object with id, aiModelId, messages
     * @returns {HTMLElement} Complete chat window element ready to be added to DOM
     */
    function createChatElement(chatData) {
        log('debug', 'Creating chat element', chatData);
        
        // Get AI type info using model ID
        const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) || 
                        (window.state.aiTypes && window.state.aiTypes.length > 0 ? window.state.aiTypes[0] : null) || // Fallback to first model
                        { name: `Unknown AI (ID: ${chatData.aiModelId})`, icon: 'bi bi-question-circle' }; // Ultimate fallback
        
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
                    <i class="${aiModel.icon}"></i>
                    <span>${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
                    ${!isModelLocked ? '<i class="bi bi-chevron-down model-selector-icon"></i>' : 
                      '<i class="bi bi-lock-fill model-locked-icon"></i>'}
                </div>
                <div class="chat-controls">
                    <button class="chat-control-btn chat-minimize-btn" title="Minimize Chat">
                        <i class="bi bi-dash-lg"></i>
                    </button>
                    <button class="chat-control-btn chat-close-btn" title="Close Chat">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
            <div class="chat-messages">
                ${chatData.messages && chatData.messages.length > 0 ? 
                    chatData.messages.map(msg => createMessageHTML(msg)).join('') : 
                    createWelcomeMessageHTML(aiModel.name)
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
     * 2.2 Message HTML Generators
     * -------------------------
     */
    
    /**
     * Creates HTML markup for a single chat message
     * @param {Object} message - Message data with isUser, text, timestamp properties
     * @param {boolean} isFirstAIMessage - Whether this is the first AI message in the conversation
     * @param {string} aiName - Name of the AI model (only used for first AI message)
     * @returns {string} HTML markup for the message
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
     * Creates HTML markup for the welcome message shown when a chat is first opened
     * @param {string} aiName - Name of the AI model
     * @returns {string} HTML markup for the welcome message
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

    //=============================================================================
    // 3. RENDERING FUNCTIONS
    //=============================================================================

    /**
     * 3.1 Chat Windows
     * --------------
     */
    
    /**
     * Renders all active chat windows and manages layout based on count
     * Handles welcome screen visibility and chat window arrangement
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
        const activeChats = state.chats.filter(chat => !chat.isMinimized);

        // Show welcome screen if no active (non-minimized) chats
        if (activeChats.length === 0 && state.chats.length > 0) { // All chats are minimized
            // Optionally, show a message indicating all chats are minimized
            // For now, just show the welcome screen as if there are no chats.
            // Or, if you want a different screen, create and append it here.
            elements.chatContainer.appendChild(elements.welcomeScreen);
            // Update layout class to default or remove specific layout classes
            elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap'; 
            return;
        } else if (state.chats.length === 0) { // No chats at all
            elements.chatContainer.appendChild(elements.welcomeScreen);
            elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap'; 
            return;
        }

        switch (activeChats.length) {
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
        activeChats.forEach(chatData => {
            const chatElement = createChatElement(chatData);
            elements.chatContainer.appendChild(chatElement);
            setupChatControls(chatElement);
        });
        renderActiveChatsDropdown(); // Renamed
    }

    /**
     * 3.2 Active Chats Dropdown
     * ----------------------
     */
    
    /**
     * Renders the active chats dropdown in the sidebar
     * Shows all active chats with options to highlight or restore minimized chats
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
            const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) || { name: `AI (${chatData.aiModelId ? chatData.aiModelId.slice(-4) : 'Unknown'})`, icon: 'bi bi-cpu' };
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

            let chatNameHTML = `
                <span class="d-flex align-items-center">
                    <i class="${aiModel.icon} me-2"></i>
                    <span>${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
                </span>`;

            if (chatData.isMinimized) {
                listItem.classList.add('active-chat-item--minimized');
                listItem.innerHTML = chatNameHTML + '<span class="ms-auto"><i class="bi bi-window-plus" title="Restore Chat"></i></span>';
                listItem.onclick = (e) => {
                    e.stopPropagation(); 
                    const chatToRestore = state.chats.find(c => c.id === chatData.id);
                    if (chatToRestore) {
                        chatToRestore.isMinimized = false;
                        renderChats();
                        renderActiveChatsDropdown();
                    }
                };
            } else {
                listItem.innerHTML = chatNameHTML;
                listItem.onclick = () => {
                    log('action', `Active chat item clicked: ${chatData.id}. Highlighting chat window.`);
                    
                    // Highlight the chat window
                    const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                    if (chatWindow) {
                        chatWindow.classList.add('chat-window--highlighted');
                        setTimeout(() => {
                            chatWindow.classList.remove('chat-window--highlighted');
                        }, 2000); // Highlight for 2 seconds
                    }
                    
                    // Do not close the dropdown
                    // const dropdownInstance = bootstrap.Collapse.getInstance(elements.activeChatsDropdownMenu);
                    // if (dropdownInstance) {
                    //     dropdownInstance.hide();
                    // }
                };
            }

            elements.activeChatsList.appendChild(listItem);
        });
    }

    /**
     * 3.3 Chat History
     * -------------
     */
    
    /**
     * Renders the chat history list in the sidebar
     * Shows closed chats that can be restored or viewed
     */
    function renderChatHistory() {
        if (!elements.chatHistoryList || !elements.chatHistoryTrigger || !elements.chatHistoryMenu) {
            log('warn', 'Chat history elements not found in DOM.');
            return;
        }

        elements.chatHistoryList.innerHTML = ''; // Clear current list

        if (state.chatHistory.length === 0) {
            elements.chatHistoryTrigger.classList.add('disabled');
            elements.chatHistoryMenu.classList.remove('show'); 
            const noHistoryLi = document.createElement('li');
            noHistoryLi.className = 'list-group-item text-muted';
            noHistoryLi.textContent = 'No chat history';
            noHistoryLi.style.paddingLeft = '1rem';
            elements.chatHistoryList.appendChild(noHistoryLi);
            elements.chatHistoryTrigger.setAttribute('aria-expanded', 'false');
            return;
        }

        elements.chatHistoryTrigger.classList.remove('disabled');

        state.chatHistory.forEach(chat => {
            const aiType = state.aiTypes.find(ai => ai.id === chat.aiType) || { name: 'Unknown AI', icon: 'bi bi-archive' };
            const listItem = document.createElement('li');
            // Aktif sohbetlerle aynı temel sınıfı kullan, gerekirse ek özel sınıflar eklenebilir
            listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex justify-content-between align-items-center';
            listItem.setAttribute('data-chat-id', chat.id);
            listItem.style.paddingLeft = '1rem'; // Aktif sohbetlerdeki gibi padding
            listItem.style.paddingRight = '1rem'; // Aktif sohbetlerdeki gibi padding

            // İsim ve simge için aktif sohbetlerdeki gibi bir container span
            const nameContainerSpan = document.createElement('span');
            nameContainerSpan.className = 'd-flex align-items-center';
            // Uzun isimlerin butonu itmesini engellemek için stil
            nameContainerSpan.style.overflow = 'hidden';
            nameContainerSpan.style.textOverflow = 'ellipsis';
            nameContainerSpan.style.whiteSpace = 'nowrap';
            nameContainerSpan.style.flexGrow = '1'; // Alanı doldurması için
            nameContainerSpan.style.marginRight = '0.5rem'; // Butondan önce boşluk

            const iconElement = document.createElement('i');
            iconElement.className = `${aiType.icon} me-2`;
            
            const nameSpanElement = document.createElement('span');
            let historyItemText = aiType.name;
            if (chat.closedTimestamp) {
                const date = new Date(chat.closedTimestamp);
                // Tarihi daha kısa formatta göster: GG/AA/YY
                const dateString = date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: '2-digit' });
                historyItemText += ` (${dateString})`;
            }
            nameSpanElement.textContent = historyItemText;
            nameSpanElement.title = historyItemText; // Tam metin için tooltip

            nameContainerSpan.appendChild(iconElement);
            nameContainerSpan.appendChild(nameSpanElement);
            
            listItem.appendChild(nameContainerSpan);

            // Geri yükleme butonu (sağda kalacak)
            const restoreButton = document.createElement('button');
            restoreButton.className = 'btn btn-sm btn-icon chat-history-restore-btn flex-shrink-0'; 
            restoreButton.title = 'Restore Chat';
            restoreButton.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i>';
            restoreButton.onclick = function(event) {
                event.stopPropagation();
                log('action', 'Restore chat from history clicked (not implemented yet)', chat.id);
                alert('Restoring chat from history is not yet implemented.');
                // TODO: Implement restoreChatFromHistory(chat.id);
            };
            listItem.appendChild(restoreButton);

            // Geçmiş öğesine tıklandığında (işlevsellik daha sonra eklenecek)
            listItem.onclick = function() {
                log('action', 'Chat history item clicked', chat.id);
                alert(`Displaying history for chat ${chat.id} is not yet implemented. Messages: ${JSON.stringify(chat.messages)}`);
                // TODO: Implement logic to display chat history messages
            };

            elements.chatHistoryList.appendChild(listItem);
        });
    }

    //=============================================================================
    // 4. EVENT HANDLERS
    //=============================================================================

    /**
     * 4.1 Chat Controls
     * --------------
     */
    
    /**
     * Sets up event handlers for buttons and inputs in a chat window
     * Handles close, minimize, model selection, and message sending
     * @param {HTMLElement} chatElement - Chat window DOM element
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
                const chatData = state.chats.find(c => c.id === chatId);

                if (chatData && chatData.messages && chatData.messages.length > 0) {
                    // Sohbet aktif, mesajları var, onay iste
                    if (confirm("Bu sohbeti kapatmak istediğinizden emin misiniz?")) {
                        removeChat(chatId);
                    }
                } else {
                    // Sohbet aktif değil veya hiç mesaj yok, direkt kapat
                    removeChat(chatId);
                }
            };
        }

        // Minimize button (Updated version)
        const minimizeBtn = chatElement.querySelector('.chat-minimize-btn');
        if (minimizeBtn) {
            minimizeBtn.onclick = (e) => {
                e.stopPropagation();
                log('action', 'Minimize chat button clicked', chatId);
                const chat = state.chats.find(c => c.id === chatId);
                if (chat) {
                    chat.isMinimized = true;
                    renderChats();
                    renderActiveChatsDropdown();
                }
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
     * 4.2 Global Handlers
     * ----------------
     */
    
    /**
     * Sets up global event handlers for buttons and controls
     * Handles new chat, clear chats, and broadcast message functionality
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
            const chatsToRemovePreview = state.chats.filter(chat => !chat.messages || !chat.messages.some(msg => msg.isUser));
            
            if (chatsToRemovePreview.length > 0) {
                if (confirm(`Are you sure you want to close ${chatsToRemovePreview.length} unused chat(s)? Chats with ongoing conversations will not be affected.`)) {
                    clearAllChats(); 
                }
            } else {
                alert('There are no unused chats to clear. All active chats have ongoing conversations or there are no chats.');
            }
        };

        // Broadcast Message Handlers
        if (elements.sendBroadcastBtn && elements.broadcastMessageInput) {
            elements.sendBroadcastBtn.addEventListener('click', () => {
                log('action', 'Send broadcast button clicked');
                sendBroadcastMessage();
            });

            elements.broadcastMessageInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    log('action', 'Enter key pressed in broadcast input');
                    sendBroadcastMessage();
                }
            });
        }
    }


    //=============================================================================
    // 5. CHAT OPERATIONS
    //=============================================================================

    /**
     * 5.1 Chat Management
     * ----------------
     */
    
    /**
     * Creates and adds a new chat window
     * @param {string} [aiModelId] - Optional AI model ID to use (defaults to first available)
     * @returns {string|null} New chat ID if successful, null if failed
     */
    function addChat(aiModelId) {
        log('action', 'Attempting to add new chat. Requested AI Model ID:', aiModelId);

        if (!elements.chatContainer) {
            log('error', 'Chat container not found. Cannot add chat.');
            ModalManager.showAlert('Error: Chat container not found.');
            return null;
        }

        if (state.chats.length >= state.maxChats) {
            log('warn', `Max chats reached (${state.maxChats}). Cannot add new chat.`);
            ModalManager.showAlert(`Maximum of ${state.maxChats} chat panels reached. Please close one first.`);
            return null;
        }

        // Determine the AI model ID to use
        let finalAiModelId = aiModelId;
        if (!finalAiModelId) {
            if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                finalAiModelId = window.state.aiTypes[0].id; // Default to the ID of the first AI in the list
                log('info', 'No AI Model ID provided, defaulting to first in list:', finalAiModelId);
            } else {
                log('error', 'addChat: No AI Model ID provided and no default AI available from window.state.aiTypes.');
                ModalManager.showAlert('Cannot create chat: No AI models available or AI models not loaded yet.');
                return null; // Cannot create chat without an AI model
            }
        } else {
            // Verify the provided aiModelId exists
            const modelExists = window.state.aiTypes.some(m => m.id === finalAiModelId);
            if (!modelExists) {
                log('warn', `addChat: Provided AI Model ID "${finalAiModelId}" does not exist in window.state.aiTypes. Defaulting to first AI.`);
                if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                    finalAiModelId = window.state.aiTypes[0].id;
                } else {
                    log('error', 'addChat: Provided AI Model ID was invalid and no fallback AI available.');
                    ModalManager.showAlert('Cannot create chat: Specified AI model is invalid and no fallback available.');
                    return null;
                }
            }
        }
        
        const newChat = {
            id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            aiModelId: finalAiModelId, // Use the resolved string ID
            messages: [],
            createdAt: Date.now(),
            lastActivity: Date.now(),
            isMinimized: false,
            inputHistory: [], // For up/down arrow message recall
            historyIndex: -1   // For up/down arrow message recall
        };

        state.chats.push(newChat);
        log('info', 'New chat added:', JSON.parse(JSON.stringify(newChat)));
        
        renderChats(); // This function should call createChatElement internally
        updateWelcomeScreen(); // To hide it if this is the first chat
        renderActiveChatsDropdown(); // To update the list of active chats
        // saveChatsToHistory(); // Usually only save if there's interaction or on close

        // Focus the input of the new chat if it's visible
        const newChatElement = elements.chatContainer.querySelector(`[data-chat-id="${newChat.id}"]`);
        if (newChatElement) {
            const inputField = newChatElement.querySelector('.chat-input');
            if (inputField) {
                // Ensure panel is not minimized or hidden before focusing
                if (newChatElement.offsetParent !== null) { // Basic check for visibility
                   inputField.focus();
                }
            }
        }
        return newChat.id;
    }

    /**
     * Removes a chat window with animation
     * If chat has user messages, it's moved to history before removal
     * @param {string} chatId - ID of chat to remove
     */
    function removeChat(chatId) {
        log('action', 'Attempting to remove chat', chatId);
        // data-chat-id özelliğini kullanarak doğru pencereyi seç
        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);

        if (chatWindow) {
            chatWindow.classList.add('closing'); // Kapanış animasyonunu başlat

            // Animasyonun bitmesini dinle
            // Define the handler function to be able to remove it specifically
            const handleAnimationEnd = () => {
                // Olay dinleyicisini kaldır ki birden fazla kez tetiklenmesin
                // chatWindow.removeEventListener('animationend', handleAnimationEnd); // {once: true} handles this

                // Animasyon bittikten sonra state güncellemesi ve DOM'dan tam kaldırma
                const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
                if (chatIndex !== -1) {
                    const chatToRemove = state.chats[chatIndex];
                    const hasUserMessages = chatToRemove.messages && chatToRemove.messages.some(msg => msg.isUser);

                    if (hasUserMessages) {
                        log('info', `Chat ${chatId} has user messages. Moving to history.`);
                        chatToRemove.closedTimestamp = Date.now(); 
                        // Ensure chatHistory is initialized
                        if (!Array.isArray(state.chatHistory)) {
                            state.chatHistory = [];
                        }
                        state.chatHistory.unshift(chatToRemove); 
                    } else {
                        log('info', `Chat ${chatId} has no user messages. Removing without adding to history.`);
                    }
                    state.chats.splice(chatIndex, 1);

                    if (chatWindow.parentNode) {
                        chatWindow.parentNode.removeChild(chatWindow);
                    }
                    
                    renderChats(); // Kalan pencerelerin düzenini güncelle
                    renderActiveChatsDropdown();
                    if (typeof renderChatHistory === 'function') {
                        renderChatHistory(); 
                    }
                } else {
                    log('warn', `Chat ${chatId} not found in active chats for state removal after animation.`);
                    if (chatWindow.parentNode) {
                        chatWindow.parentNode.removeChild(chatWindow);
                    }
                }
            };

            chatWindow.addEventListener('animationend', handleAnimationEnd, { once: true });

            // Güvenlik önlemi: Eğer animationend olayı bir sebepten tetiklenmezse
            setTimeout(() => {
                if (chatWindow.parentNode && chatWindow.classList.contains('closing')) {
                    log('warn', `Animationend for ${chatId} timed out. Forcing removal.`);
                    // chatWindow.removeEventListener('animationend', handleAnimationEnd); // Not strictly needed if already fired due to {once: true}
                    
                    const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
                    if (chatIndex !== -1) {
                         state.chats.splice(chatIndex, 1); 
                    }
                    chatWindow.parentNode.removeChild(chatWindow);
                    renderChats(); 
                    renderActiveChatsDropdown();
                    if (typeof renderChatHistory === 'function') {
                        renderChatHistory();
                    }
                }
            }, 700); // Animasyon süresinden biraz daha uzun (CSS: 0.35s -> 350ms)

        } else {
            log('warn', `Chat window element for ${chatId} not found for closing animation. Removing directly.`);
            const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
            if (chatIndex !== -1) {
                const chatToRemove = state.chats[chatIndex];
                const hasUserMessages = chatToRemove.messages && chatToRemove.messages.some(msg => msg.isUser);
                if (hasUserMessages) {
                    chatToRemove.closedTimestamp = Date.now();
                    if (!Array.isArray(state.chatHistory)) { state.chatHistory = []; }
                    state.chatHistory.unshift(chatToRemove);
                }
                state.chats.splice(chatIndex, 1);
                renderChats();
                renderActiveChatsDropdown();
                if (typeof renderChatHistory === 'function') {
                    renderChatHistory();
                }
            }
        }
    }

    /**
     * Clears all unused chats (chats with no user messages)
     * Called after user confirmation from the UI
     */
    function clearAllChats() {
        log('action', 'Clearing unused chats');

        const initialChatCount = state.chats.length;
        if (initialChatCount === 0) {
            log('info', 'No chats to clear.');
            return; // Erken çıkış, onclick içinde zaten kontrol ediliyor ama yine de iyi bir pratik.
        }

        // Kullanıcı mesajı olan sohbetleri koru, olmayanları filtrele (kaldır)
        state.chats = state.chats.filter(chat => {
            const hasUserMessage = chat.messages && chat.messages.some(msg => msg.isUser);
            return hasUserMessage; // Kullanıcı mesajı olanları tutar
        });

        const chatsRemovedCount = initialChatCount - state.chats.length;

        if (chatsRemovedCount > 0) {
            log('info', `${chatsRemovedCount} unused chat(s) removed.`);
            renderChats();
            renderActiveChatsDropdown();
        } else {
            log('info', 'No unused chats were found to remove (all chats have conversations).');
            // Kullanıcıya zaten onclick içinde bir alert gösteriliyor, bu yüzden burada ek bir alert'e gerek yok.
        }
    }


    /**
     * 5.2 Messaging System
     * -----------------
     */
    
    /**
     * Sends a user message to a specific chat, communicates with the backend for AI response,
     * updates UI, and locks model selection after the first user message.
     * @param {string} chatId - Target chat ID
     * @param {string} text - Message text content
     */
    async function sendMessage(chatId, text) {
        log('action', 'Sending message', chatId, text);

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', `sendMessage: Chat not found for ID ${chatId}`);
            return;
        }

        // 1. Kullanıcı mesajını state'e ve UI'a ekle
        const userMessage = {
            isUser: true,
            text: text,
            timestamp: Date.now()
        };
        chat.messages.push(userMessage);
        chat.lastActivity = Date.now();

        // Kullanıcının ilk mesajı olup olmadığını kontrol et (model kilitleme vb. için)
        // Bu kontrol, kullanıcı mesajı eklendikten sonra yapılmalı.
        const isUsersFirstMessageInChat = chat.messages.filter(m => m.isUser).length === 1;

        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer) {
                const messageElement = document.createElement('div');
                // Kullanıcı mesajı için isFirstAIMessage her zaman false, aiName gereksiz
                messageElement.innerHTML = createMessageHTML(userMessage, false, '');
                messagesContainer.appendChild(messageElement.firstElementChild);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // Eğer bu kullanıcının ilk mesajıysa, model seçimi UI'ını kilitle
                if (isUsersFirstMessageInChat) {
                    const chatTitle = chatElement.querySelector('.chat-title');
                    if (chatTitle) {
                        chatTitle.classList.remove('model-changeable');
                        chatTitle.classList.add('model-locked');
                        chatTitle.title = 'Model locked - conversation already started';
                        const selectorIcon = chatTitle.querySelector('.model-selector-icon');
                        if (selectorIcon) {
                            const lockIcon = document.createElement('i');
                            lockIcon.className = 'bi bi-lock-fill model-locked-icon';
                            chatTitle.replaceChild(lockIcon, selectorIcon);
                        }
                        chatTitle.onclick = null; // Model değiştirme olayını kaldır
                    }
                }
            }
        }

        // 2. AI yanıtı için backend'e istek gönder
        try {
            // Yükleniyor... göstergesi eklenebilir (opsiyonel)
            // Örnek: showLoadingIndicator(chatId);

            // Konuşma geçmişini (yeni mesaj dahil) API formatına dönüştür
            const fullConversationForAPI = chat.messages
                .filter(msg => msg.text && typeof msg.text === 'string' && msg.text.trim() !== '') // Sadece geçerli metin içeren mesajları al
                .map(msg => ({
                    role: msg.isUser ? 'user' : 'model',
                    parts: [{ text: msg.text.trim() }]
                }));

            const response = await fetch('/api/chat/send', { // Backend route'unuzu buraya yazın
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Gerekirse ek başlıklar (örn: CSRF token, Authorization)
                },
                body: JSON.stringify({
                    chatId: chatId,
                    message: text, // En son kullanıcı mesajı (loglama/doğrulama veya Gemini olmayan modeller için ana mesaj olarak kullanılabilir)
                    aiModelId: chat.aiModelId,
                    history: fullConversationForAPI, // Gemini için tam konuşma içeriği
                    // Backend'in ihtiyaç duyabileceği diğer bilgiler (örn: kullanıcı ID'si)
                }),
            });

            // Yükleniyor... göstergesi kaldırılabilir (opsiyonel)
            // Örnek: hideLoadingIndicator(chatId);

            if (!response.ok) {
                let errorText = `Error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorText = errorData.error || errorText;
                } catch (e) {
                    // JSON parse hatası olursa response.text() kullanılabilir
                    errorText = await response.text() || errorText;
                }
                log('error', `Error from1 backend: ${errorText}`);
                throw new Error(errorText); // Hata durumunda catch bloğuna yönlendir
            }

            const data = await response.json();
            const aiResponseText = data.aiResponse; // Backend'in { "aiResponse": "..." } döndürdüğünü varsayalım

            // 3. AI yanıtını state'e ve UI'a ekle
            const aiModelForResponse = window.state.aiTypes.find(m => m.id === chat.aiModelId);
            const currentAiNameForResponse = aiModelForResponse ? aiModelForResponse.name : 'AI';

            // Bu AI yanıtının sohbetteki ilk AI mesajı olup olmadığını kontrol et
            const isFirstAIMessageInChat = chat.messages.filter(m => !m.isUser).length === 0;

            const aiMessage = {
                isUser: false,
                text: aiResponseText,
                timestamp: Date.now()
            };
            chat.messages.push(aiMessage); // State'e AI mesajını ekle
            chat.lastActivity = Date.now();

            if (chatElement) {
                const messagesContainer = chatElement.querySelector('.chat-messages');
                if (messagesContainer) {
                    const messageElement = document.createElement('div');
                    messageElement.innerHTML = createMessageHTML(aiMessage, isFirstAIMessageInChat, currentAiNameForResponse);
                    messagesContainer.appendChild(messageElement.firstElementChild);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }

        } catch (error) {
            log('error', 'Failed to send message or get AI response:', error);
            // Kullanıcıya hata mesajı göster
            const aiErrorMessage = {
                isUser: false,
                text: `Sorry, I couldn\'t get a response. ${error.message || ''}`,
                timestamp: Date.now()
            };
            // Hata mesajını state'e ve UI'a ekle
            chat.messages.push(aiErrorMessage);
            chat.lastActivity = Date.now();
            if (chatElement) {
                const messagesContainer = chatElement.querySelector('.chat-messages');
                if (messagesContainer) {
                    const messageElement = document.createElement('div');
                    // Hata mesajı için AI adı vb. gerekmeyebilir veya genel bir ad kullanılabilir
                    messageElement.innerHTML = createMessageHTML(aiErrorMessage, false, "System");
                    messagesContainer.appendChild(messageElement.firstElementChild);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }
        } finally {
            // Her durumda aktif sohbetler dropdown'ını güncelle
            renderActiveChatsDropdown();
        }
    }

    /**
     * 5.3 Broadcast Messages
     * -------------------
     */
    
    /**
     * Sends the same message to all active (non-minimized) chats
     * Used for broadcasting announcements or instructions
     */
    function sendBroadcastMessage() {
        if (!elements.broadcastMessageInput) {
            log('warn', 'Broadcast message input not found.');
            return;
        }
        const messageText = elements.broadcastMessageInput.value.trim();

        if (messageText === '') {
            log('info', 'Broadcast message is empty, not sending.');
            return;
        }

        log('action', `Attempting to broadcast message: "${messageText}"`);

        const activeChats = state.chats.filter(chat => !chat.isMinimized);

        if (activeChats.length === 0) {
            log('info', 'No active (non-minimized) chats to broadcast to.');
            alert('There are no active chats to send a message to. Create a new chat or restore a minimized one.');
            return;
        }

        activeChats.forEach(chat => {
            log('debug', `Sending broadcast message to chat ID: ${chat.id}`);
            sendMessage(chat.id, messageText); 
        });

        elements.broadcastMessageInput.value = ''; 
        log('info', 'Broadcast message sent and input cleared.');
    }
    //=============================================================================
    // 6. AI MODEL MANAGEMENT
    //=============================================================================

    /**
     * 6.1 Response Generation
     * --------------------
     */
    
    /**
     * Generates a simulated AI response based on user message and AI model
     * @param {string} userMessage - The user's message text
     * @param {string} aiModelId - ID of the AI model to use for response
     * @returns {string} Simulated AI response text
     */
    function getAIResponse(userMessage, aiModelId) {
        log('debug', `getAIResponse called for userMessage: "${userMessage}", aiModelId: "${aiModelId}"`);

        let modelIndex = 0; 
        if (window.state && window.state.aiTypes && Array.isArray(window.state.aiTypes)) {
            const foundIndex = window.state.aiTypes.findIndex(m => m.id === aiModelId);
            if (foundIndex !== -1) {
                modelIndex = foundIndex;
            } else {
                log('warn', `getAIResponse: aiModelId "${aiModelId}" not found in window.state.aiTypes. Defaulting to index 0 for responses.`);
            }
        } else {
            log('warn', `getAIResponse: window.state.aiTypes is not available or not an array. Defaulting to index 0 for responses.`);
        }

        const responses = { 
            0: [ // Example: Corresponds to the first model in window.state.aiTypes
                "I understand what you're asking. Let me ponder that for a moment...",
                "That's a fascinating query! Here is my perspective...",
                "Based on my current information, I would suggest...",
                "Allow me to shed some light on that. Here's what I found..."
            ],
            1: [ // Example: Corresponds to the second model
                "Translation complete: ... (simulated)",
                "I've processed your translation request, and here's the result...",
                "In the specified language, that would be approximately: ..."
            ],
            2: [ // Example: Corresponds to the third model
                "Generating image based on your prompt... [Simulated Image Placeholder]",
                "Here is a visual representation of your words: [Simulated Image Placeholder]",
                "Image created: [Simulated Image Placeholder]"
            ]
            // IMPORTANT: Add more entries here if you have more than 3 AI models in your database,
            // or ensure the fallback logic handles it gracefully.
        };
        
        const aiModelSpecificResponses = responses[modelIndex] || responses[0]; // Fallback to 0 if index is out of bounds
        if (!aiModelSpecificResponses) { 
            log('error', `getAIResponse: No responses found for modelIndex ${modelIndex} or default. Returning generic response.`);
            return "I'm currently unable to provide a specific response for this model.";
        }
        return aiModelSpecificResponses[Math.floor(Math.random() * aiModelSpecificResponses.length)];
    }

    /**
     * 6.2 Model Selection
     * ----------------
     */
    
    /**
     * Shows the AI model selection dropdown for a chat
     * @param {string} chatId - Target chat ID
     * @param {HTMLElement} titleElement - Chat title element to position dropdown near
     */
    function showModelDropdown(chatId, titleElement) {
        log('action', 'Showing model dropdown', chatId);
        
        document.querySelectorAll('.model-dropdown').forEach(dropdown => {
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
        });
        
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', `showModelDropdown: Chat not found for ID: ${chatId}`);
            return;
        }
        if (!window.state || !window.state.aiTypes || window.state.aiTypes.length === 0) {
            log('error', 'showModelDropdown: window.state.aiTypes is not available.');
            ModalManager.showAlert('AI Models not loaded. Cannot change model.');
            return;
        }

        const dropdown = document.createElement('div');
        dropdown.className = 'model-dropdown';
        
        const options = window.state.aiTypes.map(model => {
            const isSelected = model.id === chat.aiModelId;
            return `
                <div class="model-option ${isSelected ? 'selected' : ''}" data-model-id="${model.id}">
                    <i class="${model.icon || 'bi bi-cpu'}"></i>
                    <span>${model.name || 'Unknown Model'}</span>
                    ${isSelected ? '<i class="bi bi-check-lg ms-auto"></i>' : ''}
                </div>
            `;
        }).join('');
        
        dropdown.innerHTML = options;
        elements.chatContainer.appendChild(dropdown);

        const titleRect = titleElement.getBoundingClientRect();
        const containerRect = elements.chatContainer.getBoundingClientRect();

        dropdown.style.position = 'absolute';
        dropdown.style.top = `${titleRect.bottom - containerRect.top + elements.chatContainer.scrollTop}px`;
        dropdown.style.left = `${titleRect.left - containerRect.left + elements.chatContainer.scrollLeft}px`;
        
        setTimeout(() => {
            dropdown.classList.add('show');
        }, 10);
        
        dropdown.querySelectorAll('.model-option').forEach(option => {
            option.onclick = (e) => {
                e.stopPropagation();
                const newModelId = option.getAttribute('data-model-id');
                if (newModelId) {
                    changeAIModel(chatId, newModelId);
                }
                dropdown.classList.remove('show');
                setTimeout(() => {
                    if (dropdown.parentNode) {
                        dropdown.parentNode.removeChild(dropdown);
                    }
                }, 300);
            };
        });
        
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
        
        document.addEventListener('click', closeDropdown, { once: true }); // Use once for cleaner removal
    }

    /**
     * Changes the AI model for a chat (only if no messages yet)
     * Updates UI elements to reflect the new model
     * @param {string} chatId - Target chat ID
     * @param {string} newAiModelId - ID of the new AI model to use
     */
    function changeAIModel(chatId, newAiModelId) {
        log('action', 'Changing AI model for chat:', chatId, 'to new ID:', newAiModelId);
        
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', `changeAIModel: Chat not found for ID: ${chatId}`);
            return;
        }
        
        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('warn', 'Cannot change model: chat already has messages', chatId);
            ModalManager.showAlert('Cannot change AI model: conversation has already started.');
            return;
        }
        
        if (!window.state || !window.state.aiTypes || window.state.aiTypes.length === 0) {
            log('error', 'changeAIModel: window.state.aiTypes is not available.');
            ModalManager.showAlert('AI Models not loaded. Cannot change model.');
            return;
        }

        const newModel = window.state.aiTypes.find(m => m.id === newAiModelId);
        if (!newModel) {
            log('error', 'Invalid new AI Model ID:', newAiModelId);
            ModalManager.showAlert('Invalid AI Model selected.');
            return;
        }
        
        chat.aiModelId = newAiModelId; // Update the chat's AI model ID
        log('info', `Chat ${chatId} AI model ID updated to: ${chat.aiModelId}`);
        
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            // Update chat title
            const chatTitleElement = chatElement.querySelector('.chat-title');
            if (chatTitleElement) {
                const iconElement = chatTitleElement.querySelector('i:first-child');
                const nameElement = chatTitleElement.querySelector('span');
                
                if (iconElement) iconElement.className = newModel.icon || 'bi bi-cpu';
                if (nameElement) nameElement.textContent = `${newModel.name || 'Unknown Model'} (ID: ${chat.id.slice(-4)})`;
            }
            
            // Update welcome message if no messages yet
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer && (!chat.messages || chat.messages.length === 0)) {
                messagesContainer.innerHTML = createWelcomeMessageHTML(newModel.name || 'Selected AI');
            }
            log('debug', 'Chat element updated for new AI model', newModel);
        } else {
            log('warn', `Chat element for ${chatId} not found for UI update after model change. Re-rendering all.`);
            renderChats(); // Fallback if specific element isn't found
        }
        renderActiveChatsDropdown();
        // Consider saving state here if necessary: saveChatsToHistory(); or similar
    }

    //=============================================================================
    // 7. PUBLIC API
    //=============================================================================

    /**
     * 7.1 Exposed Methods
     * ----------------
     */
    
    /**
     * Initializes the chat manager system
     * Sets up DOM elements, event handlers, and renders initial state
     */
    function init() {
        log('info', 'Initializing ChatManager');
        
        if (!initElements()) {
            log('error', 'Failed to initialize ChatManager: required elements not found');
            return;
        }
        
        setupGlobalHandlers();

        // NEW: Add event listeners to AI Model selector items
        const aiModelSelectorItems = document.querySelectorAll('.ai-model-selector-item');
        aiModelSelectorItems.forEach(item => {
            item.addEventListener('click', function(event) {
                event.preventDefault(); 
                const modelId = this.dataset.aiIndex; // Get the string ID
                if (modelId) { // Check if modelId is not null or empty
                    ChatManager.addChat(modelId); // Pass the string ID
                    
                    // Manage 'active' class
                    aiModelSelectorItems.forEach(i => i.classList.remove('active'));
                    this.classList.add('active');
                } else {
                    log('error', 'Invalid AI model ID selected from sidebar.', this.dataset.aiIndex);
                }
            });
        });
        
        renderChats(); 
        renderActiveChatsDropdown();
        renderChatHistory();
        log('info', 'ChatManager initialized successfully');
    }

    // Return public API methods
    return {
        init,              // Initialize the chat system
        addChat,           // Create a new chat window
        removeChat,        // Remove a chat window
        clearAllChats,     // Clear unused chats
        sendMessage,       // Send a message in a chat
        sendBroadcastMessage, // Send to all chats
        changeAIModel      // Change AI model for a chat
    };
})();

/**
 * 7.2 DOM Ready Handlers
 * -------------------
 */
document.addEventListener('DOMContentLoaded', () => {
    
    // Initialize the chat manager
    ChatManager.init();
    
    // Set up welcome screen new chat button
    const welcomeNewChatBtn = document.getElementById('welcome-new-chat-btn');

    // Set up AI category accordion chevron animations
    const aiCategoriesAccordion = document.getElementById('aiCategoriesAccordion');
    if (aiCategoriesAccordion) {
        const collapseElements = aiCategoriesAccordion.querySelectorAll('.collapse');
        collapseElements.forEach(collapseEl => {
            const header = collapseEl.previousElementSibling;
            const chevron = header ? header.querySelector('.category-chevron') : null;

            if (chevron) {
                collapseEl.addEventListener('show.bs.collapse', function () {
                    chevron.classList.remove('bi-chevron-down');
                    chevron.classList.add('bi-chevron-up');
                });

                collapseEl.addEventListener('hide.bs.collapse', function () {
                    chevron.classList.remove('bi-chevron-up');
                    chevron.classList.add('bi-chevron-down');
                });
            }
        });
    }
});
