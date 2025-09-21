# =============================================================================
# MESSAGE REPOSITORY
# =============================================================================
# Messages tablosu için CRUD işlemlerini yönetir.
# =============================================================================

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.db_connection import get_connection, get_cursor, execute_query


class MessageRepository:
    """Messages tablosu için veri erişim katmanı."""

    # --------------------------- CREATE --------------------------- #
    @staticmethod
    def create_message(chat_id: str, content: str, is_user: bool, model_id: Optional[int] = None, when: Optional[datetime] = None) -> Optional[int]:
        sql = (
            "INSERT INTO messages (chat_id, model_id, content, is_user, timestamp, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        when = when or datetime.now()
        params = (chat_id, model_id, content, is_user, when, when)
        conn = None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute(sql, params)
            conn.commit()
            msg_id = cur.lastrowid
            cur.close(); conn.close()
            return int(msg_id) if msg_id else None
        except Exception as e:
            try:
                if conn and conn.is_connected():
                    conn.rollback(); conn.close()
            except Exception:
                pass
            return None

    # --------------------------- READ --------------------------- #
    @staticmethod
    def list_by_chat(chat_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        sql = (
            "SELECT message_id, chat_id, model_id, content, is_user, timestamp, created_at "
            "FROM messages WHERE chat_id = %s ORDER BY created_at ASC LIMIT %s OFFSET %s"
        )
        try:
            rows = execute_query(sql, (chat_id, limit, offset), fetch=True)
            return rows or []
        except Exception as e:
            return []

    @staticmethod
    def get_by_id(message_id: int) -> Optional[Dict[str, Any]]:
        try:
            rows = execute_query(
                "SELECT * FROM messages WHERE message_id = %s",
                (message_id,),
                fetch=True,
            )
            return rows[0] if rows else None
        except Exception as e:
            return None

    # --------------------------- UPDATE --------------------------- #
    @staticmethod
    def update_message(message_id: int, content: Optional[str] = None) -> bool:
        if content is None:
            return True
        try:
            execute_query(
                "UPDATE messages SET content = %s, updated_at = CURRENT_TIMESTAMP WHERE message_id = %s",
                (content, message_id),
                fetch=False,
            )
            return True
        except Exception as e:
            return False

    # --------------------------- DELETE --------------------------- #
    @staticmethod
    def delete_message(message_id: int) -> bool:
        try:
            execute_query("DELETE FROM messages WHERE message_id = %s", (message_id,), fetch=False)
            return True
        except Exception as e:
            return False

    @staticmethod
    def delete_by_chat(chat_id: str) -> bool:
        try:
            execute_query("DELETE FROM messages WHERE chat_id = %s", (chat_id,), fetch=False)
            return True
        except Exception as e:
            return False

    # --------------------------- HELPERS --------------------------- #
    @staticmethod
    def count_by_chat(chat_id: str) -> int:
        try:
            rows = execute_query("SELECT COUNT(*) AS cnt FROM messages WHERE chat_id = %s", (chat_id,), fetch=True)
            return int(rows[0]["cnt"]) if rows else 0
        except Exception as e:
            return 0
