# =============================================================================
# USER REPOSITORY
# =============================================================================
# Users tablosu için CRUD işlemlerini yönetir.
# =============================================================================

import logging
from typing import List, Dict, Any, Optional
from app.database.db_connection import get_connection, get_cursor, execute_query

logger = logging.getLogger(__name__)


class UserRepository:
    @staticmethod
    def list_users() -> List[Dict[str, Any]]:
        try:
            rows = execute_query(
                """
                SELECT user_id, email, first_name, last_name, is_active, is_verified, is_admin, created_at, last_login
                FROM users
                ORDER BY created_at DESC
                """
            )
            return rows or []
        except Exception as e:
            logger.error(f"Kullanıcıları getirme hatası: {str(e)}")
            return []

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        try:
            rows = execute_query(
                """
                SELECT user_id, email, first_name, last_name, is_active, is_verified, is_admin, created_at, last_login
                FROM users WHERE user_id = %s
                """,
                (user_id,),
                fetch=True,
            )
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Kullanıcı getirme hatası (id={user_id}): {str(e)}")
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        try:
            rows = execute_query(
                """
                SELECT user_id, email, password_hash, first_name, last_name, is_active, is_verified, is_admin, created_at, last_login
                FROM users WHERE email = %s
                """,
                (email,),
                fetch=True,
            )
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Kullanıcı getirme hatası (email={email}): {str(e)}")
            return None

    @staticmethod
    def create_user(email: str, password_hash: str, first_name: Optional[str], last_name: Optional[str], is_admin: bool = False, is_active: bool = True, is_verified: bool = False) -> Optional[int]:
        query = (
            "INSERT INTO users (email, password_hash, first_name, last_name, is_active, is_verified, is_admin) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (email, password_hash, first_name, last_name, is_active, is_verified, is_admin)
        connection = None
        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, params)
            connection.commit()
            new_id = cursor.lastrowid
            cursor.close()
            connection.close()
            logger.info(f"Kullanıcı oluşturuldu: {email} (ID: {new_id})")
            return new_id
        except Exception as e:
            logger.error(f"Kullanıcı oluşturma hatası: {str(e)}")
            try:
                if connection and connection.is_connected():
                    connection.rollback()
                    connection.close()
            except Exception:
                pass
            return None

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> bool:
        allowed = ['email', 'first_name', 'last_name', 'is_active', 'is_verified', 'is_admin']
        set_parts = []
        params = []
        for k, v in data.items():
            if k in allowed:
                set_parts.append(f"{k} = %s")
                params.append(v)
        if not set_parts:
            return False
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(set_parts)} WHERE user_id = %s"
        connection = None
        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, tuple(params))
            connection.commit()
            affected = cursor.rowcount
            cursor.close()
            connection.close()
            return affected > 0
        except Exception as e:
            logger.error(f"Kullanıcı güncelleme hatası (id={user_id}): {str(e)}")
            try:
                if connection and connection.is_connected():
                    connection.rollback()
                    connection.close()
            except Exception:
                pass
            return False

    @staticmethod
    def update_password(user_id: int, password_hash: str) -> bool:
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        connection = None
        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, (password_hash, user_id))
            connection.commit()
            affected = cursor.rowcount
            cursor.close()
            connection.close()
            return affected > 0
        except Exception as e:
            logger.error(f"Şifre güncelleme hatası (id={user_id}): {str(e)}")
            try:
                if connection and connection.is_connected():
                    connection.rollback()
                    connection.close()
            except Exception:
                pass
            return False

    @staticmethod
    def delete_user(user_id: int) -> bool:
        query = "DELETE FROM users WHERE user_id = %s"
        connection = None
        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, (user_id,))
            connection.commit()
            affected = cursor.rowcount
            cursor.close()
            connection.close()
            return affected > 0
        except Exception as e:
            logger.error(f"Kullanıcı silme hatası (id={user_id}): {str(e)}")
            try:
                if connection and connection.is_connected():
                    connection.rollback()
                    connection.close()
            except Exception:
                pass
            return False
