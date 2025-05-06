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

// --- PANEL STATE ---
if (!state.panels) state.panels = [];

// --- RENDER FUNCTIONS ---
function renderPanels() {
    log('debug', 'Rendering panels. Current state:', JSON.parse(JSON.stringify(state.panels)));
    const panelArea = elements.panelArea;
    panelArea.innerHTML = '';
    const visiblePanels = state.panels.filter(p => !p.closed);
    if (visiblePanels.length === 0) {
        elements.welcomeMsg.style.display = '';
        panelArea.appendChild(elements.welcomeMsg);
        log('debug', 'No visible panels, showing welcome message.');
        return;
    } else {
        elements.welcomeMsg.style.display = 'none';
    }
    visiblePanels.forEach(panelData => {
        const panel = createPanelElement(panelData);
        panelArea.appendChild(panel);
    });
    setupPanelControls();
    setupAIModelSelects();
    updateLayoutClasses();
}

function renderSidebar() {
    log('debug', 'Rendering sidebar.');
    const activeList = document.getElementById('active-chats-list');
    if (activeList) activeList.innerHTML = '';
    state.panels.filter(p => !p.closed && !p.minimized).forEach(panel => {
        if (activeList) activeList.appendChild(createActiveChatItem(panel));
    });
    const pastList = document.getElementById('past-chats-list');
    if (pastList) pastList.innerHTML = '';
    state.panels.filter(p => p.closed).forEach(panel => {
        if (pastList) pastList.appendChild(createPastChatItem(panel));
    });
}

function rerenderAll() {
    log('debug', 'Full rerender triggered.');
    renderPanels();
    renderSidebar();
    updatePanelControlsUI();
}

// --- PANEL ELEMENT FACTORIES ---
function createPanelElement(panelData) {
    log('debug', 'Creating panel element', panelData);
    const panel = document.createElement('div');
    panel.className = 'ai-panel' + (panelData.minimized ? ' minimized' : '');
    panel.setAttribute('data-panel-id', panelData.id);
    panel.setAttribute('data-ai-type', panelData.aiType);
    // ... add inner HTML for header, messages, controls, etc. ...
    // (You can copy from createNewPanel logic, using panelData)
    // For brevity, not repeating full HTML here
    return panel;
}
function createActiveChatItem(panelData) {
    log('debug', 'Creating active chat item', panelData);
    const li = document.createElement('li');
    li.className = 'active-chat-item';
    li.setAttribute('data-panel-id', panelData.id);
    // ... add inner HTML for AI type, preview, etc. ...
    return li;
}
function createPastChatItem(panelData) {
    log('debug', 'Creating past chat item', panelData);
    const li = document.createElement('li');
    li.className = 'past-chat-item';
    li.setAttribute('data-panel-id', panelData.id);
    // ... add inner HTML for AI type, preview, etc. ...
    return li;
}

// --- PANEL CONTROL ACTIONS ---
function addPanel(aiType) {
    if (state.panels.length >= config.maxPanels) {
        log('warn', 'Panel add blocked: maxPanels reached');
        return;
    }
    const id = `panel-${Date.now()}-${Math.floor(Math.random()*10000)}`;
    state.panels.push({
        id,
        aiType: aiType || 0,
        minimized: false,
        closed: false,
        messages: [],
        createdAt: Date.now()
    });
    log('action', 'Panel added', id, aiType);
    rerenderAll();
}
function removePanel() {
    const idx = state.panels.findIndex(p => !p.closed);
    if (idx !== -1) {
        const panel = state.panels[idx];
        if (panel.messages && panel.messages.length > 0) {
            log('info', 'Remove panel confirmation for panel', panel.id);
            if (!window.confirm('Sohbet sonlandırılacak, emin misiniz?')) return;
        }
        panel.closed = true;
        panel.minimized = false;
        log('action', 'Panel closed', panel.id);
        rerenderAll();
    } else {
        log('warn', 'No open panel to remove');
    }
}
function minimizePanel(panelId) {
    const panel = state.panels.find(p => p.id === panelId);
    if (panel) {
        panel.minimized = true;
        log('action', 'Panel minimized', panelId);
        rerenderAll();
    }
}
function restorePanel(panelId) {
    const panel = state.panels.find(p => p.id === panelId);
    if (panel) {
        panel.minimized = false;
        log('action', 'Panel restored', panelId);
        rerenderAll();
    }
}
function setLayout(n) {
    let openPanels = state.panels.filter(p => !p.closed && !p.minimized);
    if (openPanels.length > n) {
        openPanels.slice(n).forEach(p => {
            p.minimized = true;
            log('action', 'Panel minimized for layout', p.id);
        });
    } else if (openPanels.length < n) {
        for (let i = openPanels.length; i < n; i++) {
            addPanel();
        }
    }
    log('info', 'Layout changed', n);
    rerenderAll();
}

// --- WIRE UP BUTTONS ---
elements.addPanelBtn.onclick = () => { log('action', 'Add panel button clicked'); addPanel(); };
elements.removePanelBtn.onclick = () => { log('action', 'Remove panel button clicked'); removePanel(); };
elements.getLayoutBtns().forEach(btn => {
    btn.onclick = () => {
        const layout = parseInt(btn.getAttribute('data-layout'));
        log('action', 'Layout button clicked', layout);
        setLayout(layout);
    };
});

// --- INITIAL RENDER ---
log('info', 'Initial render');
rerenderAll();

/**
 * Update panels based on the current layout
 * @param {number|string} layout - Layout configuration (1, 2, 6, "custom")
 */
function updatePanels(layout) {
    log('debug', 'Updating panels for layout', layout);
    // Handle custom layout differently
    if (layout === 'custom') {
        // Just update the active layout button without changing panel count
        updateActiveLayoutButton(layout);
        return;
    }
    
    // Convert layout to number for numeric layouts
    const numericLayout = parseInt(layout);
    state.currentLayout = numericLayout;
    
    // Update active layout button
    updateActiveLayoutButton(layout);
    
    // If there are no panels, show welcome message
    if (state.panelCount === 0) {
        elements.welcomeMsg.style.display = '';
        elements.panelArea.innerHTML = '';
        elements.panelArea.appendChild(elements.welcomeMsg);
        log('debug', 'No panels, showing welcome message');
        return;
    } else {
        elements.welcomeMsg.style.display = 'none';
    }
    
    // Save existing panels before clearing
    const existingPanels = Array.from(document.querySelectorAll('.ai-panel'));
    const activePanels = existingPanels.filter(panel => !panel.classList.contains('minimized'));
    const minimizedPanels = existingPanels.filter(panel => panel.classList.contains('minimized'));
    
    log('debug', `Layout changed to ${layout}. Active panels: ${activePanels.length}, Minimized: ${minimizedPanels.length}, Total: ${existingPanels.length}`);
    
    // Determine how many panels to keep based on the new layout
    const maxPanelsInLayout = numericLayout;
    
    // If we need to reduce panels, prioritize active panels first
    if (existingPanels.length > maxPanelsInLayout) {
        log('debug', `Need to reduce panels from ${existingPanels.length} to ${maxPanelsInLayout}`);
        
        // First, try to keep all active panels
        if (activePanels.length <= maxPanelsInLayout) {
            // We can keep all active panels, but may need to remove some minimized ones
            log('debug', 'Keeping all active panels, removing excess minimized panels');
            
            // Update panel count to match the new layout
            state.panelCount = maxPanelsInLayout;
            
            // Clear panel area to rebuild it
            elements.panelArea.innerHTML = '';
            
            // Add all active panels back
            activePanels.forEach(panel => {
                elements.panelArea.appendChild(panel.cloneNode(true));
            });
            
            // If we still have room, add some minimized panels back (they'll stay minimized)
            const remainingSlots = maxPanelsInLayout - activePanels.length;
            if (remainingSlots > 0 && minimizedPanels.length > 0) {
                log('debug', `Adding ${Math.min(remainingSlots, minimizedPanels.length)} minimized panels back`);
                
                // Add minimized panels from left to right until we fill the layout
                for (let i = 0; i < Math.min(remainingSlots, minimizedPanels.length); i++) {
                    elements.panelArea.appendChild(minimizedPanels[i].cloneNode(true));
                }
            }
            
            // Setup panel controls after rebuilding
            setupPanelControls();
            setupAIModelSelects();
            updateLayoutClasses();
            return;
        } else {
            // We have more active panels than the layout allows
            // Keep panels from left to right up to the layout limit
            log('debug', `Too many active panels (${activePanels.length}), keeping first ${maxPanelsInLayout}`);
            
            // Update panel count to match the new layout
            state.panelCount = maxPanelsInLayout;
            
            // Clear panel area
            elements.panelArea.innerHTML = '';
            
            // Add panels from left to right up to the layout limit
            for (let i = 0; i < maxPanelsInLayout; i++) {
                if (i < activePanels.length) {
                    elements.panelArea.appendChild(activePanels[i].cloneNode(true));
                }
            }
            
            // Setup panel controls after rebuilding
            setupPanelControls();
            setupAIModelSelects();
            updateLayoutClasses();
            return;
        }
    }
    
    // If we're increasing the number of panels or keeping the same number
    if (existingPanels.length < maxPanelsInLayout) {
        // We need to add more panels
        const panelsToAdd = maxPanelsInLayout - existingPanels.length;
        log('debug', `Adding ${panelsToAdd} new panels`);
        
        // Update panel count
        state.panelCount = maxPanelsInLayout;
        
        // Clear panel area
        elements.panelArea.innerHTML = '';
        
        // First add existing panels back
        existingPanels.forEach(panel => {
            elements.panelArea.appendChild(panel.cloneNode(true));
        });
        
        // Then create new panels for the remaining slots
        for (let i = existingPanels.length; i < maxPanelsInLayout; i++) {
            createNewPanel();
        }
        
        // Setup panel controls after creating panels
        setupPanelControls();
        setupAIModelSelects();
        updateLayoutClasses();
        return;
    }
    
    // If we have exactly the right number of panels, just update the layout classes
    if (existingPanels.length === maxPanelsInLayout) {
        updateLayoutClasses();
    }
    syncActiveChatsWithPanels();
}

/**
 * Update the active layout button
 * @param {number|string} layout - Layout configuration (1, 2, 6, "custom")
 */
function updateActiveLayoutButton(layout) {
    elements.getLayoutBtns().forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-layout') === layout.toString()) {
            btn.classList.add('active');
        }
    });
}

/**
 * Create a new panel and add it to the panel area
 */
function createNewPanel() {
    log('debug', 'Creating new panel');
    // Generate a truly unique ID with timestamp and random component
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 10000);
    const panelId = `panel-${timestamp}-${random}`;
    
    console.log('Creating panel with ID:', panelId);
    
    // Select a random AI type for variety
    const randomIndex = Math.floor(Math.random() * state.aiTypes.length);
    const aiType = state.aiTypes[randomIndex];
    
    // Create dropdown options for AI models
    let aiModelOptions = '';
    state.aiTypes.forEach((type, index) => {
        aiModelOptions += `<option value="${index}" ${index === randomIndex ? 'selected' : ''}>${type.name}</option>`;
    });
    
    const panel = createElement('div', {
        className: 'ai-panel',
        draggable: 'true',
        'data-panel-id': panelId,
        'data-ai-type': randomIndex,
        innerHTML: `
            <div class="panel-header">
                <div class="panel-title">
                    <i class="${aiType.icon}"></i>
                    <select class="ai-model-select" data-panel-id="${panelId}">
                        ${aiModelOptions}
                    </select>
                </div>
                <div class="panel-controls">
                    <button class="btn-panel-minimize" title="Minimize">
                        <i class="bi bi-dash"></i>
                    </button>
                    <button class="btn-panel-maximize" title="Maximize">
                        <i class="bi bi-arrows-fullscreen"></i>
                    </button>
                    <button class="btn-panel-close" title="Close">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
            <div class="panel-body">
                <div class="messages-container">
                    <!-- Messages will appear here -->
                    <div class="message ai-message">
                        <div class="message-content">
                            <p>Hello! I'm ${aiType.name}. How can I assist you today?</p>
                        </div>
                    </div>
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
        `
    });
    
    elements.panelArea.appendChild(panel);
}

/**
 * Setup panel control buttons and interactions
 */
function setupPanelControls() {
    log('debug', 'Setting up panel controls');
    // Panel minimize/maximize functionality
    elements.getPanelMinimizeButtons().forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            const panel = e.target.closest('.ai-panel');
            // Add minimizing animation class
            panel.classList.add('minimizing');
            setTimeout(() => {
                if (!panel.classList.contains('minimized')) {
                    panel.classList.add('minimized');
                    panel.classList.remove('minimizing');
                    panel.style.display = 'none';
                    addToActiveChats(panel);
                } else {
                    panel.classList.remove('minimized');
                    panel.classList.remove('minimizing');
                    panel.style.display = '';
                    removeFromActiveChats(panel.getAttribute('data-panel-id'));
                }
            }, 300);
        };
    });

    // Panel close (çarpı) button functionality
    elements.getPanelCloseButtons().forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            const panel = e.target.closest('.ai-panel');
            const panelId = panel.getAttribute('data-panel-id');
            // Check if conversation is active (has user messages)
            const hasUserMsg = panel.querySelector('.message.user-message');
            if (hasUserMsg) {
                if (!window.confirm('Sohbet sonlandırılacak, emin misiniz?')) {
                    return;
                }
                addToPastChats(panel);
            }
            // Remove from active chats
            const chatItem = document.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`);
            if (chatItem) chatItem.remove();
            // Remove panel from DOM
            panel.remove();
            // Update panel count
            const remainingPanels = document.querySelectorAll('.ai-panel').length;
            state.panelCount = remainingPanels;
            // If no panels left, show welcome message
            if (remainingPanels === 0) {
                elements.welcomeMsg.style.display = '';
                elements.panelArea.appendChild(elements.welcomeMsg);
            } else {
                updateLayoutClasses();
            }
        };
    });

    // Simulate sending messages
    elements.getSendButtons().forEach(btn => {
        btn.onclick = (e) => {
            const inputField = e.target.closest('.input-group').querySelector('.panel-input');
            if (inputField.value.trim()) {
                simulateResponse(e.target.closest('.ai-panel'), inputField.value);
                inputField.value = '';
            }
        };
    });

    // Also allow Enter key to send messages
    elements.getPanelInputs().forEach(input => {
        input.onkeypress = (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                simulateResponse(e.target.closest('.ai-panel'), input.value);
                input.value = '';
            }
        };
    });
}

/**
 * Setup AI model selects
 */
function setupAIModelSelects() {
    log('debug', 'Setting up AI model selects');
    elements.getAIModelSelects().forEach(select => {
        // Check if panel already has conversation
        const panel = select.closest('.ai-panel');
        const hasMessages = panel.querySelector('.message:not(.ai-message)');
        
        if (hasMessages) {
            select.disabled = true;
            return;
        }
        
        select.onchange = (e) => {
            const panel = e.target.closest('.ai-panel');
            const selectedIndex = e.target.value;
            const aiType = state.aiTypes[selectedIndex];
            
            // Update panel data attribute
            panel.setAttribute('data-ai-type', selectedIndex);
            
            // Update AI icon in panel header
            const aiIcon = panel.querySelector('.panel-title i');
            aiIcon.className = aiType.icon;
            
            // Update welcome message if it exists
            const welcomeMsg = panel.querySelector('.ai-message');
            if (welcomeMsg) {
                welcomeMsg.querySelector('.message-content p').textContent = 
                    `Hello! I'm ${aiType.name}. How can I assist you today?`;
            }
            
            log('info', `Changed AI model to ${aiType.name} for panel ${panel.getAttribute('data-panel-id')}`);
        };
    });
}

/**
 * Simulate sending and receiving messages
 * @param {HTMLElement} panel - The panel to add messages to
 * @param {string} userMessage - The user's message
 */
function simulateResponse(panel, userMessage) {
    log('debug', 'Simulating response for panel', panel.getAttribute('data-panel-id'));
    // Get the messages container
    const messagesContainer = panel.querySelector('.messages-container');
    
    // Add user message
    const userMessageEl = createElement('div', {
        className: 'message user-message',
        innerHTML: `
            <div class="message-content">
                <p>${userMessage}</p>
            </div>
        `
    });
    
    messagesContainer.appendChild(userMessageEl);
    
    // Lock the AI model dropdown for this panel
    const aiModelSelect = panel.querySelector('.ai-model-select');
    if (aiModelSelect) {
        aiModelSelect.disabled = true;
    }
    
    // Add to active chats if not already there
    const panelId = panel.getAttribute('data-panel-id');
    if (!document.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`)) {
        addToActiveChats(panel);
    }
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Simulate AI thinking delay
    setTimeout(() => {
        // Generate response based on message content
        let response;
        switch(userMessage.toLowerCase()) {
            case 'hello':
                response = "Hello there! How can I help you today?";
                break;
            case 'hi':
                response = "Hi! What would you like to know?";
                break;
            default:
                response = `I'm an AI assistant. ${getRandomResponse()}`;
        }
        
        // Add AI response with animation
        const aiMessageEl = createElement('div', {
            className: 'message ai-message',
            innerHTML: `
                <div class="message-content">
                    <p>${response}</p>
                </div>
            `
        });
        
        messagesContainer.appendChild(aiMessageEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 1500);
}

/**
 * Get a random response for the AI
 * @returns {string} - A random response
 */
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

/**
 * Add a panel to the active chats sidebar
 * @param {HTMLElement} panel - The panel to add to active chats
 */
function addToActiveChats(panel) {
    log('debug', 'Adding panel to active chats', panel.getAttribute('data-panel-id'));
    const panelId = panel.getAttribute('data-panel-id') || `panel-${Date.now()}`;
    const aiTypeIndex = parseInt(panel.getAttribute('data-ai-type') || '0');
    const aiType = state.aiTypes[aiTypeIndex];
    const lastMessage = panel.querySelector('.message.user-message:last-child')?.textContent?.trim() || '';
    const preview = lastMessage.length > 32 ? lastMessage.slice(0, 32) + '…' : lastMessage || '...';
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    // Remove existing chat item if present
    const existingItem = document.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`);
    if (existingItem) existingItem.remove();

    // Create new chat item
    const chatItem = createElement('li', {
        className: `active-chat-item${panel.classList.contains('minimized') ? ' minimized' : ''}`,
        'data-panel-id': panelId,
        innerHTML: `
            <i class="${aiType.icon}"></i>
            <div class="chat-info flex-grow-1">
                <div class="d-flex justify-content-between align-items-center">
                    <strong class="chat-title">${aiType.name}</strong>
                    <span class="chat-time">${timestamp}</span>
                </div>
                <div class="chat-preview text-muted small">
                    <i class="bi bi-chat-dots me-1"></i>${preview}
                </div>
            </div>
        `
    });

    // Click handler
    chatItem.onclick = () => {
        const targetPanel = document.querySelector(`.ai-panel[data-panel-id="${panelId}"]`);
        if (targetPanel) {
            if (targetPanel.classList.contains('minimized')) {
                // Restore panel
                targetPanel.classList.remove('minimized');
                targetPanel.style.display = '';
                // Remove from active chats minimized state
                chatItem.classList.remove('minimized');
            }
            targetPanel.scrollIntoView({behavior: 'smooth', block: 'nearest'});
            targetPanel.classList.add('highlight');
            setTimeout(() => targetPanel.classList.remove('highlight'), 1200);
        }
    };

    // Add to top of list
    const list = document.getElementById('active-chats-list');
    if (list.firstChild) {
        list.insertBefore(chatItem, list.firstChild);
    } else {
        list.appendChild(chatItem);
    }
}

/**
 * Remove a panel from the active chats sidebar
 * @param {string} panelId - The ID of the panel to remove
 */
function removeFromActiveChats(panelId) {
    log('debug', 'Removing panel from active chats', panelId);
    
    const chatItem = document.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`);
    if (chatItem) {
        log('debug', 'Found chat item, removing it');
        
        // Add removing animation class
        chatItem.classList.add('removing');
        
        // Wait for animation to complete before removing
        setTimeout(() => {
            chatItem.remove();
            
            // If no more active chats, show empty message
            if (document.querySelectorAll('.active-chat-item').length === 0) {
                const emptyMessage = createElement('li', {
                    className: 'empty-list-message text-muted small px-2 py-3 text-center',
                    innerHTML: 'No active chats yet. Start a conversation or minimize a panel.'
                });
                document.getElementById('active-chats-list').appendChild(emptyMessage);
            }
        }, 300); // Match this with the CSS animation duration
    } else {
        log('debug', 'Chat item not found for panel:', panelId);
    }
}

/**
 * Utility to add to past chats
 * @param {HTMLElement} panel - The panel to add to past chats
 */
function addToPastChats(panel) {
    log('debug', 'Adding panel to past chats', panel.getAttribute('data-panel-id'));
    const panelId = panel.getAttribute('data-panel-id');
    const aiTypeIndex = parseInt(panel.getAttribute('data-ai-type') || '0');
    const aiType = state.aiTypes[aiTypeIndex];
    const lastMessage = panel.querySelector('.message.user-message:last-child')?.textContent?.trim() || '';
    const preview = lastMessage.length > 32 ? lastMessage.slice(0, 32) + '…' : lastMessage || '...';
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    // Remove existing past chat item if present
    const existingItem = document.querySelector(`.past-chat-item[data-panel-id="${panelId}"]`);
    if (existingItem) existingItem.remove();

    // Create new past chat item
    const chatItem = createElement('li', {
        className: 'past-chat-item',
        'data-panel-id': panelId,
        innerHTML: `
            <i class="${aiType.icon}"></i>
            <div class="chat-info flex-grow-1">
                <div class="d-flex justify-content-between align-items-center">
                    <strong class="chat-title">${aiType.name}</strong>
                    <span class="chat-time">${timestamp}</span>
                </div>
                <div class="chat-preview text-muted small">
                    <i class="bi bi-chat-dots me-1"></i>${preview}
                </div>
            </div>
        `
    });
    // Add to list
    const list = document.getElementById('past-chats-list');
    if (list) list.prepend(chatItem);
}

/**
 * Update removePanel logic to show confirmation and move to past chats
 */
function removePanel() {
    if (state.panelCount > 0) {
        const panels = document.querySelectorAll('.ai-panel');
        const panelToRemove = panels[panels.length - 1];
        if (panelToRemove) {
            const panelId = panelToRemove.getAttribute('data-panel-id');
            // Check if conversation is active (has user messages)
            const hasUserMsg = panelToRemove.querySelector('.message.user-message');
            if (hasUserMsg) {
                if (!window.confirm('Sohbet sonlandırılacak, emin misiniz?')) {
                    return;
                }
                // Move to past chats
                addToPastChats(panelToRemove);
            }
            // Remove from active chats
            const chatItem = document.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`);
            if (chatItem) chatItem.remove();
        }
        state.panelCount--;
        updatePanels(state.currentLayout);
        syncActiveChatsWithPanels();
    }
}

/**
 * Update layout classes based on the current layout
 */
function updateLayoutClasses() {
    log('debug', 'Updating layout classes');
    const panelArea = elements.panelArea;
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
        // Remove all width classes
        panel.classList.remove('panel-full', 'panel-half', 'panel-third', 'panel-quarter');
        
        // Add appropriate width class based on layout
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
                // This allows panels to be freely resized
                break;
            default:
                // Default to quarter width for other layouts
                panel.classList.add('panel-quarter');
        }
    });
    
    log('debug', `Updated layout classes to: layout-${state.currentLayout}`);
    syncActiveChatsWithPanels();
}

/**
 * Add a new panel
 */
function addPanel() {
    if (state.panelCount < config.maxPanels) {
        state.panelCount++;
        updatePanels(state.currentLayout);
        syncActiveChatsWithPanels();
    }
}

/**
 * Remove a panel
 */
function removePanel() {
    if (state.panelCount > 0) {
        const panels = document.querySelectorAll('.ai-panel');
        const panelToRemove = panels[panels.length - 1];
        if (panelToRemove) {
            const panelId = panelToRemove.getAttribute('data-panel-id');
            // Check if conversation is active (has user messages)
            const hasUserMsg = panelToRemove.querySelector('.message.user-message');
            if (hasUserMsg) {
                if (!window.confirm('Sohbet sonlandırılacak, emin misiniz?')) {
                    return;
                }
                // Move to past chats
                addToPastChats(panelToRemove);
            }
            // Remove from active chats
            const chatItem = document.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`);
            if (chatItem) chatItem.remove();
        }
        state.panelCount--;
        updatePanels(state.currentLayout);
        syncActiveChatsWithPanels();
    }
}

/**
 * Update remove panel button state
 */
function updateRemovePanelBtn() {
    elements.removePanelBtn.disabled = state.panelCount === 0;
}

/**
 * Setup panel-related event listeners
 */
function setupPanelEventListeners() {
    elements.addPanelBtn.onclick = addPanel;
    elements.removePanelBtn.onclick = removePanel;
    elements.welcomeAddBtn.onclick = addPanel;
    
    elements.getLayoutBtns().forEach(btn => {
        btn.onclick = () => {
            let layout = parseInt(btn.getAttribute('data-layout'));
            if (state.panelCount < layout) state.panelCount = layout;
            updatePanels(layout);
            syncActiveChatsWithPanels();
        };
    });
    
    // Remove panel from within
    elements.panelArea.addEventListener('click', (e) => {
        if (e.target.closest('.remove-panel-btn')) {
            e.stopPropagation();
            removePanel();
        }
    });
}

// --- Helper to sync Active Chats with visible panels ---
function syncActiveChatsWithPanels() {
    log('debug', 'Syncing active chats with panels');
    // Get all current panel IDs
    const currentPanels = Array.from(document.querySelectorAll('.ai-panel'));
    const currentPanelIds = currentPanels.map(panel => panel.getAttribute('data-panel-id'));
    const activeChatsList = document.getElementById('active-chats-list');
    if (!activeChatsList) return;

    // Remove any Active Chat items for panels that no longer exist
    Array.from(activeChatsList.querySelectorAll('.active-chat-item')).forEach(item => {
        const panelId = item.getAttribute('data-panel-id');
        if (!currentPanelIds.includes(panelId)) {
            item.remove();
        }
    });

    // Add Active Chat items for any panels that are missing from the sidebar
    currentPanels.forEach(panel => {
        const panelId = panel.getAttribute('data-panel-id');
        if (!activeChatsList.querySelector(`.active-chat-item[data-panel-id="${panelId}"]`)) {
            addToActiveChats(panel);
        }
    });
}

/**
 * Update panel controls UI
 */
function updatePanelControlsUI() {
    log('debug', 'Updating panel controls UI');
    // Panel count (open and not minimized)
    const openPanels = state.panels.filter(p => !p.closed && !p.minimized);
    const totalPanels = state.panels.filter(p => !p.closed).length;
    // Update panel count badge/icon if exists
    const panelCountElem = document.getElementById('panel-count-badge');
    if (panelCountElem) {
        panelCountElem.textContent = openPanels.length;
    }
    // Enable/disable remove panel button
    if (elements.removePanelBtn) {
        elements.removePanelBtn.disabled = totalPanels === 0;
    }
    // Enable/disable add panel button
    if (elements.addPanelBtn) {
        elements.addPanelBtn.disabled = totalPanels >= config.maxPanels;
    }
    // Highlight active layout button
    const currentLayout = openPanels.length;
    elements.getLayoutBtns().forEach(btn => {
        const btnLayout = parseInt(btn.getAttribute('data-layout'));
        if (btnLayout === currentLayout) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}
