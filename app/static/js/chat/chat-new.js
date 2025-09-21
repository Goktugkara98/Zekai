/**
 * Main Chat Application Entry Point
 * Modüler JavaScript yapısı
 */

// Silence all console output for chat app (before anything else)
import './utils/silence-console.js';
import { App } from './core/app.js';

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const app = App.getInstance();
        await app.init();
    } catch (error) {
        // Application startup failed - silently handle
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
