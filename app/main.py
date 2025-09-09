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

# Database ve routes import
import importlib.util
import sys

# 0000_models.py dosyasını import et
spec = importlib.util.spec_from_file_location("models_migration", "app/database/migrations/0000_models.py")
models_migration = importlib.util.module_from_spec(spec)
sys.modules["models_migration"] = models_migration
spec.loader.exec_module(models_migration)

create_models_table = models_migration.create_models_table
from app.routes.main_routes import main_bp
from app.routes.api.models import models_bp
from app.routes.api.health import health_bp

# Flask uygulaması oluştur
app = Flask(__name__)

# Config'i .env'den çek
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Blueprint'leri kaydet
app.register_blueprint(main_bp)
app.register_blueprint(models_bp)
app.register_blueprint(health_bp)

if __name__ == '__main__':
    # Veritabanı tablolarını oluştur
    create_models_table()
    
    # Programı çalıştır
    app.run(debug=True)
