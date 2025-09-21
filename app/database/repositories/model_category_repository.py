# =============================================================================
# MODEL-CATEGORY REPOSITORY
# =============================================================================
# model_categories ilişki tablosu için CRUD ve toplu işlemler
# =============================================================================

import logging
from typing import List, Optional, Dict
from app.database.db_connection import get_connection, get_cursor, execute_query

logger = logging.getLogger(__name__)


class ModelCategoryRepository:
    @staticmethod
    def get_category_ids_by_model(model_id: int) -> List[int]:
        try:
            rows = execute_query(
                "SELECT category_id FROM model_categories WHERE model_id = %s ORDER BY category_id ASC",
                (model_id,),
                fetch=True
            )
            return [int(r['category_id']) for r in rows] if rows else []
        except Exception as e:
            logger.error(f"Kategori ID'leri alınamadı (model_id={model_id}): {e}")
            return []

    @staticmethod
    def replace_model_categories(model_id: int, category_ids: List[int], primary_category_id: Optional[int] = None) -> bool:
        """Verilen model için kategorileri tamamen değiştirir (transaction)."""
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            # Temizle
            cur.execute("DELETE FROM model_categories WHERE model_id = %s", (model_id,))
            # Ekle
            if category_ids:
                vals = [(model_id, int(cid)) for cid in category_ids]
                cur.executemany("INSERT INTO model_categories (model_id, category_id) VALUES (%s, %s)", vals)
            # Primary category güncelle
            if primary_category_id is not None:
                # Eğer primary listede yoksa ekle
                if primary_category_id not in (category_ids or []):
                    cur.execute("INSERT IGNORE INTO model_categories (model_id, category_id) VALUES (%s, %s)", (model_id, primary_category_id))
                cur.execute("UPDATE models SET primary_category_id=%s WHERE model_id=%s", (primary_category_id, model_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"replace_model_categories hata: {e}")
            try:
                if conn and conn.is_connected():
                    conn.rollback()
            except Exception:
                pass
            return False
        finally:
            try:
                if cur:
                    cur.close()
                if conn and conn.is_connected():
                    conn.close()
            except Exception:
                pass

    @staticmethod
    def add_model_categories(model_id: int, category_ids: List[int]) -> bool:
        if not category_ids:
            return True
        try:
            vals = [(model_id, int(cid)) for cid in category_ids]
            # IGNORE ile aynı ilişkiyi tekrar eklemeye çalışırken hata engellenir (MySQL varsayımı)
            conn = get_connection(); cur = get_cursor(conn)
            cur.executemany("INSERT IGNORE INTO model_categories (model_id, category_id) VALUES (%s, %s)", vals)
            conn.commit()
            cur.close();
            if conn and conn.is_connected():
                conn.close()
            return True
        except Exception as e:
            logger.error(f"add_model_categories hata: {e}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return False

    @staticmethod
    def remove_model_categories(model_id: int, category_ids: List[int]) -> bool:
        if not category_ids:
            return True
        try:
            conn = get_connection(); cur = get_cursor(conn)
            placeholders = ','.join(['%s'] * len(category_ids))
            sql = f"DELETE FROM model_categories WHERE model_id=%s AND category_id IN ({placeholders})"
            params = tuple([model_id] + [int(cid) for cid in category_ids])
            cur.execute(sql, params)
            conn.commit()
            cur.close();
            if conn and conn.is_connected():
                conn.close()
            return True
        except Exception as e:
            logger.error(f"remove_model_categories hata: {e}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return False

    @staticmethod
    def bulk_replace(models: List[int], category_ids: List[int], primary_category_id: Optional[int] = None) -> bool:
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            for mid in models:
                # temizle
                cur.execute("DELETE FROM model_categories WHERE model_id = %s", (mid,))
                # ekle
                if category_ids:
                    vals = [(mid, int(cid)) for cid in category_ids]
                    cur.executemany("INSERT IGNORE INTO model_categories (model_id, category_id) VALUES (%s, %s)", vals)
                # primary
                if primary_category_id is not None:
                    if primary_category_id not in (category_ids or []):
                        cur.execute("INSERT IGNORE INTO model_categories (model_id, category_id) VALUES (%s, %s)", (mid, primary_category_id))
                    cur.execute("UPDATE models SET primary_category_id=%s WHERE model_id=%s", (primary_category_id, mid))
            conn.commit()
            cur.close();
            if conn and conn.is_connected():
                conn.close()
            return True
        except Exception as e:
            logger.error(f"bulk_replace hata: {e}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return False
