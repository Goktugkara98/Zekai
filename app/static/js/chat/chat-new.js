/**
 * Main Chat Application Entry Point
 * Modüler JavaScript yapısı
 */

// Silence all console output for chat app (before anything else)
import './utils/silence-console.js';
import { App } from './core/app.js';

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', async () => {
    const pre = document.getElementById('preloader');
    let fallbackTimer = null;

    let done = false;
    const hide = () => {
        if (done) return;
        done = true;
        try { document.body.classList.remove('preloading'); } catch (_) {}
        if (pre) {
            pre.classList.add('hide');
            const onEnd = (e) => {
                if (e && e.target !== pre) return;
                try { pre.remove(); } catch (_) {}
            };
            pre.addEventListener('transitionend', onEnd, { once: true });
            setTimeout(() => {
                try { pre.removeEventListener('transitionend', onEnd); } catch (_) {}
                try { pre.remove(); } catch (_) {}
            }, 600);
        }
    };

    try {
        const app = App.getInstance();

        // Kısa bir maksimum bekleme koy — yavaş ağlarda bile spinner takılı kalmasın
        fallbackTimer = setTimeout(hide, 1500);

        // Event bus varsa, init sırasında gelebilecek event'leri yakalamak için ÖNCE bağlan
        if (window.ZekaiApp && window.ZekaiApp.eventManager) {
            window.ZekaiApp.eventManager.on('models:loaded', hide);
            window.ZekaiApp.eventManager.on('panes:auto-opened', hide);
        }

        window.addEventListener('load', hide, { once: true });

        await app.init();
    } catch (error) {
        // Application startup failed - silently handle
    } finally {
        hide();
        if (fallbackTimer) {
            try { clearTimeout(fallbackTimer); } catch (_) {}
        }
    }
});

// Global error handling
window.addEventListener('error', (event) => {
    // Global error - silently handle
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', (event) => {
    // Unhandled promise rejection - silently handle
});
