# =============================================================================
# Admin Panel Database Module (ESKİ - DEPRECATED)
# =============================================================================
# NOT: Bu modül artık kullanılmamaktadır.
# Yeni geliştirmeler için lütfen aşağıdaki modülleri kullanın:
#
# - app/repositories/admin_repository.py: Admin paneli işlemleri
# - app/repositories/category_repository.py: Kategori işlemleri
# - app/repositories/model_repository.py: Model işlemleri
#
# Örnek kullanım:
# from app.repositories import AdminRepository
#
# # Admin repository'i kullan
# admin_repo = AdminRepository()
# 
# # Kategori oluştur
# success, message, category_id = admin_repo.create_category("Yeni Kategori", "bi-robot")
#
# # Tüm kategorileri ve modellerini getir
# categories_with_models = admin_repo.get_all_categories_with_models()
# =============================================================================

from app.repositories.admin_repository import AdminRepository as NewAdminRepository
from typing import Dict, List, Optional, Any, Tuple

class AdminRepository:
    """Admin paneli işlemleri için repository sınıfı (ESKİ - DEPRECATED).
    
    Bu sınıf artık kullanılmamaktadır.
    Yeni geliştirmeler için app.repositories.AdminRepository sınıfını kullanın.
    """
    
    def __init__(self, db_connection=None):
        # Yeni AdminRepository sınıfını kullan
        self._repo = NewAdminRepository(db_connection)
        
        # Geriye dönük uyumluluk için ai_repo özelliğini ekle
        from app.models.database import AIModelRepository
        self.ai_repo = AIModelRepository(db_connection)
    
    # Tüm metotları yeni AdminRepository sınıfına yönlendir
    def create_category(self, name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
        """Yeni bir kategori oluşturur."""
        return self._repo.create_category(name, icon)
    
    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """Var olan bir kategoriyi günceller."""
        return self._repo.update_category(category_id, name, icon)
    
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """Bir kategoriyi ve ilişkili tüm modelleri siler."""
        return self._repo.delete_category(category_id)
    
    def get_category_details(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Kategori detaylarını ve ilişkili modelleri getirir."""
        return self._repo.get_category_details(category_id)
    
    def create_model(self, category_id: int, name: str, icon: str, 
                     data_ai_index: str, api_url: str, request_method: str = 'POST',
                     request_headers: str = None, request_body_template: str = None,
                     response_path: str = None) -> Tuple[bool, str, Optional[int]]:
        """Yeni bir model oluşturur."""
        return self._repo.create_model(
            category_id, name, icon, data_ai_index, api_url, 
            request_method, request_headers, request_body_template, response_path
        )
    
    def update_model(self, model_id: int, category_id: int, name: str, 
                     icon: str, data_ai_index: str, api_url: str, request_method: str = 'POST',
                     request_headers: str = None, request_body_template: str = None,
                     response_path: str = None) -> Tuple[bool, str]:
        """Var olan bir modeli günceller."""
        return self._repo.update_model(
            model_id, category_id, name, icon, data_ai_index, api_url, 
            request_method, request_headers, request_body_template, response_path
        )
    
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """Bir modeli siler."""
        return self._repo.delete_model(model_id)
    
    def get_model_details(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Model detaylarını getirir."""
        return self._repo.get_model_details(model_id)
    
    def get_all_categories_with_models(self) -> List[Dict[str, Any]]:
        """Tüm kategorileri ve ilişkili modelleri getirir."""
        return self._repo.get_all_categories_with_models()
    
    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        """Admin paneli için istatistikleri getirir."""
        return self._repo.get_admin_dashboard_stats()
    
    def get_available_icons(self) -> List[Dict[str, str]]:
        """Kullanılabilir Bootstrap ikonlarını getirir."""
        return self._repo.get_available_icons()
