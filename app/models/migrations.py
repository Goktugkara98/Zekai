# =============================================================================
# Database Migrations Module
# =============================================================================
# Contents:
# 1. Imports
# 2. DatabaseMigrations Class
#    2.1. __init__
#    2.2. create_all_tables
#    2.3. create_categories_table
#    2.4. create_models_table
#    2.5. create_user_messages_table
#    2.6. migrate_user_messages_table
#    2.7. check_database_status
# 3. Helper Functions
#    3.1. initialize_database
#    3.2. migrate_database
# =============================================================================

# 1. Imports
# =============================================================================
from app.models.base import DatabaseConnection
from mysql.connector import Error # Specific error type
from typing import Tuple, List, Dict, Any

# 2. DatabaseMigrations Class
# =============================================================================
class DatabaseMigrations:
    """Class for database table creation and migration operations."""

    # 2.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self):
        """Initializes the DatabaseMigrations class."""
        self.db = DatabaseConnection()

    # 2.2. create_all_tables
    # -------------------------------------------------------------------------
    def create_all_tables(self) -> bool:
        """Creates all necessary database tables if they don't exist."""
        all_created_successfully = True
        try:
            self.db._ensure_connection() # Ensure connection is active

            # Order matters due to foreign key constraints
            if not self.create_categories_table():
                all_created_successfully = False
                # Log: "Failed to create categories table."
            if not self.create_models_table():
                all_created_successfully = False
                # Log: "Failed to create models table."
            if not self.create_user_messages_table():
                all_created_successfully = False
                # Log: "Failed to create user_messages table."

            return all_created_successfully
        except Error as e:
            # Log: f"Error during create_all_tables: {e}"
            return False
        finally:
            self.db.close() # Ensure connection is closed

    # 2.3. create_categories_table
    # -------------------------------------------------------------------------
    def create_categories_table(self) -> bool:
        """Creates the 'ai_categories' table if it doesn't exist."""
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL COMMENT 'Category name',
                    icon VARCHAR(255) COMMENT 'Category icon (e.g., FontAwesome class)'
                ) COMMENT 'Stores AI categories';
            """)
            self.db.connection.commit()
            # Log: "ai_categories table checked/created successfully."
            return True
        except Error as e:
            # Log: f"Error creating ai_categories table: {e}"
            if self.db.connection:
                self.db.connection.rollback()
            return False

    # 2.4. create_models_table
    # -------------------------------------------------------------------------
    def create_models_table(self) -> bool:
        """Creates the 'ai_models' table if it doesn't exist."""
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category_id INT,
                    name VARCHAR(255) NOT NULL COMMENT 'Model name',
                    icon VARCHAR(255) COMMENT 'Model icon',
                    data_ai_index VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique index for AI model identification',
                    api_url VARCHAR(2048) NOT NULL COMMENT 'API endpoint URL',
                    request_method VARCHAR(10) DEFAULT 'POST' COMMENT 'HTTP request method',
                    request_headers TEXT COMMENT 'JSON string of request headers',
                    request_body_template TEXT COMMENT 'JSON template for request body',
                    response_path TEXT COMMENT 'Path to extract response from JSON (e.g., candidates[0].text)',
                    FOREIGN KEY (category_id) REFERENCES ai_categories(id) ON DELETE SET NULL ON UPDATE CASCADE
                ) COMMENT 'Stores AI models and their configurations';
            """)
            # Changed ON DELETE CASCADE to ON DELETE SET NULL for ai_models.category_id
            # to prevent accidental deletion of models when a category is deleted.
            # User should explicitly delete models or reassign them.
            self.db.connection.commit()
            # Log: "ai_models table checked/created successfully."
            return True
        except Error as e:
            # Log: f"Error creating ai_models table: {e}"
            if self.db.connection:
                self.db.connection.rollback()
            return False

    # 2.5. create_user_messages_table
    # -------------------------------------------------------------------------
    def create_user_messages_table(self) -> bool:
        """Creates the 'user_messages' table if it doesn't exist."""
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255) COMMENT 'User session identifier',
                    user_id VARCHAR(255) COMMENT 'User identifier (if logged in)',
                    user_message TEXT COMMENT 'The message sent by the user',
                    prompt TEXT COMMENT 'The full prompt sent to the AI (can include history)',
                    ai_response TEXT COMMENT 'The response from the AI',
                    ai_model_name VARCHAR(255) COMMENT 'Name of the AI model used (data_ai_index)',
                    model_params TEXT COMMENT 'JSON string of parameters used for the AI model',
                    request_json TEXT COMMENT 'JSON string of the actual request sent to AI',
                    response_json TEXT COMMENT 'JSON string of the actual response from AI',
                    tokens INT COMMENT 'Number of tokens used for the interaction',
                    duration FLOAT COMMENT 'Duration of the AI call in seconds',
                    error_message TEXT COMMENT 'Any error message if the AI call failed',
                    status VARCHAR(32) COMMENT 'Status of the message (e.g., success, error, pending)',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp of the message'
                ) COMMENT 'Stores user interactions with AI models';
            """)
            # Added ON UPDATE CURRENT_TIMESTAMP to timestamp for better tracking of last update.
            self.db.connection.commit()
            # Log: "user_messages table checked/created successfully."
            return True
        except Error as e:
            # Log: f"Error creating user_messages table: {e}"
            if self.db.connection:
                self.db.connection.rollback()
            return False

    # 2.6. migrate_user_messages_table
    # -------------------------------------------------------------------------
    def migrate_user_messages_table(self) -> Tuple[bool, List[str]]:
        """Adds new columns to the 'user_messages' table if they don't exist.
           This is a simple migration example; more complex migrations might need a dedicated library.
        """
        added_columns = []
        migration_successful = True
        try:
            self.db._ensure_connection()
            # Columns to add with their types and optional comments for ALTER TABLE
            columns_to_add = [
                ("user_id", "VARCHAR(255)", "AFTER session_id", "User identifier"),
                ("prompt", "TEXT", "AFTER user_message", "Full prompt to AI"),
                ("model_params", "TEXT", "AFTER ai_model_name", "AI model parameters"),
                ("request_json", "TEXT", "AFTER model_params", "Actual request JSON"),
                ("response_json", "TEXT", "AFTER request_json", "Actual response JSON"),
                ("tokens", "INT", "AFTER response_json", "Tokens used"),
                ("duration", "FLOAT", "AFTER tokens", "AI call duration"),
                ("error_message", "TEXT", "AFTER duration", "Error message from AI call"),
                ("status", "VARCHAR(32)", "AFTER error_message", "Status of the message")
            ]

            for col_name, col_type, col_position, col_comment in columns_to_add:
                try:
                    # Check if column exists first
                    self.db.cursor.execute(f"""
                        SELECT COUNT(*) AS count
                        FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = 'user_messages'
                        AND COLUMN_NAME = '{col_name}';
                    """)
                    if self.db.cursor.fetchone()['count'] == 0:
                        self.db.cursor.execute(
                            f"ALTER TABLE user_messages ADD COLUMN {col_name} {col_type} "
                            f"COMMENT '{col_comment}' {col_position};"
                        )
                        added_columns.append(col_name)
                        # Log: f"Column {col_name} added to user_messages table."
                    else:
                        # Log: f"Column {col_name} already exists in user_messages table."
                        pass
                except Error as e:
                    # Log: f"Error adding column {col_name} to user_messages: {e}"
                    # Decide if one failure should stop all: here, we continue but mark as not fully successful
                    migration_successful = False
                    # Optional: if "Duplicate column name" in str(e): pass, else: raise

            if migration_successful and added_columns: # Commit only if any columns were actually added and no errors for those.
                self.db.connection.commit()
            elif not added_columns and migration_successful: # No columns to add, no errors
                pass # It's fine, nothing to do
            else: # Errors occurred or commit was skipped
                if self.db.connection: self.db.connection.rollback() # Rollback if something went wrong

            return migration_successful, added_columns
        except Error as e:
            # Log: f"General error during migrate_user_messages_table: {e}"
            if self.db.connection:
                self.db.connection.rollback()
            return False, added_columns
        finally:
            self.db.close()

    # 2.7. check_database_status
    # -------------------------------------------------------------------------
    def check_database_status(self) -> Dict[str, Any]:
        """Checks the status of the database, including table existence and row counts."""
        status = {
            'database_name': None,
            'tables': {},
            'row_counts': {},
            'connection_status': 'Disconnected',
            'overall_success': False
        }

        try:
            self.db._ensure_connection()
            status['connection_status'] = 'Connected'
            status['database_name'] = self.db.connection.database

            tables_to_check = ['ai_categories', 'ai_models', 'user_messages']
            for table_name in tables_to_check:
                try:
                    self.db.cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = '{table_name}'")
                    table_exists = self.db.cursor.fetchone()['COUNT(*)'] > 0

                    if table_exists:
                        self.db.cursor.execute(f"DESCRIBE {table_name}")
                        columns_data = self.db.cursor.fetchall()
                        column_details = {col['Field']: {'type': col['Type'], 'null': col['Null'], 'key': col['Key'], 'default': col['Default'], 'extra': col['Extra']} for col in columns_data}

                        status['tables'][table_name] = {
                            'exists': True,
                            'column_count': len(columns_data),
                            'columns': column_details
                        }

                        self.db.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                        count = self.db.cursor.fetchone()['count']
                        status['row_counts'][table_name] = count
                    else:
                        status['tables'][table_name] = {'exists': False, 'column_count': 0, 'columns': {}}
                        status['row_counts'][table_name] = 0
                except Error as e:
                    # Log: f"Error checking table {table_name}: {e}"
                    status['tables'][table_name] = {'exists': False, 'error': str(e)}
                    status['row_counts'][table_name] = 0
            status['overall_success'] = True
        except Error as e:
            # Log: f"Database connection error in check_database_status: {e}"
            status['connection_status'] = f"Error: {str(e)}"
            status['overall_success'] = False
        finally:
            self.db.close()
        return status

# 3. Helper Functions
# =============================================================================

# 3.1. initialize_database
# -----------------------------------------------------------------------------
def initialize_database() -> bool:
    """Initializes the database and creates necessary tables.
    Returns True if all tables are created successfully, False otherwise.
    """
    # Log: "Initializing database..."
    migrations = DatabaseMigrations()
    success = migrations.create_all_tables()
    if success:
        # Log: "Database initialized successfully."
        pass
    else:
        # Log: "Database initialization failed."
        pass
    return success

# 3.2. migrate_database
# -----------------------------------------------------------------------------
def migrate_database() -> Tuple[bool, List[str]]:
    """Runs database migrations, e.g., adding new columns to existing tables.
    Returns a tuple (success_status, list_of_added_columns).
    """
    # Log: "Starting database migration..."
    migrations = DatabaseMigrations()
    success, added_columns = migrations.migrate_user_messages_table()
    if success:
        if added_columns:
            # Log: f"Database migration successful. Added columns: {', '.join(added_columns)}"
            pass
        else:
            # Log: "Database migration checked. No new columns to add."
            pass
    else:
        # Log: "Database migration failed."
        pass
    return success, added_columns

# Example of how to run (typically called from main.py or a setup script)
if __name__ == '__main__':
    print("Initializing database...")
    if initialize_database():
        print("Database initialized successfully.")
        print("\nRunning migrations...")
        mig_success, mig_cols = migrate_database()
        if mig_success:
            if mig_cols:
                print(f"Migrations applied for columns: {', '.join(mig_cols)}")
            else:
                print("No new migrations to apply.")
        else:
            print("Migrations failed.")

        print("\nChecking database status...")
        db_status = DatabaseMigrations().check_database_status()
        import json
        print(json.dumps(db_status, indent=4))
    else:
        print("Database initialization failed.")
