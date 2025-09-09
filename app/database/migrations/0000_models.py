# =============================================================================
# 0000 MODELS MIGRATION
# =============================================================================
# Bu dosya, models tablosunun oluşturulması için migration işlemlerini tanımlar.
# =============================================================================

import logging
from app.database.db_connection import execute_query

logger = logging.getLogger(__name__)

def create_models_table():
    """
    Models tablosunu oluşturur.
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS models (
                model_id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(255) NOT NULL,
                model_type VARCHAR(100),
                provider_name VARCHAR(100),
                api_key VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                -- Indexler
                INDEX idx_model_name (model_name),
                INDEX idx_provider_name (provider_name),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        execute_query(create_sql, fetch=False)
        logger.info("Models tablosu oluşturuldu")
        return True
        
    except Exception as e:
        logger.error(f"Models tablosu oluşturma hatası: {str(e)}")
        return False

def drop_models_table():
    """
    Models tablosunu siler.
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS models", fetch=False)
        logger.info("Models tablosu silindi")
        return True
        
    except Exception as e:
        logger.error(f"Models tablosu silme hatası: {str(e)}")
        return False
