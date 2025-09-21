# =============================================================================
# SEEDERS PACKAGE
# =============================================================================
# Bu paket, veritabanı için başlangıç verilerini (seed) ekleyen betikleri içerir.
# =============================================================================

from .seed_categories import seed_categories
from .seed_admin_user import seed_admin_user

__all__ = [
    'seed_categories',
    'seed_admin_user',
]
