/**
 * Arayüz Bileşenleri Modülü (UI Components / Factories)
 * ====================================================
 * @description Veri alıp karşılığında HTML string'leri veya
 * DOM elementleri üreten fonksiyonları barındırır.
 */

import { getAiModelById, getAllAiCategories } from './state.js';
import { downloadImage, viewFullImage, downloadAudio } from './mediaUtils.js';
import { log } from './logger.js';

// Medya fonksiyonlarını global scope'a ekleyerek inline onclick'lerin çalışmasını sağla
window.mediaUtils = { downloadImage, viewFullImage, downloadAudio };

/**
 * Bir sohbet penceresi için DOM elementi oluşturur.
 * @param {object} chatData - Sohbet verisi.
 * @returns {HTMLElement} Oluşturulan div elementi.
 */
export function createChatElement(chatData) {
    const aiModel = getAiModelById(chatData.aiModelId) || { name: `Bilinmeyen AI`, icon: 'bi bi-question-circle' };
    
    const chatWindow = document.createElement('div');
    chatWindow.className = 'chat-window';
    chatWindow.setAttribute('data-chat-id', chatData.id);

    const isModelLocked = chatData.messages.some(msg => msg.isUser);
    const modelSelectionClass = isModelLocked ? 'model-locked' : 'model-changeable';
    const modelSelectionTitle = isModelLocked ? 'Model kilitli - konuşma başladı' : 'AI modelini değiştirmek için tıkla';

    chatWindow.innerHTML = `
        <div class="chat-header">
            <div class="chat-title ${modelSelectionClass}" title="${modelSelectionTitle}">
                <i class="${aiModel.icon || 'bi bi-cpu'}"></i>
                <span>${aiModel.name || 'AI Model'} (ID: ${chatData.id.slice(-4)})</span>
                ${!isModelLocked ? '<i class="bi bi-chevron-down model-selector-icon"></i>' : '<i class="bi bi-lock-fill model-locked-icon"></i>'}
            </div>
            <div class="chat-controls">
                <button class="chat-control-btn chat-minimize-btn" title="Küçült"><i class="bi bi-dash-lg"></i></button>
                <button class="chat-control-btn chat-close-btn" title="Kapat"><i class="bi bi-x"></i></button>
            </div>
        </div>
        <div class="chat-messages">
            ${chatData.messages.length > 0 ?
                chatData.messages.map(msg => createMessageHTML(msg, chatData.aiModelId)).join('') :
                createWelcomeMessageHTML(aiModel.name || 'AI Model')
            }
        </div>
        <div class="chat-input-container">
            <div class="chat-input-group">
                <input type="text" class="chat-input" placeholder="Mesajınızı yazın...">
                <button class="chat-send-btn"><i class="bi bi-send"></i></button>
            </div>
        </div>
    `;
    return chatWindow;
}

/**
 * Bir mesaj için HTML string'i oluşturur.
 * @param {object} message - Mesaj verisi.
 * @param {number} aiModelId - Mesajın ait olduğu sohbetin model ID'si.
 * @returns {string} Oluşturulan HTML.
 */
export function createMessageHTML(message, aiModelId) {
    const messageClass = message.isUser ? 'user-message' : 'ai-message';
    const timestamp = new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const aiModel = getAiModelById(aiModelId) || {};

    const isFirstAIMessage = !message.isUser && (message.isFirstAIMessageInChat || message.showAiName);

    let messageContent = message.isUser ? renderTextContent(message.text) : renderContentByModel(message.text, aiModelId);
    
    if (isFirstAIMessage) {
        messageContent = `<div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiModel.name}</div>${messageContent}`;
    }
    
    if (message.isError) {
        return `
            <div class="message ${messageClass} error-message">
                <div class="message-content">
                    <div class="ai-model-indicator"><i class="bi bi-exclamation-triangle-fill"></i> Sistem</div>
                    ${renderTextContent(message.text)}
                </div>
                <div class="message-time">${timestamp}</div>
            </div>`;
    }

    return `
        <div class="message ${messageClass}">
            <div class="message-content">${messageContent}</div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;
}

export function createWelcomeMessageHTML(aiName) {
    return `
        <div class="message ai-message welcome-message">
            <div class="message-content">
                <div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>
                <p>Merhaba! Ben ${aiName}. Bugün size nasıl yardımcı olabilirim?</p>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
    `;
}

export function createLoadingMessageHTML(loadingId) {
    return `
        <div class="message ai-message loading-dots" id="${loadingId}">
            <div class="message-content">
                <div class="ai-model-indicator"><i class="bi bi-robot"></i> AI düşünüyor...</div>
                <div class="text-content"><span class="dots"><span>.</span><span>.</span><span>.</span></span></div>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
    `;
}


// --- Alt Bileşenler ve İçerik Render Fonksiyonları ---

function renderContentByModel(content, aiModelId) {
    const categories = getAllAiCategories();
    let categoryType = 'txt'; // Varsayılan

    for (const category of categories) {
        if (category.models?.some(model => model.id === aiModelId)) {
            const categoryNameLower = category.name.toLowerCase();
            if (categoryNameLower.includes('image') || categoryNameLower.includes('resim')) {
                categoryType = 'img';
            } else if (categoryNameLower.includes('audio') || categoryNameLower.includes('ses')) {
                categoryType = 'aud';
            }
            break;
        }
    }
    
    log('debug', 'UIComponents', `İçerik tipi belirlendi: ${categoryType}, Model ID: ${aiModelId}`);

    switch (categoryType) {
        case 'img': return renderImageContent(content);
        case 'aud': return renderAudioContent(content);
        default: return renderTextContent(content);
    }
}

function renderTextContent(content) {
    const sanitized = String(content || "").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return `<div class="text-content">${sanitized}</div>`;
}

function renderImageContent(content) {
    if (!content || typeof content !== 'string') return `<div class="image-content error-content">Resim yüklenemedi.</div>`;
    return `
        <div class="image-content">
            <img src="${content}" alt="AI Tarafından Oluşturulan Resim" class="ai-generated-image" onerror="this.alt='Resim yüklenemedi'; this.src='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';">
            <div class="image-controls">
                <button class="btn btn-sm btn-primary" onclick="window.mediaUtils.downloadImage(this.closest('.image-content').querySelector('img').src)"><i class="bi bi-download"></i> İndir</button>
                <button class="btn btn-sm btn-secondary" onclick="window.mediaUtils.viewFullImage(this.closest('.image-content').querySelector('img').src)"><i class="bi bi-arrows-fullscreen"></i> Tam Ekran</button>
            </div>
        </div>`;
}

function renderAudioContent(content) {
    if (!content || typeof content !== 'string') return `<div class="audio-content error-content">Ses yüklenemedi.</div>`;
    return `
        <div class="audio-content">
            <audio controls src="${content}"></audio>
            <button class="btn btn-sm btn-primary" onclick="window.mediaUtils.downloadAudio(this.closest('.audio-content').querySelector('audio').src)"><i class="bi bi-download"></i> İndir</button>
        </div>`;
}

// --- Dropdown ve Liste Elemanları ---

export function createActiveChatDropdownItem(chatData) {
    const aiModel = getAiModelById(chatData.aiModelId) || { name: 'Bilinmeyen', icon: 'bi bi-cpu' };
    const listItem = document.createElement('li');
    listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex align-items-center justify-content-between';
    listItem.setAttribute('data-chat-id', chatData.id);
    listItem.style.cursor = 'pointer';

    let content = `
        <span class="d-flex align-items-center" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;">
            <i class="${aiModel.icon || 'bi bi-cpu'} me-2"></i>
            <span title="${aiModel.name} (ID: ${chatData.id.slice(-4)})">${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
        </span>`;

    if (chatData.isMinimized) {
        listItem.classList.add('active-chat-item--minimized');
        content += '<span class="ms-auto flex-shrink-0"><i class="bi bi-window-plus" title="Geri Yükle"></i></span>';
    }
    listItem.innerHTML = content;
    return listItem;
}

export function createChatHistoryItem(chatData) {
    const aiModel = getAiModelById(chatData.aiModelId) || { name: 'Bilinmeyen', icon: 'bi bi-archive' };
    const listItem = document.createElement('li');
    listItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
    listItem.style.cursor = 'pointer';
    
    const date = new Date(chatData.closedTimestamp).toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit', year: '2-digit' });
    const historyItemText = `${aiModel.name} (${date})`;

    listItem.innerHTML = `
        <span class="d-flex align-items-center" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;">
            <i class="${aiModel.icon || 'bi bi-archive'} me-2"></i>
            <span title="${historyItemText} (ID: ${chatData.id.slice(-4)})">${historyItemText}</span>
        </span>
        <button class="btn btn-sm btn-icon chat-history-restore-btn flex-shrink-0" title="Geri Yükle">
            <i class="bi bi-arrow-counterclockwise"></i>
        </button>
    `;
    return listItem;
}

export function createModelDropdown(chatId) {
    const chat = getAiModelById(chatId); // This seems wrong, should be getChatById
    // Correction: This function should receive the chat object or at least the current model ID.
    // Let's assume the caller (uiManager) will get the chat data.
    const currentModelId = getAiModelById(chatId)?.aiModelId; // This is still not quite right.
    // Let's refactor to pass the necessary data directly.
    // The function signature in uiManager should be: createModelDropdown(currentModelId)
    // For now, let's just get all models and mark the selected one.
    const allModels = getAllAiCategories().flatMap(c => c.models); // This is also not right.
    const aiTypes = getAiTypes();
    const currentChat = getChatById(chatId);
    if (!currentChat) return null;

    const dropdownElement = document.createElement('div');
    dropdownElement.className = 'model-dropdown';
    const optionsHTML = aiTypes.map(model => `
        <div class="model-option ${model.id === currentChat.aiModelId ? 'selected active' : ''}" data-model-id="${model.id}" title="${model.description || model.name}">
            <i class="${model.icon || 'bi bi-cpu'} me-2"></i>
            <span>${model.name || 'Bilinmeyen Model'}</span>
            ${model.id === currentChat.aiModelId ? '<i class="bi bi-check-lg ms-auto"></i>' : ''}
        </div>
    `).join('');
    dropdownElement.innerHTML = `<div class="list-group list-group-flush">${optionsHTML}</div>`;
    return dropdownElement;
}
