# =============================================================================
# SEED DEFAULT ADMIN USER
# =============================================================================
# Inserts a default admin user for initial access if none exists.
# Email: admin@admin.com
# Password: 123456 (hashed)
# =============================================================================

import os
from app.database.db_connection import execute_query
from app.services.auth_service import AuthService


def seed_admin_user() -> bool:
    try:
        # Read config from environment
        enabled = os.getenv('SEED_ADMIN_ENABLED', 'true').lower() == 'true'
        if not enabled:
            return True

        email = os.getenv('SEED_ADMIN_EMAIL', 'admin@admin.com')
        password = os.getenv('SEED_ADMIN_PASSWORD', '123456')
        first_name = os.getenv('SEED_ADMIN_FIRST_NAME', 'Admin')
        last_name = os.getenv('SEED_ADMIN_LAST_NAME', 'User')
        is_verified = os.getenv('SEED_ADMIN_IS_VERIFIED', 'true').lower() == 'true'
        is_admin = os.getenv('SEED_ADMIN_IS_ADMIN', 'true').lower() == 'true'

        # If there is already at least one user, do not seed a default admin.
        # This ensures you can safely delete this bootstrap user later without it reappearing.
        user_count_rows = execute_query(
            "SELECT COUNT(*) as cnt FROM users",
            (),
            fetch=True,
        )
        total_users = (user_count_rows[0].get('cnt') if user_count_rows else 0) or 0
        if total_users > 0:
            return True

        # Hash the default password
        password_hash = AuthService.hash_password(password)

        # Insert admin user
        insert_sql = (
            "INSERT INTO users (email, password_hash, first_name, last_name, is_active, is_verified, is_admin) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (email, password_hash, first_name, last_name, True, is_verified, is_admin)
        execute_query(insert_sql, params, fetch=False)

        return True
    except Exception as e:
        return False
