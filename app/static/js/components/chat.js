/**
 * ZekAI Sohbet Bileşeni Modülü
 * ===========================
 * @description AI sohbet pencerelerini, düzenlerini ve kullanıcı etkileşimlerini yönetir
 * @version 1.0.2 (Gelişmiş Hata Ayıklama)
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
 * 2.3. İçerik Oluşturucuları (Content Renderers - Text, Image, Audio)
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
 * 6.3. AI Yanıt Üretimi (Simüle Edilmiş) (AI Response Generation - Simulated)
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
     * 1.1. Gelişmiş Günlükleme Sistemi (Advanced Logging System)
     * -------------------------------------------------------
     * Hata ayıklama, bilgi, eylem, uyarı ve hata seviyelerinde,
     * bağlam bilgisiyle ve yapılandırılabilir günlük seviyesiyle günlükleme sağlar.
     */
    window.DEBUG_LOG_ACTIVE = true; // Günlükleri tamamen aç/kapa
    window.ACTIVE_LOG_LEVEL = 'debug'; // Gösterilecek minimum günlük seviyesi: 'debug', 'info', 'action', 'warn', 'error'

    const LOG_LEVELS = {
        debug:  { priority: 0, color: 'color:#9E9E9E;', prefix: 'DEBUG' },  // Gri
        info:   { priority: 1, color: 'color:#2196F3;', prefix: 'INFO ' },  // Mavi
        action: { priority: 2, color: 'color:#4CAF50;', prefix: 'ACTION'}, // Yeşil
        warn:   { priority: 3, color: 'color:#FFC107;', prefix: 'WARN ' },  // Sarı
        error:  { priority: 4, color: 'color:#F44336;', prefix: 'ERROR'}   // Kırmızı
    };

    /**
     * Mesajı zaman damgası, seviye, bağlam ve renkle günlükler.
     * @param {string} level - Günlük seviyesi (debug|info|action|warn|error)
     * @param {string} context - Günlüğün kaynağı (örn: "ChatOps", "Render", "AIModel")
     * @param {string} message - Günlüklenecek ana mesaj.
     * @param {...any} details - Günlüklenecek ek argümanlar (objeler, değerler vb.).
     */
    function log(level, context, message, ...details) {
        if (!window.DEBUG_LOG_ACTIVE) return;

        const levelConfig = LOG_LEVELS[level] || LOG_LEVELS['info'];
        const activeLevelConfig = LOG_LEVELS[window.ACTIVE_LOG_LEVEL] || LOG_LEVELS['debug'];

        if (levelConfig.priority < activeLevelConfig.priority) {
            return; // Ayarlanan seviyeden düşük öncelikli günlükleri gösterme
        }

        const timestamp = new Date().toISOString().substr(11, 12); // HH:MM:SS.mmm
        const logPrefix = `%c[${timestamp}] [${levelConfig.prefix}] [${context}]`;
        
        const hasObjects = details.some(arg => typeof arg === 'object' && arg !== null);

        if (details.length > 0) {
            if (hasObjects || message.length > 50 || details.length > 1) { // Çok fazla detay varsa veya obje varsa grupla
                console.groupCollapsed(logPrefix, levelConfig.color, message);
                details.forEach(detail => {
                    if (typeof detail === 'object' && detail !== null) {
                        console.dir(detail); // Objeler için console.dir daha detaylı olabilir
                    } else {
                        console.log(detail);
                    }
                });
                console.groupEnd();
            } else {
                console.log(logPrefix, levelConfig.color, message, ...details);
            }
        } else {
            console.log(logPrefix, levelConfig.color, message);
        }
    }

    /**
     * 1.2. Durum Yönetimi (State Management)
     * ----------------------------------
     * Sohbetleri, geçmişi ve yapılandırmayı yönetmek için özel durum (state).
     * ÖNEMLİ: state objesini doğrudan değiştirmek yerine state değiştiren fonksiyonlar kullanın.
     * Bu, değişikliklerin takibini ve loglanmasını kolaylaştırır.
     */
    const state = {
        chats: [],
        chatHistory: [],
        maxChats: 6
    };

    // Global durumu başlat veya mevcut olanı kullan
    if (window.state) {
        log('warn', 'CoreSystem:StateInit', 'Mevcut window.state algılandı. Birleştiriliyor...', {
            existingChats: window.state.chats ? window.state.chats.length : 'yok',
            existingHistory: window.state.chatHistory ? window.state.chatHistory.length : 'yok',
            existingAiTypes: window.state.aiTypes ? window.state.aiTypes.length : 'yok'
        });
        if (!window.state.chats) window.state.chats = state.chats;
        if (!window.state.chatHistory) window.state.chatHistory = state.chatHistory;
        if (!window.state.aiTypes) window.state.aiTypes = []; // index.html tarafından doldurulacak
    } else {
        window.state = {
            chats: state.chats,
            chatHistory: state.chatHistory,
            aiTypes: []
        };
        log('info', 'CoreSystem:StateInit', 'Yeni window.state oluşturuldu.');
    }
    log('debug', 'CoreSystem:StateInit', 'Başlangıç durumu:', JSON.parse(JSON.stringify(window.state)));


    /**
     * 1.3. DOM Elementleri (DOM Elements)
     * -------------------------------
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
            // Geliştirme aşamasında bir uyarı gösterilebilir, ancak canlıda sessiz kalmak daha iyi olabilir.
            // alert(`Hata: Şu DOM elementleri eksik: ${missingElements.join(', ')}. Uygulama düzgün çalışmayabilir.`);
            return false;
        }
        log('info', 'CoreSystem:DOMInit', 'Tüm DOM elementleri başarıyla bulundu.');
        return true;
    }

    /**
     * 1.4. Global Hata Yakalayıcı (Global Error Handler)
     * --------------------------------------------------
     * Yakalanmamış JavaScript hatalarını loglar.
     */
    window.onerror = function(message, source, lineno, colno, error) {
        log('error', 'GlobalErrorHandler', 'Yakalanmamış bir hata oluştu!', {
            message: message,
            source: source,
            lineno: lineno,
            colno: colno,
            errorObject: error ? JSON.parse(JSON.stringify(error, Object.getOwnPropertyNames(error))) : 'N/A'
        });
        // True döndürmek, hatanın tarayıcı konsolunda varsayılan şekilde işlenmesini engeller.
        // Hata ayıklama sırasında false bırakmak daha iyi olabilir.
        return false;
    };

    window.onunhandledrejection = function(event) {
        log('error', 'GlobalPromiseRejection', 'İşlenmemiş Promise reddi!', {
            reason: event.reason ? (typeof event.reason === 'object' ? JSON.parse(JSON.stringify(event.reason, Object.getOwnPropertyNames(event.reason))) : event.reason) : 'N/A',
            promise: event.promise
        });
    };


    //=============================================================================
    // 2. KULLANICI ARAYÜZÜ BİLEŞENLERİ (UI COMPONENTS)
    //=============================================================================

    /**
     * 2.1. Sohbet Elementi Fabrikaları (Chat Element Factories)
     */
    function createChatElement(chatData) {
        log('debug', 'UI:CreateChat', 'Sohbet elementi oluşturuluyor...', chatData);
        try {
            const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) ||
                            (window.state.aiTypes && window.state.aiTypes.length > 0 ? window.state.aiTypes[0] : null) ||
                            { name: `Bilinmeyen AI (ID: ${chatData.aiModelId})`, icon: 'bi bi-question-circle' };

            if (!aiModel) {
                log('warn', 'UI:CreateChat', `AI modeli bulunamadı: ${chatData.aiModelId}. Varsayılan kullanılıyor.`, chatData);
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
            // Hata durumunda boş bir div veya bir hata mesajı döndürebilirsiniz.
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chat-window chat-window-error';
            errorDiv.textContent = 'Sohbet yüklenirken bir hata oluştu.';
            errorDiv.setAttribute('data-chat-id', chatData.id);
            return errorDiv;
        }
    }

    /**
     * 2.2. Mesaj HTML Üreteçleri (Message HTML Generators)
     */
    function createMessageHTML(message, isFirstAIMessage = false, aiName = '', aiModelId = '') {
        // log('debug', 'UI:CreateMsgHTML', 'Mesaj HTML oluşturuluyor...', { message, isFirstAIMessage, aiName, aiModelId }); // Bu çok fazla log üretebilir
        try {
            const messageClass = message.isUser ? 'user-message' : 'ai-message';
            const timestamp = new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            let messageContent = message.isUser ? renderTextContent(message.text) : renderContent(message.text, aiModelId);

            if (!message.isUser && aiName && (isFirstAIMessage || message.showAiName)) { // showAiName gibi bir flag eklenebilir
                messageContent = `<div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>${messageContent}`;
            }
            
            if (message.isError) { // Hata mesajları için özel stil
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
        // log('debug', 'UI:WelcomeMsg', `Hoş geldin mesajı HTML oluşturuluyor: ${aiName}`);
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
     * 2.3. İçerik Oluşturucuları (Content Renderers)
     */
    function renderContent(content, aiModelId) {
        // log('debug', 'UI:RenderContent', `İçerik oluşturuluyor: Model ID ${aiModelId}`, {contentPreview: String(content).substring(0,50) });
        try {
            const aiType = aiModelId ? aiModelId.split('_')[0] : 'txt'; // aiModelId null/undefined ise txt varsay

            switch (aiType) {
                case 'img':
                    return renderImageContent(content);
                case 'aud':
                    return renderAudioContent(content);
                case 'txt':
                default:
                    return renderTextContent(content);
            }
        } catch (error) {
            log('error', 'UI:RenderContent', 'İçerik oluşturulurken hata!', error, { aiModelId });
            return renderTextContent("İçerik yüklenirken bir sorun oluştu.");
        }
    }

    function renderTextContent(content) {
        const sanitizedContent = String(content || "").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        // Markdown benzeri temel formatlamalar eklenebilir (örn: satır sonları için <br>)
        // const formattedContent = sanitizedContent.replace(/\n/g, '<br>');
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
            elements.chatContainer.innerHTML = ''; // Konteyneri temizle

            const activeVisibleChats = state.chats.filter(chat => !chat.isMinimized);

            if (activeVisibleChats.length === 0) {
                // Karşılama ekranını göster. Eğer zaten chatContainer'daysa tekrar ekleme.
                if (elements.welcomeScreen && elements.welcomeScreen.parentNode !== elements.chatContainer) {
                     elements.chatContainer.appendChild(elements.welcomeScreen);
                }
                elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap justify-content-center align-items-center';
                log('info', 'Render:Chats', 'Aktif sohbet yok, karşılama ekranı gösteriliyor.');
            } else {
                // Karşılama ekranını kaldır (eğer varsa)
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
                    default: layoutClass = 'layout-6'; break; // 6'dan fazla için de aynı düzen
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
            log('error', 'Render:Chats', 'Sohbetleri oluştururken genel bir hata oluştu!', error, { activeChatsCount: state.chats.filter(c => !c.isMinimized).length });
            elements.chatContainer.innerHTML = '<div class="alert alert-danger m-3">Sohbetler yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.</div>';
        } finally {
            renderActiveChatsDropdown(); // Her durumda dropdown'ı güncelle
        }
    }

    function renderActiveChatsDropdown() {
        // log('debug', 'Render:Dropdown', 'Aktif sohbetler açılır menüsü oluşturuluyor...'); // Çok sık çağrılabilir
        if (!elements.activeChatsList || !elements.activeChatsDropdownMenu || !elements.activeChatsDropdownTrigger) {
            log('warn', 'Render:Dropdown', 'Aktif sohbetler açılır menü elementleri bulunamadı, işlem atlanıyor.');
            return;
        }
        try {
            elements.activeChatsList.innerHTML = '';

            if (state.chats.length === 0) {
                elements.activeChatsDropdownTrigger.classList.add('disabled');
                // elements.activeChatsDropdownMenu.classList.remove('show'); // Bootstrap bunu kendi yönetir
                const noChatsLi = document.createElement('li');
                noChatsLi.className = 'list-group-item text-muted';
                noChatsLi.textContent = 'Aktif sohbet yok';
                noChatsLi.style.paddingLeft = '1rem';
                elements.activeChatsList.appendChild(noChatsLi);
                // elements.activeChatsDropdownTrigger.setAttribute('aria-expanded', 'false'); // Bootstrap bunu kendi yönetir
                return;
            }

            elements.activeChatsDropdownTrigger.classList.remove('disabled');

            state.chats.forEach(chatData => {
                const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) || { name: `AI (${chatData.aiModelId ? chatData.aiModelId.slice(-4) : 'Bilinmeyen'})`, icon: 'bi bi-cpu' };
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex align-items-center justify-content-between';
                listItem.setAttribute('data-chat-id', chatData.id);
                listItem.style.cursor = 'pointer'; // Tıklanabilir olduğunu belirt
                listItem.style.paddingLeft = '1rem';
                listItem.style.paddingRight = '1rem';

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
                        log('action', 'Render:Dropdown', `Küçültülmüş sohbet geri yükleniyor: ${chatData.id}`);
                        const chatToRestore = state.chats.find(c => c.id === chatData.id);
                        if (chatToRestore) {
                            chatToRestore.isMinimized = false;
                            renderChats();
                        } else {
                            log('warn', 'Render:Dropdown', `Geri yüklenecek sohbet bulunamadı: ${chatData.id}`);
                        }
                    };
                } else {
                    listItem.innerHTML = chatNameHTML;
                    listItem.onclick = () => {
                        log('action', 'Render:Dropdown', `Aktif sohbet öğesi tıklandı: ${chatData.id}. Sohbet penceresi vurgulanıyor.`);
                        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                        if (chatWindow) {
                            chatWindow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            chatWindow.classList.add('chat-window--highlighted');
                            setTimeout(() => {
                                chatWindow.classList.remove('chat-window--highlighted');
                            }, 2000);
                        } else {
                             log('warn', 'Render:Dropdown', `Vurgulanacak sohbet penceresi bulunamadı: ${chatData.id}`);
                        }
                    };
                }
                elements.activeChatsList.appendChild(listItem);
            });
        } catch (error) {
            log('error', 'Render:Dropdown', 'Aktif sohbetler açılır menüsü oluşturulurken hata!', error, { numChats: state.chats.length });
            if (elements.activeChatsList) elements.activeChatsList.innerHTML = '<li class="list-group-item text-danger">Liste yüklenemedi.</li>';
        }
    }

    function renderChatHistory() {
        log('debug', 'Render:History', 'Sohbet geçmişi oluşturuluyor...', { historyCount: state.chatHistory.length });
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
                noHistoryLi.style.paddingLeft = '1rem';
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
                listItem.style.paddingLeft = '1rem';
                listItem.style.paddingRight = '1rem';

                const nameContainerSpan = document.createElement('span');
                nameContainerSpan.className = 'd-flex align-items-center';
                nameContainerSpan.style.overflow = 'hidden';
                nameContainerSpan.style.textOverflow = 'ellipsis';
                nameContainerSpan.style.whiteSpace = 'nowrap';
                nameContainerSpan.style.flexGrow = '1';
                nameContainerSpan.style.marginRight = '0.5rem';

                const iconElement = document.createElement('i');
                iconElement.className = `${aiModelInfo.icon || 'bi bi-archive'} me-2`;

                const nameSpanElement = document.createElement('span');
                let historyItemText = aiModelInfo.name || 'Geçmiş Sohbet';
                if (chat.closedTimestamp) {
                    const date = new Date(chat.closedTimestamp);
                    const dateString = date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: '2-digit' });
                    historyItemText += ` (${dateString})`;
                } else if (chat.createdAt) { // closedTimestamp yoksa createdAt kullan
                     const date = new Date(chat.createdAt);
                    const dateString = date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: '2-digit' });
                    historyItemText += ` (Oluşturma: ${dateString})`;
                }
                nameSpanElement.textContent = historyItemText;
                nameSpanElement.title = historyItemText + ` (ID: ${chat.id.slice(-4)})`;

                nameContainerSpan.appendChild(iconElement);
                nameContainerSpan.appendChild(nameSpanElement);
                listItem.appendChild(nameContainerSpan);

                const restoreButton = document.createElement('button');
                restoreButton.className = 'btn btn-sm btn-icon chat-history-restore-btn flex-shrink-0';
                restoreButton.title = 'Sohbeti Geri Yükle';
                restoreButton.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i>';
                restoreButton.onclick = function(event) {
                    event.stopPropagation();
                    log('action', 'Render:History', `Geçmişten sohbet geri yükle tıklandı: ${chat.id}`);
                    // TODO: restoreChatFromHistory(chat.id) fonksiyonunu uygula;
                    alert('Geçmişten sohbet geri yükleme henüz tam olarak uygulanmadı. Konsolu kontrol edin.');
                    log('info', 'Render:History', 'Geri yüklenecek sohbet verisi:', chat);
                    // Örnek: addChat(chat.aiModelId, chat.messages); // addChat'i mesajları alacak şekilde güncellemek gerekebilir.
                };
                listItem.appendChild(restoreButton);

                listItem.onclick = function() {
                    log('action', 'Render:History', `Sohbet geçmişi öğesi tıklandı: ${chat.id}`);
                    // TODO: Sohbet geçmişi mesajlarını görüntüleme mantığını uygula (örn: bir modal içinde)
                    alert(`'${historyItemText}' sohbetinin geçmişini görüntüleme henüz uygulanmadı. Mesajlar konsolda loglandı.`);
                    log('info', 'Render:History', `Görüntülenecek geçmiş sohbet mesajları (${chat.id}):`, chat.messages);
                };
                elements.chatHistoryList.appendChild(listItem);
            });
        } catch (error) {
            log('error', 'Render:History', 'Sohbet geçmişi oluşturulurken hata!', error, { historyCount: state.chatHistory.length });
             if (elements.chatHistoryList) elements.chatHistoryList.innerHTML = '<li class="list-group-item text-danger">Geçmiş yüklenemedi.</li>';
        }
    }


    //=============================================================================
    // 4. OLAY İŞLEYİCİLERİ (EVENT HANDLERS)
    //=============================================================================

    function setupChatWindowControls(chatElement) {
        if (!chatElement) {
            log('error', 'Events:ChatCtrl', 'Sohbet kontrolleri ayarlanamıyor: sohbet elementi null.');
            return;
        }
        const chatId = chatElement.getAttribute('data-chat-id');
        if (!chatId) {
            log('error', 'Events:ChatCtrl', 'Sohbet kontrolleri ayarlanamıyor: chat ID eksik.', chatElement);
            return;
        }
        // log('debug', 'Events:ChatCtrl', `Sohbet penceresi kontrolleri ayarlanıyor: ${chatId}`);

        try {
            const closeBtn = chatElement.querySelector('.chat-close-btn');
            if (closeBtn) {
                closeBtn.onclick = (e) => {
                    e.stopPropagation();
                    log('action', 'Events:ChatCtrl:Close', `Sohbet kapatma düğmesi tıklandı: ${chatId}`);
                    const chatData = state.chats.find(c => c.id === chatId);
                    if (chatData && chatData.messages && chatData.messages.some(msg => msg.isUser)) {
                        if (confirm("Bu sohbeti kapatmak istediğinizden emin misiniz? Konuşma geçmişe kaydedilecek.")) {
                            removeChat(chatId);
                        } else {
                            log('info', 'Events:ChatCtrl:Close', `Sohbet kapatma iptal edildi: ${chatId}`);
                        }
                    } else {
                        removeChat(chatId); // Boş sohbeti sormadan kapat
                    }
                };
            } else { log('warn', 'Events:ChatCtrl', `Kapatma düğmesi bulunamadı: ${chatId}`); }

            const minimizeBtn = chatElement.querySelector('.chat-minimize-btn');
            if (minimizeBtn) {
                minimizeBtn.onclick = (e) => {
                    e.stopPropagation();
                    log('action', 'Events:ChatCtrl:Minimize', `Sohbet küçültme düğmesi tıklandı: ${chatId}`);
                    const chat = state.chats.find(c => c.id === chatId);
                    if (chat) {
                        chat.isMinimized = true;
                        log('info', 'Events:ChatCtrl:Minimize', `Sohbet küçültüldü: ${chatId}. Durum:`, chat.isMinimized);
                        renderChats();
                    } else {
                        log('warn', 'Events:ChatCtrl:Minimize', `Küçültülecek sohbet bulunamadı: ${chatId}`);
                    }
                };
            } else { log('warn', 'Events:ChatCtrl', `Küçültme düğmesi bulunamadı: ${chatId}`); }

            const chatTitle = chatElement.querySelector('.chat-title');
            if (chatTitle && chatTitle.classList.contains('model-changeable')) {
                chatTitle.onclick = (e) => {
                    e.stopPropagation();
                    log('action', 'Events:ChatCtrl:TitleClick', `Model seçimi için sohbet başlığı tıklandı: ${chatId}`);
                    showModelDropdown(chatId, chatTitle);
                };
            } else if (chatTitle && chatTitle.classList.contains('model-locked')) {
                 // log('debug', 'Events:ChatCtrl', `Model kilitli olduğu için başlık tıklama olayı atanmadı: ${chatId}`);
            } else { log('warn', 'Events:ChatCtrl', `Sohbet başlığı bulunamadı veya sınıfı yanlış: ${chatId}`); }


            const sendBtn = chatElement.querySelector('.chat-send-btn');
            const inputField = chatElement.querySelector('.chat-input');
            if (sendBtn && inputField) {
                const sendMessageHandler = () => {
                    const messageText = inputField.value.trim();
                    if (messageText) {
                        log('action', 'Events:ChatCtrl:Send', `Gönder düğmesi/Enter ile mesaj gönderiliyor: ${chatId}`, messageText);
                        sendMessage(chatId, messageText);
                        inputField.value = '';
                        inputField.focus(); // Gönderdikten sonra inputa odaklan
                    } else {
                        log('info', 'Events:ChatCtrl:Send', `Boş mesaj gönderilmedi: ${chatId}`);
                    }
                };
                sendBtn.onclick = sendMessageHandler;
                inputField.onkeypress = (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) { // Shift+Enter yeni satır için
                        e.preventDefault(); // Formun gönderilmesini engelle (eğer varsa)
                        sendMessageHandler();
                    }
                };
            } else {
                if (!sendBtn) log('warn', 'Events:ChatCtrl', `Gönderme düğmesi bulunamadı: ${chatId}`);
                if (!inputField) log('warn', 'Events:ChatCtrl', `Giriş alanı bulunamadı: ${chatId}`);
            }
        } catch (error) {
            log('error', 'Events:ChatCtrl', `Sohbet penceresi (${chatId}) kontrolleri ayarlanırken hata!`, error);
        }
    }

    function setupGlobalHandlers() {
        log('info', 'Events:Global', 'Global olay işleyicileri ayarlanıyor...');
        try {
            if(elements.welcomeNewChatBtn) {
                elements.welcomeNewChatBtn.onclick = () => {
                    log('action', 'Events:Global:WelcomeNewChat', 'Karşılama ekranı yeni sohbet düğmesi tıklandı.');
                    addChat();
                };
            } else { log('warn', 'Events:Global', 'Karşılama ekranı yeni sohbet düğmesi bulunamadı.'); }

            if(elements.newChatBtn) {
                elements.newChatBtn.onclick = () => {
                    log('action', 'Events:Global:NewChat', 'Yeni sohbet düğmesi tıklandı.');
                    addChat();
                };
            } else { log('warn', 'Events:Global', 'Yeni sohbet düğmesi bulunamadı.'); }

            if(elements.clearChatsBtn) {
                elements.clearChatsBtn.onclick = () => {
                    log('action', 'Events:Global:ClearChats', 'Tüm sohbetleri temizle düğmesi tıklandı.');
                    const startedChatsCount = state.chats.filter(chat => chat.messages && chat.messages.some(msg => msg.isUser)).length;
                    const unstartedChatsCount = state.chats.length - startedChatsCount;

                    if (unstartedChatsCount > 0) {
                        if (confirm(`${unstartedChatsCount} adet henüz başlanmamış sohbeti kapatmak istediğinizden emin misiniz? Devam eden konuşmaları olan sohbetler etkilenmeyecektir.`)) {
                            clearAllChats(false); // Sadece boş olanları temizle
                        } else {
                             log('info', 'Events:Global:ClearChats', 'Kullanılmayan sohbetleri temizleme iptal edildi.');
                        }
                    } else if (state.chats.length > 0) {
                         if (confirm(`Tüm (${state.chats.length}) sohbetleri kapatmak ve geçmişe taşımak istediğinizden emin misiniz?`)) {
                            clearAllChats(true); // Hepsini temizle (geçmişe taşı)
                        } else {
                            log('info', 'Events:Global:ClearChats', 'Tüm sohbetleri temizleme iptal edildi.');
                        }
                    }
                    else {
                        alert('Temizlenecek sohbet yok.');
                        log('info', 'Events:Global:ClearChats', 'Temizlenecek sohbet yok.');
                    }
                };
            } else { log('warn', 'Events:Global', 'Sohbetleri temizle düğmesi bulunamadı.'); }

            if (elements.sendBroadcastBtn && elements.broadcastMessageInput) {
                const broadcastHandler = () => {
                    log('action', 'Events:Global:Broadcast', 'Yayın mesajı gönderiliyor...');
                    sendBroadcastMessage();
                };
                elements.sendBroadcastBtn.addEventListener('click', broadcastHandler);
                elements.broadcastMessageInput.addEventListener('keypress', (event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault();
                        broadcastHandler();
                    }
                });
            } else {
                if(!elements.sendBroadcastBtn) log('warn', 'Events:Global', 'Yayın gönderme düğmesi bulunamadı.');
                if(!elements.broadcastMessageInput) log('warn', 'Events:Global', 'Yayın mesaj girişi bulunamadı.');
            }
            log('info', 'Events:Global', 'Global olay işleyicileri başarıyla ayarlandı.');
        } catch (error) {
            log('error', 'Events:Global', 'Global olay işleyicileri ayarlanırken hata!', error);
        }
    }


    //=============================================================================
    // 5. SOHBET OPERASYONLARI (CHAT OPERATIONS)
    //=============================================================================

    /**
     * 5.1. Sohbet Yönetimi (Chat Management)
     */
    function addChat(aiModelId, initialMessages = []) {
        log('action', 'ChatOps:Add', 'Yeni sohbet ekleme denemesi...', { requestedModelId: aiModelId, initialMessagesCount: initialMessages.length });

        if (!elements.chatContainer) {
            log('error', 'ChatOps:Add', 'Sohbet konteyneri bulunamadı. Sohbet eklenemiyor.');
            alert('Hata: Sohbet arayüzü doğru yüklenemedi. Lütfen sayfayı yenileyin.');
            return null;
        }

        const activeVisibleChatCount = state.chats.filter(c => !c.isMinimized).length;
        if (activeVisibleChatCount >= state.maxChats) {
            log('warn', 'ChatOps:Add', `Maksimum (${state.maxChats}) aktif sohbet sayısına ulaşıldı. Yeni sohbet eklenemiyor.`);
            alert(`Maksimum ${state.maxChats} sohbet paneline ulaşıldı. Lütfen önce birini kapatın veya küçültün.`);
            return null;
        }

        let finalAiModelId = aiModelId;
        if (!finalAiModelId) {
            if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                finalAiModelId = window.state.aiTypes[0].id; // Varsayılan olarak listedeki ilk model
                log('info', 'ChatOps:Add', `AI Model ID sağlanmadı, listedeki ilkine varsayılıyor: ${finalAiModelId}`);
            } else {
                log('error', 'ChatOps:Add', 'AI Model ID sağlanmadı ve varsayılan AI modeli mevcut değil (window.state.aiTypes boş).');
                alert('Sohbet oluşturulamıyor: Kullanılabilir AI modelleri bulunamadı. Lütfen yapılandırmayı kontrol edin.');
                return null;
            }
        } else {
            const modelExists = window.state.aiTypes.some(m => m.id === finalAiModelId);
            if (!modelExists) {
                log('warn', 'ChatOps:Add', `Sağlanan AI Model ID "${finalAiModelId}" geçerli değil. Listede bulunamadı. İlk AI modeline dönülüyor.`);
                if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                    finalAiModelId = window.state.aiTypes[0].id;
                } else {
                    log('error', 'ChatOps:Add', 'Sağlanan AI Model ID geçersizdi ve geri dönüş için AI modeli de bulunamadı.');
                    alert('Sohbet oluşturulamıyor: Belirtilen AI modeli geçersiz ve alternatif model de yok.');
                    return null;
                }
            }
        }
        
        // Model ID'sinin prefix içerip içermediğini kontrol et. Genellikle aiTypes içinde tam ID olmalı.
        // Eğer window.state.aiTypes içindeki ID'ler zaten "txt_", "img_" gibi prefixler içeriyorsa,
        // burada tekrar eklemeye gerek yok. Bu varsayımla devam ediliyor.
        // Eğer ID'ler prefix içermiyorsa, burada bir mantık eklenebilir.
        // log('debug', 'ChatOps:Add', `Kullanılacak son AI Model ID: ${finalAiModelId}`);


        const newChat = {
            id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            aiModelId: finalAiModelId,
            messages: [...initialMessages], // Başlangıç mesajlarını kopyala
            createdAt: Date.now(),
            lastActivity: Date.now(),
            isMinimized: false,
            inputHistory: [],
            historyIndex: -1 // Veya inputHistory.length
        };

        state.chats.push(newChat);
        log('info', 'ChatOps:Add', 'Yeni sohbet başarıyla eklendi.', newChat);

        renderChats();

        // Yeni eklenen ve görünür olan sohbete odaklan
        const newChatElement = elements.chatContainer.querySelector(`.chat-window[data-chat-id="${newChat.id}"]:not([style*="display: none"])`);
        if (newChatElement) {
            const inputField = newChatElement.querySelector('.chat-input');
            if (inputField) { // Elementin görünür olup olmadığını kontrol etmek daha iyi olabilir (offsetParent)
                setTimeout(() => inputField.focus(), 0); // DOM güncellemesinden sonra odaklan
            }
        }
        return newChat.id;
    }

    function removeChat(chatId, bypassHistory = false) {
        log('action', 'ChatOps:Remove', `Sohbet kaldırma denemesi: ${chatId}`, { bypassHistory });
        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);

        const performRemove = () => {
            const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
            if (chatIndex !== -1) {
                const chatToRemove = state.chats[chatIndex];
                const hasUserMessages = chatToRemove.messages && chatToRemove.messages.some(msg => msg.isUser);

                if (!bypassHistory && hasUserMessages) {
                    log('info', 'ChatOps:Remove', `Sohbet ${chatId} kullanıcı mesajlarına sahip. Geçmişe taşınıyor.`);
                    chatToRemove.closedTimestamp = Date.now();
                    if (!Array.isArray(state.chatHistory)) state.chatHistory = []; // Güvenlik kontrolü
                    state.chatHistory.unshift(chatToRemove); // Başa ekle
                    renderChatHistory(); // Geçmiş listesini hemen güncelle
                } else {
                    log('info', 'ChatOps:Remove', `Sohbet ${chatId} kullanıcı mesajlarına sahip değil veya geçmiş atlandı. Kalıcı olarak kaldırılıyor.`);
                }
                state.chats.splice(chatIndex, 1);
                log('info', 'ChatOps:Remove', `Sohbet ${chatId} durumdan kaldırıldı.`);

                if (chatWindow && chatWindow.parentNode) {
                    chatWindow.parentNode.removeChild(chatWindow);
                    log('debug', 'ChatOps:Remove', `Sohbet penceresi ${chatId} DOM'dan kaldırıldı.`);
                }
                renderChats(); // Düzeni ve dropdown'ı güncelle
            } else {
                log('warn', 'ChatOps:Remove', `Sohbet ${chatId} durum (state) içinde bulunamadı. DOM'dan kaldırılmaya çalışılıyor (eğer varsa).`);
                 if (chatWindow && chatWindow.parentNode) chatWindow.parentNode.removeChild(chatWindow); // Yine de DOM'dan kaldır
            }
        };

        if (chatWindow) {
            chatWindow.classList.add('closing'); // Animasyon için sınıf ekle
            // 'animationend' olayını dinlemek, animasyonun bitmesini bekler.
            const onAnimationEnd = () => {
                chatWindow.removeEventListener('animationend', onAnimationEnd);
                performRemove();
            };
            chatWindow.addEventListener('animationend', onAnimationEnd);

            // Fallback: Animasyon olayı tetiklenmezse (CSS yoksa veya hata varsa)
            setTimeout(() => {
                if (chatWindow.classList.contains('closing')) { // Hala kapanıyorsa ve olay tetiklenmediyse
                    log('warn', 'ChatOps:Remove', `Sohbet ${chatId} için 'animationend' olayı zaman aşımına uğradı. Zorla kaldırılıyor.`);
                    performRemove();
                }
            }, 700); // Animasyon süresinden biraz daha uzun (CSS'e göre ayarla, örn: 0.5s ise 700ms)
        } else {
            log('warn', 'ChatOps:Remove', `Kapanış animasyonu için ${chatId} ID'li sohbet penceresi elementi bulunamadı. Doğrudan kaldırılıyor.`);
            performRemove(); // DOM elementi yoksa doğrudan state'den kaldır
        }
    }

    function clearAllChats(includeStartedChats = false) {
        log('action', 'ChatOps:ClearAll', `Tüm sohbetleri temizleme çağrıldı. Başlamış olanlar dahil: ${includeStartedChats}`);
        const initialChatCount = state.chats.length;
        if (initialChatCount === 0) {
            log('info', 'ChatOps:ClearAll', 'Temizlenecek aktif sohbet yok.');
            alert('Temizlenecek aktif sohbet bulunmuyor.');
            return;
        }

        const chatsToRemove = [];
        const chatsToKeep = [];

        state.chats.forEach(chat => {
            const hasUserMessages = chat.messages && chat.messages.some(msg => msg.isUser);
            if (includeStartedChats || !hasUserMessages) {
                chatsToRemove.push(chat.id);
            } else {
                chatsToKeep.push(chat);
            }
        });

        if (chatsToRemove.length === 0) {
            log('info', 'ChatOps:ClearAll', 'Kriterlere uyan temizlenecek sohbet bulunamadı.');
            alert(includeStartedChats ? 'Tüm sohbetler zaten temiz veya bir hata oluştu.' : 'Temizlenecek kullanılmayan sohbet yok.');
            return;
        }

        log('info', 'ChatOps:ClearAll', `${chatsToRemove.length} sohbet temizlenmek üzere işaretlendi.`);
        chatsToRemove.forEach(chatId => {
            // removeChat fonksiyonu geçmişe ekleme mantığını zaten içeriyor.
            // Eğer includeStartedChats false ise, bypassHistory true olmalı ki boş sohbetler geçmişe gitmesin.
            removeChat(chatId, !includeStartedChats);
        });

        // state.chats = chatsToKeep; // removeChat zaten state'i güncelliyor, bu satır gereksiz olabilir.
        // renderChats(); // removeChat içinde çağrılıyor.

        const chatsRemovedCount = initialChatCount - state.chats.length; // state.chats güncel olduğu için
        if (chatsRemovedCount > 0) {
            log('info', 'ChatOps:ClearAll', `${chatsRemovedCount} sohbet başarıyla temizlendi.`);
            alert(`${chatsRemovedCount} sohbet temizlendi.`);
        } else {
             log('info', 'ChatOps:ClearAll', 'Hiçbir sohbet temizlenmedi (belki hepsi korunacak durumdaydı).');
        }
    }


    /**
     * 5.2. Mesajlaşma Sistemi (Messaging System)
     */
    async function sendMessage(chatId, text) {
        log('action', 'ChatOps:SendMsg', `Mesaj gönderiliyor: Chat ID ${chatId}`, { textPreview: text.substring(0, 30) });

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', 'ChatOps:SendMsg', `Sohbet bulunamadı: ${chatId}. Mesaj gönderilemedi.`);
            // Kullanıcıya bir geri bildirim verilebilir, örneğin ilgili sohbet penceresinde.
            return;
        }

        const userMessage = { isUser: true, text: text, timestamp: Date.now() };
        chat.messages.push(userMessage);
        chat.lastActivity = Date.now();
        // Input history eklenebilir (yukarı/aşağı oklarla gezinmek için)
        // chat.inputHistory.push(text);
        // chat.historyIndex = chat.inputHistory.length;

        const isUsersFirstMessageInChat = chat.messages.filter(m => m.isUser).length === 1;

        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        let messagesContainer;
        if (chatElement) {
            messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer) {
                // Önceki "hoşgeldin" mesajını temizle (eğer varsa ve bu ilk kullanıcı mesajıysa)
                if (isUsersFirstMessageInChat && messagesContainer.children.length === 1 && messagesContainer.firstElementChild.textContent.includes("Bugün size nasıl yardımcı olabilirim?")) {
                    // log('debug', 'ChatOps:SendMsg', 'İlk kullanıcı mesajı, hoşgeldin mesajı temizleniyor.', chatId);
                    // messagesContainer.innerHTML = ''; // Ya da sadece hoşgeldin mesajını sil
                }

                const userMessageHTML = createMessageHTML(userMessage, false, '', chat.aiModelId);
                messagesContainer.insertAdjacentHTML('beforeend', userMessageHTML);
                messagesContainer.scrollTop = messagesContainer.scrollHeight; // En alta kaydır

                if (isUsersFirstMessageInChat) {
                    log('info', 'ChatOps:SendMsg', `Bu, ${chatId} sohbetindeki ilk kullanıcı mesajı. Model seçimi kilitleniyor.`);
                    const chatTitle = chatElement.querySelector('.chat-title');
                    if (chatTitle) {
                        chatTitle.classList.remove('model-changeable');
                        chatTitle.classList.add('model-locked');
                        chatTitle.title = 'Model kilitli - konuşma zaten başladı';
                        const selectorIcon = chatTitle.querySelector('.model-selector-icon');
                        if (selectorIcon) {
                            const lockIcon = document.createElement('i');
                            lockIcon.className = 'bi bi-lock-fill model-locked-icon';
                            chatTitle.replaceChild(lockIcon, selectorIcon);
                        }
                        chatTitle.onclick = null; // Tıklama olayını kaldır
                    }
                    renderActiveChatsDropdown(); // Dropdown'daki durumu güncellemek için
                }
            } else {
                log('warn', 'ChatOps:SendMsg', `Mesaj konteyneri bulunamadı: ${chatId}`);
            }
        } else {
            log('warn', 'ChatOps:SendMsg', `Sohbet elementi DOM'da bulunamadı: ${chatId}`);
        }

        // AI Yanıtı için Yükleme Göstergesi
        let loadingElement = null;
        const aiModelForLoading = window.state.aiTypes.find(m => m.id === chat.aiModelId);
        const currentAiNameForLoading = aiModelForLoading ? aiModelForLoading.name : 'AI';
        const isFirstAIMessageOverall = chat.messages.filter(m => !m.isUser).length === 0;

        if (messagesContainer) {
            const loadingMessageData = { isUser: false, text: '', timestamp: Date.now() }; // text boş olacak, createMessageHTML'de loading dots eklenecek
            const loadingMessageHTML = createMessageHTML(
                loadingMessageData,
                isFirstAIMessageOverall,
                currentAiNameForLoading,
                chat.aiModelId
            );
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = loadingMessageHTML;
            loadingElement = tempDiv.firstElementChild;

            if (loadingElement) {
                loadingElement.classList.add('loading-dots'); // CSS'te .loading-dots tanımlanmalı
                const messageContentDiv = loadingElement.querySelector('.message-content');
                if (messageContentDiv) {
                    const dotsSpan = document.createElement('span');
                    dotsSpan.className = 'dots'; // CSS'te .dots ve içindeki span'ler için animasyon tanımlanmalı
                    dotsSpan.innerHTML = '<span>.</span><span>.</span><span>.</span>'; // Basit noktalar veya CSS ile animasyonlu
                    
                    // AI model göstergesinden sonra veya metin içeriğine ekle
                    const textContentDiv = messageContentDiv.querySelector('.text-content');
                    if (textContentDiv) { // text-content div'i renderTextContent tarafından oluşturulur
                        textContentDiv.innerHTML = ''; // Boş metin içeriğini temizle
                        textContentDiv.appendChild(dotsSpan);
                    } else { // Fallback, doğrudan messageContentDiv'e ekle
                        messageContentDiv.appendChild(dotsSpan);
                    }
                }
                messagesContainer.appendChild(loadingElement);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }

        try {
            log('debug', 'ChatOps:SendMsg:API', `API'ye gönderilecek mesaj geçmişi hazırlanıyor: ${chatId}`, { historyLength: chat.messages.length });
            // API'ye gönderilecek geçmişi hazırla (sadece kullanıcı ve model mesajları)
            const conversationHistoryForAPI = chat.messages
                .filter(msg => msg.text && String(msg.text).trim() !== '') // Boş AI yanıtlarını (örn. sadece yükleme) filtrele
                .map(msg => ({
                    role: msg.isUser ? 'user' : 'model', // veya 'assistant'
                    parts: [{ text: String(msg.text).trim() }]
                }));
            
            // Son kullanıcı mesajı zaten chat.messages'a eklendi, bu yüzden conversationHistoryForAPI'de olacak.
            // API'nin son mesajı ayrı mı yoksa geçmişin bir parçası olarak mı beklediğini kontrol et.
            // Mevcut kodda `message: text` ayrıca gönderiliyor, bu çift gönderime yol açabilir.
            // Genellikle tüm konuşma `history` içinde gönderilir.

            log('info', 'ChatOps:SendMsg:API', `AI yanıtı için istek gönderiliyor: ${chat.aiModelId}`, { chatId: chatId, historyLength: conversationHistoryForAPI.length });

            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({
                    chatId: chatId, // Backend'de loglama veya state yönetimi için
                    aiModelId: chat.aiModelId,
                    // message: text, // Bu satır gereksiz olabilir eğer history son mesajı içeriyorsa. API tasarımına bağlı.
                                     // Eğer API son mesajı history'den ayrı bekliyorsa kalsın.
                                     // Genellikle history son kullanıcı mesajını da içerir ve API bunu anlar.
                    history: conversationHistoryForAPI, // Tüm konuşma geçmişi
                }),
            });

            if (!response.ok) {
                let errorText = `Sunucu hatası: ${response.status} ${response.statusText}`;
                let errorData = null;
                try {
                    errorData = await response.json();
                    errorText = errorData.error || errorData.message || errorText;
                    log('warn', 'ChatOps:SendMsg:API', 'API Hata Detayı (JSON):', errorData);
                } catch (e) {
                    const rawErrorText = await response.text();
                    errorText = rawErrorText || errorText;
                    log('warn', 'ChatOps:SendMsg:API', 'API Hata Detayı (Text):', rawErrorText);
                }
                throw new Error(errorText);
            }

            const data = await response.json();
            const aiResponseText = data.response;

            if (!aiResponseText && typeof aiResponseText !== 'string') { // Yanıtın varlığını ve türünü kontrol et
                 log('warn', 'ChatOps:SendMsg:API', 'API yanıtı alındı ancak `response` alanı eksik veya geçersiz.', data);
                 throw new Error("AI'dan beklenen formatta bir yanıt alınamadı.");
            }

            log('info', 'ChatOps:SendMsg:API', 'AI yanıtı başarıyla alındı.', { responsePreview: String(aiResponseText).substring(0,50) });

            if (loadingElement && loadingElement.parentNode) {
                const aiMessage = { isUser: false, text: aiResponseText, timestamp: Date.now() };
                chat.messages.push(aiMessage); // AI yanıtını state'e ekle
                chat.lastActivity = Date.now();

                const finalMessageHTML = createMessageHTML(aiMessage, isFirstAIMessageOverall, currentAiNameForLoading, chat.aiModelId);
                const finalTempDiv = document.createElement('div');
                finalTempDiv.innerHTML = finalMessageHTML;
                const finalMessageElement = finalTempDiv.firstElementChild;

                loadingElement.parentNode.replaceChild(finalMessageElement, loadingElement);
                if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                log('warn', 'ChatOps:SendMsg:API', 'Yükleme elementi DOM\'da bulunamadı. AI yanıtı eklenemiyor veya fallback gerekiyor.');
                // Fallback: Eğer yükleme elementi yoksa, mesajı doğrudan eklemeye çalış (nadiren olmalı)
                if (messagesContainer) {
                    const aiMessage = { isUser: false, text: aiResponseText, timestamp: Date.now() };
                    chat.messages.push(aiMessage);
                    const fallbackHTML = createMessageHTML(aiMessage, isFirstAIMessageOverall, currentAiNameForLoading, chat.aiModelId);
                    messagesContainer.insertAdjacentHTML('beforeend', fallbackHTML);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }

        } catch (error) {
            log('error', 'ChatOps:SendMsg:Catch', 'Mesaj gönderme veya AI yanıtı alma sırasında kritik hata!', error, { chatId });
            const errorMessageText = `Üzgünüm, bir sorun oluştu ve yanıt alamadım. Lütfen tekrar deneyin. (Hata: ${error.message || 'Bilinmeyen sunucu hatası'})`;
            
            if (loadingElement && loadingElement.parentNode) {
                const aiErrorMessage = { isUser: false, text: errorMessageText, timestamp: Date.now(), isError: true };
                // chat.messages.push(aiErrorMessage); // Hata mesajlarını state'e eklemek isteğe bağlı
                
                const errorHTML = createMessageHTML(aiErrorMessage, false, "Sistem", chat.aiModelId);
                const errorTempDiv = document.createElement('div');
                errorTempDiv.innerHTML = errorHTML;
                const errorElement = errorTempDiv.firstElementChild;
                // errorElement.classList.add('error-message'); // createMessageHTML zaten ekliyor

                loadingElement.parentNode.replaceChild(errorElement, loadingElement);
                if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else if (messagesContainer) { // Yükleme elementi yoksa bile hata mesajını göster
                 const aiErrorMessage = { isUser: false, text: errorMessageText, timestamp: Date.now(), isError: true };
                 const errorHTML = createMessageHTML(aiErrorMessage, false, "Sistem", chat.aiModelId);
                 messagesContainer.insertAdjacentHTML('beforeend', errorHTML);
                 messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                log('error', 'ChatOps:SendMsg:Catch', 'Hata mesajı UI\'da gösterilemedi, yükleme ve mesaj konteyneri eksik.');
                alert(errorMessageText); // Son çare olarak alert
            }
        } finally {
            // renderActiveChatsDropdown(); // Her mesaj sonrası dropdown güncellemesi çok sık olabilir. Belki sadece model değişince veya sohbet eklenip/kaldırılınca.
                                        // Ancak sohbetin 'başlamış' durumunu yansıtmak için gerekli olabilir.
        }
    }


    /**
     * 5.3. Yayın Mesajları (Broadcast Messages)
     */
    function sendBroadcastMessage() {
        if (!elements.broadcastMessageInput) {
            log('warn', 'ChatOps:Broadcast', 'Yayın mesajı girişi bulunamadı.');
            alert("Yayın mesajı gönderme aracı bulunamadı.");
            return;
        }
        const messageText = elements.broadcastMessageInput.value.trim();

        if (messageText === '') {
            log('info', 'ChatOps:Broadcast', 'Yayın mesajı boş, gönderilmiyor.');
            alert("Lütfen göndermek için bir mesaj yazın.");
            elements.broadcastMessageInput.focus();
            return;
        }

        log('action', 'ChatOps:Broadcast', `Yayın mesajı gönderme denemesi: "${messageText}"`);
        const activeVisibleChats = state.chats.filter(chat => !chat.isMinimized);

        if (activeVisibleChats.length === 0) {
            log('info', 'ChatOps:Broadcast', 'Yayın yapılacak aktif (küçültülmemiş) sohbet yok.');
            alert('Mesaj gönderilecek aktif sohbet yok. Yeni bir sohbet oluşturun veya küçültülmüş birini geri yükleyin.');
            return;
        }

        log('info', 'ChatOps:Broadcast', `${activeVisibleChats.length} sohbete yayın mesajı gönderilecek.`);
        activeVisibleChats.forEach(chat => {
            log('debug', 'ChatOps:Broadcast', `Yayın mesajı ${chat.id} ID'li sohbete gönderiliyor.`);
            sendMessage(chat.id, `📢 **YAYIN:** ${messageText}`); // Mesajın yayın olduğunu belirt
        });

        elements.broadcastMessageInput.value = ''; // Girişi temizle
        log('info', 'ChatOps:Broadcast', 'Yayın mesajı gönderildi ve giriş temizlendi.');
        // elements.broadcastMessageInput.focus(); // İsteğe bağlı
    }


    //=============================================================================
    // 6. AI MODEL YÖNETİMİ (AI MODEL MANAGEMENT)
    //=============================================================================

    /**
     * 6.1. Model Seçimi Arayüzü (Model Selection UI)
     */
    function showModelDropdown(chatId, titleElement) {
        log('action', 'AIModel:ShowDropdown', `Model açılır menüsü gösteriliyor: ${chatId}`);

        // Mevcut tüm model dropdown'larını kapat
        document.querySelectorAll('.model-dropdown.show').forEach(openDropdown => {
            if (openDropdown.parentNode && openDropdown !== titleElement.nextElementSibling) { // Kendisi değilse
                 openDropdown.classList.remove('show');
                 setTimeout(() => { // Animasyon için
                    if(openDropdown.parentNode) openDropdown.parentNode.removeChild(openDropdown);
                 }, 300);
            }
        });

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', 'AIModel:ShowDropdown', `Sohbet bulunamadı: ${chatId}`);
            return;
        }
        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('info', 'AIModel:ShowDropdown', `Model zaten kilitli olduğu için dropdown gösterilmiyor: ${chatId}`);
            return; // Model kilitliyse dropdown gösterme
        }

        if (!window.state || !window.state.aiTypes || window.state.aiTypes.length === 0) {
            log('error', 'AIModel:ShowDropdown', 'Kullanılabilir AI modelleri (window.state.aiTypes) bulunamadı.');
            alert('AI Modelleri yüklenmedi veya bulunamadı. Model değiştirilemiyor.');
            return;
        }

        const dropdown = document.createElement('div');
        dropdown.className = 'model-dropdown'; // CSS'te stil tanımlanmalı

        const optionsHTML = window.state.aiTypes.map(model => {
            const isSelected = model.id === chat.aiModelId;
            return `
                <div class="model-option ${isSelected ? 'selected active' : ''}" data-model-id="${model.id}" title="${model.description || model.name}">
                    <i class="${model.icon || 'bi bi-cpu'} me-2"></i>
                    <span>${model.name || 'Bilinmeyen Model'}</span>
                    ${isSelected ? '<i class="bi bi-check-lg ms-auto"></i>' : ''}
                </div>
            `;
        }).join('');

        dropdown.innerHTML = `<div class="list-group list-group-flush">${optionsHTML}</div>`;
        
        // Dropdown'ı titleElement'in hemen altına yerleştir
        titleElement.parentNode.insertBefore(dropdown, titleElement.nextSibling);

        // Konumlandırma (CSS ile daha iyi yönetilebilir, ama JS ile de ayarlanabilir)
        // Basitlik için, CSS'in .chat-header'ı position:relative yapması ve .model-dropdown'un position:absolute olması beklenir.
        // dropdown.style.top = `${titleElement.offsetHeight}px`;
        // dropdown.style.left = `0`;
        // dropdown.style.width = `${titleElement.offsetWidth}px`; // Başlık genişliğinde yap

        // Göstermek için 'show' sınıfını ekle (Bootstrap benzeri)
        // requestAnimationFrame veya setTimeout(0) ile DOM'a eklendikten sonra sınıf eklemek animasyonları tetikleyebilir.
        requestAnimationFrame(() => {
            dropdown.classList.add('show');
        });


        dropdown.querySelectorAll('.model-option').forEach(option => {
            option.onclick = (e) => {
                e.stopPropagation(); // Olayın dışarıya yayılmasını engelle
                const newModelId = option.getAttribute('data-model-id');
                log('action', 'AIModel:ShowDropdown:Select', `Model seçildi: ${newModelId} (Chat ID: ${chatId})`);
                if (newModelId && newModelId !== chat.aiModelId) {
                    changeAIModel(chatId, newModelId);
                }
                // Dropdown'ı kapat
                dropdown.classList.remove('show');
                setTimeout(() => { // Animasyon için
                    if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
                }, 300); // CSS animasyon süresiyle eşleşmeli
            };
        });

        // Dışarı tıklandığında kapatma işlevselliği
        const handleClickOutside = (event) => {
            if (!dropdown.contains(event.target) && event.target !== titleElement && !titleElement.contains(event.target)) {
                log('debug', 'AIModel:ShowDropdown:OutsideClick', 'Dışarı tıklandı, dropdown kapatılıyor.');
                dropdown.classList.remove('show');
                setTimeout(() => {
                    if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
                }, 300);
                document.removeEventListener('click', handleClickOutside, true); // Dinleyiciyi kaldır
            }
        };
        // Olayı capture fazında eklemek, diğer tıklama olaylarından önce çalışmasını sağlar ve stopPropagation ile engellenebilir.
        document.addEventListener('click', handleClickOutside, true);
    }

    /**
     * 6.2. Model Değiştirme Mantığı (Model Changing Logic)
     */
    function changeAIModel(chatId, newAiModelId) {
        log('action', 'AIModel:Change', `Sohbet için AI modeli değiştiriliyor: ${chatId}, Yeni Model ID: ${newAiModelId}`);

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', 'AIModel:Change', `Sohbet bulunamadı: ${chatId}`);
            return;
        }

        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('warn', 'AIModel:Change', `Model değiştirilemiyor: sohbette zaten mesaj var (${chatId}). Bu durumun oluşmaması gerekirdi.`);
            alert('Konuşma başladıktan sonra AI modeli değiştirilemez.');
            return;
        }

        if (!window.state || !window.state.aiTypes) {
            log('error', 'AIModel:Change', 'window.state.aiTypes mevcut değil.');
            alert('AI Modelleri yüklenemedi. Model değiştirilemiyor.');
            return;
        }

        const newModel = window.state.aiTypes.find(m => m.id === newAiModelId);
        if (!newModel) {
            log('error', 'AIModel:Change', `Geçersiz yeni AI Model ID: ${newAiModelId}. Model listesinde bulunamadı.`);
            alert('Geçersiz AI Modeli seçildi. Lütfen tekrar deneyin.');
            return;
        }

        const oldModelId = chat.aiModelId;
        chat.aiModelId = newAiModelId;
        log('info', 'AIModel:Change', `Sohbet ${chatId} AI modeli güncellendi: ${oldModelId} -> ${newAiModelId}`);

        // UI'ı güncelle
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            const chatTitleElement = chatElement.querySelector('.chat-title');
            if (chatTitleElement) {
                const iconElement = chatTitleElement.querySelector('i:first-child');
                const nameElement = chatTitleElement.querySelector('span');
                if (iconElement) iconElement.className = newModel.icon || 'bi bi-cpu';
                if (nameElement) nameElement.textContent = `${newModel.name || 'Bilinmeyen Model'} (ID: ${chat.id.slice(-4)})`;
                log('debug', 'AIModel:Change', `Sohbet başlığı güncellendi: ${chatId}`);
            }

            // Hoşgeldin mesajını güncelle (eğer mesaj yoksa)
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer && (!chat.messages || chat.messages.length === 0)) {
                messagesContainer.innerHTML = createWelcomeMessageHTML(newModel.name || 'Seçilen AI');
                log('debug', 'AIModel:Change', `Hoşgeldin mesajı yeni modelle güncellendi: ${chatId}`);
            }
        } else {
            log('warn', 'AIModel:Change', `${chatId} ID'li sohbet elementi UI güncellemesi için bulunamadı. renderChats() çağrılabilir.`);
            // renderChats(); // Gerekirse tüm sohbetleri yeniden çiz (genellikle gerekmez)
        }
        renderActiveChatsDropdown(); // Kenar çubuğundaki dropdown'ı da güncelle
    }

    /**
     * 6.3. AI Yanıt Üretimi (Simüle Edilmiş)
     * NOT: Bu fonksiyon artık doğrudan sendMessage içindeki API çağrısı ile yer değiştirdi.
     * Test veya offline mod için saklanabilir.
     */
    function getAIResponse_simulated(userMessage, aiModelId) {
        log('debug', 'AIModel:GetResponseSim', `Simüle AI yanıtı üretiliyor (AKTİF KULLANIMDA DEĞİL): Model ${aiModelId}`, { userMessage });
        // ... (eski simülasyon kodu)
        return "Bu simüle edilmiş bir yanıttır.";
    }


    //=============================================================================
    // 7. MEDYA İŞLEMLERİ (MEDIA HANDLING)
    //=============================================================================
    function downloadMedia(mediaSrc, defaultFileName = 'downloaded-media') {
        log('action', 'Media:Download', 'Medya indirme isteği', { mediaSrc, defaultFileName });
        if (!mediaSrc || typeof mediaSrc !== 'string') {
            log('error', 'Media:Download', 'Geçersiz medya kaynağı sağlandı.', mediaSrc);
            alert('İndirilecek medya kaynağı bulunamadı veya geçersiz.');
            return;
        }
        try {
            const link = document.createElement('a');
            link.href = mediaSrc;
            
            // Dosya adını ve uzantısını belirlemeye çalış
            let fileName = defaultFileName;
            try {
                const url = new URL(mediaSrc.startsWith('data:') ? 'http://localhost' : mediaSrc); // data URL için geçici host
                const pathName = url.pathname;
                const lastSegment = pathName.substring(pathName.lastIndexOf('/') + 1);
                if (lastSegment && lastSegment.includes('.')) { // Uzantı var gibi görünüyor
                    fileName = lastSegment;
                } else { // Uzantı yoksa veya data URL ise, MIME türünden tahmin et
                    if (mediaSrc.startsWith('data:image/png')) fileName = `${defaultFileName}-${Date.now()}.png`;
                    else if (mediaSrc.startsWith('data:image/jpeg')) fileName = `${defaultFileName}-${Date.now()}.jpg`;
                    else if (mediaSrc.startsWith('data:audio/mpeg')) fileName = `${defaultFileName}-${Date.now()}.mp3`;
                    else if (mediaSrc.startsWith('data:audio/wav')) fileName = `${defaultFileName}-${Date.now()}.wav`;
                    else fileName = `${defaultFileName}-${Date.now()}`; // Genel fallback
                }
            } catch (e) {
                log('warn', 'Media:Download', 'Dosya adı URL\'den çıkarılamadı, varsayılan kullanılıyor.', e);
                 if (mediaSrc.startsWith('data:image/png')) fileName = `${defaultFileName}-${Date.now()}.png`;
                 else fileName = `${defaultFileName}-${Date.now()}`;
            }

            link.download = fileName;
            document.body.appendChild(link); // Firefox için gerekli olabilir
            link.click();
            document.body.removeChild(link); // Temizle
            log('info', 'Media:Download', `Medya indirme işlemi başlatıldı: ${fileName}`);
        } catch (error) {
            log('error', 'Media:Download', 'Medya indirilirken hata oluştu!', error, { mediaSrc });
            alert(`Medya indirilirken bir sorun oluştu: ${error.message}`);
        }
    }

    function downloadImage(imageData) {
        downloadMedia(imageData, 'ai-image');
    }

    function downloadAudio(audioData) {
        downloadMedia(audioData, 'ai-audio');
    }

    function viewFullImage(imageData) {
        log('action', 'Media:ViewFullImage', 'Tam ekran resim görüntüleme isteği');
        if (!imageData || typeof imageData !== 'string') {
            log('error', 'Media:ViewFullImage', 'Geçersiz resim verisi.', imageData);
            alert('Görüntülenecek resim bulunamadı veya geçersiz.');
            return;
        }

        // Mevcut modal varsa kaldır
        const existingModal = document.querySelector('.image-modal-zk');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.className = 'image-modal-zk'; // CSS'te stil tanımlanmalı (örn: position fixed, z-index, background)
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.8); display: flex;
            align-items: center; justify-content: center; z-index: 2000;
            padding: 20px; box-sizing: border-box;
        `;

        modal.innerHTML = `
            <div class="image-modal-content-zk" style="max-width: 90%; max-height: 90%; position: relative;">
                <img src="${imageData}" alt="AI Tarafından Oluşturulan Resim (Tam Ekran)" style="max-width: 100%; max-height: 100%; display: block; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.5);">
                <button class="close-modal-btn-zk" title="Kapat (Esc)" style="position: absolute; top: 10px; right: 10px; background: white; border: none; border-radius: 50%; width: 30px; height: 30px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">&times;</button>
            </div>
        `;

        const closeModal = () => {
            if (modal.parentNode) {
                modal.remove();
            }
            document.removeEventListener('keydown', handleEscapeKey);
            log('info', 'Media:ViewFullImage', 'Tam ekran resim kapatıldı.');
        };

        modal.addEventListener('click', (e) => {
            // Sadece modal arka planına veya kapatma düğmesine tıklanınca kapat
            if (e.target === modal || e.target.closest('.close-modal-btn-zk')) {
                closeModal();
            }
        });

        const handleEscapeKey = (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        };
        document.addEventListener('keydown', handleEscapeKey);
        document.body.appendChild(modal);
        log('info', 'Media:ViewFullImage', 'Tam ekran resim gösterildi.');
    }


    //=============================================================================
    // 8. GENEL API VE BAŞLATMA (PUBLIC API & INITIALIZATION)
    //=============================================================================

    function init() {
        log('info', 'Init', 'ChatManager başlatılıyor...', { version: "1.0.2" });

        if (!initElements()) {
            log('error', 'Init', 'ChatManager başlatılamadı: Gerekli DOM elementleri bulunamadı. Lütfen HTML yapısını kontrol edin.');
            // Kullanıcıya bir uyarı gösterilebilir.
            const body = document.querySelector('body');
            if (body) {
                 const errorMsgDiv = document.createElement('div');
                 errorMsgDiv.innerHTML = '<p style="background-color: red; color: white; padding: 10px; text-align: center; position: fixed; top:0; left:0; width:100%; z-index:9999;">Hata: Sohbet arayüzü başlatılamadı. Lütfen konsolu kontrol edin.</p>';
                 body.prepend(errorMsgDiv);
            }
            return; // Başlatmayı durdur
        }

        setupGlobalHandlers();

        // Kenar çubuğundaki AI Model seçicilerine olay dinleyicileri ekle
        const aiModelSelectorItems = document.querySelectorAll('.ai-model-selector-item');
        if (aiModelSelectorItems.length > 0) {
            aiModelSelectorItems.forEach(item => {
                // Eski dinleyiciyi kaldır (eğer varsa - birden fazla init çağrısını engellemek için)
                if (item._chatManagerClickListener) {
                    item.removeEventListener('click', item._chatManagerClickListener);
                }
                // Yeni dinleyiciyi tanımla ve sakla
                item._chatManagerClickListener = function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    // HTML'de data-ai-index kullanıldığını biliyoruz, dataset'te camelCase olarak aiIndex olarak erişilir
                    const modelId = this.dataset.aiIndex;
                    log('action', 'Init:SidebarModelClick', `Kenar çubuğu model seçildi: ${modelId}`);
                    if (modelId) {
                        log('debug', 'Init:SidebarModelClick', `Sohbet başlatılıyor: Model ID = ${modelId}`);
                        addChat(modelId);
                        // Aktif sınıfını yönet (isteğe bağlı, eğer CSS ile yapılmıyorsa)
                        // aiModelSelectorItems.forEach(i => i.classList.remove('active'));
                        // this.classList.add('active');
                    } else {
                        log('error', 'Init:SidebarModelClick', 'Kenar çubuğundan geçersiz AI model ID seçildi.', { dataset: this.dataset });
                        alert("Geçersiz model seçimi.");
                    }
                };
                item.addEventListener('click', item._chatManagerClickListener);
            });
            log('info', 'Init', `${aiModelSelectorItems.length} adet kenar çubuğu AI model seçiciye olay dinleyici eklendi.`);
        } else {
            log('warn', 'Init', 'Kenar çubuğunda AI model seçici öğe (.ai-model-selector-item) bulunamadı.');
        }

        renderChats(); // Başlangıçta sohbetleri (veya hoşgeldin ekranını) oluştur
        renderChatHistory(); // Başlangıçta geçmişi oluştur
        log('info', 'Init', 'ChatManager başarıyla başlatıldı ve ilk oluşturma tamamlandı.');
    }

    return {
        init,
        addChat,
        removeChat,
        clearAllChats,
        sendMessage,
        sendBroadcastMessage,
        // Medya işlemleri için public API
        downloadImage,
        viewFullImage,
        downloadAudio,
        // Hata ayıklama için state'e erişim (sadece geliştirme sırasında)
        _getState: () => JSON.parse(JSON.stringify(state)),
        _getElements: () => elements,
        _log: log // Geliştirme konsolundan manuel loglama için
    };
})();

window.ChatManager = ChatManager;

document.addEventListener('DOMContentLoaded', () => {
    // Global log fonksiyonunu test et
    // ChatManager._log('info', 'DOMContentLoaded', 'DOM yüklendi, ChatManager başlatılacak.');
    // ChatManager._log('debug', 'DOMContentLoaded', 'Test debug mesajı.');
    // ChatManager._log('action', 'DOMContentLoaded', 'Test eylem mesajı.');
    // ChatManager._log('warn', 'DOMContentLoaded', 'Test uyarı mesajı.');
    // ChatManager._log('error', 'DOMContentLoaded', 'Test hata mesajı.', { detail1: "ek bilgi", detail2: { nested: true }});

    ChatManager.init();

    // AI kategori akordeon chevron animasyonları (Bootstrap kullanılıyorsa)
    const aiCategoriesAccordion = document.getElementById('aiCategoriesAccordion');
    if (aiCategoriesAccordion && typeof bootstrap !== 'undefined') { // Bootstrap varlığını kontrol et
        const collapseElements = aiCategoriesAccordion.querySelectorAll('.collapse');
        collapseElements.forEach(collapseEl => {
            const header = collapseEl.previousElementSibling; // .accordion-header
            const chevron = header ? header.querySelector('.category-chevron') : null;

            if (chevron) {
                collapseEl.addEventListener('show.bs.collapse', function () {
                    // ChatManager._log('debug', 'AccordionEvent', `Akordeon açılıyor: ${this.id}`);
                    chevron.classList.remove('bi-chevron-down');
                    chevron.classList.add('bi-chevron-up');
                });
                collapseEl.addEventListener('hide.bs.collapse', function () {
                    // ChatManager._log('debug', 'AccordionEvent', `Akordeon kapanıyor: ${this.id}`);
                    chevron.classList.remove('bi-chevron-up');
                    chevron.classList.add('bi-chevron-down');
                });
            }
        });
    } else if (aiCategoriesAccordion) {
        ChatManager._log('warn', 'DOMContentLoaded', 'Akordeon bulundu ancak Bootstrap globalde tanımlı değil. Chevron animasyonları çalışmayabilir.');
    }
});