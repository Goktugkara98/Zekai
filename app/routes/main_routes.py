from flask import Blueprint, render_template
from models.database import fetch_ai_categories_from_db

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    ai_categories = fetch_ai_categories_from_db()
    if not ai_categories:
        # Fallback or error message if data couldn't be fetched
        print("Warning: Could not fetch AI categories from the database. Using sample data.")
        # You could provide some default static data here if needed, or an error message
        # For now, let's use the previous sample data as a fallback for demonstration
        ai_categories = [
            {"name": "Error Fetching Categories", "icon": "bi-exclamation-triangle", "models": []}
        ]
    return render_template('index.html', ai_categories=ai_categories)
