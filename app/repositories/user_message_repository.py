# =============================================================================
# User Message Repository
# =============================================================================
# Contents:
# 1. Imports
# 2. UserMessageRepository Class
#    2.1. __init__ (Implicit from BaseRepository)
#    2.2. insert_user_message
#    2.3. get_user_message_by_id
#    2.4. get_all_user_messages
#    2.5. get_user_messages_by_session
#    2.6. get_user_messages_by_user
#    2.7. get_message_count
#    2.8. get_message_stats
# =============================================================================

# 1. Imports
# =============================================================================
from app.models.base import BaseRepository, DatabaseConnection # Added DatabaseConnection for completeness
from app.models.entities import UserMessage
from typing import List, Optional, Tuple, Dict, Any # Tuple is not used but kept for consistency
from mysql.connector import Error

# 2. UserMessageRepository Class
# =============================================================================
class UserMessageRepository(BaseRepository):
    """Repository class for user message operations."""

    # 2.1. __init__ is implicitly inherited from BaseRepository.

    # 2.2. insert_user_message
    # -------------------------------------------------------------------------
    def insert_user_message(self, session_id: str, user_message: str, ai_response: str,
                           ai_model_name: str, user_id: str = None, prompt: str = None,
                           model_params: str = None, request_json: str = None,
                           response_json: str = None, tokens: int = None,
                           duration: float = None, error_message: str = None,
                           status: str = None) -> Optional[int]:
        """Inserts a new user message into the database."""
        try:
            # Validate essential values
            session_id = session_id or "UNKNOWN"
            user_message = user_message or "" # Allow empty user message if AI initiates
            ai_response = ai_response or ""   # Allow empty AI response if error or user only message
            ai_model_name = ai_model_name or "UNKNOWN"

            # Prepare query fields and values
            fields = ["session_id", "user_message", "ai_response", "ai_model_name"]
            values = [session_id, user_message, ai_response, ai_model_name]

            # Add optional fields
            optional_fields = {
                "user_id": user_id,
                "prompt": prompt,
                "model_params": model_params,
                "request_json": request_json,
                "response_json": response_json,
                "tokens": tokens,
                "duration": duration,
                "error_message": error_message,
                "status": status
            }

            for field, value in optional_fields.items():
                if value is not None:
                    fields.append(field)
                    values.append(value)

            # Construct SQL query
            placeholders = ", ".join(["%s"] * len(fields))
            field_names = ", ".join(fields)

            query = f"INSERT INTO user_messages ({field_names}) VALUES ({placeholders})"

            # Execute query
            return self.insert(query, tuple(values))

        except Error as e:
            # In a real application, log this error: print(f"Database error on insert_user_message: {e}")
            return None

    # 2.3. get_user_message_by_id
    # -------------------------------------------------------------------------
    def get_user_message_by_id(self, message_id: int) -> Optional[UserMessage]:
        """Retrieves a user message by its ID."""
        if not message_id or not isinstance(message_id, int):
            # print("Invalid message_id provided to get_user_message_by_id")
            return None
        query = "SELECT * FROM user_messages WHERE id = %s"
        result = self.fetch_one(query, (message_id,))
        return UserMessage.from_dict(result) if result else None

    # 2.4. get_all_user_messages
    # -------------------------------------------------------------------------
    def get_all_user_messages(self, limit: int = 100, offset: int = 0) -> List[UserMessage]:
        """Retrieves all user messages with pagination."""
        # Validate limit and offset
        try:
            limit = max(1, int(limit))
            offset = max(0, int(offset))
        except ValueError:
            # print("Invalid limit or offset provided to get_all_user_messages")
            return []

        query = """
            SELECT * FROM user_messages
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """
        results = self.fetch_all(query, (limit, offset))
        return [UserMessage.from_dict(row) for row in results]

    # 2.5. get_user_messages_by_session
    # -------------------------------------------------------------------------
    def get_user_messages_by_session(self, session_id: str, limit: int = 100) -> List[UserMessage]:
        """Retrieves user messages for a specific session ID, with a limit."""
        if not session_id:
            # print("Invalid session_id provided to get_user_messages_by_session")
            return []
        try:
            limit = max(1, int(limit))
        except ValueError:
            # print("Invalid limit provided to get_user_messages_by_session")
            return []

        query = """
            SELECT * FROM user_messages
            WHERE session_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        results = self.fetch_all(query, (session_id, limit))
        return [UserMessage.from_dict(row) for row in results]

    # 2.6. get_user_messages_by_user
    # -------------------------------------------------------------------------
    def get_user_messages_by_user(self, user_id: str, limit: int = 100) -> List[UserMessage]:
        """Retrieves user messages for a specific user ID, with a limit."""
        if not user_id:
            # print("Invalid user_id provided to get_user_messages_by_user")
            return []
        try:
            limit = max(1, int(limit))
        except ValueError:
            # print("Invalid limit provided to get_user_messages_by_user")
            return []

        query = """
            SELECT * FROM user_messages
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        results = self.fetch_all(query, (user_id, limit))
        return [UserMessage.from_dict(row) for row in results]

    # 2.7. get_message_count
    # -------------------------------------------------------------------------
    def get_message_count(self) -> int:
        """Retrieves the total number of user messages."""
        query = "SELECT COUNT(*) as count FROM user_messages"
        result = self.fetch_one(query)
        return result['count'] if result and 'count' in result else 0

    # 2.8. get_message_stats
    # -------------------------------------------------------------------------
    def get_message_stats(self) -> Dict[str, Any]:
        """Retrieves statistics about user messages."""
        stats = {
            'total_count': 0,
            'model_counts': {},
            'session_count': 0,
            'user_count': 0
        }

        try:
            # Total message count
            query_total = "SELECT COUNT(*) as count FROM user_messages"
            result_total = self.fetch_one(query_total)
            stats['total_count'] = result_total['count'] if result_total and 'count' in result_total else 0

            # Message counts per AI model
            query_model = """
                SELECT ai_model_name, COUNT(*) as count
                FROM user_messages
                WHERE ai_model_name IS NOT NULL AND ai_model_name != ''
                GROUP BY ai_model_name
            """
            results_model = self.fetch_all(query_model)
            for row in results_model:
                if row and 'ai_model_name' in row and 'count' in row:
                    stats['model_counts'][row['ai_model_name']] = row['count']

            # Unique session count
            query_session = "SELECT COUNT(DISTINCT session_id) as count FROM user_messages"
            result_session = self.fetch_one(query_session)
            stats['session_count'] = result_session['count'] if result_session and 'count' in result_session else 0

            # Unique user count (where user_id is not NULL)
            query_user = "SELECT COUNT(DISTINCT user_id) as count FROM user_messages WHERE user_id IS NOT NULL"
            result_user = self.fetch_one(query_user)
            stats['user_count'] = result_user['count'] if result_user and 'count' in result_user else 0

        except Error as e:
            # In a real application, log this error: print(f"Database error on get_message_stats: {e}")
            # Return current (possibly partial) stats or re-raise, depending on desired behavior
            pass

        return stats
