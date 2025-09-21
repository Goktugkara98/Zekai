# =============================================================================
# 0003 CHATS MIGRATION
# =============================================================================
# Bu dosya, chats tablosunun oluşturulması için migration işlemlerini tanımlar.
# =============================================================================

from app.database.db_connection import execute_query


def create_chats_table():
    """
    Chats tablosunu oluşturur.

    Returns:
        bool: Başarılı ise True
    """
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id VARCHAR(255) PRIMARY KEY,
                user_id INT NULL,
                model_id INT,
                title VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP NULL,

                -- Foreign key constraints
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,

                -- Indexler
                INDEX idx_user_id (user_id),
                INDEX idx_model_id (model_id),
                INDEX idx_is_active (is_active),
                INDEX idx_created_at (created_at),
                INDEX idx_last_message_at (last_message_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        execute_query(create_sql, fetch=False)
        return True

    except Exception as e:
        return False


def drop_chats_table():
    """
    Chats tablosunu siler.

    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS chats", fetch=False)
        return True

    except Exception as e:
        return False


def run_migration():
    """
    Migration'ı çalıştırır.

    Returns:
        bool: Başarılı ise True
    """
    try:
        if not create_chats_table():
            return False
        return True
    except Exception as e:
        return False
