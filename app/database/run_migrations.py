# =============================================================================
# MIGRATION RUNNER
# =============================================================================
# Bu dosya, veritabanı migration'larını çalıştırır.
# =============================================================================

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
        print("DEBUG: Migration 0000 (models) çalıştırılıyor...")
        if not migration_0000_models.create_models_table():
            print("HATA: Migration 0000 (models) başarısız.")
            return False
        print("DEBUG: Migration 0000 (models) tamamlandı.")

        print("DEBUG: Migration 0001 (users) çalıştırılıyor...")
        if not migration_0001_users.run_migration():
            print("HATA: Migration 0001 (users) başarısız.")
            return False
        print("DEBUG: Migration 0001 (users) tamamlandı.")

        print("DEBUG: Migration 0002 (categories) çalıştırılıyor...")
        if not migration_0002_categories.run_migration():
            print("HATA: Migration 0002 (categories) başarısız.")
            return False
        print("DEBUG: Migration 0002 (categories) tamamlandı.")

        print("DEBUG: Migration 0003 (chats) çalıştırılıyor...")
        if not migration_0003_chats.run_migration():
            print("HATA: Migration 0003 (chats) başarısız.")
            return False
        print("DEBUG: Migration 0003 (chats) tamamlandı.")

        print("DEBUG: Migration 0004 (messages) çalıştırılıyor...")
        if not migration_0004_messages.run_migration():
            print("HATA: Migration 0004 (messages) başarısız.")
            return False
        print("DEBUG: Migration 0004 (messages) tamamlandı.")

        return True
    except Exception as e:
        print(f"HATA: Migration'lar çalıştırılırken beklenmedik bir hata oluştu: {e}")
        return False

if __name__ == "__main__":
    # No console output
    _ = run_all_migrations()
