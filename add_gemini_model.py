import os
import sys
import io
from dotenv import load_dotenv

# Windows'ta UnicodeEncodeError hatasını önlemek için stdout kodlamasını ayarla
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.base import DatabaseConnection
from app.repositories.category_repository import CategoryRepository
from app.repositories.model_repository import ModelRepository

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

def add_gemini_model():
    """
    Veritabanına Gemini API için gerekli olan kategoriyi ve modeli ekler.
    """
    db_connection = None
    try:
        print("Veritabanı bağlantısı hazırlanıyor...")
        # Depo (repository) sınıfları, gerektiğinde bağlantıyı kendileri kuracaktır.
        db_connection = DatabaseConnection()

        category_repo = CategoryRepository(db_connection)
        model_repo = ModelRepository(db_connection)

        # --- 1. Kategori Oluştur ---
        category_name = "Sohbet ve Diyalog"
        category_icon = "bi bi-chat-dots-fill"
        print(f"\n'__{category_name}__' kategorisi kontrol ediliyor...")

        category = category_repo.get_category_by_name(category_name)
        if category:
            category_id = category.id
            print(f"Kategori zaten mevcut (ID: {category_id}).")
        else:
            print(f"Kategori bulunamadı, yeni kategori oluşturuluyor...")
            success, message, category_id = category_repo.create_category(name=category_name, icon=category_icon)
            if not success:
                print(f"HATA: Kategori oluşturulamadı: {message}")
                return
            print(message)

        if not category_id:
            print("HATA: Kategori ID'si alınamadı. İşlem durduruldu.")
            return

        # --- 2. Gemini Modeli Ekle ---
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("\nHATA: .env dosyasında GEMINI_API_KEY bulunamadı.")
            print("Lütfen projenizin ana dizininde .env adında bir dosya oluşturun ve içine aşağıdaki satırı ekleyin:")
            print("GEMINI_API_KEY='YOUR_API_KEY_HERE'")
            return

        model_name = "Gemini Pro"
        print(f"\n'__ {model_name}__' modeli ekleniyor...")

        success, message, model_id = model_repo.create_model(
            category_id=category_id,
            name=model_name,
            icon="bi bi-google",
            description="Google tarafından geliştirilen, çok modlu ve güçlü bir sohbet modeli.",
            service_provider="gemini_service",
            external_model_name="gemini-1.5-pro-latest",
            api_key=gemini_api_key,
            status="active"
        )

        if success:
            print(f"BAŞARILI: {message}")
        else:
            print(f"HATA: Model eklenemedi: {message}")

    except Exception as e:
        print(f"\nBeklenmedik bir hata oluştu: {e}")
    finally:
        if db_connection:
            db_connection.close()
            print("\nVeritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    add_gemini_model()
