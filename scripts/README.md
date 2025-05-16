# Veritabanı Yönetim Scriptleri

Bu dizin, veritabanı işlemlerini otomatikleştirmek için kullanılan Python scriptlerini içerir.

## Mevcut Scriptler

### add_gemini_model.py

Bu script, Google'ın Gemini API'sini kullanmak için gerekli model yapılandırmasını veritabanına ekler.

#### Kurulum

1. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install python-dotenv
   ```

2. `.env` dosyanızın proje kök dizininde olduğundan ve veritabanı bağlantı bilgilerini içerdiğinden emin olun:
   ```
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=your_database
   ```

#### Kullanım

1. Scripti çalıştırın:
   ```bash
   python scripts/add_gemini_model.py
   ```

2. Başarılı bir şekilde çalıştığında, aşağıdaki gibi bir çıktı görmelisiniz:
   ```
   AI kategorisi oluşturuldu.
   Gemini modeli başarıyla eklendi. Model ID: 1
   ```

#### Ne Yapar?

1. "AI Models" adında bir kategori oluşturur (eğer yoksa).
2. Gemini 2.0 Flash modelini veritabanına ekler.
3. Modelin API yapılandırmasını ayarlar (URL, istek metodu, başlıklar, vb.).
4. Güvenlik ayarlarını ve oluşturma parametrelerini yapılandırır.

#### Özellikler

- Otomatik kategori oluşturma
- Hata yönetimi ve loglama
- Güvenli veritabanı bağlantı yönetimi
- JSON tabanlı esnek yapılandırma

#### Gereksinimler

- Python 3.7+
- `python-dotenv` paketi
- Geçerli bir veritabanı bağlantısı
