/**
 * Zekai Admin Panel JavaScript
 * ===========================
 * @description Manages all functionality of the admin panel.
 * @version 1.0.0 (Refactored for better organization)
 * @author ZekAI Team (Refactored by AI Assistant)
 *
 * TABLE OF CONTENTS
 * =================
 * 1. CORE SYSTEM
 * 1.1. Logging System
 * 1.2. State Management (Basic)
 * 1.3. DOM Elements Cache
 * 1.4. Global Error Handlers (Placeholder)
 *
 * 2. UI COMPONENTS & UTILITIES
 * 2.1. Toast Notifications
 * 2.2. Page Loader
 * 2.3. Model Card Creation
 *
 * 3. RENDERING FUNCTIONS
 * 3.1. Model List Rendering (Add/Update/Remove)
 * 3.2. Active Menu Item
 *
 * 4. EVENT HANDLERS & SETUP
 * 4.1. Global Event Listeners Setup
 * 4.2. Page Specific Event Listeners Setup
 * 4.3. Model Card Event Listeners
 *
 * 5. OPERATIONS & LOGIC
 * 5.1. Theme Management
 * 5.2. Sidebar Management
 * 5.3. Page Navigation (AJAX)
 * 5.4. Model Filtering
 * 5.5. Model Modal Operations (Add/Edit)
 * 5.6. Model Actions (Delete)
 * 5.7. Chart Management
 *
 * 6. INITIALIZATION
 * 6.1. Main Initialization Function
 * 6.2. DOM Ready Initialization
 */

const AdminPanelManager = (function() {
    'use strict';

    //=============================================================================
    // 1. CORE SYSTEM
    //=============================================================================

    /**
     * 1.1. Logging System
     */
    const LOG_LEVELS = {
        debug: { priority: 0, color: 'color:#9E9E9E;', prefix: 'DEBUG' },
        info:  { priority: 1, color: 'color:#2196F3;', prefix: 'INFO ' },
        warn:  { priority: 2, color: 'color:#FFC107;', prefix: 'WARN ' },
        error: { priority: 3, color: 'color:#F44336;', prefix: 'ERROR'}
    };
    // Set to true to enable logging, or false to disable
    const DEBUG_LOG_ACTIVE = true; 
    // Set the minimum log level to display (e.g., 'info', 'debug')
    const ACTIVE_LOG_LEVEL = 'debug'; 

    function log(level, context, message, ...details) {
        if (!DEBUG_LOG_ACTIVE) return;
        const levelConfig = LOG_LEVELS[level] || LOG_LEVELS['info'];
        const activeLevelConfig = LOG_LEVELS[ACTIVE_LOG_LEVEL] || LOG_LEVELS['debug'];
        if (levelConfig.priority < activeLevelConfig.priority) return;

        const timestamp = new Date().toISOString().substr(11, 12);
        const logPrefix = `%c[${timestamp}] [${levelConfig.prefix}] [AdminPanel:${context}]`;
        
        if (details.length > 0) {
            console.groupCollapsed(logPrefix, levelConfig.color, message);
            details.forEach(detail => console.log(detail));
            console.groupEnd();
        } else {
            console.log(logPrefix, levelConfig.color, message);
        }
    }

    /**
     * 1.2. State Management (Basic)
     */
    const state = {
        sidebarCollapsed: false,
        currentTheme: 'light',
        modelToDelete: null,
        charts: {
            aiRequestTrendChartInstance: null,
            topModelsChartInstance: null
        }
    };

    /**
     * 1.3. DOM Elements Cache
     */
    const elements = {};

    function cacheCommonDOMElements() {
        log('info', 'DOM', 'Caching common DOM elements...');
        elements.htmlElement = document.documentElement;
        elements.sidebar = document.getElementById('sidebar');
        elements.mainContent = document.getElementById('mainContent');
        elements.sidebarToggle = document.getElementById('sidebarToggle');
        elements.themeToggle = document.getElementById('themeToggle');
        elements.themeIcon = document.getElementById('themeIcon');
        elements.navLinks = document.querySelectorAll('nav a.nav-link'); // For page navigation

        // Elements for Models page (might be loaded dynamically)
        elements.modelsContainer = document.getElementById('modelsContainer');
        elements.categoryFilter = document.getElementById('categoryFilter');
        elements.providerFilter = document.getElementById('providerFilter');
        elements.statusFilter = document.getElementById('statusFilter');
        elements.addModelBtn = document.getElementById('addModelBtn');
        // emptyAddModelBtn is created dynamically if no models exist, handle separately.
        
        elements.modelModal = document.getElementById('modelModal');
        elements.modalOverlay = document.getElementById('modalOverlay');
        elements.closeModalBtn = document.getElementById('closeModalBtn');
        elements.cancelModelBtn = document.getElementById('cancelModelBtn');
        elements.modelForm = document.getElementById('modelForm');
        elements.modalTitle = document.getElementById('modalTitle');
        
        elements.deleteConfirmModal = document.getElementById('deleteConfirmModal');
        elements.deleteModalOverlay = document.getElementById('deleteModalOverlay');
        elements.cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
        elements.confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

        // Chart elements
        elements.aiRequestTrendChart = document.getElementById('aiRequestTrendChart');
        elements.topModelsChart = document.getElementById('topModelsChart');
        elements.trendChartTimespanSelect = document.getElementById('trendChartTimespan');

        log('debug', 'DOM', 'Cached elements:', elements);
    }
    
    /**
     * 1.4. Global Error Handlers (Placeholder)
     * Consider adding global error handlers like in chat.js if needed.
     * window.onerror = function(...) { log('error', 'Global', ...); }
     * window.onunhandledrejection = function(...) { log('error', 'GlobalPromise', ...); }
     */

    //=============================================================================
    // 2. UI COMPONENTS & UTILITIES
    //=============================================================================

    /**
     * 2.1. Toast Notifications
     */
    function showToast(message, type = 'info') {
        log('action', 'Toast', `Showing toast: ${message}, type: ${type}`);
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'fixed bottom-4 right-4 z-[10000]'; // Ensure high z-index
            document.body.appendChild(container);
            toastContainer = container;
        }
        
        const toast = document.createElement('div');
        toast.className = `flex items-center p-4 mb-3 rounded-lg shadow-lg max-w-xs animate-fade-in-toast`;
        
        let bgColor, textColor, iconClass;
        switch (type) {
            case 'success':
                bgColor = 'bg-green-100 dark:bg-green-900/30';
                textColor = 'text-green-800 dark:text-green-300';
                iconClass = 'fa-check-circle';
                break;
            case 'error':
                bgColor = 'bg-red-100 dark:bg-red-900/30';
                textColor = 'text-red-800 dark:text-red-300';
                iconClass = 'fa-exclamation-circle';
                break;
            case 'warning':
                bgColor = 'bg-yellow-100 dark:bg-yellow-900/30';
                textColor = 'text-yellow-800 dark:text-yellow-300';
                iconClass = 'fa-exclamation-triangle';
                break;
            default: // info
                bgColor = 'bg-blue-100 dark:bg-blue-900/30';
                textColor = 'text-blue-800 dark:text-blue-300';
                iconClass = 'fa-info-circle';
        }
        
        toast.classList.add(...bgColor.split(' '), ...textColor.split(' '));
        
        toast.innerHTML = `
            <i class="fas ${iconClass} mr-3 text-lg"></i>
            <div class="text-sm font-medium">${message}</div>
            <button class="ml-auto text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        const closeBtn = toast.querySelector('button');
        closeBtn.addEventListener('click', () => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        });
        
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    /**
     * 2.2. Page Loader
     */
    function showPageLoader() {
        log('action', 'Loader', 'Showing page loader');
        let loader = document.querySelector('.page-loader-zk');
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'page-loader-zk fixed inset-0 bg-black bg-opacity-50 z-[9999] flex items-center justify-center';
            loader.innerHTML = `
                <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-lg flex items-center">
                    <div class="loader-spinner-zk mr-3"></div>
                    <p class="text-gray-700 dark:text-gray-300">Yükleniyor...</p>
                </div>
            `;
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    }

    function hidePageLoader() {
        log('action', 'Loader', 'Hiding page loader');
        const loader = document.querySelector('.page-loader-zk');
        if (loader) {
            loader.style.display = 'none';
        }
    }
    
    /**
     * 2.3. Model Card Creation
     * This is the more detailed version from the original admin.js for creating the full card HTML.
     */
    function createModelCardHTML(model) {
        log('debug', 'UI', '--- createModelCardHTML: Received model data ---', model);
        let statusClass = '';
        let statusText = '';
        
        switch(model.status) {
            case 'active':
                statusClass = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
                statusText = 'Aktif';
                break;
            case 'inactive':
                statusClass = 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400';
                statusText = 'Pasif';
                break;
            case 'maintenance':
                statusClass = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-500/30 dark:text-yellow-400';
                statusText = 'Beklemede';
                break;
            default:
                statusClass = 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400';
                statusText = model.status ? String(model.status).charAt(0).toUpperCase() + String(model.status).slice(1) : 'Belirsiz';
        }

        // Kategori adını bulmak için (API'den gelmiyorsa)
        let categoryNameDisplay = model.category_name || 'Kategori';
        if (!model.category_name && elements.categoryFilter) {
             const selectedOption = Array.from(elements.categoryFilter.options).find(option => option.value === String(model.category_id));
             if (selectedOption) categoryNameDisplay = selectedOption.textContent;
        }
        
        return `
        <div class="kpi-card rounded-xl shadow-custom overflow-hidden bg-white dark:bg-gray-800" data-model-id="${model.id}" data-category="${model.category_id}" data-provider="${model.service_provider}" data-status="${model.status}">
            <div class="p-5">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <span class="inline-block px-2.5 py-1 text-xs font-medium rounded-full mb-2 ${statusClass}">
                            ${statusText}
                        </span>
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">${model.name}</h3>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">${categoryNameDisplay}</p>
                    </div>
                    <div class="flex space-x-1">
                        <button class="edit-model-btn p-1.5 text-gray-500 dark:text-gray-400 hover:text-accent dark:hover:text-accent-light hover:bg-accent-light dark:hover:bg-gray-700 rounded-md" title="Düzenle" data-model-id="${model.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="delete-model-btn p-1.5 text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md" title="Sil" data-model-id="${model.id}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
                
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2 min-h-[2.5rem]">${model.description || 'Açıklama bulunmuyor.'}</p>
                
                <div class="grid grid-cols-2 gap-3 text-xs mb-4">
                    <div class="flex flex-col">
                        <span class="text-gray-500 dark:text-gray-400">Sağlayıcı</span>
                        <span class="font-medium text-gray-700 dark:text-gray-200">${model.service_provider ? model.service_provider.charAt(0).toUpperCase() + model.service_provider.slice(1) : 'N/A'}</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-gray-500 dark:text-gray-400">Dış Model Adı</span>
                        <span class="font-medium text-gray-700 dark:text-gray-200 truncate" title="${model.external_model_name || ''}">${model.external_model_name || 'N/A'}</span>
                    </div>
                    <div class="flex flex-col mt-2">
                        <span class="text-gray-500 dark:text-gray-400">API URL</span>
                        <span class="font-medium text-gray-700 dark:text-gray-200 truncate" title="${model.api_url || ''}">${model.api_url || 'N/A'}</span>
                    </div>
                    <div class="flex flex-col mt-2">
                        <span class="text-gray-500 dark:text-gray-400">Request Method</span>
                        <span class="font-medium text-gray-700 dark:text-gray-200">${model.request_method || 'POST'}</span>
                    </div>
                </div>
            </div>
            <div class="p-3 bg-[var(--card-footer-bg,theme(colors.gray.50))] dark:bg-[var(--dark-card-footer-bg,theme(colors.gray.700))] border-t border-[var(--card-border,theme(colors.gray.200))] dark:border-[var(--dark-card-border,theme(colors.gray.700))] rounded-b-lg">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-medium text-[var(--text-muted)] dark:text-[var(--dark-text-muted)]"><span class="${statusClass} text-xs font-medium me-2 px-2.5 py-0.5 rounded-full">${statusText}</span></span>
                    <button class="details-model-btn text-xs font-medium text-accent hover:text-accent-hover dark:text-accent-light dark:hover:text-accent" data-model-id="${model.id}">Detaylar</button>
                </div>
            </div>
        </div>
        `;
    }


    //=============================================================================
    // 3. RENDERING FUNCTIONS
    //=============================================================================

    /**
     * 3.1. Model List Rendering (Add/Update/Remove)
     * This is the consolidated and more detailed version of updateModelsList.
     */
    function renderOrUpdateModelInList(modelData, isEdit) {
        log('action', 'Render', `Rendering/Updating model in list. Edit: ${isEdit}`, modelData);
        elements.modelsContainer = elements.modelsContainer || document.getElementById('modelsContainer'); // Ensure it's fresh if page reloaded
        if (!elements.modelsContainer) {
            log('error', 'Render', 'Models container not found for rendering model.');
            return;
        }

        const modelCardHTML = createModelCardHTML(modelData);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = modelCardHTML;
        const newCardElement = tempDiv.firstElementChild;

        if (isEdit) {
            const existingCard = elements.modelsContainer.querySelector(`.kpi-card[data-model-id="${modelData.id}"]`);
            if (existingCard) {
                log('info', 'Render', `Updating existing model card: ${modelData.id}`);
                existingCard.replaceWith(newCardElement);
            } else {
                log('warn', 'Render', `Edit mode, but existing card not found for ID: ${modelData.id}. Appending as new.`);
                elements.modelsContainer.prepend(newCardElement); // Or append, depending on desired behavior
            }
        } else {
            const emptyState = elements.modelsContainer.querySelector('.empty-state-models');
            if (emptyState) {
                emptyState.remove();
            }
            log('info', 'Render', `Adding new model card: ${modelData.id}`);
            elements.modelsContainer.prepend(newCardElement);
        }
        setupModelCardEventListeners(newCardElement);
        rebindAllModelCardListeners();
        applyCurrentFilters(); // Re-apply filters if any
    }

    function removeModelFromListDOM(modelId) {
        log('action', 'Render', `Removing model from list DOM: ${modelId}`);
        elements.modelsContainer = elements.modelsContainer || document.getElementById('modelsContainer');
        if (!elements.modelsContainer) {
            log('error', 'Render', 'Models container not found for removing model.');
            return;
        }
        
        const modelCard = elements.modelsContainer.querySelector(`.kpi-card[data-model-id="${modelId}"]`);
        if (modelCard) {
            modelCard.style.transition = 'all 0.3s ease';
            modelCard.style.opacity = '0';
            modelCard.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                modelCard.remove();
                const remainingCards = elements.modelsContainer.querySelectorAll('.kpi-card[data-model-id]');
                if (remainingCards.length === 0) {
                    log('info', 'Render', 'No models left, showing empty state.');
                    elements.modelsContainer.innerHTML = `
                    <div class="col-span-1 md:col-span-2 lg:col-span-3 py-12 flex flex-col items-center justify-center text-center empty-state-models">
                        <div class="bg-accent-light text-accent p-4 rounded-full mb-4">
                            <i class="fas fa-robot text-3xl"></i>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">Henüz Model Yok</h3>
                        <p class="text-gray-600 dark:text-gray-300 mb-6 max-w-md">Sisteme henüz AI modeli eklenmemiş. İlk modeli eklemek için yukarıdaki 'Yeni Model Ekle' butonuna tıklayın.</p>
                        </div>
                    `;
                }
            }, 300);
        } else {
            log('warn', 'Render', `Model card not found for removal: ${modelId}`);
        }
    }
    
    /**
     * 3.2. Active Menu Item
     */
    function updateActiveMenuItem(pageName) {
        log('action', 'UI', `Updating active menu item for page: ${pageName}`);
        elements.navLinks.forEach(link => {
            link.classList.remove('active', 'bg-accent-light', 'text-accent', 'dark:bg-gray-700');
            link.classList.add('text-gray-600', 'dark:text-gray-300', 'hover:bg-gray-100', 'dark:hover:bg-gray-700');
            // Ensure the icon also resets color if specific classes were added
            const icon = link.querySelector('i');
            if (icon) {
                icon.classList.remove('text-accent');
                icon.classList.add('text-gray-400');
            }

        });
        
        const activeLink = document.querySelector(`nav a[href*="/admin/${pageName}"]`);
        if (activeLink) {
            activeLink.classList.add('active', 'bg-accent-light', 'text-accent', 'dark:bg-gray-700');
            activeLink.classList.remove('text-gray-600', 'dark:text-gray-300', 'hover:bg-gray-100', 'dark:hover:bg-gray-700');
            const icon = activeLink.querySelector('i');
            if (icon) {
                icon.classList.add('text-accent');
                icon.classList.remove('text-gray-400');
            }
        } else {
            log('warn', 'UI', `No matching nav link found for page: /admin/${pageName}`);
        }
    }

    //=============================================================================
    // 4. EVENT HANDLERS & SETUP
    //=============================================================================

    /**
     * 4.1. Global Event Listeners Setup
     */
    function setupGlobalEventListeners() {
        // Small delay to ensure all elements are likely in the DOM after initial render or AJAX load
        setTimeout(() => {
            cacheCommonDOMElements(); // Ensure critical elements like htmlElement are cached
            if (!elements.htmlElement) {
                log('error', 'Events', 'HTML element not found, cannot set up global listeners reliably.');
                return;
            }
        }, 0);
        log('info', 'Events', 'Setting up global event listeners.');

        if (elements.themeToggle) {
            elements.themeToggle.removeEventListener('click', handleThemeToggle);
            elements.themeToggle.addEventListener('click', handleThemeToggle);
        }
        if (elements.sidebarToggle) {
            elements.sidebarToggle.removeEventListener('click', handleSidebarToggle);
            elements.sidebarToggle.addEventListener('click', handleSidebarToggle);
        }

        elements.navLinks.forEach(link => {
            // Remove existing listener before adding, using a wrapper if the handler is anonymous or bound
            // For simplicity here, assuming direct re-attachment is okay if navLinks are re-fetched and are new elements
            // or if setupGlobalEventListeners is called sparingly.
            link.removeEventListener('click', handlePageNavigationClick); // Might need a named function or a more robust removal strategy if issues persist
            link.addEventListener('click', handlePageNavigationClick);
        });

        window.removeEventListener('popstate', handleBrowserNavigation);
        window.addEventListener('popstate', handleBrowserNavigation);
        window.removeEventListener('resize', handleWindowResize);
        window.addEventListener('resize', handleWindowResize);
        
        // Modal common close actions and form submit listeners are MOVED to setupPageSpecificEventListeners
        // to ensure they are bound correctly when modal/form HTML is loaded via AJAX for specific pages.
    }

    /**
     * Helper for adding model modal listener to avoid direct anonymous function if removeEventListener is needed.
     */
    const openAddModelModalHandler = () => openModelModal(false);

    /**
     * 4.2. Page Specific Event Listeners Setup
     */
    function setupPageSpecificEventListeners(pageName) {
        log('info', 'Events', `Setting up listeners for page: ${pageName}`);
        cacheCommonDOMElements(); // Re-cache elements that might be specific to the new page content

        if (pageName === 'models') {
            // Add Model Buttons
            if (elements.addModelBtn) {
                elements.addModelBtn.removeEventListener('click', openAddModelModalHandler);
                elements.addModelBtn.addEventListener('click', openAddModelModalHandler);
            }
            const emptyAddModelBtn = document.getElementById('emptyAddModelBtn'); 
            if (emptyAddModelBtn) {
                 emptyAddModelBtn.removeEventListener('click', openAddModelModalHandler);
                 emptyAddModelBtn.addEventListener('click', openAddModelModalHandler);
            }

            // Filters
            if (elements.categoryFilter) {
                elements.categoryFilter.removeEventListener('change', applyCurrentFilters);
                elements.categoryFilter.addEventListener('change', applyCurrentFilters);
            }
            if (elements.providerFilter) {
                elements.providerFilter.removeEventListener('change', applyCurrentFilters);
                elements.providerFilter.addEventListener('change', applyCurrentFilters);
            }
            if (elements.statusFilter) {
                elements.statusFilter.removeEventListener('change', applyCurrentFilters);
                elements.statusFilter.addEventListener('change', applyCurrentFilters);
            }
            
            // Model Add/Edit Modal Form Submit
            if (elements.modelForm) {
                elements.modelForm.removeEventListener('submit', handleModelFormSubmit);
                elements.modelForm.addEventListener('submit', handleModelFormSubmit);
            }

            // Model Add/Edit Modal Close Actions (X button, Cancel button, Overlay)
            if (elements.closeModalBtn) { 
                elements.closeModalBtn.removeEventListener('click', closeModelModal);
                elements.closeModalBtn.addEventListener('click', closeModelModal);
            }
            if (elements.cancelModelBtn) { 
                elements.cancelModelBtn.removeEventListener('click', closeModelModal);
                elements.cancelModelBtn.addEventListener('click', closeModelModal);
            }
            if (elements.modalOverlay) { 
                elements.modalOverlay.removeEventListener('click', closeModelModal);
                elements.modalOverlay.addEventListener('click', closeModelModal);
            }

            // Delete Confirmation Modal Actions
            if (elements.confirmDeleteBtn) {
                elements.confirmDeleteBtn.removeEventListener('click', handleDeleteModelConfirm);
                elements.confirmDeleteBtn.addEventListener('click', handleDeleteModelConfirm);
            }
            if (elements.cancelDeleteBtn) {
                elements.cancelDeleteBtn.removeEventListener('click', closeDeleteConfirmModal);
                elements.cancelDeleteBtn.addEventListener('click', closeDeleteConfirmModal);
            }
            if (elements.deleteModalOverlay) { 
                elements.deleteModalOverlay.removeEventListener('click', closeDeleteConfirmModal);
                elements.deleteModalOverlay.addEventListener('click', closeDeleteConfirmModal);
            }
            
            rebindAllModelCardListeners(); // Setup listeners for all model cards on the page
        }

        if (pageName === 'dashboard') {
            if (elements.trendChartTimespanSelect) {
                elements.trendChartTimespanSelect.removeEventListener('change', handleTrendChartTimespanChange);
                elements.trendChartTimespanSelect.addEventListener('change', handleTrendChartTimespanChange);
            }
            initializeCharts();
        }
    }

    /**
     * 4.3. Model Card Event Listeners
     */
    function setupModelCardEventListeners(cardElement) {
        const modelId = cardElement.dataset.modelId;
        if (!modelId) return;

        // --- Event listener'ları önce temizle (memory leak/çakışma önlemi) ---
        const editBtn = cardElement.querySelector(`.edit-model-btn[data-model-id="${modelId}"]`);
        const deleteBtn = cardElement.querySelector(`.delete-model-btn[data-model-id="${modelId}"]`);
        const detailsBtn = cardElement.querySelector(`.details-model-btn[data-model-id="${modelId}"]`);

        if (editBtn) {
            editBtn.replaceWith(editBtn.cloneNode(true));
        }
        if (deleteBtn) {
            deleteBtn.replaceWith(deleteBtn.cloneNode(true));
        }
        if (detailsBtn) {
            detailsBtn.replaceWith(detailsBtn.cloneNode(true));
        }

        // Tekrar seç (çünkü cloneNode ile DOM değişti)
        const freshEditBtn = cardElement.querySelector(`.edit-model-btn[data-model-id="${modelId}"]`);
        const freshDeleteBtn = cardElement.querySelector(`.delete-model-btn[data-model-id="${modelId}"]`);
        const freshDetailsBtn = cardElement.querySelector(`.details-model-btn[data-model-id="${modelId}"]`);

        if (freshEditBtn) {
            freshEditBtn.addEventListener('click', async function() {
                log('action', 'ModelCard', `Edit button clicked for model: ${modelId}`);
                try {
                    const response = await fetch(`/admin/api/models/${modelId}`);
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({ error: 'Sunucudan geçersiz yanıt.' }));
                        throw new Error(errorData.error || `Model verileri alınamadı: ${response.status}`);
                    }
                    const data = await response.json();
                    if (data.model) {
                        openModelModal(true, data.model);
                    } else {
                        throw new Error('Model verisi eksik.');
                    }
                } catch (error) {
                    log('error', 'ModelCard', `Edit error: ${error.message}`);
                    showToast(error.message, 'error');
                }
            });
        }
        if (freshDeleteBtn) {
            freshDeleteBtn.addEventListener('click', function() {
                log('action', 'ModelCard', `Delete button clicked for model: ${modelId}`);
                state.modelToDelete = modelId;
                if (elements.deleteConfirmModal) {
                    elements.deleteConfirmModal.classList.remove('hidden');
                } else {
                    log('error', 'ModelCard', 'Delete confirmation modal not found.');
                }
            });
        }
        if (freshDetailsBtn) {
            freshDetailsBtn.addEventListener('click', function() {
                log('info', 'ModelCard', `Details button clicked for model: ${modelId}. (No action defined yet)`);
                showToast(`Model ${modelId} için detay görüntüleme henüz aktif değil.`, 'info');
            });
        }
    }

    // Sayfa yüklendiğinde ve yeni model eklendiğinde tüm kartlara listener bağla
    function rebindAllModelCardListeners() {
        elements.modelsContainer = elements.modelsContainer || document.getElementById('modelsContainer');
        if (!elements.modelsContainer) return;
        const cards = elements.modelsContainer.querySelectorAll('.kpi-card[data-model-id]');
        cards.forEach(card => setupModelCardEventListeners(card));
    }

    //=============================================================================
    // 5. OPERATIONS & LOGIC
    //=============================================================================

    /**
     * 5.1. Theme Management
     */
    function applyTheme(theme) {
        log('action', 'Theme', `Applying theme: ${theme}`);
        if (!elements.htmlElement || !elements.themeIcon) {
            log('warn', 'Theme', 'HTML element or theme icon not cached for applying theme.');
            cacheCommonDOMElements(); // Try to cache them again
             if (!elements.htmlElement || !elements.themeIcon) {
                log('error', 'Theme', 'Critical theme elements still not found.');
                return;
             }
        }

        if (theme === 'dark') {
            elements.htmlElement.classList.add('dark');
            elements.themeIcon.classList.remove('fa-moon');
            elements.themeIcon.classList.add('fa-sun');
        } else {
            elements.htmlElement.classList.remove('dark');
            elements.themeIcon.classList.remove('fa-sun');
            elements.themeIcon.classList.add('fa-moon');
        }
        state.currentTheme = theme;
        localStorage.setItem('theme', theme);

        // Re-initialize charts if they exist, as their colors might depend on the theme
        if (state.charts.aiRequestTrendChartInstance || state.charts.topModelsChartInstance) {
            log('info', 'Theme', 'Theme changed, re-initializing charts.');
            destroyCharts();
            initializeCharts(); // This will pick up new theme colors
        }
    }

    function handleThemeToggle() {
        const newTheme = elements.htmlElement.classList.contains('dark') ? 'light' : 'dark';
        applyTheme(newTheme);
    }

    /**
     * 5.2. Sidebar Management
     */
    function setSidebarState(collapsed) {
        if (!elements.sidebar || !elements.mainContent) {
            log('warn', 'Sidebar', 'Sidebar or main content element not cached.');
            return;
        }
        if (collapsed) {
            elements.sidebar.classList.add('collapsed');
            elements.mainContent.style.marginLeft = '80px'; // Ensure this matches collapsed sidebar width
        } else {
            elements.sidebar.classList.remove('collapsed');
            elements.mainContent.style.marginLeft = '250px'; // Ensure this matches expanded sidebar width
        }
        state.sidebarCollapsed = collapsed;
        localStorage.setItem('sidebarCollapsed', collapsed);
        log('action', 'Sidebar', `Sidebar state set to: ${collapsed ? 'collapsed' : 'expanded'}`);
    }

    function handleSidebarToggle() {
        setSidebarState(!elements.sidebar.classList.contains('collapsed'));
    }
    
    function handleWindowResize() {
        log('debug', 'UI', 'Window resize event triggered.');
        const isMobileView = window.innerWidth < 1024; // Tailwind 'lg' breakpoint
        if (isMobileView) {
            if (!state.sidebarCollapsed) { // If sidebar is open on mobile, collapse it
                setSidebarState(true);
            }
        } else {
            // Optional: Restore sidebar state on larger screens based on user's last preference
            // For now, we let manual toggle manage it on larger screens.
            // Or, you could force it open if it was collapsed ONLY due to mobile view:
            // const lastKnownCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            // setSidebarState(lastKnownCollapsed);
             if (elements.sidebar && elements.mainContent) { // Ensure elements are available
                if (elements.sidebar.classList.contains('collapsed')) {
                    elements.mainContent.style.marginLeft = '80px';
                } else {
                    elements.mainContent.style.marginLeft = '250px';
                }
            }
        }
    }

    /**
     * 5.3. Page Navigation (AJAX)
     */
    async function loadPageContent(pageName, addToHistory = true) {
        log('action', 'Navigation', `Loading page content: ${pageName}, addToHistory: ${addToHistory}`);
        showPageLoader();
        try {
            const response = await fetch(`/admin/${pageName}`);
            if (!response.ok) {
                throw new Error(`Sayfa yüklenemedi: ${response.status} ${response.statusText}`);
            }
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const newContent = doc.querySelector('#mainContent');
            if (newContent && elements.mainContent) {
                elements.mainContent.innerHTML = newContent.innerHTML;
            }
            document.title = `${pageName.charAt(0).toUpperCase() + pageName.slice(1)} - Zekai Admin`;

            if (addToHistory) {
                history.pushState({ page: pageName }, '', `/admin/${pageName}`);
            }
            
            updateActiveMenuItem(pageName);
            setupPageSpecificEventListeners(pageName); // Setup listeners for the new content
            rebindAllModelCardListeners();

        } catch (error) {
            log('error', 'Navigation', `Page load error: ${error.message}`, error);
            showToast('Sayfa yüklenirken bir hata oluştu.', 'error');
        } finally {
            hidePageLoader();
        }
    }

    function handlePageNavigationClick(event) {
        event.preventDefault();
        const href = this.getAttribute('href');
        if (!href || href.startsWith('#') || href === 'javascript:void(0)') return;
        
        // Extract page name, assuming URL like /admin/dashboard or /admin/models
        const pageName = href.substring(href.lastIndexOf('/') + 1);
        if (pageName) {
            loadPageContent(pageName);
        } else {
            log('warn', 'Navigation', `Could not extract page name from href: ${href}`);
        }
    }

    function handleBrowserNavigation(event) {
        if (event.state && event.state.page) {
            log('info', 'Navigation', `Browser navigation (popstate) to page: ${event.state.page}`);
            loadPageContent(event.state.page, false);
        }
    }

    /**
     * 5.4. Model Filtering
     */
    function applyCurrentFilters() {
        log('action', 'Filter', 'Applying current filters to model list.');
        elements.modelsContainer = elements.modelsContainer || document.getElementById('modelsContainer');
        elements.categoryFilter = elements.categoryFilter || document.getElementById('categoryFilter');
        elements.providerFilter = elements.providerFilter || document.getElementById('providerFilter');
        elements.statusFilter = elements.statusFilter || document.getElementById('statusFilter');

        if (!elements.modelsContainer) {
            log('warn', 'Filter', 'Models container not found for filtering.');
            return;
        }
        // Ensure filter elements exist before trying to read their values
        const categoryValue = elements.categoryFilter ? elements.categoryFilter.value : '';
        const providerValue = elements.providerFilter ? elements.providerFilter.value : '';
        const statusValue = elements.statusFilter ? elements.statusFilter.value : '';

        const modelCards = elements.modelsContainer.querySelectorAll('.kpi-card[data-model-id]');
        let visibleCount = 0;

        modelCards.forEach(card => {
            const categoryMatch = !categoryValue || card.dataset.category === categoryValue;
            const providerMatch = !providerValue || card.dataset.provider === providerValue;
            const statusMatch = !statusValue || card.dataset.status === statusValue;
            
            if (categoryMatch && providerMatch && statusMatch) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        let noResultsElement = elements.modelsContainer.querySelector('#noFilterResultsMessage');
        if (visibleCount === 0 && modelCards.length > 0) {
            if (!noResultsElement) {
                noResultsElement = document.createElement('div');
                noResultsElement.id = 'noFilterResultsMessage';
                noResultsElement.className = 'col-span-1 md:col-span-2 lg:col-span-3 py-12 flex flex-col items-center justify-center text-center';
                noResultsElement.innerHTML = `
                    <div class="bg-accent-light text-accent p-4 rounded-full mb-4">
                        <i class="fas fa-filter text-3xl"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">Sonuç Bulunamadı</h3>
                    <p class="text-gray-600 dark:text-gray-300 max-w-md mb-6">Seçtiğiniz filtrelere uygun model bulunamadı. Lütfen filtreleri değiştirin veya temizleyin.</p>
                    <button id="clearFiltersBtn" class="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center">
                        <i class="fas fa-times mr-2"></i> Filtreleri Temizle
                    </button>
                `;
                elements.modelsContainer.appendChild(noResultsElement);
                
                document.getElementById('clearFiltersBtn').addEventListener('click', function() {
                    if(elements.categoryFilter) elements.categoryFilter.value = '';
                    if(elements.providerFilter) elements.providerFilter.value = '';
                    if(elements.statusFilter) elements.statusFilter.value = '';
                    applyCurrentFilters();
                });
            }
            noResultsElement.style.display = 'flex';
        } else if (noResultsElement) {
            noResultsElement.style.display = 'none';
        }
        log('info', 'Filter', `Filtering complete. Visible models: ${visibleCount}`);
    }

    /**
     * 5.5. Model Modal Operations (Add/Edit)
     */
    function openModelModal(isEdit = false, modelData = null) {
        log('action', 'Modal', `Opening model modal. Edit: ${isEdit}`, modelData);
        if (!elements.modelModal || !elements.modalTitle || !elements.modelForm) {
            log('error', 'Modal', 'Model modal elements not found.');
            return;
        }
        elements.modalTitle.textContent = isEdit ? 'Modeli Düzenle' : 'Yeni Model Ekle';
        elements.modelForm.reset(); // Reset form first

        if (isEdit && modelData) {
            document.getElementById('modelId').value = modelData.id || '';
            document.getElementById('modelName').value = modelData.name || '';
            document.getElementById('modelCategory').value = modelData.category_id || '';
            document.getElementById('modelDescription').value = modelData.description || '';
            document.getElementById('modelProvider').value = modelData.service_provider || '';
            document.getElementById('modelExternalName').value = modelData.external_model_name || '';
            document.getElementById('modelApiUrl').value = modelData.api_url || '';
            document.getElementById('modelRequestMethod').value = modelData.request_method || 'POST';
            document.getElementById('modelStatus').value = modelData.status || 'inactive';
            document.getElementById('modelPricePerToken').value = modelData.price_per_token === null || modelData.price_per_token === undefined ? '' : modelData.price_per_token;

        } else {
            document.getElementById('modelId').value = ''; // Ensure ID is cleared for new models
            document.getElementById('modelStatus').value = 'inactive'; // Default status
            document.getElementById('modelRequestMethod').value = 'POST'; // Default method
        }
        elements.modelModal.classList.remove('hidden');
        // DO NOT re-call setupGlobalEventListeners() here.
        // Modal specific listeners are handled by setupPageSpecificEventListeners or directly if needed.
    }

    function closeModelModal() {
        log('action', 'Modal', 'Closing model modal.');
        if (elements.modelModal && elements.modelForm) {
            elements.modelModal.classList.add('hidden');
            elements.modelForm.reset();
        }
    }

    async function handleModelFormSubmit(event) {
        event.preventDefault();
        log('action', 'Form', 'Model form submitted.');
        const formData = new FormData(elements.modelForm);
        const modelId = formData.get('modelId');
        const isEdit = modelId !== '' && modelId !== null && typeof modelId !== 'undefined';
        
        const modelData = {};
        formData.forEach((value, key) => {
            if (key === 'modelId') return; // Don't send modelId in the body if it's for URL
            if (key === 'category_id' || key === 'modelCategory') { // Handle both possible names
                modelData['category_id'] = value ? parseInt(value) : null;
            } else if (key === 'price_per_token' || key === 'modelPricePerToken') {
                modelData['price_per_token'] = value === '' ? null : parseFloat(value);
            } 
            else {
                // Convert form field names like 'modelName' to 'name' for the API
                const apiFieldKey = key.startsWith('model') ? key.substring(5).charAt(0).toLowerCase() + key.substring(6) : key;
                modelData[apiFieldKey] = value;
            }
        });
        // Ensure 'name' field is correctly mapped if it was 'modelName'
        if (modelData.hasOwnProperty('Name') && !modelData.hasOwnProperty('name')) {
             modelData.name = modelData.Name;
             delete modelData.Name;
        }


        const url = isEdit ? `/admin/api/models/${modelId}` : '/admin/api/models';
        const method = isEdit ? 'PUT' : 'POST';
        
        const submitBtn = document.getElementById('submitModelBtn');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Kaydediliyor...';

        try {
            log('info', 'API', `Sending model data to ${method} ${url}`, modelData);
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(modelData)
            });

            const responseData = await response.json();
            if (!response.ok) {
                throw new Error(responseData.error || `Bir hata oluştu: ${response.status}`);
            }
            
            showToast(responseData.message || (isEdit ? 'Model başarıyla güncellendi.' : 'Yeni model başarıyla eklendi.'), 'success');
            closeModelModal();
            
            loadPageContent('models', false);

        } catch (error) {
            log('error', 'FormSubmit', `Error submitting model form: ${error.message}`, error);
            showToast(error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    }

    /**
     * 5.6. Model Actions (Delete)
     */
    function closeDeleteConfirmModal() {
        log('action', 'Modal', 'Closing delete confirmation modal.');
        if (elements.deleteConfirmModal) {
            elements.deleteConfirmModal.classList.add('hidden');
        }
        state.modelToDelete = null;
    }

    async function handleDeleteModelConfirm() {
        if (!state.modelToDelete) {
            log('warn', 'Delete', 'No model ID set for deletion.');
            return;
        }
        log('action', 'Delete', `Confirming deletion for model: ${state.modelToDelete}`);

        const modelIdToDelete = state.modelToDelete; // Store locally in case state changes
        const originalBtnText = elements.confirmDeleteBtn.innerHTML;
        elements.confirmDeleteBtn.disabled = true;
        elements.confirmDeleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Siliniyor...';

        try {
            const response = await fetch(`/admin/api/models/${modelIdToDelete}`, {
                method: 'DELETE',
                headers: { 'Accept': 'application/json' }
            });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Model silinemedi: ${response.status}`);
            }
            
            showToast(data.message || 'Model başarıyla silindi.', 'success');
            closeDeleteConfirmModal();
            removeModelFromListDOM(modelIdToDelete);

        } catch (error) {
            log('error', 'Delete', `Error deleting model: ${error.message}`, error);
            showToast(error.message, 'error');
        } finally {
            elements.confirmDeleteBtn.disabled = false;
            elements.confirmDeleteBtn.innerHTML = originalBtnText;
            state.modelToDelete = null; // Clear it regardless of outcome
        }
    }
    
    /**
     * 5.7. Chart Management
     */
    function getChartThemeColors() {
        const isDarkMode = elements.htmlElement ? elements.htmlElement.classList.contains('dark') : false;
        // Ensure CSS variables are loaded and accessible
        const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color')?.trim() || '#4A90E2'; // Default accent
        return {
            primary: accentColor,
            primaryTransparent: `${accentColor}33`, // Approx 20% opacity
            gridColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
            textColor: isDarkMode ? '#cbd5e1' : '#4b5563', // Tailwind gray-300 / gray-600
            tooltipBg: isDarkMode ? '#1f2937' : '#ffffff', // Tailwind gray-800 / white
            doughnutBorder: isDarkMode ? '#374151' : '#ffffff' // Tailwind gray-700 / white (card bg for dark, white for light)
        };
    }

    function loadAiRequestTrendChart() {
        elements.aiRequestTrendChart = elements.aiRequestTrendChart || document.getElementById('aiRequestTrendChart');
        if (!elements.aiRequestTrendChart || typeof Chart === 'undefined') {
            log('warn', 'Charts', 'AI Request Trend Chart canvas not found or Chart.js not loaded.');
            return;
        }
        if (state.charts.aiRequestTrendChartInstance) state.charts.aiRequestTrendChartInstance.destroy();

        const themeColors = getChartThemeColors();
        const days = elements.trendChartTimespanSelect ? parseInt(elements.trendChartTimespanSelect.value) : 30;
        const labels = Array.from({length: days}, (_, i) => `${i + 1}`); // Simple day numbers
        const data = Array.from({length: days}, () => Math.floor(Math.random() * 280) + 50); // Random data

        state.charts.aiRequestTrendChartInstance = new Chart(elements.aiRequestTrendChart, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'AI İstekleri',
                    data: data,
                    borderColor: themeColors.primary,
                    backgroundColor: themeColors.primaryTransparent,
                    borderWidth: 2,
                    pointBackgroundColor: themeColors.primary,
                    pointBorderColor: themeColors.doughnutBorder, // Use doughnutBorder for point border for contrast
                    pointRadius: 0, // No points by default
                    pointHoverRadius: 5,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    y: { grid: { color: themeColors.gridColor, drawBorder: false }, ticks: { color: themeColors.textColor, font: {size: 10} } },
                    x: { grid: { display: false }, ticks: { color: themeColors.textColor, font: {size: 10} } }
                },
                plugins: { legend: { display: false }, tooltip: { backgroundColor: themeColors.tooltipBg, titleColor: themeColors.textColor, bodyColor: themeColors.textColor, padding: 10, cornerRadius: 4, boxPadding: 3 } }
            }
        });
        log('info', 'Charts', 'AI Request Trend Chart loaded/reloaded.');
    }

    function loadTopModelsChart() {
        elements.topModelsChart = elements.topModelsChart || document.getElementById('topModelsChart');
        if (!elements.topModelsChart || typeof Chart === 'undefined') {
            log('warn', 'Charts', 'Top Models Chart canvas not found or Chart.js not loaded.');
            return;
        }
        if (state.charts.topModelsChartInstance) state.charts.topModelsChartInstance.destroy();
        
        const themeColors = getChartThemeColors();
        const modelLabels = ['GPT-4 Turbo', 'Claude 3 Sonnet', 'Gemini Pro', 'Llama 3 70B', 'Diğer'];
        const modelData = [320, 210, 150, 100, 70]; // Random data
        const backgroundColors = [
            themeColors.primary, 
            '#60A5FA', // blue-400
            '#34D399', // green-400
            '#FBBF24', // yellow-400
            '#F87171'  // red-400
        ].map(c => elements.htmlElement.classList.contains('dark') ? `${c}BF` : c); // Add opacity for dark mode

        state.charts.topModelsChartInstance = new Chart(elements.topModelsChart, {
            type: 'doughnut',
            data: {
                labels: modelLabels,
                datasets: [{
                    data: modelData,
                    backgroundColor: backgroundColors,
                    borderColor: themeColors.doughnutBorder,
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: themeColors.textColor, usePointStyle: true, boxWidth: 10, padding: 15, font: {size: 11} } }, tooltip: { backgroundColor: themeColors.tooltipBg, titleColor: themeColors.textColor, bodyColor: themeColors.textColor, padding: 10, cornerRadius: 4, boxPadding: 3 } },
                cutout: '65%'
            }
        });
        log('info', 'Charts', 'Top Models Chart loaded/reloaded.');
    }

    function destroyCharts() {
        if (state.charts.aiRequestTrendChartInstance) {
            state.charts.aiRequestTrendChartInstance.destroy();
            state.charts.aiRequestTrendChartInstance = null;
            log('info', 'Charts', 'AI Request Trend Chart destroyed.');
        }
        if (state.charts.topModelsChartInstance) {
            state.charts.topModelsChartInstance.destroy();
            state.charts.topModelsChartInstance = null;
            log('info', 'Charts', 'Top Models Chart destroyed.');
        }
    }

    function initializeCharts() {
        log('action', 'Charts', 'Initializing charts.');
        // Ensure Chart.js is loaded
        if (typeof Chart === 'undefined') {
            log('error', 'Charts', 'Chart.js is not loaded. Cannot initialize charts.');
            return;
        }
        loadAiRequestTrendChart();
        loadTopModelsChart();
    }
    
    function handleTrendChartTimespanChange(event) {
        if (state.charts.aiRequestTrendChartInstance) {
            log('action', 'Charts', `Trend chart timespan changed to: ${event.target.value} days`);
            const days = parseInt(event.target.value);
            state.charts.aiRequestTrendChartInstance.data.labels = Array.from({length: days}, (_, i) => `${i + 1}`);
            state.charts.aiRequestTrendChartInstance.data.datasets[0].data = Array.from({length: days}, () => Math.floor(Math.random() * 280) + 50);
            state.charts.aiRequestTrendChartInstance.update();
        }
    }


    //=============================================================================
    // 6. INITIALIZATION
    //=============================================================================

    /**
     * 6.1. Main Initialization Function
     */
    function init() {
        log('info', 'Init', 'AdminPanelManager initializing...');
        cacheCommonDOMElements();

        // Initialize theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);

        // Initialize sidebar state
        const savedSidebarState = localStorage.getItem('sidebarCollapsed') === 'true';
        setSidebarState(savedSidebarState);
        handleWindowResize(); // Adjust sidebar based on initial window size

        setupGlobalEventListeners();
        
        // Initial page load (e.g., dashboard or based on URL)
        // Determine initial page from URL path or default to 'dashboard'
        const pathSegments = window.location.pathname.split('/');
        const initialPage = pathSegments[pathSegments.length -1] || 'dashboard';
        if (initialPage && initialPage !== 'admin' && initialPage !== '') {
             loadPageContent(initialPage, false); // Load initial page without adding to history again
             updateActiveMenuItem(initialPage);
        } else {
             loadPageContent('dashboard', false); // Default to dashboard
             updateActiveMenuItem('dashboard');
        }


        // Inject necessary CSS for animations if not already present
        const styleId = 'admin-panel-dynamic-styles';
        if (!document.getElementById(styleId)) {
            const styleElement = document.createElement('style');
            styleElement.id = styleId;
            styleElement.textContent = `
                @keyframes fadeInToast {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in-toast { animation: fadeInToast 0.3s ease-out forwards; }

                .loader-spinner-zk {
                    border: 3px solid rgba(0, 0, 0, 0.1);
                    border-radius: 50%;
                    border-top-color: var(--accent-color, #4A90E2); /* Use accent or a default */
                    width: 24px;
                    height: 24px;
                    animation: spin-zk 1s linear infinite;
                }
                @keyframes spin-zk {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(styleElement);
        }
        log('info', 'Init', 'AdminPanelManager initialization complete.');
    }

    /**
     * 6.2. DOM Ready Initialization
     */
    document.addEventListener('DOMContentLoaded', () => {
        init();
    });

    // Expose public methods if any (though for admin panel, init might be enough)
    return {
        init, // Could be called again if needed, e.g. after full page reloads by other scripts
        // Potentially expose other functions if they need to be called from outside, e.g. from inline scripts
        // openModelModal, // Example: if a button outside this script needs to open it
        // showToast // Example: if other scripts need to show toasts
    };

})();
