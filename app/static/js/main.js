/**
 * ZekAI Main Entry Point
 * =====================
 * @description Yeni modüler mimarinin ana başlatma dosyası
 * @version 2.0.0
 * @author ZekAI Team
 */

(function() {
    'use strict';

    /**
     * DOM hazır olduğunda uygulamayı başlat
     */
    document.addEventListener('DOMContentLoaded', async function() {
        console.log('🚀 ZekAI Application Starting...');
        console.log('📦 New Modular Architecture v2.0.0');
        
        try {
            // Uygulamayı başlat
            await ZekAIApp.initialize();
            
            console.log('✅ ZekAI Application Started Successfully');
            console.log('📊 Application Status:', ZekAIApp.getStatus());
            
        } catch (error) {
            console.error('❌ ZekAI Application Failed to Start:', error);
            
            // Fallback: Eski sistemi başlatmaya çalış
            if (window.ChatManager && typeof window.ChatManager.init === 'function') {
                console.warn('🔄 Falling back to legacy ChatManager...');
                try {
                    window.ChatManager.init();
                    console.log('✅ Legacy ChatManager initialized as fallback');
                } catch (legacyError) {
                    console.error('❌ Legacy ChatManager also failed:', legacyError);
                }
            }
        }
    });

    /**
     * Debug için global fonksiyonlar
     */
    if (typeof window !== 'undefined') {
        // Debug modunu açma/kapama
        window.toggleDebug = function() {
            window.DEBUG_LOG_ACTIVE = !window.DEBUG_LOG_ACTIVE;
            Logger.configure({ enabled: window.DEBUG_LOG_ACTIVE });
            console.log(`Debug mode: ${window.DEBUG_LOG_ACTIVE ? 'ON' : 'OFF'}`);
        };

        // Uygulama durumunu görüntüleme
        window.getAppStatus = function() {
            return ZekAIApp.getStatus();
        };

        // Debug bilgilerini görüntüleme
        window.getDebugInfo = function() {
            return ZekAIApp.getDebugInfo();
        };

        // Uygulamayı yeniden başlatma
        window.restartApp = async function() {
            console.log('🔄 Restarting application...');
            try {
                await ZekAIApp.restart();
                console.log('✅ Application restarted successfully');
            } catch (error) {
                console.error('❌ Failed to restart application:', error);
            }
        };

        // State'i görüntüleme
        window.getState = function() {
            return StateManager.getSnapshot();
        };

        // Chat istatistiklerini görüntüleme
        window.getChatStats = function() {
            return ChatManager.getStats();
        };

        // Event listener'ları görüntüleme
        window.getEventListeners = function() {
            return EventBus.getListeners();
        };

        console.log('🛠️  Debug functions available:');
        console.log('   - toggleDebug()');
        console.log('   - getAppStatus()');
        console.log('   - getDebugInfo()');
        console.log('   - restartApp()');
        console.log('   - getState()');
        console.log('   - getChatStats()');
        console.log('   - getEventListeners()');
    }

    /**
     * Sayfa kapatılırken temizlik yap
     */
    window.addEventListener('beforeunload', function() {
        console.log('🧹 Cleaning up before page unload...');
        
        // Dropdown'ları kapat
        if (window.ModelSelector) {
            ModelSelector.closeAllDropdowns();
        }
        
        // Event listener'ları temizle
        if (window.EventBus) {
            EventBus.clear();
        }
    });

    /**
     * Hata yakalama
     */
    window.addEventListener('error', function(event) {
        console.error('🚨 Global Error:', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error
        });
    });

    window.addEventListener('unhandledrejection', function(event) {
        console.error('🚨 Unhandled Promise Rejection:', event.reason);
    });

})();

// Versiyon bilgisi
console.log(`
╔══════════════════════════════════════╗
║            ZekAI Frontend            ║
║         Modular Architecture         ║
║            Version 2.0.0             ║
╚══════════════════════════════════════╝
`);

