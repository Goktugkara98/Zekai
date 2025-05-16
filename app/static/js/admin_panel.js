/**
 * Admin Paneli Yönetim Modülü (Yeniden Düzenlenmiş)
 * =================================================
 * @description Model, kategori, kullanıcı ve mesaj yönetim arayüzü ve etkileşimlerini yönetir.
 * @version 1.1.0
 * @author Proje Geliştiricisi (Yeniden Düzenleyen: Gemini AI)
 *
 * İÇİNDEKİLER
 * ===============
 * 1.  AdminPanel Ana Namespace
 * 
 * 2.  LOGGER MODÜLÜ (AdminPanel.Logger)
 *      2.1. Log Seviyeleri (logLevels)
 *      2.2. Mevcut Log Seviyesi (currentLogLevel)
 *      2.3. Log Seviyesini Ayarla (setLevel)
 *      2.4. Ana Log Fonksiyonu (log)
 *      2.5. Yardımcı Log Fonksiyonları (debug, info, warn, error)
 * 3.  DOM MODÜLÜ (AdminPanel.DOM)
 *      3.1. DOM Element Referansları
 * 4.  STATE MODÜLÜ (AdminPanel.State)
 *      4.1. Uygulama Durumu (models, categories, userMessages)
 * 5.  API SERVİS MODÜLÜ (AdminPanel.ApiService)
 *      5.1. Temel Fetch Fonksiyonu (_fetch)
 *      5.2. Model API Fonksiyonları (getModels, addModel, updateModel, deleteModel)
 *      5.3. Kategori API Fonksiyonları (getCategories, addCategory, updateCategory, deleteCategory)
 *      5.4. Kullanıcı Mesajları API Fonksiyonları (getUserMessages, deleteUserMessage)
 * 6.  UI YÖNETİCİ MODÜLÜ (AdminPanel.UIManager)
 *      6.1. Bölüm Gösterimi (showSection)
 *      6.2. Veri Oluşturucular (Renderers)
 *          6.2.1. Modelleri Oluştur (renderModels)
 *          6.2.2. Kategorileri Oluştur (renderCategories)
 *          6.2.3. Kullanıcı Mesajlarını Oluştur (renderUserMessages)
 *      6.3. Form Doldurucular (Form Populators)
 *          6.3.1. Model Düzenleme Formunu Doldur (populateEditModelForm)
 *          6.3.2. Kategori Düzenleme Formunu Doldur (populateEditCategoryForm)
 *      6.4. Olay Dinleyici Ekleyicileri (Event Listener Attachments for UI elements)
 *          6.4.1. Model Aksiyon Dinleyicileri (attachModelActionListeners)
 *          6.4.2. Kategori Aksiyon Dinleyicileri (attachCategoryActionListeners)
 *          6.4.3. Mesaj Aksiyon Dinleyicileri (attachMessageActionListeners)
 *      6.5. Geri Bildirim (showToast)
 * 7.  VERİ YÜKLEYİCİ MODÜLÜ (AdminPanel.DataLoaders)
 *      7.1. Modelleri Yükle (loadModels)
 *      7.2. Kategorileri Yükle (loadCategories)
 *      7.3. Model Formları İçin Kategorileri Yükle (loadCategoriesForModelForms)
 *      7.4. Kullanıcı Mesajlarını Yükle (loadUserMessages)
 *      7.5. Dashboard Verilerini Yükle (loadDashboardData)
 * 8.  OLAY İŞLEYİCİ MODÜLÜ (AdminPanel.EventHandlers)
 *      8.1. Navigasyon Tıklamaları (handleNavClick)
 *      8.2. Dashboard İstatistiklerini Güncelle (updateDashboardStats)
 *      8.3. Model İşlemleri (handleAddModel, handleEditModelShow, handleUpdateModel, handleDeleteModel)
 *      8.4. Kategori İşlemleri (handleAddCategory, handleEditCategoryShow, handleUpdateCategory, handleDeleteCategory)
 *      8.5. Mesaj İşlemleri (handleDeleteMessage)
 * 9.  UYGULAMA BAŞLATMA MODÜLÜ (AdminPanel.App)
 *      9.1. Olay Dinleyicilerini Kur (setupEventListeners)
 *      9.2. Başlatma Fonksiyonu (init)
 * 10. DOM HAZIR OLDUĞUNDA BAŞLATMA
 */

//=============================================================================
// 1. AdminPanel Ana Namespace
//=============================================================================
const AdminPanel = {};

//=============================================================================
// 2. LOGGER MODÜLÜ (AdminPanel.Logger)
//=============================================================================
AdminPanel.Logger = (function () {
    const MODULE_NAME = 'Logger';
    const logLevels = {
        DEBUG: 0,
        INFO: 1,
        WARN: 2,
        ERROR: 3,
        NONE: 4,
    };

    let currentLogLevel = logLevels.DEBUG; // Varsayılan olarak tüm logları göster

    function setLevel(levelName) {
        const level = logLevels[levelName.toUpperCase()];
        if (typeof level !== 'undefined') {
            currentLogLevel = level;
            console.log(`[${MODULE_NAME}] Log level set to ${levelName.toUpperCase()}`);
        } else {
            console.warn(`[${MODULE_NAME}] Invalid log level: ${levelName}`);
        }
    }

    function _log(level, sourceModule, message, ...args) {
        if (level < currentLogLevel) {
            return;
        }

        const timestamp = new Date().toISOString();
        let levelStr = 'LOG';
        let consoleMethod = console.log;

        switch (level) {
            case logLevels.DEBUG:
                levelStr = 'DEBUG';
                consoleMethod = console.debug || console.log;
                break;
            case logLevels.INFO:
                levelStr = 'INFO';
                consoleMethod = console.info;
                break;
            case logLevels.WARN:
                levelStr = 'WARN';
                consoleMethod = console.warn;
                break;
            case logLevels.ERROR:
                levelStr = 'ERROR';
                consoleMethod = console.error;
                break;
        }

        const prefix = `[${timestamp}] [${levelStr}] [${sourceModule}]`;
        if (args.length > 0) {
            consoleMethod(prefix, message, ...args);
        } else {
            consoleMethod(prefix, message);
        }
    }

    return {
        levels: logLevels,
        setLevel,
        debug: (module, msg, ...args) => _log(logLevels.DEBUG, module, msg, ...args),
        info: (module, msg, ...args) => _log(logLevels.INFO, module, msg, ...args),
        warn: (module, msg, ...args) => _log(logLevels.WARN, module, msg, ...args),
        error: (module, msg, ...args) => _log(logLevels.ERROR, module, msg, ...args),
    };
})();

//=============================================================================
// 3. DOM MODÜLÜ (AdminPanel.DOM)
//=============================================================================
AdminPanel.DOM = {
    navLinks: {
        dashboard: document.getElementById('nav-dashboard'), // Dashboard linki eklendi varsayımı
        models: document.getElementById('nav-models'),
        categories: document.getElementById('nav-categories'),
        users: document.getElementById('nav-users'),
        settings: document.getElementById('nav-settings'),
        messages: document.getElementById('nav-messages'),
    },
    contentSections: {
        dashboard: document.getElementById('dashboard-section'), // Dashboard bölümü eklendi varsayımı
        models: document.getElementById('models-section'),
        categories: document.getElementById('categories-section'),
        users: document.getElementById('users-section'),
        settings: document.getElementById('settings-section'),
        messages: document.getElementById('messages-section'),
    },
    modelsTableBody: document.querySelector('#models-section table tbody'),
    addModelForm: document.getElementById('addModelForm'),
    modelCategorySelect: document.getElementById('modelCategory'),
    editModelModal: document.getElementById('editModelModal'),
    editModelForm: document.getElementById('editModelForm'),
    editModelCategorySelect: document.getElementById('editModelCategory'),
    categoriesTableBody: document.getElementById('categoriesTableBody'),
    addCategoryForm: document.getElementById('addCategoryForm'),
    editCategoryModal: document.getElementById('editCategoryModal'),
    editCategoryForm: document.getElementById('editCategoryForm'),
    messagesTableBody: document.querySelector('#messages-section table tbody'),
    toastContainer: null, // Dinamik olarak oluşturulacak
    // Dashboard istatistik elementleri
    dashboardCategoryCount: document.getElementById('categoryCount'),
    dashboardModelCount: document.getElementById('modelCount'),
    dashboardMessageCount: document.getElementById('messageCount'), // Mesaj sayısı için eklendi varsayımı
};

//=============================================================================
// 4. STATE MODÜLÜ (AdminPanel.State)
//=============================================================================
AdminPanel.State = {
    models: [],
    categories: [],
    userMessages: [],
};

//=============================================================================
// 5. API SERVİS MODÜLÜ (AdminPanel.ApiService)
//=============================================================================
AdminPanel.ApiService = (function (Logger) {
    const MODULE_NAME = 'ApiService';

    async function _fetch(url, options = {}) {
        Logger.debug(MODULE_NAME, `Requesting: ${options.method || 'GET'} ${url}`, options.body ? JSON.parse(options.body) : '');
        try {
            const response = await fetch(url, options);
            const responseData = await response.json().catch(() => null); // JSON parse hatasını yakala

            if (!response.ok) {
                const errorMessage = responseData?.message || responseData?.error || `HTTP error! status: ${response.status}`;
                Logger.error(MODULE_NAME, `API Error on ${url}: ${errorMessage}`, responseData);
                throw new Error(errorMessage);
            }
            Logger.debug(MODULE_NAME, `Response from ${url}:`, responseData);
            return responseData;
        } catch (error) {
            Logger.error(MODULE_NAME, `Network or parsing error on ${url}: ${error.message}`, error);
            // UI Manager'ın varlığını kontrol etmeden doğrudan toast gösterme, bu servisin UI'dan bağımsız olmasını sağlar.
            // Hata yukarı fırlatılacak ve UI katmanı bunu ele alacaktır.
            throw error;
        }
    }

    return {
        getModels: function () {
            return _fetch('/admin/api/models').then(response => {
                if (response && response.success && Array.isArray(response.models)) {
                    return response.models;
                }
                Logger.warn(MODULE_NAME, 'getModels: Invalid model data received.', response);
                return [];
            });
        },
        addModel: function (data) {
            return _fetch('/admin/api/models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        updateModel: function (id, data) {
            return _fetch(`/admin/api/models/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        deleteModel: function (id) {
            return _fetch(`/admin/api/models/${id}`, { method: 'DELETE' });
        },
        getCategories: function () {
            return _fetch('/admin/api/categories').then(response => {
                if (response && response.success && Array.isArray(response.categories)) {
                    return response.categories;
                }
                Logger.warn(MODULE_NAME, 'getCategories: Invalid category data received.', response);
                return [];
            });
        },
        addCategory: function (data) {
            return _fetch('/admin/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        updateCategory: function (id, data) {
            return _fetch(`/admin/api/categories/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        deleteCategory: function (id) {
            return _fetch(`/admin/api/categories/${id}`, { method: 'DELETE' });
        },
        getUserMessages: function (page = 1, perPage = 25) {
            return _fetch(`/admin/api/user_messages?page=${page}&per_page=${perPage}`)
                .then(response => {
                    if (response && response.success && Array.isArray(response.messages)) {
                        // API'den gelen yanıtı doğrudan döndürüyoruz
                        // çünkü sayfalama bilgilerini de içeriyor
                        return response;
                    }
                    Logger.warn(MODULE_NAME, 'getUserMessages: Invalid messages data received.', response);
                    return { messages: [], total: 0, page: 1, per_page: perPage, total_pages: 0 };
                })
                .catch(error => {
                    Logger.error(MODULE_NAME, 'Error fetching user messages:', error);
                    return { messages: [], total: 0, page: 1, per_page: perPage, total_pages: 0 };
                });
        },
        deleteUserMessage: function (id) {
            return _fetch(`/admin/api/user_messages/${id}`, { method: 'DELETE' });
        }
    };
})(AdminPanel.Logger);

//=============================================================================
// 6. UI YÖNETİCİ MODÜLÜ (AdminPanel.UIManager)
//=============================================================================
AdminPanel.UIManager = (function (DOM, Logger, State, EventHandlers) { // EventHandlers'ı buraya enjekte etmeyebiliriz, App modülü bağlayabilir.
    const MODULE_NAME = 'UIManager';

    function showSection(sectionId) {
        Logger.debug(MODULE_NAME, `Showing section: ${sectionId}`);
        Object.values(DOM.contentSections).forEach(section => {
            if (section) section.style.display = 'none';
        });
        if (DOM.contentSections[sectionId]) {
            DOM.contentSections[sectionId].style.display = 'block';
        } else {
            Logger.warn(MODULE_NAME, `Section with ID '${sectionId}' not found in DOM.contentSections.`);
        }

        Object.values(DOM.navLinks).forEach(link => {
            if (link) link.classList.remove('active');
        });
        if (DOM.navLinks[sectionId]) {
            DOM.navLinks[sectionId].classList.add('active');
        } else {
            Logger.warn(MODULE_NAME, `Nav link for section '${sectionId}' not found in DOM.navLinks.`);
        }
    }

    function renderModels(models) {
        Logger.debug(MODULE_NAME, 'Rendering models. Count:', models.length, models);
        if (!DOM.modelsTableBody) {
            Logger.error(MODULE_NAME, 'Models table body (DOM.modelsTableBody) not found.');
            return;
        }
        DOM.modelsTableBody.innerHTML = '';
        if (!Array.isArray(models) || models.length === 0) {
            const message = Array.isArray(models) ? 'Henüz model bulunmamaktadır' : 'Modeller yüklenirken bir hata oluştu veya veri formatı geçersiz.';
            Logger.info(MODULE_NAME, message, models);
            const row = DOM.modelsTableBody.insertRow();
            row.innerHTML = `<td colspan="7" class="text-center">${message}</td>`;
            return;
        }
        models.forEach(model => {
            const row = DOM.modelsTableBody.insertRow();
            row.innerHTML = `
                <td>${model.id || 'N/A'}</td>
                <td>${model.name || 'İsimsiz'}</td>
                <td>${model.api_key ? '*****' : 'N/A'}</td>
                <td>${model.base_url || 'N/A'}</td>
                <td>${model.description || ''}</td>
                <td>${model.category_name || model.category_id || 'Kategorisiz'}</td>
                <td>
                    <button class="btn btn-sm btn-primary btn-edit-model" data-id="${model.id}">Düzenle</button>
                    <button class="btn btn-sm btn-danger btn-delete-model" data-id="${model.id}">Sil</button>
                </td>
            `;
        });
        attachModelActionListeners();
    }

    function renderCategories(categories) {
        Logger.debug(MODULE_NAME, 'Rendering categories. Count:', categories.length, categories);
        if (!DOM.categoriesTableBody) {
            Logger.error(MODULE_NAME, 'Categories table body (DOM.categoriesTableBody) not found.');
            return;
        }
        DOM.categoriesTableBody.innerHTML = '';
        if (!Array.isArray(categories) || categories.length === 0) {
            const message = Array.isArray(categories) ? 'Henüz kategori bulunmamaktadır' : 'Kategoriler yüklenirken bir hata oluştu veya veri formatı geçersiz.';
            Logger.info(MODULE_NAME, message, categories);
            const row = DOM.categoriesTableBody.insertRow();
            row.innerHTML = `<td colspan="5" class="text-center">${message}</td>`;
            return;
        }
        categories.forEach(category => {
            const row = DOM.categoriesTableBody.insertRow();
            row.innerHTML = `
                <td>${category.id || 'N/A'}</td>
                <td><i class="bi ${category.icon || 'bi-folder'}"></i></td>
                <td>
                    <strong>${category.name || 'İsimsiz Kategori'}</strong>
                    ${category.description ? `<div class="text-muted small">${category.description}</div>` : ''}
                </td>
                <td>${category.model_count || 0}</td>
                <td>
                    <button class="btn btn-sm btn-primary btn-edit-category" data-id="${category.id}">
                        <i class="bi bi-pencil"></i> Düzenle
                    </button>
                    <button class="btn btn-sm btn-danger btn-delete-category" data-id="${category.id}">
                        <i class="bi bi-trash"></i> Sil
                    </button>
                </td>
            `;
        });
        attachCategoryActionListeners();
    }

    function renderUserMessages(data) {
        const $container = document.getElementById('user-messages-container');
        const $pagination = document.getElementById('messages-pagination');
        
        if (!$container) {
            // If the container isn't found, it might be because the messages section isn't active yet
            // Log a debug message instead of an error, as this can happen during initial load
            Logger.debug(MODULE_NAME, 'User messages container not found - messages section may not be active');
            return;
        }
        
        // Clear previous content
        $container.innerHTML = '';
        if ($pagination) $pagination.innerHTML = '';
        
        // Check if data is valid
        if (!data || !data.messages || !Array.isArray(data.messages)) {
            Logger.error(MODULE_NAME, 'Invalid messages data received', data);
            $container.innerHTML = `
                <div class="alert alert-warning">
                    Mesajlar yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.
                </div>
            `;
            return;
        }
        
        // Set default values for pagination if not provided
        const messages = data.messages || [];
        const total = data.total || messages.length;
        const page = data.page || 1;
        const perPage = data.per_page || data.perPage || 25;
        const totalPages = data.total_pages || data.totalPages || Math.ceil(total / perPage);
        
        Logger.debug(MODULE_NAME, 'Rendering messages with pagination:', { 
            currentPage: page, 
            perPage: perPage, 
            total: total, 
            totalPages: totalPages,
            messageCount: messages.length 
        });
        
        // If no messages
        if (messages.length === 0) {
            $container.innerHTML = `
                <div class="alert alert-info">
                    Henüz mesaj bulunmamaktadır.
                </div>
            `;
            return;
        }
        
        // Build the messages table
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Kullanıcı</th>
                            <th>Mesaj</th>
                            <th>Model</th>
                            <th>Tarih</th>
                            <th class="text-end">İşlemler</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        // Add each message as a row
        messages.forEach(msg => {
            const date = msg.created_at ? new Date(msg.created_at) : new Date();
            const formattedDate = date.toLocaleString('tr-TR');
            const userInfo = msg.user_id ? `ID: ${msg.user_id}` : 'Misafir';
            const messagePreview = msg.user_message ? 
                (msg.user_message.length > 30 ? msg.user_message.substring(0, 30) + '...' : msg.user_message) : 
                'Mesaj yok';
            
            // Format date string (remove milliseconds)
            const formattedDateStr = formattedDate.split('.')[0];
            
            html += `
                <tr data-id="${msg.id || ''}">
                    <td class="align-middle">${msg.id || '-'}</td>
                    <td class="align-middle">${userInfo}</td>
                    <td class="align-middle">${messagePreview}</td>
                    <td class="align-middle">${msg.ai_model_name || 'Bilinmiyor'}</td>
                    <td class="align-middle">${formattedDateStr}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary view-message me-1" 
                                data-id="${msg.id}" 
                                title="Mesaj Detayı">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-message" 
                                data-id="${msg.id}" 
                                title="Mesajı Sil">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        // Close table
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        // Add pagination if there are multiple pages
        if (totalPages > 1 && $pagination) {
            let paginationHtml = `
                <nav aria-label="Mesaj sayfaları">
                    <ul class="pagination justify-content-center mt-4">
            `;
            
            // Previous button
            const prevDisabled = page <= 1 ? 'disabled' : '';
            paginationHtml += `
                <li class="page-item ${prevDisabled}">
                    <a class="page-link" href="#" data-page="${page - 1}" 
                       ${prevDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                        &laquo; Önceki
                    </a>
                </li>
            `;
            
            // Page numbers
            const maxPagesToShow = 5;
            let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
            let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
            
            if (endPage - startPage + 1 < maxPagesToShow) {
                startPage = Math.max(1, endPage - maxPagesToShow + 1);
            }
            
            if (startPage > 1) {
                paginationHtml += `
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="1">1</a>
                    </li>
                `;
                if (startPage > 2) {
                    paginationHtml += '<li class="page-item disabled"><span class="page-link">...</span></li>';
                }
            }
            
            for (let i = startPage; i <= endPage; i++) {
                const active = i === page ? 'active' : '';
                paginationHtml += `
                    <li class="page-item ${active}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            }
            
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    paginationHtml += '<li class="page-item disabled"><span class="page-link">...</span></li>';
                }
                paginationHtml += `
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
                    </li>
                `;
            }
            
            // Next button
            const nextDisabled = page >= totalPages ? 'disabled' : '';
            paginationHtml += `
                <li class="page-item ${nextDisabled}">
                    <a class="page-link" href="#" data-page="${page + 1}" 
                       ${nextDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                        Sonraki &raquo;
                    </a>
                </li>
            `;
            
            paginationHtml += `
                    </ul>
                </nav>
                <div class="text-muted text-center mt-2">
                    Toplam ${total} mesaj, Sayfa ${page} / ${totalPages}
                </div>
            `;
            
            $pagination.innerHTML = paginationHtml;
            
            // Add click event for pagination
            $pagination.querySelectorAll('.page-link').forEach(link => {
                const targetPage = link.dataset.page;
                if (targetPage) {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        const pageNum = parseInt(targetPage);
                        if (pageNum >= 1 && pageNum <= totalPages && pageNum !== page) {
                            // Use the DataLoaders module to load the selected page
                            DataLoaders.loadUserMessages(pageNum, perPage);
                            // Scroll to top of messages container
                            if ($container) {
                                $container.scrollIntoView({ behavior: 'smooth' });
                            }
                        }
                    });
                }
            });
        }
        
        // Set the HTML content
        $container.innerHTML = html;
        
        // Add event listeners for view and delete buttons
        document.querySelectorAll('.view-message').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const messageId = e.currentTarget.dataset.id;
                showMessageDetail(messageId);
            });
        });

        document.querySelectorAll('.delete-message').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const messageId = e.currentTarget.dataset.id;
                confirmDeleteMessage(messageId);
            });
        });
    }

    function populateEditModelForm(model) {
        try {
            if (!model || !model.id) {
                const errorMsg = 'Invalid model data provided to populateEditModelForm';
                Logger.error(MODULE_NAME, errorMsg, model);
                // Use the showToast function that's in scope
                showToast('Geçersiz model verisi.', 'error');
                return false;
            }

            Logger.debug(MODULE_NAME, 'Populating edit model form for model ID:', model.id, 'Model data:', model);
            
            // Check if the modal and form elements exist in the DOM
            if (!DOM.editModelModal || !DOM.editModelForm) {
                const errorMsg = 'Edit model form or modal not found in the DOM. ' +
                               'Make sure the HTML contains elements with IDs "editModelModal" and "editModelForm".';
                Logger.error(MODULE_NAME, errorMsg, {
                    editModelModal: !!DOM.editModelModal,
                    editModelForm: !!DOM.editModelForm
                });
                showToast('Düzenleme formu yüklenemedi. Sayfayı yenilemeyi deneyin.', 'error');
                return false;
            }

            // If the modal/form exists in the document but not in our DOM cache, update the cache
            if (!DOM.editModelForm || !DOM.editModelModal) {
                Logger.debug(MODULE_NAME, 'Updating DOM cache for edit model form/modal');
                DOM.editModelForm = formInDocument;
                DOM.editModelModal = modalInDocument;
            }

            // Safely populate form fields
            try {
                // Debug: Check each form field before setting its value
                const formFields = {
                    modelId: DOM.editModelForm.elements['modelId'],
                    name: DOM.editModelForm.elements['editModelName'],
                    apiKey: DOM.editModelForm.elements['editModelApiKey'],
                    baseUrl: DOM.editModelForm.elements['editModelBaseUrl'],
                    description: DOM.editModelForm.elements['editModelDescription'],
                    category: DOM.editModelForm.elements['editModelCategory']
                };
                
                // Log which fields were found and their current values
                const fieldStatus = Object.entries(formFields).map(([key, el]) => ({
                    field: key,
                    exists: !!el,
                    currentValue: el?.value,
                    elementType: el?.type || (el ? el.tagName : 'undefined')
                }));
                
                Logger.debug(MODULE_NAME, 'Form fields status:', fieldStatus);

                // Set form values from model data
                const setFieldValue = (id, value) => {
                    const element = document.getElementById(id);
                    if (element) element.value = value || '';
                };

                try {
                    // Set basic model info
                    setFieldValue('editModelId', model.id);
                    setFieldValue('editModelName', model.name);
                    setFieldValue('editModelDataAiIndex', model.data_ai_index);
                    
                    // Set API configuration
                    const apiConfig = model.api_config || {};
                    setFieldValue('editModelApiUrl', apiConfig.url || '');
                    setFieldValue('editModelRequestMethod', apiConfig.method || 'POST');
                    setFieldValue('editModelResponsePath', apiConfig.response_path || '');
                    
                    // Set headers and body as JSON strings
                    if (apiConfig.headers) {
                        setFieldValue('editModelRequestHeaders', JSON.stringify(apiConfig.headers, null, 2));
                    }
                    
                    if (apiConfig.body_template) {
                        setFieldValue('editModelRequestBody', JSON.stringify(apiConfig.body_template, null, 2));
                    }
                    
                    // Set icon preview
                    const iconPreview = document.getElementById('editModelIconPreview');
                    if (iconPreview && model.icon) {
                        iconPreview.className = `bi ${model.icon}`;
                    }
                    
                    // Load categories and select the correct one
                    const categorySelect = document.getElementById('editModelCategory');
                    if (categorySelect) {
                        // Clear existing options first
                        categorySelect.innerHTML = '';
                        
                        // Load categories and select the correct one
                        AdminPanel.DataLoaders.loadCategories()
                            .then(categories => {
                                if (categories && categories.length > 0) {
                                    categories.forEach(category => {
                                        const option = document.createElement('option');
                                        option.value = category.id;
                                        option.textContent = category.name;
                                        categorySelect.appendChild(option);
                                    });
                                    
                                    // Select the category if specified
                                    if (model.category_id) {
                                        categorySelect.value = model.category_id;
                                    }
                                    
                                    // Show the edit model modal
                                    if (DOM.editModelModal) {
                                        const modal = bootstrap.Modal.getInstance(DOM.editModelModal) || new bootstrap.Modal(DOM.editModelModal);
                                        modal.show();
                                        Logger.debug(MODULE_NAME, 'Modal shown successfully');
                                    } else {
                                        Logger.error(MODULE_NAME, 'Edit model modal element not found in DOM');
                                    }
                                }
                            })
                            .catch(error => {
                                Logger.error(MODULE_NAME, 'Error loading categories:', error);
                                showToast('Kategoriler yüklenirken bir hata oluştu.', 'error');
                            });
                    }
                    
                    return true;
                } catch (error) {
                    Logger.error(MODULE_NAME, 'Error populating form:', error);
                    showToast('Form doldurulurken bir hata oluştu.', 'error');
                    return false;
                }
            } catch (formError) {
                Logger.error(MODULE_NAME, 'Error populating form fields:', formError);
                UIManager.showToast('Form alanları doldurulurken hata oluştu.', 'error');
                return false;
            }
        } catch (error) {
            Logger.error(MODULE_NAME, 'Unexpected error in populateEditModelForm:', error);
            UIManager.showToast('Model düzenleme formu yüklenirken beklenmeyen bir hata oluştu.', 'error');
            return false;
        }
    }

    function populateEditCategoryForm(category) {
        Logger.debug(MODULE_NAME, 'Populating edit category form for category ID:', category.id, category);
        if (!DOM.editCategoryForm || !DOM.editCategoryModal) {
            Logger.error(MODULE_NAME, 'Edit category form or modal not found in DOM.');
            return;
        }
        DOM.editCategoryForm.categoryId.value = category.id;
        DOM.editCategoryForm.editCategoryName.value = category.name;
        // Diğer kategori alanları (icon, description vb.) varsa buraya eklenebilir.
        // DOM.editCategoryForm.editCategoryIcon.value = category.icon || '';
        // DOM.editCategoryForm.editCategoryDescription.value = category.description || '';
        const modalInstance = bootstrap.Modal.getInstance(DOM.editCategoryModal) || new bootstrap.Modal(DOM.editCategoryModal);
        modalInstance.show();
    }

    function attachModelActionListeners() {
        Logger.debug(MODULE_NAME, 'Attaching model action listeners.');
        document.querySelectorAll('#models-section .btn-edit-model').forEach(button => {
            button.removeEventListener('click', AdminPanel.EventHandlers.handleEditModelShow); // Global namespace üzerinden erişim
            button.addEventListener('click', AdminPanel.EventHandlers.handleEditModelShow);
        });
        document.querySelectorAll('#models-section .btn-delete-model').forEach(button => {
            button.removeEventListener('click', AdminPanel.EventHandlers.handleDeleteModel);
            button.addEventListener('click', AdminPanel.EventHandlers.handleDeleteModel);
        });
    }

    function attachCategoryActionListeners() {
        Logger.debug(MODULE_NAME, 'Attaching category action listeners.');
        document.querySelectorAll('#categories-section .btn-edit-category').forEach(button => {
            button.removeEventListener('click', AdminPanel.EventHandlers.handleEditCategoryShow);
            button.addEventListener('click', AdminPanel.EventHandlers.handleEditCategoryShow);
        });
        document.querySelectorAll('#categories-section .btn-delete-category').forEach(button => {
            button.removeEventListener('click', AdminPanel.EventHandlers.handleDeleteCategory);
            button.addEventListener('click', AdminPanel.EventHandlers.handleDeleteCategory);
        });
    }

    function attachMessageActionListeners() {
        Logger.debug(MODULE_NAME, 'Attaching message action listeners.');
        document.querySelectorAll('#messages-section .btn-delete-message').forEach(button => {
            button.removeEventListener('click', AdminPanel.EventHandlers.handleDeleteMessage);
            button.addEventListener('click', AdminPanel.EventHandlers.handleDeleteMessage);
        });
    }

    function showToast(message, type = 'info') {
        Logger.info(MODULE_NAME, `Showing toast: [${type}] ${message}`);
        if (!DOM.toastContainer) {
            DOM.toastContainer = document.createElement('div');
            DOM.toastContainer.id = 'toast-container';
            DOM.toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            DOM.toastContainer.style.zIndex = "1090";
            document.body.appendChild(DOM.toastContainer);
            Logger.debug(MODULE_NAME, 'Toast container created and appended to body.');
        }

        const toastEl = document.createElement('div');
        const toastTypeClass = type === 'error' ? 'bg-danger' : (type === 'success' ? 'bg-success' : 'bg-primary');
        toastEl.className = `toast align-items-center text-white ${toastTypeClass} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        DOM.toastContainer.appendChild(toastEl);
        const bsToast = new bootstrap.Toast(toastEl, { delay: 5000 });
        bsToast.show();
        toastEl.addEventListener('hidden.bs.toast', () => {
            Logger.debug(MODULE_NAME, 'Toast hidden and removing from DOM.');
            toastEl.remove();
        });
    }

    return {
        showSection,
        renderModels,
        renderCategories,
        renderUserMessages,
        populateEditModelForm,
        populateEditCategoryForm,
        // attach listener fonksiyonları dahili olarak çağrıldığı için dışa aktarmaya gerek yok,
        // ama gerekirse eklenebilir.
        showToast,
    };
})(AdminPanel.DOM, AdminPanel.Logger, AdminPanel.State);


//=============================================================================
// 7. VERİ YÜKLEYİCİ MODÜLÜ (AdminPanel.DataLoaders)
//=============================================================================
AdminPanel.DataLoaders = (function (ApiService, UIManager, State, Logger, DOM, EventHandlers) {
    const MODULE_NAME = 'DataLoaders';

    async function loadModels() {
        Logger.info(MODULE_NAME, 'Loading models...');
        try {
            const models = await ApiService.getModels();
            State.models = models;
            UIManager.renderModels(models);
            Logger.info(MODULE_NAME, 'Models loaded and rendered successfully.', models.length);
            // Model formlarındaki kategori dropdown'larını güncelle (eğer kategoriler zaten yüklüyse)
            if (State.categories.length > 0) {
                 await loadCategoriesForModelForms(DOM.modelCategorySelect);
                 await loadCategoriesForModelForms(DOM.editModelCategorySelect);
            } else {
                // Kategoriler henüz yüklenmediyse, önce onları yükle
                await loadCategories(false); // renderCategories çağrılmasın, sadece state güncellensin
                await loadCategoriesForModelForms(DOM.modelCategorySelect);
                await loadCategoriesForModelForms(DOM.editModelCategorySelect);
            }
        } catch (error) {
            Logger.error(MODULE_NAME, 'Failed to load models:', error.message, error);
            UIManager.showToast(`Modeller yüklenirken bir hata oluştu: ${error.message}`, 'error');
            UIManager.renderModels([]); // Hata durumunda boş liste göster
        }
    }

    async function loadCategories(shouldRender = true) {
        Logger.info(MODULE_NAME, `Loading categories... (render: ${shouldRender})`);
        try {
            const categories = await ApiService.getCategories();
            State.categories = categories;
            if (shouldRender) {
                UIManager.renderCategories(categories);
            }
            Logger.info(MODULE_NAME, 'Categories loaded successfully.', categories.length);
            // Model formlarındaki kategori dropdown'larını güncelle
            await loadCategoriesForModelForms(DOM.modelCategorySelect);
            await loadCategoriesForModelForms(DOM.editModelCategorySelect);
        } catch (error) {
            Logger.error(MODULE_NAME, 'Failed to load categories:', error.message, error);
            UIManager.showToast(`Kategoriler yüklenirken bir hata oluştu: ${error.message}`, 'error');
            if (shouldRender) {
                UIManager.renderCategories([]); // Hata durumunda boş liste göster
            }
        }
    }

    async function loadCategoriesForModelForms(selectElement, selectedValue = null) {
        if (!selectElement) {
            Logger.warn(MODULE_NAME, 'loadCategoriesForModelForms: Select element is null or undefined.');
            return;
        }
        Logger.debug(MODULE_NAME, `Loading categories for model form select: ${selectElement.id}, selectedValue: ${selectedValue}`);
        try {
            // State'deki kategorileri kullan, eğer boşsa API'den çek (ama bu genellikle loadCategories tarafından halledilmiş olmalı)
            let categoriesToUse = State.categories;
            if (!categoriesToUse || categoriesToUse.length === 0) {
                Logger.info(MODULE_NAME, 'Categories not in state, fetching for model forms.');
                categoriesToUse = await ApiService.getCategories();
                State.categories = categoriesToUse; // State'i de güncelle
            }

            selectElement.innerHTML = '<option value="">Kategori Seçin</option>';
            categoriesToUse.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                if (selectedValue && category.id.toString() === selectedValue.toString()) {
                    option.selected = true;
                }
                selectElement.appendChild(option);
            });
            Logger.debug(MODULE_NAME, `Categories populated for select: ${selectElement.id}`);
        } catch (error) {
            Logger.error(MODULE_NAME, `Failed to load categories for model form ${selectElement.id}:`, error.message, error);
            UIManager.showToast('Model formları için kategoriler yüklenemedi.', 'error');
        }
    }

    async function loadUserMessages(page = 1, perPage = 25, forceRender = false) {
        Logger.info(MODULE_NAME, `Loading user messages (page: ${page}, perPage: ${perPage}, forceRender: ${forceRender})...`);
        
        // Only proceed if we're forcing the render or if the messages section is active
        const messagesSection = document.getElementById('messages-section');
        if (!forceRender && (!messagesSection || window.getComputedStyle(messagesSection).display === 'none')) {
            Logger.debug(MODULE_NAME, 'Messages section is not active, skipping render');
            return;
        }
        
        try {
            const response = await ApiService.getUserMessages(page, perPage);
            State.userMessages = response.messages;
            State.userMessagesPagination = {
                currentPage: response.page || page,
                perPage: response.per_page || perPage,
                total: response.total || 0,
                totalPages: response.total_pages || Math.ceil((response.total || 0) / perPage)
            };
            
            // Only render if we have a container or if we're forcing the render
            const $container = document.getElementById('user-messages-container');
            if ($container || forceRender) {
                UIManager.renderUserMessages(response);
                Logger.info(MODULE_NAME, 'User messages loaded and rendered successfully.', response.messages.length);
            } else {
                Logger.debug(MODULE_NAME, 'Skipping render - messages container not found');
            }
        } catch (error) {
            Logger.error(MODULE_NAME, 'Failed to load user messages:', error.message, error);
            UIManager.showToast(`Kullanıcı mesajları yüklenirken bir hata oluştu: ${error.message}`, 'error');
            
            // Only try to render error state if we have a container
            const $container = document.getElementById('user-messages-container');
            if ($container || forceRender) {
                UIManager.renderUserMessages({ messages: [], total: 0, page: 1, per_page: perPage, total_pages: 0 });
            }
        }
    }

    async function loadDashboardData() {
        Logger.info(MODULE_NAME, 'Loading dashboard data...');
        UIManager.showSection('dashboard'); // Önce dashboard bölümünü göster
        try {
            // Load data in parallel
            await Promise.all([
                loadModels(),
                loadCategories(), // This might also update models, be careful
                loadUserMessages()
            ]);
            
            // Update dashboard stats
            if (typeof AdminPanel !== 'undefined' && AdminPanel.EventHandlers && 
                typeof AdminPanel.EventHandlers.updateDashboardStats === 'function') {
                AdminPanel.EventHandlers.updateDashboardStats();
            } else {
                Logger.warn(MODULE_NAME, 'updateDashboardStats function not found in EventHandlers');
            }
            
            Logger.info(MODULE_NAME, 'Dashboard data loaded successfully.');
        } catch (error) {
            Logger.error(MODULE_NAME, 'Error loading dashboard data:', error);
            UIManager.showToast('Dashboard verileri yüklenirken genel bir hata oluştu.', 'error');
        }
    }


    return {
        loadModels,
        loadCategories,
        loadCategoriesForModelForms,
        loadUserMessages,
        loadDashboardData,
    };
})(AdminPanel.ApiService, AdminPanel.UIManager, AdminPanel.State, AdminPanel.Logger, AdminPanel.DOM, AdminPanel.EventHandlers); // EventHandlers buraya eklendi


//=============================================================================
// 8. OLAY İŞLEYİCİ MODÜLÜ (AdminPanel.EventHandlers)
//=============================================================================
AdminPanel.EventHandlers = (function (DOM, UIManager, ApiService, DataLoaders, State, Logger) {
    const MODULE_NAME = 'EventHandlers';

    function handleNavClick(event) {
        event.preventDefault();
        const targetLink = event.target.closest('a');
        if (!targetLink || !targetLink.id) {
            Logger.warn(MODULE_NAME, 'handleNavClick: Invalid navigation link clicked.', event.target);
            return;
        }

        const sectionId = targetLink.id.replace('nav-', ''); // 'nav-models' -> 'models'
        Logger.info(MODULE_NAME, `Navigation click: ${sectionId}`);
        UIManager.showSection(sectionId);

        switch (sectionId) {
            case 'dashboard':
                DataLoaders.loadDashboardData();
                break;
            case 'models':
                DataLoaders.loadModels();
                break;
            case 'categories':
                DataLoaders.loadCategories();
                break;
            case 'messages':
                Logger.info(MODULE_NAME, 'Messages section clicked, loading messages...');
                // Force load and render messages when the messages section is clicked
                DataLoaders.loadUserMessages(1, 25, true);
                break;
            case 'users': // Kullanıcılar bölümü için veri yükleme eklenebilir
                 Logger.info(MODULE_NAME, "Users section clicked, no data loader implemented yet.");
                 UIManager.showToast("Kullanıcı yönetimi henüz aktif değil.", "info");
                break;
            case 'settings': // Ayarlar bölümü için veri yükleme eklenebilir
                 Logger.info(MODULE_NAME, "Settings section clicked, no data loader implemented yet.");
                 UIManager.showToast("Ayarlar bölümü henüz aktif değil.", "info");
                break;
            default:
                Logger.warn(MODULE_NAME, `No data loader defined for section: ${sectionId}`);
        }
    }

    function updateDashboardStats() {
        Logger.debug(MODULE_NAME, 'Updating dashboard stats.');
        if (DOM.dashboardCategoryCount) {
            DOM.dashboardCategoryCount.textContent = State.categories.length;
        }
        if (DOM.dashboardModelCount) {
            DOM.dashboardModelCount.textContent = State.models.length;
        }
        if (DOM.dashboardMessageCount) { // Eğer mesaj sayısı gösteriliyorsa
            DOM.dashboardMessageCount.textContent = State.userMessages.length;
        }
    }

    async function handleAddModel(event) {
        event.preventDefault();
        Logger.info(MODULE_NAME, 'Attempting to add a new model.');
        if (!DOM.addModelForm) {
            Logger.error(MODULE_NAME, 'Add model form not found.');
            return;
        }
        const formData = new FormData(DOM.addModelForm);
        const data = {
            name: formData.get('modelName'),
            api_key: formData.get('modelApiKey'),
            base_url: formData.get('modelBaseUrl'),
            description: formData.get('modelDescription'),
            category_id: parseInt(formData.get('modelCategory'), 10) || null, // Kategori ID'sini integer yap, yoksa null
        };
        Logger.debug(MODULE_NAME, 'Add model form data:', data);
        try {
            await ApiService.addModel(data);
            UIManager.showToast('Model başarıyla eklendi!', 'success');
            DOM.addModelForm.reset();
            await DataLoaders.loadModels(); // Listeyi ve state'i yenile
            updateDashboardStats(); // Dashboard'u güncelle
        } catch (error) {
            Logger.error(MODULE_NAME, 'Failed to add model:', error.message, data, error);
            UIManager.showToast(`Model eklenirken hata: ${error.message}`, 'error');
        }
    }

    async function handleEditModelShow(event) {
        if (!event || !event.target) {
            Logger.error(MODULE_NAME, 'Invalid event object in handleEditModelShow');
            return;
        }

        const modelId = event.target.dataset?.id;
        if (!modelId) {
            Logger.error(MODULE_NAME, 'No model ID found in the event target');
            UIManager.showToast('Düzenlenecek model bulunamadı.', 'error');
            return;
        }

        Logger.info(MODULE_NAME, `Attempting to show edit form for model ID: ${modelId}`);
        
        try {
            // First, try to find the model in the current state
            let model = State.models?.find(m => m && m.id && m.id.toString() === modelId);
            
            if (!model) {
                Logger.debug(MODULE_NAME, `Model with ID ${modelId} not found in current state. Attempting to refresh models.`);
                await DataLoaders.loadModels();
                model = State.models?.find(m => m && m.id && m.id.toString() === modelId);
                
                if (!model) {
                    Logger.warn(MODULE_NAME, `Model with ID ${modelId} not found after refreshing models.`);
                    UIManager.showToast(`Model (ID: ${modelId}) bulunamadı.`, 'error');
                    return;
                }
            }

            // Load categories for the form
            try {
                await DataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect, model.category_id);
                
                // Try to populate and show the form
                const success = UIManager.populateEditModelForm(model);
                if (!success) {
                    Logger.warn(MODULE_NAME, `Failed to populate edit form for model ID: ${modelId}`);
                    // populateEditModelForm already shows an error toast
                }
            } catch (categoryError) {
                Logger.error(MODULE_NAME, `Error loading categories for model form:`, categoryError);
                UIManager.showToast('Kategoriler yüklenirken bir hata oluştu.', 'error');
            }
        } catch (error) {
            const errorMessage = error?.message || 'Bilinmeyen hata';
            Logger.error(MODULE_NAME, `Error in handleEditModelShow for model ID ${modelId}:`, errorMessage, error);
            UIManager.showToast(`Model düzenleme ekranı açılırken hata: ${errorMessage}`, 'error');
        }
    }

    async function handleUpdateModel(event) {
        event.preventDefault();
        Logger.info(MODULE_NAME, 'Attempting to update a model.');
        if (!DOM.editModelForm) {
            Logger.error(MODULE_NAME, 'Edit model form not found.');
            return;
        }
        const modelId = DOM.editModelForm.modelId.value;
        const formData = new FormData(DOM.editModelForm);
        const data = {
            name: formData.get('editModelName'),
            api_key: formData.get('editModelApiKey'),
            base_url: formData.get('editModelBaseUrl'),
            description: formData.get('editModelDescription'),
            category_id: parseInt(formData.get('editModelCategory'), 10) || null,
        };
        Logger.debug(MODULE_NAME, `Updating model ID: ${modelId} with data:`, data);
        try {
            await ApiService.updateModel(modelId, data);
            UIManager.showToast('Model başarıyla güncellendi!', 'success');
            const modalInstance = bootstrap.Modal.getInstance(DOM.editModelModal);
            if (modalInstance) modalInstance.hide();
            await DataLoaders.loadModels();
            updateDashboardStats();
        } catch (error) {
            Logger.error(MODULE_NAME, `Failed to update model ID ${modelId}:`, error.message, data, error);
            UIManager.showToast(`Model güncellenirken hata: ${error.message}`, 'error');
        }
    }

    async function handleDeleteModel(event) {
        const modelId = event.target.dataset.id;
        Logger.info(MODULE_NAME, `Attempting to delete model ID: ${modelId}`);
        if (confirm('Bu modeli silmek istediğinizden emin misiniz?')) {
            try {
                await ApiService.deleteModel(modelId);
                UIManager.showToast('Model başarıyla silindi!', 'success');
                await DataLoaders.loadModels();
                updateDashboardStats();
            } catch (error) {
                Logger.error(MODULE_NAME, `Failed to delete model ID ${modelId}:`, error.message, error);
                UIManager.showToast(`Model silinirken hata: ${error.message}`, 'error');
            }
        } else {
            Logger.debug(MODULE_NAME, `Deletion cancelled for model ID: ${modelId}`);
        }
    }

    async function handleAddCategory(event) {
        event.preventDefault();
        Logger.info(MODULE_NAME, 'Attempting to add a new category.');
        if (!DOM.addCategoryForm) {
            Logger.error(MODULE_NAME, 'Add category form not found.');
            return;
        }
        const formData = new FormData(DOM.addCategoryForm);
        const data = {
            name: formData.get('categoryName'),
            // icon: formData.get('categoryIcon'), // Eğer icon alanı varsa
            // description: formData.get('categoryDescription') // Eğer açıklama alanı varsa
        };
        Logger.debug(MODULE_NAME, 'Add category form data:', data);
        try {
            await ApiService.addCategory(data);
            UIManager.showToast('Kategori başarıyla eklendi!', 'success');
            DOM.addCategoryForm.reset();
            await DataLoaders.loadCategories(); // Kategori listesini ve state'i yenile
            // Model formlarındaki kategori dropdown'larını da güncelle
            await DataLoaders.loadCategoriesForModelForms(DOM.modelCategorySelect);
            await DataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect);
            updateDashboardStats();
        } catch (error) {
            Logger.error(MODULE_NAME, 'Failed to add category:', error.message, data, error);
            UIManager.showToast(`Kategori eklenirken hata: ${error.message}`, 'error');
        }
    }

    async function handleEditCategoryShow(event) {
        const categoryId = event.target.closest('button').dataset.id; // Buton içindeki ikondan tıklama gelebilir
        Logger.info(MODULE_NAME, `Showing edit form for category ID: ${categoryId}`);
        try {
            const category = State.categories.find(c => c.id.toString() === categoryId);
            if (category) {
                Logger.debug(MODULE_NAME, 'Category found in state:', category);
                UIManager.populateEditCategoryForm(category);
            } else {
                Logger.warn(MODULE_NAME, `Category with ID ${categoryId} not found in current state. Attempting to fetch.`);
                await DataLoaders.loadCategories();
                const freshCategory = State.categories.find(c => c.id.toString() === categoryId);
                if (freshCategory) {
                    UIManager.populateEditCategoryForm(freshCategory);
                } else {
                    UIManager.showToast(`Kategori ID ${categoryId} bulunamadı.`, 'error');
                }
            }
        } catch (error) {
            Logger.error(MODULE_NAME, `Error showing edit category form for ID ${categoryId}:`, error.message, error);
            UIManager.showToast(`Kategori detayları getirilirken hata: ${error.message}`, 'error');
        }
    }

    async function handleUpdateCategory(event) {
        event.preventDefault();
        Logger.info(MODULE_NAME, 'Attempting to update a category.');
        if (!DOM.editCategoryForm) {
            Logger.error(MODULE_NAME, 'Edit category form not found.');
            return;
        }
        const categoryId = DOM.editCategoryForm.categoryId.value;
        const formData = new FormData(DOM.editCategoryForm);
        const data = {
            name: formData.get('editCategoryName'),
            // icon: formData.get('editCategoryIcon'),
            // description: formData.get('editCategoryDescription')
        };
        Logger.debug(MODULE_NAME, `Updating category ID: ${categoryId} with data:`, data);
        try {
            await ApiService.updateCategory(categoryId, data);
            UIManager.showToast('Kategori başarıyla güncellendi!', 'success');
            const modalInstance = bootstrap.Modal.getInstance(DOM.editCategoryModal);
            if (modalInstance) modalInstance.hide();
            await DataLoaders.loadCategories();
            await DataLoaders.loadCategoriesForModelForms(DOM.modelCategorySelect);
            await DataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect);
            await DataLoaders.loadModels(); // Kategori adı değişmiş olabileceğinden modelleri de güncelle
            updateDashboardStats();
        } catch (error) {
            Logger.error(MODULE_NAME, `Failed to update category ID ${categoryId}:`, error.message, data, error);
            UIManager.showToast(`Kategori güncellenirken hata: ${error.message}`, 'error');
        }
    }

    async function handleDeleteCategory(event) {
        const categoryId = event.target.closest('button').dataset.id;
        Logger.info(MODULE_NAME, `Attempting to delete category ID: ${categoryId}`);
        if (confirm('Bu kategoriyi silmek istediğinizden emin misiniz? Bu kategoriyi kullanan modeller etkilenebilir.')) {
            try {
                await ApiService.deleteCategory(categoryId);
                UIManager.showToast('Kategori başarıyla silindi!', 'success');
                await DataLoaders.loadCategories();
                await DataLoaders.loadCategoriesForModelForms(DOM.modelCategorySelect);
                await DataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect);
                await DataLoaders.loadModels(); // Kategorisi silinen modelleri de güncelle
                updateDashboardStats();
            } catch (error) {
                Logger.error(MODULE_NAME, `Failed to delete category ID ${categoryId}:`, error.message, error);
                UIManager.showToast(`Kategori silinirken hata: ${error.message}`, 'error');
            }
        } else {
            Logger.debug(MODULE_NAME, `Deletion cancelled for category ID: ${categoryId}`);
        }
    }

    async function handleDeleteMessage(event) {
        const messageId = event.target.dataset.id;
        Logger.info(MODULE_NAME, `Attempting to delete message ID: ${messageId}`);
        if (confirm('Bu mesajı silmek istediğinizden emin misiniz?')) {
            try {
                await ApiService.deleteUserMessage(messageId);
                UIManager.showToast('Mesaj başarıyla silindi!', 'success');
                await DataLoaders.loadUserMessages();
                updateDashboardStats(); // Mesaj sayısı değiştiği için
            } catch (error) {
                Logger.error(MODULE_NAME, `Failed to delete message ID ${messageId}:`, error.message, error);
                UIManager.showToast(`Mesaj silinirken hata: ${error.message}`, 'error');
            }
        } else {
            Logger.debug(MODULE_NAME, `Deletion cancelled for message ID: ${messageId}`);
        }
    }

    return {
        handleNavClick,
        updateDashboardStats,
        handleAddModel,
        handleEditModelShow,
        handleUpdateModel,
        handleDeleteModel,
        handleAddCategory,
        handleEditCategoryShow,
        handleUpdateCategory,
        handleDeleteCategory,
        handleDeleteMessage,
    };
})(AdminPanel.DOM, AdminPanel.UIManager, AdminPanel.ApiService, AdminPanel.DataLoaders, AdminPanel.State, AdminPanel.Logger);

//=============================================================================
// 9. UYGULAMA BAŞLATMA MODÜLÜ (AdminPanel.App)
//=============================================================================
AdminPanel.App = (function (DOM, EventHandlers, DataLoaders, Logger, UIManager) {
    const MODULE_NAME = 'App';

    function setupEventListeners() {
        Logger.info(MODULE_NAME, 'Setting up global event listeners...');

        // Navigasyon olay dinleyicileri
        Object.entries(DOM.navLinks).forEach(([key, link]) => {
            if (!link) {
                Logger.debug(MODULE_NAME, `Navigation link for '${key}' not found in DOM. This is expected if the feature is not implemented yet.`);
                return;
            }
            
            try {
                // Remove existing listener to prevent duplicates
                link.removeEventListener('click', EventHandlers.handleNavClick);
                // Add new listener
                link.addEventListener('click', EventHandlers.handleNavClick);
                Logger.debug(MODULE_NAME, `Added event listener for navigation: ${key}`);
            } catch (error) {
                Logger.error(MODULE_NAME, `Failed to set up event listener for ${key}:`, error);
            }
        });
        Logger.debug(MODULE_NAME, 'Navigation listeners attached.');

        // Form event listeners
        const formHandlers = [
            { form: DOM.addModelForm, handler: EventHandlers.handleAddModel, name: 'Add Model Form' },
            { form: DOM.editModelForm, handler: EventHandlers.handleUpdateModel, name: 'Edit Model Form' },
            { form: DOM.addCategoryForm, handler: EventHandlers.handleAddCategory, name: 'Add Category Form' },
            { form: DOM.editCategoryForm, handler: EventHandlers.handleUpdateCategory, name: 'Edit Category Form' }
        ];

        formHandlers.forEach(({ form, handler, name }) => {
            if (!form) {
                Logger.debug(MODULE_NAME, `${name} not found in DOM. This is expected if the feature is not implemented yet.`);
                return;
            }

            try {
                // Remove existing listener to prevent duplicates
                form.removeEventListener('submit', handler);
                // Add new listener
                form.addEventListener('submit', handler);
                Logger.debug(MODULE_NAME, `Added event listener for: ${name}`);
            } catch (error) {
                Logger.error(MODULE_NAME, `Failed to set up event listener for ${name}:`, error);
            }
        });
        Logger.debug(MODULE_NAME, 'Form submit listeners attached.');
    }

    function init() {
        Logger.info(MODULE_NAME, 'Admin Panel Initializing...');
        AdminPanel.Logger.setLevel('DEBUG'); // Log seviyesini ayarla (DEBUG, INFO, WARN, ERROR, NONE)

        setupEventListeners();

        // Başlangıç bölümünü ve verilerini yükle
        // URL hash'ine göre başlangıç bölümünü belirle veya varsayılan olarak dashboard'u kullan
        const initialSectionIdFromHash = window.location.hash ? window.location.hash.substring(1) : null;
        const validSectionIds = Object.keys(DOM.contentSections);
        let initialSectionId = 'dashboard'; // Varsayılan

        if (initialSectionIdFromHash && validSectionIds.includes(initialSectionIdFromHash)) {
            initialSectionId = initialSectionIdFromHash;
        }
        Logger.info(MODULE_NAME, `Initial section to load: ${initialSectionId}`);


        // İlgili navigasyon linkini aktif yap ve bölümü göster
        UIManager.showSection(initialSectionId);

        // İlgili bölüm için veri yükleme
        // handleNavClick zaten bölüm ID'sine göre doğru yükleyiciyi çağırıyor.
        // Sahte bir event objesi oluşturup handleNavClick'i tetikleyebiliriz veya doğrudan yükleyiciyi çağırabiliriz.
        // Doğrudan çağırmak daha temiz olabilir.
        switch (initialSectionId) {
            case 'dashboard':
                DataLoaders.loadDashboardData();
                break;
            case 'models':
                DataLoaders.loadModels();
                break;
            case 'categories':
                DataLoaders.loadCategories();
                break;
            case 'messages':
                Logger.info(MODULE_NAME, 'Messages section clicked, loading messages...');
                // Force load and render messages when the messages section is clicked
                DataLoaders.loadUserMessages(1, 25, true);
                break;
            // Diğer bölümler için de benzer case'ler eklenebilir.
            default:
                Logger.info(MODULE_NAME, `No specific data loader for initial section: ${initialSectionId}. Dashboard will be loaded if section is invalid.`);
                // Eğer initialSectionId geçersizse veya dashboard ise, dashboard verilerini yükle
                if (!validSectionIds.includes(initialSectionId)) {
                    UIManager.showSection('dashboard'); // Geçersizse dashboard'a yönlendir
                    DataLoaders.loadDashboardData();
                }
        }
        Logger.info(MODULE_NAME, 'Admin Panel Initialized.');
    }

    return {
        init,
    };
})(AdminPanel.DOM, AdminPanel.EventHandlers, AdminPanel.DataLoaders, AdminPanel.Logger, AdminPanel.UIManager);

//=============================================================================
// 10. DOM HAZIR OLDUĞUNDA BAŞLATMA
//=============================================================================
document.addEventListener('DOMContentLoaded', AdminPanel.App.init);

