# =============================================================================
# MIGRATIONS PACKAGE
# =============================================================================
# Bu paket, veritabanı tablolarının oluşturulması için migration dosyalarını içerir.
# =============================================================================

from .migration_0000_models import create_models_table, drop_models_table
from .migration_0001_users import run_migration as users_migration_run
from .migration_0002_categories import run_migration as categories_migration_run
from .migration_0003_chats import run_migration as chats_migration_run
from .migration_0004_messages import run_migration as messages_migration_run, drop_messages_table

__all__ = [
    'create_models_table',
    'drop_models_table',
    'users_migration_run',
    'categories_migration_run',
    'chats_migration_run',
    'messages_migration_run',
    'drop_messages_table',
]
