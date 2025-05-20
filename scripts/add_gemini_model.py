# add_gemini_model.py
import os
import sys
import json
from typing import Optional

# Proje ana dizinini Python yoluna ekleyin
# Bu betiği projenizin ana dizininden çalıştırdığınızı varsayarsak (örn: python scripts/add_gemini_model.py)
# veya betiğin bulunduğu yere göre app dizininin yolunu ayarlamanız gerekebilir.
# Örnek: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Eğer betik projenin kök dizinindeyse bu satırlara genellikle gerek kalmaz.
# Eğer app klasörü ile aynı seviyede bir scripts klasöründe ise:
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..')) 
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from app.models.base import DatabaseConnection
    from app.repositories.model_repository import ModelRepository
    from app.repositories.category_repository import CategoryRepository
    from app.config import DB_CONFIG # DB_CONFIG'in app.config içinde tanımlı olduğunu varsayıyoruz
except ImportError as e:
    print(f"Hata: Gerekli modüller yüklenemedi. Lütfen PYTHONPATH ayarlarınızı kontrol edin veya betiği doğru konumdan çalıştırın.")
    print(f"Import Hatası: {e}")
    print(f"Mevcut Python Yolu: {sys.path}")
    sys.exit(1)

# --- YENİ MODELİN BİLGİLERİ ---
GEMINI_API_KEY = "AIzaSyAkd4grtdow3141FUfsfzYxxaSc5_5xee4" # !!! API Anahtarınızı buraya girin !!!

MODEL_NAME = "Gemini 2.0 Flash"
MODEL_ICON = "fas fa-bolt" # Font Awesome ikonu
MODEL_DESCRIPTION = "Google tarafından geliştirilen hızlı ve verimli bir AI modeli."
MODEL_DETAILS = {
    "version": "2.0-flash",
    "provider": "Google Generative Language API",
    "capabilities": ["Metin üretimi", "Sohbet", "Soru yanıtlama"],
    "notes": "Hızlı yanıtlar için optimize edilmiştir."
}
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent" # Key olmadan temel URL
# API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" # Eğer bu endpoint doğruysa
REQUEST_METHOD = "POST"
REQUEST_HEADERS = {
    "Content-Type": "application/json"
}
# İstek gövdesinde kullanıcı girdisi için bir yer tutucu kullanalım
REQUEST_BODY_TEMPLATE = {
    "contents": [
        {
            "parts": [
                {
                    "text": "{user_prompt}" # Uygulama bu yer tutucuyu kullanıcı girdisiyle değiştirecek
                }
            ]
        }
    ]
}
# Gemini API'sinin yanıtından metni çıkarmak için JSON yolu
# Örnek yanıt: {"candidates": [{"content": {"parts": [{"text": "Yanıt..."}]}}]}
RESPONSE_PATH = "candidates.0.content.parts.0.text"

# --- KATEGORİ BİLGİLERİ ---
CATEGORY_NAME = "Sohbet ve Metin Üretimi"
CATEGORY_ICON = "fas fa-comments" # Font Awesome ikonu

def ensure_category_exists(category_repo: CategoryRepository, name: str, icon: str) -> Optional[int]:
    """
    Belirtilen isimde bir kategori olup olmadığını kontrol eder.
    Yoksa oluşturur ve kategori ID'sini döndürür.
    """
    print(f"'{name}' kategorisi kontrol ediliyor...")
    category = category_repo.get_category_by_name(name)
    if category:
        print(f"Kategori '{name}' zaten mevcut (ID: {category.id}).")
        return category.id
    else:
        print(f"Kategori '{name}' bulunamadı, oluşturuluyor...")
        success, message, category_id = category_repo.create_category(name, icon)
        if success:
            print(f"Kategori '{name}' başarıyla oluşturuldu (ID: {category_id}). Mesaj: {message}")
            return category_id
        else:
            print(f"HATA: Kategori '{name}' oluşturulamadı. Mesaj: {message}")
            return None

def main():
    """Ana betik fonksiyonu."""
    if GEMINI_API_KEY == "BURAYA_GEMINI_API_ANAHTARINIZI_GIRIN" or not GEMINI_API_KEY:
        print("Lütfen betik içerisindeki GEMINI_API_KEY değişkenine geçerli bir API anahtarı girin.")
        return

    print("Veritabanı bağlantısı ve depolar hazırlanıyor...")
    try:
        # Veritabanı bağlantısını oluştur
        db_connection = DatabaseConnection()
        
        # Repository'leri başlat ve aynı bağlantıyı kullan
        category_repo = CategoryRepository(db_connection)
        model_repo = ModelRepository(db_connection)
    except Exception as e:
        print(f"HATA: Depolar başlatılırken bir sorun oluştu: {e}")
        print("DB_CONFIG ayarlarınızın doğru olduğundan ve veritabanının çalıştığından emin olun.")
        return

    # 1. Kategori varlığını kontrol et veya oluştur
    category_id = ensure_category_exists(category_repo, CATEGORY_NAME, CATEGORY_ICON)
    if category_id is None:
        print("Model ekleme işlemi için kategori ID'si alınamadı. Betik sonlandırılıyor.")
        return

    # 2. Modeli oluştur
    print(f"\n'{MODEL_NAME}' modeli veritabanına ekleniyor...")
    success, message, model_id = model_repo.create_model(
        category_id=category_id,
        name=MODEL_NAME,
        icon=MODEL_ICON,
        description=MODEL_DESCRIPTION,
        details=MODEL_DETAILS,
        api_url=API_URL,
        request_method=REQUEST_METHOD,
        request_headers=REQUEST_HEADERS,
        request_body=REQUEST_BODY_TEMPLATE,
        response_path=RESPONSE_PATH,
        api_key=GEMINI_API_KEY # API anahtarı burada veriliyor
    )

    if success:
        print(f"\nBAŞARILI: Model '{MODEL_NAME}' (ID: {model_id}) veritabanına eklendi.")
        print(f"Mesaj: {message}")
    else:
        print(f"\nHATA: Model '{MODEL_NAME}' eklenemedi.")
        print(f"Mesaj: {message}")

if __name__ == "__main__":
    # Veritabanı tablolarının oluşturulduğundan emin olmak için migrations.py'deki
    # initialize_database() fonksiyonunu burada çağırabilirsiniz, ancak bu genellikle
    # uygulamanın ana başlangıç noktasında yapılır.
    # from app.models.migrations import initialize_database
    # print("Veritabanı tabloları kontrol ediliyor/oluşturuluyor...")
    # if not initialize_database():
    #     print("HATA: Veritabanı tabloları oluşturulamadı. Lütfen migrations.py'yi kontrol edin.")
    #     sys.exit(1)
    # print("Veritabanı tabloları hazır.")
    
    main()
