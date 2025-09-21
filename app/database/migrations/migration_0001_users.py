# =============================================================================
# 0001 USERS MIGRATION
# =============================================================================
# Bu dosya, users tablosunun oluşturulması için migration işlemlerini tanımlar.
# is_admin kolonu ana tablo oluşturma migration'ına dahildir.
# =============================================================================

import logging
from app.database.db_connection import execute_query

logger = logging.getLogger(__name__)


def create_users_table():
    """
    Users tablosunu oluşturur.

    Returns:
        bool: Başarılı ise True
    """
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                is_admin BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,

                -- Indexler
                INDEX idx_email (email),
                INDEX idx_is_active (is_active),
                INDEX idx_is_verified (is_verified),
                INDEX idx_is_admin (is_admin)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        execute_query(create_sql, fetch=False)
        logger.info("Users tablosu oluşturuldu")
        return True

    except Exception as e:
        logger.error(f"Users tablosu oluşturma hatası: {str(e)}")
        return False


def drop_users_table():
    """
    Users tablosunu siler.

    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS users", fetch=False)
        logger.info("Users tablosu silindi")
        return True

    except Exception as e:
        logger.error(f"Users tablosu silme hatası: {str(e)}")
        return False


def run_migration():
    """
    Migration'ı çalıştırır.

    Returns:
        bool: Başarılı ise True
    """
    try:
        logger.info("Users migration başlatılıyor...")
        success = create_users_table()
        if success:
            logger.info("✅ Users migration başarılı!")
        else:
            logger.error("❌ Users migration başarısız!")
        return success

    except Exception as e:
        logger.error(f"Users migration hatası: {str(e)}")
        return False
