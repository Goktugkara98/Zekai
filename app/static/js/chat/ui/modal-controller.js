/**
 * Modal Controller
 * Modal ve popup kontrolü
 */

import { DOMUtils } from '../utils/dom-utils.js';
import { Helpers } from '../utils/helpers.js';

export class ModalController {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.activeModal = null;
        this.modals = new Map();
    }

    /**
     * Controller'ı başlat
     */
    async init() {
        // Event listener'ları kur
        this.setupEventListeners();

        console.log('ModalController initialized');
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Modal show event'i
        this.eventManager.on('modal:show', (event) => {
            this.showModal(event.data);
        });

        // Modal hide event'i
        this.eventManager.on('modal:hide', (event) => {
            this.hideModal(event.data);
        });

        // Modal close event'i
        this.eventManager.on('modal:close', () => {
            this.closeActiveModal();
        });

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.closeActiveModal();
            }
        });
    }

    /**
     * Modal göster
     * @param {Object} data - Modal data
     */
    showModal(data) {
        const { type, title, content, options = {} } = data;

        // Mevcut modal'ı kapat
        if (this.activeModal) {
            this.closeActiveModal();
        }

        let modal;
        switch (type) {
            case 'prompts':
                modal = this.createPromptsModal();
                break;
            case 'settings':
                modal = this.createSettingsModal();
                break;
            case 'confirm':
                modal = this.createConfirmModal(title, content, options);
                break;
            case 'alert':
                modal = this.createAlertModal(title, content, options);
                break;
            default:
                modal = this.createGenericModal(title, content, options);
        }

        if (modal) {
            this.activeModal = modal;
            document.body.appendChild(modal);
            
            // Animation
            setTimeout(() => {
                DOMUtils.addClass(modal, 'show');
            }, 10);

            // Event emit et
            this.eventManager.emit('modal:shown', {
                type,
                element: modal
            });
        }
    }

    /**
     * Modal gizle
     * @param {Object} data - Modal data
     */
    hideModal(data) {
        const { id } = data;
        const modal = this.modals.get(id);
        
        if (modal) {
            this.closeModal(modal);
        }
    }

    /**
     * Aktif modal'ı kapat
     */
    closeActiveModal() {
        if (this.activeModal) {
            this.closeModal(this.activeModal);
        }
    }

    /**
     * Modal kapat
     * @param {Element} modal - Modal elementi
     */
    closeModal(modal) {
        if (!modal) return;

        DOMUtils.addClass(modal, 'hide');
        
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            
            if (this.activeModal === modal) {
                this.activeModal = null;
            }
        }, 300);

        // Event emit et
        this.eventManager.emit('modal:closed', {
            element: modal
        });
    }

    /**
     * Prompts modal oluştur
     * @returns {Element}
     */
    createPromptsModal() {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Prompts</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="prompt-categories">
                        <div class="prompt-category">
                            <h4>Creative Writing</h4>
                            <div class="prompt-item" data-prompt="Write a short story about...">Write a short story about...</div>
                            <div class="prompt-item" data-prompt="Create a poem about...">Create a poem about...</div>
                            <div class="prompt-item" data-prompt="Write a dialogue between...">Write a dialogue between...</div>
                        </div>
                        <div class="prompt-category">
                            <h4>Business</h4>
                            <div class="prompt-item" data-prompt="Write a business plan for...">Write a business plan for...</div>
                            <div class="prompt-item" data-prompt="Create a marketing strategy for...">Create a marketing strategy for...</div>
                            <div class="prompt-item" data-prompt="Analyze the market for...">Analyze the market for...</div>
                        </div>
                        <div class="prompt-category">
                            <h4>Technical</h4>
                            <div class="prompt-item" data-prompt="Explain how to...">Explain how to...</div>
                            <div class="prompt-item" data-prompt="Write code for...">Write code for...</div>
                            <div class="prompt-item" data-prompt="Debug this code...">Debug this code...</div>
                        </div>
                        <div class="prompt-category">
                            <h4>Education</h4>
                            <div class="prompt-item" data-prompt="Teach me about...">Teach me about...</div>
                            <div class="prompt-item" data-prompt="Create a lesson plan for...">Create a lesson plan for...</div>
                            <div class="prompt-item" data-prompt="Explain the concept of...">Explain the concept of...</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupPromptsModalEvents(modal);

        return modal;
    }

    /**
     * Prompts modal event'lerini kur
     * @param {Element} modal - Modal elementi
     */
    setupPromptsModalEvents(modal) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });

        // Prompt items
        const promptItems = DOMUtils.$$('.prompt-item', modal);
        promptItems.forEach(item => {
            DOMUtils.on(item, 'click', (e) => {
                const prompt = item.dataset.prompt;
                this.handlePromptSelection(prompt);
                this.closeModal(modal);
            });
        });
    }

    /**
     * Prompt seçimi işle
     * @param {string} prompt - Prompt metni
     */
    handlePromptSelection(prompt) {
        // Event emit et
        this.eventManager.emit('prompt:selected', {
            prompt
        });

        // Input'a prompt'u ekle
        const messageInput = DOMUtils.$('.message-input');
        if (messageInput) {
            messageInput.value = prompt;
            messageInput.focus();
        }
    }

    /**
     * Settings modal oluştur
     * @returns {Element}
     */
    createSettingsModal() {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Settings</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="settings-section">
                        <h4>General</h4>
                        <div class="setting-item">
                            <label>Theme</label>
                            <select class="setting-input">
                                <option value="light">Light</option>
                                <option value="dark">Dark</option>
                                <option value="auto">Auto</option>
                            </select>
                        </div>
                        <div class="setting-item">
                            <label>Language</label>
                            <select class="setting-input">
                                <option value="en">English</option>
                                <option value="tr">Türkçe</option>
                            </select>
                        </div>
                    </div>
                    <div class="settings-section">
                        <h4>Chat</h4>
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" class="setting-checkbox">
                                Auto-save conversations
                            </label>
                        </div>
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" class="setting-checkbox">
                                Show typing indicator
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                    <button class="btn btn-primary" data-action="save">Save</button>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupSettingsModalEvents(modal);

        return modal;
    }

    /**
     * Settings modal event'lerini kur
     * @param {Element} modal - Modal elementi
     */
    setupSettingsModalEvents(modal) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });

        // Footer buttons
        const cancelBtn = DOMUtils.$('[data-action="cancel"]', modal);
        const saveBtn = DOMUtils.$('[data-action="save"]', modal);

        if (cancelBtn) {
            DOMUtils.on(cancelBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        if (saveBtn) {
            DOMUtils.on(saveBtn, 'click', () => {
                this.handleSettingsSave(modal);
            });
        }
    }

    /**
     * Settings kaydetme işle
     * @param {Element} modal - Modal elementi
     */
    handleSettingsSave(modal) {
        // Settings'leri topla
        const settings = {};
        
        const selects = DOMUtils.$$('.setting-input', modal);
        selects.forEach(select => {
            const label = select.previousElementSibling.textContent;
            settings[label.toLowerCase()] = select.value;
        });

        const checkboxes = DOMUtils.$$('.setting-checkbox', modal);
        checkboxes.forEach(checkbox => {
            const label = checkbox.parentElement.textContent.trim();
            settings[label.toLowerCase().replace(/\s+/g, '_')] = checkbox.checked;
        });

        // State'e kaydet
        this.stateManager.setPreference('settings', settings);

        // Event emit et
        this.eventManager.emit('settings:saved', {
            settings
        });

        // Modal'ı kapat
        this.closeModal(modal);

        // Notification göster
        this.stateManager.addNotification({
            type: 'success',
            message: 'Settings saved successfully!'
        });
    }

    /**
     * Confirm modal oluştur
     * @param {string} title - Modal başlığı
     * @param {string} content - Modal içeriği
     * @param {Object} options - Modal seçenekleri
     * @returns {Element}
     */
    createConfirmModal(title, content, options = {}) {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${content}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                    <button class="btn btn-danger" data-action="confirm">Confirm</button>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupConfirmModalEvents(modal, options);

        return modal;
    }

    /**
     * Confirm modal event'lerini kur
     * @param {Element} modal - Modal elementi
     * @param {Object} options - Modal seçenekleri
     */
    setupConfirmModalEvents(modal, options) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onCancel) {
                    options.onCancel();
                }
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
                if (options.onCancel) {
                    options.onCancel();
                }
            }
        });

        // Footer buttons
        const cancelBtn = DOMUtils.$('[data-action="cancel"]', modal);
        const confirmBtn = DOMUtils.$('[data-action="confirm"]', modal);

        if (cancelBtn) {
            DOMUtils.on(cancelBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onCancel) {
                    options.onCancel();
                }
            });
        }

        if (confirmBtn) {
            DOMUtils.on(confirmBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onConfirm) {
                    options.onConfirm();
                }
            });
        }
    }

    /**
     * Alert modal oluştur
     * @param {string} title - Modal başlığı
     * @param {string} content - Modal içeriği
     * @param {Object} options - Modal seçenekleri
     * @returns {Element}
     */
    createAlertModal(title, content, options = {}) {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${content}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" data-action="ok">OK</button>
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupAlertModalEvents(modal, options);

        return modal;
    }

    /**
     * Alert modal event'lerini kur
     * @param {Element} modal - Modal elementi
     * @param {Object} options - Modal seçenekleri
     */
    setupAlertModalEvents(modal, options) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onOk) {
                    options.onOk();
                }
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
                if (options.onOk) {
                    options.onOk();
                }
            }
        });

        // OK button
        const okBtn = DOMUtils.$('[data-action="ok"]', modal);
        if (okBtn) {
            DOMUtils.on(okBtn, 'click', () => {
                this.closeModal(modal);
                if (options.onOk) {
                    options.onOk();
                }
            });
        }
    }

    /**
     * Generic modal oluştur
     * @param {string} title - Modal başlığı
     * @param {string} content - Modal içeriği
     * @param {Object} options - Modal seçenekleri
     * @returns {Element}
     */
    createGenericModal(title, content, options = {}) {
        const modal = DOMUtils.createElement('div', {
            className: 'modal-overlay'
        }, '');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        // Event listener'ları kur
        this.setupGenericModalEvents(modal, options);

        return modal;
    }

    /**
     * Generic modal event'lerini kur
     * @param {Element} modal - Modal elementi
     * @param {Object} options - Modal seçenekleri
     */
    setupGenericModalEvents(modal, options) {
        // Close button
        const closeBtn = DOMUtils.$('.close-btn', modal);
        if (closeBtn) {
            DOMUtils.on(closeBtn, 'click', () => {
                this.closeModal(modal);
            });
        }

        // Overlay click
        DOMUtils.on(modal, 'click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });
    }

    /**
     * Controller'ı temizle
     */
    destroy() {
        // Tüm modal'ları kapat
        if (this.activeModal) {
            this.closeActiveModal();
        }

        // Event listener'ları kaldır
        document.removeEventListener('keydown', this.handleEscapeKey);

        console.log('ModalController destroyed');
    }
}
