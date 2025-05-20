import sys
import os
import json # MODEL_DETAILS için
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# --- Proje Kök Dizinini Python Path'e Ekleme ---
# Bu script'in 'scripts' klasöründe olduğunu varsayar
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # scripts klasöründen bir üst dizine çık
    sys.path.insert(0, project_root)
    
    # Doğrudan repository modülünü import et
    from app.repositories.model_repository import ModelRepository
    from app.repositories.category_repository import CategoryRepository
    from app.models.base import DatabaseConnection
    
    print(f"Proje kök dizini: {project_root}")
    print("Modüller başarıyla import edildi.")
    
except ImportError as e:
    print(f"Gerekli modüller import edilirken hata oluştu: {e}")
    print("Lütfen script'in doğru konumda olduğundan ve 'app' paketinin Python path'inde bulunduğundan emin olun.")
    sys.exit(1)
except Exception as e:
    print(f"Script başlangıcında bir hata oluştu: {e}")
    sys.exit(1)

# --- Configuration ---
# ÖNEMLİ: Bu değerleri kendi ortamınıza ve ihtiyaçlarınıza göre güncelleyin.

# Veritabanı Bağlantı Parametreleri (EĞER BaseRepository bu şekilde parametre alıyorsa)
# BaseRepository'niz bağlantıyı ortam değişkenlerinden veya bir config dosyasından okuyorsa,
# bu kısım gerekmeyebilir veya BaseRepository'nin beklentisine göre ayarlanmalıdır.
DB_PARAMS = {
    "host": "localhost",
    "user": "your_db_user",
    "password": "your_db_password",
    "database": "your_db_name"
}

# Eklenecek Model Bilgileri
MODEL_CATEGORY_ID = 1  # ÖNEMLİ: Modeliniz için doğru kategori ID'sini ayarlayın.
MODEL_NAME = "Gemini 2.0 Flash"
MODEL_ICON = "fas fa-bolt"  # Örnek: Font Awesome ikon sınıfı veya None
# API URL'sinden API anahtarını çıkardık. Uygulamanız anahtarı ayrıca yönetmeli.
MODEL_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
MODEL_DATA_AI_INDEX = "gemini-2.0-flash"  # Benzersiz olmalı
MODEL_DESCRIPTION = "Google'ın içerik üretimi için hız ve verimlilik odaklı Gemini 2.0 Flash modeli. Metin tabanlı girdileri destekler."
MODEL_DETAILS = {
    "model_family": "Gemini",
    "version": "2.0 Flash (kullanıcı tarafından belirtilen)",
    "provider": "Google",
    "input_type": "text",
    "output_type": "text",
    "notes": "API isteğinde API Anahtarı gereklidir. API URL'si 'generateContent' metodu içindir. API anahtarı uygulamada güvenli bir şekilde yönetilmelidir.",
    "example_request_body": {
        "contents": [{
            "parts": [{"text": "Explain how AI works"}]
        }]
    },
    "official_documentation": "https://ai.google.dev/gemini-api/docs/models/gemini",
    "capabilities": ["Metin Üretimi", "Özetleme", "Soru-Cevap", "Sınıflandırma"]
}
MODEL_IMAGE_FILENAME = "gemini_flash.png"  # İsteğe bağlı: model için bir görsel dosya adı veya None

def ensure_ai_category_exists(db_conn):
    """AI kategorisinin varlığını kontrol eder, yoksa oluşturur."""
    category_repo = CategoryRepository(db_conn)
    
    try:
        # AI kategorisini kontrol et
        categories = category_repo.get_all_categories()
        
        ai_category = next((cat for cat in categories if cat.name.lower() == 'ai models'), None)
        
        # Eğer AI kategorisi yoksa oluştur
        if not ai_category:
            success, message, category_id = category_repo.create_category(
                name="AI Models",
                icon="fas fa-robot"  # Varsayılan bir ikon
            )
            if not success:
                print(f"AI kategorisi oluşturulamadı: {message}")
                return None
            print("AI kategorisi oluşturuldu.")
            return category_id
        
        # Kategori zaten varsa mevcut ID'yi döndür
        return ai_category.id
        
    except Exception as e:
        print(f"Kategori kontrolü sırasında hata oluştu: {str(e)}")
        return None

def main():
    print("Gemini 2.0 Flash modeli veritabanına eklenmeye çalışılıyor...")

    # Veritabanı bağlantısını oluştur
    db_conn = DatabaseConnection()
    print("Veritabanı bağlantısı oluşturuldu.")
    
    try:
        # AI kategorisini kontrol et ve gerekirse oluştur
        category_id = ensure_ai_category_exists(db_conn)
        if not category_id:
            print("Hata: AI kategorisi oluşturulamadı.")
            return
            
        # ModelRepository'i oluştur
        repo = ModelRepository(db_conn)
        print("ModelRepository başarıyla oluşturuldu.")

    except TypeError as te: # Genellikle __init__ argümanları uyuşmadığında alınır
        print(f"ModelRepository oluşturulurken TypeError oluştu: {te}")
        print("BaseRepository'nizin __init__ metodu argüman bekliyor olabilir.")
        print("Lütfen script içerisindeki 'ModelRepository'i Örnekleme' bölümünü ve")
        print("app.models.base.BaseRepository sınıfınızı kontrol edin.")
        print(f"Eğer DB_PARAMS gibi bir argüman gerekiyorsa: repo = ModelRepository(db_connection_params=DB_PARAMS) şeklinde deneyin.")
        return
    except Exception as e:
        print(f"ModelRepository oluşturulurken hata: {e}")
        print("Lütfen app.models.base.BaseRepository sınıfınızın veritabanı bağlantıları için doğru şekilde yapılandırıldığından emin olun.")
        return

    try:
        # Bu data_ai_index ile bir model zaten var mı kontrol et
        print(f"'{MODEL_DATA_AI_INDEX}' data_ai_index'ine sahip model kontrol ediliyor...")
        existing_model = repo.get_model_by_data_ai_index(MODEL_DATA_AI_INDEX)
        if existing_model:
            print(f"'{MODEL_DATA_AI_INDEX}' data_ai_index ({existing_model.name}) ID:{existing_model.id} ile zaten mevcut. Ekleme işlemi atlanıyor.")
            return # Fonksiyondan çık

        print("Yeni model oluşturuluyor...")
        
        # API yapılandırmasını details içinde sakla
        api_config = {
            'request_method': 'POST',
            'request_headers': {
                'Content-Type': 'application/json'
            },
            'request_body_template': {
                'contents': [{
                    'parts': [{
                        'text': '{user_message}'
                    }]
                }],
                'generationConfig': {
                    'temperature': 0.9,
                    'topK': 1,
                    'topP': 1,
                    'maxOutputTokens': 2048,
                    'stopSequences': []
                },
                'safetySettings': [
                    {
                        'category': 'HARM_CATEGORY_HARASSMENT',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    },
                    {
                        'category': 'HARM_CATEGORY_HATE_SPEECH',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    },
                    {
                        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    },
                    {
                        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    }
                ]
            },
            'response_path': 'candidates.0.content.parts.0.text'
        }
        
        # Debug bilgisi yazdır
        print("\nAPI Yapılandırması (details):\n", json.dumps(api_config, indent=2, ensure_ascii=False))
        
        # Modeli oluştur
        success, message, model_id = repo.create_model(
            category_id=category_id,  # AI kategorisinden alınan ID'yi kullan
            name='Gemini 2.0 Flash',
            icon='fas fa-robot',
            api_url='https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
            data_ai_index='gemini-2.0-flash',
            description='Google\'un gelişmiş çoklu modlu AI modeli',
            details=api_config
        )

        if success:
            print(f"'{MODEL_NAME}' modeli başarıyla eklendi! Yeni Model ID: {model_id}")
        else:
            print(f"'{MODEL_NAME}' modeli eklenemedi. Hata: {message}")

    except Exception as e:
        print(f"Model ekleme/kontrol sırasında bir hata oluştu: {e}")
    finally:
        # Veritabanı bağlantısını kapatma (eğer BaseRepository böyle bir metod sağlıyorsa)
        # Standalone scriptler için iyi bir pratiktir.
        if repo and hasattr(repo, 'close_connection') and callable(repo.close_connection):
            try:
                repo.close_connection()
                print("Veritabanı bağlantısı kapatıldı.")
            except Exception as e:
                print(f"Veritabanı bağlantısı kapatılırken hata oluştu: {e}")
        elif repo and hasattr(repo, 'db') and hasattr(repo.db, 'close') and callable(repo.db.close):
             # Eğer repo.db doğrudan bağlantı nesnesiyse
            try:
                repo.db.close()
                print("Veritabanı bağlantısı (repo.db.close()) kapatıldı.")
            except Exception as e:
                print(f"Veritabanı bağlantısı (repo.db.close()) kapatılırken hata oluştu: {e}")


if __name__ == "__main__":
    # ÖNEMLİ UYARILAR:
    # 1. Bu script, 'app' klasörünün (models.model_repository, models.base, models.entities içeren)
    #    Python'un import yolunda (sys.path) olduğunu varsayar.
    #    Scriptin başındaki sys.path.insert satırı bunu yönetmeye çalışır.
    #    İçe aktarmaların doğru çalışması için yolları ayarlamanız veya bu script'i
    #    belirli bir dizinden (örn: proje kök dizini) çalıştırmanız gerekebilir.
    #
    # 2. Veritabanı sunucunuzun çalıştığından ve (eğer BaseRepository DB_PARAMS'ı
    #    kullanacak şekilde ayarlandıysa) sağlanan kimlik bilgileriyle erişilebilir
    #    olduğundan emin olun.
    #
    # 3. MODEL_CATEGORY_ID'yi sisteminizdeki geçerli bir kategori ID'si ile güncelleyin.
    #    Aksi takdirde, create_model içindeki kategori kontrolü başarısız olabilir.

    main()