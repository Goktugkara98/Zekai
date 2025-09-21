// Modern Admin UI Utilities
(function(){
  'use strict';

  // Initialize tooltips
  function initTooltips() {
    try {
      const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
      tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        if (window.bootstrap && window.bootstrap.Tooltip) {
          new window.bootstrap.Tooltip(tooltipTriggerEl);
        }
      });
    } catch (e) {
      console.warn('Tooltips initialization failed:', e);
    }
  }

  // Enhanced toast system
  function ensureToastContainer() {
    let el = document.getElementById('admin-toast-container');
    if (!el) {
      el = document.createElement('div');
      el.id = 'admin-toast-container';
      el.style.position = 'fixed';
      el.style.top = '20px';
      el.style.right = '20px';
      el.style.zIndex = '9999';
      el.style.maxWidth = '400px';
      document.body.appendChild(el);
    }
    return el;
  }

  function showToast(message, type = 'info', timeout = 4000) {
    const container = ensureToastContainer();
    const toast = document.createElement('div');
    toast.className = `admin-toast admin-toast-${type}`;
    
    // Toast content
    const icon = getToastIcon(type);
    toast.innerHTML = `
      <div class="d-flex align-items-center">
        <div class="toast-icon me-3">
          <i class="fas ${icon}"></i>
        </div>
        <div class="toast-content flex-grow-1">
          <div class="toast-message">${message}</div>
        </div>
        <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
      </div>
    `;

    container.appendChild(toast);

    // Auto remove
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, timeout);
  }

  function getToastIcon(type) {
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
  }

  // Enhanced confirmation dialog
  function confirmAction(message, title = 'Onay Gerekli') {
    return new Promise((resolve) => {
      if (window.confirm(`${title}\n\n${message}`)) {
        resolve(true);
      } else {
        resolve(false);
      }
    });
  }

  // Smooth scrolling
  function smoothScrollTo(element) {
    try {
      if (typeof element === 'string') {
        element = document.querySelector(element);
      }
      if (!element) return;
      
      element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start',
        inline: 'nearest'
      });
    } catch (e) {
      console.warn('Smooth scroll failed:', e);
    }
  }

  // Loading states
  function setLoading(element, loading = true) {
    if (typeof element === 'string') {
      element = document.querySelector(element);
    }
    if (!element) return;

    if (loading) {
      element.classList.add('loading');
      element.disabled = true;
    } else {
      element.classList.remove('loading');
      element.disabled = false;
    }
  }

  // Form validation
  function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        field.classList.add('is-invalid');
        isValid = false;
      } else {
        field.classList.remove('is-invalid');
      }
    });
    
    return isValid;
  }

  // Sidebar toggle for mobile
  function initSidebarToggle() {
    const sidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebar = document.getElementById('adminSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebarToggle && sidebar && overlay) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
      });
      
      overlay.addEventListener('click', () => {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
      });
    }
  }

  // Table enhancements
  function initTableEnhancements() {
    // Add hover effects to table rows
    const tables = document.querySelectorAll('.table tbody tr');
    tables.forEach(row => {
      row.addEventListener('mouseenter', () => {
        row.style.backgroundColor = 'var(--gray-50)';
      });
      row.addEventListener('mouseleave', () => {
        row.style.backgroundColor = '';
      });
    });
  }

  // Initialize everything when DOM is ready
  function init() {
    initTooltips();
    initSidebarToggle();
    initTableEnhancements();
  }

  // Export public API
  window.AdminUI = {
    showToast,
    confirmAction,
    smoothScrollTo,
    setLoading,
    validateForm,
    init
  };

  // Auto-initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
