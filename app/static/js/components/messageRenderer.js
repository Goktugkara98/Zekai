/**
 * ZekAI Message Renderer Component
 * ===============================
 * @description Mesaj render işlemleri (text, image, audio)
 * @version 1.0.0
 * @author ZekAI Team
 */

const MessageRenderer = (function() {
    'use strict';

    /**
     * Mesaj HTML'i oluşturur
     * @param {object} message - Mesaj objesi
     * @param {boolean} isFirstAIMessage - İlk AI mesajı mı?
     * @param {string} aiName - AI adı
     * @param {number} aiModelId - AI Model ID
     * @returns {string} Mesaj HTML'i
     */
    function createMessageHTML(message, isFirstAIMessage = false, aiName = '', aiModelId = '') {
        try {
            const messageClass = message.isUser ? 'user-message' : 'ai-message';
            const timestamp = new Date(message.timestamp || Date.now()).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });

            let messageContent = message.isUser ? 
                renderTextContent(message.text) : 
                renderContent(message.text, aiModelId);

            // AI model indicator ekle
            if (!message.isUser && aiName && (isFirstAIMessage || message.showAiName)) {
                const iconClass = message.isError ? 'bi bi-exclamation-triangle-fill' : 'bi bi-robot';
                const displayName = message.isError ? 'Sistem' : aiName;
                messageContent = `<div class="ai-model-indicator"><i class="${iconClass}"></i> ${displayName}</div>${messageContent}`;
            }
            
            const errorClass = message.isError ? ' error-message' : '';
            
            return `
                <div class="message ${messageClass}${errorClass}">
                    <div class="message-content">
                        ${messageContent}
                    </div>
                    <div class="message-time">${timestamp}</div>
                </div>
            `;
        } catch (error) {
            Logger.error('MessageRenderer', 'Error creating message HTML', error);
            return createErrorMessageHTML();
        }
    }

    /**
     * Karşılama mesajı HTML'i oluşturur
     * @param {string} aiName - AI adı
     * @returns {string} Karşılama mesajı HTML'i
     */
    function createWelcomeMessageHTML(aiName) {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        return `
            <div class="message ai-message">
                <div class="message-content">
                    <div class="ai-model-indicator"><i class="bi bi-robot"></i> ${aiName}</div>
                    <div class="text-content">
                        <p>Merhaba! Ben ${aiName}. Bugün size nasıl yardımcı olabilirim?</p>
                    </div>
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
    }

    /**
     * Hata mesajı HTML'i oluşturur
     * @returns {string} Hata mesajı HTML'i
     */
    function createErrorMessageHTML() {
        return `
            <div class="message error-message">
                <div class="message-content">
                    <div class="text-content">Mesaj görüntülenemedi.</div>
                </div>
            </div>
        `;
    }

    /**
     * İçerik tipine göre render eder
     * @param {string} content - İçerik
     * @param {number} aiModelId - AI Model ID
     * @returns {string} Render edilmiş içerik
     */
    function renderContent(content, aiModelId) {
        const categoryType = determineCategoryType(aiModelId);
        
        Logger.debug('MessageRenderer', `Rendering content with type: ${categoryType}`, { aiModelId });

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

    /**
     * AI Model ID'sine göre kategori tipini belirler
     * @param {number} aiModelId - AI Model ID
     * @returns {string} Kategori tipi (txt, img, aud)
     */
    function determineCategoryType(aiModelId) {
        let categoryType = 'txt'; // Varsayılan
        
        const allAiCategories = StateManager.getState('allAiCategories');
        
        if (allAiCategories && Array.isArray(allAiCategories)) {
            for (const category of allAiCategories) {
                if (category.models && Array.isArray(category.models)) {
                    const modelFound = category.models.find(model => model.id === aiModelId);
                    if (modelFound) {
                        const categoryNameLower = category.name.toLowerCase();
                        
                        if (categoryNameLower.includes('image') || categoryNameLower.includes('resim')) {
                            categoryType = 'img';
                        } else if (categoryNameLower.includes('audio') || categoryNameLower.includes('ses')) {
                            categoryType = 'aud';
                        } else {
                            categoryType = 'txt';
                        }
                        
                        Logger.debug('MessageRenderer', `Model ID ${aiModelId} found in category '${category.name}' (ID: ${category.id}). Type: ${categoryType}`);
                        break;
                    }
                }
            }
        }
        
        if (categoryType === 'txt') {
            Logger.debug('MessageRenderer', `Model ID ${aiModelId} not found in categories or default text type used`);
        }
        
        return categoryType;
    }

    /**
     * Metin içeriği render eder
     * @param {string} content - Metin içeriği
     * @returns {string} Render edilmiş HTML
     */
    function renderTextContent(content) {
        if (!content) return '<div class="text-content"></div>';
        
        const sanitizedContent = String(content)
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br>");
            
        return `<div class="text-content">${sanitizedContent}</div>`;
    }

    /**
     * Resim içeriği render eder
     * @param {string} content - Resim URL'i
     * @returns {string} Render edilmiş HTML
     */
    function renderImageContent(content) {
        if (!content || typeof content !== 'string') {
            Logger.warn('MessageRenderer', 'Invalid image content provided', content);
            return `<div class="image-content error-content">Resim yüklenemedi (geçersiz veri).</div>`;
        }

        const imageId = `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        return `
            <div class="image-content" data-image-id="${imageId}">
                <img src="${content}" 
                     alt="AI Tarafından Oluşturulan Resim" 
                     class="ai-generated-image" 
                     onerror="MessageRenderer.handleImageError(this)"
                     onload="MessageRenderer.handleImageLoad(this)">
                <div class="image-controls">
                    <button class="btn btn-sm btn-primary download-image" 
                            onclick="MessageRenderer.downloadImage('${content}')"
                            title="Resmi İndir">
                        <i class="bi bi-download"></i> İndir
                    </button>
                    <button class="btn btn-sm btn-secondary view-image" 
                            onclick="MessageRenderer.viewFullImage('${content}')"
                            title="Tam Ekran Görüntüle">
                        <i class="bi bi-arrows-fullscreen"></i> Tam Ekran
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Ses içeriği render eder
     * @param {string} content - Ses URL'i
     * @returns {string} Render edilmiş HTML
     */
    function renderAudioContent(content) {
        if (!content || typeof content !== 'string') {
            Logger.warn('MessageRenderer', 'Invalid audio content provided', content);
            return `<div class="audio-content error-content">Ses yüklenemedi (geçersiz veri).</div>`;
        }

        const audioId = `audio-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        return `
            <div class="audio-content" data-audio-id="${audioId}">
                <audio controls 
                       src="${content}" 
                       onerror="MessageRenderer.handleAudioError(this)"
                       onloadeddata="MessageRenderer.handleAudioLoad(this)">
                    Tarayıcınız ses elementini desteklemiyor.
                </audio>
                <div class="audio-controls">
                    <button class="btn btn-sm btn-primary download-audio" 
                            onclick="MessageRenderer.downloadAudio('${content}')"
                            title="Ses Dosyasını İndir">
                        <i class="bi bi-download"></i> İndir
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Resim yükleme hatası işleyicisi
     * @param {HTMLImageElement} imgElement - Resim elementi
     */
    function handleImageError(imgElement) {
        Logger.error('MessageRenderer', 'Image loading error', { src: imgElement.src });
        
        imgElement.alt = 'Resim yüklenemedi';
        imgElement.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        
        const imageContent = imgElement.closest('.image-content');
        if (imageContent) {
            imageContent.classList.add('error-content');
            
            // Hata mesajı ekle
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = 'Resim yüklenemedi';
            imageContent.appendChild(errorMsg);
        }
    }

    /**
     * Resim yükleme başarı işleyicisi
     * @param {HTMLImageElement} imgElement - Resim elementi
     */
    function handleImageLoad(imgElement) {
        Logger.debug('MessageRenderer', 'Image loaded successfully', { src: imgElement.src });
        
        const imageContent = imgElement.closest('.image-content');
        if (imageContent) {
            imageContent.classList.add('loaded');
        }
    }

    /**
     * Ses yükleme hatası işleyicisi
     * @param {HTMLAudioElement} audioElement - Ses elementi
     */
    function handleAudioError(audioElement) {
        Logger.error('MessageRenderer', 'Audio loading error', { src: audioElement.src });
        
        const audioContent = audioElement.closest('.audio-content');
        if (audioContent) {
            audioContent.classList.add('error-content');
            audioContent.innerHTML = '<p class="error-message">Ses dosyası yüklenemedi.</p>';
        }
    }

    /**
     * Ses yükleme başarı işleyicisi
     * @param {HTMLAudioElement} audioElement - Ses elementi
     */
    function handleAudioLoad(audioElement) {
        Logger.debug('MessageRenderer', 'Audio loaded successfully', { src: audioElement.src });
        
        const audioContent = audioElement.closest('.audio-content');
        if (audioContent) {
            audioContent.classList.add('loaded');
        }
    }

    /**
     * Resim indirir
     * @param {string} imageUrl - Resim URL'i
     */
    function downloadImage(imageUrl) {
        downloadMedia(imageUrl, 'ai-image');
    }

    /**
     * Ses dosyası indirir
     * @param {string} audioUrl - Ses URL'i
     */
    function downloadAudio(audioUrl) {
        downloadMedia(audioUrl, 'ai-audio');
    }

    /**
     * Medya dosyası indirir
     * @param {string} mediaUrl - Medya URL'i
     * @param {string} defaultFileName - Varsayılan dosya adı
     */
    function downloadMedia(mediaUrl, defaultFileName = 'downloaded-media') {
        if (!mediaUrl || typeof mediaUrl !== 'string') {
            Logger.warn('MessageRenderer', 'Invalid media URL for download', mediaUrl);
            alert('İndirilecek medya kaynağı geçersiz.');
            return;
        }

        try {
            const link = document.createElement('a');
            link.href = mediaUrl;
            
            let fileName = defaultFileName;
            
            try {
                const url = new URL(mediaUrl.startsWith('data:') ? 'http://localhost' : mediaUrl);
                const lastSegment = url.pathname.substring(url.pathname.lastIndexOf('/') + 1);
                
                if (lastSegment && lastSegment.includes('.')) {
                    fileName = lastSegment;
                } else {
                    // Data URL'den format belirle
                    if (mediaUrl.startsWith('data:image/png')) fileName = `${defaultFileName}-${Date.now()}.png`;
                    else if (mediaUrl.startsWith('data:image/jpeg')) fileName = `${defaultFileName}-${Date.now()}.jpg`;
                    else if (mediaUrl.startsWith('data:audio/mpeg')) fileName = `${defaultFileName}-${Date.now()}.mp3`;
                    else fileName = `${defaultFileName}-${Date.now()}`;
                }
            } catch (e) {
                if (mediaUrl.startsWith('data:image/png')) fileName = `${defaultFileName}-${Date.now()}.png`;
                else fileName = `${defaultFileName}-${Date.now()}`;
            }
            
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            Logger.info('MessageRenderer', `Media download initiated: ${fileName}`);
            
        } catch (error) {
            Logger.error('MessageRenderer', 'Media download error', error);
            alert(`Medya indirilemedi: ${error.message}`);
        }
    }

    /**
     * Resmi tam ekranda gösterir
     * @param {string} imageUrl - Resim URL'i
     */
    function viewFullImage(imageUrl) {
        if (!imageUrl || typeof imageUrl !== 'string') {
            Logger.warn('MessageRenderer', 'Invalid image URL for full view', imageUrl);
            alert('Görüntülenecek resim geçersiz.');
            return;
        }

        // Mevcut modal'ı kaldır
        const existingModal = document.querySelector('.image-modal-zk');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.className = 'image-modal-zk';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            padding: 20px;
            box-sizing: border-box;
        `;

        modal.innerHTML = `
            <div style="max-width: 90%; max-height: 90%; position: relative;">
                <img src="${imageUrl}" 
                     alt="Tam Ekran Resim" 
                     style="max-width: 100%; max-height: 100%; display: block; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.5);">
                <button title="Kapat (Esc)" 
                        style="position: absolute; top: 10px; right: 10px; background: white; border: none; border-radius: 50%; width: 30px; height: 30px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center;">
                    &times;
                </button>
            </div>
        `;

        const closeModal = () => {
            if (modal.parentNode) modal.remove();
            document.removeEventListener('keydown', handleEscapeKey);
        };

        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('image-modal-zk')) {
                closeModal();
            }
        });

        const handleEscapeKey = (e) => {
            if (e.key === 'Escape') closeModal();
        };

        document.addEventListener('keydown', handleEscapeKey);
        document.body.appendChild(modal);

        Logger.info('MessageRenderer', 'Full image view opened', { imageUrl });
    }

    // Public API
    return {
        createMessageHTML,
        createWelcomeMessageHTML,
        renderContent,
        renderTextContent,
        renderImageContent,
        renderAudioContent,
        handleImageError,
        handleImageLoad,
        handleAudioError,
        handleAudioLoad,
        downloadImage,
        downloadAudio,
        viewFullImage
    };
})();

// Global olarak erişilebilir yap
window.MessageRenderer = MessageRenderer;
window.createMessageHTML = MessageRenderer.createMessageHTML;
window.createWelcomeMessageHTML = MessageRenderer.createWelcomeMessageHTML;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessageRenderer;
}

