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
        # 0000 - Models tablosu
        if migration_0000_models.create_models_table():
            pass
        else:
            return False
        
        # 0001 - Users tablosu (is_admin dahil)
        if migration_0001_users.run_migration():
            pass
        else:
            return False

        # 0002 - Categories ve model_categories tabloları ve ilişkiler
        if migration_0002_categories.run_migration():
            pass
        else:
            return False

        # 0003 - Chats tablosu
        if migration_0003_chats.run_migration():
            pass
        else:
            return False

        # 0004 - Messages tablosu (FK -> chats)
        if migration_0004_messages.run_migration():
            pass
        else:
            return False
        return True
        
    except Exception as e:
        return False

if __name__ == "__main__":
    # No console output
    _ = run_all_migrations()
