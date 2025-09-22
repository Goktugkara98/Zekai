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

def initialize_database():
    """Runs database migrations and seeders."""
    app.logger.debug("Starting database migrations...")
    run_all_migrations()
    app.logger.debug("Database migrations completed.")

    app.logger.debug("Running database seeders...")
    run_all_seeders()
    app.logger.debug("Database seeders completed.")

if __name__ != "__main__":
    # Production environment (Gunicorn)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.DEBUG) # Set to DEBUG as requested
    app.logger.info('Starting Zekai application under Gunicorn...')

@app.cli.command('init-db')
def init_db_command():
    """Command to initialize the database."""
    initialize_database()
    print("Database has been initialized.")

if __name__ == '__main__':
    # Development environment
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    initialize_database()
    app.logger.info("Starting Flask application in debug mode...")
    app.run(debug=True, use_reloader=False) # use_reloader=False to prevent running init twice

