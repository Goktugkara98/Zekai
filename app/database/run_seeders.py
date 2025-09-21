# =============================================================================
# SEEDERS RUNNER
# =============================================================================
# Bu dosya, veritabanı seed (başlangıç verileri) işlemlerini çalıştırır.
# =============================================================================

from app.database.seeders import seed_categories, seed_admin_user


def run_all_seeders() -> bool:
    try:
        if not seed_categories():
            return False
        if not seed_admin_user():
            return False
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # No console output
    _ = run_all_seeders()
