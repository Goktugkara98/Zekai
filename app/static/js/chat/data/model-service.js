/**
 * Model Service
 * AI model yönetimi ve konfigürasyon
 */

import { Helpers } from '../utils/helpers.js';

export class ModelService {
    constructor(stateManager, eventManager) {
        this.stateManager = stateManager;
        this.eventManager = eventManager;
        this.models = [];
        this.activeModel = null;
        this.modelConfigs = new Map();
    }

    /**
     * Servisi başlat
     */
    async init() {
        // Model'leri yükle
        this.loadModels();
        
        // Model konfigürasyonlarını yükle
        this.loadModelConfigs();
        
        // Event listener'ları kur
        this.setupEventListeners();

        console.log('ModelService initialized');
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Model seçimi event'i
        this.eventManager.on('model:selected', (event) => {
            this.handleModelSelection(event.data);
        });

        // Model değişikliği event'i
        this.eventManager.on('model:change', (event) => {
            this.handleModelChange(event.data);
        });
    }

    /**
     * Model'leri yükle
     */
    loadModels() {
        this.models = [
            {
                id: 'chatgpt-5',
                name: 'ChatGPT-5',
                provider: 'OpenAI',
                type: 'text',
                description: 'Latest GPT model with enhanced capabilities',
                icon: 'fas fa-robot',
                color: '#10a37f',
                capabilities: ['text', 'code', 'reasoning'],
                maxTokens: 128000,
                isAvailable: true,
                isPinned: true
            },
            {
                id: 'gemini-2.5-flash',
                name: 'Gemini 2.5 Flash',
                provider: 'Google',
                type: 'multimodal',
                description: 'Fast and efficient multimodal model',
                icon: 'fab fa-google',
                color: '#4285f4',
                capabilities: ['text', 'image', 'code'],
                maxTokens: 1000000,
                isAvailable: true,
                isPinned: true
            },
            {
                id: 'claude-sonnet-4',
                name: 'Claude Sonnet 4',
                provider: 'Anthropic',
                type: 'text',
                description: 'Advanced reasoning and analysis',
                icon: 'fas fa-brain',
                color: '#d97706',
                capabilities: ['text', 'reasoning', 'analysis'],
                maxTokens: 200000,
                isAvailable: true,
                isPinned: false
            },
            {
                id: 'deepseek-v3-0324',
                name: 'DeepSeek V3 0324',
                provider: 'DeepSeek',
                type: 'text',
                description: 'Specialized in coding and technical tasks',
                icon: 'fas fa-search',
                color: '#7c3aed',
                capabilities: ['text', 'code', 'math'],
                maxTokens: 64000,
                isAvailable: true,
                isPinned: false
            },
            {
                id: 'llama-4-scout',
                name: 'Llama 4 Scout',
                provider: 'Meta',
                type: 'text',
                description: 'Open source language model',
                icon: 'fas fa-mountain',
                color: '#059669',
                capabilities: ['text', 'reasoning'],
                maxTokens: 128000,
                isAvailable: true,
                isPinned: false
            },
            {
                id: 'perplexity-sonar-pro',
                name: 'Perplexity Sonar Pro',
                provider: 'Perplexity',
                type: 'search',
                description: 'Real-time web search and analysis',
                icon: 'fas fa-question-circle',
                color: '#dc2626',
                capabilities: ['text', 'search', 'web'],
                maxTokens: 32000,
                isAvailable: true,
                isPinned: false
            }
        ];
    }

    /**
     * Model konfigürasyonlarını yükle
     */
    loadModelConfigs() {
        // Her model için varsayılan konfigürasyon
        this.models.forEach(model => {
            this.modelConfigs.set(model.id, {
                temperature: 0.7,
                maxTokens: model.maxTokens,
                topP: 0.9,
                frequencyPenalty: 0,
                presencePenalty: 0,
                systemPrompt: '',
                customInstructions: '',
                isEnabled: true
            });
        });
    }

    /**
     * Model seçimi işle
     * @param {Object} data - Event data
     */
    handleModelSelection(data) {
        const { modelName } = data;
        const model = this.getModelByName(modelName);
        
        if (model) {
            this.setActiveModel(model);
        }
    }

    /**
     * Model değişikliği işle
     * @param {Object} data - Event data
     */
    handleModelChange(data) {
        const { modelId } = data;
        const model = this.getModelById(modelId);
        
        if (model) {
            this.setActiveModel(model);
        }
    }

    /**
     * Aktif model'i ayarla
     * @param {Object} model - Model objesi
     */
    setActiveModel(model) {
        this.activeModel = model;
        this.stateManager.setState('activeModel', model.name);
        
        // Event emit et
        this.eventManager.emit('model:activated', {
            model,
            config: this.getModelConfig(model.id)
        });
    }

    /**
     * Model'i ID ile al
     * @param {string} modelId - Model ID
     * @returns {Object|null}
     */
    getModelById(modelId) {
        return this.models.find(model => model.id === modelId) || null;
    }

    /**
     * Model'i isim ile al
     * @param {string} modelName - Model ismi
     * @returns {Object|null}
     */
    getModelByName(modelName) {
        return this.models.find(model => model.name === modelName) || null;
    }

    /**
     * Tüm model'leri al
     * @param {Object} filters - Filtreler
     * @returns {Array}
     */
    getModels(filters = {}) {
        let filteredModels = [...this.models];

        // Provider filtresi
        if (filters.provider) {
            filteredModels = filteredModels.filter(model => 
                model.provider === filters.provider
            );
        }

        // Type filtresi
        if (filters.type) {
            filteredModels = filteredModels.filter(model => 
                model.type === filters.type
            );
        }

        // Capability filtresi
        if (filters.capability) {
            filteredModels = filteredModels.filter(model => 
                model.capabilities.includes(filters.capability)
            );
        }

        // Availability filtresi
        if (filters.available !== undefined) {
            filteredModels = filteredModels.filter(model => 
                model.isAvailable === filters.available
            );
        }

        // Pinned filtresi
        if (filters.pinned !== undefined) {
            filteredModels = filteredModels.filter(model => 
                model.isPinned === filters.pinned
            );
        }

        return filteredModels;
    }

    /**
     * Model konfigürasyonunu al
     * @param {string} modelId - Model ID
     * @returns {Object}
     */
    getModelConfig(modelId) {
        return this.modelConfigs.get(modelId) || {};
    }

    /**
     * Model konfigürasyonunu güncelle
     * @param {string} modelId - Model ID
     * @param {Object} config - Yeni konfigürasyon
     */
    updateModelConfig(modelId, config) {
        const currentConfig = this.getModelConfig(modelId);
        const newConfig = { ...currentConfig, ...config };
        
        this.modelConfigs.set(modelId, newConfig);
        
        // Event emit et
        this.eventManager.emit('model:config-updated', {
            modelId,
            config: newConfig
        });
    }

    /**
     * Model'i pin/unpin yap
     * @param {string} modelId - Model ID
     * @param {boolean} pinned - Pin durumu
     */
    toggleModelPin(modelId, pinned) {
        const model = this.getModelById(modelId);
        if (!model) return false;

        model.isPinned = pinned;
        
        // Event emit et
        this.eventManager.emit('model:pinned', {
            modelId,
            pinned
        });

        return true;
    }

    /**
     * Model'i enable/disable yap
     * @param {string} modelId - Model ID
     * @param {boolean} enabled - Enable durumu
     */
    toggleModelEnabled(modelId, enabled) {
        const model = this.getModelById(modelId);
        if (!model) return false;

        model.isAvailable = enabled;
        
        // Event emit et
        this.eventManager.emit('model:enabled', {
            modelId,
            enabled
        });

        return true;
    }

    /**
     * Model istatistiklerini al
     * @returns {Object}
     */
    getModelStats() {
        const totalModels = this.models.length;
        const availableModels = this.models.filter(model => model.isAvailable).length;
        const pinnedModels = this.models.filter(model => model.isPinned).length;
        
        const providerStats = {};
        this.models.forEach(model => {
            providerStats[model.provider] = (providerStats[model.provider] || 0) + 1;
        });

        const typeStats = {};
        this.models.forEach(model => {
            typeStats[model.type] = (typeStats[model.type] || 0) + 1;
        });

        return {
            totalModels,
            availableModels,
            pinnedModels,
            providerStats,
            typeStats
        };
    }

    /**
     * Model arama
     * @param {string} query - Arama sorgusu
     * @returns {Array}
     */
    searchModels(query) {
        if (!query.trim()) return [];

        const searchTerm = query.toLowerCase();
        return this.models.filter(model => 
            model.name.toLowerCase().includes(searchTerm) ||
            model.description.toLowerCase().includes(searchTerm) ||
            model.provider.toLowerCase().includes(searchTerm)
        );
    }

    /**
     * Model kategorilerini al
     * @returns {Array}
     */
    getModelCategories() {
        const categories = new Set();
        
        this.models.forEach(model => {
            if (model.category) {
                categories.add(model.category);
            }
        });

        return Array.from(categories);
    }

    /**
     * Model etiketlerini al
     * @returns {Array}
     */
    getModelTags() {
        const tags = new Set();
        
        this.models.forEach(model => {
            if (model.tags && Array.isArray(model.tags)) {
                model.tags.forEach(tag => tags.add(tag));
            }
        });

        return Array.from(tags);
    }

    /**
     * Model'i güncelle
     * @param {string} modelId - Model ID
     * @param {Object} updates - Güncellemeler
     */
    updateModel(modelId, updates) {
        const model = this.getModelById(modelId);
        if (!model) return false;

        Object.assign(model, updates);
        
        // Event emit et
        this.eventManager.emit('model:updated', {
            model,
            modelId
        });

        return true;
    }

    /**
     * Model ekle
     * @param {Object} model - Model objesi
     */
    addModel(model) {
        // Model ID'si yoksa oluştur
        if (!model.id) {
            model.id = Helpers.generateId();
        }

        // Varsayılan değerleri ekle
        const defaultModel = {
            isAvailable: true,
            isPinned: false,
            capabilities: [],
            maxTokens: 32000,
            ...model
        };

        this.models.push(defaultModel);
        
        // Varsayılan konfigürasyon ekle
        this.modelConfigs.set(defaultModel.id, {
            temperature: 0.7,
            maxTokens: defaultModel.maxTokens,
            topP: 0.9,
            frequencyPenalty: 0,
            presencePenalty: 0,
            systemPrompt: '',
            customInstructions: '',
            isEnabled: true
        });

        // Event emit et
        this.eventManager.emit('model:added', {
            model: defaultModel
        });

        return defaultModel.id;
    }

    /**
     * Model sil
     * @param {string} modelId - Model ID
     */
    deleteModel(modelId) {
        const index = this.models.findIndex(model => model.id === modelId);
        if (index === -1) return false;

        const deletedModel = this.models.splice(index, 1)[0];
        this.modelConfigs.delete(modelId);
        
        // Event emit et
        this.eventManager.emit('model:deleted', {
            model: deletedModel,
            modelId
        });

        return true;
    }

    /**
     * Model'leri export et
     * @param {Object} options - Export seçenekleri
     * @returns {string}
     */
    exportModels(options = {}) {
        const { format = 'json', includeConfigs = false } = options;
        let data = this.models;

        if (includeConfigs) {
            data = this.models.map(model => ({
                ...model,
                config: this.getModelConfig(model.id)
            }));
        }

        switch (format) {
            case 'json':
                return JSON.stringify(data, null, 2);
            case 'csv':
                return this.exportToCSV(data);
            default:
                return JSON.stringify(data, null, 2);
        }
    }

    /**
     * CSV formatında export
     * @param {Array} models - Model listesi
     * @returns {string}
     */
    exportToCSV(models) {
        const headers = ['ID', 'Name', 'Provider', 'Type', 'Description', 'Max Tokens', 'Available', 'Pinned'];
        const rows = models.map(model => [
            model.id,
            `"${model.name}"`,
            model.provider,
            model.type,
            `"${model.description}"`,
            model.maxTokens,
            model.isAvailable,
            model.isPinned
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * Servisi temizle
     */
    destroy() {
        // Event listener'ları kaldır
        this.eventManager.off('model:selected');
        this.eventManager.off('model:change');

        console.log('ModelService destroyed');
    }
}
