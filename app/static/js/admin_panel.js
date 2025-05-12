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
    fetch('/admin/api/categories/count')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('categoryCount').textContent = data.count;
            }
        })
        .catch(error => {
            console.error('Error fetching category count:', error);
        });
    
    // Fetch model count
    fetch('/admin/api/models/count')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('modelCount').textContent = data.count;
            }
        })
        .catch(error => {
            console.error('Error fetching model count:', error);
        });
}

/**
 * Load categories for the categories table and dropdowns
 */
function loadCategories() {
    fetch('/admin/api/categories')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate categories table
                populateCategoriesTable(data.categories);
                
                // Populate category dropdowns for model forms
                populateCategoryDropdowns(data.categories);
            } else {
                showAlert('error', data.error || 'Failed to load categories');
            }
        })
        .catch(error => {
            console.error('Error fetching categories:', error);
            showAlert('error', 'Failed to load categories. Please try again.');
        });
}

/**
 * Load models for the models table
 */
function loadModels() {
    fetch('/admin/api/models')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateModelsTable(data.models);
            } else {
                showAlert('error', data.error || 'Failed to load models');
            }
        })
        .catch(error => {
            console.error('Error fetching models:', error);
            showAlert('error', 'Failed to load models. Please try again.');
        });
}

/**
 * Load available icons for icon dropdowns
 */
function loadIconOptions() {
    fetch('/admin/api/icons')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateIconDropdowns(data.icons);
            }
        })
        .catch(error => {
            console.error('Error fetching icons:', error);
        });
}

/**
 * Set up navigation between sections
 */
function setupNavigation() {
    // Dashboard nav link
    document.getElementById('nav-dashboard').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('dashboard');
    });
    
    // Categories nav link
    document.getElementById('nav-categories').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('categories');
    });
    
    // Models nav link
    document.getElementById('nav-models').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('models');
    });
    
    // Quick action buttons
    document.getElementById('quick-add-category').addEventListener('click', function() {
        showSection('categories');
        const addCategoryModal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
        addCategoryModal.show();
    });
    
    document.getElementById('quick-add-model').addEventListener('click', function() {
        showSection('models');
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
        section.style.display = 'none';
    });
    
    // Show the selected section
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.getElementById('nav-' + sectionName).classList.add('active');
}

/**
 * Set up all event listeners for the admin panel
 */
function setupEventListeners() {
    // Category form events
    setupCategoryFormEvents();
    
    // Model form events
    setupModelFormEvents();
    
    // Icon preview events
    setupIconPreviewEvents();
    
    // Delete confirmation events
    setupDeleteConfirmationEvents();
    
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', function() {
        fetch('/admin/api/admin/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('Error logging out:', error);
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
            showAlert('error', 'Category name is required');
            return;
        }
        
        const categoryData = {
            name: categoryName,
            icon: categoryIcon
        };
        
        fetch('/admin/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(categoryData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message || 'Category created successfully');
                document.getElementById('addCategoryForm').reset();
                bootstrap.Modal.getInstance(document.getElementById('addCategoryModal')).hide();
                loadCategories();
                loadDashboardData();
            } else {
                showAlert('error', data.error || 'Failed to create category');
            }
        })
        .catch(error => {
            console.error('Error creating category:', error);
            showAlert('error', 'Failed to create category. Please try again.');
        });
    });
    
    // Edit Category form
    document.getElementById('updateCategoryBtn').addEventListener('click', function() {
        const categoryId = document.getElementById('editCategoryId').value;
        const categoryName = document.getElementById('editCategoryName').value.trim();
        const categoryIcon = document.getElementById('editCategoryIcon').value;
        
        if (!categoryName) {
            showAlert('error', 'Category name is required');
            return;
        }
        
        const categoryData = {
            id: parseInt(categoryId),
            name: categoryName,
            icon: categoryIcon
        };
        
        fetch(`/admin/api/categories/${categoryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(categoryData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message || 'Category updated successfully');
                bootstrap.Modal.getInstance(document.getElementById('editCategoryModal')).hide();
                loadCategories();
            } else {
                showAlert('error', data.error || 'Failed to update category');
            }
        })
        .catch(error => {
            console.error('Error updating category:', error);
            showAlert('error', 'Failed to update category. Please try again.');
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
            data_ai_index: dataAiIndex,
            api_url: apiUrl,
            request_method: requestMethod,
            request_headers: requestHeaders,
            request_body_template: requestBodyTemplate,
            response_path: responsePath
        };
        
        fetch('/admin/api/models', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(modelData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message || 'Model created successfully');
                document.getElementById('addModelForm').reset();
                bootstrap.Modal.getInstance(document.getElementById('addModelModal')).hide();
                loadModels();
                loadDashboardData();
            } else {
                showAlert('error', data.error || 'Failed to create model');
            }
        })
        .catch(error => {
            console.error('Error creating model:', error);
            showAlert('error', 'Failed to create model. Please try again.');
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
            data_ai_index: dataAiIndex,
            api_url: apiUrl,
            request_method: requestMethod,
            request_headers: requestHeaders,
            request_body_template: requestBodyTemplate,
            response_path: responsePath
        };
        
        fetch(`/admin/api/models/${modelId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(modelData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message || 'Model updated successfully');
                bootstrap.Modal.getInstance(document.getElementById('editModelModal')).hide();
                loadModels();
            } else {
                showAlert('error', data.error || 'Failed to update model');
            }
        })
        .catch(error => {
            console.error('Error updating model:', error);
            showAlert('error', 'Failed to update model. Please try again.');
        });
    });
}

/**
 * Set up icon preview events for dropdowns
 */
function setupIconPreviewEvents() {
    // Category icon preview
    document.getElementById('categoryIcon').addEventListener('change', function() {
        document.getElementById('iconPreview').className = 'bi ' + this.value;
    });
    
    // Edit category icon preview
    document.getElementById('editCategoryIcon').addEventListener('change', function() {
        document.getElementById('editIconPreview').className = 'bi ' + this.value;
    });
    
    // Model icon preview
    document.getElementById('modelIcon').addEventListener('change', function() {
        document.getElementById('modelIconPreview').className = 'bi ' + this.value;
    });
    
    // Edit model icon preview
    document.getElementById('editModelIcon').addEventListener('change', function() {
        document.getElementById('editModelIconPreview').className = 'bi ' + this.value;
    });
}

/**
 * Set up delete confirmation modal events
 */
function setupDeleteConfirmationEvents() {
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    deleteConfirmModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const itemType = button.getAttribute('data-type');
        const itemId = button.getAttribute('data-id');
        const itemName = button.getAttribute('data-name');
        
        document.getElementById('deleteConfirmMessage').textContent = 
            `Are you sure you want to delete the ${itemType} "${itemName}"?`;
        
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
    fetch(`/admin/api/categories/${categoryId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message || 'Category deleted successfully');
            bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
            loadCategories();
            loadModels(); // Reload models in case some were deleted with the category
            loadDashboardData();
        } else {
            showAlert('error', data.error || 'Failed to delete category');
        }
    })
    .catch(error => {
        console.error('Error deleting category:', error);
        showAlert('error', 'Failed to delete category. Please try again.');
    });
}

/**
 * Delete a model
 * @param {string} modelId - The ID of the model to delete
 */
function deleteModel(modelId) {
    fetch(`/admin/api/models/${modelId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message || 'Model deleted successfully');
            bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
            loadModels();
            loadDashboardData();
        } else {
            showAlert('error', data.error || 'Failed to delete model');
        }
    })
    .catch(error => {
        console.error('Error deleting model:', error);
        showAlert('error', 'Failed to delete model. Please try again.');
    });
}

/**
 * Populate the categories table with data
 * @param {Array} categories - The categories data
 */
function populateCategoriesTable(categories) {
    const tableBody = document.getElementById('categoriesTableBody');
    tableBody.innerHTML = '';
    
    if (categories.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="5" class="text-center">No categories found</td>`;
        tableBody.appendChild(row);
        return;
    }
    
    categories.forEach(category => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${category.id}</td>
            <td><i class="bi ${category.icon}"></i></td>
            <td>${category.name}</td>
            <td>${category.model_count || 0}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary edit-category-btn" 
                            data-id="${category.id}" 
                            data-name="${category.name}" 
                            data-icon="${category.icon}">
                        <i class="bi bi-pencil"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" 
                            data-bs-toggle="modal" 
                            data-bs-target="#deleteConfirmModal" 
                            data-type="category" 
                            data-id="${category.id}" 
                            data-name="${category.name}">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
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
            document.getElementById('editIconPreview').className = 'bi ' + categoryIcon;
            
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
    tableBody.innerHTML = '';
    
    if (models.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="7" class="text-center">No models found</td>`;
        tableBody.appendChild(row);
        return;
    }
    
    models.forEach(model => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${model.id}</td>
            <td><i class="bi ${model.icon}"></i></td>
            <td>${model.name}</td>
            <td>${model.category_name}</td>
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
                        <i class="bi bi-pencil"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" 
                            data-bs-toggle="modal" 
                            data-bs-target="#deleteConfirmModal" 
                            data-type="model" 
                            data-id="${model.id}" 
                            data-name="${model.name}">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Add event listeners to edit buttons
    document.querySelectorAll('.edit-model-btn').forEach(button => {
        button.addEventListener('click', function() {
            const modelId = this.getAttribute('data-id');
            const categoryId = this.getAttribute('data-category');
            const modelName = this.getAttribute('data-name');
            const modelIcon = this.getAttribute('data-icon');
            const dataAiIndex = this.getAttribute('data-ai-index');
            const apiUrl = this.getAttribute('data-api-url');
            const requestMethod = this.getAttribute('data-request-method') || 'POST';
            const requestHeaders = this.getAttribute('data-request-headers') || '{"Content-Type": "application/json"}';
            const requestBody = this.getAttribute('data-request-body') || '{"contents": [{"parts":[{"text": "$message"}]}]}';
            const responsePath = this.getAttribute('data-response-path') || 'candidates[0].content.parts[0].text';
            
            document.getElementById('editModelId').value = modelId;
            document.getElementById('editModelCategory').value = categoryId;
            document.getElementById('editModelName').value = modelName;
            document.getElementById('editModelIcon').value = modelIcon;
            document.getElementById('editModelIconPreview').className = 'bi ' + modelIcon;
            document.getElementById('editModelDataAiIndex').value = dataAiIndex;
            document.getElementById('editModelApiUrl').value = apiUrl;
            document.getElementById('editModelRequestMethod').value = requestMethod;
            document.getElementById('editModelRequestHeaders').value = requestHeaders;
            document.getElementById('editModelRequestBody').value = requestBody;
            document.getElementById('editModelResponsePath').value = responsePath;
            
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
        dropdown.innerHTML = '';
        
        if (categories.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No categories available';
            option.disabled = true;
            option.selected = true;
            dropdown.appendChild(option);
            return;
        }
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            dropdown.appendChild(option);
        });
    });
}

/**
 * Populate icon dropdowns
 * @param {Array} icons - The icons data
 */
function populateIconDropdowns(icons) {
    const dropdowns = [
        document.getElementById('categoryIcon'),
        document.getElementById('editCategoryIcon'),
        document.getElementById('modelIcon'),
        document.getElementById('editModelIcon')
    ];
    
    dropdowns.forEach(dropdown => {
        dropdown.innerHTML = '';
        
        icons.forEach(icon => {
            const option = document.createElement('option');
            option.value = icon.class;
            option.textContent = icon.name;
            dropdown.appendChild(option);
        });
        
        // Trigger change event to update preview
        dropdown.dispatchEvent(new Event('change'));
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
        showAlert('error', 'Model name is required');
        return false;
    }
    
    if (!dataAiIndex) {
        showAlert('error', 'Data AI Index is required');
        return false;
    }
    
    // Validate data_ai_index format (alphanumeric)
    if (!/^[a-zA-Z0-9_-]+$/.test(dataAiIndex)) {
        showAlert('error', 'Data AI Index must contain only letters, numbers, underscores, and hyphens');
        return false;
    }
    
    if (!apiUrl) {
        showAlert('error', 'API URL is required');
        return false;
    }
    
    // Validate JSON format for headers
    if (requestHeaders) {
        try {
            JSON.parse(requestHeaders);
        } catch (e) {
            showAlert('error', 'Request Headers must be valid JSON');
            return false;
        }
    }
    
    // Validate JSON format for body template
    if (requestBodyTemplate) {
        try {
            JSON.parse(requestBodyTemplate);
        } catch (e) {
            showAlert('error', 'Request Body Template must be valid JSON');
            return false;
        }
        
        // Check if the template contains the $message placeholder
        if (!requestBodyTemplate.includes('$message')) {
            showAlert('warning', 'Request Body Template should contain $message placeholder');
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
    
    // Map type to Bootstrap alert class
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert ${alertClass} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    
    // Add icon based on type
    const icon = {
        'success': 'bi-check-circle',
        'error': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-circle',
        'info': 'bi-info-circle'
    }[type] || 'bi-info-circle';
    
    alertElement.innerHTML = `
        <i class="bi ${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to container
    alertContainer.appendChild(alertElement);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => {
            alertElement.remove();
        }, 150);
    }, 5000);
}
