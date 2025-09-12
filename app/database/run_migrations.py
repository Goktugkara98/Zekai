# =============================================================================
# MIGRATION RUNNER
# =============================================================================
# Bu dosya, veritabanı migration'larını çalıştırır.
# =============================================================================

import logging
from app.database.migrations import 0000_models, 0001_messages

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
        if 0000_models.create_models_table():
            logger.info("✅ Models tablosu oluşturuldu")
        else:
            logger.error("❌ Models tablosu oluşturulamadı")
            return False
        
        # 0001 - Messages ve Chats tabloları
        logger.info("0001 - Messages ve Chats tabloları oluşturuluyor...")
        if 0001_messages.run_migration():
            logger.info("✅ Messages ve Chats tabloları oluşturuldu")
        else:
            logger.error("❌ Messages ve Chats tabloları oluşturulamadı")
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
