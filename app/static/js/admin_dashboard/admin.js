/**
 * Zekai Admin Panel JavaScript
 * Bu dosya, admin panelinin tüm işlevselliğini yönetir.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tema değiştirme işlevi
    initThemeToggle();
    
    // Sidebar toggle işlevi
    initSidebarToggle();
    
    // Dashboard sayfası için grafikleri yükle
    if (document.getElementById('aiRequestTrendChart')) {
        initDashboardCharts();
    }
    
    // AI Modelleri sayfası için işlevler
    if (document.getElementById('modelsContainer')) {
        initModelFilters();
        initModelModal();
        initModelActions();
    }
});

const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const sidebarToggle = document.getElementById('sidebarToggle');
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const htmlElement = document.documentElement;

/**
 * Sidebar toggle işlevini başlatır
 */
function initSidebarToggle() {
    if (!sidebarToggle || !sidebar || !mainContent) return;
    
    // Kayıtlı sidebar durumunu kontrol et
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        mainContent.style.marginLeft = '80px';
    }
    
    // Sidebar toggle butonu tıklama olayı
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        
        if (sidebar.classList.contains('collapsed')) {
            mainContent.style.marginLeft = '80px';
            localStorage.setItem('sidebarCollapsed', 'true');
        } else {
            mainContent.style.marginLeft = '250px';
            localStorage.setItem('sidebarCollapsed', 'false');
        }
    });
}

/**
 * Tema değiştirme işlevini başlatır
 */
function initThemeToggle() {
    if (!themeToggle || !themeIcon || !htmlElement) return;
    
    // Kayıtlı temayı kontrol et
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        htmlElement.classList.add('dark');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    }
    
    // Tema değiştirme butonu tıklama olayı
    themeToggle.addEventListener('click', function() {
        if (htmlElement.classList.contains('dark')) {
            htmlElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        } else {
            htmlElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    });
}

// Eski tema yönetimi fonksiyonu (geriye dönük uyumluluk için)
function applyTheme(theme) {
    if (theme === 'dark') {
        htmlElement.classList.add('dark');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    } else {
        htmlElement.classList.remove('dark');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
    }
    // Grafikleri yeniden çiz (eğer bu sayfada grafikler varsa)
    if (typeof destroyCharts === 'function' && typeof initializeCharts === 'function') {
        destroyCharts();
        initializeCharts();
    }
}

// Eski tema değiştirme kodu kaldırıldı - çift event listener çakışması önlendi

/**
 * AI Modelleri sayfası için filtreleme işlevini başlatır
 */
function initModelFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const providerFilter = document.getElementById('providerFilter');
    const statusFilter = document.getElementById('statusFilter');
    const modelsContainer = document.getElementById('modelsContainer');
    
    if (!categoryFilter || !providerFilter || !statusFilter || !modelsContainer) return;
    
    const modelCards = modelsContainer.querySelectorAll('.kpi-card[data-model-id]');
    
    // Filtreleme fonksiyonu
    function filterModels() {
        const categoryValue = categoryFilter.value;
        const providerValue = providerFilter.value;
        const statusValue = statusFilter.value;
        
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
        
        // Hiç sonuç yoksa mesaj göster
        if (visibleCount === 0 && modelCards.length > 0) {
            let noResultsElement = document.getElementById('noFilterResults');
            if (!noResultsElement) {
                noResultsElement = document.createElement('div');
                noResultsElement.id = 'noFilterResults';
                noResultsElement.className = 'col-span-3 py-12 flex flex-col items-center justify-center text-center';
                noResultsElement.innerHTML = `
                    <div class="bg-accent-light text-accent p-4 rounded-full mb-4">
                        <i class="fas fa-filter text-3xl"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-[var(--text-primary)] mb-2">Sonuç Bulunamadı</h3>
                    <p class="text-[var(--text-secondary)] max-w-md mb-6">Seçtiğiniz filtrelere uygun model bulunamadı. Lütfen filtreleri değiştirin veya temizleyin.</p>
                    <button id="clearFiltersBtn" class="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center">
                        <i class="fas fa-times mr-2"></i> Filtreleri Temizle
                    </button>
                `;
                modelsContainer.appendChild(noResultsElement);
                
                // Filtreleri temizleme butonu
                document.getElementById('clearFiltersBtn').addEventListener('click', function() {
                    categoryFilter.value = '';
                    providerFilter.value = '';
                    statusFilter.value = '';
                    filterModels();
                });
            }
        } else {
            const noResultsElement = document.getElementById('noFilterResults');
            if (noResultsElement) {
                noResultsElement.remove();
            }
        }
    }
    
    // Filtre değişikliklerini dinle
    categoryFilter.addEventListener('change', filterModels);
    providerFilter.addEventListener('change', filterModels);
    statusFilter.addEventListener('change', filterModels);
}

/**
 * AI Modelleri sayfası için modal işlevlerini başlatır
 */
function initModelModal() {
    const addModelBtn = document.getElementById('addModelBtn');
    const emptyAddModelBtn = document.getElementById('emptyAddModelBtn');
    const modelModal = document.getElementById('modelModal');
    const modalOverlay = document.getElementById('modalOverlay');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModelBtn = document.getElementById('cancelModelBtn');
    const modelForm = document.getElementById('modelForm');
    const modalTitle = document.getElementById('modalTitle');
    
    if (!modelModal) return;
    
    // Modal açma fonksiyonu
    function openModal(isEdit = false, modelData = null) {
        modalTitle.textContent = isEdit ? 'Modeli Düzenle' : 'Yeni Model Ekle';
        
        // Form alanlarını sıfırla veya doldur
        if (isEdit && modelData) {
            document.getElementById('modelId').value = modelData.id;
            document.getElementById('modelName').value = modelData.name;
            document.getElementById('modelCategory').value = modelData.category_id;
            document.getElementById('modelDescription').value = modelData.description || '';
            document.getElementById('modelProvider').value = modelData.service_provider;
            document.getElementById('modelExternalName').value = modelData.external_model_name;
            document.getElementById('modelApiUrl').value = modelData.api_url || '';
            document.getElementById('modelRequestMethod').value = modelData.request_method || 'POST';
            document.getElementById('modelStatus').value = modelData.status;
        } else {
            modelForm.reset();
            document.getElementById('modelId').value = '';
        }
        
        modelModal.classList.remove('hidden');
    }
    
    // Modal kapatma fonksiyonu
    function closeModal() {
        modelModal.classList.add('hidden');
    }
    
    // Yeni model ekleme butonları
    if (addModelBtn) {
        addModelBtn.addEventListener('click', () => openModal());
    }
    
    if (emptyAddModelBtn) {
        emptyAddModelBtn.addEventListener('click', () => openModal());
    }
    
    // Modal kapatma butonları
    closeModalBtn.addEventListener('click', closeModal);
    cancelModelBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);
    
    // Form gönderimi
    modelForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(modelForm);
        const modelId = formData.get('modelId');
        const isEdit = modelId !== '';
        
        // Form verilerini JSON'a dönüştür
        const modelData = {};
        formData.forEach((value, key) => {
            if (key === 'category_id') {
                modelData[key] = parseInt(value);
            } else if (key !== 'modelId') {
                modelData[key] = value;
            }
        });
        
        // API isteği gönder
        const url = isEdit ? `/admin/api/models/${modelId}` : '/admin/api/models';
        const method = isEdit ? 'PUT' : 'POST';
        
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(modelData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Bir hata oluştu');
                });
            }
            return response.json();
        })
        .then(data => {
            showToast(isEdit ? 'Model başarıyla güncellendi.' : 'Yeni model başarıyla eklendi.', 'success');
            closeModal();
            
            // Sayfayı zorla yenile
            setTimeout(function() {
                window.location.reload(true);
            }, 500);
        })
        .catch(error => {
            showToast(error.message, 'error');
        });
    });
    
    // Global erişim için modal açma fonksiyonunu dışa aktar
    window.modelModalFunctions = { openModal };
}

/**
 * AI Modelleri sayfası için model işlemlerini başlatır
 */
function initModelActions() {
    const modelsContainer = document.getElementById('modelsContainer');
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const deleteModalOverlay = document.getElementById('deleteModalOverlay');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    if (!modelsContainer || !deleteConfirmModal) return;
    
    let modelToDelete = null;
    
    // Düzenleme butonları
    const editButtons = document.querySelectorAll('.edit-model-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modelId = this.dataset.modelId;
            
            // Model verilerini API'den al
            fetch(`/admin/api/models/${modelId}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Bir hata oluştu');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Modal'ı aç ve verileri doldur
                if (window.modelModalFunctions && window.modelModalFunctions.openModal) {
                    window.modelModalFunctions.openModal(true, data.model);
                }
            })
            .catch(error => {
                showToast(error.message, 'error');
            });
        });
    });
    
    // Silme butonları
    const deleteButtons = document.querySelectorAll('.delete-model-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            modelToDelete = this.dataset.modelId;
            deleteConfirmModal.classList.remove('hidden');
        });
    });
    
    // Silme modalını kapat
    function closeDeleteModal() {
        deleteConfirmModal.classList.add('hidden');
        modelToDelete = null;
    }
    
    // Silme modalı kapatma butonları
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    deleteModalOverlay.addEventListener('click', closeDeleteModal);
    
    // Silme onay butonu
    confirmDeleteBtn.addEventListener('click', function() {
        if (!modelToDelete) return;
        
        fetch(`/admin/api/models/${modelToDelete}`, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Bir hata oluştu');
                });
            }
            return response.json();
        })
        .then(data => {
            showToast('Model başarıyla silindi.', 'success');
            closeDeleteModal();
            
            // Sayfayı zorla yenile
            setTimeout(function() {
                window.location.reload(true);
            }, 500);
        })
        .catch(error => {
            showToast(error.message, 'error');
        });
    });
}

// Sayfa yüklendiğinde kayıtlı temayı uygula
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light'; // Varsayılan açık tema
    applyTheme(savedTheme);
    
    // Grafikleri yükle
    if (document.getElementById('aiRequestTrendChart')) {
        initializeCharts();
    }
    
    // Sidebar durumunu ayarla (eğer büyük ekran ise)
    if (window.innerWidth < 1024) { // Tailwind lg breakpoint
         if (!sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
            mainContent.style.marginLeft = '80px';
         }
    } else {
         if (sidebar.classList.contains('collapsed')) {
            mainContent.style.marginLeft = '80px';
         } else {
            mainContent.style.marginLeft = '250px';
         }
    }
});
 // Ekran boyutu değiştiğinde sidebar'ı ayarla
window.addEventListener('resize', () => {
    if (window.innerWidth < 1024) {
        if (!sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
            mainContent.style.marginLeft = '80px';
        }
    } else {
        // Büyük ekranda isteğe bağlı olarak sidebar'ı açık bırakabilirsiniz
        // Veya son kullanıcı tercihine göre ayarlayabilirsiniz.
        // Bu örnekte dokunmuyoruz, kullanıcı toggle ile yönetebilir.
         if (sidebar.classList.contains('collapsed')) {
            mainContent.style.marginLeft = '80px';
         } else {
            mainContent.style.marginLeft = '250px';
         }
    }
});


let aiRequestTrendChartInstance;
let topModelsChartInstance;

function getChartThemeColors() {
    const isDarkMode = htmlElement.classList.contains('dark');
    const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
    return {
        primary: accent,
        primaryTransparent: accent + '33', // ~20% opacity
        gridColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
        textColor: isDarkMode ? '#cbd5e1' : '#4b5563', // gray-300 / gray-600
        tooltipBg: isDarkMode ? '#1f2937' : '#ffffff', // gray-800 / white
        doughnutBorder: isDarkMode ? '#2d3748' : '#ffffff' // card-bg
    };
}

function loadAiRequestTrendChart() {
    const ctx = document.getElementById('aiRequestTrendChart');
    if (!ctx) return;
    const themeColors = getChartThemeColors();
    const labels = Array.from({length: 30}, (_, i) => `${i + 1}`);
    const data = Array.from({length: 30}, () => Math.floor(Math.random() * 280) + 50);

    aiRequestTrendChartInstance = new Chart(ctx, {
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
                pointBorderColor: themeColors.doughnutBorder,
                pointRadius: 0,
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
            plugins: { legend: { display: false }, tooltip: { backgroundColor: themeColors.tooltipBg, titleColor: themeColors.textColor, bodyColor: themeColors.textColor, padding: 10, cornerRadius: 4 } }
        }
    });
}

function loadTopModelsChart() {
    const ctx = document.getElementById('topModelsChart');
    if (!ctx) return;
    const themeColors = getChartThemeColors();
    const data = {
        labels: ['GPT-4 Turbo', 'Claude 3 Sonnet', 'Gemini Pro', 'Llama 2 70B', 'Diğer'],
        datasets: [{
            data: [320, 210, 150, 100, 70],
            backgroundColor: [themeColors.primary, '#60A5FA', '#34D399', '#FBBF24', '#F87171'].map(c => htmlElement.classList.contains('dark') ? c + 'BF' : c), // Add opacity for dark mode or use distinct colors
            borderColor: themeColors.doughnutBorder,
            borderWidth: 2,
            hoverOffset: 6
        }]
    };
    topModelsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: themeColors.textColor, usePointStyle: true, boxWidth: 10, padding: 15, font: {size: 11} } }, tooltip: { backgroundColor: themeColors.tooltipBg, titleColor: themeColors.textColor, bodyColor: themeColors.textColor, padding: 10, cornerRadius: 4 } },
            cutout: '65%'
        }
    });
}

const trendChartTimespanSelect = document.getElementById('trendChartTimespan');
if (trendChartTimespanSelect) {
    trendChartTimespanSelect.addEventListener('change', (event) => {
        if (aiRequestTrendChartInstance) {
            const days = parseInt(event.target.value);
            aiRequestTrendChartInstance.data.labels = Array.from({length: days}, (_, i) => `${i + 1}`);
            aiRequestTrendChartInstance.data.datasets[0].data = Array.from({length: days}, () => Math.floor(Math.random() * 280) + 50);
            aiRequestTrendChartInstance.update();
        }
    });
}

function destroyCharts() {
    if (aiRequestTrendChartInstance) aiRequestTrendChartInstance.destroy();
    if (topModelsChartInstance) topModelsChartInstance.destroy();
}
function initializeCharts() {
    loadAiRequestTrendChart();
    loadTopModelsChart();
}
document.addEventListener('DOMContentLoaded', () => {
    // Tema zaten DOMContentLoaded içinde ayarlanıyor, grafikler de orada initialize ediliyor.
});

/**
 * Toast bildirimi gösterir
 */
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        // Toast container yoksa oluştur
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'fixed bottom-4 right-4 z-50';
        document.body.appendChild(container);
        toastContainer = container;
    }
    
    const toast = document.createElement('div');
    toast.className = `flex items-center p-4 mb-3 rounded-lg shadow-lg max-w-xs animate-fade-in`;
    
    // Toast tipi
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-100 dark:bg-green-900/30';
            textColor = 'text-green-800 dark:text-green-300';
            icon = 'fa-check-circle';
            break;
        case 'error':
            bgColor = 'bg-red-100 dark:bg-red-900/30';
            textColor = 'text-red-800 dark:text-red-300';
            icon = 'fa-exclamation-circle';
            break;
        case 'warning':
            bgColor = 'bg-yellow-100 dark:bg-yellow-900/30';
            textColor = 'text-yellow-800 dark:text-yellow-300';
            icon = 'fa-exclamation-triangle';
            break;
        default: // info
            bgColor = 'bg-blue-100 dark:bg-blue-900/30';
            textColor = 'text-blue-800 dark:text-blue-300';
            icon = 'fa-info-circle';
    }
    
    toast.classList.add(bgColor, textColor);
    
    toast.innerHTML = `
        <i class="fas ${icon} mr-3 text-lg"></i>
        <div class="text-sm font-medium">${message}</div>
        <button class="ml-auto text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Kapatma butonu
    const closeBtn = toast.querySelector('button');
    closeBtn.addEventListener('click', () => {
        toast.classList.add('opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
    
    // Otomatik kapanma
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

// CSS Animasyonları
document.head.insertAdjacentHTML('beforeend', `
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeIn 0.3s ease-out forwards;
    }
    .opacity-0 {
        opacity: 0;
        transition: opacity 0.3s ease-out;
    }
</style>
`);