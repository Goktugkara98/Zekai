/**
 * ZekAI UI Manager Module
 * ======================
 * @description UI render işlemleri ve layout yönetimi
 * @version 1.0.1
 * @author ZekAI Team
 */

const UIManager = (function() {
    'use strict';

    // DOM elementleri cache
    let elements = {};

    /**
     * DOM elementlerini başlatır
     */
    function initializeElements() {
        Logger.info('UIManager', 'Initializing DOM elements...');
        
        elements = {
            chatContainer: document.getElementById('chat-container'),
            welcomeScreen: document.getElementById('welcome-screen'),
            welcomeNewChatBtn: document.getElementById('welcome-new-chat-btn'),
            newChatBtn: document.getElementById('new-chat-btn'),
            clearChatsBtn: document.getElementById('clear-chats-btn'),
            activeChatsDropdownTrigger: document.getElementById('active-chats-dropdown-trigger'),
            activeChatsDropdownMenu: document.getElementById('active-chats-dropdown-menu'),
            activeChatsList: document.getElementById('active-chats-list'),
            broadcastMessageInput: document.getElementById('broadcast-message-input'),
            sendBroadcastBtn: document.getElementById('send-broadcast-btn'),
            chatHistoryTrigger: document.getElementById('chat-history-trigger'),
            chatHistoryMenu: document.getElementById('chat-history-menu'),
            chatHistoryList: document.getElementById('chat-history-list')
        };

        const missingElements = Object.keys(elements).filter(key => !elements[key]);
        if (missingElements.length > 0) {
            Logger.error('UIManager', `Missing DOM elements: ${missingElements.join(', ')}`);
            return false;
        }

        Logger.info('UIManager', 'All DOM elements found successfully');
        return true;
    }

    /**
     * Chat'leri render eder
     */
    function renderChats() {
        const chats = StateManager.getState('chats');
        const activeVisibleChats = chats.filter(chat => !chat.isMinimized);

        Logger.debug('UIManager', `Rendering chats. Active: ${activeVisibleChats.length}, Total: ${chats.length}`);

        if (!elements.chatContainer) {
            Logger.error('UIManager', 'Cannot render chats: chat container not found');
            return;
        }

        try {
            // Mevcut chat pencerelerini takip etmek için bir Set kullan
            const existingChatIds = new Set();
            elements.chatContainer.querySelectorAll('.chat-window').forEach(el => {
                existingChatIds.add(el.getAttribute('data-chat-id'));
            });

            const newChatElements = [];
            activeVisibleChats.forEach(chatData => {
                if (!existingChatIds.has(chatData.id)) {
                    // Yeni chat penceresi oluştur
                    const chatElement = createChatElement(chatData);
                    newChatElements.push(chatElement);
                    elements.chatContainer.appendChild(chatElement);
                    setupChatWindowEvents(chatElement);
                } else {
                    // Mevcut chat penceresini güncelle (içeriği değil, sadece görünürlüğü veya durumu)
                    const existingElement = elements.chatContainer.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                    if (existingElement) {
                        // Layout sınıfını güncelle
                        const currentLayoutClass = existingElement.parentNode.className.match(/layout-\d/);
                        const newLayoutClass = getLayoutClass(activeVisibleChats.length);
                        if (!currentLayoutClass || currentLayoutClass[0] !== newLayoutClass) {
                            elements.chatContainer.className = `flex-grow-1 d-flex flex-wrap ${newLayoutClass}`;
                        }
                        // Eğer minimize durum değiştiyse, bu burada handle edilmez, ChatManager'dan EventBus ile tetiklenir.
                        // Sadece chatData'daki isMinimized durumu değiştiğinde renderChats çağrılır.
                        // Bu durumda, chatElement'in kendisi zaten DOM'da olduğundan, sadece layout güncellenir.
                    }
                }
            });

            // Artık görünür olmayan chat pencerelerini kaldır
            const currentActiveChatIds = new Set(activeVisibleChats.map(chat => chat.id));
            elements.chatContainer.querySelectorAll('.chat-window').forEach(el => {
                const chatId = el.getAttribute('data-chat-id');
                if (!currentActiveChatIds.has(chatId)) {
                    el.remove();
                }
            });

            if (activeVisibleChats.length === 0) {
                showWelcomeScreen();
            } else {
                hideWelcomeScreen();
                // Layout sınıfını güncelle
                elements.chatContainer.className = `flex-grow-1 d-flex flex-wrap ${getLayoutClass(activeVisibleChats.length)}`;
            }

            renderActiveChatsDropdown();
            EventBus.emit('ui:chats:rendered', { count: activeVisibleChats.length });

        } catch (error) {
            Logger.error('UIManager', 'Error rendering chats', error);
            showErrorMessage('Sohbetler yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.');
        }
    }

    /**
     * Chat pencerelerini render eder
     * @param {array} chats - Render edilecek chat'ler
     */
    function renderChatWindows(chats) {
        // Bu fonksiyon artık renderChats içinde entegre edildiği için doğrudan çağrılmayacak.
        // Ancak, mevcut chat pencerelerinin içeriğini güncellemek için kullanılabilir.
        // Şimdilik boş bırakıyorum, çünkü renderChats zaten DOM manipülasyonunu yapıyor.
        // Gelecekte, sadece belirli bir chat'in içeriğini güncellemek için bu fonksiyon geliştirilebilir.
    }

    /**
     * Layout sınıfını belirler
     * @param {number} count - Chat sayısı
     * @returns {string} Layout sınıfı
     */
    function getLayoutClass(count) {
        if (count <= 0) return 'layout-1';
        if (count > 6) return 'layout-6';
        return `layout-${count}`;
    }

    /**
     * Chat elementi oluşturur
     * @param {object} chatData - Chat verisi
     * @returns {HTMLElement} Chat elementi
     */
    function createChatElement(chatData) {
        Logger.debug('UIManager', 'Creating chat element', chatData);

        try {
            const aiTypes = StateManager.getState('aiTypes');
            const aiModel = aiTypes.find(m => m.id === chatData.aiModelId) || {
                name: `Bilinmeyen AI (ID: ${chatData.aiModelId})`,
                icon: 'bi bi-question-circle'
            };

            const chatWindow = document.createElement('div');
            chatWindow.className = 'chat-window';
            chatWindow.setAttribute('data-chat-id', chatData.id);

            const isModelLocked = chatData.messages && chatData.messages.some(msg => msg.isUser);
            const modelSelectionClass = isModelLocked ? 'model-locked' : 'model-changeable';
            const modelSelectionTitle = isModelLocked ? 
                'Model kilitli - konuşma zaten başladı' : 
                'AI modelini değiştirmek için tıklayın';

            chatWindow.innerHTML = `
                <div class="chat-header">
                    <div class="chat-title ${modelSelectionClass}" title="${modelSelectionTitle}">
                        <i class="${aiModel.icon || 'bi bi-cpu'}"></i>
                        <span>${aiModel.name || 'AI Model'} (ID: ${chatData.id.slice(-4)})</span>
                        ${!isModelLocked ? 
                            '<i class="bi bi-chevron-down model-selector-icon"></i>' :
                            '<i class="bi bi-lock-fill model-locked-icon"></i>'
                        }
                    </div>
                    <div class="chat-controls">
                        <button class="chat-control-btn chat-minimize-btn" title="Sohbeti Küçült">
                            <i class="bi bi-dash-lg"></i>
                        </button>
                        <button class="chat-control-btn chat-close-btn" title="Sohbeti Kapat">
                            <i class="bi bi-x"></i>
                        </button>
                    </div>
                </div>
                <div class="chat-messages">
                    ${renderChatMessages(chatData)}
                </div>
                <div class="chat-input-container">
                    <div class="chat-input-group">
                        <input type="text" class="chat-input" placeholder="Mesajınızı yazın...">
                        <button class="chat-send-btn">
                            <i class="bi bi-send"></i>
                        </button>
                    </div>
                </div>
            `;

            Logger.info('UIManager', `Chat element created successfully: ${chatData.id}`);
            return chatWindow;

        } catch (error) {
            Logger.error('UIManager', 'Error creating chat element', error);
            return createErrorChatElement(chatData.id);
        }
    }

    /**
     * Chat mesajlarını render eder
     * @param {object} chatData - Chat verisi
     * @returns {string} Mesajlar HTML'i
     */
    function renderChatMessages(chatData) {
        if (!chatData.messages || chatData.messages.length === 0) {
            const aiTypes = StateManager.getState('aiTypes');
            const aiModel = aiTypes.find(m => m.id === chatData.aiModelId);
            return MessageRenderer.createWelcomeMessageHTML(aiModel ? aiModel.name : 'AI Model');
        }

        const aiTypes = StateManager.getState('aiTypes');
        const aiModel = aiTypes.find(m => m.id === chatData.aiModelId);
        
        return chatData.messages.map((msg, index) => {
            const isFirstAIMessage = !msg.isUser && 
                chatData.messages.filter(m => !m.isUser).indexOf(msg) === 0;
            return MessageRenderer.createMessageHTML(msg, isFirstAIMessage, aiModel ? aiModel.name : 'AI', chatData.aiModelId);
        }).join('');
    }

    /**
     * Hata chat elementi oluşturur
     * @param {string} chatId - Chat ID
     * @returns {HTMLElement} Hata elementi
     */
    function createErrorChatElement(chatId) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-window chat-window-error';
        errorDiv.textContent = 'Sohbet yüklenirken bir hata oluştu.';
        errorDiv.setAttribute('data-chat-id', chatId);
        return errorDiv;
    }

    /**
     * Karşılama ekranını gösterir
     */
    function showWelcomeScreen() {
        if (elements.welcomeScreen && elements.welcomeScreen.parentNode !== elements.chatContainer) {
            elements.chatContainer.appendChild(elements.welcomeScreen);
        }
        elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap justify-content-center align-items-center';
        
        StateManager.setState('ui.welcomeScreenVisible', true);
        Logger.info('UIManager', 'Welcome screen shown');
    }

    /**
     * Karşılama ekranını gizler
     */
    function hideWelcomeScreen() {
        if (elements.welcomeScreen && elements.welcomeScreen.parentNode === elements.chatContainer) {
            elements.chatContainer.removeChild(elements.welcomeScreen);
        }
        
        StateManager.setState('ui.welcomeScreenVisible', false);
        Logger.debug('UIManager', 'Welcome screen hidden');
    }

    /**
     * Hata mesajı gösterir
     * @param {string} message - Hata mesajı
     */
    function showErrorMessage(message) {
        elements.chatContainer.innerHTML = `
            <div class="alert alert-danger m-3">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                ${message}
            </div>
        `;
    }

    /**
     * Aktif chat'ler dropdown'ını render eder
     */
    function renderActiveChatsDropdown() {
        if (!elements.activeChatsList || !elements.activeChatsDropdownTrigger) {
            Logger.warn('UIManager', 'Active chats dropdown elements not found');
            return;
        }

        try {
            const chats = StateManager.getState('chats');
            elements.activeChatsList.innerHTML = '';

            if (chats.length === 0) {
                elements.activeChatsDropdownTrigger.classList.add('disabled');
                const noChatsLi = document.createElement('li');
                noChatsLi.className = 'list-group-item text-muted';
                noChatsLi.textContent = 'Aktif sohbet yok';
                elements.activeChatsList.appendChild(noChatsLi);
                return;
            }

            elements.activeChatsDropdownTrigger.classList.remove('disabled');
            
            chats.forEach(chatData => {
                const listItem = createActiveChatsDropdownItem(chatData);
                elements.activeChatsList.appendChild(listItem);
            });

            Logger.debug('UIManager', `Active chats dropdown rendered with ${chats.length} items`);

        } catch (error) {
            Logger.error('UIManager', 'Error rendering active chats dropdown', error);
            if (elements.activeChatsList) {
                elements.activeChatsList.innerHTML = '<li class="list-group-item text-danger">Liste yüklenemedi.</li>';
            }
        }
    }

    /**
     * Aktif chat dropdown item'ı oluşturur
     * @param {object} chatData - Chat verisi
     * @returns {HTMLElement} Dropdown item elementi
     */
    function createActiveChatsDropdownItem(chatData) {
        const aiTypes = StateManager.getState('aiTypes');
        const aiModel = aiTypes.find(m => m.id === chatData.aiModelId) || {
            name: `AI (${chatData.aiModelId ? String(chatData.aiModelId).slice(-4) : 'Bilinmeyen'})`,
            icon: 'bi bi-cpu'
        };

        const listItem = document.createElement('li');
        listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex align-items-center justify-content-between';
        listItem.setAttribute('data-chat-id', chatData.id);
        listItem.style.cursor = 'pointer';

        if (chatData.messages && chatData.messages.some(msg => msg.isUser)) {
            listItem.classList.add('active-chat-item--started');
        }

        const chatNameHTML = `
            <span class="d-flex align-items-center" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;">
                <i class="${aiModel.icon || 'bi bi-cpu'} me-2"></i>
                <span title="${aiModel.name} (ID: ${chatData.id.slice(-4)})">${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
            </span>
        `;

        if (chatData.isMinimized) {
            listItem.classList.add('active-chat-item--minimized');
            listItem.innerHTML = chatNameHTML + '<span class="ms-auto flex-shrink-0"><i class="bi bi-window-plus" title="Sohbeti Geri Yükle"></i></span>';
            
            listItem.onclick = (e) => {
                e.stopPropagation();
                EventBus.emit('chat:restore:requested', { chatId: chatData.id });
            };
        } else {
            listItem.innerHTML = chatNameHTML;
            
            listItem.onclick = () => {
                EventBus.emit('chat:focus:requested', { chatId: chatData.id });
            };
        }

        return listItem;
    }

    /**
     * Chat geçmişini render eder
     */
    function renderChatHistory() {
        if (!elements.chatHistoryList || !elements.chatHistoryTrigger) {
            Logger.warn('UIManager', 'Chat history elements not found');
            return;
        }

        try {
            const chatHistory = StateManager.getState('chatHistory');
            elements.chatHistoryList.innerHTML = '';

            if (chatHistory.length === 0) {
                elements.chatHistoryTrigger.classList.add('disabled');
                const noHistoryLi = document.createElement('li');
                noHistoryLi.className = 'list-group-item text-muted';
                noHistoryLi.textContent = 'Sohbet geçmişi yok';
                elements.chatHistoryList.appendChild(noHistoryLi);
                return;
            }

            elements.chatHistoryTrigger.classList.remove('disabled');
            
            chatHistory.forEach(chat => {
                const listItem = createChatHistoryItem(chat);
                elements.chatHistoryList.appendChild(listItem);
            });

            Logger.debug('UIManager', `Chat history rendered with ${chatHistory.length} items`);

        } catch (error) {
            Logger.error('UIManager', 'Error rendering chat history', error);
            if (elements.chatHistoryList) {
                elements.chatHistoryList.innerHTML = '<li class="list-group-item text-danger">Geçmiş yüklenemedi.</li>';
            }
        }
    }

    /**
     * Chat geçmişi item'ı oluşturur
     * @param {object} chat - Chat verisi
     * @returns {HTMLElement} Geçmiş item elementi
     */
    function createChatHistoryItem(chat) {
        const aiTypes = StateManager.getState('aiTypes');
        const aiModelInfo = aiTypes.find(ai => ai.id === chat.aiModelId) || {
            name: 'Bilinmeyen AI',
            icon: 'bi bi-archive'
        };

        const listItem = document.createElement('li');
        listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex justify-content-between align-items-center';
        listItem.setAttribute('data-chat-id', chat.id);
        listItem.style.cursor = 'pointer';

        let historyItemText = aiModelInfo.name || 'Geçmiş Sohbet';
        if (chat.closedTimestamp) {
            const date = new Date(chat.closedTimestamp);
            historyItemText += ` (${date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: '2-digit' })})`;
        }

        listItem.innerHTML = `
            <span class="d-flex align-items-center" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;">
                <i class="${aiModelInfo.icon || 'bi bi-archive'} me-2"></i>
                <span title="${historyItemText} (ID: ${chat.id.slice(-4)})">${historyItemText}</span>
            </span>
            <button class="btn btn-sm btn-icon chat-history-restore-btn flex-shrink-0" title="Sohbeti Geri Yükle">
                <i class="bi bi-arrow-counterclockwise"></i>
            </button>
        `;

        // Event listener'ları ekle
        const restoreButton = listItem.querySelector('.chat-history-restore-btn');
        if (restoreButton) {
            restoreButton.onclick = (event) => {
                event.stopPropagation();
                EventBus.emit('chat:history:restore:requested', { chatId: chat.id, chat });
            };
        }

        listItem.onclick = () => {
            EventBus.emit('chat:history:view:requested', { chatId: chat.id, chat });
        };

        return listItem;
    }

    /**
     * Chat penceresi event'lerini ayarlar
     * @param {HTMLElement} chatElement - Chat elementi
     */
    function setupChatWindowEvents(chatElement) {
        const chatId = chatElement.getAttribute('data-chat-id');
        if (!chatId) {
            Logger.error('UIManager', 'Cannot setup chat window events: missing chat ID');
            return;
        }

        try {
            // Close button
            const closeBtn = chatElement.querySelector('.chat-close-btn');
            if (closeBtn) {
                closeBtn.onclick = (e) => {
                    e.stopPropagation();
                    EventBus.emit('chat:close:requested', { chatId });
                };
            }

            // Minimize button
            const minimizeBtn = chatElement.querySelector('.chat-minimize-btn');
            if (minimizeBtn) {
                minimizeBtn.onclick = (e) => {
                    e.stopPropagation();
                    EventBus.emit('chat:minimize:requested', { chatId });
                };
            }

            // Model selector
            const chatTitle = chatElement.querySelector('.chat-title');
            if (chatTitle && chatTitle.classList.contains('model-changeable')) {
                chatTitle.onclick = (e) => {
                    e.stopPropagation();
                    EventBus.emit('chat:model:selector:requested', { chatId, element: chatTitle });
                };
            }

            // Send button and input
            const sendBtn = chatElement.querySelector('.chat-send-btn');
            const inputField = chatElement.querySelector('.chat-input');
            
            if (sendBtn && inputField) {
                const sendMessageHandler = () => {
                    const messageText = inputField.value.trim();
                    if (messageText) {
                        EventBus.emit('chat:message:send:requested', { chatId, message: messageText });
                        inputField.value = '';
                        inputField.focus();
                    }
                };

                sendBtn.onclick = sendMessageHandler;
                inputField.onkeypress = (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessageHandler();
                    }
                };
            }

            Logger.debug('UIManager', `Chat window events setup for ${chatId}`);

        } catch (error) {
            Logger.error('UIManager', `Error setting up chat window events for ${chatId}`, error);
        }
    }

    /**
     * Chat'e odaklanır
     * @param {string} chatId - Chat ID
     */
    function focusChat(chatId) {
        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatWindow) {
            chatWindow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            chatWindow.classList.add('chat-window--highlighted');
            setTimeout(() => chatWindow.classList.remove('chat-window--highlighted'), 2000);
            
            // Input'a odaklan
            const inputField = chatWindow.querySelector('.chat-input');
            if (inputField) {
                setTimeout(() => inputField.focus(), 100);
            }
        }
    }

    /**
     * Loading mesajı ekler
     * @param {string} chatId - Chat ID
     * @param {string} aiName - AI adı
     * @returns {HTMLElement|null} Loading elementi
     */
    function addLoadingMessage(chatId, aiName) {
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (!chatElement) return null;

        const messagesContainer = chatElement.querySelector('.chat-messages');
        if (!messagesContainer) return null;

        const loadingElement = document.createElement('div');
        loadingElement.className = 'message ai-message loading-dots';
        loadingElement.innerHTML = `
            <div class="message-content">
                <div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>
                <div class="text-content">
                    <span class="dots"><span>.</span><span>.</span><span>.</span></span>
                </div>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        `;

        messagesContainer.appendChild(loadingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return loadingElement;
    }

    /**
     * Loading mesajını kaldırır ve gerçek mesajla değiştirir
     * @param {HTMLElement} loadingElement - Loading elementi
     * @param {string} messageHTML - Yeni mesaj HTML'i
     */
    function replaceLoadingMessage(loadingElement, messageHTML) {
        if (loadingElement && loadingElement.parentNode) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = messageHTML;
            const newElement = tempDiv.firstElementChild;
            
            loadingElement.parentNode.replaceChild(newElement, loadingElement);
            
            // Scroll to bottom
            const messagesContainer = newElement.closest('.chat-messages');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    }

    // Public API
    return {
        initializeElements,
        renderChats,
        renderActiveChatsDropdown,
        renderChatHistory,
        focusChat,
        addLoadingMessage,
        replaceLoadingMessage,
        showErrorMessage,
        renderChatMessages // Dışarıya açıldı
    };
})();

// Global olarak erişilebilir yap
window.UIManager = UIManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIManager;
}

