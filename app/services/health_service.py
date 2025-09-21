# =============================================================================
# HEALTH SERVICE
# =============================================================================
# Bu dosya, sistem sağlık kontrolü için servis sınıfını tanımlar.
# =============================================================================

from typing import Dict, Any
from datetime import datetime
from app.database.db_connection import test_connection

class HealthService:
    """
    Sistem sağlık kontrolü için servis sınıfı.
    """
    
    def check_health(self) -> Dict[str, Any]:
        """
        Sistem sağlık kontrolü yapar.
        
        Returns:
            Dict[str, Any]: Sağlık durumu bilgileri
        """
        try:
            db_status = test_connection()
            
            return {
                'success': True,
                'status': 'healthy' if db_status else 'unhealthy',
                'database': 'connected' if db_status else 'disconnected',
                'timestamp': str(datetime.now())
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'unhealthy',
                'error': str(e)
            }
