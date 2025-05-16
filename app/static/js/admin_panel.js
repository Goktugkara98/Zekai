
        /**
         * Zekai Admin Panel JavaScript
         *
         * This file contains all the client-side functionality for the admin panel,
         * including AJAX calls, form handling, and UI interactions.
         */

        document.addEventListener('DOMContentLoaded', function() {
            // Initialize the admin panel
            initAdminPanel();
        });

        /**
         * Initialize the admin panel components and load data
         */
        function initAdminPanel() {
            // Load data for dashboard
            loadDashboardData();

            // Load categories and models
            loadCategories();
            loadModels();

            // Load available icons for dropdowns
            loadIconOptions();

            // Set up event listeners
            setupEventListeners();

            // Set up navigation
            setupNavigation();
        }

        /**
         * Load dashboard data (category and model counts)
         */
        function loadDashboardData() {
            // Fetch category count
            // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
            fetch('/admin/api/categories/count')
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        document.getElementById('categoryCount').textContent = data.count;
                    } else {
                        console.warn('API success false for category count:', data.message);
                        // document.getElementById('categoryCount').textContent = 'N/A';
                    }
                })
                .catch(error => {
                    console.error('Error fetching category count:', error);
                    // document.getElementById('categoryCount').textContent = 'Hata';
                });

            // Fetch model count
            // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
            fetch('/admin/api/models/count')
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
                    return response.json();
                 })
                .then(data => {
                    if (data.success) {
                        document.getElementById('modelCount').textContent = data.count;
                    } else {
                         console.warn('API success false for model count:', data.message);
                        // document.getElementById('modelCount').textContent = 'N/A';
                    }
                })
                .catch(error => {
                    console.error('Error fetching model count:', error);
                    // document.getElementById('modelCount').textContent = 'Hata';
                });
        }

        /**
         * Load categories for the categories table and dropdowns
         */
        function loadCategories() {
            // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
            fetch('/admin/api/categories')
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateCategoriesTable(data.categories);
                        populateCategoryDropdowns(data.categories);
                    } else {
                        showAlert('error', data.error || 'Kategoriler yüklenemedi');
                    }
                })
                .catch(error => {
                    console.error('Error fetching categories:', error);
                    showAlert('error', 'Kategoriler yüklenemedi. Lütfen tekrar deneyin.');
                });
        }

        /**
         * Load models for the models table
         */
        function loadModels() {
            // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
            fetch('/admin/api/models')
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateModelsTable(data.models);
                    } else {
                        showAlert('error', data.error || 'Modeller yüklenemedi');
                    }
                })
                .catch(error => {
                    console.error('Error fetching models:', error);
                    showAlert('error', 'Modeller yüklenemedi. Lütfen tekrar deneyin.');
                });
        }

        /**
         * Load available icons for icon dropdowns
         * Bu fonksiyon backend'den Bootstrap Icons sınıflarını çekmelidir.
         * Örnek olarak statik bir liste kullanılmıştır.
         */
        function loadIconOptions() {
            fetch('/admin/api/icons')
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
                    return response.json();
                })
                .then(data => {
                    if (data.success && data.icons) {
                        populateIconDropdowns(data.icons);
                    } else {
                        console.error('Failed to load icons from API');
                        showAlert('error', 'İkonlar yüklenemedi');
                    }
                })
                .catch(error => {
                    console.error('Error fetching icons:', error);
                    showAlert('error', 'İkonlar yüklenemedi. Lütfen tekrar deneyin.');
                });
        }


        /**
         * Set up navigation between sections
         */
        function setupNavigation() {
            const navLinks = document.querySelectorAll('.nav-link');
            const contentSections = document.querySelectorAll('.content-section');

            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    // Hide all sections
                    contentSections.forEach(section => {
                        section.classList.remove('active');
                    });

                    // Show the target section
                    const targetSectionId = this.id.replace('nav-', '') + '-section';
                    const targetSection = document.getElementById(targetSectionId);
                    if (targetSection) {
                        targetSection.classList.add('active');
                    }


                    // Update active nav link
                    navLinks.forEach(nav => nav.classList.remove('active'));
                    this.classList.add('active');
                });
            });

             // Quick action buttons
            document.getElementById('quick-add-category').addEventListener('click', function() {
                showSection('categories'); // Kategoriler bölümünü göster
                const addCategoryModal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
                addCategoryModal.show();
            });

            document.getElementById('quick-add-model').addEventListener('click', function() {
                showSection('models'); // Modeller bölümünü göster
                const addModelModal = new bootstrap.Modal(document.getElementById('addModelModal'));
                addModelModal.show();
            });
        }

        /**
        * Show a specific section and hide others
        * @param {string} sectionName - The name of the section to show (dashboard, categories, models)
        */
        function showSection(sectionName) {
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });

            // Show the selected section
            const sectionToShow = document.getElementById(sectionName + '-section');
            if (sectionToShow) {
                 sectionToShow.classList.add('active');
            }


            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            const activeNavLink = document.getElementById('nav-' + sectionName);
            if (activeNavLink) {
                activeNavLink.classList.add('active');
            }
        }


        /**
         * Set up all event listeners for the admin panel
         */
        function setupEventListeners() {
            setupCategoryFormEvents();
            setupModelFormEvents();
            setupIconPreviewEvents();
            setupDeleteConfirmationEvents();

            // Logout button
            document.getElementById('logoutBtn').addEventListener('click', function() {
                 // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
                fetch('/admin/api/admin/logout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('success', 'Başarıyla çıkış yapıldı. Yönlendiriliyorsunuz...');
                        setTimeout(() => { window.location.href = '/login'; }, 1500); // Giriş sayfasına yönlendir
                    } else {
                        showAlert('error', data.error || 'Çıkış yapılamadı.');
                    }
                })
                .catch(error => {
                    console.error('Error logging out:', error);
                    showAlert('error', 'Çıkış sırasında bir hata oluştu.');
                });
            });
        }

        /**
         * Set up event listeners for category forms
         */
        function setupCategoryFormEvents() {
            // Add Category form
            document.getElementById('saveCategoryBtn').addEventListener('click', function() {
                const categoryName = document.getElementById('categoryName').value.trim();
                const categoryIcon = document.getElementById('categoryIcon').value;

                if (!categoryName) {
                    showAlert('error', 'Kategori adı gereklidir');
                    return;
                }

                const categoryData = { name: categoryName, icon: categoryIcon };
                // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
                fetch('/admin/api/categories', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(categoryData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.category_id) {
                        showAlert('success', data.message || 'Kategori başarıyla oluşturuldu');
                        document.getElementById('addCategoryForm').reset();
                        bootstrap.Modal.getInstance(document.getElementById('addCategoryModal')).hide();
                        loadCategories();
                        loadDashboardData();
                    } else {
                        showAlert('error', data.error || 'Kategori oluşturulamadı');
                    }
                })
                .catch(error => {
                    console.error('Error creating category:', error);
                    showAlert('error', 'Kategori oluşturulamadı. Lütfen tekrar deneyin.');
                });
            });

            // Edit Category form
            document.getElementById('updateCategoryBtn').addEventListener('click', function() {
                const categoryId = document.getElementById('editCategoryId').value;
                const categoryName = document.getElementById('editCategoryName').value.trim();
                const categoryIcon = document.getElementById('editCategoryIcon').value;

                if (!categoryName) {
                    showAlert('error', 'Kategori adı gereklidir');
                    return;
                }

                const categoryData = { id: parseInt(categoryId), name: categoryName, icon: categoryIcon };
                // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
                fetch(`/admin/api/categories/${categoryId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(categoryData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('success', data.message || 'Kategori başarıyla güncellendi');
                        bootstrap.Modal.getInstance(document.getElementById('editCategoryModal')).hide();
                        loadCategories();
                    } else {
                        showAlert('error', data.error || 'Kategori güncellenemedi');
                    }
                })
                .catch(error => {
                    console.error('Error updating category:', error);
                    showAlert('error', 'Kategori güncellenemedi. Lütfen tekrar deneyin.');
                });
            });
        }

        /**
         * Set up event listeners for model forms
         */
        function setupModelFormEvents() {
            // Add Model form
            document.getElementById('saveModelBtn').addEventListener('click', function() {
                const categoryId = document.getElementById('modelCategory').value;
                const modelName = document.getElementById('modelName').value.trim();
                const modelIcon = document.getElementById('modelIcon').value;
                const dataAiIndex = document.getElementById('modelDataAiIndex').value.trim();
                const apiUrl = document.getElementById('modelApiUrl').value.trim();
                const requestMethod = document.getElementById('modelRequestMethod').value;
                const requestHeaders = document.getElementById('modelRequestHeaders').value.trim();
                const requestBodyTemplate = document.getElementById('modelRequestBody').value.trim();
                const responsePath = document.getElementById('modelResponsePath').value.trim();

                if (!validateModelForm(modelName, dataAiIndex, apiUrl, requestHeaders, requestBodyTemplate)) {
                    return;
                }

                const modelData = {
                    category_id: parseInt(categoryId),
                    name: modelName,
                    icon: modelIcon,
                    api_url: apiUrl,
                    data_ai_index: dataAiIndex, // Ayrı bir alan olarak
                    description: modelName, // Veya formdan ayrı bir açıklama alanı
                    request_method: requestMethod, // Ayrı bir alan olarak
                    request_headers: requestHeaders, // Ayrı bir alan olarak
                    request_body_template: requestBodyTemplate, // Ayrı bir alan olarak
                    response_path: responsePath, // Ayrı bir alan olarak
                    details: { /* İleride eklenebilecek diğer tüm ekstra bilgiler için burası kullanılabilir */ } 
                };
                
                // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
                fetch('/admin/api/models', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(modelData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('success', data.message || 'Model başarıyla oluşturuldu');
                        document.getElementById('addModelForm').reset();
                        bootstrap.Modal.getInstance(document.getElementById('addModelModal')).hide();
                        loadModels();
                        loadDashboardData();
                    } else {
                        showAlert('error', data.error || 'Model oluşturulamadı');
                    }
                })
                .catch(error => {
                    console.error('Error creating model:', error);
                    showAlert('error', 'Model oluşturulamadı. Lütfen tekrar deneyin.');
                });
            });

            // Edit Model form
            document.getElementById('updateModelBtn').addEventListener('click', function() {
                const modelId = document.getElementById('editModelId').value;
                const categoryId = document.getElementById('editModelCategory').value;
                const modelName = document.getElementById('editModelName').value.trim();
                const modelIcon = document.getElementById('editModelIcon').value;
                const dataAiIndex = document.getElementById('editModelDataAiIndex').value.trim();
                const apiUrl = document.getElementById('editModelApiUrl').value.trim();
                const requestMethod = document.getElementById('editModelRequestMethod').value;
                const requestHeaders = document.getElementById('editModelRequestHeaders').value.trim();
                const requestBodyTemplate = document.getElementById('editModelRequestBody').value.trim();
                const responsePath = document.getElementById('editModelResponsePath').value.trim();

                if (!validateModelForm(modelName, dataAiIndex, apiUrl, requestHeaders, requestBodyTemplate)) {
                    return;
                }

                const modelData = {
                    id: parseInt(modelId),
                    category_id: parseInt(categoryId),
                    name: modelName,
                    icon: modelIcon,
                    api_url: apiUrl,
                    description: modelName,
                    details: {
                        data_ai_index: dataAiIndex,
                        request_method: requestMethod,
                        request_headers: requestHeaders,
                        request_body_template: requestBodyTemplate,
                        response_path: responsePath
                    }
                };
                // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
                fetch(`/admin/api/models/${modelId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(modelData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('success', data.message || 'Model başarıyla güncellendi');
                        bootstrap.Modal.getInstance(document.getElementById('editModelModal')).hide();
                        loadModels();
                    } else {
                        showAlert('error', data.error || 'Model güncellenemedi');
                    }
                })
                .catch(error => {
                    console.error('Error updating model:', error);
                    showAlert('error', 'Model güncellenemedi. Lütfen tekrar deneyin.');
                });
            });
        }

        /**
         * Set up icon preview events for dropdowns
         */
        function setupIconPreviewEvents() {
            const iconPreviews = [
                { select: 'categoryIcon', preview: 'iconPreview', defaultClass: 'bi-folder' },
                { select: 'editCategoryIcon', preview: 'editIconPreview', defaultClass: 'bi-folder' },
                { select: 'modelIcon', preview: 'modelIconPreview', defaultClass: 'bi-robot' },
                { select: 'editModelIcon', preview: 'editModelIconPreview', defaultClass: 'bi-robot' }
            ];

            iconPreviews.forEach(({ select, preview, defaultClass }) => {
                const selectElement = document.getElementById(select);
                const previewElement = document.getElementById(preview);

                if (selectElement && previewElement) {
                    // Initial preview
                    previewElement.className = 'bi ' + (selectElement.value || defaultClass);

                    // Update preview on change
                    selectElement.addEventListener('change', function() {
                        previewElement.className = 'bi ' + (this.value || defaultClass);
                    });
                }
            });
        }


        /**
         * Set up delete confirmation modal events
         */
        function setupDeleteConfirmationEvents() {
            const deleteConfirmModalElement = document.getElementById('deleteConfirmModal');
            if (!deleteConfirmModalElement) return;

            const deleteConfirmModal = new bootstrap.Modal(deleteConfirmModalElement);
            const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

            deleteConfirmModalElement.addEventListener('show.bs.modal', function(event) {
                const button = event.relatedTarget;
                const itemType = button.getAttribute('data-type');
                const itemId = button.getAttribute('data-id');
                const itemName = button.getAttribute('data-name');

                document.getElementById('deleteConfirmMessage').textContent =
                    `"${itemName}" isimli ${itemType === 'category' ? 'kategoriyi' : 'modeli'} silmek istediğinizden emin misiniz?`;

                confirmDeleteBtn.setAttribute('data-type', itemType);
                confirmDeleteBtn.setAttribute('data-id', itemId);
            });

            confirmDeleteBtn.addEventListener('click', function() {
                const itemType = this.getAttribute('data-type');
                const itemId = this.getAttribute('data-id');

                if (itemType === 'category') {
                    deleteCategory(itemId);
                } else if (itemType === 'model') {
                    deleteModel(itemId);
                }
            });
        }

        /**
         * Delete a category
         * @param {string} categoryId - The ID of the category to delete
         */
        function deleteCategory(categoryId) {
            // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
            fetch(`/admin/api/categories/${categoryId}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', data.message || 'Kategori başarıyla silindi');
                    bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
                    loadCategories();
                    loadModels(); // Kategori silindiğinde modeller de etkilenebilir
                    loadDashboardData();
                } else {
                    showAlert('error', data.error || 'Kategori silinemedi');
                }
            })
            .catch(error => {
                console.error('Error deleting category:', error);
                showAlert('error', 'Kategori silinemedi. Lütfen tekrar deneyin.');
            });
        }

        /**
         * Delete a model
         * @param {string} modelId - The ID of the model to delete
         */
        function deleteModel(modelId) {
             // GERÇEK API Entegrasyonu: Aşağıdaki URL'yi kendi backend API'nizle değiştirin
            fetch(`/admin/api/models/${modelId}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', data.message || 'Model başarıyla silindi');
                    bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
                    loadModels();
                    loadDashboardData();
                } else {
                    showAlert('error', data.error || 'Model silinemedi');
                }
            })
            .catch(error => {
                console.error('Error deleting model:', error);
                showAlert('error', 'Model silinemedi. Lütfen tekrar deneyin.');
            });
        }

        /**
         * Populate the categories table with data
         * @param {Array} categories - The categories data
         */
        function populateCategoriesTable(categories) {
            const tableBody = document.getElementById('categoriesTableBody');
            tableBody.innerHTML = ''; // Clear previous rows

            if (!categories || categories.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center">Kategori bulunamadı</td></tr>`;
                return;
            }

            categories.forEach(category => {
                const row = tableBody.insertRow();
                row.innerHTML = `
                    <td>${category.id}</td>
                    <td><i class="bi ${category.icon || 'bi-folder'}"></i></td>
                    <td>${category.name}</td>
                    <td>${category.model_count || 0}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-sm btn-primary edit-category-btn"
                                    data-id="${category.id}"
                                    data-name="${category.name}"
                                    data-icon="${category.icon}">
                                <i class="bi bi-pencil"></i> Düzenle
                            </button>
                            <button class="btn btn-sm btn-danger"
                                    data-bs-toggle="modal"
                                    data-bs-target="#deleteConfirmModal"
                                    data-type="category"
                                    data-id="${category.id}"
                                    data-name="${category.name}">
                                <i class="bi bi-trash"></i> Sil
                            </button>
                        </div>
                    </td>
                `;
            });

            // Add event listeners to edit buttons
            document.querySelectorAll('.edit-category-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const categoryId = this.getAttribute('data-id');
                    const categoryName = this.getAttribute('data-name');
                    const categoryIcon = this.getAttribute('data-icon');

                    document.getElementById('editCategoryId').value = categoryId;
                    document.getElementById('editCategoryName').value = categoryName;
                    document.getElementById('editCategoryIcon').value = categoryIcon;

                    const previewElement = document.getElementById('editIconPreview');
                    if (previewElement) previewElement.className = 'bi ' + (categoryIcon || 'bi-folder');


                    const editModal = new bootstrap.Modal(document.getElementById('editCategoryModal'));
                    editModal.show();
                });
            });
        }

        /**
         * Populate the models table with data
         * @param {Array} models - The models data
         */
        function populateModelsTable(models) {
            const tableBody = document.getElementById('modelsTableBody');
            tableBody.innerHTML = ''; // Clear previous rows

            if (!models || models.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="7" class="text-center">Model bulunamadı</td></tr>`;
                return;
            }

            models.forEach(model => {
                const row = tableBody.insertRow();
                row.innerHTML = `
                    <td>${model.id}</td>
                    <td><i class="bi ${model.icon || 'bi-robot'}"></i></td>
                    <td>${model.name}</td>
                    <td>${model.category_name || 'N/A'}</td>
                    <td>${model.data_ai_index}</td>
                    <td>
                        <div class="text-truncate" style="max-width: 150px;" title="${model.api_url}">
                            ${model.api_url}
                        </div>
                    </td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-sm btn-primary edit-model-btn"
                                    data-id="${model.id}"
                                    data-category="${model.category_id}"
                                    data-name="${model.name}"
                                    data-icon="${model.icon}"
                                    data-ai-index="${model.data_ai_index}"
                                    data-api-url="${model.api_url}"
                                    data-request-method="${model.request_method || 'POST'}"
                                    data-request-headers='${model.request_headers || '{"Content-Type": "application/json"}'}'
                                    data-request-body='${model.request_body_template || '{"contents": [{"parts":[{"text": "$message"}]}]}'}'
                                    data-response-path="${model.response_path || 'candidates[0].content.parts[0].text'}">
                                <i class="bi bi-pencil"></i> Düzenle
                            </button>
                            <button class="btn btn-sm btn-danger"
                                    data-bs-toggle="modal"
                                    data-bs-target="#deleteConfirmModal"
                                    data-type="model"
                                    data-id="${model.id}"
                                    data-name="${model.name}">
                                <i class="bi bi-trash"></i> Sil
                            </button>
                        </div>
                    </td>
                `;
            });

            // Add event listeners to edit buttons
            document.querySelectorAll('.edit-model-btn').forEach(button => {
                button.addEventListener('click', function() {
                    document.getElementById('editModelId').value = this.getAttribute('data-id');
                    document.getElementById('editModelCategory').value = this.getAttribute('data-category');
                    document.getElementById('editModelName').value = this.getAttribute('data-name');
                    document.getElementById('editModelIcon').value = this.getAttribute('data-icon');
                    document.getElementById('editModelDataAiIndex').value = this.getAttribute('data-ai-index');
                    document.getElementById('editModelApiUrl').value = this.getAttribute('data-api-url');
                    document.getElementById('editModelRequestMethod').value = this.getAttribute('data-request-method');
                    document.getElementById('editModelRequestHeaders').value = this.getAttribute('data-request-headers');
                    document.getElementById('editModelRequestBody').value = this.getAttribute('data-request-body');
                    document.getElementById('editModelResponsePath').value = this.getAttribute('data-response-path');

                    const previewElement = document.getElementById('editModelIconPreview');
                     if (previewElement) previewElement.className = 'bi ' + (this.getAttribute('data-icon') || 'bi-robot');


                    const editModal = new bootstrap.Modal(document.getElementById('editModelModal'));
                    editModal.show();
                });
            });
        }


        /**
         * Populate category dropdowns for model forms
         * @param {Array} categories - The categories data
         */
        function populateCategoryDropdowns(categories) {
            const dropdowns = [
                document.getElementById('modelCategory'),
                document.getElementById('editModelCategory')
            ];

            dropdowns.forEach(dropdown => {
                if (!dropdown) return;
                const currentValue = dropdown.value; // Preserve selected value if any
                dropdown.innerHTML = ''; // Clear previous options

                if (!categories || categories.length === 0) {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'Kategori bulunamadı';
                    option.disabled = true;
                    option.selected = true;
                    dropdown.appendChild(option);
                    return;
                }
                 const defaultOption = document.createElement('option');
                 defaultOption.value = "";
                 defaultOption.textContent = "Bir kategori seçin";
                 defaultOption.disabled = true;
                 defaultOption.selected = !currentValue; // Select if no current value
                 dropdown.appendChild(defaultOption);


                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.id;
                    option.textContent = category.name;
                    dropdown.appendChild(option);
                });
                if (currentValue) dropdown.value = currentValue; // Restore selected value
            });
        }

        /**
         * Populate icon dropdowns
         * @param {Array} icons - The icons data (array of objects with 'name' and 'class' properties)
         */
        function populateIconDropdowns(icons) {
            const dropdownsInfo = [
                { id: 'categoryIcon', preview: 'iconPreview', defaultClass: 'bi-folder' },
                { id: 'editCategoryIcon', preview: 'editIconPreview', defaultClass: 'bi-folder' },
                { id: 'modelIcon', preview: 'modelIconPreview', defaultClass: 'bi-robot' },
                { id: 'editModelIcon', preview: 'editModelIconPreview', defaultClass: 'bi-robot' }
            ];

            dropdownsInfo.forEach(({ id, preview, defaultClass }) => {
                const dropdown = document.getElementById(id);
                const previewElement = document.getElementById(preview);

                if (dropdown) {
                    const currentValue = dropdown.value;
                    dropdown.innerHTML = ''; // Clear existing options

                    // Add default "Select an icon" option
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = 'Bir ikon seçin';
                    dropdown.appendChild(defaultOption);

                    // Add icon options from the provided list
                    if (icons && icons.length > 0) {
                        icons.forEach(icon => {
                            const option = document.createElement('option');
                            option.value = icon.class; // e.g., "bi-folder"
                            option.textContent = icon.name; // e.g., "Klasör"
                            dropdown.appendChild(option);
                        });
                    }


                    // Restore previous value if it exists
                    if (currentValue) {
                        dropdown.value = currentValue;
                    }

                    // Update preview
                    if (previewElement) {
                        previewElement.className = 'bi ' + (dropdown.value || defaultClass);
                    }
                }
            });
        }


        /**
         * Validate model form inputs
         * @param {string} name - The model name
         * @param {string} dataAiIndex - The data-ai-index value
         * @param {string} apiUrl - The API URL
         * @param {string} requestHeaders - The request headers JSON
         * @param {string} requestBodyTemplate - The request body template JSON
         * @returns {boolean} - Whether the form is valid
         */
        function validateModelForm(name, dataAiIndex, apiUrl, requestHeaders, requestBodyTemplate) {
            if (!name) {
                showAlert('error', 'Model adı gereklidir');
                return false;
            }
            if (!dataAiIndex) {
                showAlert('error', 'Data AI Index gereklidir');
                return false;
            }
            // Validate data_ai_index format (alphanumeric, underscore, hyphen)
            if (!/^[a-zA-Z0-9_-]+$/.test(dataAiIndex)) {
                showAlert('error', 'Data AI Index sadece harf, rakam, alt çizgi ve tire içerebilir');
                return false;
            }
            if (!apiUrl) {
                showAlert('error', 'API URL gereklidir');
                return false;
            }
            if (requestHeaders) {
                try { JSON.parse(requestHeaders); }
                catch (e) { showAlert('error', 'İstek Başlıkları geçerli JSON formatında olmalıdır'); return false; }
            }
            if (requestBodyTemplate) {
                try { JSON.parse(requestBodyTemplate); }
                catch (e) { showAlert('error', 'İstek Gövdesi Şablonu geçerli JSON formatında olmalıdır'); return false; }

                if (!requestBodyTemplate.includes('$message')) {
                    showAlert('warning', 'İstek Gövdesi Şablonu $message yer tutucusunu içermelidir');
                }
            }
            return true;
        }

        /**
         * Show an alert message
         * @param {string} type - The type of alert ('success', 'error', 'warning', 'info')
         * @param {string} message - The message to display
         */
        function showAlert(type, message) {
            const alertContainer = document.getElementById('alertContainer');
            if (!alertContainer) return;

            const alertClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            }[type] || 'alert-info';

            const icon = {
                'success': 'bi-check-circle-fill',
                'error': 'bi-x-octagon-fill',
                'warning': 'bi-exclamation-triangle-fill',
                'info': 'bi-info-circle-fill'
            }[type] || 'bi-info-circle-fill';

            const alertElement = document.createElement('div');
            alertElement.className = `alert ${alertClass} alert-dismissible fade show d-flex align-items-center`;
            alertElement.setAttribute('role', 'alert');
            alertElement.innerHTML = `
                <i class="bi ${icon} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            alertContainer.appendChild(alertElement);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertElement);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 5000);
        }