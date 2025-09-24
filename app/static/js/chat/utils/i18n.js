/**
 * Simple i18n Utility for Zekai Chat
 * Provides t(key, params) and apply(root) to update DOM with [data-i18n]
 */

import { Helpers } from './helpers.js';

const translations = {
  tr: {
    common: {
      app_welcome_title: 'Zekai',
      app_welcome_desc: 'Sohbete başlamak için kenar çubuğundan bir model seçin',
      prompts: 'İpuçları',
      send: 'Gönder',
      layout_single: 'Tek',
      layout_vertical: 'Dikey',
      layout_horizontal: 'Yatay',
      layout_grid: 'Izgara',
      layout_image: 'Görsel',
      primary: 'ÖN TANIMLI',
      chat_mode: 'Sohbet Modu',
      agent_mode: 'Ajan Modu',
      locked: 'Kilitli',
      coming_soon: 'Yakında',
      attachments_coming_soon: 'Dosya ekleme özelliği yakında!',
      favorite_models: 'FAVORİ MODELLER',
      all_models: 'TÜM MODELLER',
      categories: 'KATEGORİLER',
      ai_models: 'YAPAY ZEKA MODELLERİ',
      manage_models: 'Modelleri Yönet',
      no_ai_models: 'Aktif model bulunmuyor',
      ai_models_hint: 'Modelleri Yönet bölümünden modelleri etkinleştirin',
      loading_models: 'Modeller yükleniyor...',
      sidebar_chats_title: 'Sohbet Alanı',
      sidebar_chats_subtitle: 'Aktif veya geçmiş konuşmaları yönetin',
      sidebar_active_chats: 'Aktif Sohbetler',
      sidebar_active_desc: 'Açık pencereleri hızlıca yönet',
      sidebar_history: 'Sohbet Geçmişi',
      sidebar_history_desc: 'Eski konuşmaları tekrar incele',
      active_chats: 'AKTİF SOHBETLER',
      chat_history: 'SOHBET GEÇMİŞİ',
      profile_settings: 'Profil ve Ayarlar',
      user_label: 'Kullanıcı',
      assistant_label: 'Asistan',
      dark_mode_on: 'Karanlık mod etkinleştirildi',
      dark_mode_off: 'Karanlık mod kapatıldı',
      notifications_on: 'Bildirimler açık',
      notifications_off: 'Bildirimler kapalı',
      language_changed: 'Dil değiştirildi: {{lang}}',
      logout_mock: 'Çıkış işlemi (mock)',
      no_favorite_models: 'Favori model yok',
      no_models_found: 'Model bulunamadı',
      fav_hint: 'Favorilere eklemek için yıldız ikonuna tıklayın',
      categories_loading: 'Kategoriler yükleniyor...',
      categories_failed: 'Kategoriler yüklenemedi',
      categories_empty: 'Kategori bulunamadı',
      category_models_title: '{{category}} Modelleri',
      assistant_title: 'Önerilen Modeller',
      assistant_query: 'Sorgu:',
      assistant_loading: 'Mesaj analiz ediliyor...',
      start_chat: 'Sohbeti Başlat',
      max_panes_warning: 'En fazla {{count}} sohbet penceresi görüntülenebilir. Lütfen birini minimize edin veya kapatın.',
      limit_auto_minimized: 'Limit {{count}}. Yeni sohbet otomatik minimize edildi.',
      history_limit_auto_minimized: 'Limit {{count}}. Geçmişten açılan sohbet otomatik minimize edildi.',
      history_missing: 'Bu sohbet geçmişi mevcut oturumda bulunamadı.',
      chat_create_failed: 'Chat oluşturulamadı: {{error}}',
      internet_online: 'İnternet bağlantısı sağlandı',
      internet_offline: 'İnternet bağlantısı kesildi',
      assistant_service_missing: 'Asistan servisi mevcut değil',
      suggestions_failed: 'Öneriler alınamadı',
      assistant_error: 'Asistan hatası',
      file_uploaded: '"{{name}}" dosyası başarıyla yüklendi!',
      file_too_large: 'Dosya çok büyük (maksimum 10MB)',
      file_type_not_supported: 'Desteklenmeyen dosya türü',
      message_with_model: 'Seçili model {{model}} ile sohbet etmek için mesajınızı yazın...',
      message_placeholder: 'Sorunuzu veya isteğinizi buraya yazın; gönderdiğinizde uygun model önerileri gösterilir veya seçtiğiniz modelle sohbet başlar.',
      start_with_model: '{{model}} ile bir konuşma başlatın',
      shift_enter_hint: 'Yeni satır eklemek için Shift+Enter kullanın.',
      label_dark_mode: 'Karanlık Mod',
      label_notifications: 'Bildirimler',
      label_language: 'Dil',
      logout: 'Çıkış Yap',
      loading_btn: 'Yükleniyor...',
      copied: 'Kopyalandı!',
      general_purpose: 'Genel amaçlı başlangıç önerisi',
      general_purpose_offline: 'Genel amaçlı başlangıç önerisi (çevrimdışı)'
      ,
      // Base footer/nav
      footer_motto: 'AI destekli sohbet platformu ile geleceğin teknolojisini deneyimleyin.',
      quick_links: 'Hızlı Linkler',
      nav_home: 'Ana Sayfa',
      nav_chat: 'Sohbet',
      nav_about: 'Hakkımızda',
      contact: 'İletişim',
      rights_reserved: 'Tüm hakları saklıdır.',
      
      // Index/Landing page
      hero_subtitle: 'AI destekli sohbet platformu ile geleceğin teknolojisini deneyimleyin',
      cta_start_chat: 'Sohbete Başla',
      feature_fast_title: 'Hızlı',
      feature_fast_desc: 'Anında yanıt alın ve kesintisiz sohbet deneyimi yaşayın',
      feature_smart_title: 'Akıllı',
      feature_smart_desc: 'Gelişmiş AI modelleri ile doğal ve akıllı konuşmalar',
      feature_secure_title: 'Güvenli',
      feature_secure_desc: 'Verileriniz güvende, gizliliğiniz korunur',
      why_zekai_heading: 'Neden Zekai?',
      reasons_easy_title: 'Kolay Kullanım',
      reasons_easy_desc: 'Sade ve kullanıcı dostu arayüz ile kolayca sohbet edin',
      reasons_multi_title: 'Çoklu Model Desteği',
      reasons_multi_desc: 'Farklı AI modelleri arasında seçim yapın',
      reasons_247_title: '7/24 Erişim',
      reasons_247_desc: 'İstediğiniz zaman, istediğiniz yerde sohbet edin',
      reasons_advanced_title: 'Gelişmiş Özellikler',
      reasons_advanced_desc: 'Sohbet geçmişi, favoriler ve daha fazlası'
      ,
      // App/core errors
      unexpected_error: 'Beklenmeyen bir hata oluştu',
      app_init_failed: 'Uygulama başlatılamadı',
      
      // Chat pane
      chat_number: 'Sohbet #{{num}}',
      type_message: 'Mesajınızı yazın...',
      readonly_placeholder: 'Bu sohbet geçmişi görüntüleniyor. Mesaj gönderilemez.',
      minimize: 'Küçült',
      close: 'Kapat',
      error_prefix: 'Hata: {{msg}}',
      connection_error: 'Bağlantı hatası: {{msg}}',
      
      // Welcome messages
      welcome_gemini: 'Merhaba, ben Gemini. Bugün size nasıl yardımcı olabilirim?',
      welcome_gpt: 'Merhaba, ChatGPT burada. Size nasıl yardımcı olabilirim?',
      welcome_claude: 'Selam, ben Claude. Nasıl yardımcı olabilirim?',
      welcome_deepseek: 'Merhaba, DeepSeek olarak kod ve teknik konularda yardımcı olabilirim. Nereden başlayalım?',
      welcome_generic: 'Merhaba! {{model}} ile buradayım. Size nasıl yardımcı olabilirim?'
      ,
      // Prompts modal
      prompts_modal_title: 'İpuçları',
      prompts_creative: 'Yaratıcı Yazım',
      prompts_business: 'İş',
      prompts_technical: 'Teknik',
      prompts_education: 'Eğitim',
      write_short_story: '... hakkında kısa bir hikaye yaz',
      create_poem: '... hakkında bir şiir oluştur',
      write_dialogue: '... arasında bir diyalog yaz',
      write_business_plan: '... için bir iş planı yaz',
      create_marketing_strategy: '... için bir pazarlama stratejisi oluştur',
      analyze_market: '... için pazarı analiz et',
      explain_how_to: 'Nasıl ... yapılacağını açıkla',
      write_code_for: '... için kod yaz',
      debug_code: 'Şu kodu hata ayıkla...',
      teach_me_about: '... hakkında öğret',
      create_lesson_plan: '... için ders planı oluştur',
      explain_concept: '... kavramını açıkla',
      
      // Settings/Confirm/Alert
      settings_title: 'Ayarlar',
      settings_general: 'Genel',
      settings_theme: 'Tema',
      settings_language: 'Dil',
      settings_chat: 'Sohbet',
      auto_save_conversations: 'Sohbetleri otomatik kaydet',
      show_typing_indicator: 'Yazıyor göstergesini göster',
      cancel: 'İptal',
      save: 'Kaydet',
      confirm: 'Onayla',
      ok: 'Tamam',
      theme_light: 'Açık',
      theme_dark: 'Koyu',
      theme_auto: 'Otomatik',
      favorite: 'Favori',
      settings_saved_success: 'Ayarlar başarıyla kaydedildi!'
      ,
      models_manage_title: 'Modelleri Yönet',
      model_active: 'Aktif',
      model_inactive: 'Pasif',
      // Input validation and mock responses
      msg_too_long: 'Mesaj çok uzun (maksimum {{max}} karakter)',
      mock_response_1: 'Bu çok ilginç bir soru! Size nasıl yardımcı olabilirim?',
      mock_response_2: 'Anladım. Bu konuda size daha detaylı bilgi verebilirim.',
      mock_response_3: 'Harika bir nokta! Bu konuyu daha derinlemesine inceleyelim.',
      mock_response_4: 'Evet, bu konuda size yardımcı olabilirim. Hangi açıdan bakmak istersiniz?',
      mock_response_5: 'Bu sorunuzu yanıtlamak için biraz daha bilgiye ihtiyacım var.'
      ,
      // Models
      model_by_provider: '{{provider}} tarafından geliştirilen AI modeli',
      unknown_provider: 'Bilinmiyor'
      ,
      // Validation
      val_required_field: 'Bu alan gerekli',
      val_min_length: 'En az {{min}} karakter olmalı',
      val_max_length: 'En fazla {{max}} karakter olmalı',
      val_email: 'Geçerli bir email adresi girin',
      val_phone: 'Geçerli bir telefon numarası girin',
      val_url: 'Geçerli bir URL girin',
      val_alpha: 'Sadece harf içermeli',
      val_numeric: 'Sadece sayı içermeli',
      val_alphanumeric: 'Sadece harf ve sayı içermeli',
      val_invalid: 'Geçersiz değer',
      pw_min_length: 'En az 8 karakter olmalı',
      pw_lowercase: 'En az bir küçük harf içermeli',
      pw_uppercase: 'En az bir büyük harf içermeli',
      pw_digit: 'En az bir rakam içermeli',
      pw_special: 'En az bir özel karakter içermeli'
    },
  },
  en: {
    common: {
      app_welcome_title: 'Zekai',
      app_welcome_desc: 'Select a model from the sidebar to start chatting',
      prompts: 'Prompts',
      send: 'Send',
      layout_single: 'Single',
      layout_vertical: 'Vertical',
      layout_horizontal: 'Horizontal',
      layout_grid: 'Grid',
      layout_image: 'Image',
      primary: 'PRIMARY',
      chat_mode: 'Chat Mode',
      agent_mode: 'Agent Mode',
      locked: 'Locked',
      coming_soon: 'Coming soon',
      attachments_coming_soon: 'File attachments are coming soon!',
      favorite_models: 'FAVORITE MODELS',
      all_models: 'ALL MODELS',
      categories: 'CATEGORIES',
      ai_models: 'AI MODELS',
      manage_models: 'Manage Models',
      no_ai_models: 'No active models available',
      ai_models_hint: 'Enable models from Manage Models',
      loading_models: 'Loading models...',
      sidebar_chats_title: 'Conversation Hub',
      sidebar_chats_subtitle: 'Manage active or past chats',
      sidebar_active_chats: 'Active Chats',
      sidebar_active_desc: 'Quickly manage open panes',
      sidebar_history: 'Chat History',
      sidebar_history_desc: 'Revisit previous conversations',
      active_chats: 'ACTIVE CHATS',
      chat_history: 'CHAT HISTORY',
      profile_settings: 'Profile & Settings',
      user_label: 'User',
      assistant_label: 'Assistant',
      dark_mode_on: 'Dark mode enabled',
      dark_mode_off: 'Dark mode disabled',
      notifications_on: 'Notifications on',
      notifications_off: 'Notifications off',
      language_changed: 'Language changed: {{lang}}',
      logout_mock: 'Logout (mock)',
      no_favorite_models: 'No favorite models',
      no_models_found: 'No models found',
      fav_hint: 'Click the star icon to add favorites',
      categories_loading: 'Loading categories...',
      categories_failed: 'Failed to load categories',
      categories_empty: 'No categories found',
      category_models_title: '{{category}} Models',
      assistant_title: 'Recommended Models',
      assistant_query: 'Query:',
      assistant_loading: 'Analyzing the message...',
      start_chat: 'Start Chat',
      max_panes_warning: 'Up to {{count}} chat panes can be visible. Please minimize or close one.',
      limit_auto_minimized: 'Limit {{count}}. New chat was auto-minimized.',
      history_limit_auto_minimized: 'Limit {{count}}. History chat was auto-minimized.',
      history_missing: 'This chat history could not be found in the current session.',
      chat_create_failed: 'Failed to create chat: {{error}}',
      internet_online: 'Internet connection restored',
      internet_offline: 'Internet connection lost',
      assistant_service_missing: 'Assistant service not available',
      suggestions_failed: 'Failed to fetch suggestions',
      assistant_error: 'Assistant error',
      file_uploaded: 'File "{{name}}" uploaded successfully!',
      file_too_large: 'File is too large (max 10MB)',
      file_type_not_supported: 'Unsupported file type',
      message_with_model: 'Type your message to chat with {{model}}...',
      message_placeholder: 'Type your question or request here; when you send, we’ll recommend a suitable model or start chatting with your selected model.',
      start_with_model: 'Start a conversation with {{model}}',
      shift_enter_hint: 'Use Shift+Enter to add new line.',
      label_dark_mode: 'Dark Mode',
      label_notifications: 'Notifications',
      label_language: 'Language',
      logout: 'Logout',
      loading_btn: 'Loading...',
      copied: 'Copied!',
      general_purpose: 'General-purpose starting suggestion',
      general_purpose_offline: 'General-purpose starting suggestion (offline)'
      ,
      // Base footer/nav
      footer_motto: 'Experience the future of technology with an AI-powered chat platform.',
      quick_links: 'Quick Links',
      nav_home: 'Home',
      nav_chat: 'Chat',
      nav_about: 'About',
      contact: 'Contact',
      rights_reserved: 'All rights reserved.',
      
      // Index/Landing page
      hero_subtitle: 'Experience the future of technology with an AI-powered chat platform',
      cta_start_chat: 'Start Chatting',
      feature_fast_title: 'Fast',
      feature_fast_desc: 'Get instant responses and enjoy a seamless chat experience',
      feature_smart_title: 'Smart',
      feature_smart_desc: 'Natural and intelligent conversations with advanced AI models',
      feature_secure_title: 'Secure',
      feature_secure_desc: 'Your data is safe, your privacy protected',
      why_zekai_heading: 'Why Zekai?',
      reasons_easy_title: 'Easy to Use',
      reasons_easy_desc: 'Chat easily with a simple and user-friendly interface',
      reasons_multi_title: 'Multi-Model Support',
      reasons_multi_desc: 'Choose among different AI models',
      reasons_247_title: '24/7 Access',
      reasons_247_desc: 'Chat anytime, anywhere',
      reasons_advanced_title: 'Advanced Features',
      reasons_advanced_desc: 'Chat history, favorites and more'
      ,
      // App/core errors
      unexpected_error: 'An unexpected error occurred',
      app_init_failed: 'Failed to start the application',
      
      // Chat pane
      chat_number: 'Chat #{{num}}',
      type_message: 'Type your message...',
      readonly_placeholder: 'This chat history is read-only. You cannot send messages.',
      minimize: 'Minimize',
      close: 'Close',
      error_prefix: 'Error: {{msg}}',
      connection_error: 'Connection error: {{msg}}',
      
      // Welcome messages
      welcome_gemini: 'Hello, I\'m Gemini. How can I help you today?',
      welcome_gpt: 'Hello, ChatGPT here. How can I assist you?',
      welcome_claude: 'Hi, I\'m Claude. How can I help?',
      welcome_deepseek: 'Hello, I\'m DeepSeek. I can help with code and technical topics. Where should we start?',
      welcome_generic: 'Hello! I\'m here with {{model}}. How can I help you?'
      ,
      // Prompts modal
      prompts_modal_title: 'Prompts',
      prompts_creative: 'Creative Writing',
      prompts_business: 'Business',
      prompts_technical: 'Technical',
      prompts_education: 'Education',
      write_short_story: 'Write a short story about...',
      create_poem: 'Create a poem about...',
      write_dialogue: 'Write a dialogue between...',
      write_business_plan: 'Write a business plan for...',
      create_marketing_strategy: 'Create a marketing strategy for...',
      analyze_market: 'Analyze the market for...',
      explain_how_to: 'Explain how to...',
      write_code_for: 'Write code for...',
      debug_code: 'Debug this code...',
      teach_me_about: 'Teach me about...',
      create_lesson_plan: 'Create a lesson plan for...',
      explain_concept: 'Explain the concept of...',
      
      // Settings/Confirm/Alert
      settings_title: 'Settings',
      settings_general: 'General',
      settings_theme: 'Theme',
      settings_language: 'Language',
      settings_chat: 'Chat',
      auto_save_conversations: 'Auto-save conversations',
      show_typing_indicator: 'Show typing indicator',
      cancel: 'Cancel',
      save: 'Save',
      confirm: 'Confirm',
      ok: 'OK',
      theme_light: 'Light',
      theme_dark: 'Dark',
      theme_auto: 'Auto',
      favorite: 'Favorite',
      settings_saved_success: 'Settings saved successfully!'
      ,
      models_manage_title: 'Manage Models',
      model_active: 'Active',
      model_inactive: 'Inactive',
      // Input validation and mock responses
      msg_too_long: 'Message is too long (maximum {{max}} characters)',
      mock_response_1: 'That is a very interesting question! How can I help?',
      mock_response_2: 'Got it. I can provide more detailed information on this.',
      mock_response_3: 'Great point! Let’s explore this in more depth.',
      mock_response_4: 'Yes, I can help with that. What angle would you like to take?',
      mock_response_5: 'I need a bit more information to answer this question.'
      ,
      // Models
      model_by_provider: 'AI model by {{provider}}',
      unknown_provider: 'Unknown'
      ,
      // Validation
      val_required_field: 'This field is required',
      val_min_length: 'Must be at least {{min}} characters',
      val_max_length: 'Must be at most {{max}} characters',
      val_email: 'Please enter a valid email address',
      val_phone: 'Please enter a valid phone number',
      val_url: 'Please enter a valid URL',
      val_alpha: 'Letters only',
      val_numeric: 'Numbers only',
      val_alphanumeric: 'Letters and numbers only',
      val_invalid: 'Invalid value',
      pw_min_length: 'Must be at least 8 characters',
      pw_lowercase: 'Must include at least one lowercase letter',
      pw_uppercase: 'Must include at least one uppercase letter',
      pw_digit: 'Must include at least one digit',
      pw_special: 'Must include at least one special character'
    },
  },
};

const I18N_STORAGE_KEY = 'user_settings';

function interpolate(str, params = {}) {
  if (!str) return '';
  return String(str).replace(/{{\s*(\w+)\s*}}/g, (_, k) => (k in params ? params[k] : ''));
}

export const i18n = {
  lang: 'tr',
  init() {
    const defaults = { darkMode: false, notifications: true, language: 'tr' };
    const settings = Helpers.getStorage(I18N_STORAGE_KEY, defaults) || defaults;
    this.setLanguage(settings.language || 'tr', false);
  },
  setLanguage(lang, persist = true) {
    this.lang = (lang === 'en' ? 'en' : 'tr');
    try {
      document.documentElement.setAttribute('lang', this.lang);
    } catch (_) {}
    if (persist) {
      const defaults = { darkMode: false, notifications: true, language: this.lang };
      const settings = Object.assign({}, defaults, Helpers.getStorage(I18N_STORAGE_KEY, defaults) || {});
      settings.language = this.lang;
      Helpers.setStorage(I18N_STORAGE_KEY, settings);
    }
    this.apply();
  },
  t(key, params = {}) {
    const [ns, k] = key.includes(':') ? key.split(':') : ['common', key];
    const dict = translations[this.lang] && translations[this.lang][ns];
    const tr = (dict && dict[k]) || (translations['tr'] && translations['tr'][ns] && translations['tr'][ns][k]) || key;
    return interpolate(tr, params);
  },
  apply(root = document) {
    if (!root) return;
    try {
      const nodes = root.querySelectorAll('[data-i18n]');
      nodes.forEach(node => {
        const key = node.getAttribute('data-i18n');
        const attr = node.getAttribute('data-i18n-attr') || 'text';
        const value = this.t(key);
        if (attr === 'text') node.textContent = value;
        else if (attr === 'placeholder') node.setAttribute('placeholder', value);
        else if (attr === 'title') node.setAttribute('title', value);
        else node.setAttribute(attr, value);
      });
    } catch (_) {}
  }
};

// Expose on window for convenience
window.ZekaiI18n = i18n;
