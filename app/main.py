import sys
import os
import secrets

# Projenin kök dizinini (app klasörünün ebeveyni olan Zekai klasörü) sys.path'e ekle.
# Bu, app/main.py'den bir üst dizin.
# Böylece 'from app.models import ...' gibi importlar çalışır.
PACKAGE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_PARENT not in sys.path:
    sys.path.insert(0, PACKAGE_PARENT)

from flask import Flask
from app.models.migrations import DatabaseMigrations # app. öneki eklendi
from app.routes.main_routes import main_bp # app. öneki eklendi
from app.routes.admin_routes import admin_bp # Admin blueprint'i import et

app = Flask(__name__)

# Configure application
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp) # Admin blueprint'i kaydet

if __name__ == '__main__':
    db_migrations = DatabaseMigrations() # Call the initializer
    db_migrations.create_all_tables()
    app.run(debug=True)
