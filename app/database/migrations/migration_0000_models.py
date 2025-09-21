# =============================================================================
# 0000 MODELS MIGRATION
# =============================================================================
# Bu dosya, models tablosunun oluşturulması için migration işlemlerini tanımlar.
# =============================================================================

from app.database.db_connection import execute_query

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
                request_model_name VARCHAR(255) NULL,
                model_type VARCHAR(100),
                provider_name VARCHAR(100) NOT NULL,
                provider_type ENUM('gemini', 'openrouter', 'openai', 'anthropic') NOT NULL,
                api_key VARCHAR(500),
                base_url VARCHAR(500),
                logo_path VARCHAR(500) NULL,
                description TEXT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                -- Indexler
                INDEX idx_model_name (model_name),
                INDEX idx_request_model_name (request_model_name),
                INDEX idx_provider_name (provider_name),
                INDEX idx_provider_type (provider_type),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        execute_query(create_sql, fetch=False)

        # Var olan veritabanları için güvenli ALTER: sütun yoksa ekle
        try:
            alter_sql = """
                ALTER TABLE models
                ADD COLUMN IF NOT EXISTS request_model_name VARCHAR(255) NULL AFTER model_name,
                ADD INDEX IF NOT EXISTS idx_request_model_name (request_model_name)
            """
            execute_query(alter_sql, fetch=False)
        except Exception:
            # Bazı MySQL sürümleri IF NOT EXISTS desteklemeyebilir; ayrı ayrı dene
            try:
                execute_query("ALTER TABLE models ADD COLUMN request_model_name VARCHAR(255) NULL AFTER model_name", fetch=False)
            except Exception:
                pass
            try:
                execute_query("ALTER TABLE models ADD INDEX idx_request_model_name (request_model_name)", fetch=False)
            except Exception:
                pass
        # Yeni kolonlar için ayrı fallback
        try:
            execute_query("ALTER TABLE models ADD COLUMN IF NOT EXISTS logo_path VARCHAR(500) NULL AFTER base_url", fetch=False)
        except Exception:
            try:
                execute_query("ALTER TABLE models ADD COLUMN logo_path VARCHAR(500) NULL AFTER base_url", fetch=False)
            except Exception:
                pass
        try:
            execute_query("ALTER TABLE models ADD COLUMN IF NOT EXISTS description TEXT NULL AFTER logo_path", fetch=False)
        except Exception:
            try:
                execute_query("ALTER TABLE models ADD COLUMN description TEXT NULL AFTER logo_path", fetch=False)
            except Exception:
                pass
        return True
        
    except Exception as e:
        return False

def drop_models_table():
    """
    Models tablosunu siler.
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        execute_query("DROP TABLE IF EXISTS models", fetch=False)
        return True
        
    except Exception as e:
        return False
