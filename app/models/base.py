# =============================================================================
# Database Base Module
# =============================================================================
# Contents:
# 1. Imports
# 2. DatabaseConnection Class
#    2.1. __init__
#    2.2. connect
#    2.3. close
#    2.4. _ensure_connection
#    2.5. __enter__ (Context Manager)
#    2.6. __exit__ (Context Manager)
# 3. BaseRepository Class
#    3.1. __init__
#    3.2. _ensure_connection
#    3.3. _close_if_owned
#    3.4. execute_query
#    3.5. fetch_one
#    3.6. fetch_all
#    3.7. insert
# =============================================================================

# 1. Imports
# =============================================================================
import mysql.connector
from mysql.connector import Error,pooling
from app.config import DB_CONFIG
from typing import Optional, Any, Dict, List, Type

# 2. DatabaseConnection Class
# =============================================================================
class DatabaseConnection:
    """
    Manages a single database connection.
    Not inherently thread-safe if the same instance is shared across threads
    without external locking. For multi-threaded applications, consider using
    a connection pool or creating a new instance per thread/task.
    """

    # 2.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self):
        """Initializes the DatabaseConnection."""
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursorDict] = None
        self.db_config: Dict[str, Any] = DB_CONFIG
        # Log: "DatabaseConnection instance created."

    # 2.2. connect
    # -------------------------------------------------------------------------
    def connect(self) -> None:
        """
        Establishes a connection to the database.
        Raises:
            mysql.connector.Error: If connection fails.
        """
        try:
            # Log: f"Attempting to connect to database: {self.db_config.get('database')}@{self.db_config.get('host')}"
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                # Log: "Database connection successful."
            else:
                # Log: "Database connection failed: Connection not established."
                # This case might be rare as connect() itself would raise Error
                raise Error("Failed to connect to the database.")
        except Error as e:
            # Log: f"Database connection error: {e}"
            self.connection = None # Ensure connection is None if connect fails
            self.cursor = None
            raise # Re-raise the exception to be handled by the caller

    # 2.3. close
    # -------------------------------------------------------------------------
    def close(self) -> None:
        """Closes the database cursor and connection if they are open."""
        if self.cursor:
            try:
                self.cursor.close()
                # Log: "Database cursor closed."
            except Error as e:
                # Log: f"Error closing cursor: {e}"
                pass # Ignore cursor close errors, but log them
            self.cursor = None
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
                # Log: "Database connection closed."
            except Error as e:
                # Log: f"Error closing connection: {e}"
                pass # Ignore connection close errors, but log them
            self.connection = None
        # Log: "DatabaseConnection resources released."


    # 2.4. _ensure_connection
    # -------------------------------------------------------------------------
    def _ensure_connection(self) -> None:
        """
        Ensures that an active database connection is available.
        If not connected, it attempts to establish a new connection.
        """
        if not self.connection or not self.connection.is_connected() or not self.cursor:
            # Log: "No active connection found or cursor missing. Attempting to reconnect..."
            self.connect()

    # 2.5. __enter__ (Context Manager)
    # -------------------------------------------------------------------------
    def __enter__(self) -> 'DatabaseConnection':
        """
        Context management protocol. Ensures connection on entering.
        Allows 'with DatabaseConnection() as db:' syntax.
        """
        self._ensure_connection()
        return self

    # 2.6. __exit__ (Context Manager)
    # -------------------------------------------------------------------------
    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[Any]) -> None:
        """
        Context management protocol. Closes connection on exiting.
        """
        self.close()
        # if exc_type:
        #     Log: f"Exception occurred within 'with' block: {exc_type}, {exc_val}"
        # Return None (or False) to propagate exceptions, True to suppress.


# 3. BaseRepository Class
# =============================================================================
class BaseRepository:
    """
    Base class for all repository classes, providing common database operations.
    Handles its own database connection lifecycle if one is not provided.
    """

    # 3.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        Initializes the BaseRepository.
        Args:
            db_connection: An optional existing DatabaseConnection instance.
                           If None, a new connection is created and managed by this repository.
        """
        if db_connection:
            self.db: DatabaseConnection = db_connection
            self.own_connection: bool = False # Connection is managed externally
            # Log: "BaseRepository initialized with an external DatabaseConnection."
        else:
            self.db: DatabaseConnection = DatabaseConnection()
            self.own_connection: bool = True # Connection is owned and managed by this instance
            # Log: "BaseRepository initialized with a new internal DatabaseConnection."

    # 3.2. _ensure_connection
    # -------------------------------------------------------------------------
    def _ensure_connection(self) -> None:
        """Ensures the database connection is active, especially if repository owns it."""
        if self.own_connection: # Only ensure if we own it; external connections manage themselves.
            self.db._ensure_connection()
        elif not self.db.connection or not self.db.connection.is_connected() or not self.db.cursor:
            # This case implies an external connection was passed but is now closed.
            # This could be an issue with how the external connection is managed.
            # Log: "Warning: External DatabaseConnection is not active. Re-establishing might be needed by the owner."
            # Optionally, could raise an error or try to reconnect if policy allows.
            # For now, we assume the external connection manager handles this.
            # If strict adherence is needed, one might raise an exception here.
            raise Error("External DatabaseConnection is not active.")


    # 3.3. _close_if_owned
    # -------------------------------------------------------------------------
    def _close_if_owned(self) -> None:
        """Closes the database connection if it was created and is managed by this repository instance."""
        if self.own_connection:
            self.db.close()
            # Log: "Internal DatabaseConnection closed by BaseRepository."

    # 3.4. execute_query (e.g., UPDATE, DELETE)
    # -------------------------------------------------------------------------
    def execute_query(self, query: str, params: tuple = None) -> int:
        """
        Executes a query that modifies data (UPDATE, DELETE) or DDL.
        Args:
            query: The SQL query string.
            params: A tuple of parameters to bind to the query.
        Returns:
            The number of rows affected by the query.
        Raises:
            mysql.connector.Error: If the query execution fails.
        """
        # Log: f"Executing query: {query} with params: {params}"
        try:
            self._ensure_connection()
            # Ensure cursor is valid
            if not self.db.cursor:
                # Log: "Error: Cursor not available for query execution."
                raise Error("Cursor not available for query execution.")
            self.db.cursor.execute(query, params or ())
            self.db.connection.commit()
            affected_rows = self.db.cursor.rowcount
            # Log: f"Query executed successfully. Rows affected: {affected_rows}"
            return affected_rows
        except Error as e:
            # Log: f"Error executing query: {e}. Rolling back transaction."
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                    # Log: "Transaction rolled back."
                except Error as rb_error:
                    # Log: f"Error during rollback: {rb_error}"
                    pass
            raise # Re-raise the original error
        finally:
            self._close_if_owned()

    # 3.5. fetch_one
    # -------------------------------------------------------------------------
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Executes a query and fetches a single result.
        Args:
            query: The SQL query string.
            params: A tuple of parameters to bind to the query.
        Returns:
            A dictionary representing the row, or None if no result is found or an error occurs.
        """
        # Log: f"Fetching one: {query} with params: {params}"
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # Log: "Error: Cursor not available for fetch_one."
                return None # Or raise Error("Cursor not available")
            self.db.cursor.execute(query, params or ())
            result = self.db.cursor.fetchone()
            # Log: f"Fetch one result: {'Found' if result else 'Not found'}"
            return result
        except Error as e:
            # Log: f"Error in fetch_one: {e}"
            return None # Suppress error and return None as per original behavior
        finally:
            self._close_if_owned()

    # 3.6. fetch_all
    # -------------------------------------------------------------------------
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Executes a query and fetches all results.
        Args:
            query: The SQL query string.
            params: A tuple of parameters to bind to the query.
        Returns:
            A list of dictionaries, where each dictionary represents a row.
            Returns an empty list if no results are found or an error occurs.
        """
        # Log: f"Fetching all: {query} with params: {params}"
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # Log: "Error: Cursor not available for fetch_all."
                return [] # Or raise Error("Cursor not available")
            self.db.cursor.execute(query, params or ())
            results = self.db.cursor.fetchall()
            # Log: f"Fetch all result: {len(results)} rows found."
            return results
        except Error as e:
            # Log: f"Error in fetch_all: {e}"
            return [] # Suppress error and return empty list as per original behavior
        finally:
            self._close_if_owned()

    # 3.7. insert
    # -------------------------------------------------------------------------
    def insert(self, query: str, params: tuple = None) -> Optional[int]:
        """
        Executes an INSERT query and returns the ID of the last inserted row.
        Args:
            query: The SQL INSERT query string.
            params: A tuple of parameters to bind to the query.
        Returns:
            The ID of the last inserted row, or None if the query doesn't generate an ID
            (e.g. multi-row insert without lastrowid support or error).
        Raises:
            mysql.connector.Error: If the query execution fails.
        """
        # Log: f"Inserting: {query} with params: {params}"
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # Log: "Error: Cursor not available for insert."
                raise Error("Cursor not available for insert operation.")
            self.db.cursor.execute(query, params or ())
            self.db.connection.commit()
            last_row_id = self.db.cursor.lastrowid
            # Log: f"Insert successful. Last row ID: {last_row_id}"
            return last_row_id
        except Error as e:
            # Log: f"Error during insert: {e}. Rolling back transaction."
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                    # Log: "Transaction rolled back due to insert error."
                except Error as rb_error:
                    # Log: f"Error during rollback after insert error: {rb_error}"
                    pass
            raise # Re-raise the original error
        finally:
            self._close_if_owned()
