/**
 * ZekAI Sohbet Bileşeni Modülü
 * ===========================
 * @description AI sohbet pencerelerini, düzenlerini ve kullanıcı etkileşimlerini yönetir
 * @version 1.0.3 (Kategori ID bazlı içerik renderlama ve AI ID ile belirleme)
 * @author ZekAI Team
 *
 * İÇİNDEKİLER
 * ================
 * 1. TEMEL SİSTEM (CORE SYSTEM)
 * 1.1. Gelişmiş Günlükleme Sistemi (Advanced Logging System)
 * 1.2. Durum Yönetimi (State Management)
 * 1.3. DOM Elementleri (DOM Elements)
 * 1.4. Global Hata Yakalayıcı (Global Error Handler)
 *
 * 2. KULLANICI ARAYÜZÜ BİLEŞENLERİ (UI COMPONENTS)
 * 2.1. Sohbet Elementi Fabrikaları (Chat Element Factories)
 * 2.2. Mesaj HTML Üreteçleri (Message HTML Generators)
 * 2.3. İçerik Oluşturucuları (Content Renderers - Text, Image, Audio) - Kategori ID'ye göre güncellendi
 *
 * 3. OLUŞTURMA FONKSİYONLARI (RENDERING FUNCTIONS)
 * 3.1. Sohbet Pencereleri (Chat Windows)
 * 3.2. Aktif Sohbetler Açılır Menüsü (Active Chats Dropdown)
 * 3.3. Sohbet Geçmişi (Chat History)
 *
 * 4. OLAY İŞLEYİCİLERİ (EVENT HANDLERS)
 * 4.1. Sohbet Penceresi Kontrolleri (Chat Window Controls)
 * 4.2. Global Kontroller (Global Handlers)
 *
 * 5. SOHBET OPERASYONLARI (CHAT OPERATIONS)
 * 5.1. Sohbet Yönetimi (Chat Management - Ekle/Kaldır/Temizle)
 * 5.2. Mesajlaşma Sistemi (Messaging System)
 * 5.3. Yayın Mesajları (Broadcast Messages)
 *
 * 6. AI MODEL YÖNETİMİ (AI MODEL MANAGEMENT)
 * 6.1. Model Seçimi Arayüzü (Model Selection UI)
 * 6.2. Model Değiştirme Mantığı (Model Changing Logic)
 *
 * 7. MEDYA İŞLEMLERİ (MEDIA HANDLING)
 * 7.1. Resim İşlemleri (Image Handling)
 * 7.2. Ses İşlemleri (Audio Handling)
 *
 * 8. GENEL API VE BAŞLATMA (PUBLIC API & INITIALIZATION)
 * 8.1. Başlatma Fonksiyonu (Initialization Function)
 * 8.2. Açığa Çıkarılan Metotlar (Exposed Methods)
 * 8.3. DOM Hazır Olduğunda Başlatma (DOM Ready Initialization)
 */

//=============================================================================
// ChatManager Modülü (IIFE)
//=============================================================================
const ChatManager = (function() {
    'use strict'; // Strict modu etkinleştir

    //=============================================================================
    // 1. TEMEL SİSTEM (CORE SYSTEM)
    //=============================================================================

    /**
     * 1.1. Gelişmiş Günlükleme Sistemi
     */
    window.DEBUG_LOG_ACTIVE = true;
    window.ACTIVE_LOG_LEVEL = 'debug';

    const LOG_LEVELS = {
        debug:  { priority: 0, color: 'color:#9E9E9E;', prefix: 'DEBUG' },
        info:   { priority: 1, color: 'color:#2196F3;', prefix: 'INFO ' },
        action: { priority: 2, color: 'color:#4CAF50;', prefix: 'ACTION'},
        warn:   { priority: 3, color: 'color:#FFC107;', prefix: 'WARN ' },
        error:  { priority: 4, color: 'color:#F44336;', prefix: 'ERROR'}
    };

    function log(level, context, message, ...details) {
        if (!window.DEBUG_LOG_ACTIVE) return;
        const levelConfig = LOG_LEVELS[level] || LOG_LEVELS['info'];
        const activeLevelConfig = LOG_LEVELS[window.ACTIVE_LOG_LEVEL] || LOG_LEVELS['debug'];
        if (levelConfig.priority < activeLevelConfig.priority) return;

        const timestamp = new Date().toISOString().substr(11, 12);
        const logPrefix = `%c[${timestamp}] [${levelConfig.prefix}] [${context}]`;
        const hasObjects = details.some(arg => typeof arg === 'object' && arg !== null);

        if (details.length > 0) {
            if (hasObjects || message.length > 50 || details.length > 1) {
                console.groupCollapsed(logPrefix, levelConfig.color, message);
                details.forEach(detail => console.dir(detail) || console.log(detail));
                console.groupEnd();
            } else {
                console.log(logPrefix, levelConfig.color, message, ...details);
            }
        } else {
            console.log(logPrefix, levelConfig.color, message);
        }
    }

    /**
     * 1.2. Durum Yönetimi
     */
    const state = {
        chats: [],
        chatHistory: [],
        maxChats: 6
    };

    if (window.state) {
        log('warn', 'CoreSystem:StateInit', 'Mevcut window.state algılandı. Birleştiriliyor...');
        if (!window.state.chats) window.state.chats = state.chats;
        if (!window.state.chatHistory) window.state.chatHistory = state.chatHistory;
        if (!window.state.aiTypes) window.state.aiTypes = [];
        if (!window.state.allAiCategories) window.state.allAiCategories = [];
    } else {
        window.state = {
            chats: state.chats,
            chatHistory: state.chatHistory,
            aiTypes: [],
            allAiCategories: [] // Bu, index.html tarafından doldurulacak
        };
        log('info', 'CoreSystem:StateInit', 'Yeni window.state oluşturuldu.');
    }
    log('debug', 'CoreSystem:StateInit', 'Başlangıç durumu:', JSON.parse(JSON.stringify(window.state)));

    /**
     * 1.3. DOM Elementleri
     */
    let elements = {};

    function initElements() {
        log('info', 'CoreSystem:DOMInit', 'DOM elementleri başlatılıyor...');
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
            chatHistoryList: document.getElementById('chat-history-list'),
        };
        const missingElements = Object.keys(elements).filter(key => !elements[key]);
        if (missingElements.length > 0) {
            log('error', 'CoreSystem:DOMInit', `Kritik DOM elementleri bulunamadı: ${missingElements.join(', ')}`);
            return false;
        }
        log('info', 'CoreSystem:DOMInit', 'Tüm DOM elementleri başarıyla bulundu.');
        return true;
    }

    /**
     * 1.4. Global Hata Yakalayıcı
     */
    window.onerror = function(message, source, lineno, colno, error) {
        log('error', 'GlobalErrorHandler', 'Yakalanmamış bir hata oluştu!', { message, source, lineno, colno, errorObject: error ? JSON.parse(JSON.stringify(error, Object.getOwnPropertyNames(error))) : 'N/A' });
        return false;
    };
    window.onunhandledrejection = function(event) {
        log('error', 'GlobalPromiseRejection', 'İşlenmemiş Promise reddi!', { reason: event.reason ? (typeof event.reason === 'object' ? JSON.parse(JSON.stringify(event.reason, Object.getOwnPropertyNames(event.reason))) : event.reason) : 'N/A', promise: event.promise });
    };

    //=============================================================================
    // 2. KULLANICI ARAYÜZÜ BİLEŞENLERİ (UI COMPONENTS)
    //=============================================================================

    /**
     * 2.1. Sohbet Elementi Fabrikaları
     */
    function createChatElement(chatData) {
        log('debug', 'UI:CreateChat', 'Sohbet elementi oluşturuluyor...', chatData);
        try {
            // window.state.aiTypes'daki id'nin, veritabanındaki ai_models.id olduğunu varsayıyoruz (index.html'deki değişikliklerle)
            const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) ||
                            (window.state.aiTypes && window.state.aiTypes.length > 0 ? window.state.aiTypes[0] : null) ||
                            { name: `Bilinmeyen AI (ID: ${chatData.aiModelId})`, icon: 'bi bi-question-circle' };

            if (!aiModel) {
                log('warn', 'UI:CreateChat', `AI modeli bulunamadı: ${chatData.aiModelId}. Varsayılan kullanılıyor.`);
            }

            const chatWindow = document.createElement('div');
            chatWindow.className = 'chat-window';
            chatWindow.setAttribute('data-chat-id', chatData.id);

            const isModelLocked = chatData.messages && chatData.messages.some(msg => msg.isUser);
            const modelSelectionClass = isModelLocked ? 'model-locked' : 'model-changeable';
            const modelSelectionTitle = isModelLocked ? 'Model kilitli - konuşma zaten başladı' : 'AI modelini değiştirmek için tıklayın';

            chatWindow.innerHTML = `
                <div class="chat-header">
                    <div class="chat-title ${modelSelectionClass}" title="${modelSelectionTitle}">
                        <i class="${aiModel.icon || 'bi bi-cpu'}"></i>
                        <span>${aiModel.name || 'AI Model'} (ID: ${chatData.id.slice(-4)})</span>
                        ${!isModelLocked ? '<i class="bi bi-chevron-down model-selector-icon"></i>' :
                                          '<i class="bi bi-lock-fill model-locked-icon"></i>'}
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
                    ${chatData.messages && chatData.messages.length > 0 ?
                        chatData.messages.map(msg => createMessageHTML(msg, !msg.isUser && chatData.messages.filter(m => !m.isUser).indexOf(msg) === 0, aiModel.name, chatData.aiModelId)).join('') :
                        createWelcomeMessageHTML(aiModel.name || 'AI Model')
                    }
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
            log('info', 'UI:CreateChat', `Sohbet elementi başarıyla oluşturuldu: ${chatData.id}`);
            return chatWindow;
        } catch (error) {
            log('error', 'UI:CreateChat', 'Sohbet elementi oluşturulurken hata oluştu!', error, chatData);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chat-window chat-window-error';
            errorDiv.textContent = 'Sohbet yüklenirken bir hata oluştu.';
            errorDiv.setAttribute('data-chat-id', chatData.id);
            return errorDiv;
        }
    }

    /**
     * 2.2. Mesaj HTML Üreteçleri
     */
    function createMessageHTML(message, isFirstAIMessage = false, aiName = '', aiModelId = '') {
        try {
            const messageClass = message.isUser ? 'user-message' : 'ai-message';
            const timestamp = new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // aiModelId (artık DB model ID'si) renderContent'e gönderiliyor
            let messageContent = message.isUser ? renderTextContent(message.text) : renderContent(message.text, aiModelId);

            if (!message.isUser && aiName && (isFirstAIMessage || message.showAiName)) {
                messageContent = `<div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>${messageContent}`;
            }
            
            if (message.isError) {
                 return `
                    <div class="message ${messageClass} error-message">
                        <div class="message-content">
                             <div class="ai-model-indicator"><i class="bi bi-exclamation-triangle-fill"></i> Sistem</div>
                            ${renderTextContent(message.text)}
                        </div>
                        <div class="message-time">${timestamp}</div>
                    </div>
                `;
            }

            return `
                <div class="message ${messageClass}">
                    <div class="message-content">
                        ${messageContent}
                    </div>
                    <div class="message-time">${timestamp}</div>
                </div>
            `;
        } catch (error) {
            log('error', 'UI:CreateMsgHTML', 'Mesaj HTML oluşturulurken hata!', error, { message });
            return `<div class="message error-message"><div class="message-content">Mesaj görüntülenemedi.</div></div>`;
        }
    }

    function createWelcomeMessageHTML(aiName) {
        return `
            <div class="message ai-message">
                <div class="message-content">
                    <div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>
                    <p>Merhaba! Ben ${aiName}. Bugün size nasıl yardımcı olabilirim?</p>
                </div>
                <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
    }

    /**
     * 2.3. İçerik Oluşturucuları (Content Renderers) - Kategori ID'ye göre güncellendi
     * aiModelIdFromChatState: Bu, chat.aiModelId'dir ve artık ai_models.id (veritabanı birincil anahtarı) olmalıdır.
     */
    function renderContent(content, aiModelIdFromChatState) {
        let categoryType = 'txt'; // Varsayılan metin
        let categoryOfModel = null;

        if (window.state && window.state.allAiCategories) {
            outerLoop:
            for (const category of window.state.allAiCategories) {
                if (category.models && Array.isArray(category.models)) {
                    for (const modelInLoop of category.models) {
                        // modelInLoop.id, ai_models tablosundaki birincil anahtardır.
                        // aiModelIdFromChatState'in de bu ID olduğunu varsayıyoruz.
                        if (modelInLoop.id === aiModelIdFromChatState) {
                            categoryOfModel = category;
                            const categoryNameLower = category.name.toLowerCase();
                            // Kategori adına göre tipi belirle
                            if (categoryNameLower.includes('image') || categoryNameLower.includes('resim')) {
                                categoryType = 'img';
                            } else if (categoryNameLower.includes('audio') || categoryNameLower.includes('ses')) {
                                categoryType = 'aud';
                            } else {
                                categoryType = 'txt';
                            }
                            log('debug', 'UI:RenderContent', `Model ID ${aiModelIdFromChatState} kategori '${category.name}' (Kategori ID: ${category.id}) içinde bulundu. Belirlenen tip: ${categoryType}`);
                            break outerLoop;
                        }
                    }
                }
            }
            if (!categoryOfModel) {
                log('warn', 'UI:RenderContent', `Model ID ${aiModelIdFromChatState} hiçbir kategoride bulunamadı (window.state.allAiCategories). Varsayılan tip 'txt' olarak ayarlandı.`);
            }
        } else {
            log('warn', 'UI:RenderContent', 'window.state.allAiCategories mevcut değil. Varsayılan tip "txt" olarak ayarlandı.');
        }

        log('debug', 'UI:RenderContent', `Son kategori tipi: ${categoryType}, Model ID: ${aiModelIdFromChatState} için`);

        switch (categoryType) {
            case 'img':
                return renderImageContent(content);
            case 'aud':
                return renderAudioContent(content);
            case 'txt':
            default:
                return renderTextContent(content);
        }
    }

    function renderTextContent(content) {
        const sanitizedContent = String(content || "").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        return `<div class="text-content">${sanitizedContent}</div>`;
    }

    function renderImageContent(content) {
        if (!content || typeof content !== 'string') {
            log('warn', 'UI:RenderImage', 'Geçersiz resim içeriği sağlandı.', content);
            return `<div class="image-content error-content">Resim yüklenemedi (geçersiz veri).</div>`;
        }
        return `
            <div class="image-content">
                <img src="${content}" alt="AI Tarafından Oluşturulan Resim" class="ai-generated-image" onerror="this.alt='Resim yüklenemedi'; this.src='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; console.error('Resim yükleme hatası:', this.src);">
                <div class="image-controls">
                    <button class="btn btn-sm btn-primary download-image" onclick="ChatManager.downloadImage(this.closest('.image-content').querySelector('img').src)"><i class="bi bi-download"></i> İndir</button>
                    <button class="btn btn-sm btn-secondary view-image" onclick="ChatManager.viewFullImage(this.closest('.image-content').querySelector('img').src)"><i class="bi bi-arrows-fullscreen"></i> Tam Ekran</button>
                </div>
            </div>
        `;
    }

    function renderAudioContent(content) {
         if (!content || typeof content !== 'string') {
            log('warn', 'UI:RenderAudio', 'Geçersiz ses içeriği sağlandı.', content);
            return `<div class="audio-content error-content">Ses yüklenemedi (geçersiz veri).</div>`;
        }
        return `
            <div class="audio-content">
                <audio controls src="${content}" onerror="this.closest('.audio-content').innerHTML = '<p>Ses dosyası yüklenemedi.</p>'; console.error('Ses yükleme hatası:', this.src);">
                    Tarayıcınız ses elementini desteklemiyor.
                </audio>
                <button class="btn btn-sm btn-primary download-audio" onclick="ChatManager.downloadAudio(this.closest('.audio-content').querySelector('audio').src)"><i class="bi bi-download"></i> İndir</button>
            </div>
        `;
    }

    //=============================================================================
    // 3. OLUŞTURMA FONKSİYONLARI (RENDERING FUNCTIONS)
    //=============================================================================

    function renderChats() {
        log('debug', 'Render:Chats', 'Sohbetler oluşturuluyor. Aktif (küçültülmemiş) sohbet sayısı:', state.chats.filter(c => !c.isMinimized).length, 'Toplam sohbet:', state.chats.length);
        if (!elements.chatContainer) {
            log('error', 'Render:Chats', 'Sohbetler oluşturulamıyor: sohbet konteyneri bulunamadı.');
            return;
        }
        try {
            elements.chatContainer.innerHTML = '';
            const activeVisibleChats = state.chats.filter(chat => !chat.isMinimized);
            if (activeVisibleChats.length === 0) {
                if (elements.welcomeScreen && elements.welcomeScreen.parentNode !== elements.chatContainer) {
                     elements.chatContainer.appendChild(elements.welcomeScreen);
                }
                elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap justify-content-center align-items-center';
                log('info', 'Render:Chats', 'Aktif sohbet yok, karşılama ekranı gösteriliyor.');
            } else {
                if (elements.welcomeScreen && elements.welcomeScreen.parentNode === elements.chatContainer) {
                    elements.chatContainer.removeChild(elements.welcomeScreen);
                }
                let layoutClass;
                switch (activeVisibleChats.length) {
                    case 1: layoutClass = 'layout-1'; break;
                    case 2: layoutClass = 'layout-2'; break;
                    case 3: layoutClass = 'layout-3'; break;
                    case 4: layoutClass = 'layout-4'; break;
                    case 5: layoutClass = 'layout-5'; break;
                    case 6: layoutClass = 'layout-6'; break;
                    default: layoutClass = 'layout-6'; break;
                }
                elements.chatContainer.className = `flex-grow-1 d-flex flex-wrap ${layoutClass}`;
                activeVisibleChats.forEach(chatData => {
                    const chatElement = createChatElement(chatData);
                    elements.chatContainer.appendChild(chatElement);
                    setupChatWindowControls(chatElement);
                });
                log('info', 'Render:Chats', `${activeVisibleChats.length} sohbet penceresi oluşturuldu. Düzen: ${layoutClass}`);
            }
        } catch (error) {
            log('error', 'Render:Chats', 'Sohbetleri oluştururken genel bir hata oluştu!', error);
            elements.chatContainer.innerHTML = '<div class="alert alert-danger m-3">Sohbetler yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.</div>';
        } finally {
            renderActiveChatsDropdown();
        }
    }

    function renderActiveChatsDropdown() {
        if (!elements.activeChatsList || !elements.activeChatsDropdownMenu || !elements.activeChatsDropdownTrigger) {
            log('warn', 'Render:Dropdown', 'Aktif sohbetler açılır menü elementleri bulunamadı, işlem atlanıyor.');
            return;
        }
        try {
            elements.activeChatsList.innerHTML = '';
            if (state.chats.length === 0) {
                elements.activeChatsDropdownTrigger.classList.add('disabled');
                const noChatsLi = document.createElement('li');
                noChatsLi.className = 'list-group-item text-muted';
                noChatsLi.textContent = 'Aktif sohbet yok';
                elements.activeChatsList.appendChild(noChatsLi);
                return;
            }
            elements.activeChatsDropdownTrigger.classList.remove('disabled');
            state.chats.forEach(chatData => {
                const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) || { name: `AI (${chatData.aiModelId ? String(chatData.aiModelId).slice(-4) : 'Bilinmeyen'})`, icon: 'bi bi-cpu' };
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex align-items-center justify-content-between';
                listItem.setAttribute('data-chat-id', chatData.id);
                listItem.style.cursor = 'pointer';

                if (chatData.messages && chatData.messages.some(msg => msg.isUser)) {
                    listItem.classList.add('active-chat-item--started');
                }
                let chatNameHTML = `
                    <span class="d-flex align-items-center" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;">
                        <i class="${aiModel.icon || 'bi bi-cpu'} me-2"></i>
                        <span title="${aiModel.name} (ID: ${chatData.id.slice(-4)})">${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
                    </span>`;
                if (chatData.isMinimized) {
                    listItem.classList.add('active-chat-item--minimized');
                    listItem.innerHTML = chatNameHTML + '<span class="ms-auto flex-shrink-0"><i class="bi bi-window-plus" title="Sohbeti Geri Yükle"></i></span>';
                    listItem.onclick = (e) => {
                        e.stopPropagation();
                        const chatToRestore = state.chats.find(c => c.id === chatData.id);
                        if (chatToRestore) { chatToRestore.isMinimized = false; renderChats(); }
                    };
                } else {
                    listItem.innerHTML = chatNameHTML;
                    listItem.onclick = () => {
                        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                        if (chatWindow) {
                            chatWindow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            chatWindow.classList.add('chat-window--highlighted');
                            setTimeout(() => chatWindow.classList.remove('chat-window--highlighted'), 2000);
                        }
                    };
                }
                elements.activeChatsList.appendChild(listItem);
            });
        } catch (error) {
            log('error', 'Render:Dropdown', 'Aktif sohbetler açılır menüsü oluşturulurken hata!', error);
            if (elements.activeChatsList) elements.activeChatsList.innerHTML = '<li class="list-group-item text-danger">Liste yüklenemedi.</li>';
        }
    }

    function renderChatHistory() {
        if (!elements.chatHistoryList || !elements.chatHistoryTrigger || !elements.chatHistoryMenu) {
            log('warn', 'Render:History', 'Sohbet geçmişi elementleri DOM\'da bulunamadı, işlem atlanıyor.');
            return;
        }
        try {
            elements.chatHistoryList.innerHTML = '';
            if (state.chatHistory.length === 0) {
                elements.chatHistoryTrigger.classList.add('disabled');
                const noHistoryLi = document.createElement('li');
                noHistoryLi.className = 'list-group-item text-muted';
                noHistoryLi.textContent = 'Sohbet geçmişi yok';
                elements.chatHistoryList.appendChild(noHistoryLi);
                return;
            }
            elements.chatHistoryTrigger.classList.remove('disabled');
            state.chatHistory.forEach(chat => {
                const aiModelInfo = window.state.aiTypes.find(ai => ai.id === chat.aiModelId) || { name: 'Bilinmeyen AI', icon: 'bi bi-archive' };
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex justify-content-between align-items-center';
                listItem.setAttribute('data-chat-id', chat.id);
                listItem.style.cursor = 'pointer';

                const nameContainerSpan = document.createElement('span');
                nameContainerSpan.className = 'd-flex align-items-center';
                nameContainerSpan.style.cssText = 'overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;';
                const iconElement = document.createElement('i');
                iconElement.className = `${aiModelInfo.icon || 'bi bi-archive'} me-2`;
                const nameSpanElement = document.createElement('span');
                let historyItemText = aiModelInfo.name || 'Geçmiş Sohbet';
                if (chat.closedTimestamp) {
                    const date = new Date(chat.closedTimestamp);
                    historyItemText += ` (${date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: '2-digit' })})`;
                }
                nameSpanElement.textContent = historyItemText;
                nameSpanElement.title = historyItemText + ` (ID: ${chat.id.slice(-4)})`;
                nameContainerSpan.append(iconElement, nameSpanElement);
                listItem.appendChild(nameContainerSpan);

                const restoreButton = document.createElement('button');
                restoreButton.className = 'btn btn-sm btn-icon chat-history-restore-btn flex-shrink-0';
                restoreButton.title = 'Sohbeti Geri Yükle';
                restoreButton.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i>';
                restoreButton.onclick = (event) => {
                    event.stopPropagation();
                    log('action', 'Render:History', `Geçmişten sohbeti geri yükle tıklandı: ${chat.id}`);
                    alert('Geçmişten sohbeti geri yükleme henüz tam olarak uygulanmadı.');
                    log('info', 'Render:History', 'Geri yüklenecek sohbet verisi:', chat);
                };
                listItem.appendChild(restoreButton);
                listItem.onclick = () => {
                    log('action', 'Render:History', `Sohbet geçmişi öğesi tıklandı: ${chat.id}`);
                    alert(`'${historyItemText}' sohbetinin geçmişini görüntüleme henüz uygulanmadı.`);
                    log('info', 'Render:History', `Görüntülenecek geçmiş sohbet mesajları (${chat.id}):`, chat.messages);
                };
                elements.chatHistoryList.appendChild(listItem);
            });
        } catch (error) {
            log('error', 'Render:History', 'Sohbet geçmişi oluşturulurken hata!', error);
             if (elements.chatHistoryList) elements.chatHistoryList.innerHTML = '<li class="list-group-item text-danger">Geçmiş yüklenemedi.</li>';
        }
    }

    //=============================================================================
    // 4. OLAY İŞLEYİCİLERİ (EVENT HANDLERS)
    //=============================================================================

    function setupChatWindowControls(chatElement) {
        if (!chatElement) return log('error', 'Events:ChatCtrl', 'Sohbet kontrolleri ayarlanamıyor: sohbet elementi null.');
        const chatId = chatElement.getAttribute('data-chat-id');
        if (!chatId) return log('error', 'Events:ChatCtrl', 'Sohbet kontrolleri ayarlanamıyor: chat ID eksik.', chatElement);

        try {
            const closeBtn = chatElement.querySelector('.chat-close-btn');
            if (closeBtn) closeBtn.onclick = (e) => {
                e.stopPropagation();
                const chatData = state.chats.find(c => c.id === chatId);
                if (chatData && chatData.messages && chatData.messages.some(msg => msg.isUser)) {
                    if (confirm("Bu sohbeti kapatmak istediğinizden emin misiniz? Konuşma geçmişe kaydedilecek.")) removeChat(chatId);
                } else removeChat(chatId);
            };
            const minimizeBtn = chatElement.querySelector('.chat-minimize-btn');
            if (minimizeBtn) minimizeBtn.onclick = (e) => {
                e.stopPropagation();
                const chat = state.chats.find(c => c.id === chatId);
                if (chat) { chat.isMinimized = true; renderChats(); }
            };
            const chatTitle = chatElement.querySelector('.chat-title');
            if (chatTitle && chatTitle.classList.contains('model-changeable')) {
                chatTitle.onclick = (e) => { e.stopPropagation(); showModelDropdown(chatId, chatTitle); };
            }
            const sendBtn = chatElement.querySelector('.chat-send-btn');
            const inputField = chatElement.querySelector('.chat-input');
            if (sendBtn && inputField) {
                const sendMessageHandler = () => {
                    const messageText = inputField.value.trim();
                    if (messageText) { sendMessage(chatId, messageText); inputField.value = ''; inputField.focus(); }
                };
                sendBtn.onclick = sendMessageHandler;
                inputField.onkeypress = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessageHandler(); } };
            }
        } catch (error) {
            log('error', 'Events:ChatCtrl', `Sohbet penceresi (${chatId}) kontrolleri ayarlanırken hata!`, error);
        }
    }

    function setupGlobalHandlers() {
        log('info', 'Events:Global', 'Global olay işleyicileri ayarlanıyor...');
        try {
            if(elements.welcomeNewChatBtn) elements.welcomeNewChatBtn.onclick = () => addChat();
            if(elements.newChatBtn) elements.newChatBtn.onclick = () => addChat();
            if(elements.clearChatsBtn) elements.clearChatsBtn.onclick = () => {
                const startedChatsCount = state.chats.filter(chat => chat.messages && chat.messages.some(msg => msg.isUser)).length;
                const unstartedChatsCount = state.chats.length - startedChatsCount;
                if (unstartedChatsCount > 0) {
                    if (confirm(`${unstartedChatsCount} adet henüz başlanmamış sohbeti kapatmak istediğinizden emin misiniz?`)) clearAllChats(false);
                } else if (state.chats.length > 0) {
                     if (confirm(`Tüm (${state.chats.length}) sohbetleri kapatmak ve geçmişe taşımak istediğinizden emin misiniz?`)) clearAllChats(true);
                } else alert('Temizlenecek sohbet yok.');
            };
            if (elements.sendBroadcastBtn && elements.broadcastMessageInput) {
                const broadcastHandler = () => sendBroadcastMessage();
                elements.sendBroadcastBtn.addEventListener('click', broadcastHandler);
                elements.broadcastMessageInput.addEventListener('keypress', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); broadcastHandler(); }});
            }
            log('info', 'Events:Global', 'Global olay işleyicileri başarıyla ayarlandı.');
        } catch (error) {
            log('error', 'Events:Global', 'Global olay işleyicileri ayarlanırken hata!', error);
        }
    }

    //=============================================================================
    // 5. SOHBET OPERASYONLARI (CHAT OPERATIONS)
    //=============================================================================

    function addChat(aiModelIdFromDataset, initialMessages = []) { // Parametre adını daha açıklayıcı yaptım
        log('action', 'ChatOps:Add', 'Yeni sohbet ekleme denemesi...', { requestedModelId: aiModelIdFromDataset });
        if (!elements.chatContainer) {
            log('error', 'ChatOps:Add', 'Sohbet konteyneri bulunamadı.');
            alert('Hata: Sohbet arayüzü doğru yüklenemedi.');
            return null;
        }
        const activeVisibleChatCount = state.chats.filter(c => !c.isMinimized).length;
        if (activeVisibleChatCount >= state.maxChats) {
            alert(`Maksimum ${state.maxChats} sohbet paneline ulaşıldı.`);
            return null;
        }

        let finalAiModelIdNumeric; // Kullanılacak ID'yi saklayacak, sayı olmalı

        // aiModelIdFromDataset'in tanımlı ve null olmadığını kontrol et
        if (typeof aiModelIdFromDataset !== 'undefined' && aiModelIdFromDataset !== null && aiModelIdFromDataset !== '') {
            const numericRequestedId = Number(aiModelIdFromDataset); // Metinden sayıya dönüştür
            
            // window.state.aiTypes içindeki id'lerin sayı olduğunu varsayıyoruz
            const modelExists = window.state.aiTypes.some(m => m.id === numericRequestedId);

            if (modelExists) {
                finalAiModelIdNumeric = numericRequestedId;
            } else {
                log('warn', 'ChatOps:Add', `Sağlanan AI Model ID "${aiModelIdFromDataset}" (dönüştürülmüş: ${numericRequestedId}) geçerli değil. İlk AI modeline dönülüyor.`);
                if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                    finalAiModelIdNumeric = window.state.aiTypes[0].id; // Varsayılan modelin ID'si (sayı)
                } else {
                    log('error', 'ChatOps:Add', 'Geçersiz AI Model ID ve alternatif model yok.');
                    alert('Sohbet oluşturulamıyor: Model bulunamadı.');
                    return null;
                }
            }
        } else { // aiModelIdFromDataset sağlanmadıysa, varsayılanı kullan
            if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                finalAiModelIdNumeric = window.state.aiTypes[0].id; // Varsayılan modelin ID'si (sayı)
            } else {
                log('error', 'ChatOps:Add', 'Varsayılan AI modeli bulunamadı.');
                alert('Sohbet oluşturulamıyor: Kullanılabilir AI modelleri yok.');
                return null;
            }
        }
        
        const newChat = {
            id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            aiModelId: finalAiModelIdNumeric, // Artık tutarlı bir şekilde sayı
            messages: [...initialMessages],
            createdAt: Date.now(),
            lastActivity: Date.now(),
            isMinimized: false,
        };
        state.chats.push(newChat);
        renderChats();
        const newChatElement = elements.chatContainer.querySelector(`.chat-window[data-chat-id="${newChat.id}"]:not([style*="display: none"])`);
        if (newChatElement) {
            const inputField = newChatElement.querySelector('.chat-input');
            if (inputField) setTimeout(() => inputField.focus(), 0);
        }
        log('info', 'ChatOps:Add', `Yeni sohbet başarıyla eklendi. ID: ${newChat.id}, AI Model ID (Sayısal): ${finalAiModelIdNumeric}`);
        return newChat.id;
    }

    function removeChat(chatId, bypassHistory = false) {
        log('action', 'ChatOps:Remove', `Sohbet kaldırma: ${chatId}`, { bypassHistory });
        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        const performActualRemove = () => {
            const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
            if (chatIndex !== -1) {
                const chatToRemove = state.chats[chatIndex];
                const hasUserMessages = chatToRemove.messages && chatToRemove.messages.some(msg => msg.isUser);
                if (!bypassHistory && hasUserMessages) {
                    chatToRemove.closedTimestamp = Date.now();
                    if (!Array.isArray(state.chatHistory)) state.chatHistory = [];
                    state.chatHistory.unshift(chatToRemove);
                    renderChatHistory();
                }
                state.chats.splice(chatIndex, 1);
                if (chatWindow && chatWindow.parentNode) chatWindow.parentNode.removeChild(chatWindow);
                renderChats();
            }
        };
        if (chatWindow) {
            chatWindow.classList.add('closing');
            const onAnimationEnd = () => { chatWindow.removeEventListener('animationend', onAnimationEnd); performActualRemove(); };
            chatWindow.addEventListener('animationend', onAnimationEnd);
            setTimeout(() => { if (chatWindow.classList.contains('closing')) performActualRemove(); }, 700);
        } else {
            performActualRemove();
        }
    }

    function clearAllChats(includeStartedChats = false) {
        const initialChatCount = state.chats.length;
        if (initialChatCount === 0) return alert('Temizlenecek aktif sohbet bulunmuyor.');
        const chatsToRemove = state.chats
            .filter(chat => includeStartedChats || !(chat.messages && chat.messages.some(msg => msg.isUser)))
            .map(chat => chat.id);
        if (chatsToRemove.length === 0) return alert(includeStartedChats ? 'Tüm sohbetler temiz.' : 'Temizlenecek kullanılmayan sohbet yok.');
        chatsToRemove.forEach(chatId => removeChat(chatId, !includeStartedChats));
        const chatsRemovedCount = initialChatCount - state.chats.length;
        if (chatsRemovedCount > 0) alert(`${chatsRemovedCount} sohbet temizlendi.`);
    }

    /**
     * 5.2. Mesajlaşma Sistemi
     */
    async function sendMessage(chatId, text) {
        log('action', 'ChatOps:SendMsg', `Mesaj gönderiliyor: Chat ID ${chatId}`);
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) return log('error', 'ChatOps:SendMsg', `Sohbet bulunamadı: ${chatId}.`);

        const userMessage = { isUser: true, text: text, timestamp: Date.now() };
        chat.messages.push(userMessage);
        chat.lastActivity = Date.now();
        const isUsersFirstMessageInChat = chat.messages.filter(m => m.isUser).length === 1;

        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        let messagesContainer;
        if (chatElement) {
            messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer) {
                const userMessageHTML = createMessageHTML(userMessage, false, '', chat.aiModelId);
                messagesContainer.insertAdjacentHTML('beforeend', userMessageHTML);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                if (isUsersFirstMessageInChat) {
                    const chatTitle = chatElement.querySelector('.chat-title');
                    if (chatTitle) {
                        chatTitle.classList.remove('model-changeable');
                        chatTitle.classList.add('model-locked');
                        chatTitle.title = 'Model kilitli';
                        const selectorIcon = chatTitle.querySelector('.model-selector-icon');
                        if (selectorIcon) {
                            const lockIcon = document.createElement('i');
                            lockIcon.className = 'bi bi-lock-fill model-locked-icon';
                            chatTitle.replaceChild(lockIcon, selectorIcon);
                        }
                        chatTitle.onclick = null;
                    }
                    renderActiveChatsDropdown();
                }
            }
        }

        let loadingElement = null;
        const aiModelForLoading = window.state.aiTypes.find(m => m.id === chat.aiModelId);
        const currentAiNameForLoading = aiModelForLoading ? aiModelForLoading.name : 'AI';
        const isFirstAIMessageOverall = chat.messages.filter(m => !m.isUser).length === 0;

        if (messagesContainer) {
            const loadingMessageData = { isUser: false, text: '', timestamp: Date.now() };
            const loadingMessageHTML = createMessageHTML(loadingMessageData, isFirstAIMessageOverall, currentAiNameForLoading, chat.aiModelId);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = loadingMessageHTML;
            loadingElement = tempDiv.firstElementChild;
            if (loadingElement) {
                loadingElement.classList.add('loading-dots');
                const messageContentDiv = loadingElement.querySelector('.message-content');
                if (messageContentDiv) {
                    const dotsSpan = document.createElement('span');
                    dotsSpan.className = 'dots';
                    dotsSpan.innerHTML = '<span>.</span><span>.</span><span>.</span>';
                    const textContentDiv = messageContentDiv.querySelector('.text-content');
                    if (textContentDiv) { textContentDiv.innerHTML = ''; textContentDiv.appendChild(dotsSpan); }
                    else { messageContentDiv.appendChild(dotsSpan); }
                }
                messagesContainer.appendChild(loadingElement);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }

        try {
            // Son mesajı hariç tutarak geçmişi oluştur
            const conversationHistoryForAPI = chat.messages
                .slice(0, -1) // Son mesajı hariç tut
                .filter(msg => msg.text && String(msg.text).trim() !== '')
                .map(msg => ({ role: msg.isUser ? 'user' : 'model', parts: [{ text: String(msg.text).trim() }] }));
            
            log('info', 'ChatOps:SendMsg:API', `AI yanıtı için istek gönderiliyor: Model ID ${chat.aiModelId}`); // aiModelId artık DB ID'si
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({ 
                    chatId: chatId, 
                    aiModelId: chat.aiModelId, 
                    chat_message: text, // <<<<< YENİ MESAJI BURADA EKLE
                    history: conversationHistoryForAPI 
                }),
            });

            if (!response.ok) {
                let errorText = `Sunucu hatası: ${response.status}`;
                try { const errorData = await response.json(); errorText = errorData.error || errorText; }
                catch (e) { errorText = (await response.text()) || errorText; }
                throw new Error(errorText);
            }
            const data = await response.json();
            if (!data.response || typeof data.response !== 'string') throw new Error("AI'dan geçersiz yanıt formatı.");

            if (loadingElement && loadingElement.parentNode) {
                const aiMessage = { isUser: false, text: data.response, timestamp: Date.now() };
                chat.messages.push(aiMessage); chat.lastActivity = Date.now();
                const finalMessageHTML = createMessageHTML(aiMessage, isFirstAIMessageOverall, currentAiNameForLoading, chat.aiModelId);
                const finalTempDiv = document.createElement('div');
                finalTempDiv.innerHTML = finalMessageHTML;
                loadingElement.parentNode.replaceChild(finalTempDiv.firstElementChild, loadingElement);
                if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } catch (error) {
            log('error', 'ChatOps:SendMsg:Catch', 'Mesaj gönderme/alma hatası!', error);
            const errorMessageText = `Üzgünüm, bir sorun oluştu: ${error.message || 'Bilinmeyen sunucu hatası'}`;
            if (loadingElement && loadingElement.parentNode) {
                const aiErrorMessage = { isUser: false, text: errorMessageText, timestamp: Date.now(), isError: true };
                const errorHTML = createMessageHTML(aiErrorMessage, false, "Sistem", chat.aiModelId);
                loadingElement.parentNode.innerHTML = errorHTML; // Replace loading content
                if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else if (messagesContainer) {
                 const aiErrorMessage = { isUser: false, text: errorMessageText, timestamp: Date.now(), isError: true };
                 messagesContainer.insertAdjacentHTML('beforeend', createMessageHTML(aiErrorMessage, false, "Sistem", chat.aiModelId));
                 messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                alert(errorMessageText);
            }
        }
    }

    /**
     * 5.3. Yayın Mesajları
     */
    function sendBroadcastMessage() {
        if (!elements.broadcastMessageInput) return alert("Yayın aracı bulunamadı.");
        const messageText = elements.broadcastMessageInput.value.trim();
        if (messageText === '') return alert("Lütfen bir mesaj yazın.");
        const activeVisibleChats = state.chats.filter(chat => !chat.isMinimized);
        if (activeVisibleChats.length === 0) return alert('Aktif sohbet yok.');
        activeVisibleChats.forEach(chat => sendMessage(chat.id, `📢 **YAYIN:** ${messageText}`));
        elements.broadcastMessageInput.value = '';
    }

    //=============================================================================
    // 6. AI MODEL YÖNETİMİ (AI MODEL MANAGEMENT)
    //=============================================================================

    // Global bir referans, aktif olan model dropdown'ının dışına tıklama olayını yönetmek için
    let activeModelDropdownContext = null;

    function closeAllModelDropdowns() {
        if (activeModelDropdownContext) {
            if (activeModelDropdownContext.dropdownEl && activeModelDropdownContext.dropdownEl.parentNode) {
                activeModelDropdownContext.dropdownEl.classList.remove('show');
                // Animasyonun bitmesini bekleyip DOM'dan kaldırmak daha pürüzsüz olabilir
                setTimeout(() => {
                    if (activeModelDropdownContext.dropdownEl && activeModelDropdownContext.dropdownEl.parentNode) {
                         activeModelDropdownContext.dropdownEl.parentNode.removeChild(activeModelDropdownContext.dropdownEl);
                    }
                }, 300);
            }
            document.removeEventListener('click', activeModelDropdownContext.handler, true);
            activeModelDropdownContext = null;
            log('debug', 'AIModel:Dropdown', 'Mevcut model dropdown kapatıldı ve olay dinleyici kaldırıldı.');
        }
        // Ek olarak, DOM'da kalmış olabilecek diğer dropdownları da temizleyelim (güvenlik önlemi)
        document.querySelectorAll('.model-dropdown').forEach(openDropdown => {
            openDropdown.classList.remove('show');
            setTimeout(() => { if(openDropdown.parentNode) openDropdown.parentNode.removeChild(openDropdown); }, 300);
        });
    }

    function showModelDropdown(chatId, titleElement) {
        log('action', 'AIModel:ShowDropdown', `Model açılır menüsü gösteriliyor: ${chatId}`);

        // Başka bir dropdown açıksa önce onu kapat
        closeAllModelDropdowns();

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('warn', 'AIModel:ShowDropdown', `Sohbet bulunamadı: ${chatId}`);
            return;
        }
        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('info', 'AIModel:ShowDropdown', `Model zaten kilitli, dropdown gösterilmeyecek: ${chatId}`);
            return;
        }
        if (!window.state || !window.state.aiTypes || window.state.aiTypes.length === 0) {
            log('error', 'AIModel:ShowDropdown', 'AI Modelleri yüklenemedi.');
            alert('AI Modelleri yüklenemedi.');
            return;
        }

        const dropdownElement = document.createElement('div'); // Değişken adını farklılaştırdım
        dropdownElement.className = 'model-dropdown';

        // window.state.aiTypes'daki id'nin, veritabanındaki ai_models.id olduğunu varsayıyoruz (index.html'deki değişikliklerle)
        // chat.aiModelId de sayısal olmalı
        const optionsHTML = window.state.aiTypes.map(model => `
            <div class="model-option ${model.id === chat.aiModelId ? 'selected active' : ''}" data-model-id="${model.id}" title="${model.description || model.name}">
                <i class="${model.icon || 'bi bi-cpu'} me-2"></i>
                <span>${model.name || 'Bilinmeyen Model'}</span>
                ${model.id === chat.aiModelId ? '<i class="bi bi-check-lg ms-auto"></i>' : ''}
            </div>
        `).join('');
        dropdownElement.innerHTML = `<div class="list-group list-group-flush">${optionsHTML}</div>`;

        // dropdownElement'i DOM'a ekle
        if (titleElement.parentNode) {
             titleElement.parentNode.insertBefore(dropdownElement, titleElement.nextSibling);
        } else {
            log('error', 'AIModel:ShowDropdown', 'Dropdown eklenecek başlık elementinin parentNode\'u yok.', titleElement);
            return;
        }

        // Gösterim için animasyon frame'i bekle
        requestAnimationFrame(() => {
            dropdownElement.classList.add('show');
        });

        dropdownElement.querySelectorAll('.model-option').forEach(option => {
            option.onclick = (e) => {
                e.stopPropagation();
                const newModelIdString = option.getAttribute('data-model-id'); // Bu bir metin (string)
                // chat.aiModelId sayısal olmalı (önceki düzeltmelerle sağlandı)
                if (newModelIdString && Number(newModelIdString) !== chat.aiModelId) {
                    changeAIModel(chatId, newModelIdString); // changeAIModel metin ID'yi alıp kendisi dönüştürecek
                }
                closeAllModelDropdowns(); // Seçim yapıldıktan sonra kapat
            };
        });

        const handleClickOutside = (event) => {
            // dropdownElement'in hala DOM'da olup olmadığını kontrol et
            if (!dropdownElement || !dropdownElement.parentNode) {
                document.removeEventListener('click', handleClickOutside, true);
                activeModelDropdownContext = null; // Eğer bir şekilde silindiyse context'i temizle
                return;
            }
            if (!dropdownElement.contains(event.target) && event.target !== titleElement && !titleElement.contains(event.target)) {
                closeAllModelDropdowns();
            }
        };

        // Yeni aktif dropdown context'ini ayarla
        activeModelDropdownContext = {
            dropdownEl: dropdownElement,
            handler: handleClickOutside
        };
        document.addEventListener('click', handleClickOutside, true);
        log('debug', 'AIModel:ShowDropdown', `Model dropdown oluşturuldu ve olay dinleyici eklendi: ${chatId}`);
    }

    function changeAIModel(chatId, newAiModelIdString) { // Parametre adını daha açıklayıcı yaptım
        log('action', 'AIModel:Change', `Model değişimi: ${chatId}, Yeni Model ID (Metin): ${newAiModelIdString}`);
        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
             log('error', 'AIModel:Change', `Sohbet bulunamadı: ${chatId}`);
             return;
        }
        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('warn', 'AIModel:Change', `Sohbet ${chatId} için model değiştirilemez, mesajlaşma başladı.`);
            return;
        }
        if (!window.state || !window.state.aiTypes) {
            alert('AI Modelleri yüklenemedi.');
            return;
        }

        const numericNewModelId = Number(newAiModelIdString); // Metinden sayıya dönüştür
        const newModel = window.state.aiTypes.find(m => m.id === numericNewModelId); // Sayı ile sayı karşılaştır

        if (!newModel) {
            log('error', 'AIModel:Change', `Geçersiz AI Modeli seçildi: "${newAiModelIdString}" (dönüştürülmüş: ${numericNewModelId})`);
            alert('Geçersiz AI Modeli seçildi.');
            return;
        }
        chat.aiModelId = numericNewModelId; // Modeli sayı olarak sakla
        
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            const chatTitleElement = chatElement.querySelector('.chat-title');
            if (chatTitleElement) {
                const iconElement = chatTitleElement.querySelector('i:first-child');
                const nameElement = chatTitleElement.querySelector('span');
                if (iconElement) iconElement.className = newModel.icon || 'bi bi-cpu';
                if (nameElement) nameElement.textContent = `${newModel.name || 'Bilinmeyen'} (ID: ${chat.id.slice(-4)})`;
            }
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer && (!chat.messages || chat.messages.length === 0)) {
                messagesContainer.innerHTML = createWelcomeMessageHTML(newModel.name || 'Seçilen AI');
            }
        }
        log('info', 'AIModel:Change', `Sohbet ${chatId} için AI modeli başarıyla ${newModel.name} (ID: ${numericNewModelId}) olarak değiştirildi.`);
        renderActiveChatsDropdown();
    }

    //=============================================================================
    // 7. MEDYA İŞLEMLERİ (MEDIA HANDLING)
    //=============================================================================
    function downloadMedia(mediaSrc, defaultFileName = 'downloaded-media') {
        if (!mediaSrc || typeof mediaSrc !== 'string') return alert('İndirilecek medya kaynağı geçersiz.');
        try {
            const link = document.createElement('a');
            link.href = mediaSrc;
            let fileName = defaultFileName;
            try {
                const url = new URL(mediaSrc.startsWith('data:') ? 'http://localhost' : mediaSrc);
                const lastSegment = url.pathname.substring(url.pathname.lastIndexOf('/') + 1);
                if (lastSegment && lastSegment.includes('.')) fileName = lastSegment;
                else {
                    if (mediaSrc.startsWith('data:image/png')) fileName = `${defaultFileName}-${Date.now()}.png`;
                    else if (mediaSrc.startsWith('data:image/jpeg')) fileName = `${defaultFileName}-${Date.now()}.jpg`;
                    else if (mediaSrc.startsWith('data:audio/mpeg')) fileName = `${defaultFileName}-${Date.now()}.mp3`;
                    else fileName = `${defaultFileName}-${Date.now()}`;
                }
            } catch (e) {
                 if (mediaSrc.startsWith('data:image/png')) fileName = `${defaultFileName}-${Date.now()}.png`;
                 else fileName = `${defaultFileName}-${Date.now()}`;
            }
            link.download = fileName;
            document.body.appendChild(link); link.click(); document.body.removeChild(link);
        } catch (error) {
            log('error', 'Media:Download', 'Medya indirilirken hata!', error);
            alert(`Medya indirilemedi: ${error.message}`);
        }
    }
    function downloadImage(imageData) { downloadMedia(imageData, 'ai-image'); }
    function downloadAudio(audioData) { downloadMedia(audioData, 'ai-audio'); }
    function viewFullImage(imageData) {
        if (!imageData || typeof imageData !== 'string') return alert('Görüntülenecek resim geçersiz.');
        const existingModal = document.querySelector('.image-modal-zk');
        if (existingModal) existingModal.remove();
        const modal = document.createElement('div');
        modal.className = 'image-modal-zk';
        modal.style.cssText = `position:fixed;top:0;left:0;width:100%;height:100%;background-color:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:2000;padding:20px;box-sizing:border-box;`;
        modal.innerHTML = `
            <div style="max-width:90%;max-height:90%;position:relative;">
                <img src="${imageData}" alt="Tam Ekran Resim" style="max-width:100%;max-height:100%;display:block;border-radius:8px;box-shadow:0 0 20px rgba(0,0,0,0.5);">
                <button title="Kapat (Esc)" style="position:absolute;top:10px;right:10px;background:white;border:none;border-radius:50%;width:30px;height:30px;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;">&times;</button>
            </div>`;
        const closeModal = () => {
            if (modal.parentNode) modal.remove();
            document.removeEventListener('keydown', handleEscapeKey);
        };
        modal.addEventListener('click', (e) => { if (e.target === modal || e.target.classList.contains('image-modal-zk')) closeModal(); });
        const handleEscapeKey = (e) => { if (e.key === 'Escape') closeModal(); };
        document.addEventListener('keydown', handleEscapeKey);
        document.body.appendChild(modal);
    }

    //=============================================================================
    // 8. GENEL API VE BAŞLATMA (PUBLIC API & INITIALIZATION)
    //=============================================================================
    function init() {
        log('info', 'Init', 'ChatManager başlatılıyor...', { version: "1.0.3" });
        if (!initElements()) {
            log('error', 'Init', 'ChatManager başlatılamadı: Gerekli DOM elementleri yok.');
            const body = document.querySelector('body');
            if (body) {
                 const errorMsgDiv = document.createElement('div');
                 errorMsgDiv.innerHTML = '<p style="background-color:red;color:white;padding:10px;text-align:center;position:fixed;top:0;left:0;width:100%;z-index:9999;">Hata: Sohbet arayüzü başlatılamadı.</p>';
                 body.prepend(errorMsgDiv);
            }
            return;
        }
        setupGlobalHandlers();

        // Sidebar AI Model seçicilerine olay dinleyici ekle
        // index.html'deki değişikliklerle data-ai-index, model.id'yi tutacak
        const aiModelSelectorItems = document.querySelectorAll('.ai-model-selector-item');
        if (aiModelSelectorItems.length > 0) {
            aiModelSelectorItems.forEach(item => {
                if (item._chatManagerClickListener) item.removeEventListener('click', item._chatManagerClickListener);
                item._chatManagerClickListener = function(event) {
                    event.preventDefault(); event.stopPropagation();
                    const modelId = this.dataset.aiIndex; // Bu artık ai_models.id olmalı
                    log('action', 'Init:SidebarModelClick', `Kenar çubuğu model seçildi (Model ID): ${modelId}`);
                    if (modelId) addChat(modelId);
                    else { log('error', 'Init:SidebarModelClick', 'Geçersiz AI model ID seçildi.', { dataset: this.dataset }); alert("Geçersiz model seçimi."); }
                };
                item.addEventListener('click', item._chatManagerClickListener);
            });
        } else {
            log('warn', 'Init', 'Kenar çubuğunda AI model seçici öğe (.ai-model-selector-item) bulunamadı.');
        }
        renderChats();
        renderChatHistory();
        log('info', 'Init', 'ChatManager başarıyla başlatıldı.');
    }

    return {
        init, addChat, removeChat, clearAllChats, sendMessage, sendBroadcastMessage,
        downloadImage, viewFullImage, downloadAudio,
        _getState: () => JSON.parse(JSON.stringify(state)),
        _log: log
    };
})();

window.ChatManager = ChatManager;

// ... (ChatManager kodunun geri kalanı) ...

document.addEventListener('DOMContentLoaded', () => {
    ChatManager._log('info', 'DOMContentLoaded', 'DOM yüklendi.'); // Sadece log bırakılabilir veya bu blok tamamen kaldırılabilir eğer main.js DOMContentLoaded'i bekliyorsa.
    // ChatManager.init(); // <--- BU SATIRI YORUM SATIRI YAPIN VEYA SİLİN

    // Akordiyon menü ile ilgili Bootstrap olay dinleyicileri kalabilir,
    // çünkü bunlar DOM'un hazır olmasını gerektirir ve ChatManager'ın init'i ile doğrudan bağlantılı olmayabilir.
    const aiCategoriesAccordion = document.getElementById('aiCategoriesAccordion');
    if (aiCategoriesAccordion && typeof bootstrap !== 'undefined') {
        const collapseElements = aiCategoriesAccordion.querySelectorAll('.collapse');
        collapseElements.forEach(collapseEl => {
            const header = collapseEl.previousElementSibling;
            const chevron = header ? header.querySelector('.category-chevron') : null;
            if (chevron) {
                collapseEl.addEventListener('show.bs.collapse', () => { chevron.classList.remove('bi-chevron-down'); chevron.classList.add('bi-chevron-up'); });
                collapseEl.addEventListener('hide.bs.collapse', () => { chevron.classList.remove('bi-chevron-up'); chevron.classList.add('bi-chevron-down'); });
            }
        });
    }
});