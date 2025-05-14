/**
 * ZekAI Sohbet Bileşeni Modülü
 * ===========================
 * @description AI sohbet pencerelerini, düzenlerini ve kullanıcı etkileşimlerini yönetir
 * @version 1.0.1 (Yeniden Düzenlendi)
 * @author ZekAI Team
 *
 * İÇİNDEKİLER
 * ================
 * 1. TEMEL SİSTEM (CORE SYSTEM)
 * 1.1. Günlükleme Sistemi (Logging System)
 * 1.2. Durum Yönetimi (State Management)
 * 1.3. DOM Elementleri (DOM Elements)
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
     * 1.1. Günlükleme Sistemi (Logging System)
     * ------------------------------------
     * Hata ayıklama, bilgi, eylem, uyarı ve hata seviyelerinde günlükleme sağlar.
     */
    window.DEBUG_LOG = true; // Günlükleri susturmak için false yapın
    const LOG_LEVELS = ['debug', 'info', 'action', 'warn', 'error'];

    /**
     * Mesajı zaman damgası ve seviyeye göre renk kodlamasıyla günlükler.
     * @param {string} level - Günlük seviyesi (debug|info|action|warn|error)
     * @param {string} msg - Günlüklenecek mesaj
     * @param {...any} args - Günlüklenecek ek argümanlar
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
     * 1.2. Durum Yönetimi (State Management)
     * ----------------------------------
     * Sohbetleri, geçmişi ve yapılandırmayı yönetmek için özel durum (state).
     */
    const state = {
        chats: [],         // Aktif sohbet pencereleri
        chatHistory: [],   // Mesajları olan kapatılmış sohbetler
        maxChats: 6        // Maksimum eşzamanlı sohbet penceresi sayısı
    };

    // Global durumu başlat veya mevcut olanı kullan
    if (window.state) {
        if (!window.state.chats) window.state.chats = state.chats;
        if (!window.state.chatHistory) window.state.chatHistory = state.chatHistory;
        if (!window.state.aiTypes) window.state.aiTypes = [];
    } else {
        window.state = {
            chats: state.chats,
            chatHistory: state.chatHistory,
            aiTypes: [] // index.html tarafından doldurulacak
        };
    }

    /**
     * 1.3. DOM Elementleri (DOM Elements)
     * -------------------------------
     * Önemli DOM elementlerine referanslar.
     */
    let elements = {}; // Başlangıçta boş obje

    /**
     * Gerekli tüm DOM element referanslarını başlatır.
     * @returns {boolean} Tüm kritik elementler bulunursa true, aksi takdirde false.
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
            activeChatsList: document.getElementById('active-chats-list'),
            broadcastMessageInput: document.getElementById('broadcast-message-input'),
            sendBroadcastBtn: document.getElementById('send-broadcast-btn'),
            chatHistoryTrigger: document.getElementById('chat-history-trigger'),
            chatHistoryMenu: document.getElementById('chat-history-menu'),
            chatHistoryList: document.getElementById('chat-history-list'),
        };

        if (!elements.chatContainer) {
            log('error', 'Sohbet konteyner elementi bulunamadı');
            return false;
        }
        return true;
    }

    //=============================================================================
    // 2. KULLANICI ARAYÜZÜ BİLEŞENLERİ (UI COMPONENTS)
    //=============================================================================

    /**
     * 2.1. Sohbet Elementi Fabrikaları (Chat Element Factories)
     * -----------------------------------------------------
     */

    /**
     * Yeni bir sohbet penceresi DOM elementi oluşturur.
     * @param {Object} chatData - id, aiModelId, messages özelliklerine sahip sohbet veri objesi.
     * @returns {HTMLElement} DOM'a eklenmeye hazır tam sohbet penceresi elementi.
     */
    function createChatElement(chatData) {
        log('debug', 'Sohbet elementi oluşturuluyor', chatData);

        const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) ||
                        (window.state.aiTypes && window.state.aiTypes.length > 0 ? window.state.aiTypes[0] : null) ||
                        { name: `Bilinmeyen AI (ID: ${chatData.aiModelId})`, icon: 'bi bi-question-circle' };

        const chatWindow = document.createElement('div');
        chatWindow.className = 'chat-window';
        chatWindow.setAttribute('data-chat-id', chatData.id);

        const isModelLocked = chatData.messages && chatData.messages.some(msg => msg.isUser);
        const modelSelectionClass = isModelLocked ? 'model-locked' : 'model-changeable';
        const modelSelectionTitle = isModelLocked ? 'Model kilitli - konuşma zaten başladı' : 'AI modelini değiştirmek için tıklayın';

        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-title ${modelSelectionClass}" title="${modelSelectionTitle}">
                    <i class="${aiModel.icon}"></i>
                    <span>${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
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
                    chatData.messages.map(msg => createMessageHTML(msg, !msg.isUser && chatData.messages.filter(m => !m.isUser).indexOf(msg) === 0, aiModel.name, chat.aiModelId)).join('') : // aiModelId eklendi
                    createWelcomeMessageHTML(aiModel.name)
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
        return chatWindow;
    }

    /**
     * 2.2. Mesaj HTML Üreteçleri (Message HTML Generators)
     * --------------------------------------------------
     */

    /**
     * Tek bir sohbet mesajı için HTML işaretlemesi oluşturur.
     * @param {Object} message - isUser, text, timestamp özelliklerine sahip mesaj verisi.
     * @param {boolean} isFirstAIMessage - Bu, konuşmadaki ilk AI mesajı mı.
     * @param {string} aiName - AI modelinin adı (sadece ilk AI mesajı için kullanılır).
     * @param {string} aiModelId - AI model ID'si (içerik oluşturma için).
     * @returns {string} Mesaj için HTML işaretlemesi.
     */
    function createMessageHTML(message, isFirstAIMessage = false, aiName = '', aiModelId = '') {
        const messageClass = message.isUser ? 'user-message' : 'ai-message';
        const timestamp = new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let messageContent = message.isUser ? renderTextContent(message.text) : renderContent(message.text, aiModelId); // Her zaman renderContent kullan

        if (!message.isUser && aiName) { // aiName kontrolü AI mesajları için geçerli
             // İlk AI mesajıysa veya her AI mesajında model belirtmek isteniyorsa bu kısım ayarlanabilir.
             // Mevcut mantık: Eğer aiName verilmişse (genellikle ilk AI mesajı için), model göstergesini ekle.
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
     * Bir sohbet ilk açıldığında gösterilen hoş geldin mesajı için HTML işaretlemesi oluşturur.
     * @param {string} aiName - AI modelinin adı.
     * @returns {string} Hoş geldin mesajı için HTML işaretlemesi.
     */
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
     * 2.3. İçerik Oluşturucuları (Content Renderers)
     * --------------------------------------------
     * Farklı AI model türlerine göre içeriği oluşturur.
     */

    /**
     * AI model türüne göre içeriği oluşturur.
     * @param {string} content - Oluşturulacak içerik.
     * @param {string} aiModelId - AI model ID'si.
     * @returns {string} Oluşturulmuş HTML içeriği.
     */
    function renderContent(content, aiModelId) {
        const aiType = aiModelId.split('_')[0]; // Model ID önekinden AI türünü al

        switch (aiType) {
            case 'img':
                return renderImageContent(content);
            case 'aud':
                return renderAudioContent(content);
            case 'txt':
            default:
                return renderTextContent(content);
        }
    }

    /**
     * Metin içeriğini oluşturur.
     * @param {string} content - Metin içeriği.
     * @returns {string} HTML işaretlemesi.
     */
    function renderTextContent(content) {
        // Basit metin için HTML'e dönüştürme (güvenlik için sanitize edilebilir)
        const sanitizedContent = String(content).replace(/</g, "&lt;").replace(/>/g, "&gt;");
        return `<div class="text-content">${sanitizedContent}</div>`;
    }

    /**
     * Resim içeriğini oluşturur.
     * @param {string} content - Resim URL'si veya base64 verisi.
     * @returns {string} HTML işaretlemesi.
     */
    function renderImageContent(content) {
        return `
            <div class="image-content">
                <img src="${content}" alt="AI Tarafından Oluşturulan Resim" class="ai-generated-image">
                <div class="image-controls">
                    <button class="btn btn-sm btn-primary download-image" onclick="ChatManager.downloadImage('${content}')"><i class="bi bi-download"></i> İndir</button>
                    <button class="btn btn-sm btn-secondary view-image" onclick="ChatManager.viewFullImage('${content}')"><i class="bi bi-arrows-fullscreen"></i> Tam Ekran</button>
                </div>
            </div>
        `;
    }

    /**
     * Ses içeriğini oluşturur.
     * @param {string} content - Ses URL'si veya base64 verisi.
     * @returns {string} HTML işaretlemesi.
     */
    function renderAudioContent(content) {
        return `
            <div class="audio-content">
                <audio controls>
                    <source src="${content}" type="audio/mpeg">
                    Tarayıcınız ses elementini desteklemiyor.
                </audio>
                <button class="btn btn-sm btn-primary download-audio" onclick="ChatManager.downloadAudio('${content}')"><i class="bi bi-download"></i> İndir</button>
            </div>
        `;
    }


    //=============================================================================
    // 3. OLUŞTURMA FONKSİYONLARI (RENDERING FUNCTIONS)
    //=============================================================================

    /**
     * 3.1. Sohbet Pencereleri (Chat Windows)
     * ----------------------------------
     * Tüm aktif sohbet pencerelerini oluşturur ve sayıya göre düzeni yönetir.
     * Karşılama ekranı görünürlüğünü ve sohbet penceresi düzenlemesini yönetir.
     */
    function renderChats() {
        log('debug', 'Sohbetler oluşturuluyor. Mevcut durum:', JSON.parse(JSON.stringify(state.chats)));

        if (!elements.chatContainer) {
            log('error', 'Sohbetler oluşturulamıyor: sohbet konteyneri bulunamadı');
            return;
        }

        elements.chatContainer.innerHTML = ''; // Konteyneri temizle

        const activeChats = state.chats.filter(chat => !chat.isMinimized);

        if (activeChats.length === 0) { // Hiç aktif (küçültülmemiş) sohbet yoksa veya hiç sohbet yoksa
            elements.chatContainer.appendChild(elements.welcomeScreen);
             // Hoşgeldin ekranı için layout sınıfını ayarla veya kaldır
            elements.chatContainer.className = 'flex-grow-1 d-flex flex-wrap justify-content-center align-items-center'; // Merkezi yerleşim
            if (elements.welcomeScreen.parentNode !== elements.chatContainer) { // Eğer zaten ekli değilse ekle
                elements.chatContainer.appendChild(elements.welcomeScreen);
            }
            renderActiveChatsDropdown(); // Küçültülmüş sohbetler varsa bile dropdown güncellenmeli
            return;
        }
        
        // Karşılama ekranını kaldır (eğer varsa ve aktif sohbetler varsa)
        if (elements.welcomeScreen.parentNode === elements.chatContainer) {
            elements.chatContainer.removeChild(elements.welcomeScreen);
        }
        
        let layoutClass;
        switch (activeChats.length) {
            case 1: layoutClass = 'layout-1'; break;
            case 2: layoutClass = 'layout-2'; break;
            case 3: layoutClass = 'layout-3'; break;
            case 4: layoutClass = 'layout-4'; break;
            case 5: layoutClass = 'layout-5'; break;
            case 6: layoutClass = 'layout-6'; break;
            default: layoutClass = 'layout-6'; break;
        }

        elements.chatContainer.className = `flex-grow-1 d-flex flex-wrap ${layoutClass}`;

        activeChats.forEach(chatData => {
            const chatElement = createChatElement(chatData);
            elements.chatContainer.appendChild(chatElement);
            setupChatWindowControls(chatElement); // Yeniden adlandırıldı: setupChatControls -> setupChatWindowControls
        });
        renderActiveChatsDropdown();
    }

    /**
     * 3.2. Aktif Sohbetler Açılır Menüsü (Active Chats Dropdown)
     * ------------------------------------------------------
     * Kenar çubuğundaki aktif sohbetler açılır menüsünü oluşturur.
     * Vurgulama veya küçültülmüş sohbetleri geri yükleme seçenekleriyle tüm aktif sohbetleri gösterir.
     */
    function renderActiveChatsDropdown() {
        if (!elements.activeChatsList || !elements.activeChatsDropdownMenu || !elements.activeChatsDropdownTrigger) {
            log('warn', 'Aktif sohbetler açılır menü elementleri bulunamadı');
            return;
        }

        elements.activeChatsList.innerHTML = '';

        if (state.chats.length === 0) {
            elements.activeChatsDropdownTrigger.classList.add('disabled');
            elements.activeChatsDropdownMenu.classList.remove('show');
            const noChatsLi = document.createElement('li');
            noChatsLi.className = 'list-group-item text-muted';
            noChatsLi.textContent = 'Aktif sohbet yok';
            noChatsLi.style.paddingLeft = '1rem';
            elements.activeChatsList.appendChild(noChatsLi);
            elements.activeChatsDropdownTrigger.setAttribute('aria-expanded', 'false');
            return;
        }

        elements.activeChatsDropdownTrigger.classList.remove('disabled');
        // Yeni sohbet eklendiğinde veya render edildiğinde dropdown'ı açık tutmak yerine,
        // kullanıcının etkileşimine bırakmak daha iyi olabilir. Ancak mevcut davranış korunuyor.
        // elements.activeChatsDropdownMenu.classList.add('show'); 
        // elements.activeChatsDropdownTrigger.setAttribute('aria-expanded', 'true');


        state.chats.forEach(chatData => {
            const aiModel = window.state.aiTypes.find(m => m.id === chatData.aiModelId) || { name: `AI (${chatData.aiModelId ? chatData.aiModelId.slice(-4) : 'Bilinmeyen'})`, icon: 'bi bi-cpu' };
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex align-items-center justify-content-between';
            listItem.setAttribute('data-chat-id', chatData.id);
            listItem.style.paddingLeft = '1rem';
            listItem.style.paddingRight = '1rem';

            // Sohbetin başlayıp başlamadığını kontrol et
            if (chatData.messages && chatData.messages.some(msg => msg.isUser)) { // Sadece kullanıcı mesajı varsa 'başlamış' say
                listItem.classList.add('active-chat-item--started');
            }

            let chatNameHTML = `
                <span class="d-flex align-items-center" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-grow: 1; margin-right: 0.5rem;">
                    <i class="${aiModel.icon} me-2"></i>
                    <span>${aiModel.name} (ID: ${chatData.id.slice(-4)})</span>
                </span>`;

            if (chatData.isMinimized) {
                listItem.classList.add('active-chat-item--minimized');
                listItem.innerHTML = chatNameHTML + '<span class="ms-auto flex-shrink-0"><i class="bi bi-window-plus" title="Sohbeti Geri Yükle"></i></span>';
                listItem.onclick = (e) => {
                    e.stopPropagation();
                    const chatToRestore = state.chats.find(c => c.id === chatData.id);
                    if (chatToRestore) {
                        chatToRestore.isMinimized = false;
                        renderChats(); // Bu renderActiveChatsDropdown'ı da çağırır
                    }
                };
            } else {
                listItem.innerHTML = chatNameHTML;
                listItem.onclick = () => {
                    log('action', `Aktif sohbet öğesi tıklandı: ${chatData.id}. Sohbet penceresi vurgulanıyor.`);
                    const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatData.id}"]`);
                    if (chatWindow) {
                        chatWindow.classList.add('chat-window--highlighted');
                        setTimeout(() => {
                            chatWindow.classList.remove('chat-window--highlighted');
                        }, 2000);
                    }
                };
            }
            elements.activeChatsList.appendChild(listItem);
        });
    }

    /**
     * 3.3. Sohbet Geçmişi (Chat History)
     * -------------------------------
     * Kenar çubuğundaki sohbet geçmişi listesini oluşturur.
     * Geri yüklenebilen veya görüntülenebilen kapatılmış sohbetleri gösterir.
     */
    function renderChatHistory() {
        if (!elements.chatHistoryList || !elements.chatHistoryTrigger || !elements.chatHistoryMenu) {
            log('warn', 'Sohbet geçmişi elementleri DOM\'da bulunamadı.');
            return;
        }

        elements.chatHistoryList.innerHTML = '';

        if (state.chatHistory.length === 0) {
            elements.chatHistoryTrigger.classList.add('disabled');
            elements.chatHistoryMenu.classList.remove('show');
            const noHistoryLi = document.createElement('li');
            noHistoryLi.className = 'list-group-item text-muted';
            noHistoryLi.textContent = 'Sohbet geçmişi yok';
            noHistoryLi.style.paddingLeft = '1rem';
            elements.chatHistoryList.appendChild(noHistoryLi);
            elements.chatHistoryTrigger.setAttribute('aria-expanded', 'false');
            return;
        }

        elements.chatHistoryTrigger.classList.remove('disabled');

        state.chatHistory.forEach(chat => {
            const aiModelInfo = window.state.aiTypes.find(ai => ai.id === chat.aiModelId) || { name: 'Bilinmeyen AI', icon: 'bi bi-archive' };
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item list-group-item-action active-chat-item d-flex justify-content-between align-items-center';
            listItem.setAttribute('data-chat-id', chat.id);
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
            iconElement.className = `${aiModelInfo.icon} me-2`;

            const nameSpanElement = document.createElement('span');
            let historyItemText = aiModelInfo.name;
            if (chat.closedTimestamp) {
                const date = new Date(chat.closedTimestamp);
                const dateString = date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: '2-digit' });
                historyItemText += ` (${dateString})`;
            }
            nameSpanElement.textContent = historyItemText;
            nameSpanElement.title = historyItemText;

            nameContainerSpan.appendChild(iconElement);
            nameContainerSpan.appendChild(nameSpanElement);
            listItem.appendChild(nameContainerSpan);

            const restoreButton = document.createElement('button');
            restoreButton.className = 'btn btn-sm btn-icon chat-history-restore-btn flex-shrink-0';
            restoreButton.title = 'Sohbeti Geri Yükle';
            restoreButton.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i>';
            restoreButton.onclick = function(event) {
                event.stopPropagation();
                log('action', 'Geçmişten sohbet geri yükle tıklandı (henüz uygulanmadı)', chat.id);
                alert('Geçmişten sohbet geri yükleme henüz uygulanmadı.');
                // TODO: restoreChatFromHistory(chat.id) fonksiyonunu uygula;
            };
            listItem.appendChild(restoreButton);

            listItem.onclick = function() {
                log('action', 'Sohbet geçmişi öğesi tıklandı', chat.id);
                alert(`${chat.id} ID'li sohbetin geçmişini görüntüleme henüz uygulanmadı. Mesajlar: ${JSON.stringify(chat.messages)}`);
                // TODO: Sohbet geçmişi mesajlarını görüntüleme mantığını uygula
            };
            elements.chatHistoryList.appendChild(listItem);
        });
    }

    //=============================================================================
    // 4. OLAY İŞLEYİCİLERİ (EVENT HANDLERS)
    //=============================================================================

    /**
     * 4.1. Sohbet Penceresi Kontrolleri (Chat Window Controls)
     * ----------------------------------------------------
     * Bir sohbet penceresindeki düğmeler ve girişler için olay işleyicilerini ayarlar.
     * Kapatma, küçültme, model seçimi ve mesaj göndermeyi yönetir.
     * @param {HTMLElement} chatElement - Sohbet penceresi DOM elementi.
     */
    function setupChatWindowControls(chatElement) { // setupChatControls -> setupChatWindowControls
        if (!chatElement) {
            log('error', 'Sohbet kontrolleri ayarlanamıyor: sohbet elementi null');
            return;
        }

        const chatId = chatElement.getAttribute('data-chat-id');

        const closeBtn = chatElement.querySelector('.chat-close-btn');
        if (closeBtn) {
            closeBtn.onclick = (e) => {
                e.stopPropagation();
                log('action', 'Sohbet kapatma düğmesi tıklandı', chatId);
                const chatData = state.chats.find(c => c.id === chatId);
                if (chatData && chatData.messages && chatData.messages.some(msg => msg.isUser)) {
                    if (confirm("Bu sohbeti kapatmak istediğinizden emin misiniz?")) {
                        removeChat(chatId);
                    }
                } else {
                    removeChat(chatId);
                }
            };
        }

        const minimizeBtn = chatElement.querySelector('.chat-minimize-btn');
        if (minimizeBtn) {
            minimizeBtn.onclick = (e) => {
                e.stopPropagation();
                log('action', 'Sohbet küçültme düğmesi tıklandı', chatId);
                const chat = state.chats.find(c => c.id === chatId);
                if (chat) {
                    chat.isMinimized = true;
                    renderChats(); // Bu, renderActiveChatsDropdown'ı da çağırır
                }
            };
        }

        const chatTitle = chatElement.querySelector('.chat-title');
        if (chatTitle && chatTitle.classList.contains('model-changeable')) {
            chatTitle.onclick = (e) => {
                e.stopPropagation();
                log('action', 'Model seçimi için sohbet başlığı tıklandı', chatId);
                showModelDropdown(chatId, chatTitle); // Bu fonksiyon AI Model Yönetimi bölümünde olacak
            };
        }

        const sendBtn = chatElement.querySelector('.chat-send-btn');
        const inputField = chatElement.querySelector('.chat-input');
        if (sendBtn && inputField) {
            sendBtn.onclick = () => {
                if (inputField.value.trim()) {
                    log('action', 'Gönder düğmesi tıklandı', chatId);
                    sendMessage(chatId, inputField.value); // Bu fonksiyon Sohbet Operasyonları bölümünde olacak
                    inputField.value = '';
                }
            };
            inputField.onkeypress = (e) => {
                if (e.key === 'Enter' && inputField.value.trim()) {
                    log('action', 'Sohbet girişinde Enter tuşuna basıldı', chatId);
                    sendMessage(chatId, inputField.value);
                    inputField.value = '';
                }
            };
        }
    }

    /**
     * 4.2. Global Kontroller (Global Handlers)
     * --------------------------------------
     * Düğmeler ve kontroller için global olay işleyicilerini ayarlar.
     * Yeni sohbet, sohbetleri temizle ve yayın mesajı işlevselliğini yönetir.
     */
    function setupGlobalHandlers() {
        if (!elements.welcomeNewChatBtn || !elements.newChatBtn || !elements.clearChatsBtn) {
            log('warn', 'Bazı kontrol elementleri bulunamadı');
            // return; // Hata durumunda bile diğerlerini bağlamaya çalışabiliriz.
        }

        if(elements.welcomeNewChatBtn) {
            elements.welcomeNewChatBtn.onclick = () => {
                log('action', 'Karşılama ekranı yeni sohbet düğmesi tıklandı');
                addChat(); // Bu fonksiyon Sohbet Operasyonları bölümünde olacak
            };
        }

        if(elements.newChatBtn) {
            elements.newChatBtn.onclick = () => {
                log('action', 'Yeni sohbet düğmesi tıklandı');
                addChat();
            };
        }

        if(elements.clearChatsBtn) {
            elements.clearChatsBtn.onclick = () => {
                log('action', 'Tüm sohbetleri temizle düğmesi tıklandı');
                const chatsToRemovePreview = state.chats.filter(chat => !chat.messages || !chat.messages.some(msg => msg.isUser));
                if (chatsToRemovePreview.length > 0) {
                    if (confirm(`${chatsToRemovePreview.length} kullanılmayan sohbeti kapatmak istediğinizden emin misiniz? Devam eden konuşmaları olan sohbetler etkilenmeyecektir.`)) {
                        clearAllChats(); // Bu fonksiyon Sohbet Operasyonları bölümünde olacak
                    }
                } else {
                    alert('Temizlenecek kullanılmayan sohbet yok. Tüm aktif sohbetlerde devam eden konuşmalar var veya hiç sohbet yok.');
                }
            };
        }

        if (elements.sendBroadcastBtn && elements.broadcastMessageInput) {
            elements.sendBroadcastBtn.addEventListener('click', () => {
                log('action', 'Yayın gönder düğmesi tıklandı');
                sendBroadcastMessage(); // Bu fonksiyon Sohbet Operasyonları bölümünde olacak
            });
            elements.broadcastMessageInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    log('action', 'Yayın girişinde Enter tuşuna basıldı');
                    sendBroadcastMessage();
                }
            });
        }
    }


    //=============================================================================
    // 5. SOHBET OPERASYONLARI (CHAT OPERATIONS)
    //=============================================================================

    /**
     * 5.1. Sohbet Yönetimi (Chat Management)
     * ------------------------------------
     */

    /**
     * Yeni bir sohbet penceresi oluşturur ve ekler.
     * @param {string} [aiModelId] - Kullanılacak isteğe bağlı AI model ID'si (varsayılan olarak ilk kullanılabilir olan).
     * @returns {string|null} Başarılı olursa yeni sohbet ID'si, başarısız olursa null.
     */
    function addChat(aiModelId) {
        log('action', 'Yeni sohbet ekleme denemesi. İstenen AI Model ID:', aiModelId);

        if (!elements.chatContainer) {
            log('error', 'Sohbet konteyneri bulunamadı. Sohbet eklenemiyor.');
            alert('Hata: Sohbet konteyneri bulunamadı.'); // ModalManager yerine basit alert
            return null;
        }

        if (state.chats.filter(c => !c.isMinimized).length >= state.maxChats) { // Sadece aktif (küçültülmemiş) olanları say
            log('warn', `Maksimum sohbet sayısına ulaşıldı (${state.maxChats}). Yeni sohbet eklenemiyor.`);
            alert(`Maksimum ${state.maxChats} sohbet paneline ulaşıldı. Lütfen önce birini kapatın.`); // ModalManager yerine basit alert
            return null;
        }

        let finalAiModelId = aiModelId;
        if (!finalAiModelId) {
            if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                finalAiModelId = window.state.aiTypes[0].id;
                log('info', 'AI Model ID sağlanmadı, listedeki ilkine varsayılıyor:', finalAiModelId);
            } else {
                log('error', 'addChat: AI Model ID sağlanmadı ve window.state.aiTypes\'dan varsayılan AI mevcut değil.');
                alert('Sohbet oluşturulamıyor: AI modelleri mevcut değil veya henüz yüklenmedi.'); // ModalManager yerine basit alert
                return null;
            }
        } else {
            const modelExists = window.state.aiTypes.some(m => m.id === finalAiModelId);
            if (!modelExists) {
                log('warn', `addChat: Sağlanan AI Model ID "${finalAiModelId}" window.state.aiTypes içinde mevcut değil. İlk AI'ye varsayılıyor.`);
                if (window.state && window.state.aiTypes && window.state.aiTypes.length > 0) {
                    finalAiModelId = window.state.aiTypes[0].id;
                } else {
                    log('error', 'addChat: Sağlanan AI Model ID geçersizdi ve geri dönüş AI mevcut değil.');
                    alert('Sohbet oluşturulamıyor: Belirtilen AI modeli geçersiz ve geri dönüş mevcut değil.'); // ModalManager yerine basit alert
                    return null;
                }
            }
        }
        
        // Model ID'sini prefix ile oluştur (bu mantık korunuyor, ancak finalAiModelId zaten prefix içerebilir)
        // Eğer finalAiModelId zaten 'img_' veya 'txt_' ile başlıyorsa, tekrar eklememek gerekir.
        // Bu kısım, AI model ID'lerinin nasıl tanımlandığına bağlı olarak gözden geçirilebilir.
        // Şimdilik, eğer bir prefix yoksa 'txt_' ekleyelim.
        let modelPrefix = finalAiModelId;
        if (!finalAiModelId.startsWith('img_') && !finalAiModelId.startsWith('txt_') && !finalAiModelId.startsWith('aud_')) {
             modelPrefix = 'txt_' + finalAiModelId; // Varsayılan olarak metin tabanlı olduğunu varsay
        }


        const newChat = {
            id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            aiModelId: modelPrefix, // Çözümlenmiş string ID'yi kullan
            messages: [],
            createdAt: Date.now(),
            lastActivity: Date.now(),
            isMinimized: false,
            inputHistory: [],
            historyIndex: -1
        };

        state.chats.push(newChat);
        log('info', 'Yeni sohbet eklendi:', JSON.parse(JSON.stringify(newChat)));

        renderChats(); // Bu, renderActiveChatsDropdown'ı da çağırır

        const newChatElement = elements.chatContainer.querySelector(`[data-chat-id="${newChat.id}"]`);
        if (newChatElement) {
            const inputField = newChatElement.querySelector('.chat-input');
            if (inputField && newChatElement.offsetParent !== null) {
                inputField.focus();
            }
        }
        return newChat.id;
    }

    /**
     * Bir sohbet penceresini animasyonla kaldırır.
     * Sohbetin kullanıcı mesajları varsa, kaldırılmadan önce geçmişe taşınır.
     * @param {string} chatId - Kaldırılacak sohbetin ID'si.
     */
    function removeChat(chatId) {
        log('action', 'Sohbet kaldırma denemesi', chatId);
        const chatWindow = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);

        if (chatWindow) {
            chatWindow.classList.add('closing');

            const handleAnimationEnd = () => {
                const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
                if (chatIndex !== -1) {
                    const chatToRemove = state.chats[chatIndex];
                    const hasUserMessages = chatToRemove.messages && chatToRemove.messages.some(msg => msg.isUser);

                    if (hasUserMessages) {
                        log('info', `Sohbet ${chatId} kullanıcı mesajlarına sahip. Geçmişe taşınıyor.`);
                        chatToRemove.closedTimestamp = Date.now();
                        if (!Array.isArray(state.chatHistory)) state.chatHistory = [];
                        state.chatHistory.unshift(chatToRemove);
                    } else {
                        log('info', `Sohbet ${chatId} kullanıcı mesajlarına sahip değil. Geçmişe eklenmeden kaldırılıyor.`);
                    }
                    state.chats.splice(chatIndex, 1);

                    if (chatWindow.parentNode) {
                        chatWindow.parentNode.removeChild(chatWindow);
                    }
                    renderChats(); // Bu, renderActiveChatsDropdown'ı da çağırır
                    if (typeof renderChatHistory === 'function') renderChatHistory();
                } else {
                    log('warn', `Sohbet ${chatId} animasyon sonrası durum kaldırma için aktif sohbetlerde bulunamadı.`);
                    if (chatWindow.parentNode) chatWindow.parentNode.removeChild(chatWindow);
                }
            };

            chatWindow.addEventListener('animationend', handleAnimationEnd, { once: true });

            setTimeout(() => {
                if (chatWindow.parentNode && chatWindow.classList.contains('closing')) {
                    log('warn', `${chatId} için animationend zaman aşımına uğradı. Zorla kaldırılıyor.`);
                    const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
                    if (chatIndex !== -1) state.chats.splice(chatIndex, 1);
                    chatWindow.parentNode.removeChild(chatWindow);
                    renderChats();
                    if (typeof renderChatHistory === 'function') renderChatHistory();
                }
            }, 700); // Animasyon süresinden biraz daha uzun

        } else {
            log('warn', `Kapanış animasyonu için ${chatId} ID'li sohbet penceresi elementi bulunamadı. Doğrudan kaldırılıyor.`);
            const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
            if (chatIndex !== -1) {
                const chatToRemove = state.chats[chatIndex];
                const hasUserMessages = chatToRemove.messages && chatToRemove.messages.some(msg => msg.isUser);
                if (hasUserMessages) {
                    chatToRemove.closedTimestamp = Date.now();
                    if (!Array.isArray(state.chatHistory)) state.chatHistory = [];
                    state.chatHistory.unshift(chatToRemove);
                }
                state.chats.splice(chatIndex, 1);
                renderChats();
                if (typeof renderChatHistory === 'function') renderChatHistory();
            }
        }
    }

    /**
     * Tüm kullanılmayan sohbetleri (kullanıcı mesajı olmayan sohbetler) temizler.
     * Kullanıcı arayüzünden onay alındıktan sonra çağrılır.
     */
    function clearAllChats() {
        log('action', 'Kullanılmayan sohbetler temizleniyor');
        const initialChatCount = state.chats.length;
        if (initialChatCount === 0) {
            log('info', 'Temizlenecek sohbet yok.');
            return;
        }

        state.chats = state.chats.filter(chat => {
            const hasUserMessage = chat.messages && chat.messages.some(msg => msg.isUser);
            return hasUserMessage;
        });

        const chatsRemovedCount = initialChatCount - state.chats.length;
        if (chatsRemovedCount > 0) {
            log('info', `${chatsRemovedCount} kullanılmayan sohbet kaldırıldı.`);
            renderChats(); // Bu, renderActiveChatsDropdown'ı da çağırır
        } else {
            log('info', 'Kaldırılacak kullanılmayan sohbet bulunamadı (tüm sohbetlerde konuşmalar var).');
        }
    }

    /**
     * 5.2. Mesajlaşma Sistemi (Messaging System)
     * --------------------------------------
     */

    /**
     * Belirli bir sohbete kullanıcı mesajı gönderir, AI yanıtı için backend ile iletişim kurar,
     * kullanıcı arayüzünü günceller ve ilk kullanıcı mesajından sonra model seçimini kilitler.
     * @param {string} chatId - Hedef sohbet ID'si.
     * @param {string} text - Mesaj metni içeriği.
     */
    async function sendMessage(chatId, text) {
        log('action', 'Mesaj gönderiliyor', chatId, text);

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', `sendMessage: ${chatId} ID'li sohbet bulunamadı`);
            return;
        }

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
                        chatTitle.title = 'Model kilitli - konuşma zaten başladı';
                        const selectorIcon = chatTitle.querySelector('.model-selector-icon');
                        if (selectorIcon) {
                            const lockIcon = document.createElement('i');
                            lockIcon.className = 'bi bi-lock-fill model-locked-icon';
                            chatTitle.replaceChild(lockIcon, selectorIcon);
                        }
                        chatTitle.onclick = null;
                    }
                }
            }
        }

        let loadingElement = null;
        const aiModelForLoading = window.state.aiTypes.find(m => m.id === chat.aiModelId);
        const currentAiNameForLoading = aiModelForLoading ? aiModelForLoading.name : 'AI';
        // AI'nın ilk mesajı olup olmadığını belirle (yükleme göstergesi ve nihai mesaj için)
        const isFirstAIMessageForThisTurn = chat.messages.filter(m => !m.isUser).length === 0;


        if (messagesContainer) { // messagesContainer'ın varlığını kontrol et
            const loadingMessageHTML = createMessageHTML(
                { isUser: false, text: '' },
                isFirstAIMessageForThisTurn, // Yükleme için bu doğru olmalı
                currentAiNameForLoading,
                chat.aiModelId
            );
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = loadingMessageHTML;
            loadingElement = tempDiv.firstElementChild;

            if (loadingElement) {
                loadingElement.classList.add('loading-dots');
                const messageContentDiv = loadingElement.querySelector('.message-content');
                if (messageContentDiv) { // messageContentDiv null değilse devam et
                    const dotsSpan = document.createElement('span');
                    dotsSpan.className = 'dots';
                    dotsSpan.innerHTML = '<span></span><span></span><span></span>';
                    // AI model göstergesinden sonra noktaları ekle
                    const aiModelIndicator = messageContentDiv.querySelector('.ai-model-indicator');
                    if (aiModelIndicator && aiModelIndicator.nextSibling) {
                        messageContentDiv.insertBefore(dotsSpan, aiModelIndicator.nextSibling);
                    } else if (aiModelIndicator) {
                         messageContentDiv.appendChild(dotsSpan);
                    }
                     else { // Eğer model göstergesi yoksa (örn. metin boş olduğu için), doğrudan ekle
                        // Ya da metin içeriği div'ine ekle
                        const textContentDiv = messageContentDiv.querySelector('.text-content');
                        if (textContentDiv) {
                            textContentDiv.appendChild(dotsSpan);
                        } else {
                             messageContentDiv.appendChild(dotsSpan); // Fallback
                        }
                    }
                }
                messagesContainer.appendChild(loadingElement);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }


        try {
            const fullConversationForAPI = chat.messages
                .filter(msg => msg.isUser || (msg.text && typeof msg.text === 'string' && msg.text.trim() !== ''))
                .map(msg => ({
                    role: msg.isUser ? 'user' : 'model',
                    parts: [{ text: msg.text.trim() }]
                }));

            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chatId: chatId,
                    message: text,
                    aiModelId: chat.aiModelId,
                    history: fullConversationForAPI,
                }),
            });

            if (!response.ok) {
                let errorText = `Hata: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorText = errorData.error || errorText;
                } catch (e) {
                    errorText = await response.text() || errorText;
                }
                log('error', `Backend hatası: ${errorText}`);
                throw new Error(errorText);
            }

            const data = await response.json();
            const aiResponseText = data.response;

            if (loadingElement && loadingElement.parentNode) {
                const aiMessage = { isUser: false, text: aiResponseText, timestamp: Date.now() };
                chat.messages.push(aiMessage);
                chat.lastActivity = Date.now();

                // isFirstAIMessageForThisTurn, yükleme sırasında belirlenen değeri kullanır
                const finalMessageHTML = createMessageHTML(aiMessage, isFirstAIMessageForThisTurn, currentAiNameForLoading, chat.aiModelId);
                const finalTempDiv = document.createElement('div');
                finalTempDiv.innerHTML = finalMessageHTML;
                const finalMessageElement = finalTempDiv.firstElementChild;

                loadingElement.parentNode.replaceChild(finalMessageElement, loadingElement);
                if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                // Fallback
                log('warn', 'Yükleme elementi bulunamadı, AI yanıtı doğrudan ekleniyor.');
                 const aiMessage = { isUser: false, text: aiResponseText, timestamp: Date.now() };
                chat.messages.push(aiMessage);
                chat.lastActivity = Date.now();
                // UI'ı güncellemek için renderChats çağrılabilir veya doğrudan mesaj eklenebilir.
                // Şimdilik, eğer chatElement varsa, mesajı oraya ekleyelim.
                if (chatElement && messagesContainer) {
                    const messageElementHTML = createMessageHTML(aiMessage, isFirstAIMessageForThisTurn, currentAiNameForLoading, chat.aiModelId);
                    messagesContainer.insertAdjacentHTML('beforeend', messageElementHTML);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }

        } catch (error) {
            log('error', 'Mesaj gönderme veya AI yanıtı alma başarısız:', error);
            if (loadingElement && loadingElement.parentNode) {
                const aiErrorMessage = { isUser: false, text: `Üzgünüm, bir yanıt alamadım. ${error.message || ''}`, timestamp: Date.now(), isError: true };
                const errorMessageHTML = createMessageHTML(aiErrorMessage, false, "Sistem", chat.aiModelId); // Hata mesajı için Sistem adı
                const errorTempDiv = document.createElement('div');
                errorTempDiv.innerHTML = errorMessageHTML;
                const errorMessageElement = errorTempDiv.firstElementChild;
                if (errorMessageElement) errorMessageElement.classList.add('error-message');

                loadingElement.parentNode.replaceChild(errorMessageElement, loadingElement);
                if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                log('error', 'Hata mesajı UI\'da gösterilemedi, yükleme elementi eksik.');
            }
        } finally {
            renderActiveChatsDropdown(); // Her durumda dropdown'ı güncelle
        }
    }


    /**
     * 5.3. Yayın Mesajları (Broadcast Messages)
     * ---------------------------------------
     */

    /**
     * Aynı mesajı tüm aktif (küçültülmemiş) sohbetlere gönderir.
     * Duyuruları veya talimatları yayınlamak için kullanılır.
     */
    function sendBroadcastMessage() {
        if (!elements.broadcastMessageInput) {
            log('warn', 'Yayın mesajı girişi bulunamadı.');
            return;
        }
        const messageText = elements.broadcastMessageInput.value.trim();

        if (messageText === '') {
            log('info', 'Yayın mesajı boş, gönderilmiyor.');
            return;
        }

        log('action', `Yayın mesajı gönderme denemesi: "${messageText}"`);
        const activeChats = state.chats.filter(chat => !chat.isMinimized);

        if (activeChats.length === 0) {
            log('info', 'Yayın yapılacak aktif (küçültülmemiş) sohbet yok.');
            alert('Mesaj gönderilecek aktif sohbet yok. Yeni bir sohbet oluşturun veya küçültülmüş birini geri yükleyin.');
            return;
        }

        activeChats.forEach(chat => {
            log('debug', `Yayın mesajı ${chat.id} ID'li sohbete gönderiliyor`);
            sendMessage(chat.id, messageText);
        });

        elements.broadcastMessageInput.value = '';
        log('info', 'Yayın mesajı gönderildi ve giriş temizlendi.');
    }


    //=============================================================================
    // 6. AI MODEL YÖNETİMİ (AI MODEL MANAGEMENT)
    //=============================================================================

    /**
     * 6.1. Model Seçimi Arayüzü (Model Selection UI)
     * --------------------------------------------
     */

    /**
     * Bir sohbet için AI model seçimi açılır menüsünü gösterir.
     * @param {string} chatId - Hedef sohbet ID'si.
     * @param {HTMLElement} titleElement - Açılır menüyü yakınına konumlandırmak için sohbet başlığı elementi.
     */
    function showModelDropdown(chatId, titleElement) {
        log('action', 'Model açılır menüsü gösteriliyor', chatId);

        document.querySelectorAll('.model-dropdown').forEach(dropdown => {
            if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
        });

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', `showModelDropdown: ${chatId} ID'li sohbet bulunamadı`);
            return;
        }
        if (!window.state || !window.state.aiTypes || window.state.aiTypes.length === 0) {
            log('error', 'showModelDropdown: window.state.aiTypes mevcut değil.');
            alert('AI Modelleri yüklenmedi. Model değiştirilemiyor.'); // ModalManager yerine basit alert
            return;
        }

        const dropdown = document.createElement('div');
        dropdown.className = 'model-dropdown';

        const options = window.state.aiTypes.map(model => {
            const isSelected = model.id === chat.aiModelId;
            return `
                <div class="model-option ${isSelected ? 'selected' : ''}" data-model-id="${model.id}">
                    <i class="${model.icon || 'bi bi-cpu'}"></i>
                    <span>${model.name || 'Bilinmeyen Model'}</span>
                    ${isSelected ? '<i class="bi bi-check-lg ms-auto"></i>' : ''}
                </div>
            `;
        }).join('');

        dropdown.innerHTML = options;
        // elements.chatContainer yerine document.body'e eklemek, konumlandırmayı basitleştirebilir.
        // Ancak, chatContainer içinde kalması, scroll durumlarını daha iyi yönetebilir.
        // Mevcut implementasyon korunuyor:
        elements.chatContainer.appendChild(dropdown);


        const titleRect = titleElement.getBoundingClientRect();
        const containerRect = elements.chatContainer.getBoundingClientRect();

        dropdown.style.position = 'absolute';
        // Konumlandırma, chatContainer'ın scroll durumunu dikkate almalı
        dropdown.style.top = `${titleRect.bottom - containerRect.top + elements.chatContainer.scrollTop}px`;
        dropdown.style.left = `${titleRect.left - containerRect.left + elements.chatContainer.scrollLeft}px`;
        dropdown.style.zIndex = '1050'; // Bootstrap dropdown z-index'ine yakın

        setTimeout(() => dropdown.classList.add('show'), 10);

        dropdown.querySelectorAll('.model-option').forEach(option => {
            option.onclick = (e) => {
                e.stopPropagation();
                const newModelId = option.getAttribute('data-model-id');
                if (newModelId) {
                    changeAIModel(chatId, newModelId);
                }
                dropdown.classList.remove('show');
                setTimeout(() => {
                    if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
                }, 300);
            };
        });

        // Dışarı tıklandığında kapat
        const closeDropdownOnClickOutside = (e) => {
            if (!dropdown.contains(e.target) && e.target !== titleElement && !titleElement.contains(e.target)) {
                dropdown.classList.remove('show');
                 setTimeout(() => {
                    if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
                }, 300); // Animasyon süresi
                document.removeEventListener('click', closeDropdownOnClickOutside, true); // true capture fazında dinler
            }
        };
        // event listener'ı capture fazında eklemek, diğer tıklama olaylarından önce çalışmasını sağlar.
        document.addEventListener('click', closeDropdownOnClickOutside, true);
    }

    /**
     * 6.2. Model Değiştirme Mantığı (Model Changing Logic)
     * --------------------------------------------------
     */

    /**
     * Bir sohbet için AI modelini değiştirir (sadece henüz mesaj yoksa).
     * Yeni modeli yansıtmak için kullanıcı arayüzü elementlerini günceller.
     * @param {string} chatId - Hedef sohbet ID'si.
     * @param {string} newAiModelId - Kullanılacak yeni AI modelinin ID'si.
     */
    function changeAIModel(chatId, newAiModelId) {
        log('action', 'Sohbet için AI modeli değiştiriliyor:', chatId, 'yeni ID:', newAiModelId);

        const chat = state.chats.find(c => c.id === chatId);
        if (!chat) {
            log('error', `changeAIModel: ${chatId} ID'li sohbet bulunamadı`);
            return;
        }

        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            log('warn', 'Model değiştirilemiyor: sohbette zaten mesaj var', chatId);
            alert('AI modeli değiştirilemiyor: konuşma zaten başladı.'); // ModalManager yerine basit alert
            return;
        }

        if (!window.state || !window.state.aiTypes || window.state.aiTypes.length === 0) {
            log('error', 'changeAIModel: window.state.aiTypes mevcut değil.');
            alert('AI Modelleri yüklenmedi. Model değiştirilemiyor.'); // ModalManager yerine basit alert
            return;
        }

        const newModel = window.state.aiTypes.find(m => m.id === newAiModelId);
        if (!newModel) {
            log('error', 'Geçersiz yeni AI Model ID:', newAiModelId);
            alert('Geçersiz AI Modeli seçildi.'); // ModalManager yerine basit alert
            return;
        }

        chat.aiModelId = newAiModelId;
        log('info', `Sohbet ${chatId} AI model ID'si şuna güncellendi: ${chat.aiModelId}`);

        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (chatElement) {
            const chatTitleElement = chatElement.querySelector('.chat-title');
            if (chatTitleElement) {
                const iconElement = chatTitleElement.querySelector('i:first-child'); // İlk ikon (model ikonu)
                const nameElement = chatTitleElement.querySelector('span');
                if (iconElement) iconElement.className = newModel.icon || 'bi bi-cpu';
                if (nameElement) nameElement.textContent = `${newModel.name || 'Bilinmeyen Model'} (ID: ${chat.id.slice(-4)})`;
            }

            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer && (!chat.messages || chat.messages.length === 0)) {
                messagesContainer.innerHTML = createWelcomeMessageHTML(newModel.name || 'Seçilen AI');
            }
            log('debug', 'Yeni AI modeli için sohbet elementi güncellendi', newModel);
        } else {
            log('warn', `${chatId} ID'li sohbet elementi model değişikliği sonrası UI güncellemesi için bulunamadı. Tümünü yeniden oluşturma.`);
            renderChats(); // Fallback
        }
        renderActiveChatsDropdown(); // Model değişikliğinden sonra dropdown'ı da güncelle
    }


    /**
     * 6.3. AI Yanıt Üretimi (Simüle Edilmiş) (AI Response Generation - Simulated)
     * ----------------------------------------------------------------------
     * Bu fonksiyon doğrudan sendMessage içinde backend çağrısı ile değiştirildiği için,
     * eğer hala bir simülasyon/fallback mekanizması isteniyorsa burada tutulabilir.
     * Mevcut kodda /api/chat/send kullanıldığı için bu fonksiyon artık doğrudan çağrılmıyor.
     * İhtiyaç duyulursa, offline mod veya testler için saklanabilir.
     */
    function getAIResponse(userMessage, aiModelId) {
        log('debug', `getAIResponse çağrıldı: kullanıcıMesajı: "${userMessage}", aiModelId: "${aiModelId}" (Bu fonksiyon artık aktif olarak kullanılmıyor olabilir)`);

        // Model ID'sine göre yanıt türünü belirle (img_, aud_, txt_)
        if (aiModelId.startsWith('img_')) {
            // Test için küçük bir base64 görseli
            return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAKklEQVQ4jWNgGAWjYBSMAjgIAOL/tDCYBYj/08JwBmYgZqCF4aNgFFAKAE1wAv2knXVrAAAAAElFTkSuQmCC';
        } else if (aiModelId.startsWith('aud_')) {
            // Test için örnek bir ses dosyası URL'si (gerçek bir URL ile değiştirin veya base64 kullanın)
            // return 'path/to/sample-audio.mp3'; // Bu satır yorumlu kalsın, çünkü geçerli bir ses dosyası yok
            return 'Üzgünüm, şu anda sesli yanıt üretemiyorum (simülasyon).';
        }

        // Metin tabanlı yanıtlar için
        const responses = [
            "Anlıyorum ne sorduğunuzu. Bir an düşüneyim...",
            "Bu büyüleyici bir soru! İşte benim bakış açım...",
            "Mevcut bilgilerime dayanarak şunu öneririm...",
            "Bu konuda biraz ışık tutmama izin verin. Bulduklarım şunlar..."
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    }


    //=============================================================================
    // 7. MEDYA İŞLEMLERİ (MEDIA HANDLING)
    //=============================================================================

    /**
     * 7.1. Resim İşlemleri (Image Handling)
     * -----------------------------------
     */

    /**
     * Bir URL'den veya base64 verisinden resim indirir.
     * @param {string} imageData - Resim URL'si veya base64 verisi.
     */
    function downloadImage(imageData) {
        const link = document.createElement('a');
        link.href = imageData;
        link.download = `ai-generated-image-${Date.now()}.png`; // Daha spesifik dosya adı
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Bir resmi tam ekran görüntüler.
     * @param {string} imageData - Resim URL'si veya base64 verisi.
     */
    function viewFullImage(imageData) {
        const modal = document.createElement('div');
        modal.className = 'image-modal'; // CSS'te stil tanımlanmalı
        modal.innerHTML = `
            <div class="image-modal-content">
                <img src="${imageData}" alt="AI Tarafından Oluşturulan Resim (Tam Ekran)">
                <button class="btn btn-light close-modal-btn"><i class="bi bi-x-lg"></i></button>
            </div>
        `;

        const closeModal = () => {
            if (modal.parentNode) {
                document.body.removeChild(modal);
            }
            document.removeEventListener('keydown', handleEscapeKey);
        };

        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.closest('.close-modal-btn')) {
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
    }

    /**
     * 7.2. Ses İşlemleri (Audio Handling)
     * ---------------------------------
     */

    /**
     * Bir URL'den veya base64 verisinden ses dosyası indirir.
     * @param {string} audioData - Ses URL'si veya base64 verisi.
     */
    function downloadAudio(audioData) {
        const link = document.createElement('a');
        link.href = audioData;
        link.download = `ai-generated-audio-${Date.now()}.mp3`; // Daha spesifik dosya adı
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }


    //=============================================================================
    // 8. GENEL API VE BAŞLATMA (PUBLIC API & INITIALIZATION)
    //=============================================================================

    /**
     * 8.1. Başlatma Fonksiyonu (Initialization Function)
     * ----------------------------------------------
     * Sohbet yöneticisi sistemini başlatır.
     * DOM elementlerini, olay işleyicilerini ayarlar ve başlangıç durumunu oluşturur.
     */
    function init() {
        log('info', 'ChatManager başlatılıyor');

        if (!initElements()) {
            log('error', 'ChatManager başlatılamadı: gerekli elementler bulunamadı');
            return;
        }

        setupGlobalHandlers();

        // AI Model seçici öğelerine olay dinleyicileri ekle (sidebar)
        const aiModelSelectorItems = document.querySelectorAll('.ai-model-selector-item');
        aiModelSelectorItems.forEach(item => {
            // Önce mevcut tıklama dinleyicilerini kaldır (varsa)
            const oldListener = item._clickListener; // Saklanan referansı kullan
            if (oldListener) {
                item.removeEventListener('click', oldListener);
            }

            // Yeni tıklama dinleyicisini ekle
            const newListener = function(event) { // `this` bağlamını korumak için function() kullan
                event.preventDefault();
                event.stopPropagation();

                const modelId = this.dataset.aiIndex; // dataset.aiIndex veya uygun dataset anahtarı
                if (modelId) {
                    addChat(modelId); // ChatManager.addChat yerine doğrudan addChat çağırılabilir (IIFE içinde)

                    // 'active' sınıfını yönet
                    aiModelSelectorItems.forEach(i => i.classList.remove('active'));
                    this.classList.add('active');
                } else {
                    log('error', 'Kenar çubuğundan geçersiz AI model ID seçildi.', this.dataset.aiIndex);
                }
            };
            item._clickListener = newListener; // Yeni dinleyiciyi sakla
            item.addEventListener('click', newListener);
        });

        renderChats();
        // renderActiveChatsDropdown(); // renderChats içinde çağrılıyor
        renderChatHistory();
        log('info', 'ChatManager başarıyla başlatıldı');
    }

    /**
     * 8.2. Açığa Çıkarılan Metotlar (Exposed Methods)
     * --------------------------------------------
     */
    return {
        init,
        addChat,
        removeChat,
        clearAllChats,
        sendMessage,
        sendBroadcastMessage,
        // changeAIModel, // Bu genellikle dahili bir fonksiyondur, ancak gerekirse açığa çıkarılabilir.
                           // Model seçimi UI üzerinden tetikleniyor.
        // Medya işlemleri için public API
        downloadImage,
        viewFullImage,
        downloadAudio
    };
})();

// ChatManager'ı global olarak kullanılabilir yap
window.ChatManager = ChatManager;

/**
 * 8.3. DOM Hazır Olduğunda Başlatma (DOM Ready Initialization)
 * --------------------------------------------------------
 */
document.addEventListener('DOMContentLoaded', () => {
    ChatManager.init();

    // Karşılama ekranı yeni sohbet düğmesi (initElements içinde zaten referans alınıyor,
    // burada özel bir kurulum gerekmiyorsa kaldırılabilir)
    // const welcomeNewChatBtn = document.getElementById('welcome-new-chat-btn');
    // if (welcomeNewChatBtn) { /* ... */ }

    // AI kategori akordeon chevron animasyonlarını ayarla
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
