# =============================================================================
# 0002 CATEGORIES & MODEL-CATEGORIES MIGRATION
# =============================================================================
# Bu dosya, categories tablosunun ve models ile categories arasında
# çoktan-çoka (many-to-many) ilişki kuran model_categories eşleme
# tablosunun oluşturulmasını ve models tablosunun revizyonunu içerir.
# Not: Migration dosyaları yalnızca tablo/şema oluşturma ve değiştirme
# (DDL) içerir; veri ekleme/seed işlemleri bu dosyadan kaldırılmıştır.
# =============================================================================

from app.database.db_connection import execute_query, get_db_config


def create_categories_table():
    """
    Categories tablosunu oluşturur.

    Returns:
        bool: Başarılı ise True
    """
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS categories (
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                slug VARCHAR(255) UNIQUE,
                description VARCHAR(500) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                INDEX idx_category_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        execute_query(create_sql, fetch=False)
        return True
    except Exception as e:
        return False


def _check_if_exists(table_name, column_name=None, index_name=None, constraint_name=None):
    """
    INFORMATION_SCHEMA'yı sorgulayarak sütun, index veya constraint varlığını kontrol eder.
    """
    db_name = get_db_config()['database']
    if column_name:
        sql = """
            SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """
        params = (db_name, table_name, column_name)
    elif index_name:
        sql = """
            SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s
        """
        params = (db_name, table_name, index_name)
    elif constraint_name:
        sql = """
            SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = %s AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s
        """
        params = (db_name, table_name, constraint_name)
    else:
        return False

    result = execute_query(sql, params, fetch=True)
    return result[0]['count'] > 0 if result else False

def alter_models_table_add_columns():
    """
    Models tablosuna logo_path ve primary_category_id sütunlarını ekler.
    primary_category_id, categories(category_id)'e FK olarak tanımlanır.

    Returns:
        bool: Başarılı ise True
    """
    try:
        # logo_path sütununu kontrol et ve ekle
        if not _check_if_exists('models', column_name='logo_path'):
            execute_query("ALTER TABLE models ADD COLUMN logo_path VARCHAR(500) NULL AFTER base_url", fetch=False)

        # primary_category_id sütununu kontrol et ve ekle
        if not _check_if_exists('models', column_name='primary_category_id'):
            execute_query("ALTER TABLE models ADD COLUMN primary_category_id INT NULL AFTER is_active", fetch=False)

        # Index'i kontrol et ve ekle
        if not _check_if_exists('models', index_name='idx_primary_category_id'):
            execute_query("ALTER TABLE models ADD INDEX idx_primary_category_id (primary_category_id)", fetch=False)

        # Foreign key'i kontrol et ve ekle
        if not _check_if_exists('models', constraint_name='fk_models_primary_category'):
            execute_query(
                "ALTER TABLE models ADD CONSTRAINT fk_models_primary_category FOREIGN KEY (primary_category_id) REFERENCES categories(category_id) ON DELETE SET NULL",
                fetch=False
            )

        return True
    except Exception as e:
        return False


def create_model_categories_table():
    """
    model_categories eşleme tablosunu oluşturur (many-to-many).

    Returns:
        bool: Başarılı ise True
    """
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS model_categories (
                model_id INT NOT NULL,
                category_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (model_id, category_id),
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,

                INDEX idx_model_id (model_id),
                INDEX idx_category_id (category_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        execute_query(create_sql, fetch=False)
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
        if not create_categories_table():
            return False
        if not alter_models_table_add_columns():
            return False
        if not create_model_categories_table():
            return False
        return True
    except Exception as e:
        return False
