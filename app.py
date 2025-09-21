from app.main import app
from app.database.run_migrations import run_all_migrations
from app.database.run_seeders import run_all_seeders

if __name__ == '__main__':
    # Ensure DB schema is up-to-date and seed initial data
    try:
        run_all_migrations()
    except Exception as _e:
        # Allow app to still start; detailed logs are inside run_all_migrations
        pass

    try:
        run_all_seeders()
    except Exception as _e:
        # Allow app to still start; detailed logs are inside run_all_seeders
        pass

    app.run(debug=True, host='0.0.0.0', port=5000)
