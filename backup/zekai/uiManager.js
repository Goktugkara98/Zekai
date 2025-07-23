/**
 * Arayüz Yöneticisi Modülü (UI Manager)
 * =====================================
 * @description DOM elementlerini yönetir, arayüzü render eder,
 * ve kullanıcı etkileşimlerini dinleyip ilgili servislere yönlendirir.
 */

import { log } from './logger.js';
import * as state from './state.js';
import * as service from './chatService.js';
import * as components from './uicomponents.js';

// DOM element referanslarını tutan nesne
const elements = {};
let isInitialized = false;

/**
 * Gerekli DOM elementlerini bulur ve `elements` nesnesine atar.
 * @returns {boolean} Başarılı olup olmadığı.
 */
export function initUIManager() {
    if (isInitialized) return true;
    log('info', 'UIManager', 'DOM elementleri başlatılıyor...');
    const elementIds = [
        'chat-container', 'welcome-screen', 'welcome-new-chat-btn', 'new-chat-btn',
        'clear-chats-btn', 'active-chats-dropdown-trigger', 'active-chats-dropdown-menu',
        'active-chats-list', 'broadcast-message-input', 'send-broadcast-btn',
        'chat-history-trigger', 'chat-history-menu', 'chat-history-list'
    ];
    elementIds.forEach(id => {
        elements[id.replace(/-(\w)/g, (m, p1) => p1.toUpperCase())] = document.getElementById(id);
    });

    const missing = Object.keys(elements).filter(key => !elements[key]);
    if (missing.length > 0) {
        log('error', 'UIManager', `Kritik DOM elementleri bulunamadı: ${missing.join(', ')}`);
        return false;
    }
    isInitialized = true;
    log('info', 'UIManager', 'Tüm DOM elementleri başarıyla bulundu.');
    return true;
}

/**
 * Tüm arayüzü (sohbetler, dropdown, geçmiş) yeniden çizer.
 */
export function renderAll() {
    renderChats();
    renderActiveChatsDropdown();
    renderChatHistory();
}

/**
 * Sohbet pencerelerini state'e göre render eder.
 */
function renderChats() {
    if (!elements.chatContainer) return;
    elements.chatContainer.innerHTML = '';
    
    const activeVisibleChats = state.getChats().filter(chat => !chat.isMinimized);

    if (activeVisibleChats.length === 0) {
        elements.chatContainer.appendChild(elements.welcomeScreen);
        elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap justify-content-center align-items-center';
    } else {
        let layoutClass;
        switch (activeVisibleChats.length) {
            case 1: layoutClass = 'layout-1'; break;
            case 2: layoutClass = 'layout-2'; break;
            case 3: layoutClass = 'layout-3'; break;
            case 4: layoutClass = 'layout-4'; break;
            default: layoutClass = `layout-${Math.min(activeVisibleChats.length, 6)}`; break;
        }
        elements.chatContainer.className = `flex-grow-1 d-flex flex-wrap ${layoutClass}`;
        
        activeVisibleChats.forEach(chatData => {
            const chatElement = components.createChatElement(chatData);
            elements.chatContainer.appendChild(chatElement);
            setupChatWindowControls(chatElement);
        });
    }
}

/**
 * Aktif sohbetler dropdown menüsünü render eder.
 */
function renderActiveChatsDropdown() {
    if (!elements.activeChatsList) return;
    elements.activeChatsList.innerHTML = '';
    const chats = state.getChats();

    if (chats.length === 0) {
        elements.activeChatsDropdownTrigger.classList.add('disabled');
        elements.activeChatsList.innerHTML = '<li class="list-group-item text-muted">Aktif sohbet yok</li>';
        return;
    }

    elements.activeChatsDropdownTrigger.classList.remove('disabled');
    chats.forEach(chatData => {
        const listItem = components.createActiveChatDropdownItem(chatData);
        listItem.addEventListener('click', (e) => {
            e.stopPropagation();
            if (chatData.isMinimized) {
                state.setChatMinimized(chatData.id, false);
                renderAll();
            } else {
                const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                if (chatWindow) {
                    chatWindow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    chatWindow.classList.add('chat-window--highlighted');
                    setTimeout(() => chatWindow.classList.remove('chat-window--highlighted'), 2000);
                }
            }
        });
        elements.activeChatsList.appendChild(listItem);
    });
}

/**
 * Sohbet geçmişi menüsünü render eder.
 */
function renderChatHistory() {
    if (!elements.chatHistoryList) return;
    elements.chatHistoryList.innerHTML = '';
    const history = state.getChatHistory();

    if (history.length === 0) {
        elements.chatHistoryTrigger.classList.add('disabled');
        elements.chatHistoryList.innerHTML = '<li class="list-group-item text-muted">Sohbet geçmişi yok</li>';
        return;
    }

    elements.chatHistoryTrigger.classList.remove('disabled');
    history.forEach(chatData => {
        const listItem = components.createChatHistoryItem(chatData);
        // TODO: Geçmişi geri yükleme ve görüntüleme fonksiyonları eklenecek.
        listItem.querySelector('.chat-history-restore-btn').onclick = (e) => {
            e.stopPropagation();
            alert('Geçmişi geri yükleme henüz aktif değil.');
        };
        listItem.onclick = () => alert('Geçmişi görüntüleme henüz aktif değil.');
        elements.chatHistoryList.appendChild(listItem);
    });
}

/**
 * Tek bir sohbet penceresini günceller (örn: model değiştiğinde).
 * @param {string} chatId Güncellenecek pencerenin ID'si.
 */
export function updateChatWindow(chatId) {
    const chatData = state.getChatById(chatId);
    const existingElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
    if (chatData && existingElement) {
        const newElement = components.createChatElement(chatData);
        existingElement.replaceWith(newElement);
        setupChatWindowControls(newElement);
    }
}

/**
 * Bir sohbet penceresine yeni bir mesaj ekler.
 * @param {string} chatId Mesajın ekleneceği pencerenin ID'si.
 * @param {object} messageData Mesaj verisi.
 */
export function addMessageToWindow(chatId, messageData) {
    const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
    if (!chatElement) return;
    const messagesContainer = chatElement.querySelector('.chat-messages');
    if (messagesContainer) {
        // Hoşgeldin mesajı varsa kaldır
        const welcome = messagesContainer.querySelector('.welcome-message');
        if(welcome) welcome.remove();

        const messageHTML = components.createMessageHTML(messageData);
        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// --- Yükleniyor / Hata Mesajı Yönetimi ---

let loadingMessageCounter = 0;

export function showLoadingMessage(chatId) {
    const loadingId = `loading-${loadingMessageCounter++}`;
    const loadingMessageHTML = components.createLoadingMessageHTML(loadingId);
    const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
    if (!chatElement) return null;

    const messagesContainer = chatElement.querySelector('.chat-messages');
    if (messagesContainer) {
        messagesContainer.insertAdjacentHTML('beforeend', loadingMessageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    return loadingId;
}

export function updateLoadingMessage(chatId, loadingId, finalMessageData) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        const finalMessageHTML = components.createMessageHTML(finalMessageData);
        loadingElement.outerHTML = finalMessageHTML;
    } else {
        addMessageToWindow(chatId, finalMessageData);
    }
}

export function showErrorMessage(chatId, loadingId, errorMessageData) {
    const loadingElement = document.getElementById(loadingId);
    const errorHTML = components.createMessageHTML(errorMessageData);
    if (loadingElement) {
        loadingElement.outerHTML = errorHTML;
    } else {
        addMessageToWindow(chatId, errorMessageData);
    }
}


// --- Olay Dinleyici Kurulumları (Event Handler Setup) ---

export function setupGlobalHandlers() {
    elements.welcomeNewChatBtn.onclick = () => service.addChat();
    elements.newChatBtn.onclick = () => service.addChat();

    elements.clearChatsBtn.onclick = () => {
        const chats = state.getChats();
        const startedChatsCount = chats.filter(c => c.messages.some(msg => msg.isUser)).length;
        if (chats.length > startedChatsCount) {
            if (confirm(`${chats.length - startedChatsCount} adet başlanmamış sohbeti kapatmak istiyor musunuz?`)) {
                service.clearAllChats(false);
            }
        } else if (chats.length > 0) {
            if (confirm(`Tüm (${chats.length}) sohbetleri kapatıp geçmişe taşımak istiyor musunuz?`)) {
                service.clearAllChats(true);
            }
        } else {
            alert('Temizlenecek sohbet yok.');
        }
    };

    const broadcastHandler = () => {
        const text = elements.broadcastMessageInput.value.trim();
        if (text) {
            service.sendBroadcastMessage(text);
            elements.broadcastMessageInput.value = '';
        }
    };
    elements.sendBroadcastBtn.addEventListener('click', broadcastHandler);
    elements.broadcastMessageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            broadcastHandler();
        }
    });
}

function setupChatWindowControls(chatElement) {
    const chatId = chatElement.getAttribute('data-chat-id');
    if (!chatId) return;

    chatElement.querySelector('.chat-close-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        const chat = state.getChatById(chatId);
        if (chat && chat.messages.some(msg => msg.isUser)) {
            if (confirm("Bu sohbeti kapatmak istediğinizden emin misiniz? Konuşma geçmişe kaydedilecek.")) {
                service.removeChat(chatId);
            }
        } else {
            service.removeChat(chatId);
        }
    });

    chatElement.querySelector('.chat-minimize-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        state.setChatMinimized(chatId, true);
        renderAll();
    });

    const chatTitle = chatElement.querySelector('.chat-title.model-changeable');
    if (chatTitle) {
        chatTitle.onclick = (e) => {
            e.stopPropagation();
            showModelDropdown(chatId, chatTitle);
        };
    }

    const sendBtn = chatElement.querySelector('.chat-send-btn');
    const inputField = chatElement.querySelector('.chat-input');
    const sendMessageHandler = () => {
        const messageText = inputField.value.trim();
        if (messageText) {
            service.sendMessage(chatId, messageText);
            inputField.value = '';
            inputField.focus();
        }
    };
    sendBtn?.addEventListener('click', sendMessageHandler);
    inputField?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessageHandler();
        }
    });
}

export function setupSidebarListeners(onModelSelect) {
    document.querySelectorAll('.ai-model-selector-item').forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            const modelId = this.dataset.aiIndex;
            if (modelId) {
                onModelSelect(modelId);
            } else {
                log('error', 'UIManager', 'Geçersiz AI model ID seçildi.', { dataset: this.dataset });
                alert("Geçersiz model seçimi.");
            }
        });
    });
}

// --- Model Dropdown Yönetimi ---
let activeModelDropdownContext = null;

function closeAllModelDropdowns() {
    if (activeModelDropdownContext) {
        const { dropdownEl, handler } = activeModelDropdownContext;
        if (dropdownEl && dropdownEl.parentNode) {
            dropdownEl.classList.remove('show');
            setTimeout(() => {
                if (dropdownEl.parentNode) dropdownEl.parentNode.removeChild(dropdownEl);
            }, 300);
        }
        document.removeEventListener('click', handler, true);
        activeModelDropdownContext = null;
    }
}

function showModelDropdown(chatId, titleElement) {
    closeAllModelDropdowns();

    const dropdownElement = components.createModelDropdown(chatId);
    if (!dropdownElement) return;

    titleElement.parentNode.insertBefore(dropdownElement, titleElement.nextSibling);
    requestAnimationFrame(() => dropdownElement.classList.add('show'));

    dropdownElement.querySelectorAll('.model-option').forEach(option => {
        option.onclick = (e) => {
            e.stopPropagation();
            const newModelId = option.getAttribute('data-model-id');
            service.changeAIModel(chatId, newModelId);
            closeAllModelDropdowns();
        };
    });

    const handleClickOutside = (event) => {
        if (!dropdownElement.contains(event.target) && event.target !== titleElement) {
            closeAllModelDropdowns();
        }
    };

    document.addEventListener('click', handleClickOutside, true);
    activeModelDropdownContext = { dropdownEl: dropdownElement, handler: handleClickOutside };
}
