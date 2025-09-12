# Model Setup Guide

Bu kılavuz, Zekai AI uygulamasına model ekleme ve yapılandırma sürecini açıklar.

## 📋 Mevcut Scriptler

### 1. `add_gemini_models.py`
- Gemini 2.5 Flash ve 2.5 Pro modellerini ekler
- Kullanım: `py add_gemini_models.py`

### 2. `add_openrouter_models.py`
- OpenRouter üzerinden erişilebilen modelleri ekler
- GPT-4o, Claude 3.5, Llama 3.1, vs.
- Kullanım: `py add_openrouter_models.py`

### 3. `add_all_models.py`
- Tüm modelleri tek seferde ekler
- Kullanım: `py add_all_models.py`

### 4. `update_api_keys.py`
- API anahtarlarını günceller
- Kullanım: `py update_api_keys.py`

### 5. `test_models.py`
- Modelleri test eder
- Kullanım: `py test_models.py`

## 🚀 Kurulum Adımları

### Adım 1: Modelleri Ekle
```bash
# Tüm modelleri ekle
py add_all_models.py
```

### Adım 2: API Anahtarlarını Güncelle
```bash
# API anahtarlarını güncelle
py update_api_keys.py
```

### Adım 3: Test Et
```bash
# Modelleri test et
py test_models.py
```

### Adım 4: Uygulamayı Başlat
```bash
cd app
py main.py
```

## 🔑 API Anahtarları

### Gemini API Key
1. [Google AI Studio](https://aistudio.google.com/) adresine gidin
2. API key oluşturun
3. `update_api_keys.py` scriptini çalıştırın
4. Gemini API key'ini girin

### OpenRouter API Key
1. [OpenRouter](https://openrouter.ai/) adresine gidin
2. Hesap oluşturun ve API key alın
3. `update_api_keys.py` scriptini çalıştırın
4. OpenRouter API key'ini girin

## 📊 Desteklenen Modeller

### Gemini Modelleri
- `gemini-2.5-flash` - Hızlı ve verimli
- `gemini-2.5-pro` - Gelişmiş yetenekler

### OpenRouter Modelleri
- `openai/gpt-4o` - OpenAI GPT-4o
- `openai/gpt-4o-mini` - OpenAI GPT-4o Mini
- `anthropic/claude-3.5-sonnet` - Anthropic Claude 3.5 Sonnet
- `anthropic/claude-3.5-haiku` - Anthropic Claude 3.5 Haiku
- `meta-llama/llama-3.1-8b-instruct` - Meta Llama 3.1 8B
- `meta-llama/llama-3.1-70b-instruct` - Meta Llama 3.1 70B
- `google/gemini-pro` - Google Gemini Pro
- `google/gemini-pro-vision` - Google Gemini Pro Vision
- `mistralai/mistral-7b-instruct` - Mistral 7B
- `mistralai/mixtral-8x7b-instruct` - Mixtral 8x7B

## 🔧 Sorun Giderme

### Model Görünmüyor
1. `test_models.py` çalıştırın
2. API key'lerin doğru olduğundan emin olun
3. Veritabanı bağlantısını kontrol edin

### API Hatası
1. API key'in geçerli olduğundan emin olun
2. İnternet bağlantısını kontrol edin
3. Provider'ın servis durumunu kontrol edin

### Veritabanı Hatası
1. MySQL servisinin çalıştığından emin olun
2. Veritabanı bağlantı ayarlarını kontrol edin
3. Migration'ların çalıştığından emin olun

## 📝 Notlar

- API anahtarları güvenli bir şekilde saklanmalıdır
- Test modelleri için ücretsiz tier'ları kullanabilirsiniz
- Production'da rate limit'leri göz önünde bulundurun
- Model performanslarını düzenli olarak test edin
