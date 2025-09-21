import sys
import os
from flask import Flask
from dotenv import load_dotenv

# Projenin kök dizinini sys.path'e ekle
PACKAGE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_PARENT not in sys.path:
    sys.path.insert(0, PACKAGE_PARENT)

# .env dosyasını yükle
load_dotenv()

from app.database.run_migrations import run_all_migrations
from app.database.run_seeders import run_all_seeders
from app.routes import register_blueprints

# Flask uygulaması oluştur
app = Flask(__name__)

# Config'i .env'den çek
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Blueprint'leri merkezi kayıt fonksiyonu ile kaydet
register_blueprints(app)

if __name__ == '__main__':
    # Veritabanı migration'larını çalıştır
    run_all_migrations()
    
    # Migration sonrası başlangıç verilerini (seed) yükle
    run_all_seeders()
    
    # Programı çalıştır
    app.run(debug=True)
