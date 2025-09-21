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

# Logger ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_all_migrations():
    """
    Tüm migration'ları çalıştır
    """
    try:
        logger.info("Migration'lar başlatılıyor...")
        
        # 0000 - Models tablosu
        logger.info("0000 - Models tablosu oluşturuluyor...")
        if migration_0000_models.create_models_table():
            logger.info("✅ Models tablosu oluşturuldu")
        else:
            logger.error("❌ Models tablosu oluşturulamadı")
            return False
        
        # 0001 - Users tablosu (is_admin dahil)
        logger.info("0001 - Users tablosu oluşturuluyor...")
        if migration_0001_users.run_migration():
            logger.info("✅ Users tablosu oluşturuldu")
        else:
            logger.error("❌ Users tablosu oluşturulamadı")
            return False

        # 0002 - Categories ve model_categories tabloları ve ilişkiler
        logger.info("0002 - Categories ve model_categories tabloları oluşturuluyor...")
        if migration_0002_categories.run_migration():
            logger.info("✅ Categories migration tamamlandı")
        else:
            logger.error("❌ Categories migration başarısız")
            return False

        # 0003 - Chats tablosu
        logger.info("0003 - Chats tablosu oluşturuluyor...")
        if migration_0003_chats.run_migration():
            logger.info("✅ Chats tablosu oluşturuldu")
        else:
            logger.error("❌ Chats tablosu oluşturulamadı")
            return False

        # 0004 - Messages tablosu (FK -> chats)
        logger.info("0004 - Messages tablosu oluşturuluyor...")
        if migration_0004_messages.run_migration():
            logger.info("✅ Messages tablosu oluşturuldu")
        else:
            logger.error("❌ Messages tablosu oluşturulamadı")
            return False
        
        logger.info("🎉 Tüm migration'lar başarıyla tamamlandı!")
        return True
        
    except Exception as e:
        logger.error(f"Migration hatası: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_all_migrations()
    if success:
        print("\n✅ Migration işlemi başarılı!")
    else:
        print("\n❌ Migration işlemi başarısız!")
        exit(1)
