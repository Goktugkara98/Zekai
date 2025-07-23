/**
 * ZekAI Sohbet Uygulaması - Ana Giriş Noktası (Orkestratör)
 * =======================================================
 * @description Tüm modülleri içe aktarır, uygulamayı başlatır ve
 * modüller arası koordinasyonu sağlar.
 * @version 2.0.0
 * @author ZekAI Team
 */

import { log, initLogger } from './logger.js';
import { initState, setAiTypes, setAiCategories } from './state.js';
import { initApiService } from './apiService.js';
import { initUIManager, setupGlobalHandlers, setupSidebarListeners, renderAll } from './uiManager.js';
import { addChat } from './chatService.js';

/**
 * Global Hata Yakalayıcı
 * Hataları merkezi bir yerden loglamak için logger modülünü kullanır.
 */
window.onerror = function(message, source, lineno, colno, error) {
    log('error', 'GlobalErrorHandler', 'Yakalanmamış bir hata oluştu!', { message, source, lineno, colno, errorObject: error ? JSON.parse(JSON.stringify(error, Object.getOwnPropertyNames(error))) : 'N/A' });
    return false; // Hatanın konsola yazılmasını engelleme
};

window.onunhandledrejection = function(event) {
    log('error', 'GlobalPromiseRejection', 'İşlenmemiş Promise reddi!', { reason: event.reason ? (typeof event.reason === 'object' ? JSON.parse(JSON.stringify(event.reason, Object.getOwnPropertyNames(event.reason))) : event.reason) : 'N/A', promise: event.promise });
};


/**
 * Uygulamayı Başlatan Ana Fonksiyon
 */
function initializeApp() {
    // 1. Modülleri Başlat
    initLogger();
    initState();
    initApiService();
    const elementsInitialized = initUIManager();
    
    if (!elementsInitialized) {
        log('error', 'Init', 'Uygulama başlatılamadı: Kritik DOM elementleri eksik.');
        // Kullanıcıya bir hata mesajı göster
        const body = document.querySelector('body');
        if (body) {
             const errorMsgDiv = document.createElement('div');
             errorMsgDiv.innerHTML = '<p style="background-color:red;color:white;padding:10px;text-align:center;position:fixed;top:0;left:0;width:100%;z-index:9999;">Hata: Sohbet arayüzü başlatılamadı. Lütfen sayfayı yenileyin.</p>';
             body.prepend(errorMsgDiv);
        }
        return;
    }

    // 2. Global Olayları ve Dinleyicileri Ayarla
    setupGlobalHandlers();
    setupSidebarListeners((modelId) => addChat(modelId));

    // 3. Başlangıç Verilerini Yükle (index.html'den geldiğini varsayıyoruz)
    // Bu veriler normalde bir API'den alınır, ancak mevcut yapıya uyuyoruz.
    if (window.ZekAIData) {
        setAiTypes(window.ZekAIData.aiTypes || []);
        setAiCategories(window.ZekAIData.allAiCategories || []);
    } else {
        log('warn', 'Init', '`window.ZekAIData` bulunamadı. AI modelleri yüklenemedi.');
    }

    // 4. Arayüzü İlk Kez Render Et
    renderAll();

    log('info', 'Init', 'ZekAI Sohbet Uygulaması başarıyla başlatıldı.');
}

// DOM tamamen yüklendiğinde uygulamayı başlat
document.addEventListener('DOMContentLoaded', initializeApp);
