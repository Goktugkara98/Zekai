# =============================================================================
# SEEDERS RUNNER
# =============================================================================
# Bu dosya, veritabanı seed (başlangıç verileri) işlemlerini çalıştırır.
# =============================================================================

from app.database.seeders import seed_categories, seed_admin_user


def run_all_seeders() -> bool:
    try:
        print("DEBUG: Seeder (categories) çalıştırılıyor...")
        if not seed_categories():
            print("HATA: Seeder (categories) başarısız.")
            return False
        print("DEBUG: Seeder (categories) tamamlandı.")

        print("DEBUG: Seeder (admin_user) çalıştırılıyor...")
        if not seed_admin_user():
            print("HATA: Seeder (admin_user) başarısız.")
            return False
        print("DEBUG: Seeder (admin_user) tamamlandı.")

        return True
    except Exception as e:
        print(f"HATA: Seeder'lar çalıştırılırken beklenmedik bir hata oluştu: {e}")
        return False


if __name__ == "__main__":
    # No console output
    _ = run_all_seeders()
