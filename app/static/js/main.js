/**
 * Zekai - Çoklu Yapay Zeka Arayüzü
 * Ana JavaScript dosyası
 */

// DOM yüklendikten sonra çalışacak kod
document.addEventListener('DOMContentLoaded', function() {
    // Yapay zeka seçimi
    initAISelection();
    
    // Sidebar toggle
    initSidebarToggle();
    
    // Chat fonksiyonları
    initChatFunctions();
    
    // Ekran bölme kontrolleri
    initLayoutControls();
});

/**
 * Yapay zeka seçimi işlemleri
 */
function initAISelection() {
    const aiOptions = document.querySelectorAll('.ai-option');
    
    aiOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Aktif sınıfı kaldır
            aiOptions.forEach(opt => opt.classList.remove('active'));
            
            // Tıklanan seçeneği aktif yap
            this.classList.add('active');
            
            // Seçilen yapay zekayı aktif chat penceresine uygula
            const aiName = this.querySelector('.ai-name').textContent;
            const activeChat = document.querySelector('.chat-window.active');
            
            if (activeChat) {
                activeChat.querySelector('.ai-icon').innerHTML = `<i class="bi bi-robot"></i> ${aiName}`;
            }
        });
    });
}

/**
 * Sidebar toggle işlemleri
 */
function initSidebarToggle() {
    const toggleSidebar = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    
    if (toggleSidebar) {
        toggleSidebar.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
}

/**
 * Chat fonksiyonları
 */
function initChatFunctions() {
    // Mesaj gönderme
    setupMessageSending();
    
    // Chat penceresi işlemleri
    setupChatWindowActions();
}

/**
 * Mesaj gönderme işlemleri
 */
function setupMessageSending() {
    const chatInputs = document.querySelectorAll('.chat-input input');
    const sendButtons = document.querySelectorAll('.chat-input button');
    
    // Her bir chat penceresi için mesaj gönderme olayları
    chatInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const chatWindow = this.closest('.chat-window');
                sendMessage(chatWindow, this.value);
            }
        });
    });
    
    sendButtons.forEach(button => {
        button.addEventListener('click', function() {
            const chatWindow = this.closest('.chat-window');
            const input = chatWindow.querySelector('input');
            sendMessage(chatWindow, input.value);
        });
    });
}

/**
 * Mesaj gönderme fonksiyonu
 * @param {HTMLElement} chatWindow - Mesajın gönderileceği chat penceresi
 * @param {string} message - Gönderilecek mesaj
 */
function sendMessage(chatWindow, message) {
    if (!message.trim()) return;
    
    const messagesContainer = chatWindow.querySelector('.chat-messages');
    
    // Kullanıcı mesajı ekle
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.innerHTML = `
        <div class="message-content">${message}</div>
        <div class="message-meta">
            <span>Sen • Şimdi</span>
        </div>
    `;
    messagesContainer.appendChild(userMessageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Input temizle
    chatWindow.querySelector('input').value = '';
    
    // Yapay zeka yanıt simülasyonu (gerçek API entegrasyonu burada olacak)
    setTimeout(() => {
        const aiName = chatWindow.querySelector('.ai-icon').textContent.trim();
        const aiMessageDiv = document.createElement('div');
        aiMessageDiv.className = 'message ai';
        aiMessageDiv.innerHTML = `
            <div class="message-content">"${message}" için yanıt üretiyorum...</div>
            <div class="message-meta">
                <span>${aiName} • Şimdi</span>
            </div>
        `;
        messagesContainer.appendChild(aiMessageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 500);
}

/**
 * Chat penceresi işlemleri
 */
function setupChatWindowActions() {
    // Kapat butonlarına event listener ekle
    document.querySelectorAll('.chat-window .actions button:last-child').forEach(button => {
        button.addEventListener('click', function() {
            const chatWindow = this.closest('.chat-window');
            chatWindow.remove();
            
            // Eğer hiç chat penceresi kalmadıysa yeni bir tane ekle
            const chatContainer = document.getElementById('chatContainer');
            if (chatContainer.querySelectorAll('.chat-window').length === 0) {
                addNewChatWindow();
            }
        });
    });
    
    // Yenile butonlarına event listener ekle
    document.querySelectorAll('.chat-window .actions button:first-child').forEach(button => {
        button.addEventListener('click', function() {
            const chatWindow = this.closest('.chat-window');
            const messagesContainer = chatWindow.querySelector('.chat-messages');
            
            // Mesajları temizle
            messagesContainer.innerHTML = '';
            
            // Başlangıç mesajı ekle
            const aiName = chatWindow.querySelector('.ai-icon').textContent.trim();
            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.className = 'message ai';
            aiMessageDiv.innerHTML = `
                <div class="message-content">Merhaba! Size nasıl yardımcı olabilirim?</div>
                <div class="message-meta">
                    <span>${aiName} • Şimdi</span>
                </div>
            `;
            messagesContainer.appendChild(aiMessageDiv);
        });
    });
    
    // Chat pencereleri arasında geçiş için tıklama olayı
    document.querySelectorAll('.chat-window').forEach(window => {
        window.addEventListener('click', function() {
            document.querySelectorAll('.chat-window').forEach(w => w.classList.remove('active'));
            this.classList.add('active');
        });
        
        // İlk pencereyi aktif yap
        if (document.querySelectorAll('.chat-window.active').length === 0 && 
            document.querySelectorAll('.chat-window').length > 0) {
            document.querySelector('.chat-window').classList.add('active');
        }
    });
}

/**
 * Ekran bölme kontrolleri
 */
function initLayoutControls() {
    // Layout kontrol butonları
    const layoutButtons = document.querySelectorAll('.btn-layout');
    const chatContainer = document.getElementById('chatContainer');
    
    // Layout toggle butonu
    const layoutToggle = document.querySelector('.layout-controls-toggle');
    const layoutControls = document.querySelector('.layout-controls');
    
    if (layoutToggle && layoutControls) {
        layoutToggle.addEventListener('click', function() {
            layoutControls.classList.toggle('hidden');
        });
    }
    
    // Layout değiştirme
    layoutButtons.forEach(button => {
        button.addEventListener('click', function() {
            const layout = this.getAttribute('data-layout');
            
            // Aktif buton sınıfını değiştir
            layoutButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Mevcut chat pencerelerini say
            const chatWindows = chatContainer.querySelectorAll('.chat-window');
            const currentCount = chatWindows.length;
            
            // Layout'a göre grid düzenini güncelle
            updateGridLayout(layout);
            
            // Layout'a göre pencere sayısını ayarla
            adjustChatWindowCount(parseInt(layout), currentCount);
            
            // Layout kontrollerini gizle
            if (layoutControls) {
                layoutControls.classList.add('hidden');
            }
        });
    });
    
    // Yeni chat penceresi ekleme butonu
    const addChatBtn = document.querySelector('.add-chat-btn');
    if (addChatBtn) {
        addChatBtn.addEventListener('click', addNewChatWindow);
    }
}

/**
 * Grid düzenini güncelleme
 * @param {string} layout - Seçilen düzen (1, 2, 3, 4)
 */
function updateGridLayout(layout) {
    const chatContainer = document.getElementById('chatContainer');
    
    switch (layout) {
        case '1':
            chatContainer.style.gridTemplateColumns = '1fr';
            break;
        case '2':
            chatContainer.style.gridTemplateColumns = 'repeat(2, 1fr)';
            break;
        case '3':
            chatContainer.style.gridTemplateColumns = 'repeat(3, 1fr)';
            break;
        case '4':
            chatContainer.style.gridTemplateColumns = 'repeat(2, 1fr)';
            chatContainer.style.gridTemplateRows = 'repeat(2, 1fr)';
            break;
        default:
            chatContainer.style.gridTemplateColumns = '1fr';
    }
}

/**
 * Chat penceresi sayısını ayarlama
 * @param {number} targetCount - Hedef pencere sayısı
 * @param {number} currentCount - Mevcut pencere sayısı
 */
function adjustChatWindowCount(targetCount, currentCount) {
    // Eğer yeterli pencere yoksa ekle
    if (currentCount < targetCount) {
        for (let i = 0; i < targetCount - currentCount; i++) {
            addNewChatWindow();
        }
    }
    // Eğer fazla pencere varsa, fazlalıkları gizle
    else if (currentCount > targetCount) {
        const chatWindows = document.querySelectorAll('.chat-window');
        for (let i = targetCount; i < currentCount; i++) {
            if (chatWindows[i]) {
                chatWindows[i].style.display = 'none';
            }
        }
    }
    
    // Görünür pencereleri göster
    const chatWindows = document.querySelectorAll('.chat-window');
    for (let i = 0; i < targetCount; i++) {
        if (chatWindows[i]) {
            chatWindows[i].style.display = 'flex';
        }
    }
}

/**
 * Yeni chat penceresi ekleme
 */
function addNewChatWindow() {
    // Aktif AI seçeneğini bul
    const activeAI = document.querySelector('.ai-option.active');
    const aiName = activeAI ? activeAI.querySelector('.ai-name').textContent : 'Yapay Zeka';
    
    // Chat container
    const chatContainer = document.getElementById('chatContainer');
    const addChatBtn = document.querySelector('.add-chat-btn');
    
    // Yeni chat penceresi oluştur
    const newChatWindow = document.createElement('div');
    newChatWindow.className = 'chat-window';
    newChatWindow.innerHTML = `
        <div class="chat-header">
            <div class="ai-icon">
                <i class="bi bi-robot"></i> ${aiName}
            </div>
            <div class="actions">
                <button class="tooltip">
                    <i class="bi bi-arrow-clockwise"></i>
                    <span class="tooltiptext">Yenile</span>
                </button>
                <button class="tooltip">
                    <i class="bi bi-x-lg"></i>
                    <span class="tooltiptext">Kapat</span>
                </button>
            </div>
        </div>
        <div class="chat-messages">
            <div class="message ai">
                <div class="message-content">
                    Merhaba! Size nasıl yardımcı olabilirim?
                </div>
                <div class="message-meta">
                    <span>${aiName} • Şimdi</span>
                </div>
            </div>
        </div>
        <div class="chat-input">
            <div class="input-group">
                <input type="text" placeholder="Mesajınızı yazın...">
                <button>
                    <i class="bi bi-send"></i>
                </button>
            </div>
        </div>
    `;
    
    // Yeni chat penceresini ekle
    if (addChatBtn) {
        chatContainer.insertBefore(newChatWindow, addChatBtn);
    } else {
        chatContainer.appendChild(newChatWindow);
    }
    
    // Yeni eklenen chat penceresine event listener'ları ekle
    const newInput = newChatWindow.querySelector('input');
    const newSendButton = newChatWindow.querySelector('.chat-input button');
    
    // Mesaj gönderme
    newInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(newChatWindow, this.value);
        }
    });
    
    newSendButton.addEventListener('click', function() {
        sendMessage(newChatWindow, newInput.value);
    });
    
    // Kapat butonu
    const closeButton = newChatWindow.querySelector('.actions button:last-child');
    closeButton.addEventListener('click', function() {
        newChatWindow.remove();
        
        // Eğer hiç chat penceresi kalmadıysa yeni bir tane ekle
        if (chatContainer.querySelectorAll('.chat-window').length === 0) {
            addNewChatWindow();
        }
    });
    
    // Yenile butonu
    const refreshButton = newChatWindow.querySelector('.actions button:first-child');
    refreshButton.addEventListener('click', function() {
        const messagesContainer = newChatWindow.querySelector('.chat-messages');
        
        // Mesajları temizle
        messagesContainer.innerHTML = '';
        
        // Başlangıç mesajı ekle
        const aiMessageDiv = document.createElement('div');
        aiMessageDiv.className = 'message ai';
        aiMessageDiv.innerHTML = `
            <div class="message-content">Merhaba! Size nasıl yardımcı olabilirim?</div>
            <div class="message-meta">
                <span>${aiName} • Şimdi</span>
            </div>
        `;
        messagesContainer.appendChild(aiMessageDiv);
    });
    
    // Pencere tıklama olayı
    newChatWindow.addEventListener('click', function() {
        document.querySelectorAll('.chat-window').forEach(w => w.classList.remove('active'));
        this.classList.add('active');
    });
    
    // Yeni pencereyi aktif yap
    document.querySelectorAll('.chat-window').forEach(w => w.classList.remove('active'));
    newChatWindow.classList.add('active');
    
    return newChatWindow;
}