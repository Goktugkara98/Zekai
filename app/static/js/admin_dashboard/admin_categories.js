/**
 * Zekai Admin Panel - Categories JavaScript
 * ==========================================
 * @description Manages all functionality for the categories page in the admin panel.
 * @version 1.0.0
 * @author ZekAI Team
 */

const CategoriesManager = (function() {
    'use strict';

    // 1. State Management
    const state = {
        categoryToDelete: null,
        currentPage: 'categories'
    };

    // 2. DOM Elements Cache
    const elements = {};

    // 3. API Endpoints
    const endpoints = {
        addCategory: '/admin/api/categories',
        updateCategory: (id) => `/admin/api/categories/${id}`,
        deleteCategory: (id) => `/admin/api/categories/${id}`
    };

    // 4. Initialization
    let initialized = false;
    function init() {
        if (initialized) return;
        initialized = true;
        
        console.log('Initializing Categories Manager...');
        cacheDOMElements();
        setupEventListeners();
        try {
            updateActiveMenuItem();
        } catch (e) {
            console.error('Error updating active menu item:', e);
        }
    }

    // 5. DOM Caching
    function cacheDOMElements() {
        elements.categoriesTableBody = document.getElementById('categoriesTableBody');
        elements.addCategoryBtn = document.getElementById('addCategoryBtn');
        elements.emptyAddCategoryBtn = document.getElementById('emptyAddCategoryBtn');
        elements.categoryModal = document.getElementById('categoryModal');
        elements.modalOverlay = document.getElementById('modalOverlay');
        elements.closeModalBtn = document.getElementById('closeModalBtn');
        elements.cancelCategoryBtn = document.getElementById('cancelCategoryBtn');
        elements.categoryForm = document.getElementById('categoryForm');
        elements.categoryIdInput = document.getElementById('categoryId');
        elements.categoryNameInput = document.getElementById('categoryName');
        elements.categoryIconInput = document.getElementById('categoryIcon');
        elements.categoryStatusSelect = document.getElementById('categoryStatus');
        elements.iconPreview = document.getElementById('iconPreview');
        elements.deleteConfirmModal = document.getElementById('deleteConfirmModal');
        elements.confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        elements.cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    }

    // 6. Event Listeners
    function setupEventListeners() {
        // Add Category Button
        if (elements.addCategoryBtn) {
            elements.addCategoryBtn.addEventListener('click', function() {
                openCategoryModal();
            });
        }
        if (elements.emptyAddCategoryBtn) {
            elements.emptyAddCategoryBtn.addEventListener('click', function() {
                openCategoryModal();
            });
        }
        
        // Modal Controls

        // Modal Controls
        if (elements.closeModalBtn) {
            elements.closeModalBtn.addEventListener('click', closeCategoryModal);
        }
        if (elements.cancelCategoryBtn) {
            elements.cancelCategoryBtn.addEventListener('click', closeCategoryModal);
        }
        if (elements.modalOverlay) {
            elements.modalOverlay.addEventListener('click', closeCategoryModal);
        }

        // Form Submission
        if (elements.categoryForm) {
            elements.categoryForm.addEventListener('submit', handleCategoryFormSubmit);
        }

        // Icon Preview
        if (elements.categoryIconInput) {
            elements.categoryIconInput.addEventListener('input', updateIconPreview);
        }

        // Delete Confirmation
        if (elements.confirmDeleteBtn) {
            elements.confirmDeleteBtn.addEventListener('click', handleDeleteCategoryConfirm);
        }
        if (elements.cancelDeleteBtn) {
            elements.cancelDeleteBtn.addEventListener('click', closeDeleteConfirmModal);
        }

        // Edit/Delete Buttons (delegated)
        document.addEventListener('click', (e) => {
            const editBtn = e.target.closest('.edit-category-btn');
            const deleteBtn = e.target.closest('.delete-category-btn');
            
            if (editBtn) {
                const categoryId = editBtn.dataset.categoryId;
                handleEditCategory(categoryId);
            } else if (deleteBtn) {
                const categoryId = deleteBtn.dataset.categoryId;
                showDeleteConfirmModal(categoryId);
            }
        });
    }


    // 7. Modal Management
    // Track modal state to prevent multiple calls
    let modalOpen = false;
    
    function openCategoryModal(categoryData = null) {
        // Prevent multiple calls
        if (modalOpen) return;
        modalOpen = true;
        
        console.log('Opening category modal');
        resetCategoryForm();
        
        // Get the modal element directly from the DOM each time to ensure we have the latest reference
        const modalElement = document.getElementById('categoryModal');
        const modalTitleElement = document.getElementById('modalTitle');
        
        if (categoryData) {
            // Edit mode
            if (modalTitleElement) modalTitleElement.textContent = 'Kategori Düzenle';
            if (elements.categoryIdInput) elements.categoryIdInput.value = categoryData.id || '';
            if (elements.categoryNameInput) elements.categoryNameInput.value = categoryData.name || '';
            if (elements.categoryIconInput) elements.categoryIconInput.value = categoryData.icon || '';
            if (elements.categoryStatusSelect) elements.categoryStatusSelect.value = categoryData.status || 'active';
        } else {
            // Add mode
            if (modalTitleElement) modalTitleElement.textContent = 'Yeni Kategori Ekle';
            if (elements.categoryStatusSelect) elements.categoryStatusSelect.value = 'active';
        }
        
        updateIconPreview();
        
        // Make sure the modal is visible
        if (modalElement) {
            modalElement.classList.remove('hidden');
            document.body.classList.add('overflow-hidden');
        } else {
            console.error('Category modal element not found!');
            modalOpen = false; // Reset state if modal not found
        }
        
        // Reset modal state after a short delay to allow animations to complete
        setTimeout(() => {
            modalOpen = false;
        }, 300);
    }

    function closeCategoryModal() {
        // Get the modal element directly from the DOM each time to ensure we have the latest reference
        const modalElement = document.getElementById('categoryModal');
        
        if (modalElement) {
            modalElement.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
        
        // Reset modal state
        modalOpen = false;
    }

    function resetCategoryForm() {
        elements.categoryForm.reset();
        elements.categoryIdInput.value = '';
        elements.categoryStatusSelect.value = 'active';
    }

    // 8. Form Handling
    async function handleCategoryFormSubmit(event) {
        event.preventDefault();
        
        const formData = {
            name: elements.categoryNameInput.value.trim(),
            icon: elements.categoryIconInput.value.trim(),
            status: elements.categoryStatusSelect.value
        };
        
        const categoryId = elements.categoryIdInput.value;
        const isEdit = !!categoryId;
        
        try {
            showPageLoader();
            
            let response;
            if (isEdit) {
                response = await fetch(endpoints.updateCategory(categoryId), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(formData)
                });
            } else {
                response = await fetch(endpoints.addCategory, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(formData)
                });
            }
            
            const result = await response.json();
            
            if (response.ok) {
                showToast(
                    isEdit ? 'Kategori başarıyla güncellendi.' : 'Kategori başarıyla eklendi.',
                    'success'
                );
                closeCategoryModal();
                // Reload the page to reflect changes
                window.location.reload();
            } else {
                throw new Error(result.message || 'Bir hata oluştu.');
            }
        } catch (error) {
            console.error('Kategori işlemi sırasında hata:', error);
            showToast(
                error.message || 'Kategori işlenirken bir hata oluştu. Lütfen tekrar deneyin.',
                'error'
            );
        } finally {
            hidePageLoader();
        }
    }

    // 9. Delete Confirmation
    function showDeleteConfirmModal(categoryId) {
        state.categoryToDelete = categoryId;
        if (elements.deleteConfirmModal) {
            elements.deleteConfirmModal.classList.remove('hidden');
            document.body.classList.add('overflow-hidden');
        } else {
            console.error('Delete confirm modal element not found!');
        }
    }

    function closeDeleteConfirmModal() {
        state.categoryToDelete = null;
        if (elements.deleteConfirmModal) {
            elements.deleteConfirmModal.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
    }

    async function handleDeleteCategoryConfirm() {
        if (!state.categoryToDelete) {
            closeDeleteConfirmModal();
            return;
        }
        
        try {
            showPageLoader();
            
            const response = await fetch(endpoints.deleteCategory(state.categoryToDelete), {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showToast('Kategori başarıyla silindi.', 'success');
                // Reload the page to reflect changes
                window.location.reload();
            } else {
                throw new Error(result.message || 'Kategori silinirken bir hata oluştu.');
            }
        } catch (error) {
            console.error('Kategori silinirken hata:', error);
            showToast(
                error.message || 'Kategori silinirken bir hata oluştu. Lütfen tekrar deneyin.',
                'error'
            );
        } finally {
            closeDeleteConfirmModal();
            hidePageLoader();
        }
    }

    // 10. Helper Functions
    function updateIconPreview() {
        if (elements.iconPreview && elements.categoryIconInput) {
            const iconClasses = elements.categoryIconInput.value.trim() || 'fas fa-folder';
            elements.iconPreview.className = iconClasses;
        }
    }

    async function handleEditCategory(categoryId) {
        try {
            showPageLoader();
            
            const response = await fetch(`/admin/api/categories/${categoryId}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error('Kategori bilgileri alınamadı.');
            }
            
            const categoryData = await response.json();
            openCategoryModal(categoryData);
        } catch (error) {
            console.error('Kategori bilgileri alınırken hata:', error);
            showToast(error.message || 'Kategori bilgileri alınırken bir hata oluştu.', 'error');
        } finally {
            hidePageLoader();
        }
    }

    function updateActiveMenuItem() {
        try {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                const href = link.getAttribute('href');
                if (href && state.currentPage && href.includes(state.currentPage)) {
                    link.classList.add('active');
                }
            });
        } catch (error) {
            console.error('Error updating active menu item:', error);
        }
    }

    // 11. Toast and Loader (reused from admin.js)
    function showToast(message, type = 'info') {
        // Implementation from admin.js
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    function showPageLoader() {
        // Implementation from admin.js
        document.body.style.cursor = 'wait';
    }

    function hidePageLoader() {
        // Implementation from admin.js
        document.body.style.cursor = 'default';
    }

    // Public API
    return {
        init: init,
        openCategoryModal: openCategoryModal
    };
})();

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a short time to ensure admin.js has initialized first
    setTimeout(() => {
        CategoriesManager.init();
    }, 100);
});
