import os
import logging
from flask import Flask
from dotenv import load_dotenv
from app.database.run_migrations import run_all_migrations
from app.database.run_seeders import run_all_seeders
from app.routes import register_blueprints

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Blueprint'leri kaydet
    register_blueprints(app)

    # Gunicorn logger ile entegre
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    # Migration & seeders
    app.logger.info("Starting database migrations...")
    run_all_migrations()
    app.logger.info("Database migrations completed.")

    app.logger.info("Running database seeders...")
    run_all_seeders()
    app.logger.info("Database seeders completed.")

    return app
