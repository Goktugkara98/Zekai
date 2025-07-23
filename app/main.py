import sys
import os
import secrets
import logging

# Projenin kök dizinini (app klasörünün ebeveyni olan Zekai klasörü) sys.path'e ekle.
# Bu, app/main.py'den bir üst dizin.
# Böylece 'from app.models import ...' gibi importlar çalışır.
PACKAGE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_PARENT not in sys.path:
    sys.path.insert(0, PACKAGE_PARENT)

from flask import Flask
from flask_cors import CORS
from app.models.migrations import DatabaseMigrations  # app. öneki eklendi
from app.routes.main_routes import main_bp  # app. öneki eklendi
from app.routes.admin_routes import admin_bp  # app. öneki eklendi

# Uygulama oluştur
app = Flask(__name__)

# Uygulama yapılandırması
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(16)),
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=False,
    USE_MOCK_API='false'  # Test için mock modu
)

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# CORS'u etkinleştir
cors = CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Blueprint'leri kaydet
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    db_migrations = DatabaseMigrations()  # Veritabanı başlatıcıyı çağır
    db_migrations.create_all_tables()
    app.run(debug=True)
