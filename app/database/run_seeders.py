# =============================================================================
# SEEDERS RUNNER
# =============================================================================
# Bu dosya, veritabanı seed (başlangıç verileri) işlemlerini çalıştırır.
# =============================================================================

import logging
from app.database.seeders import seed_categories, seed_admin_user


def run_all_seeders() -> bool:
    try:
        logging.debug("Running seeder (categories)...")
        if not seed_categories():
            logging.error("Seeder (categories) failed.")
            return False
        logging.debug("Seeder (categories) completed.")

        logging.debug("Running seeder (admin_user)...")
        if not seed_admin_user():
            logging.error("Seeder (admin_user) failed.")
            return False
        logging.debug("Seeder (admin_user) completed.")

        return True
    except Exception as e:
        logging.error(f"An unexpected error occurred during seeding: {e}")
        return False


if __name__ == "__main__":
    # No console output
    _ = run_all_seeders()