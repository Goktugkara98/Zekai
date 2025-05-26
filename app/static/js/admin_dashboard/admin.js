/**
 * Zekai Admin Panel JavaScript (No AJAX Navigation)
 * =================================================
 * @description Manages all functionality of the admin panel.
 * @version 1.1.0
 * @author ZekAI Team (Refactored by AI Assistant)
 */

const AdminPanelManager = (function() {
    'use strict';

    //=============================================================================
    // 1. CORE SYSTEM
    //=============================================================================
    const LOG_LEVELS = {
        debug: { priority: 0, color: 'color:#9E9E9E;', prefix: 'DEBUG' },
        info:  { priority: 1, color: 'color:#2196F3;', prefix: 'INFO ' },
        warn:  { priority: 2, color: 'color:#FFC107;', prefix: 'WARN ' },
        error: { priority: 3, color: 'color:#F44336;', prefix: 'ERROR'}
    };
    const DEBUG_LOG_ACTIVE = true;
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

    const state = {
        sidebarCollapsed: false,
        currentTheme: 'light',
        itemToDelete: { id: null, type: null }, // For both models and categories
        charts: {
            aiRequestTrendChartInstance: null,
            topModelsChartInstance: null
        },
        currentPage: '' // To identify the current page for specific listeners
    };

    const elements = {}; // Cache for DOM elements

    function getCurrentPageFromURL() {
        const pathSegments = window.location.pathname.split('/');
        // Example: /admin/dashboard -> dashboard, /admin/models -> models
        let page = pathSegments[pathSegments.length - 1] || 'dashboard';
        if (page === 'admin') page = 'dashboard'; // Handle base /admin URL
        return page;
    }

    function cacheCommonDOMElements() {
        log('info', 'DOM', 'Caching common DOM elements...');
        elements.htmlElement = document.documentElement;
        elements.sidebar = document.getElementById('sidebar');
        elements.mainContent = document.getElementById('mainContent'); // Main content area
        elements.sidebarToggle = document.getElementById('sidebarToggle');
        elements.themeToggle = document.getElementById('themeToggle');
        elements.themeIcon = document.getElementById('themeIcon');
        elements.navLinks = document.querySelectorAll('nav a.nav-link');
        elements.pageLoader = document.querySelector('.page-loader-zk'); // Central page loader
    }

    function cachePageSpecificDOMElements(pageName) {
        log('info', 'DOM', `Caching elements for page: ${pageName}`);
        if (pageName === 'models') {
            elements.modelsContainer = document.getElementById('modelsContainer');
            elements.categoryFilter = document.getElementById('categoryFilter');
            elements.providerFilter = document.getElementById('providerFilter');
            elements.statusFilter = document.getElementById('statusFilter');
            elements.addModelBtn = document.getElementById('addModelBtn');
            elements.emptyAddModelBtn = document.getElementById('emptyAddModelBtn'); // Dynamic button
            elements.modelModal = document.getElementById('modelModal');
            elements.modelModalOverlay = document.getElementById('modalOverlay'); // Specific to model modal
            elements.closeModelModalBtn = document.getElementById('closeModalBtn'); // Specific to model modal
            elements.cancelModelBtn = document.getElementById('cancelModelBtn');
            elements.modelForm = document.getElementById('modelForm');
            elements.modelModalTitle = document.getElementById('modalTitle'); // Specific to model modal
            elements.deleteModelConfirmModal = document.getElementById('deleteModelConfirmModal'); // Corrected ID
            elements.deleteModelModalOverlay = document.getElementById('deleteModelModalOverlay');
            elements.cancelDeleteModelBtn = document.getElementById('cancelDeleteModelBtn'); // Corrected ID
            elements.confirmDeleteModelBtn = document.getElementById('confirmDeleteModelBtn'); // Corrected ID
        } else if (pageName === 'categories') {
            elements.categoriesTableBody = document.getElementById('categoriesTableBody');
            elements.addCategoryBtn = document.getElementById('addCategoryBtn');
            elements.emptyAddCategoryBtn = document.getElementById('emptyAddCategoryBtn');
            elements.categoryModal = document.getElementById('categoryModal');
            elements.categoryModalOverlay = elements.categoryModal?.querySelector('#modalOverlay'); // Scoped to category modal
            elements.closeCategoryModalBtn = elements.categoryModal?.querySelector('#closeModalBtn'); // Scoped
            elements.cancelCategoryBtn = document.getElementById('cancelCategoryBtn');
            elements.categoryForm = document.getElementById('categoryForm');
            elements.categoryModalTitle = elements.categoryModal?.querySelector('#modalTitle'); // Scoped
            elements.categoryIdInput = document.getElementById('categoryId');
            elements.categoryNameInput = document.getElementById('categoryName');
            elements.categoryIconInput = document.getElementById('categoryIcon');
            elements.categoryStatusSelect = document.getElementById('categoryStatus');
            elements.iconPreview = document.getElementById('iconPreview');
            elements.deleteCategoryConfirmModal = document.getElementById('deleteCategoryConfirmModal'); // Corrected ID
            elements.deleteCategoryModalOverlay = document.getElementById('deleteCategoryModalOverlay');
            elements.cancelDeleteCategoryBtn = document.getElementById('cancelDeleteCategoryBtn'); // Corrected ID
            elements.confirmDeleteCategoryBtn = document.getElementById('confirmDeleteCategoryBtn'); // Corrected ID
        } else if (pageName === 'dashboard') {
            elements.aiRequestTrendChart = document.getElementById('aiRequestTrendChart');
            elements.topModelsChart = document.getElementById('topModelsChart');
            elements.trendChartTimespanSelect = document.getElementById('trendChartTimespan');
        }
    }

    //=============================================================================
    // 2. UI COMPONENTS & UTILITIES
    //=============================================================================
    function showToast(message, type = 'info') {
        log('action', 'Toast', `Showing toast: ${message}, type: ${type}`);
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'fixed bottom-4 right-4 z-[10000]';
            document.body.appendChild(container);
            toastContainer = container;
        }
        const toast = document.createElement('div');
        toast.className = `flex items-center p-4 mb-3 rounded-lg shadow-lg max-w-xs animate-fade-in-toast`;
        let bgColor, textColor, iconClass;
        switch (type) {
            case 'success': bgColor = 'bg-green-100 dark:bg-green-900/30'; textColor = 'text-green-800 dark:text-green-300'; iconClass = 'fa-check-circle'; break;
            case 'error': bgColor = 'bg-red-100 dark:bg-red-900/30'; textColor = 'text-red-800 dark:text-red-300'; iconClass = 'fa-exclamation-circle'; break;
            case 'warning': bgColor = 'bg-yellow-100 dark:bg-yellow-900/30'; textColor = 'text-yellow-800 dark:text-yellow-300'; iconClass = 'fa-exclamation-triangle'; break;
            default: bgColor = 'bg-blue-100 dark:bg-blue-900/30'; textColor = 'text-blue-800 dark:text-blue-300'; iconClass = 'fa-info-circle';
        }
        toast.classList.add(...bgColor.split(' '), ...textColor.split(' '));
        toast.innerHTML = `<i class="fas ${iconClass} mr-3 text-lg"></i><div class="text-sm font-medium">${message}</div><button class="ml-auto text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"><i class="fas fa-times"></i></button>`;
        toastContainer.appendChild(toast);
        toast.querySelector('button').addEventListener('click', () => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        });
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    function showPageLoader() {
        // Create loader if it doesn't exist, useful for initial load before full caching
        if (!elements.pageLoader) {
            const loaderDiv = document.createElement('div');
            loaderDiv.className = 'page-loader-zk fixed inset-0 bg-black bg-opacity-50 z-[9999] flex items-center justify-center hidden'; // Start hidden
            loaderDiv.innerHTML = `<div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-lg flex items-center"><div class="loader-spinner-zk mr-3"></div><p class="text-gray-700 dark:text-gray-300">Yükleniyor...</p></div>`;
            document.body.appendChild(loaderDiv);
            elements.pageLoader = loaderDiv;
        }
        if (elements.pageLoader) {
            log('action', 'Loader', 'Showing page loader');
            elements.pageLoader.classList.remove('hidden');
            elements.pageLoader.style.display = 'flex';
        }
    }

    function hidePageLoader() {
        if (elements.pageLoader) {
            log('action', 'Loader', 'Hiding page loader');
            elements.pageLoader.style.display = 'none';
            elements.pageLoader.classList.add('hidden');
        }
    }

    function updateActiveMenuItem(pageName) {
        log('action', 'UI', `Updating active menu item for page: ${pageName}`);
        elements.navLinks.forEach(link => {
            link.classList.remove('active', 'bg-accent-light', 'text-accent', 'dark:bg-gray-700');
            link.classList.add('text-gray-600', 'dark:text-gray-300', 'hover:bg-gray-100', 'dark:hover:bg-gray-700');
            const icon = link.querySelector('i');
            if (icon) {
                icon.classList.remove('text-accent');
                icon.classList.add('text-gray-400');
            }
        });
        const activeLink = document.querySelector(`nav a.nav-link[href*="/admin/${pageName}"]`) ||
                           (pageName === 'dashboard' ? document.querySelector('nav a.nav-link[href="/admin/"]') : null) ||
                           (pageName === 'dashboard' ? document.querySelector('nav a.nav-link[href="/admin/dashboard"]') : null);

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
    function setupGlobalEventListeners() {
        log('info', 'Events', 'Setting up global event listeners.');
        if (elements.themeToggle) elements.themeToggle.addEventListener('click', handleThemeToggle);
        if (elements.sidebarToggle) elements.sidebarToggle.addEventListener('click', handleSidebarToggle);
        window.addEventListener('resize', handleWindowResize);
        // Nav links will now perform default navigation, so no global click handler for AJAX.
    }

    function setupPageSpecificEventListeners(pageName) {
        log('info', 'Events', `Setting up listeners for page: ${pageName}`);
        cachePageSpecificDOMElements(pageName); // Cache elements for the current page

        if (pageName === 'models') {
            if (elements.addModelBtn) elements.addModelBtn.addEventListener('click', () => openModelModal(false));
            if (elements.emptyAddModelBtn) elements.emptyAddModelBtn.addEventListener('click', () => openModelModal(false));
            if (elements.categoryFilter) elements.categoryFilter.addEventListener('change', applyModelFilters);
            if (elements.providerFilter) elements.providerFilter.addEventListener('change', applyModelFilters);
            if (elements.statusFilter) elements.statusFilter.addEventListener('change', applyModelFilters);
            if (elements.modelForm) elements.modelForm.addEventListener('submit', handleModelFormSubmit);
            if (elements.closeModelModalBtn) elements.closeModelModalBtn.addEventListener('click', closeModelModal);
            if (elements.cancelModelBtn) elements.cancelModelBtn.addEventListener('click', closeModelModal);
            if (elements.modelModalOverlay) elements.modelModalOverlay.addEventListener('click', closeModelModal);
            if (elements.confirmDeleteModelBtn) elements.confirmDeleteModelBtn.addEventListener('click', () => handleDeleteConfirm('model'));
            if (elements.cancelDeleteModelBtn) elements.cancelDeleteModelBtn.addEventListener('click', () => closeDeleteConfirmModal('model'));
            if (elements.deleteModelModalOverlay) elements.deleteModelModalOverlay.addEventListener('click', () => closeDeleteConfirmModal('model'));
            rebindAllModelCardListeners();
        } else if (pageName === 'categories') {
            if (elements.addCategoryBtn) elements.addCategoryBtn.addEventListener('click', () => openCategoryModal(false));
            if (elements.emptyAddCategoryBtn) elements.emptyAddCategoryBtn.addEventListener('click', () => openCategoryModal(false));
            if (elements.categoryForm) elements.categoryForm.addEventListener('submit', handleCategoryFormSubmit);
            if (elements.closeCategoryModalBtn) elements.closeCategoryModalBtn.addEventListener('click', closeCategoryModal);
            if (elements.cancelCategoryBtn) elements.cancelCategoryBtn.addEventListener('click', closeCategoryModal);
            if (elements.categoryModalOverlay) elements.categoryModalOverlay.addEventListener('click', closeCategoryModal);
            if (elements.categoryIconInput) elements.categoryIconInput.addEventListener('input', updateCategoryIconPreview);
            if (elements.confirmDeleteCategoryBtn) elements.confirmDeleteCategoryBtn.addEventListener('click', () => handleDeleteConfirm('category'));
            if (elements.cancelDeleteCategoryBtn) elements.cancelDeleteCategoryBtn.addEventListener('click', () => closeDeleteConfirmModal('category'));
            // Event delegation for category table buttons
            if (elements.categoriesTableBody) {
                elements.categoriesTableBody.addEventListener('click', (e) => {
                    const editBtn = e.target.closest('.edit-category-btn');
                    const deleteBtn = e.target.closest('.delete-category-btn');
                    if (editBtn) handleEditCategoryClick(editBtn.dataset.categoryId);
                    if (deleteBtn) showDeleteConfirmModal('category', deleteBtn.dataset.categoryId);
                });
            }
        } else if (pageName === 'dashboard') {
            if (elements.trendChartTimespanSelect) elements.trendChartTimespanSelect.addEventListener('change', handleTrendChartTimespanChange);
            initializeCharts();
        }
    }

    function setupModelCardEventListeners(cardElement) {
        const modelId = cardElement.dataset.modelId;
        if (!modelId) return;
        const editBtn = cardElement.querySelector(`.edit-model-btn[data-model-id="${modelId}"]`);
        const deleteBtn = cardElement.querySelector(`.delete-model-btn[data-model-id="${modelId}"]`);
        // const detailsBtn = cardElement.querySelector(`.details-model-btn[data-model-id="${modelId}"]`); // If needed

        if (editBtn) {
            editBtn.addEventListener('click', async function() {
                log('action', 'ModelCard', `Edit button clicked for model: ${modelId}`);
                showPageLoader();
                try {
                    const response = await fetch(`/admin/api/models/${modelId}`); // Assumes API endpoint exists
                    if (!response.ok) throw new Error(`Model verileri alınamadı: ${response.status}`);
                    const data = await response.json();
                    if (data.model) openModelModal(true, data.model);
                    else throw new Error('Model verisi eksik.');
                } catch (error) {
                    log('error', 'ModelCard', `Edit error: ${error.message}`);
                    showToast(error.message, 'error');
                } finally {
                    hidePageLoader();
                }
            });
        }
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                log('action', 'ModelCard', `Delete button clicked for model: ${modelId}`);
                showDeleteConfirmModal('model', modelId);
            });
        }
    }

    function rebindAllModelCardListeners() {
        if (elements.modelsContainer) {
            const cards = elements.modelsContainer.querySelectorAll('.kpi-card[data-model-id]');
            cards.forEach(card => setupModelCardEventListeners(card));
        }
    }

    //=============================================================================
    // 5. OPERATIONS & LOGIC
    //=============================================================================

    // 5.1. Theme Management
    function applyTheme(theme) {
        log('action', 'Theme', `Applying theme: ${theme}`);
        if (!elements.htmlElement || !elements.themeIcon) {
            cacheCommonDOMElements();
            if (!elements.htmlElement || !elements.themeIcon) {
                log('error', 'Theme', 'Critical theme elements still not found.'); return;
            }
        }
        if (theme === 'dark') {
            elements.htmlElement.classList.add('dark');
            elements.themeIcon.classList.replace('fa-moon', 'fa-sun');
        } else {
            elements.htmlElement.classList.remove('dark');
            elements.themeIcon.classList.replace('fa-sun', 'fa-moon');
        }
        state.currentTheme = theme;
        localStorage.setItem('theme', theme);
        if (state.currentPage === 'dashboard' && (state.charts.aiRequestTrendChartInstance || state.charts.topModelsChartInstance)) {
            log('info', 'Theme', 'Theme changed, re-initializing charts.');
            destroyCharts();
            initializeCharts();
        }
    }
    function handleThemeToggle() { applyTheme(elements.htmlElement.classList.contains('dark') ? 'light' : 'dark'); }

    // 5.2. Sidebar Management
    function setSidebarState(collapsed) {
        if (!elements.sidebar || !elements.mainContent) return;
        elements.sidebar.classList.toggle('collapsed', collapsed);
        elements.mainContent.style.marginLeft = collapsed ? '80px' : '250px';
        state.sidebarCollapsed = collapsed;
        localStorage.setItem('sidebarCollapsed', collapsed);
        log('action', 'Sidebar', `Sidebar state set to: ${collapsed ? 'collapsed' : 'expanded'}`);
    }
    function handleSidebarToggle() { setSidebarState(!elements.sidebar.classList.contains('collapsed'));}
    function handleWindowResize() {
        const isMobileView = window.innerWidth < 1024;
        if (isMobileView && !state.sidebarCollapsed) setSidebarState(true);
        else if (!isMobileView && elements.sidebar && elements.mainContent) { // Ensure elements exist
             // Restore user preference on larger screens if it was collapsed due to mobile view
            const lastKnownCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            if (state.sidebarCollapsed && !lastKnownCollapsed) { // If currently collapsed but shouldn't be
                 // setSidebarState(false); // Or let manual toggle handle it
            }
            // Ensure correct margin on resize
            elements.mainContent.style.marginLeft = elements.sidebar.classList.contains('collapsed') ? '80px' : '250px';
        }
    }

    // 5.3. Model Filtering (No AJAX)
    function applyModelFilters() {
        log('action', 'Filter', 'Applying model filters.');
        if (!elements.modelsContainer) return;
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
                card.style.display = ''; visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        // Handle "no results" message (implementation can be similar to previous AJAX version)
        let noResultsElement = elements.modelsContainer.querySelector('#noFilterResultsMessage');
        if (visibleCount === 0 && modelCards.length > 0) {
            if (!noResultsElement) {
                noResultsElement = document.createElement('div');
                noResultsElement.id = 'noFilterResultsMessage';
                noResultsElement.className = 'col-span-1 md:col-span-2 lg:col-span-3 py-12 flex flex-col items-center justify-center text-center';
                noResultsElement.innerHTML = `<div class="bg-accent-light text-accent p-4 rounded-full mb-4"><i class="fas fa-filter text-3xl"></i></div><h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">Sonuç Bulunamadı</h3><p class="text-gray-600 dark:text-gray-300 max-w-md mb-6">Seçtiğiniz filtrelere uygun model bulunamadı.</p>`;
                elements.modelsContainer.appendChild(noResultsElement);
            }
            noResultsElement.style.display = 'flex';
        } else if (noResultsElement) {
            noResultsElement.style.display = 'none';
        }
        log('info', 'Filter', `Filtering complete. Visible models: ${visibleCount}`);
    }

    // 5.4. Model Modal Operations
    function openModelModal(isEdit = false, modelData = null) {
        log('action', 'Modal', `Opening model modal. Edit: ${isEdit}`, modelData);
        if (!elements.modelModal || !elements.modelModalTitle || !elements.modelForm) {
            log('error', 'Modal', 'Model modal elements not found.'); return;
        }
        elements.modelModalTitle.textContent = isEdit ? 'Modeli Düzenle' : 'Yeni Model Ekle';
        elements.modelForm.reset();
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
        } else {
            document.getElementById('modelId').value = '';
            document.getElementById('modelStatus').value = 'inactive';
            document.getElementById('modelRequestMethod').value = 'POST';
        }
        elements.modelModal.classList.remove('hidden');
    }
    function closeModelModal() {
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
        const isEdit = !!modelId;
        const modelData = {};
        formData.forEach((value, key) => {
            if (key === 'modelId') return;
            const apiFieldKey = key.startsWith('model') ? key.substring(5).charAt(0).toLowerCase() + key.substring(6) : key;
            if (apiFieldKey === 'category_id') modelData[apiFieldKey] = value ? parseInt(value) : null;
            else modelData[apiFieldKey] = value;
        });
        if (modelData.hasOwnProperty('Name') && !modelData.hasOwnProperty('name')) { modelData.name = modelData.Name; delete modelData.Name; }


        const url = isEdit ? `/admin/api/models/${modelId}` : '/admin/api/models';
        const method = isEdit ? 'PUT' : 'POST';
        const submitBtn = elements.modelForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Kaydediliyor...';
        showPageLoader();
        try {
            const response = await fetch(url, {
                method: method, headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(modelData)
            });
            const responseData = await response.json();
            if (!response.ok) throw new Error(responseData.message || responseData.error || `Bir hata oluştu: ${response.status}`);
            showToast(responseData.message || (isEdit ? 'Model başarıyla güncellendi.' : 'Yeni model başarıyla eklendi.'), 'success');
            closeModelModal();
            window.location.reload(); // Reload page to see changes
        } catch (error) {
            log('error', 'FormSubmit', `Error submitting model form: ${error.message}`, error);
            showToast(error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            hidePageLoader();
        }
    }

    // 5.5. Category Modal Operations (Integrated from admin_categories.js)
    function openCategoryModal(isEdit = false, categoryData = null) {
        log('action', 'Modal', `Opening category modal. Edit: ${isEdit}`, categoryData);
        if (!elements.categoryModal || !elements.categoryModalTitle || !elements.categoryForm) {
            log('error', 'Modal', 'Category modal elements not found.'); return;
        }
        elements.categoryModalTitle.textContent = isEdit ? 'Kategori Düzenle' : 'Yeni Kategori Ekle';
        elements.categoryForm.reset();
        elements.categoryIdInput.value = ''; // Clear hidden ID field

        if (isEdit && categoryData) {
            elements.categoryIdInput.value = categoryData.id || '';
            elements.categoryNameInput.value = categoryData.name || '';
            elements.categoryIconInput.value = categoryData.icon || '';
            // Assuming 'status' is part of categoryData from API for edit
            elements.categoryStatusSelect.value = categoryData.status || 'active';
        } else {
            elements.categoryStatusSelect.value = 'active'; // Default for new
        }
        updateCategoryIconPreview();
        elements.categoryModal.classList.remove('hidden');
    }
    function closeCategoryModal() {
        if (elements.categoryModal && elements.categoryForm) {
            elements.categoryModal.classList.add('hidden');
            elements.categoryForm.reset();
        }
    }
    async function handleCategoryFormSubmit(event) {
        event.preventDefault();
        log('action', 'Form', 'Category form submitted.');
        const categoryId = elements.categoryIdInput.value;
        const isEdit = !!categoryId;
        const formData = {
            name: elements.categoryNameInput.value.trim(),
            icon: elements.categoryIconInput.value.trim(),
            status: elements.categoryStatusSelect.value // Assuming 'status' is part of the form
        };

        const url = isEdit ? `/admin/api/categories/${categoryId}` : '/admin/api/categories';
        const method = isEdit ? 'PUT' : 'POST';
        const submitBtn = elements.categoryForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Kaydediliyor...';
        showPageLoader();
        try {
            // For PUT, ensure description is handled if your API expects it or not
            const payload = { name: formData.name, description: "" }; // Add description if needed by API
            if (formData.icon) payload.icon = formData.icon;
            // if (formData.status) payload.status = formData.status; // Add status if API handles it

            const response = await fetch(url, {
                method: method, headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload) // Send only name and description for PUT as per original API
            });
            const responseData = await response.json();
            if (!response.ok) throw new Error(responseData.message || responseData.error || `Bir hata oluştu: ${response.status}`);
            showToast(responseData.message || (isEdit ? 'Kategori başarıyla güncellendi.' : 'Kategori başarıyla eklendi.'), 'success');
            closeCategoryModal();
            window.location.reload(); // Reload page
        } catch (error) {
            log('error', 'FormSubmit', `Error submitting category form: ${error.message}`, error);
            showToast(error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            hidePageLoader();
        }
    }
    async function handleEditCategoryClick(categoryId) {
        log('action', 'Category', `Edit category click for ID: ${categoryId}`);
        showPageLoader();
        try {
            // This GET request needs to be implemented in admin_routes.py
            const response = await fetch(`/admin/api/categories/${categoryId}`);
            if (!response.ok) throw new Error(`Kategori verileri alınamadı: ${response.status}`);
            const data = await response.json();
            if (data.success && data.category) {
                openCategoryModal(true, data.category);
            } else {
                throw new Error(data.message || 'Kategori verisi alınamadı.');
            }
        } catch (error) {
            log('error', 'Category', `Error fetching category for edit: ${error.message}`);
            showToast(error.message, 'error');
        } finally {
            hidePageLoader();
        }
    }
    function updateCategoryIconPreview() {
        if (elements.iconPreview && elements.categoryIconInput) {
            const iconClasses = elements.categoryIconInput.value.trim() || 'fas fa-folder';
            elements.iconPreview.className = iconClasses + ' text-gray-400'; // Ensure base styling
        }
    }


    // 5.6. Generic Delete Operations
    function showDeleteConfirmModal(type, id) { // type can be 'model' or 'category'
        log('action', 'Modal', `Showing delete confirm modal for ${type} ID: ${id}`);
        state.itemToDelete = { id, type };
        const modal = (type === 'model') ? elements.deleteModelConfirmModal : elements.deleteCategoryConfirmModal;
        if (modal) modal.classList.remove('hidden');
        else log('error', 'Modal', `Delete confirm modal for ${type} not found.`);
    }

    function closeDeleteConfirmModal(type) {
        const modal = (type === 'model') ? elements.deleteModelConfirmModal : elements.deleteCategoryConfirmModal;
        if (modal) modal.classList.add('hidden');
        state.itemToDelete = { id: null, type: null };
    }

    async function handleDeleteConfirm(typeFromButton) { // typeFromButton is 'model' or 'category'
        const { id, type } = state.itemToDelete;
        if (!id || !type || type !== typeFromButton) {
            log('warn', 'Delete', 'No item ID/type set for deletion or type mismatch.');
            closeDeleteConfirmModal(typeFromButton); // Close the correct modal
            return;
        }
        log('action', 'Delete', `Confirming deletion for ${type}: ${id}`);

        const confirmBtn = (type === 'model') ? elements.confirmDeleteModelBtn : elements.confirmDeleteCategoryBtn;
        if (!confirmBtn) {
            log('error', 'Delete', `Confirm delete button for ${type} not found.`);
            closeDeleteConfirmModal(type);
            return;
        }
        const originalBtnText = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Siliniyor...';
        showPageLoader();
        try {
            const url = (type === 'model') ? `/admin/api/models/${id}` : `/admin/api/categories/${id}`;
            const response = await fetch(url, { method: 'DELETE', headers: { 'Accept': 'application/json' } });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || data.error || `${type} silinemedi: ${response.status}`);
            showToast(data.message || `${type.charAt(0).toUpperCase() + type.slice(1)} başarıyla silindi.`, 'success');
            closeDeleteConfirmModal(type);
            window.location.reload(); // Reload page
        } catch (error) {
            log('error', 'Delete', `Error deleting ${type}: ${error.message}`, error);
            showToast(error.message, 'error');
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalBtnText;
            state.itemToDelete = { id: null, type: null };
            hidePageLoader();
        }
    }

    // 5.7. Chart Management (from original admin.js, largely unchanged)
    function getChartThemeColors() {
        const isDarkMode = elements.htmlElement ? elements.htmlElement.classList.contains('dark') : false;
        const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color')?.trim() || '#4A90E2';
        return {
            primary: accentColor, primaryTransparent: `${accentColor}33`,
            gridColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
            textColor: isDarkMode ? '#cbd5e1' : '#4b5563',
            tooltipBg: isDarkMode ? '#1f2937' : '#ffffff',
            doughnutBorder: isDarkMode ? '#374151' : '#ffffff'
        };
    }
    function loadAiRequestTrendChart() {
        if (!elements.aiRequestTrendChart || typeof Chart === 'undefined') return;
        if (state.charts.aiRequestTrendChartInstance) state.charts.aiRequestTrendChartInstance.destroy();
        const themeColors = getChartThemeColors();
        const days = elements.trendChartTimespanSelect ? parseInt(elements.trendChartTimespanSelect.value) : 30;
        const labels = Array.from({length: days}, (_, i) => `${i + 1}`);
        const data = Array.from({length: days}, () => Math.floor(Math.random() * 280) + 50);
        state.charts.aiRequestTrendChartInstance = new Chart(elements.aiRequestTrendChart, {
            type: 'line', data: { labels: labels, datasets: [{ label: 'AI İstekleri', data: data, borderColor: themeColors.primary, backgroundColor: themeColors.primaryTransparent, borderWidth: 2, pointBackgroundColor: themeColors.primary, pointBorderColor: themeColors.doughnutBorder, pointRadius: 0, pointHoverRadius: 5, tension: 0.3, fill: true }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { grid: { color: themeColors.gridColor, drawBorder: false }, ticks: { color: themeColors.textColor, font: {size: 10} } }, x: { grid: { display: false }, ticks: { color: themeColors.textColor, font: {size: 10} } } }, plugins: { legend: { display: false }, tooltip: { backgroundColor: themeColors.tooltipBg, titleColor: themeColors.textColor, bodyColor: themeColors.textColor, padding: 10, cornerRadius: 4, boxPadding: 3 } } }
        });
    }
    function loadTopModelsChart() {
        if (!elements.topModelsChart || typeof Chart === 'undefined') return;
        if (state.charts.topModelsChartInstance) state.charts.topModelsChartInstance.destroy();
        const themeColors = getChartThemeColors();
        const modelLabels = ['GPT-4 Turbo', 'Claude 3 Sonnet', 'Gemini Pro', 'Llama 3 70B', 'Diğer'];
        const modelData = [320, 210, 150, 100, 70];
        const backgroundColors = [themeColors.primary, '#60A5FA', '#34D399', '#FBBF24', '#F87171'].map(c => elements.htmlElement.classList.contains('dark') ? `${c}BF` : c);
        state.charts.topModelsChartInstance = new Chart(elements.topModelsChart, {
            type: 'doughnut', data: { labels: modelLabels, datasets: [{ data: modelData, backgroundColor: backgroundColors, borderColor: themeColors.doughnutBorder, borderWidth: 2, hoverOffset: 6 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: themeColors.textColor, usePointStyle: true, boxWidth: 10, padding: 15, font: {size: 11} } }, tooltip: { backgroundColor: themeColors.tooltipBg, titleColor: themeColors.textColor, bodyColor: themeColors.textColor, padding: 10, cornerRadius: 4, boxPadding: 3 } }, cutout: '65%' }
        });
    }
    function destroyCharts() {
        if (state.charts.aiRequestTrendChartInstance) { state.charts.aiRequestTrendChartInstance.destroy(); state.charts.aiRequestTrendChartInstance = null; }
        if (state.charts.topModelsChartInstance) { state.charts.topModelsChartInstance.destroy(); state.charts.topModelsChartInstance = null; }
    }
    function initializeCharts() { if (typeof Chart === 'undefined') { log('error', 'Charts', 'Chart.js not loaded.'); return; } loadAiRequestTrendChart(); loadTopModelsChart(); }
    function handleTrendChartTimespanChange(event) {
        if (state.charts.aiRequestTrendChartInstance) {
            const days = parseInt(event.target.value);
            state.charts.aiRequestTrendChartInstance.data.labels = Array.from({length: days}, (_, i) => `${i + 1}`);
            state.charts.aiRequestTrendChartInstance.data.datasets[0].data = Array.from({length: days}, () => Math.floor(Math.random() * 280) + 50);
            state.charts.aiRequestTrendChartInstance.update();
        }
    }

    //=============================================================================
    // 6. INITIALIZATION
    //=============================================================================
    function init() {
        log('info', 'Init', 'AdminPanelManager initializing (No AJAX Mode)...');
        showPageLoader(); // Show loader at the very beginning
        cacheCommonDOMElements();
        state.currentPage = getCurrentPageFromURL();

        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);
        const savedSidebarState = localStorage.getItem('sidebarCollapsed') === 'true';
        setSidebarState(savedSidebarState);
        handleWindowResize();

        setupGlobalEventListeners();
        updateActiveMenuItem(state.currentPage);
        setupPageSpecificEventListeners(state.currentPage); // Setup listeners for the initially loaded page

        const styleId = 'admin-panel-dynamic-styles';
        if (!document.getElementById(styleId)) {
            const styleElement = document.createElement('style');
            styleElement.id = styleId;
            styleElement.textContent = `@keyframes fadeInToast{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}.animate-fade-in-toast{animation:fadeInToast .3s ease-out forwards}.loader-spinner-zk{border:3px solid rgba(0,0,0,.1);border-radius:50%;border-top-color:var(--accent-color,#4A90E2);width:24px;height:24px;animation:spin-zk 1s linear infinite}@keyframes spin-zk{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}`;
            document.head.appendChild(styleElement);
        }
        log('info', 'Init', 'AdminPanelManager initialization complete.');
        // Hide loader after a short delay to ensure rendering is complete
        setTimeout(hidePageLoader, 250); // Adjust delay as needed
    }

    document.addEventListener('DOMContentLoaded', init);

    return {
        // Public API if needed, e.g., for debugging from console
        // showToast, openModelModal, openCategoryModal
    };
})();
