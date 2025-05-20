document.addEventListener('DOMContentLoaded', function () {
    // Utility function to get cookie value by name
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('mainContentArea');
    const toggleSidebar = document.getElementById('toggleSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const pageTitleElement = document.getElementById('pageTitle');
    const pageContentContainer = document.getElementById('pageContentContainer');
    
    // Get initial data from Flask
    const initialDataElement = document.getElementById('initial-data');
    const appData = JSON.parse(initialDataElement.textContent);
    
    // Toggle sidebar on button click
    toggleSidebar.addEventListener('click', () => {
        const isMobile = window.innerWidth <= 992;
        
        if (isMobile) {
            sidebar.classList.toggle('show');
            sidebarOverlay.classList.toggle('active');
        } else {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('sidebar-collapsed');
        }
    });
    
    // Close sidebar when clicking overlay (mobile)
    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('show');
        sidebarOverlay.classList.remove('active');
    });
    
    // Handle window resize
    window.addEventListener('resize', () => {
        const isMobile = window.innerWidth <= 992;
        
        if (!isMobile && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('active');
        }
    });


    // --- Toast Message Function ---
    function showToast(message, type = 'info') { // type: success, info, warning, danger
        const toastContainer = document.querySelector('.toast-container');
        const toastId = 'toast-' + Date.now();
        const bgColor = type === 'info' ? 'var(--info)' : 
                       type === 'success' ? 'var(--success)' : 
                       type === 'warning' ? 'var(--warning)' : 'var(--danger)';
                       
        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header" style="background-color: ${bgColor}; color: white;">
                    <i class="fas fa-${type === 'info' ? 'info-circle' : 
                                    type === 'success' ? 'check-circle' : 
                                    type === 'warning' ? 'exclamation-triangle' : 'times-circle'} me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <small>Şimdi</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
        toast.show();
    }

    // Show flash messages
    if (appData.flashMessages && appData.flashMessages.length > 0) {
        appData.flashMessages.forEach(flash => {
            let toastType = 'info';
            if (flash.category === 'success') toastType = 'success';
            else if (flash.category === 'warning') toastType = 'warning';
            else if (flash.category === 'danger' || flash.category === 'error') toastType = 'danger';
            showToast(flash.message, toastType);
        });
    }


    // --- Dinamik İçerik Render Fonksiyonları ---
    function renderDashboard(data) {
        pageTitleElement.textContent = 'Dashboard';
        let stats = data || {}; // Gelen veri yoksa boş obje
        
        pageContentContainer.innerHTML = `
            <div class="row g-4 mb-4">
                <div class="col-md-6 col-xl-3">
                    <div class="stat-card users">
                        <div class="stat-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <h3 class="stat-value">${stats.total_users || '0'}</h3>
                        <p class="stat-label">Toplam Kullanıcı</p>
                    </div>
                </div>
                
                <div class="col-md-6 col-xl-3">
                    <div class="stat-card models">
                        <div class="stat-icon">
                            <i class="fas fa-brain"></i>
                        </div>
                        <h3 class="stat-value">${stats.total_models || '0'}</h3>
                        <p class="stat-label">AI Modelleri</p>
                    </div>
                </div>
                
                <div class="col-md-6 col-xl-3">
                    <div class="stat-card categories">
                        <div class="stat-icon">
                            <i class="fas fa-tags"></i>
                        </div>
                        <h3 class="stat-value">${stats.total_categories || '0'}</h3>
                        <p class="stat-label">Kategoriler</p>
                    </div>
                </div>
                
                <div class="col-md-6 col-xl-3">
                    <div class="stat-card chats">
                        <div class="stat-icon">
                            <i class="fas fa-comments"></i>
                        </div>
                        <h3 class="stat-value">${stats.active_tasks || '0'}</h3>
                        <p class="stat-label">Aktif Sohbetler</p>
                    </div>
                </div>
            </div>
            
            <div class="row g-4 mb-4">
                <div class="col-lg-8">
                    <div class="content-card">
                        <div class="content-card-header">
                            <h5 class="content-card-title">Kullanım İstatistikleri</h5>
                            <div>
                                <button class="btn btn-sm btn-outline-primary">Günlük</button>
                                <button class="btn btn-sm btn-primary">Haftalık</button>
                                <button class="btn btn-sm btn-outline-primary">Aylık</button>
                            </div>
                        </div>
                        <div class="content-card-body">
                            <canvas id="salesChart" height="300"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="content-card">
                        <div class="content-card-header">
                            <h5 class="content-card-title">Model Kullanımı</h5>
                        </div>
                        <div class="content-card-body">
                            <canvas id="modelUsageChart" height="250"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="content-card">
                        <div class="content-card-header">
                            <h5 class="content-card-title">Son Etkinlikler</h5>
                        </div>
                        <div class="content-card-body p-0">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex align-items-center p-3">
                                    <div class="me-3" style="width: 40px; height: 40px; background-color: rgba(67, 97, 238, 0.1); color: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-user-plus"></i>
                                    </div>
                                    <div>
                                        <p class="mb-0 fw-medium">Yeni kullanıcı kaydoldu</p>
                                        <small class="text-muted">2 dakika önce</small>
                                    </div>
                                </li>
                                <li class="list-group-item d-flex align-items-center p-3">
                                    <div class="me-3" style="width: 40px; height: 40px; background-color: rgba(76, 201, 240, 0.1); color: var(--success); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-brain"></i>
                                    </div>
                                    <div>
                                        <p class="mb-0 fw-medium">Yeni AI modeli eklendi</p>
                                        <small class="text-muted">1 saat önce</small>
                                    </div>
                                </li>
                                <li class="list-group-item d-flex align-items-center p-3">
                                    <div class="me-3" style="width: 40px; height: 40px; background-color: rgba(247, 37, 133, 0.1); color: var(--warning); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-cog"></i>
                                    </div>
                                    <div>
                                        <p class="mb-0 fw-medium">Sistem ayarları güncellendi</p>
                                        <small class="text-muted">3 saat önce</small>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="content-card">
                        <div class="content-card-header">
                            <h5 class="content-card-title">Hızlı Erişim</h5>
                        </div>
                        <div class="content-card-body">
                            <div class="row g-3">
                                <div class="col-6">
                                    <a href="{{ url_for('admin_bp.users_page') }}" class="btn btn-light w-100 py-3 text-start">
                                        <i class="fas fa-users me-2 text-primary"></i> Kullanıcılar
                                    </a>
                                </div>
                                <div class="col-6">
                                    <a href="{{ url_for('admin_bp.models_page') }}" class="btn btn-light w-100 py-3 text-start">
                                        <i class="fas fa-brain me-2 text-warning"></i> AI Modelleri
                                    </a>
                                </div>
                                <div class="col-6">
                                    <a href="{{ url_for('admin_bp.categories_page') }}" class="btn btn-light w-100 py-3 text-start">
                                        <i class="fas fa-tags me-2 text-success"></i> Kategoriler
                                    </a>
                                </div>
                                <div class="col-6">
                                    <a href="{{ url_for('admin_bp.settings_page') }}" class="btn btn-light w-100 py-3 text-start">
                                        <i class="fas fa-cog me-2 text-info"></i> Ayarlar
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Ana grafik yükle
        loadSalesChart();
        
        // Model kullanım grafiği yükle
        loadModelUsageChart();
    }

    function renderUsers(users) {
        pageTitleElement.textContent = 'Kullanıcılar';
        let tableRows = '<tr><td colspan="6" class="text-center">Kullanıcı bulunamadı.</td></tr>';
        if (users && users.length > 0) {
            tableRows = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username || 'N/A'}</td>
                    <td>${user.email || 'N/A'}</td>
                    <td><span class="badge bg-secondary">${user.role || 'N/A'}</span></td>
                    <td>${user.created_at || 'N/A'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" title="Düzenle" onclick="editUser(${user.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-outline-danger" title="Sil" onclick="deleteUser(${user.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }
        pageContentContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Kullanıcılar</h2>
                <button class="btn btn-primary rounded-pill" onclick="showAddUserModal()"><i class="fas fa-plus me-2"></i> Yeni Kullanıcı Ekle</button>
            </div>
            <div class="card"><div class="card-body"><div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light"><tr><th>ID</th><th>Kullanıcı Adı</th><th>Email</th><th>Rol</th><th>Kayıt Tarihi</th><th>İşlemler</th></tr></thead>
                    <tbody>${tableRows}</tbody>
                </table>
            </div></div></div>`;
    }

    function renderCategories(categories) {
        pageTitleElement.textContent = 'Kategoriler';
         let tableRows = '<tr><td colspan="4" class="text-center">Kategori bulunamadı.</td></tr>';
        if (categories && categories.length > 0) {
            tableRows = categories.map(cat => `
                <tr>
                    <td>${cat.id}</td>
                    <td>${cat.name || 'N/A'}</td>
                    <td>${cat.description || 'N/A'}</td>
                    <td>${cat.model_count !== undefined ? cat.model_count : 'N/A'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" title="Düzenle" onclick="editCategory(${cat.id}, '${cat.name}', '${cat.description}')"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-outline-danger" title="Sil" onclick="confirmDeleteCategory(${cat.id}, '${cat.name}')"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }
        pageContentContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Kategoriler</h2>
                <button class="btn btn-primary rounded-pill" data-bs-toggle="modal" data-bs-target="#addCategoryModal"><i class="fas fa-plus me-2"></i> Yeni Kategori Ekle</button>
            </div>
            <div class="card"><div class="card-body"><div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light"><tr><th>ID</th><th>Ad</th><th>Açıklama</th><th>Model Sayısı</th><th>İşlemler</th></tr></thead>
                    <tbody>${tableRows}</tbody>
                </table>
            </div></div></div>
            ${addCategoryModalHTML()} 
            ${editCategoryModalHTML()}
        `;
        // Event listener for add category form
        const addCategoryForm = document.getElementById('addCategoryForm');
        if(addCategoryForm) {
            addCategoryForm.addEventListener('submit', handleAddCategory);
        }
         const editCategoryForm = document.getElementById('editCategoryForm');
        if(editCategoryForm) {
            // Edit form submit logic will be handled by a separate function called by editCategory()
        }
    }
    
    function renderModels(data) {
        pageTitleElement.textContent = 'AI Modelleri';
        let tableRows = '<tr><td colspan="6" class="text-center">AI Modeli bulunamadı.</td></tr>';
        
        // Modelleri data.models'dan al (data bir obje ve models bir property)
        const models = data && data.models ? data.models : [];
        
        if (models && models.length > 0) {
            tableRows = models.map(model => `
                <tr>
                    <td>${model.id}</td>
                    <td>${model.name || 'N/A'}</td>
                    <td>${model.category_name || model.category_id || 'N/A'}</td>
                    <td>${model.description || 'N/A'}</td>
                    <td><span class="badge bg-${model.status === 'active' ? 'success' : 'secondary'}">${model.status || 'N/A'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" title="Düzenle" onclick="editModel(${model.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-outline-danger" title="Sil" onclick="deleteModel(${model.id}, '${(model.name || '').replace(/'/g, "\\'")}')"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Modal HTML'lerini ekle
        const addModalHTML = addModelModalHTML();
        const editModalHTML = editModelModalHTML();
        
        pageContentContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>AI Modelleri</h2>
                <button class="btn btn-primary rounded-pill" onclick="showAddModelModal()"><i class="fas fa-plus me-2"></i> Yeni Model Ekle</button>
            </div>
            <div class="card"><div class="card-body"><div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light"><tr><th>ID</th><th>Ad</th><th>Kategori</th><th>Açıklama</th><th>Durum</th><th>İşlemler</th></tr></thead>
                    <tbody>${tableRows}</tbody>
                </table>
            </div></div></div>
            ${addModalHTML}
            ${editModalHTML}`;
            
        // Form submit olaylarını dinle
        const addForm = document.getElementById('addModelForm');
        if (addForm) {
            addForm.addEventListener('submit', handleAddModel);
        }
        
        const editForm = document.getElementById('editModelForm');
        if (editForm) {
            editForm.addEventListener('submit', handleEditModel);
        }
    }

    function renderSettings(settings) {
        pageTitleElement.textContent = 'Ayarlar';
        let s = settings || {};
        pageContentContainer.innerHTML = `
            <div class="card">
                <div class="card-header"><h5 class="mb-0">Genel Ayarlar</h5></div>
                <div class="card-body">
                    <form id="settingsForm">
                        <div class="mb-3 row">
                            <label for="siteName" class="col-sm-3 col-form-label">Site Adı</label>
                            <div class="col-sm-9"><input type="text" class="form-control" id="siteName" value="${s.site_name || ''}"></div>
                        </div>
                        <div class="mb-3 row">
                            <label for="adminEmail" class="col-sm-3 col-form-label">Admin Email</label>
                            <div class="col-sm-9"><input type="email" class="form-control" id="adminEmail" value="${s.admin_email || ''}"></div>
                        </div>
                        <div class="mb-3 row">
                            <div class="col-sm-9 offset-sm-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" role="switch" id="maintenanceMode" ${s.maintenance_mode ? 'checked' : ''}>
                                    <label class="form-check-label" for="maintenanceMode">Bakım Modu</label>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-9 offset-sm-3">
                                <button type="submit" class="btn btn-primary rounded-pill">Ayarları Kaydet</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>`;
        document.getElementById('settingsForm').addEventListener('submit', function(e) {
            e.preventDefault();
            showToast('Ayarlar kaydedildi (demo).', 'success');
        });
    }

    // --- Modal HTML Fonksiyonları ---
    function editModelModalHTML() {
        // Kategorileri al (eğer yoksa boş dizi olarak başlat)
        const categories = (appData.pageData && appData.pageData.categories) || [];
        const categoryOptions = categories.map(cat => 
            `<option value="${cat.id}">${cat.name}</option>`
        ).join('');
        
        return `
        <div class="modal fade" id="editModelModal" tabindex="-1" aria-labelledby="editModelModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="editModelModalLabel">AI Modelini Düzenle</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <form id="editModelForm">
                        <input type="hidden" id="editModelId" name="id">
                        <div class="modal-body">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label for="editModelName" class="form-label">Model Adı <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="editModelName" name="name" required>
                                </div>
                                <div class="col-md-6">
                                    <label for="editModelCategory" class="form-label">Kategori <span class="text-danger">*</span></label>
                                    <select class="form-select" id="editModelCategory" name="category_id" required>
                                        <option value="" disabled>Kategori seçiniz</option>
                                        ${categoryOptions}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="editModelStatus" class="form-label">Durum</label>
                                    <select class="form-select" id="editModelStatus" name="status">
                                        <option value="active">Aktif</option>
                                        <option value="inactive">Pasif</option>
                                        <option value="maintenance">Bakımda</option>
                                    </select>
                                </div>
                                <div class="col-12">
                                    <label for="editModelDescription" class="form-label">Açıklama</label>
                                    <textarea class="form-control" id="editModelDescription" name="description" rows="2"></textarea>
                                </div>
                                <div class="col-12">
                                    <label for="editModelApiUrl" class="form-label">API URL</label>
                                    <input type="url" class="form-control" id="editModelApiUrl" name="api_url" placeholder="https://api.example.com/endpoint">
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">İptal</button>
                            <button type="submit" class="btn btn-primary">Güncelle</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>`;
    }
    
    function addModelModalHTML() {
        // Kategorileri al (eğer yoksa boş dizi olarak başlat)
        const categories = (appData.pageData && appData.pageData.categories) || [];
        const categoryOptions = categories.map(cat => 
            `<option value="${cat.id}">${cat.name}</option>`
        ).join('');
        
        // Örnek Bootstrap Icons
        const bootstrapIcons = [
            'bi-robot', 'bi-cpu', 'bi-braces', 'bi-code-square', 'bi-gear',
            'bi-lightbulb', 'bi-lightning', 'bi-magic', 'bi-palette', 'bi-terminal'
        ];
        
        const iconOptions = bootstrapIcons.map(icon => 
            `<option value="${icon}">${icon}</option>`
        ).join('');
        
        return `
        <div class="modal fade" id="addModelModal" tabindex="-1" aria-labelledby="addModelModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="addModelModalLabel">Yeni AI Modeli Ekle</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <form id="addModelForm">
                        <div class="modal-body">
                            <h6 class="mb-3">Temel Bilgiler</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-6">
                                    <label for="modelName" class="form-label required">Model Adı</label>
                                    <input type="text" class="form-control" id="modelName" name="name" required>
                                    <div class="form-text">Modelin görünen adı</div>
                                </div>
                                <div class="col-md-6">
                                    <label for="modelCategory" class="form-label required">Kategori</label>
                                    <select class="form-select" id="modelCategory" name="category_id" required>
                                        <option value="" selected disabled>Kategori seçiniz</option>
                                        ${categoryOptions}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="modelIcon" class="form-label">İkon</label>
                                    <select class="form-select" id="modelIcon" name="icon">
                                        <option value="" selected>İkon seçiniz</option>
                                        ${iconOptions}
                                    </select>
                                    <div class="form-text">Bootstrap Icons'tan bir ikon seçin</div>
                                </div>
                                <div class="col-md-6">
                                    <label for="modelStatus" class="form-label">Durum</label>
                                    <select class="form-select" id="modelStatus" name="status">
                                        <option value="active" selected>Aktif</option>
                                        <option value="inactive">Pasif</option>
                                        <option value="maintenance">Bakımda</option>
                                    </select>
                                </div>
                                <div class="col-12">
                                    <label for="modelDescription" class="form-label">Açıklama</label>
                                    <textarea class="form-control" id="modelDescription" name="description" rows="2"></textarea>
                                    <div class="form-text">Modelin kısa açıklaması</div>
                                </div>
                            </div>
                            
                            <h6 class="mb-3">API Ayarları</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-12">
                                    <label for="modelApiUrl" class="form-label required">API URL</label>
                                    <input type="url" class="form-control" id="modelApiUrl" name="api_url" required>
                                    <div class="form-text">Örnek: https://api.example.com/v1/chat/completions</div>
                                </div>
                                <div class="col-md-6">
                                    <label for="modelApiMethod" class="form-label required">İstek Metodu</label>
                                    <select class="form-select" id="modelApiMethod" name="api_method" required>
                                        <option value="GET">GET</option>
                                        <option value="POST" selected>POST</option>
                                        <option value="PUT">PUT</option>
                                        <option value="PATCH">PATCH</option>
                                        <option value="DELETE">DELETE</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="modelApiKey" class="form-label">API Anahtarı</label>
                                    <div class="input-group">
                                        <input type="password" class="form-control" id="modelApiKey" name="api_key" autocomplete="off">
                                        <button class="btn btn-outline-secondary toggle-password" type="button">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                    </div>
                                    <div class="form-text">Opsiyonel, güvenli bir şekilde saklanacaktır</div>
                                </div>
                            </div>
                            
                            <h6 class="mb-3">İstek ve Yanıt Yapılandırması</h6>
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label for="modelRequestHeaders" class="form-label">İstek Başlıkları (JSON)</label>
                                    <textarea class="form-control font-monospace" id="modelRequestHeaders" name="request_headers" rows="4" placeholder='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_API_KEY"}'>{
    "Content-Type": "application/json"
}</textarea>
                                    <div class="form-text">JSON formatında istek başlıkları</div>
                                </div>
                                <div class="col-md-6">
                                    <label for="modelRequestBody" class="form-label">İstek Gövdesi (JSON)</label>
                                    <textarea class="form-control font-monospace" id="modelRequestBody" name="request_body" rows="4" placeholder='{"model": "gpt-4", "messages": [{"role": "user", "content": "Merhaba!"}]}'>{
    "model": "model-adı",
    "messages": [
        {
            "role": "user",
            "content": "%MESSAGE%"
        }
    ]
}</textarea>
                                    <div class="form-text">%MESSAGE% kullanıcı girişiyle değiştirilecektir</div>
                                </div>
                                <div class="col-12">
                                    <label for="modelResponsePath" class="form-label">Yanıt Yolu (JSON Path)</label>
                                    <input type="text" class="form-control" id="modelResponsePath" name="response_path" placeholder="$.choices[0].message.content">
                                    <div class="form-text">Yanıttan metni çıkarmak için JSON Path ifadesi</div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">İptal</button>
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-save me-1"></i> Kaydet
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <script>
        // Şifre göster/gizle işlevselliği
        document.addEventListener('DOMContentLoaded', function() {
            const togglePassword = document.querySelector('.toggle-password');
            if (togglePassword) {
                togglePassword.addEventListener('click', function() {
                    const passwordInput = document.querySelector('#modelApiKey');
                    const icon = this.querySelector('i');
                    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordInput.setAttribute('type', type);
                    icon.classList.toggle('bi-eye');
                    icon.classList.toggle('bi-eye-slash');
                });
            }
        });
        </script>`;
    }
    
    function addCategoryModalHTML() {
        return `
        <div class="modal fade" id="addCategoryModal" tabindex="-1" aria-labelledby="addCategoryModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content rounded-3">
                    <form id="addCategoryForm">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="addCategoryModalLabel">Yeni Kategori Ekle</h1>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="newCategoryName" class="form-label">Kategori Adı</label>
                                <input type="text" class="form-control" id="newCategoryName" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="newCategoryDescription" class="form-label">Açıklama (Opsiyonel)</label>
                                <textarea class="form-control" id="newCategoryDescription" name="description" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary rounded-pill" data-bs-dismiss="modal">Kapat</button>
                            <button type="submit" class="btn btn-primary rounded-pill">Kaydet</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>`;
    }
    function editCategoryModalHTML() {
         return `
        <div class="modal fade" id="editCategoryModal" tabindex="-1" aria-labelledby="editCategoryModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content rounded-3">
                    <form id="editCategoryForm">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="editCategoryModalLabel">Kategoriyi Düzenle</h1>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <input type="hidden" id="editCategoryId" name="id">
                            <div class="mb-3">
                                <label for="editCategoryName" class="form-label">Kategori Adı</label>
                                <input type="text" class="form-control" id="editCategoryName" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="editCategoryDescription" class="form-label">Açıklama (Opsiyonel)</label>
                                <textarea class="form-control" id="editCategoryDescription" name="description" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary rounded-pill" data-bs-dismiss="modal">Kapat</button>
                            <button type="submit" class="btn btn-primary rounded-pill">Değişiklikleri Kaydet</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>`;
    }


    // --- CRUD İşlemleri için API Çağrıları ---
    async function handleEditModel(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const formValues = Object.fromEntries(formData.entries());
        const modelId = formValues.id;
        
        try {
            // API'ye gönderilecek veriyi hazırla
            const modelData = {
                name: formValues.name,
                category_id: parseInt(formValues.category_id),
                description: formValues.description || null,
                api_url: formValues.api_url || null,
                status: formValues.status || 'active'
            };
            
            // API isteğini gönder
            const response = await fetch(`/admin/api/models/${modelId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(modelData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showToast('Model başarıyla güncellendi.', 'success');
                
                // Modal'ı kapat
                const modal = bootstrap.Modal.getInstance(document.getElementById('editModelModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Sayfayı yenile
                window.location.reload();
            } else {
                showToast(result.message || 'Model güncellenirken bir hata oluştu.', 'danger');
            }
        } catch (error) {
            console.error('Model güncelleme hatası:', error);
            showToast('Bir hata oluştu: ' + error.message, 'danger');
        }
    }
    
    async function handleAddModel(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const formValues = Object.fromEntries(formData.entries());
        
        try {
            // JSON alanlarını parse et
            let requestHeaders = {};
            let requestBody = {};
            
            try {
                if (formValues.request_headers) {
                    requestHeaders = JSON.parse(formValues.request_headers);
                }
                if (formValues.request_body) {
                    requestBody = JSON.parse(formValues.request_body);
                }
            } catch (e) {
                showToast('JSON formatında hata: ' + e.message, 'danger');
                return;
            }
            
            // API'ye gönderilecek veriyi hazırla
            const modelData = {
                name: formValues.name,
                category_id: parseInt(formValues.category_id),
                icon: formValues.icon || null,
                description: formValues.description || null,
                api_url: formValues.api_url,
                api_method: formValues.api_method || 'POST',
                api_key: formValues.api_key || null,
                request_headers: requestHeaders,
                request_body: requestBody,
                response_path: formValues.response_path || null,
                status: formValues.status || 'active'
            };
            
            // Yükleniyor durumunu göster
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Kaydediliyor...';
            
            try {
                // API isteğini gönder
                const response = await fetch('/admin/api/models', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken') || ''
                    },
                    body: JSON.stringify(modelData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast('Model başarıyla eklendi.', 'success');
                    
                    // Modal'ı kapat
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addModelModal'));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Sayfayı yenile
                    window.location.reload();
                } else {
                    showToast(result.message || 'Model eklenirken bir hata oluştu.', 'danger');
                }
            } catch (error) {
                console.error('Model ekleme hatası:', error);
                showToast('Bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'), 'danger');
            } finally {
                // Butonu eski haline getir
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        } catch (error) {
            console.error('Beklenmeyen hata:', error);
            showToast('Beklenmeyen bir hata oluştu.', 'danger');
        }
    }
    
    async function handleAddCategory(event) {
        event.preventDefault();
        const form = event.target;
        const categoryName = form.name.value;
        const categoryDescription = form.description.value;

        try {
            const response = await fetch('{{ url_for("admin_bp.api_add_category") }}', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: categoryName, description: categoryDescription })
            });
            const result = await response.json();
            if (result.success) {
                showToast(result.message, 'success');
                bootstrap.Modal.getInstance(document.getElementById('addCategoryModal')).hide();
                // Sayfayı yeniden yüklemek yerine listeyi güncelleyebiliriz, şimdilik basitçe yönlendirme:
                window.location.href = '{{ url_for("admin_bp.categories_page") }}'; 
            } else {
                showToast(result.message || 'Kategori eklenemedi.', 'danger');
            }
        } catch (error) {
            console.error('Kategori ekleme hatası:', error);
            showToast('Bir ağ hatası oluştu.', 'danger');
        }
    }
    
    window.confirmDeleteCategory = async function(categoryId, categoryName) {
        // Basit bir custom modal ile onay alalım
        const confirmationModalHTML = `
            <div class="modal fade" id="confirmDeleteModal-${categoryId}" tabindex="-1">
                <div class="modal-dialog modal-sm">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Silme Onayı</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>"${categoryName}" kategorisini silmek istediğinizden emin misiniz?</p>
                            <p class="text-danger small">Bu işlem geri alınamaz.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary rounded-pill" data-bs-dismiss="modal">İptal</button>
                            <button type="button" class="btn btn-danger rounded-pill" id="doDeleteCategory-${categoryId}">Evet, Sil</button>
                        </div>
                    </div>
                </div>
            </div>`;
        if (!document.getElementById(`confirmDeleteModal-${categoryId}`)) {
             document.body.insertAdjacentHTML('beforeend', confirmationModalHTML);
        }
        const modalElement = document.getElementById(`confirmDeleteModal-${categoryId}`);
        const modalInstance = new bootstrap.Modal(modalElement);

        document.getElementById(`doDeleteCategory-${categoryId}`).onclick = async () => {
            modalInstance.hide(); // Onay modalını gizle
            try {
                const response = await fetch(`{{ url_for("admin_bp.api_delete_category", category_id=0) }}`.replace('0', categoryId), {
                    method: 'DELETE'
                });
                const result = await response.json();
                if (result.success) {
                    showToast(result.message, 'success');
                    window.location.href = '{{ url_for("admin_bp.categories_page") }}'; // Sayfayı yenile
                } else {
                    showToast(result.message || 'Kategori silinemedi.', 'danger');
                }
            } catch (error) {
                console.error('Kategori silme hatası:', error);
                showToast('Bir ağ hatası oluştu.', 'danger');
            }
        };
        modalInstance.show();
         modalElement.addEventListener('hidden.bs.modal', () => { // Modal kapandığında DOM'dan kaldır
            modalElement.remove();
        });
    }


    // --- Sayfa Yükleme Mantığı ---
    function loadPageContent(pageKey, data) {
        if (pageKey === 'dashboard') renderDashboard(data);
        else if (pageKey === 'users') renderUsers(data);
        else if (pageKey === 'categories') renderCategories(data);
        else if (pageKey === 'models') renderModels(data);
        else if (pageKey === 'settings') renderSettings(data);
        else renderDashboard(null); // Varsayılan olarak dashboard
    }

    // Grafik Yükleme Fonksiyonu (Dashboard için)
    function loadSalesChart() {
        const salesChartCtx = document.getElementById('salesChart');
        if (!salesChartCtx) return;
        const existingChart = Chart.getChart(salesChartCtx);
        if (existingChart) existingChart.destroy();
        new Chart(salesChartCtx, { /* ... (önceki grafik ayarları) ... */ });
    }

    // Başlangıç sayfasını yükle
    loadPageContent(appData.currentPage, appData.pageData);
    
    // Sidebar linklerinin aktifliğini ayarla (Python'dan gelen current_page'e göre)
    // Bu zaten Jinja template içinde yapılıyor.
    // window.dispatchEvent(new Event('resize')); // İlk sidebar durumunu ayarla
});

// Global scope'a CRUD fonksiyonlarını ekleyelim ki HTML içinden çağrılabilsinler
// Örnek: window.editUser = function(id) { console.log('Edit user', id); /* Modal göster vs. */ }
// window.deleteUser = function(id) { console.log('Delete user', id); /* Onay al ve sil */ }
// window.editCategory, window.deleteCategory, window.editModel, window.deleteModel vb.
// Şimdilik sadece logluyoruz, gerçek implementasyonlar eklenecek.
window.editUser = (id) => console.log('Edit user:', id);
window.deleteUser = (id) => console.log('Delete user:', id);
window.editCategory = (id, name, description) => {
    document.getElementById('editCategoryId').value = id;
    document.getElementById('editCategoryName').value = name;
    document.getElementById('editCategoryDescription').value = description;
    const modal = new bootstrap.Modal(document.getElementById('editCategoryModal'));
    modal.show();
    // Edit form submit logic...
};
// window.deleteCategory zaten confirmDeleteCategory olarak implemente edildi.
window.editModel = async (id) => {
    try {
        // Model verilerini yükle
        const response = await fetch(`/admin/api/models/${id}`, {
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error('Model verileri yüklenirken bir hata oluştu.');
        }
        
        const model = await response.json();
        
        // Modal elementini bul veya oluştur
        let modalElement = document.getElementById('editModelModal');
        if (!modalElement) {
            console.error('Düzenleme modalı bulunamadı!');
            return;
        }
        
        // Form alanlarını doldur
        document.getElementById('editModelId').value = model.id;
        document.getElementById('editModelName').value = model.name || '';
        document.getElementById('editModelDescription').value = model.description || '';
        document.getElementById('editModelApiUrl').value = model.api_url || '';
        
        // Kategori seçeneğini ayarla
        const categorySelect = document.getElementById('editModelCategory');
        if (categorySelect) {
            categorySelect.value = model.category_id || '';
        }
        
        // Durum seçeneğini ayarla
        const statusSelect = document.getElementById('editModelStatus');
        if (statusSelect) {
            statusSelect.value = model.status || 'active';
        }
        
        // Modal'ı göster
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
    } catch (error) {
        console.error('Model düzenleme hatası:', error);
        showToast('Model yüklenirken bir hata oluştu: ' + error.message, 'danger');
    }
};
window.deleteModel = async (id, name = '') => {
    // Onay iste
    if (!confirm(`"${name || 'Bu modeli'}" silmek istediğinize emin misiniz? Bu işlem geri alınamaz.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/api/models/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Model başarıyla silindi.', 'success');
            // Sayfayı yenile
            window.location.reload();
        } else {
            showToast(result.message || 'Model silinirken bir hata oluştu.', 'danger');
        }
    } catch (error) {
        console.error('Model silme hatası:', error);
        showToast('Bir hata oluştu: ' + error.message, 'danger');
    }
};
window.showAddUserModal = () => console.log('Show add user modal');
window.showAddModelModal = () => {
    // Modal elementini bul
    const modalElement = document.getElementById('addModelModal');
    
    if (modalElement) {
        // Modal'ı göster
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        // Formu sıfırla
        const form = document.getElementById('addModelForm');
        if (form) {
            form.reset();
        }
    } else {
        console.error('Model ekleme modalı bulunamadı!');
        showToast('Bir hata oluştu. Lütfen sayfayı yenileyip tekrar deneyin.', 'danger');
    }
};
