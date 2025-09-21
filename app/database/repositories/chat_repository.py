# =============================================================================
# CHAT REPOSITORY
# =============================================================================
# Chats tablosu için CRUD ve yardımcı işlemleri yönetir.
# =============================================================================

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.db_connection import get_connection, get_cursor, execute_query

logger = logging.getLogger(__name__)


class ChatRepository:
    """Chats tablosu için veri erişim katmanı."""

    # --------------------------- CREATE --------------------------- #
    @staticmethod
    def create_chat(model_id: int, title: Optional[str] = None, user_id: Optional[int] = None, chat_id: Optional[str] = None) -> Optional[str]:
        """
        Yeni bir chat oluşturur ve chat_id'yi döndürür.
        """
        chat_id = chat_id or str(uuid.uuid4())
        now = datetime.now()
        sql = (
            "INSERT INTO chats (chat_id, user_id, model_id, title, is_active, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (chat_id, user_id, model_id, title, True, now, now)
        conn = None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute(sql, params)
            conn.commit()
            cur.close()
            conn.close()
            return chat_id
        except Exception as e:
            logger.error(f"Chat oluşturulamadı: {e}")
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return None

    # --------------------------- READ --------------------------- #
    @staticmethod
    def get_chat(chat_id: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        sql = (
            "SELECT c.*, m.model_name, m.provider_name, m.provider_type "
            "FROM chats c LEFT JOIN models m ON c.model_id = m.model_id "
            "WHERE c.chat_id = %s"
        )
        params = [chat_id]
        if user_id is not None:
            sql += " AND c.user_id = %s"
            params.append(user_id)
        try:
            rows = execute_query(sql, tuple(params), fetch=True)
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Chat getirilemedi (chat_id={chat_id}): {e}")
            return None

    @staticmethod
    def list_user_chats(user_id: int, active: Optional[bool] = True, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        base_sql = (
            "SELECT c.*, m.model_name, m.provider_name, "
            "(SELECT COUNT(*) FROM messages WHERE chat_id = c.chat_id) AS message_count "
            "FROM chats c LEFT JOIN models m ON c.model_id = m.model_id "
            "WHERE c.user_id = %s"
        )
        params = [user_id]
        if active is True:
            base_sql += " AND c.is_active = TRUE"
        elif active is False:
            base_sql += " AND c.is_active = FALSE"
        base_sql += " ORDER BY c.last_message_at DESC, c.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        try:
            rows = execute_query(base_sql, tuple(params), fetch=True)
            return rows or []
        except Exception as e:
            logger.error(f"Kullanıcı chat'leri alınamadı (user_id={user_id}): {e}")
            return []

    # --------------------------- UPDATE --------------------------- #
    @staticmethod
    def update_last_message_time(chat_id: str, when: Optional[datetime] = None) -> bool:
        when = when or datetime.now()
        sql = "UPDATE chats SET last_message_at = %s, updated_at = %s WHERE chat_id = %s"
        try:
            execute_query(sql, (when, when, chat_id), fetch=False)
            return True
        except Exception as e:
            logger.error(f"last_message_at güncellenemedi (chat_id={chat_id}): {e}")
            return False

    @staticmethod
    def update_title(chat_id: str, title: str) -> bool:
        try:
            execute_query("UPDATE chats SET title = %s, updated_at = %s WHERE chat_id = %s", (title, datetime.now(), chat_id), fetch=False)
            return True
        except Exception as e:
            logger.error(f"Chat başlığı güncellenemedi (chat_id={chat_id}): {e}")
            return False

    @staticmethod
    def set_active(chat_id: str, active: bool) -> bool:
        try:
            execute_query("UPDATE chats SET is_active = %s, updated_at = %s WHERE chat_id = %s", (active, datetime.now(), chat_id), fetch=False)
            return True
        except Exception as e:
            logger.error(f"Chat aktiflik durumu güncellenemedi (chat_id={chat_id}): {e}")
            return False

    # --------------------------- DELETE --------------------------- #
    @staticmethod
    def hard_delete(chat_id: str, user_id: Optional[int] = None) -> bool:
        try:
            if user_id is not None:
                execute_query("DELETE FROM chats WHERE chat_id = %s AND user_id = %s", (chat_id, user_id), fetch=False)
            else:
                execute_query("DELETE FROM chats WHERE chat_id = %s", (chat_id,), fetch=False)
            return True
        except Exception as e:
            logger.error(f"Chat silinemedi (chat_id={chat_id}): {e}")
            return False

    @staticmethod
    def soft_delete(chat_id: str) -> bool:
        try:
            execute_query("UPDATE chats SET is_active = FALSE, updated_at = %s WHERE chat_id = %s", (datetime.now(), chat_id), fetch=False)
            return True
        except Exception as e:
            logger.error(f"Chat soft delete başarısız (chat_id={chat_id}): {e}")
            return False

    # --------------------------- HELPERS --------------------------- #
    @staticmethod
    def count_messages(chat_id: str) -> int:
        try:
            rows = execute_query("SELECT COUNT(*) AS cnt FROM messages WHERE chat_id = %s", (chat_id,), fetch=True)
            return int(rows[0]["cnt"]) if rows else 0
        except Exception as e:
            logger.error(f"Mesaj sayısı alınamadı (chat_id={chat_id}): {e}")
            return 0
