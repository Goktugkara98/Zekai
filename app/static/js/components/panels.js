/**
 * Panel management module for handling AI panels
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
 * Panel Manager Module - Handles all panel operations
 */
const PanelManager = (function() {
    // Private state
    const state = {
        panels: [],
        currentLayout: 1,
        maxPanels: 6
    };

    // Initialize state from global state if exists
    if (window.state && window.state.panels) {
        state.panels = window.state.panels;
        state.currentLayout = window.state.currentLayout || 1;
        state.maxPanels = window.config?.maxPanels || 6;
    } else if (window.state) {
        window.state.panels = state.panels;
    }

    // --- PANEL ELEMENT FACTORIES ---
    function createPanelElement(panelData) {
        log('debug', 'Creating panel element', panelData);
        const panel = document.createElement('div');
        panel.className = 'ai-panel';
        if (panelData.minimized) panel.classList.add('minimized');
        panel.setAttribute('data-panel-id', panelData.id);
        panel.setAttribute('data-ai-type', panelData.aiType);
        
        // Get AI type info
        const aiType = window.state.aiTypes[panelData.aiType];
        
        // Create panel HTML
        panel.innerHTML = `
            <div class="panel-header">
                <div class="panel-title">
                    <i class="${aiType.icon}"></i>
                    <span>${aiType.name}</span>
                </div>
                <div class="panel-controls">
                    <select class="ai-model-select">
                        ${window.state.aiTypes.map((type, index) => 
                            `<option value="${index}" ${index === panelData.aiType ? 'selected' : ''}>${type.name}</option>`
                        ).join('')}
                    </select>
                    <button class="panel-minimize-btn" title="Minimize">
                        <i class="bi bi-dash"></i>
                    </button>
                    <button class="panel-close-btn" title="Close">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
            <div class="panel-content">
                <div class="messages-container">
                    ${panelData.messages && panelData.messages.length > 0 ? 
                        panelData.messages.map(msg => `
                            <div class="message ${msg.isUser ? 'user-message' : 'ai-message'}">
                                <div class="message-content">
                                    <p>${msg.text}</p>
                                </div>
                            </div>
                        `).join('') : 
                        `<div class="message ai-message welcome-message">
                            <div class="message-content">
                                <p>Hello! I'm ${aiType.name}. How can I assist you today?</p>
                            </div>
                        </div>`
                    }
                </div>
                <div class="input-container">
                    <div class="input-group">
                        <input type="text" class="panel-input" placeholder="Type your message...">
                        <button class="btn-send">
                            <i class="bi bi-send"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return panel;
    }

    function createActiveChatItem(panelData) {
        log('debug', 'Creating active chat item', panelData);
        const li = document.createElement('li');
        li.className = 'active-chat-item';
        li.setAttribute('data-panel-id', panelData.id);
        
        // Get AI type info
        const aiType = window.state.aiTypes[panelData.aiType];
        
        // Get last message for preview
        let preview = '...';
        let lastMessage = null;
        if (panelData.messages && panelData.messages.length > 0) {
            const userMessages = panelData.messages.filter(m => m.isUser);
            if (userMessages.length > 0) {
                lastMessage = userMessages[userMessages.length - 1];
                preview = lastMessage.text;
                if (preview.length > 32) {
                    preview = preview.slice(0, 32) + '…';
                }
            }
        }
        
        // Format timestamp
        const timestamp = new Date(panelData.lastActivity || panelData.createdAt).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // Create chat item HTML
        li.innerHTML = `
            <div class="chat-info flex-grow-1">
                <div class="d-flex justify-content-between align-items-center">
                    <strong class="chat-title">${aiType.name}</strong>
                    <span class="chat-time">${timestamp}</span>
                </div>
                <div class="chat-preview text-muted small">
                    <i class="bi bi-chat-dots me-1"></i>${preview}
                </div>
            </div>
        `;
        
        // Add click handler to restore panel
        li.onclick = () => {
            restorePanel(panelData.id);
        };
        
        return li;
    }

    function createPastChatItem(panelData) {
        log('debug', 'Creating past chat item', panelData);
        const li = document.createElement('li');
        li.className = 'past-chat-item';
        li.setAttribute('data-panel-id', panelData.id);
        
        // Get AI type info
        const aiType = window.state.aiTypes[panelData.aiType];
        
        // Get last message for preview
        let preview = '...';
        if (panelData.messages && panelData.messages.length > 0) {
            const userMessages = panelData.messages.filter(m => m.isUser);
            if (userMessages.length > 0) {
                const lastMessage = userMessages[userMessages.length - 1];
                preview = lastMessage.text;
                if (preview.length > 32) {
                    preview = preview.slice(0, 32) + '…';
                }
            }
        }
        
        // Format timestamp
        const timestamp = new Date(panelData.lastActivity || panelData.createdAt).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // Create chat item HTML
        li.innerHTML = `
            <div class="chat-info flex-grow-1">
                <div class="d-flex justify-content-between align-items-center">
                    <strong class="chat-title">${aiType.name}</strong>
                    <span class="chat-time">${timestamp}</span>
                </div>
                <div class="chat-preview text-muted small">
                    <i class="bi bi-chat-dots me-1"></i>${preview}
                </div>
            </div>
        `;
        
        return li;
    }

    // --- RENDER FUNCTIONS ---
    function renderPanels() {
        log('debug', 'Rendering panels. Current state:', JSON.parse(JSON.stringify(state.panels)));
        const panelArea = window.elements.panelArea;
        panelArea.innerHTML = '';
        
        const visiblePanels = state.panels.filter(p => !p.closed);
        
        if (visiblePanels.length === 0) {
            window.elements.welcomeMsg.style.display = '';
            panelArea.appendChild(window.elements.welcomeMsg);
            log('debug', 'No visible panels, showing welcome message.');
            return;
        } else {
            window.elements.welcomeMsg.style.display = 'none';
        }
        
        // Render visible panels
        visiblePanels.forEach(panelData => {
            if (!panelData.minimized) {
                const panel = createPanelElement(panelData);
                panelArea.appendChild(panel);
            }
        });
        
        // Setup panel event handlers
        setupPanelControls();
        
        // Update layout classes
        updateLayoutClasses();
    }

    function renderSidebar() {
        log('debug', 'Rendering sidebar.');
        
        // Active Chats
        const activeList = document.getElementById('active-chats-list');
        if (activeList) {
            activeList.innerHTML = '';
            
            // Get minimized panels for active chats
            const minimizedPanels = state.panels.filter(p => !p.closed && p.minimized);
            
            if (minimizedPanels.length === 0) {
                const emptyMsg = document.createElement('li');
                emptyMsg.className = 'empty-list-message text-muted small px-2 py-3 text-center';
                emptyMsg.textContent = 'No active chats yet. Start a conversation or minimize a panel.';
                activeList.appendChild(emptyMsg);
            } else {
                minimizedPanels.forEach(panel => {
                    activeList.appendChild(createActiveChatItem(panel));
                });
            }
        }
        
        // Past Chats
        const pastList = document.getElementById('past-chats-list');
        if (pastList) {
            pastList.innerHTML = '';
            
            // Get closed panels for past chats
            const closedPanels = state.panels.filter(p => p.closed);
            
            if (closedPanels.length === 0) {
                const emptyMsg = document.createElement('li');
                emptyMsg.className = 'empty-list-message text-muted small px-2 py-3 text-center';
                emptyMsg.textContent = 'No past chats yet. Close a conversation to see it here.';
                pastList.appendChild(emptyMsg);
            } else {
                closedPanels.forEach(panel => {
                    pastList.appendChild(createPastChatItem(panel));
                });
            }
        }
    }

    function updateLayoutClasses() {
        log('debug', 'Updating layout classes');
        const panelArea = window.elements.panelArea;
        const panels = document.querySelectorAll('.ai-panel');
        
        // Remove all layout classes
        panelArea.classList.remove('layout-1', 'layout-2', 'layout-6', 'layout-custom');
        
        // Add the current layout class
        if (state.currentLayout === 'custom') {
            panelArea.classList.add('layout-custom');
        } else {
            panelArea.classList.add(`layout-${state.currentLayout}`);
        }
        
        // Update panel widths based on the layout
        panels.forEach(panel => {
            panel.classList.remove('panel-full', 'panel-half', 'panel-third', 'panel-quarter');
            
            switch (state.currentLayout) {
                case 1:
                    panel.classList.add('panel-full');
                    break;
                case 2:
                    panel.classList.add('panel-half');
                    break;
                case 6:
                    panel.classList.add('panel-third');
                    break;
                case 'custom':
                    // For custom layout, don't add any specific width class
                    break;
                default:
                    // Default to quarter width for other layouts
                    panel.classList.add('panel-quarter');
            }
        });
        
        log('debug', `Updated layout classes to: layout-${state.currentLayout}`);
    }

    function updatePanelControlsUI() {
        log('debug', 'Updating panel controls UI');
        
        // Panel count (visible and not minimized)
        const visiblePanels = state.panels.filter(p => !p.closed && !p.minimized);
        const totalPanels = state.panels.filter(p => !p.closed).length;
        
        // Update panel count badge/icon if exists
        const panelCountElem = document.getElementById('panel-count-badge');
        if (panelCountElem) {
            panelCountElem.textContent = visiblePanels.length;
        }
        
        // Enable/disable remove panel button
        if (window.elements.removePanelBtn) {
            window.elements.removePanelBtn.disabled = totalPanels === 0;
        }
        
        // Enable/disable add panel button
        if (window.elements.addPanelBtn) {
            window.elements.addPanelBtn.disabled = totalPanels >= state.maxPanels;
        }
        
        // Highlight active layout button
        const currentLayout = visiblePanels.length || 1;
        window.elements.getLayoutBtns().forEach(btn => {
            const btnLayout = parseInt(btn.getAttribute('data-layout'));
            btn.classList.toggle('active', btnLayout === currentLayout);
        });
    }

    function rerenderAll() {
        log('debug', 'Full rerender triggered.');
        renderPanels();
        renderSidebar();
        updatePanelControlsUI();
    }

    // --- PANEL EVENT HANDLERS ---
    function setupPanelControls() {
        log('debug', 'Setting up panel controls');
        
        // Panel minimize buttons
        document.querySelectorAll('.panel-minimize-btn').forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const panel = e.target.closest('.ai-panel');
                const panelId = panel.getAttribute('data-panel-id');
                minimizePanel(panelId);
            };
        });
        
        // Panel close buttons
        document.querySelectorAll('.panel-close-btn').forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const panel = e.target.closest('.ai-panel');
                const panelId = panel.getAttribute('data-panel-id');
                closePanel(panelId);
            };
        });
        
        // Send message buttons
        document.querySelectorAll('.btn-send').forEach(btn => {
            btn.onclick = (e) => {
                const inputField = e.target.closest('.input-group').querySelector('.panel-input');
                if (inputField.value.trim()) {
                    const panel = e.target.closest('.ai-panel');
                    const panelId = panel.getAttribute('data-panel-id');
                    sendMessage(panelId, inputField.value);
                    inputField.value = '';
                }
            };
        });
        
        // Enter key to send message
        document.querySelectorAll('.panel-input').forEach(input => {
            input.onkeypress = (e) => {
                if (e.key === 'Enter' && input.value.trim()) {
                    const panel = e.target.closest('.ai-panel');
                    const panelId = panel.getAttribute('data-panel-id');
                    sendMessage(panelId, input.value);
                    input.value = '';
                }
            };
        });
        
        // AI model select
        document.querySelectorAll('.ai-model-select').forEach(select => {
            select.onchange = (e) => {
                const panel = e.target.closest('.ai-panel');
                const panelId = panel.getAttribute('data-panel-id');
                const aiTypeIndex = parseInt(e.target.value);
                changeAIModel(panelId, aiTypeIndex);
            };
        });
    }

    // --- PANEL CONTROL ACTIONS ---
    function addPanel(aiType = 0) {
        if (state.panels.filter(p => !p.closed).length >= state.maxPanels) {
            log('warn', 'Panel add blocked: maxPanels reached');
            return;
        }
        
        const id = `panel-${Date.now()}-${Math.floor(Math.random()*10000)}`;
        state.panels.push({
            id,
            aiType: aiType,
            minimized: false,
            closed: false,
            messages: [],
            createdAt: Date.now(),
            lastActivity: Date.now()
        });
        
        log('action', 'Panel added', id, aiType);
        rerenderAll();
        return id;
    }

    function closePanel(panelId) {
        const panel = state.panels.find(p => p.id === panelId);
        if (panel) {
            // If has messages, confirm
            if (panel.messages && panel.messages.filter(m => m.isUser).length > 0) {
                log('info', 'Close panel confirmation for panel', panelId);
                if (!window.confirm('Sohbet sonlandırılacak, emin misiniz?')) return;
            }
            
            panel.closed = true;
            panel.minimized = false;
            panel.lastActivity = Date.now();
            
            log('action', 'Panel closed', panelId);
            rerenderAll();
        }
    }

    function removePanel() {
        // Find the last visible panel
        const visiblePanels = state.panels.filter(p => !p.closed && !p.minimized);
        if (visiblePanels.length === 0) {
            log('warn', 'No visible panel to remove');
            return;
        }
        
        // Get the last panel
        const panel = visiblePanels[visiblePanels.length - 1];
        closePanel(panel.id);
    }

    function minimizePanel(panelId) {
        const panel = state.panels.find(p => p.id === panelId);
        if (panel) {
            panel.minimized = true;
            panel.lastActivity = Date.now();
            
            log('action', 'Panel minimized', panelId);
            rerenderAll();
        }
    }

    function restorePanel(panelId) {
        const panel = state.panels.find(p => p.id === panelId);
        if (panel) {
            panel.minimized = false;
            panel.lastActivity = Date.now();
            
            log('action', 'Panel restored', panelId);
            rerenderAll();
        }
    }

    function sendMessage(panelId, text) {
        const panel = state.panels.find(p => p.id === panelId);
        if (panel) {
            // Add user message
            panel.messages.push({
                id: Date.now(),
                text: text,
                isUser: true,
                timestamp: Date.now()
            });
            
            panel.lastActivity = Date.now();
            
            log('action', 'Message sent to panel', panelId, text);
            
            // Simulate AI response
            setTimeout(() => {
                const aiType = window.state.aiTypes[panel.aiType];
                let response = '';
                
                switch (aiType.id) {
                    case 'gpt':
                        response = `I'm ${aiType.name}. ${getRandomResponse()}`;
                        break;
                    case 'claude':
                        response = `As ${aiType.name}, ${getRandomResponse()}`;
                        break;
                    default:
                        response = `I'm an AI assistant. ${getRandomResponse()}`;
                }
                
                panel.messages.push({
                    id: Date.now(),
                    text: response,
                    isUser: false,
                    timestamp: Date.now()
                });
                
                panel.lastActivity = Date.now();
                
                log('action', 'AI response received', panelId, response);
                rerenderAll();
            }, 1500);
            
            rerenderAll();
        }
    }

    function changeAIModel(panelId, aiTypeIndex) {
        const panel = state.panels.find(p => p.id === panelId);
        if (panel) {
            panel.aiType = aiTypeIndex;
            panel.lastActivity = Date.now();
            
            log('action', 'AI model changed', panelId, aiTypeIndex);
            rerenderAll();
        }
    }

    function setLayout(layout) {
        if (layout === 'custom') {
            state.currentLayout = 'custom';
            log('action', 'Layout set to custom');
            rerenderAll();
            return;
        }
        
        const numLayout = parseInt(layout);
        state.currentLayout = numLayout;
        
        // Ensure we have the right number of panels
        const visiblePanels = state.panels.filter(p => !p.closed && !p.minimized);
        
        if (visiblePanels.length > numLayout) {
            // Too many panels, minimize excess
            visiblePanels.slice(numLayout).forEach(p => {
                p.minimized = true;
                log('action', 'Panel minimized for layout', p.id);
            });
        } else if (visiblePanels.length < numLayout) {
            // Too few panels, add more or restore minimized
            const minimizedPanels = state.panels.filter(p => !p.closed && p.minimized);
            const panelsToRestore = Math.min(numLayout - visiblePanels.length, minimizedPanels.length);
            
            // First restore minimized panels
            for (let i = 0; i < panelsToRestore; i++) {
                minimizedPanels[i].minimized = false;
                log('action', 'Panel restored for layout', minimizedPanels[i].id);
            }
            
            // Then add new panels if needed
            const panelsToAdd = numLayout - visiblePanels.length - panelsToRestore;
            for (let i = 0; i < panelsToAdd; i++) {
                addPanel();
            }
        }
        
        log('action', 'Layout changed', numLayout);
        rerenderAll();
    }

    function getRandomResponse() {
        const responses = [
            "How can I assist you further?",
            "Is there anything specific you'd like to know?",
            "I'm here to help with any questions you might have.",
            "Let me know if you need more information on this topic.",
            "Feel free to ask me anything else you're curious about."
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    // --- PUBLIC API ---
    return {
        addPanel,
        removePanel,
        closePanel,
        minimizePanel,
        restorePanel,
        sendMessage,
        changeAIModel,
        setLayout,
        renderAll: rerenderAll,
        getState: () => JSON.parse(JSON.stringify(state))
    };
})();

// --- DIRECT DOM EVENT HANDLERS ---
// Attach event handlers directly to DOM elements
function attachDirectEventHandlers() {
    log('debug', 'Attaching direct event handlers to DOM elements');
    
    // Add panel button (direct DOM access)
    const addPanelBtn = document.getElementById('add-panel-btn');
    if (addPanelBtn) {
        log('debug', 'Found add panel button, attaching click handler');
        addPanelBtn.onclick = function() {
            log('action', 'Add panel button clicked (direct)');
            PanelManager.addPanel();
        };
    } else {
        log('error', 'Add panel button not found!');
    }
    
    // Remove panel button (direct DOM access)
    const removePanelBtn = document.getElementById('remove-panel-btn');
    if (removePanelBtn) {
        log('debug', 'Found remove panel button, attaching click handler');
        removePanelBtn.onclick = function() {
            log('action', 'Remove panel button clicked (direct)');
            PanelManager.removePanel();
        };
    }
    
    // Layout buttons (direct DOM access)
    const layoutBtns = document.querySelectorAll('.layout-btn');
    if (layoutBtns.length > 0) {
        log('debug', `Found ${layoutBtns.length} layout buttons, attaching click handlers`);
        layoutBtns.forEach(btn => {
            btn.onclick = function() {
                const layout = this.getAttribute('data-layout');
                log('action', 'Layout button clicked (direct)', layout);
                PanelManager.setLayout(layout);
            };
        });
    }
    
    // Welcome add button (direct DOM access)
    const welcomeAddBtn = document.querySelector('.welcome-add-btn');
    if (welcomeAddBtn) {
        log('debug', 'Found welcome add button, attaching click handler');
        welcomeAddBtn.onclick = function() {
            log('action', 'Welcome add button clicked (direct)');
            PanelManager.addPanel();
        };
    }
}

// Try to attach handlers immediately
attachDirectEventHandlers();

// Also try again when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    log('info', 'DOM fully loaded');
    attachDirectEventHandlers();
    
    // Initial render
    log('info', 'Initial render');
    PanelManager.renderAll();
});

// If document is already loaded, render immediately
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    log('info', 'Document already loaded, rendering immediately');
    attachDirectEventHandlers();
    PanelManager.renderAll();
}
