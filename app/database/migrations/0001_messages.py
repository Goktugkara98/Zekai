# =============================================================================
# 0001 MESSAGES MIGRATION
# =============================================================================
# Bu dosya, messages tablosunun oluşturulması için migration işlemlerini tanımlar.
# =============================================================================

import logging
from app.database.db_connection import execute_query

logger = logging.getLogger(__name__)

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
                
                -- Foreign key constraint
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE SET NULL,
                
                -- Indexler
                INDEX idx_chat_id (chat_id),
                INDEX idx_model_id (model_id),
                INDEX idx_is_user (is_user),
                INDEX idx_timestamp (timestamp),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        execute_query(create_sql, fetch=False)
        logger.info("Messages tablosu oluşturuldu")
        return True
        
    except Exception as e:
        logger.error(f"Messages tablosu oluşturma hatası: {str(e)}")
        return False

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
                model_id INT,
                title VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP NULL,
                
                -- Foreign key constraint
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE SET NULL,
                
                -- Indexler
                INDEX idx_model_id (model_id),
                INDEX idx_is_active (is_active),
                INDEX idx_created_at (created_at),
                INDEX idx_last_message_at (last_message_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        execute_query(create_sql, fetch=False)
        logger.info("Chats tablosu oluşturuldu")
        return True
        
    except Exception as e:
        logger.error(f"Chats tablosu oluşturma hatası: {str(e)}")
        return False

def drop_messages_table():
    """
    Messages tablosunu siler.
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS messages", fetch=False)
        logger.info("Messages tablosu silindi")
        return True
        
    except Exception as e:
        logger.error(f"Messages tablosu silme hatası: {str(e)}")
        return False

def drop_chats_table():
    """
    Chats tablosunu siler.
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS chats", fetch=False)
        logger.info("Chats tablosu silindi")
        return True
        
    except Exception as e:
        logger.error(f"Chats tablosu silme hatası: {str(e)}")
        return False

def run_migration():
    """
    Migration'ı çalıştırır.
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        # Önce chats tablosunu oluştur (foreign key için)
        if not create_chats_table():
            return False
            
        # Sonra messages tablosunu oluştur
        if not create_messages_table():
            return False
            
        logger.info("Messages migration başarıyla tamamlandı")
        return True
        
    except Exception as e:
        logger.error(f"Messages migration hatası: {str(e)}")
        return False
