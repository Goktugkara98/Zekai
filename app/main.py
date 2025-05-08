from flask import Flask
from models.database import initialize_database
from routes.main_routes import main_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_bp)

if __name__ == '__main__':
    initialize_database() # Call the initializer
    app.run(debug=True)
