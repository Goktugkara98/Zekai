/**
 * API Servis Modülü
 * =================
 * @description Sunucu ile olan tüm ağ iletişimini yönetir.
 */
import { log } from './logger.js';

let isInitialized = false;

export function initApiService() {
    if (isInitialized) return;
    log('info', 'ApiService', 'API servisi başlatıldı.');
    isInitialized = true;
}

/**
 * Mesajı ve sohbet geçmişini sunucuya gönderir.
 * @param {object} payload - Sunucuya gönderilecek veri.
 * @param {string} payload.chatId - Sohbetin ID'si.
 * @param {number} payload.aiModelId - Kullanılan AI modelinin ID'si.
 * @param {string} payload.chat_message - Kullanıcının yeni mesajı.
 * @param {Array} payload.history - Önceki konuşmalar.
 * @returns {Promise<object>} Sunucudan gelen yanıtı içeren Promise.
 */
export async function sendMessageToServer(payload) {
    log('info', 'ApiService', `AI yanıtı için istek gönderiliyor: Model ID ${payload.aiModelId}`);
    try {
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            let errorText = `Sunucu hatası: ${response.status}`;
            try {
                const errorData = await response.json();
                errorText = errorData.error || errorText;
            } catch (e) {
                // JSON parse edilemezse, text olarak oku
                const rawText = await response.text();
                errorText = rawText || errorText;
            }
            throw new Error(errorText);
        }

        const data = await response.json();
        if (!data.response || typeof data.response !== 'string') {
            throw new Error("AI'dan geçersiz yanıt formatı.");
        }
        return data;

    } catch (error) {
        log('error', 'ApiService', 'Mesaj gönderiminde ağ hatası!', error);
        // Hatanın daha üst katmanda yakalanabilmesi için tekrar fırlat.
        throw error;
    }
}
