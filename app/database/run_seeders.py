# =============================================================================
# SEEDERS RUNNER
# =============================================================================
# Bu dosya, veritabanı seed (başlangıç verileri) işlemlerini çalıştırır.
# =============================================================================

import logging
from app.database.seeders import seed_categories, seed_admin_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_all_seeders() -> bool:
    try:
        logger.info("Seed işlemleri başlatılıyor...")

        logger.info("Categories seed çalıştırılıyor...")
        if seed_categories():
            logger.info("✅ Categories seed tamamlandı")
        else:
            logger.error("❌ Categories seed başarısız")
            return False

        logger.info("Admin user seed çalıştırılıyor...")
        if seed_admin_user():
            logger.info("✅ Admin user seed tamamlandı")
        else:
            logger.error("❌ Admin user seed başarısız")
            return False

        logger.info("🎉 Tüm seed işlemleri tamamlandı!")
        return True
    except Exception as e:
        logger.error(f"Seed hatası: {str(e)}")
        return False


if __name__ == "__main__":
    ok = run_all_seeders()
    if ok:
        print("\n✅ Seed işlemi başarılı!")
    else:
        print("\n❌ Seed işlemi başarısız!")
        exit(1)
