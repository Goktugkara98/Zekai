# =============================================================================
# CATEGORY REPOSITORY
# =============================================================================
# Categories ve ilişkili modeller için DB erişim katmanı
# =============================================================================

import logging
from app.database.db_connection import execute_query, get_connection, get_cursor

logger = logging.getLogger(__name__)


class CategoryRepository:
    @staticmethod
    def get_all_categories():
        """Tüm kategorileri getirir."""
        try:
            rows = execute_query(
                "SELECT category_id, name, slug, description, created_at, updated_at FROM categories ORDER BY name ASC"
            )
            return rows or []
        except Exception as e:
            logger.error(f"Kategorileri getirme hatası: {str(e)}")
            return []

    @staticmethod
    def get_models_by_category(category_id: int):
        """Belirli bir kategoriye bağlı modelleri getirir."""
        try:
            rows = execute_query(
                """
                SELECT m.* FROM models m
                INNER JOIN model_categories mc ON mc.model_id = m.model_id
                WHERE mc.category_id = %s
                ORDER BY m.model_name ASC
                """,
                (category_id,),
            )
            return rows or []
        except Exception as e:
            logger.error(f"Kategori modellerini getirme hatası (id={category_id}): {str(e)}")
            return []

    @staticmethod
    def get_category_by_id(category_id: int):
        """Belirli bir kategoriyi ID'ye göre getirir."""
        try:
            rows = execute_query(
                "SELECT category_id, name, slug, description, created_at, updated_at FROM categories WHERE category_id = %s",
                (category_id,)
            )
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Kategori getirme hatası (id={category_id}): {str(e)}")
            return None

    @staticmethod
    def create_category(name: str, slug: str, description: str = ""):
        """Yeni kategori oluşturur."""
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute(
                "INSERT INTO categories (name, slug, description) VALUES (%s, %s, %s)",
                (name, slug, description),
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.close(); conn.close()
            return int(new_id) if new_id else None
        except Exception as e:
            logger.error(f"Kategori oluşturma hatası: {str(e)}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return None

    @staticmethod
    def update_category(category_id: int, name: str, slug: str, description: str = ""):
        """Kategoriyi günceller."""
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute(
                "UPDATE categories SET name = %s, slug = %s, description = %s, updated_at = CURRENT_TIMESTAMP WHERE category_id = %s",
                (name, slug, description, category_id),
            )
            conn.commit()
            affected = cur.rowcount
            cur.close(); conn.close()
            return affected > 0
        except Exception as e:
            logger.error(f"Kategori güncelleme hatası (id={category_id}): {str(e)}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return False

    @staticmethod
    def delete_category(category_id: int):
        """Kategoriyi siler."""
        conn = None
        cur = None
        try:
            conn = get_connection(); cur = get_cursor(conn)
            # Önce model-category ilişkilerini sil
            cur.execute("DELETE FROM model_categories WHERE category_id = %s", (category_id,))
            # Sonra kategoriyi sil
            cur.execute("DELETE FROM categories WHERE category_id = %s", (category_id,))
            conn.commit()
            affected = cur.rowcount
            cur.close(); conn.close()
            return affected > 0
        except Exception as e:
            logger.error(f"Kategori silme hatası (id={category_id}): {str(e)}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return False
