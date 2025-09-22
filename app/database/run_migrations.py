# =============================================================================
# MIGRATION RUNNER
# =============================================================================
# Bu dosya, veritabanı migration'larını çalıştırır.
# =============================================================================

import logging
from app.database.migrations import (
    migration_0000_models,
    migration_0001_users,
    migration_0002_categories,
    migration_0003_chats,
    migration_0004_messages,
)

def run_all_migrations():
    """
    Tüm migration'ları çalıştır
    """
    try:
        logging.info("Running migration 0000 (models)...")
        if not migration_0000_models.create_models_table():
            logging.error("Migration 0000 (models) failed.")
            return False
        logging.info("Migration 0000 (models) completed.")

        logging.info("Running migration 0001 (users)...")
        if not migration_0001_users.run_migration():
            logging.error("Migration 0001 (users) failed.")
            return False
        logging.info("Migration 0001 (users) completed.")

        logging.info("Running migration 0002 (categories)...")
        if not migration_0002_categories.run_migration():
            logging.error("Migration 0002 (categories) failed.")
            return False
        logging.info("Migration 0002 (categories) completed.")

        logging.info("Running migration 0003 (chats)...")
        if not migration_0003_chats.run_migration():
            logging.error("Migration 0003 (chats) failed.")
            return False
        logging.info("Migration 0003 (chats) completed.")

        logging.info("Running migration 0004 (messages)...")
        if not migration_0004_messages.run_migration():
            logging.error("Migration 0004 (messages) failed.")
            return False
        logging.info("Migration 0004 (messages) completed.")

        return True
    except Exception as e:
        logging.error(f"An unexpected error occurred during migrations: {e}")
        return False

if __name__ == "__main__":
    # No console output
    _ = run_all_migrations()
