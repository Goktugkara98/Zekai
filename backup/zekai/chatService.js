/**
 * Sohbet Servis Modülü (İş Mantığı)
 * ===================================
 * @description Sohbet operasyonlarının (ekle, sil, mesaj gönder)
 * çekirdek mantığını yönetir.
 */

import { log } from './logger.js';
import * as state from './state.js';
import { sendMessageToServer } from './apiService.js';
import { renderAll, updateChatWindow, addMessageToWindow, showLoadingMessage, updateLoadingMessage, showErrorMessage } from './uiManager.js';

/**
 * Yeni bir sohbet oluşturur ve durumu günceller.
 * @param {number|string} [aiModelIdFromDataset] - İsteğe bağlı, kullanılacak AI modelinin ID'si.
 * @param {Array} [initialMessages=[]] - Sohbetin başlangıç mesajları.
 */
export function addChat(aiModelIdFromDataset, initialMessages = []) {
    log('action', 'ChatService', 'Yeni sohbet ekleme...', { requestedModelId: aiModelIdFromDataset });
    
    const activeVisibleChatCount = state.getChats().filter(c => !c.isMinimized).length;
    if (activeVisibleChatCount >= state.getMaxChats()) {
        alert(`Maksimum ${state.getMaxChats()} sohbet paneline ulaşıldı.`);
        return null;
    }

    let finalAiModelId;
    const allModels = state.getAiTypes();

    if (aiModelIdFromDataset != null && aiModelIdFromDataset !== '') {
        const numericId = Number(aiModelIdFromDataset);
        if (allModels.some(m => m.id === numericId)) {
            finalAiModelId = numericId;
        }
    }
    
    if (!finalAiModelId) {
        if (allModels.length > 0) {
            finalAiModelId = allModels[0].id;
            log('warn', 'ChatService', `Geçersiz veya boş model ID. Varsayılan model kullanılıyor: ${finalAiModelId}`);
        } else {
            log('error', 'ChatService', 'Sohbet oluşturulamıyor: Kullanılabilir AI modeli yok.');
            alert('Sohbet oluşturulamıyor: Kullanılabilir AI modelleri yok.');
            return null;
        }
    }

    const newChat = {
        id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        aiModelId: finalAiModelId,
        messages: [...initialMessages],
        createdAt: Date.now(),
        lastActivity: Date.now(),
        isMinimized: false,
    };

    state.addChat(newChat);
    renderAll(); // Arayüzü tamamen yeniden çiz
    log('info', 'ChatService', `Yeni sohbet eklendi: ${newChat.id}`);
    return newChat.id;
}

/**
 * Bir sohbeti kaldırır, gerekirse arşivler ve arayüzü günceller.
 * @param {string} chatId - Kaldırılacak sohbetin ID'si.
 * @param {boolean} [bypassHistory=false] - Geçmişe kaydetmeyi atla.
 */
export function removeChat(chatId, bypassHistory = false) {
    log('action', 'ChatService', `Sohbet kaldırılıyor: ${chatId}`);
    const chatToRemove = state.getChatById(chatId);
    if (!chatToRemove) return;

    const hasUserMessages = chatToRemove.messages.some(msg => msg.isUser);
    if (!bypassHistory && hasUserMessages) {
        state.archiveChat(chatToRemove);
    }
    
    state.removeChat(chatId);
    renderAll(); // Arayüzü yeniden çiz
}

/**
 * Tüm sohbetleri temizler.
 * @param {boolean} includeStartedChats - Başlamış sohbetler de dahil edilsin mi?
 */
export function clearAllChats(includeStartedChats = false) {
    const chatsToRemove = state.getChats()
        .filter(chat => includeStartedChats || !chat.messages.some(msg => msg.isUser))
        .map(chat => chat.id);

    if (chatsToRemove.length === 0) {
        alert(includeStartedChats ? 'Temizlenecek sohbet yok.' : 'Temizlenecek, başlanmamış sohbet yok.');
        return;
    }

    chatsToRemove.forEach(id => removeChat(id, !includeStartedChats));
    alert(`${chatsToRemove.length} sohbet temizlendi.`);
}

/**
 * Bir sohbete mesaj gönderir.
 * @param {string} chatId - Sohbetin ID'si.
 * @param {string} text - Gönderilecek mesaj metni.
 */
export async function sendMessage(chatId, text) {
    log('action', 'ChatService', `Mesaj gönderiliyor: ${chatId}`);
    const chat = state.getChatById(chatId);
    if (!chat) return;

    // 1. Kullanıcı mesajını state'e ve UI'a ekle
    const userMessage = { isUser: true, text, timestamp: Date.now() };
    state.addMessageToChat(chatId, userMessage);
    addMessageToWindow(chatId, userMessage);

    const isFirstUserMessage = chat.messages.filter(m => m.isUser).length === 1;
    if (isFirstUserMessage) {
        updateChatWindow(chatId); // Model kilidini göstermek için pencereyi güncelle
        renderAll(); // Dropdown menüyü güncellemek için
    }

    // 2. Yükleniyor mesajını göster
    const loadingMessageId = showLoadingMessage(chatId);

    try {
        // 3. API'ye gönderilecek geçmişi hazırla
        const conversationHistoryForAPI = chat.messages
            .slice(0, -1) // Son kullanıcı mesajını hariç tut
            .filter(msg => msg.text && String(msg.text).trim() !== '')
            .map(msg => ({ role: msg.isUser ? 'user' : 'model', parts: [{ text: String(msg.text).trim() }] }));

        // 4. API'yi çağır
        const data = await sendMessageToServer({
            chatId: chatId,
            aiModelId: chat.aiModelId,
            chat_message: text,
            history: conversationHistoryForAPI
        });

        // 5. AI yanıtını state'e ve UI'a ekle
        const aiMessage = { isUser: false, text: data.response, timestamp: Date.now() };
        state.addMessageToChat(chatId, aiMessage);
        updateLoadingMessage(chatId, loadingMessageId, aiMessage);

    } catch (error) {
        log('error', 'ChatService', 'Mesaj gönderme/alma hatası!', error);
        const errorMessageText = `Üzgünüm, bir sorun oluştu: ${error.message || 'Bilinmeyen sunucu hatası'}`;
        const aiErrorMessage = { isUser: false, text: errorMessageText, timestamp: Date.now(), isError: true };
        
        // Hata mesajını UI'da göster
        showErrorMessage(chatId, loadingMessageId, aiErrorMessage);
    }
}

/**
 * Tüm aktif sohbetlere yayın mesajı gönderir.
 * @param {string} messageText - Gönderilecek mesaj.
 */
export function sendBroadcastMessage(messageText) {
    const activeVisibleChats = state.getChats().filter(chat => !chat.isMinimized);
    if (activeVisibleChats.length === 0) {
        alert('Mesaj gönderilecek aktif sohbet yok.');
        return;
    }
    activeVisibleChats.forEach(chat => sendMessage(chat.id, `📢 **YAYIN:** ${messageText}`));
}

/**
 * Bir sohbetin AI modelini değiştirir.
 * @param {string} chatId - Sohbetin ID'si.
 * @param {string} newAiModelIdString - Yeni modelin ID'si (string).
 */
export function changeAIModel(chatId, newAiModelIdString) {
    const chat = state.getChatById(chatId);
    if (!chat || chat.messages.some(msg => msg.isUser)) {
        log('warn', 'ChatService', 'Model değiştirilemez (sohbet bulunamadı veya zaten başladı).');
        return;
    }
    const numericNewModelId = Number(newAiModelIdString);
    const modelExists = state.getAiModelById(numericNewModelId);
    if (!modelExists) {
        log('error', 'ChatService', `Geçersiz model ID'si: ${numericNewModelId}`);
        return;
    }

    state.updateChatModel(chatId, numericNewModelId);
    updateChatWindow(chatId); // Pencere başlığını ve hoşgeldin mesajını güncelle
    renderAll(); // Dropdown'u güncelle
    log('info', 'ChatService', `Sohbet ${chatId} modeli değiştirildi: ${modelExists.name}`);
}
