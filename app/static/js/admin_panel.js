/**
 * Admin Paneli Yönetim Modülü
 * ============================
 * @description Model, kategori, kullanıcı ve mesaj yönetim arayüzü ve etkileşimlerini yönetir.
 * @version 1.0.0
 * @author Proje Geliştiricisi
 *
 * İÇİNDEKİLER
 * ===============
 * 1. TEMEL SİSTEM (CORE SYSTEM)
 * 1.1. DOM Elementleri (DOM Elements)
 *
 * 2. API SERVİSİ (API SERVICE)
 * 2.1. Genel Fetch Fonksiyonu (_fetch)
 * 2.2. Model API Fonksiyonları
 * 2.2.1. getModels
 * 2.2.2. addModel
 * 2.2.3. updateModel
 * 2.2.4. deleteModel
 * 2.3. Kategori API Fonksiyonları
 * 2.3.1. getCategories
 * 2.3.2. addCategory
 * 2.3.3. updateCategory
 * 2.3.4. deleteCategory
 * 2.4. Kullanıcı Mesajları API Fonksiyonları
 * 2.4.1. getUserMessages
 * 2.4.2. deleteUserMessage
 *
 * 3. KULLANICI ARAYÜZÜ YÖNETİMİ (UI MANAGEMENT)
 * 3.1. Bölüm Gösterimi (showSection)
 * 3.2. Veri Oluşturucuları (Data Renderers)
 * 3.2.1. Modelleri Oluştur (renderModels)
 * 3.2.2. Kategorileri Oluştur (renderCategories)
 * 3.2.3. Kullanıcı Mesajlarını Oluştur (renderUserMessages)
 * 3.3. Form Doldurucuları (Form Populators)
 * 3.3.1. Model Düzenleme Formunu Doldur (populateEditModelForm)
 * 3.3.2. Kategori Düzenleme Formunu Doldur (populateEditCategoryForm)
 * 3.4. Olay Dinleyici Ekleyicileri (Action Listener Attachments)
 * 3.4.1. Model Aksiyon Dinleyicileri (attachModelActionListeners)
 * 3.4.2. Kategori Aksiyon Dinleyicileri (attachCategoryActionListeners)
 * 3.4.3. Mesaj Aksiyon Dinleyicileri (attachMessageActionListeners)
 * 3.5. Geri Bildirim (showToast)
 *
 * 4. VERİ YÜKLEYİCİLER (DATA LOADERS)
 * 4.1. Modelleri Yükle (loadModels)
 * 4.2. Kategorileri Yükle (loadCategories)
 * 4.3. Model Formları İçin Kategorileri Yükle (loadCategoriesForModelForms)
 * 4.4. Kullanıcı Mesajlarını Yükle (loadUserMessages)
 *
 * 5. OLAY İŞLEYİCİLERİ (EVENT HANDLERS)
 * 5.1. Navigasyon Tıklamaları (handleNavClick)
 * 5.2. Model İşlemleri
 * 5.2.1. Model Ekle (handleAddModel)
 * 5.2.2. Model Düzenleme Formunu Göster (handleEditModelShow)
 * 5.2.3. Model Güncelle (handleUpdateModel)
 * 5.2.4. Model Sil (handleDeleteModel)
 * 5.3. Kategori İşlemleri
 * 5.3.1. Kategori Ekle (handleAddCategory)
 * 5.3.2. Kategori Düzenleme Formunu Göster (handleEditCategoryShow)
 * 5.3.3. Kategori Güncelle (handleUpdateCategory)
 * 5.3.4. Kategori Sil (handleDeleteCategory)
 * 5.4. Mesaj İşlemleri
 * 5.4.1. Mesaj Sil (handleDeleteMessage)
 *
 * 6. BAŞLATMA (INITIALIZATION)
 * 6.1. Başlatma Fonksiyonu (init)
 * 6.2. DOM Hazır Olduğunda Başlatma
 */

//=============================================================================
// AdminPanel Modülü (IIFE)
//=============================================================================
(function () {
    'use strict'; // Strict modu etkinleştir

    //=============================================================================
    // 1. TEMEL SİSTEM (CORE SYSTEM)
    //=============================================================================

    /**
     * 1.1. DOM Elementleri (DOM Elements)
     * ------------------------------------
     * Tüm DOM öğelerine merkezi erişim noktası.
     */
    const DOM = {
        navLinks: {
            models: document.getElementById('nav-models'),
            categories: document.getElementById('nav-categories'),
            users: document.getElementById('nav-users'),
            settings: document.getElementById('nav-settings'),
            messages: document.getElementById('nav-messages'),
        },
        contentSections: {
            models: document.getElementById('models-section'),
            categories: document.getElementById('categories-section'),
            users: document.getElementById('users-section'),
            settings: document.getElementById('settings-section'),
            messages: document.getElementById('messages-section'),
        },
        modelsTableBody: document.querySelector('#models-section table tbody'),
        addModelForm: document.getElementById('add-model-form'),
        modelCategorySelect: document.getElementById('modelCategory'), // Add Model Form içindeki kategori seçimi
        editModelModal: document.getElementById('edit-model-modal'),
        editModelForm: document.getElementById('edit-model-form'),
        editModelCategorySelect: document.getElementById('editModelCategory'), // Edit Model Form içindeki kategori seçimi
        categoriesTableBody: document.getElementById('categoriesTableBody'),
        addCategoryForm: document.getElementById('add-category-form'),
        editCategoryModal: document.getElementById('edit-category-modal'),
        editCategoryForm: document.getElementById('edit-category-form'),
        messagesTableBody: document.querySelector('#messages-section table tbody'),
        toastContainer: null // Dinamik olarak oluşturulacak
    };

    // Uygulama durumunu saklamak için state nesnesi
    const state = {
        models: [],
        categories: [],
        userMessages: []
    };

    //=============================================================================
    // 2. API SERVİSİ (API SERVICE)
    //=============================================================================
    /**
     * Sunucu ile iletişim kuran tüm fonksiyonları içerir.
     */
    const apiService = {
        /**
         * 2.1. Genel Fetch Fonksiyonu (_fetch)
         * ---------------------------------
         * Genel bir fetch isteği yapar ve hataları yönetir.
         * @param {string} url - İstek yapılacak URL.
         * @param {object} options - Fetch seçenekleri.
         * @returns {Promise<any>} - JSON olarak çözümlenmiş yanıt.
         */
        _fetch: async function (url, options = {}) {
            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ message: response.statusText }));
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                }
                return response.json();
            } catch (error) {
                console.error('API Hatası:', error);
                // ui objesi henüz tanımlanmamış olabileceğinden doğrudan DOM.showToast'u çağırmak yerine
                // ui.showToast'un varlığını kontrol edin veya hatayı yukarı fırlatın.
                // Bu örnekte ui.showToast'un daha sonra tanımlanacağını varsayıyoruz.
                if (ui && typeof ui.showToast === 'function') {
                    ui.showToast(`API Hatası: ${error.message}`, 'error');
                }
                throw error;
            }
        },

        /**
         * 2.2. Model API Fonksiyonları
         * ---------------------------
         */
        /** 2.2.1. getModels */
        getModels: function () {
            return this._fetch('/admin/api/models')
                .then(response => {
                    // API yanıtı {success: true, models: [...]} şeklinde geliyor
                    if (response && response.success && Array.isArray(response.models)) {
                        return response.models;
                    }
                    console.error('Geçersiz model verisi:', response);
                    return [];
                })
                .catch(error => {
                    console.error('Modeller yüklenirken hata oluştu:', error);
                    return [];
                });
        },
        /** 2.2.2. addModel */
        addModel: function (data) {
            return this._fetch('/admin/api/models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        /** 2.2.3. updateModel */
        updateModel: function (id, data) {
            return this._fetch(`/admin/api/models/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        /** 2.2.4. deleteModel */
        deleteModel: function (id) {
            return this._fetch(`/admin/api/models/${id}`, { method: 'DELETE' });
        },

        /**
         * 2.3. Kategori API Fonksiyonları
         * ------------------------------
         */
        /** 2.3.1. getCategories */
        getCategories: function () {
            return this._fetch('/admin/api/categories')
                .then(response => {
                    // API yanıtı {success: true, categories: [...]} şeklinde geliyor
                    if (response && response.success && Array.isArray(response.categories)) {
                        return response.categories;
                    }
                    console.error('Geçersiz kategori verisi:', response);
                    return [];
                })
                .catch(error => {
                    console.error('Kategoriler yüklenirken hata oluştu:', error);
                    return [];
                });
        },
        /** 2.3.2. addCategory */
        addCategory: function (data) {
            return this._fetch('/admin/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        /** 2.3.3. updateCategory */
        updateCategory: function (id, data) {
            return this._fetch(`/admin/api/categories/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        },
        /** 2.3.4. deleteCategory */
        deleteCategory: function (id) {
            return this._fetch(`/admin/api/categories/${id}`, { method: 'DELETE' });
        },

        /**
         * 2.4. Kullanıcı Mesajları API Fonksiyonları
         * ---------------------------------------
         */
        /** 2.4.1. getUserMessages */
        getUserMessages: function () {
            return this._fetch('/admin/api/user_messages');
        },
        /** 2.4.2. deleteUserMessage */
        deleteUserMessage: function (id) {
            return this._fetch(`/admin/api/user_messages/${id}`, { method: 'DELETE' });
        }
    };

    //=============================================================================
    // 3. KULLANICI ARAYÜZÜ YÖNETİMİ (UI MANAGEMENT)
    //=============================================================================
    /**
     * Kullanıcı arayüzünü güncelleyen fonksiyonlar.
     */
    const ui = {
        /**
         * 3.1. Bölüm Gösterimi (showSection)
         * --------------------------------
         * Belirli bir bölümü gösterir ve navigasyon linkini aktif hale getirir.
         * @param {string} sectionId - Gösterilecek bölümün ID'si ('models', 'categories' vb.).
         */
        showSection: function (sectionId) {
            Object.values(DOM.contentSections).forEach(section => {
                if (section) section.style.display = 'none';
            });
            if (DOM.contentSections[sectionId]) {
                DOM.contentSections[sectionId].style.display = 'block';
            }
            Object.values(DOM.navLinks).forEach(link => {
                if (link) link.classList.remove('active');
            });
            if (DOM.navLinks[sectionId]) {
                DOM.navLinks[sectionId].classList.add('active');
            }
        },

        /**
         * 3.2. Veri Oluşturucuları (Data Renderers)
         * ----------------------------------------
         */
        /**
         * 3.2.1. Modelleri Oluştur (renderModels)
         * Modelleri tabloya render eder.
         * @param {Array<object>} models - Render edilecek model listesi.
         */
        renderModels: function (models) {
            if (!DOM.modelsTableBody) {
                console.error('Models table body not found');
                return;
            }
            
            // Clear existing rows
            DOM.modelsTableBody.innerHTML = '';
            
            // Check if models is a valid array
            if (!Array.isArray(models)) {
                console.error('Invalid models data:', models);
                const row = DOM.modelsTableBody.insertRow();
                row.innerHTML = '<td colspan="7" class="text-center">Modeller yüklenirken bir hata oluştu</td>';
                return;
            }
            
            // If no models, show empty message
            if (models.length === 0) {
                const row = DOM.modelsTableBody.insertRow();
                row.innerHTML = '<td colspan="7" class="text-center">Henüz model bulunmamaktadır</td>';
                return;
            }
            
            // Render each model
            models.forEach(model => {
                try {
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
                } catch (error) {
                    console.error('Error rendering model:', model, error);
                }
            });
            
            // Attach event listeners
            this.attachModelActionListeners();
        },

        /**
         * 3.2.2. Kategorileri Oluştur (renderCategories)
         * Kategorileri listeye render eder.
         * @param {Array<object>} categories - Render edilecek kategori listesi.
         */
        renderCategories: function (categories) {
            if (!DOM.categoriesTableBody) {
                console.error('Categories table body not found');
                return;
            }
            
            // Clear existing rows
            DOM.categoriesTableBody.innerHTML = '';
            
            // Check if categories is a valid array
            if (!Array.isArray(categories)) {
                console.error('Invalid categories data:', categories);
                const row = DOM.categoriesTableBody.insertRow();
                row.innerHTML = '<td colspan="5" class="text-center">Kategoriler yüklenirken bir hata oluştu</td>';
                return;
            }
            
            // If no categories, show empty message
            if (categories.length === 0) {
                const row = DOM.categoriesTableBody.insertRow();
                row.innerHTML = '<td colspan="5" class="text-center">Henüz kategori bulunmamaktadır</td>';
                return;
            }
            
            // Render each category as a table row
            categories.forEach(category => {
                try {
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
                } catch (error) {
                    console.error('Error rendering category:', category, error);
                }
            });
            
            // Attach event listeners
            this.attachCategoryActionListeners();
        },

        /**
         * 3.2.3. Kullanıcı Mesajlarını Oluştur (renderUserMessages)
         * Kullanıcı mesajlarını tabloya render eder.
         * @param {Array<object>} messages - Render edilecek mesaj listesi.
         */
        renderUserMessages: function (messages) {
            if (!DOM.messagesTableBody) return;
            DOM.messagesTableBody.innerHTML = ''; // Mevcut satırları temizle
            messages.forEach(message => {
                const row = DOM.messagesTableBody.insertRow();
                const messageContent = message.message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                row.innerHTML = `
                    <td>${message.id}</td>
                    <td>${message.session_id}</td>
                    <td>${message.sender}</td>
                    <td class="message-content-cell" title="${message.message}">${messageContent.substring(0, 100)}${messageContent.length > 100 ? '...' : ''}</td>
                    <td>${new Date(message.timestamp).toLocaleString()}</td>
                    <td>
                        <button class="btn btn-sm btn-danger btn-delete-message" data-id="${message.id}">Sil</button>
                    </td>
                `;
            });
            this.attachMessageActionListeners();
        },

        /**
         * 3.3. Form Doldurucuları (Form Populators)
         * --------------------------------------
         */
        /**
         * 3.3.1. Model Düzenleme Formunu Doldur (populateEditModelForm)
         * Model düzenleme formunu verilen model verileriyle doldurur.
         * @param {object} model - Formu doldurmak için kullanılacak model nesnesi.
         */
        populateEditModelForm: function (model) {
            if (!DOM.editModelForm || !DOM.editModelModal) return;
            DOM.editModelForm.modelId.value = model.id;
            DOM.editModelForm.editModelName.value = model.name;
            DOM.editModelForm.editModelApiKey.value = model.api_key || '';
            DOM.editModelForm.editModelBaseUrl.value = model.base_url || '';
            DOM.editModelForm.editModelDescription.value = model.description || '';
            DOM.editModelForm.editModelCategory.value = model.category_id;
            const modalInstance = bootstrap.Modal.getInstance(DOM.editModelModal) || new bootstrap.Modal(DOM.editModelModal);
            modalInstance.show();
        },

        /**
         * 3.3.2. Kategori Düzenleme Formunu Doldur (populateEditCategoryForm)
         * Kategori düzenleme formunu verilen kategori verileriyle doldurur.
         * @param {object} category - Formu doldurmak için kullanılacak kategori nesnesi.
         */
        populateEditCategoryForm: function (category) {
            if (!DOM.editCategoryForm || !DOM.editCategoryModal) return;
            DOM.editCategoryForm.categoryId.value = category.id;
            DOM.editCategoryForm.editCategoryName.value = category.name;
            const modalInstance = bootstrap.Modal.getInstance(DOM.editCategoryModal) || new bootstrap.Modal(DOM.editCategoryModal);
            modalInstance.show();
        },

        /**
         * 3.4. Olay Dinleyici Ekleyicileri (Action Listener Attachments)
         * ----------------------------------------------------------
         */
        /**
         * 3.4.1. Model Aksiyon Dinleyicileri (attachModelActionListeners)
         * Model aksiyon (düzenle/sil) butonlarına olay dinleyicileri ekler.
         */
        attachModelActionListeners: function () {
            document.querySelectorAll('#models-section .btn-edit-model').forEach(button => {
                button.removeEventListener('click', eventHandlers.handleEditModelShow);
                button.addEventListener('click', eventHandlers.handleEditModelShow);
            });
            document.querySelectorAll('#models-section .btn-delete-model').forEach(button => {
                button.removeEventListener('click', eventHandlers.handleDeleteModel);
                button.addEventListener('click', eventHandlers.handleDeleteModel);
            });
        },
        /**
         * 3.4.2. Kategori Aksiyon Dinleyicileri (attachCategoryActionListeners)
         * Kategori aksiyon (düzenle/sil) butonlarına olay dinleyicileri ekler.
         */
        attachCategoryActionListeners: function () {
            document.querySelectorAll('#categories-section .btn-edit-category').forEach(button => {
                button.removeEventListener('click', eventHandlers.handleEditCategoryShow);
                button.addEventListener('click', eventHandlers.handleEditCategoryShow);
            });
            document.querySelectorAll('#categories-section .btn-delete-category').forEach(button => {
                button.removeEventListener('click', eventHandlers.handleDeleteCategory);
                button.addEventListener('click', eventHandlers.handleDeleteCategory);
            });
        },
        /**
         * 3.4.3. Mesaj Aksiyon Dinleyicileri (attachMessageActionListeners)
         * Mesaj silme butonlarına olay dinleyicileri ekler.
         */
        attachMessageActionListeners: function () {
            document.querySelectorAll('#messages-section .btn-delete-message').forEach(button => {
                button.removeEventListener('click', eventHandlers.handleDeleteMessage);
                button.addEventListener('click', eventHandlers.handleDeleteMessage);
            });
        },

        /**
         * 3.5. Geri Bildirim (showToast)
         * ----------------------------
         * Kullanıcıya geri bildirim göstermek için bir toast mesajı gösterir.
         * @param {string} message - Gösterilecek mesaj.
         * @param {'info' | 'success' | 'error'} type - Mesajın türü.
         */
        showToast: function (message, type = 'info') {
            if (!DOM.toastContainer) {
                DOM.toastContainer = document.createElement('div');
                DOM.toastContainer.id = 'toast-container';
                DOM.toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                DOM.toastContainer.style.zIndex = "1090"; // Bootstrap modal'ın üzerinde olması için
                document.body.appendChild(DOM.toastContainer);
            }

            const toastEl = document.createElement('div');
            toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : (type === 'success' ? 'success' : 'primary')} border-0`;
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
            toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
        }
    };

    //=============================================================================
    // 4. VERİ YÜKLEYİCİLER (DATA LOADERS)
    //=============================================================================
    /**
     * Veri yükleme işlemlerini yöneten fonksiyonlar.
     */
    const dataLoaders = {
        /**
         * 4.1. Modelleri Yükle (loadModels)
         * -------------------------------
         */
        loadModels: async function () {
            try {
                console.log('Modeller yükleniyor...');
                const response = await apiService.getModels();
                
                // Ensure we have a valid array
                const models = Array.isArray(response) ? response : [];
                console.log('Alınan modeller:', models);
                
                // Save to state
                state.models = models;
                
                // Render the models
                ui.renderModels(models);
                
                // Load categories for model forms
                await this.loadCategoriesForModelForms(DOM.modelCategorySelect);
                await this.loadCategoriesForModelForms(DOM.editModelCategorySelect);
                
                // Update dashboard stats if on dashboard
                if (document.getElementById('dashboard-section')?.style.display === 'block') {
                    eventHandlers.updateDashboardStats();
                }
            } catch (error) { 
                console.error('Modeller yüklenirken hata oluştu:', error);
                ui.showToast('Modeller yüklenirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'), 'error');
            }
        },
        /**
         * 4.2. Kategorileri Yükle (loadCategories)
         * --------------------------------------
         */
        loadCategories: async function () {
            try {
                console.log('Kategoriler yükleniyor...');
                const response = await apiService.getCategories();
                
                // Ensure we have a valid array
                const categories = Array.isArray(response) ? response : [];
                console.log('Alınan kategoriler:', categories);
                
                // Save to state
                state.categories = categories;
                
                // Render the categories
                ui.renderCategories(categories);
                
                // Update dashboard stats if on dashboard
                if (document.getElementById('dashboard-section')?.style.display === 'block') {
                    eventHandlers.updateDashboardStats();
                }
            } catch (error) { 
                console.error('Kategoriler yüklenirken hata oluştu:', error);
                ui.showToast('Kategoriler yüklenirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'), 'error');
            }
        },
        /**
         * 4.3. Model Formları İçin Kategorileri Yükle (loadCategoriesForModelForms)
         * ----------------------------------------------------------------------
         * Verilen select elementini kategorilerle doldurur.
         * @param {HTMLSelectElement} selectElement - Doldurulacak select elementi.
         * @param {number|string} [selectedValue] - Opsiyonel olarak seçili olacak değer.
         */
        loadCategoriesForModelForms: async function (selectElement, selectedValue = null) {
            if (!selectElement) return;
            try {
                const categories = await apiService.getCategories();
                selectElement.innerHTML = '<option value="">Kategori Seçin</option>'; // Varsayılan seçenek

                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.id;
                    option.textContent = category.name;
                    if (selectedValue && category.id.toString() === selectedValue.toString()) {
                        option.selected = true;
                    }
                    selectElement.appendChild(option);
                });
            } catch (error) {
                ui.showToast('Model formları için kategoriler yüklenemedi.', 'error');
            }
        },
        /**
         * 4.4. Kullanıcı Mesajlarını Yükle (loadUserMessages)
         * -------------------------------------------------
         */
        loadUserMessages: async function () {
            try {
                const messages = await apiService.getUserMessages();
                ui.renderUserMessages(messages);
            } catch (error) { /* Hata yönetimi */ }
        }
    };

    //=============================================================================
    // 5. OLAY İŞLEYİCİLERİ (EVENT HANDLERS)
    //=============================================================================
    /**
     * Kullanıcı etkileşimlerini yöneten fonksiyonlar.
     */
    const eventHandlers = {
        /**
         * 5.1. Navigasyon Tıklamaları (handleNavClick)
         * ------------------------------------------
         * Navigasyon linklerine tıklanıldığında ilgili bölümü gösterir ve verileri yükler.
         * @param {Event} event - Tıklama olayı.
         */
        handleNavClick: function (event) {
            event.preventDefault();
            const targetLink = event.target.closest('a');
            if (!targetLink) return;
            
            const targetId = targetLink.id;
            if (!targetId) return;

            const sectionId = targetId.split('-')[1]; // 'nav-models' -> 'models'
            ui.showSection(sectionId);

            // İlgili bölüm için veri yükleme
            if (sectionId === 'dashboard') {
                // Dashboard için gerekli verileri yükle
                dataLoaders.loadModels();
                dataLoaders.loadCategories();
                dataLoaders.loadUserMessages();
                
                // Dashboard istatistiklerini güncelle
                this.updateDashboardStats();
            } else if (sectionId === 'models') {
                dataLoaders.loadModels();
            } else if (sectionId === 'categories') {
                dataLoaders.loadCategories();
            } else if (sectionId === 'messages') {
                dataLoaders.loadUserMessages();
            }
        },
        
        /**
         * Dashboard istatistiklerini günceller
         */
        updateDashboardStats: function() {
            // Kategori sayısını güncelle
            const categoryCount = document.getElementById('categoryCount');
            if (categoryCount) {
                categoryCount.textContent = state.categories ? state.categories.length : 0;
            }
            
            // Model sayısını güncelle
            const modelCount = document.getElementById('modelCount');
            if (modelCount) {
                modelCount.textContent = state.models ? state.models.length : 0;
            }
        },

        /**
         * 5.2. Model İşlemleri
         * --------------------
         */
        /** 5.2.1. Model Ekle (handleAddModel) */
        handleAddModel: async function (event) {
            event.preventDefault();
            if (!DOM.addModelForm) return;
            const formData = new FormData(DOM.addModelForm);
            const data = {
                name: formData.get('modelName'),
                api_key: formData.get('modelApiKey'),
                base_url: formData.get('modelBaseUrl'),
                description: formData.get('modelDescription'),
                category_id: parseInt(formData.get('modelCategory')),
            };
            try {
                await apiService.addModel(data);
                ui.showToast('Model başarıyla eklendi!', 'success');
                DOM.addModelForm.reset();
                dataLoaders.loadModels(); // Listeyi yenile
            } catch (error) { /* Hata zaten apiService ve showToast tarafından yönetiliyor */ }
        },

        /** 5.2.2. Model Düzenleme Formunu Göster (handleEditModelShow) */
        handleEditModelShow: async function (event) {
            const modelId = event.target.dataset.id;
            try {
                // Tüm modelleri yeniden çekmek yerine, eğer state'de tutuluyorsa oradan alınabilir.
                // Ancak bu örnekte API'den çekiliyor.
                const models = await apiService.getModels();
                const model = models.find(m => m.id.toString() === modelId);
                if (model) {
                    // Düzenleme formu için kategorileri yükle ve seçili olanı ayarla
                    await dataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect, model.category_id);
                    ui.populateEditModelForm(model);
                } else {
                    ui.showToast(`Model ID ${modelId} bulunamadı.`, 'error');
                }
            } catch (error) {
                ui.showToast(`Model detayları getirilirken hata: ${error.message}`, 'error');
            }
        },

        /** 5.2.3. Model Güncelle (handleUpdateModel) */
        handleUpdateModel: async function (event) {
            event.preventDefault();
            if (!DOM.editModelForm) return;
            const modelId = DOM.editModelForm.modelId.value;
            const formData = new FormData(DOM.editModelForm);
            const data = {
                name: formData.get('editModelName'),
                api_key: formData.get('editModelApiKey'),
                base_url: formData.get('editModelBaseUrl'),
                description: formData.get('editModelDescription'),
                category_id: parseInt(formData.get('editModelCategory')),
            };
            try {
                await apiService.updateModel(modelId, data);
                ui.showToast('Model başarıyla güncellendi!', 'success');
                const modalInstance = bootstrap.Modal.getInstance(DOM.editModelModal);
                if (modalInstance) modalInstance.hide();
                dataLoaders.loadModels(); // Listeyi yenile
            } catch (error) { /* Hata yönetimi */ }
        },

        /** 5.2.4. Model Sil (handleDeleteModel) */
        handleDeleteModel: async function (event) {
            const modelId = event.target.dataset.id;
            if (confirm('Bu modeli silmek istediğinizden emin misiniz?')) {
                try {
                    await apiService.deleteModel(modelId);
                    ui.showToast('Model başarıyla silindi!', 'success');
                    dataLoaders.loadModels(); // Listeyi yenile
                } catch (error) { /* Hata yönetimi */ }
            }
        },

        /**
         * 5.3. Kategori İşlemleri
         * -----------------------
         */
        /** 5.3.1. Kategori Ekle (handleAddCategory) */
        handleAddCategory: async function (event) {
            event.preventDefault();
            if (!DOM.addCategoryForm) return;
            const formData = new FormData(DOM.addCategoryForm);
            const data = { name: formData.get('categoryName') };
            try {
                await apiService.addCategory(data);
                ui.showToast('Kategori başarıyla eklendi!', 'success');
                DOM.addCategoryForm.reset();
                dataLoaders.loadCategories(); // Listeyi yenile
                // Model formlarındaki kategori dropdown'larını da güncelle
                dataLoaders.loadCategoriesForModelForms(DOM.modelCategorySelect);
                dataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect);
            } catch (error) { /* Hata yönetimi */ }
        },

        /** 5.3.2. Kategori Düzenleme Formunu Göster (handleEditCategoryShow) */
        handleEditCategoryShow: async function (event) {
            const categoryId = event.target.dataset.id;
            // const categoryName = event.target.dataset.name; // data-name üzerinden de alınabilir veya API'den çekilebilir
            try {
                const categories = await apiService.getCategories();
                const category = categories.find(c => c.id.toString() === categoryId);
                if (category) {
                    ui.populateEditCategoryForm(category);
                } else {
                    ui.showToast(`Kategori ID ${categoryId} bulunamadı.`, 'error');
                }
            } catch (error) {
                ui.showToast(`Kategori detayları getirilirken hata: ${error.message}`, 'error');
            }
        },

        /** 5.3.3. Kategori Güncelle (handleUpdateCategory) */
        handleUpdateCategory: async function (event) {
            event.preventDefault();
            if (!DOM.editCategoryForm) return;
            const categoryId = DOM.editCategoryForm.categoryId.value;
            const formData = new FormData(DOM.editCategoryForm);
            const data = { name: formData.get('editCategoryName') };
            try {
                await apiService.updateCategory(categoryId, data);
                ui.showToast('Kategori başarıyla güncellendi!', 'success');
                const modalInstance = bootstrap.Modal.getInstance(DOM.editCategoryModal);
                if (modalInstance) modalInstance.hide();
                dataLoaders.loadCategories(); // Listeyi yenile
                dataLoaders.loadCategoriesForModelForms(DOM.modelCategorySelect);
                dataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect);
            } catch (error) { /* Hata yönetimi */ }
        },

        /** 5.3.4. Kategori Sil (handleDeleteCategory) */
        handleDeleteCategory: async function (event) {
            const categoryId = event.target.dataset.id;
            if (confirm('Bu kategoriyi silmek istediğinizden emin misiniz? Bu kategoriyi kullanan modeller etkilenebilir.')) {
                try {
                    await apiService.deleteCategory(categoryId);
                    ui.showToast('Kategori başarıyla silindi!', 'success');
                    dataLoaders.loadCategories(); // Listeyi yenile
                    dataLoaders.loadCategoriesForModelForms(DOM.modelCategorySelect);
                    dataLoaders.loadCategoriesForModelForms(DOM.editModelCategorySelect);
                    dataLoaders.loadModels(); // Kategorisi silinen modelleri de güncellemek için
                } catch (error) { /* Hata yönetimi */ }
            }
        },

        /**
         * 5.4. Mesaj İşlemleri
         * --------------------
         */
        /** 5.4.1. Mesaj Sil (handleDeleteMessage) */
        handleDeleteMessage: async function (event) {
            const messageId = event.target.dataset.id;
            if (confirm('Bu mesajı silmek istediğinizden emin misiniz?')) {
                try {
                    await apiService.deleteUserMessage(messageId);
                    ui.showToast('Mesaj başarıyla silindi!', 'success');
                    dataLoaders.loadUserMessages(); // Listeyi yenile
                } catch (error) { /* Hata yönetimi */ }
            }
        }
    };

    //=============================================================================
    // 6. BAŞLATMA (INITIALIZATION)
    //=============================================================================

    /**
     * 6.1. Başlatma Fonksiyonu (init)
     * ------------------------------
     * Uygulama başladığında çalışacak ilk fonksiyon.
     */
    function init() {
        // Navigasyon olay dinleyicilerini ekle
        Object.values(DOM.navLinks).forEach(link => {
            if (link) link.addEventListener('click', eventHandlers.handleNavClick);
        });

        // Form gönderme olay dinleyicilerini ekle
        if (DOM.addModelForm) DOM.addModelForm.addEventListener('submit', eventHandlers.handleAddModel);
        if (DOM.editModelForm) DOM.editModelForm.addEventListener('submit', eventHandlers.handleUpdateModel);
        if (DOM.addCategoryForm) DOM.addCategoryForm.addEventListener('submit', eventHandlers.handleAddCategory);
        if (DOM.editCategoryForm) DOM.editCategoryForm.addEventListener('submit', eventHandlers.handleUpdateCategory);

        // Başlangıç bölümünü göster ve verilerini yükle
        const initialSection = window.location.hash ? window.location.hash.substring(1) : 'dashboard';
        const validSections = ['dashboard', 'models', 'categories', 'users', 'settings', 'messages'];

        // Sayfa yüklendiğinde dashboard'u göster ve verileri yükle
        document.addEventListener('DOMContentLoaded', function() {
            // Dashboard'u göster
            ui.showSection('dashboard');
            
            // Tüm verileri yükle
            dataLoaders.loadModels();
            dataLoaders.loadCategories();
            dataLoaders.loadUserMessages();
            
            // Dashboard istatistiklerini güncelle
            eventHandlers.updateDashboardStats();
            
            // Navigasyon linklerine tıklama olaylarını ekle
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', eventHandlers.handleNavClick);
            });
        });
    }

    /**
     * 6.2. DOM Hazır Olduğunda Başlatma
     * ---------------------------------
     * DOM tamamen yüklendikten sonra init fonksiyonunu çalıştır.
     */
    document.addEventListener('DOMContentLoaded', init);

})();