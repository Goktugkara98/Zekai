# =============================================================================
# 0004 MESSAGES MIGRATION
# =============================================================================
# Bu dosya, messages tablosunun oluşturulması için migration işlemlerini tanımlar.
# =============================================================================

from app.database.db_connection import execute_query


def create_messages_table():
    """
    Messages tablosunu oluşturur.

    Returns:
        bool: Başarılı ise True
    """
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS messages (
                message_id INT AUTO_INCREMENT PRIMARY KEY,
                chat_id VARCHAR(255) NOT NULL,
                model_id INT,
                content TEXT NOT NULL,
                is_user BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                -- Foreign key constraints
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE SET NULL,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE,

                -- Indexler
                INDEX idx_chat_id (chat_id),
                INDEX idx_model_id (model_id),
                INDEX idx_is_user (is_user),
                INDEX idx_timestamp (timestamp),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        execute_query(create_sql, fetch=False)
        return True

    except Exception as e:
        return False


def drop_messages_table():
    """
    Messages tablosunu siler.

    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS messages", fetch=False)
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
        if not create_messages_table():
            return False
        return True

    except Exception as e:
        return False
