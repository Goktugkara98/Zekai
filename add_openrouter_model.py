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

def add_openrouter_model():
    """
    Veritabanına OpenRouter üzerinden erişilebilen bir modeli ekler.
    """
    db_connection = None
    try:
        print("Veritabanı bağlantısı hazırlanıyor...")
        db_connection = DatabaseConnection()
        category_repo = CategoryRepository(db_connection)
        model_repo = ModelRepository(db_connection)

        # --- 1. Kategori Kontrolü ---
        category_name = "Sohbet ve Diyalog"
        category_icon = "bi bi-chat-dots-fill"
        print(f"\n'__{category_name}__' kategorisi kontrol ediliyor...")

        category = category_repo.get_category_by_name(category_name)
        if category:
            category_id = category.id
            print(f"Kategori zaten mevcut (ID: {category_id}).")
        else:
            # Kategori yoksa oluştur (önceki betikler tarafından oluşturulmuş olmalı)
            print(f"Kategori bulunamadı, yeni kategori oluşturuluyor...")
            success, message, category_id = category_repo.create_category(name=category_name, icon=category_icon)
            if not success:
                print(f"HATA: Kategori oluşturulamadı: {message}")
                return
            print(message)

        if not category_id:
            print("HATA: Kategori ID'si alınamadı. İşlem durduruldu.")
            return

        # --- 2. OpenRouter Modeli Ekle ---
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key or openrouter_api_key == 'YOUR_OPENROUTER_KEY_HERE':
            print("\nHATA: .env dosyasında OPENROUTER_API_KEY bulunamadı veya güncellenmemiş.")
            print("Lütfen .env dosyasını kontrol edin.")
            return

        model_name = "Claude 3.5 Sonnet (OpenRouter)"
        print(f"\n'__ {model_name}__' modeli ekleniyor...")

        success, message, model_id = model_repo.create_model(
            category_id=category_id,
            name=model_name,
            icon="bi bi-person-bounding-box", # Anthropic/Claude için bir ikon
            description="Anthropic tarafından geliştirilen, OpenRouter üzerinden erişilebilen güçlü ve dengeli bir model.",
            service_provider="openai_router_service", # Yeni servis sağlayıcı
            external_model_name="anthropic/claude-3.5-sonnet", # OpenRouter model ID'si
            api_url="https://openrouter.ai/api/v1/chat/completions", # OpenRouter API endpoint'i
            api_key=openrouter_api_key,
            status="active"
        )

        if success:
            print(f"BAŞARILI: {message}")
        else:
            if "zaten mevcut" in message:
                print(f"BİLGİ: Model '{model_name}' zaten veritabanında mevcut.")
            else:
                print(f"HATA: Model eklenemedi: {message}")

    except Exception as e:
        print(f"\nBeklenmedik bir hata oluştu: {e}")
    finally:
        if db_connection:
            db_connection.close()
            print("\nVeritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    add_openrouter_model()
