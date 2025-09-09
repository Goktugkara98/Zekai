/**
 * Main Chat Application Entry Point
 * Modüler JavaScript yapısı
 */

import { App } from './core/app.js';

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const app = App.getInstance();
        await app.init();
        
        console.log('Zekai Chat Application started successfully');
    } catch (error) {
        console.error('Failed to start Zekai Chat Application:', error);
    }
});

// Global error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
