# =============================================================================
# MIGRATIONS PACKAGE
# =============================================================================
# Bu paket, veritabanı tablolarının oluşturulması için migration dosyalarını içerir.
# =============================================================================

from .0000_models import create_models_table, drop_models_table

__all__ = ['create_models_table', 'drop_models_table']
