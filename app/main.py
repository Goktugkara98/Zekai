import sys
import os
import logging
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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Blueprint'leri merkezi kayıt fonksiyonu ile kaydet
register_blueprints(app)

if __name__ != "__main__":
    # Gunicorn altında çalışıyorsak
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    # Standalone çalışırken temel logging yapılandırması
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        force=True)

    # Veritabanı migration'larını çalıştır
    app.logger.info("Starting database migrations...")
    run_all_migrations()
    app.logger.info("Database migrations completed.")

    # Migration sonrası başlangıç verilerini (seed) yükle
    app.logger.info("Running database seeders...")
    run_all_seeders()
    app.logger.info("Database seeders completed.")

    # Programı çalıştır
    app.logger.info("Starting Flask application in debug mode...")
    app.run(debug=True)
