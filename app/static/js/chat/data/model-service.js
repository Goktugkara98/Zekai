/**
 * Model Service
 * AI model yönetimi ve konfigürasyon
 */

import { Helpers } from '../utils/helpers.js';
import { i18n } from '../utils/i18n.js';

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
        await this.loadModels();
        
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
    async loadModels() {
        try {
            console.log('Loading models from API...');
            const response = await fetch('/api/models');
            const result = await response.json();
            
            console.log('API response:', result);
            
            if (result.success) {
                this.models = result.data.map(model => this.transformModelData(model));
                console.log('Models loaded from API:', this.models.length, this.models);
                
                // Event emit et
                this.eventManager.emit('models:loaded', {
                    models: this.models,
                    count: this.models.length
                });
            } else {
                console.error('Failed to load models:', result.error);
                this.models = [];
            }
        } catch (error) {
            console.error('Error loading models:', error);
            this.models = [];
        }
    }

    /**
     * Database model verisini frontend formatına dönüştür
     * @param {Object} dbModel - Database model verisi
     * @returns {Object} Frontend model objesi
     */
    transformModelData(dbModel) {
        console.log('Transforming model data:', dbModel);
        
        // Provider'a göre icon ve color belirle
        const providerConfig = this.getProviderConfig(dbModel.provider_name);
        
        const transformedModel = {
            id: `model-${dbModel.model_id}`,
            name: dbModel.model_name,
            model_name: dbModel.model_name, // Backend ile uyumluluk için
            provider: dbModel.provider_name || 'Unknown',
            type: dbModel.model_type || 'text',
            description: i18n.t('model_by_provider', { provider: dbModel.provider_name || i18n.t('unknown_provider') }),
            icon: providerConfig.icon,
            color: providerConfig.color,
            logoUrl: dbModel.logo_path || null,
            categories: Array.isArray(dbModel.categories) ? dbModel.categories : [],
            primaryCategory: dbModel.primary_category || null,
            capabilities: this.getModelCapabilities(dbModel.model_type),
            maxTokens: 32000, // Default value
            isAvailable: Boolean(dbModel.is_active),
            isPinned: false, // Default value
            modelId: dbModel.model_id,
            apiKey: dbModel.api_key,
            createdAt: dbModel.created_at,
            updatedAt: dbModel.updated_at
        };
        
        console.log('Transformed model:', transformedModel);
        return transformedModel;
    }

    /**
     * Provider konfigürasyonunu al
     * @param {string} provider - Provider adı
     * @returns {Object} Provider konfigürasyonu
     */
    getProviderConfig(provider) {
        const configs = {
            'OpenAI': { icon: 'fas fa-robot', color: '#10a37f' },
            'Google': { icon: 'fab fa-google', color: '#4285f4' },
            'Anthropic': { icon: 'fas fa-brain', color: '#d97706' },
            'DeepSeek': { icon: 'fas fa-search', color: '#7c3aed' },
            'Meta': { icon: 'fas fa-mountain', color: '#059669' },
            'Perplexity': { icon: 'fas fa-question-circle', color: '#dc2626' },
            'default': { icon: 'fas fa-cog', color: '#6b7280' }
        };
        
        return configs[provider] || configs.default;
    }

    /**
     * Model tipine göre capabilities belirle
     * @param {string} modelType - Model tipi
     * @returns {Array} Capabilities listesi
     */
    getModelCapabilities(modelType) {
        const capabilities = {
            'text': ['text', 'reasoning'],
            'TEXT': ['text', 'reasoning'],
            'multimodal': ['text', 'image', 'code'],
            'MULTIMODAL': ['text', 'image', 'code'],
            'code': ['text', 'code', 'math'],
            'CODE': ['text', 'code', 'math'],
            'search': ['text', 'search', 'web'],
            'SEARCH': ['text', 'search', 'web'],
            'default': ['text']
        };
        
        return capabilities[modelType] || capabilities.default;
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
