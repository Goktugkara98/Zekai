import sys
import os

# Projenin kök dizinini (app klasörünün ebeveyni olan Zekai klasörü) sys.path'e ekle.
# Bu, app/main.py'den bir üst dizin.
# Böylece 'from app.models import ...' gibi importlar çalışır.
PACKAGE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_PARENT not in sys.path:
    sys.path.insert(0, PACKAGE_PARENT)

from flask import Flask
from app.models.database import initialize_database # app. öneki eklendi
from app.routes.main_routes import main_bp # app. öneki eklendi

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_bp)

if __name__ == '__main__':
    initialize_database() # Call the initializer
    app.run(debug=True)
