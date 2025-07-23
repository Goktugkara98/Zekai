/**
 * ZekAI Model Selector Component
 * =============================
 * @description AI model seçimi ve değiştirme bileşeni
 * @version 1.0.0
 * @author ZekAI Team
 */

const ModelSelector = (function() {
    'use strict';

    // Aktif dropdown referansı
    let activeDropdown = null;

    /**
     * Model dropdown'ını gösterir
     * @param {string} chatId - Chat ID
     * @param {HTMLElement} titleElement - Başlık elementi
     */
    function showModelDropdown(chatId, titleElement) {
        Logger.action('ModelSelector', `Showing model dropdown for chat: ${chatId}`);

        // Mevcut dropdown'ı kapat
        closeAllDropdowns();

        const chat = ChatManager.getChat(chatId);
        if (!chat) {
            Logger.warn('ModelSelector', `Chat not found: ${chatId}`);
            return;
        }

        // Model kilitli mi kontrol et
        if (chat.messages && chat.messages.some(msg => msg.isUser)) {
            Logger.info('ModelSelector', `Model locked for chat: ${chatId}`);
            return;
        }

        const aiTypes = StateManager.getState('aiTypes');
        if (!aiTypes || aiTypes.length === 0) {
            Logger.error('ModelSelector', 'No AI models available');
            alert('AI Modelleri yüklenemedi.');
            return;
        }

        const dropdownElement = createDropdownElement(chat, aiTypes);
        
        // DOM'a ekle
        if (titleElement.parentNode) {
            titleElement.parentNode.insertBefore(dropdownElement, titleElement.nextSibling);
        } else {
            Logger.error('ModelSelector', 'Cannot append dropdown: title element has no parent');
            return;
        }

        // Animasyon için frame bekle
        requestAnimationFrame(() => {
            dropdownElement.classList.add('show');
        });

        // Event listener'ları ayarla
        setupDropdownEvents(dropdownElement, chatId, titleElement);

        // Aktif dropdown'ı kaydet
        activeDropdown = {
            element: dropdownElement,
            chatId: chatId
        };

        Logger.debug('ModelSelector', `Model dropdown created for chat: ${chatId}`);
    }

    /**
     * Dropdown elementi oluşturur
     * @param {object} chat - Chat objesi
     * @param {array} aiTypes - AI modelleri
     * @returns {HTMLElement} Dropdown elementi
     */
    function createDropdownElement(chat, aiTypes) {
        const dropdownElement = document.createElement('div');
        dropdownElement.className = 'model-dropdown';

        const optionsHTML = aiTypes.map(model => {
            const isSelected = model.id === chat.aiModelId;
            const selectedClass = isSelected ? 'selected active' : '';
            const checkIcon = isSelected ? '<i class="bi bi-check-lg ms-auto"></i>' : '';
            
            return `
                <div class="model-option ${selectedClass}" 
                     data-model-id="${model.id}" 
                     title="${model.description || model.name}">
                    <i class="${model.icon || 'bi bi-cpu'} me-2"></i>
                    <span>${model.name || 'Bilinmeyen Model'}</span>
                    ${checkIcon}
                </div>
            `;
        }).join('');

        dropdownElement.innerHTML = `<div class="list-group list-group-flush">${optionsHTML}</div>`;
        
        return dropdownElement;
    }

    /**
     * Dropdown event'lerini ayarlar
     * @param {HTMLElement} dropdownElement - Dropdown elementi
     * @param {string} chatId - Chat ID
     * @param {HTMLElement} titleElement - Başlık elementi
     */
    function setupDropdownEvents(dropdownElement, chatId, titleElement) {
        // Model seçimi event'leri
        dropdownElement.querySelectorAll('.model-option').forEach(option => {
            option.onclick = (e) => {
                e.stopPropagation();
                const newModelId = option.getAttribute('data-model-id');
                
                if (newModelId && Number(newModelId) !== ChatManager.getChat(chatId).aiModelId) {
                    selectModel(chatId, newModelId);
                }
                
                closeAllDropdowns();
            };
        });

        // Dışarı tıklama event'i
        const handleClickOutside = (event) => {
            if (!dropdownElement || !dropdownElement.parentNode) {
                document.removeEventListener('click', handleClickOutside, true);
                return;
            }

            if (!dropdownElement.contains(event.target) && 
                event.target !== titleElement && 
                !titleElement.contains(event.target)) {
                closeAllDropdowns();
            }
        };

        document.addEventListener('click', handleClickOutside, true);
        
        // Cleanup için referansı sakla
        dropdownElement._clickOutsideHandler = handleClickOutside;
    }

    /**
     * Model seçer
     * @param {string} chatId - Chat ID
     * @param {string} newModelId - Yeni model ID (string)
     */
    function selectModel(chatId, newModelId) {
        Logger.action('ModelSelector', `Selecting model for chat ${chatId}`, { newModelId });

        try {
            ChatManager.changeAIModel(chatId, Number(newModelId));
            
            // UI'ı güncelle
            updateChatTitle(chatId, Number(newModelId));
            
            Logger.info('ModelSelector', `Model selected successfully for chat ${chatId}`, { newModelId });
            EventBus.emit('model:selected', { chatId, modelId: Number(newModelId) });
            
        } catch (error) {
            Logger.error('ModelSelector', `Failed to select model for chat ${chatId}`, error);
            alert(error.message || 'Model değiştirilemedi.');
        }
    }

    /**
     * Chat başlığını günceller
     * @param {string} chatId - Chat ID
     * @param {number} newModelId - Yeni model ID
     */
    function updateChatTitle(chatId, newModelId) {
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (!chatElement) return;

        const aiTypes = StateManager.getState('aiTypes');
        const newModel = aiTypes.find(m => m.id === newModelId);
        
        if (!newModel) {
            Logger.warn('ModelSelector', `Model not found for ID: ${newModelId}`);
            return;
        }

        const chatTitleElement = chatElement.querySelector('.chat-title');
        if (chatTitleElement) {
            const iconElement = chatTitleElement.querySelector('i:first-child');
            const nameElement = chatTitleElement.querySelector('span');
            
            if (iconElement) {
                iconElement.className = newModel.icon || 'bi bi-cpu';
            }
            
            if (nameElement) {
                nameElement.textContent = `${newModel.name || 'Bilinmeyen'} (ID: ${chatId.slice(-4)})`;
            }
        }

        // Eğer mesaj yoksa karşılama mesajını güncelle
        const chat = ChatManager.getChat(chatId);
        if (!chat.messages || chat.messages.length === 0) {
            const messagesContainer = chatElement.querySelector('.chat-messages');
            if (messagesContainer) {
                messagesContainer.innerHTML = MessageRenderer.createWelcomeMessageHTML(newModel.name || 'Seçilen AI');
            }
        }

        Logger.debug('ModelSelector', `Chat title updated for ${chatId}`, { newModel });
    }

    /**
     * Tüm dropdown'ları kapatır
     */
    function closeAllDropdowns() {
        if (activeDropdown) {
            const { element } = activeDropdown;
            
            if (element && element.parentNode) {
                element.classList.remove('show');
                
                // Cleanup event listener
                if (element._clickOutsideHandler) {
                    document.removeEventListener('click', element._clickOutsideHandler, true);
                }
                
                // Animasyon sonrası DOM'dan kaldır
                setTimeout(() => {
                    if (element && element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                }, 300);
            }
            
            activeDropdown = null;
            Logger.debug('ModelSelector', 'Active dropdown closed');
        }

        // Güvenlik önlemi: DOM'da kalmış dropdown'ları temizle
        document.querySelectorAll('.model-dropdown').forEach(dropdown => {
            dropdown.classList.remove('show');
            setTimeout(() => {
                if (dropdown.parentNode) {
                    dropdown.parentNode.removeChild(dropdown);
                }
            }, 300);
        });
    }

    /**
     * Chat'in model seçim durumunu kontrol eder
     * @param {string} chatId - Chat ID
     * @returns {boolean} Model değiştirilebilir mi?
     */
    function isModelChangeable(chatId) {
        const chat = ChatManager.getChat(chatId);
        if (!chat) return false;
        
        return !(chat.messages && chat.messages.some(msg => msg.isUser));
    }

    /**
     * Chat başlığını model durumuna göre günceller
     * @param {string} chatId - Chat ID
     */
    function updateModelLockStatus(chatId) {
        const chatElement = document.querySelector(`.chat-window[data-chat-id="${chatId}"]`);
        if (!chatElement) return;

        const chatTitle = chatElement.querySelector('.chat-title');
        if (!chatTitle) return;

        const isChangeable = isModelChangeable(chatId);
        
        if (isChangeable) {
            chatTitle.classList.remove('model-locked');
            chatTitle.classList.add('model-changeable');
            chatTitle.title = 'AI modelini değiştirmek için tıklayın';
            
            // Icon'u değiştir
            const lockIcon = chatTitle.querySelector('.model-locked-icon');
            if (lockIcon) {
                const selectorIcon = document.createElement('i');
                selectorIcon.className = 'bi bi-chevron-down model-selector-icon';
                chatTitle.replaceChild(selectorIcon, lockIcon);
            }
            
            // Click handler ekle
            chatTitle.onclick = (e) => {
                e.stopPropagation();
                EventBus.emit('chat:model:selector:requested', { chatId, element: chatTitle });
            };
            
        } else {
            chatTitle.classList.remove('model-changeable');
            chatTitle.classList.add('model-locked');
            chatTitle.title = 'Model kilitli - konuşma zaten başladı';
            
            // Icon'u değiştir
            const selectorIcon = chatTitle.querySelector('.model-selector-icon');
            if (selectorIcon) {
                const lockIcon = document.createElement('i');
                lockIcon.className = 'bi bi-lock-fill model-locked-icon';
                chatTitle.replaceChild(lockIcon, selectorIcon);
            }
            
            // Click handler kaldır
            chatTitle.onclick = null;
        }

        Logger.debug('ModelSelector', `Model lock status updated for chat ${chatId}`, { isChangeable });
    }

    /**
     * Sidebar model seçicilerini ayarlar
     */
    function setupSidebarModelSelectors() {
        const aiModelSelectorItems = document.querySelectorAll('.ai-model-selector-item');
        
        if (aiModelSelectorItems.length > 0) {
            aiModelSelectorItems.forEach(item => {
                // Mevcut listener'ı kaldır
                if (item._modelSelectorClickListener) {
                    item.removeEventListener('click', item._modelSelectorClickListener);
                }
                
                // Yeni listener ekle
                item._modelSelectorClickListener = function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    const modelId = this.dataset.aiIndex;
                    Logger.action('ModelSelector', `Sidebar model selected: ${modelId}`);
                    
                    if (modelId) {
                        try {
                            const chatId = ChatManager.createChat(modelId);
                            EventBus.emit('chat:created:from:sidebar', { chatId, modelId });
                        } catch (error) {
                            Logger.error('ModelSelector', 'Failed to create chat from sidebar', error);
                            alert(error.message || 'Sohbet oluşturulamadı.');
                        }
                    } else {
                        Logger.error('ModelSelector', 'Invalid model ID from sidebar', { dataset: this.dataset });
                        alert('Geçersiz model seçimi.');
                    }
                };
                
                item.addEventListener('click', item._modelSelectorClickListener);
            });
            
            Logger.info('ModelSelector', `Setup ${aiModelSelectorItems.length} sidebar model selectors`);
        } else {
            Logger.warn('ModelSelector', 'No sidebar model selector items found');
        }
    }

    // Event listener'ları ayarla
    EventBus.on('chat:model:selector:requested', ({ chatId, element }) => {
        showModelDropdown(chatId, element);
    });

    EventBus.on('chat:message:sent', ({ chatId, isFirstUserMessage }) => {
        if (isFirstUserMessage) {
            updateModelLockStatus(chatId);
        }
    });

    // Public API
    return {
        showModelDropdown,
        closeAllDropdowns,
        selectModel,
        isModelChangeable,
        updateModelLockStatus,
        setupSidebarModelSelectors
    };
})();

// Global olarak erişilebilir yap
window.ModelSelector = ModelSelector;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModelSelector;
}

