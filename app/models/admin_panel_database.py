# =============================================================================
# Admin Paneli Veritabanı Modülü (ESKİ - KULLANIM DIŞI)
# =============================================================================
# DİKKAT: Bu modül artık aktif olarak geliştirilmemekte ve kullanılmamaktadır.
#          Bu dosyadaki `AdminRepository` sınıfı, çağrıları yeni
#          `app.repositories.admin_repository.AdminRepository` sınıfına yönlendirir.
#          Yeni geliştirmeler için doğrudan yeni repository sınıflarını kullanın.
#
# YENİ YAPI VE ÖNERİLEN KULLANIM:
# --------------------------------
# - Admin paneliyle ilgili tüm veritabanı işlemleri için:
#   `app.repositories.admin_repository.AdminRepository`
#
# - Kategoriye özel işlemler için:
#   `app.repositories.category_repository.CategoryRepository`
#
# - Modele özel işlemler için:
#   `app.repositories.model_repository.ModelRepository`
#
# ÖRNEK KULLANIM (YENİ YAPI):
# --------------------------
# from app.repositories import AdminRepository # Yeni AdminRepository
# from app.models.base import DatabaseConnection
#
# # Bir veritabanı bağlantısı oluştur (opsiyonel, repository kendi bağlantısını yönetebilir)
# # db_conn = DatabaseConnection()
# # db_conn.connect()
#
# # Yeni AdminRepository'i kullan
# # admin_repo = AdminRepository(db_conn) # veya admin_repo = AdminRepository()
#
# # # Kategori oluşturma örneği
# # success, message, category_id = admin_repo.create_category("Yeni Kategori Adı", "bi-tag")
# # if success:
# #     print(f"Kategori oluşturuldu: {message}, ID: {category_id}")
# # else:
# #     print(f"Kategori oluşturma başarısız: {message}")
#
# # # Tüm kategorileri ve modellerini getir
# # categories_with_models = admin_repo.get_all_categories_with_models()
# # for cat_data in categories_with_models:
# #     print(f"Kategori: {cat_data['name']}, Model Sayısı: {cat_data['model_count']}")
#
# # # Bağlantıyı kapat (eğer manuel yönetiliyorsa)
# # db_conn.close()
# =============================================================================

from app.repositories.admin_repository import AdminRepository as NewAdminRepository
from app.models.database import AIModelRepository as OldAIModelRepository # Eski AIModelRepository (database.py'den)
from app.models.base import DatabaseConnection as NewDatabaseConnection # Yeni DatabaseConnection tipi
from typing import Dict, List, Optional, Any, Tuple

class AdminRepository:
    """
    Admin paneli işlemleri için repository sınıfı (ESKİ - KULLANIM DIŞI).

    Bu sınıf, çağrıları `app.repositories.admin_repository.AdminRepository`
    sınıfına yönlendirir. Yeni geliştirmeler için doğrudan yeni sınıfı kullanın.
    """

    def __init__(self, db_connection: Optional[NewDatabaseConnection] = None): # Tip ipucu yeni bağlantı tipiyle güncellendi
        """
        Eski AdminRepository sınıfını başlatır.
        Args:
            db_connection (Optional[NewDatabaseConnection]): Yeni tipte bir veritabanı bağlantısı.
                                                            Eğer None ise, yeni AdminRepository kendi
                                                            bağlantısını oluşturacaktır.
        """
        # print("UYARI: Eski AdminRepository sınıfı (admin_panel_database.py) başlatıldı.")
        # print("         Lütfen app.repositories.admin_repository.AdminRepository kullanın.")
        self._repo = NewAdminRepository(db_connection)

        # Geriye dönük uyumluluk için `ai_repo` özelliği:
        # Bu özellik, eski `AIModelRepository` (database.py içindeki) sınıfını örnekler.
        # Bu sınıf da kendi içinde yeni repository'lere yönlendirme yapar.
        # Bu katmanlı yönlendirme, eski kodun kırılmasını engellemek için olabilir,
        # ancak idealde bu tür bağımlılıklar kaldırılmalıdır.
        # print("UYARI: Eski AdminRepository içindeki 'ai_repo' özelliği, eski AIModelRepository'i kullanıyor.")
        self.ai_repo = OldAIModelRepository(db_connection) # db_connection None olabilir, OldAIModelRepository bunu yönetir.

    # =========================================================================
    # Kategori İşlemleri (Yeni AdminRepository'e Yönlendirilir)
    # =========================================================================
    def create_category(self, name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
        """Yeni bir kategori oluşturur (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): create_category -> Ad='{name}'")
        return self._repo.create_category(name, icon)

    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """Var olan bir kategoriyi günceller (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): update_category -> ID={category_id}")
        return self._repo.update_category(category_id, name, icon)

    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """Bir kategoriyi ve ilişkili tüm modelleri siler (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): delete_category -> ID={category_id}")
        return self._repo.delete_category(category_id)

    def get_category_details(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Kategori detaylarını ve ilişkili modelleri getirir (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): get_category_details -> ID={category_id}")
        return self._repo.get_category_details(category_id)

    # =========================================================================
    # Model İşlemleri (Yeni AdminRepository'e Yönlendirilir)
    # =========================================================================
    def create_model(self, category_id: int, name: str, icon: Optional[str] = None,
                     api_url: Optional[str] = None, description: Optional[str] = None,
                     details: Optional[dict] = None, # dict olarak tip ipucu
                     image_filename: Optional[str] = None
                     ) -> Tuple[bool, str, Optional[int]]: # model_id dönüşü eklendi
        """Yeni bir model oluşturur (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): create_model -> Ad='{name}', KategoriID={category_id}")
        # data_ai_index parametresi eski imzada yoktu, yeni _repo.create_model bunu bekliyor olabilir.
        # Yeni AdminRepository.create_model'in imzasına göre data_ai_index None olarak gidecek.
        # Eğer eski kodda details içinde data_ai_index varsa, o kullanılabilir.
        data_ai_index_from_details = None
        if details and isinstance(details, dict) and 'data_ai_index' in details:
            data_ai_index_from_details = details.get('data_ai_index')

        return self._repo.create_model(
            category_id=category_id,
            name=name,
            icon=icon,
            api_url=api_url,
            data_ai_index=data_ai_index_from_details, # details'dan gelen data_ai_index'i kullan
            description=description,
            details=details,
            image_filename=image_filename
        )

    def update_model(self, model_id: int, name: Optional[str] = None,
                     category_id: Optional[int] = None,
                     api_url: Optional[str] = None, description: Optional[str] = None,
                     details: Optional[dict] = None, icon: Optional[str] = None, # dict olarak tip ipucu
                     image_filename: Optional[str] = None
                     ) -> Tuple[bool, str]:
        """Var olan bir modeli günceller (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): update_model -> ModelID={model_id}")
        # data_ai_index parametresi eski imzada yoktu.
        data_ai_index_from_details = None
        if details and isinstance(details, dict) and 'data_ai_index' in details:
            data_ai_index_from_details = details.get('data_ai_index')

        return self._repo.update_model(
            model_id=model_id,
            name=name,
            category_id=category_id,
            api_url=api_url,
            data_ai_index=data_ai_index_from_details, # details'dan gelen data_ai_index'i kullan
            description=description,
            details=details,
            icon=icon,
            image_filename=image_filename
        )

    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """Bir modeli siler (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): delete_model -> ModelID={model_id}")
        return self._repo.delete_model(model_id)

    def get_model_details(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Model detaylarını getirir (ESKİ - Yönlendirme)."""
        # print(f"DEBUG (Eski AdminRepo): get_model_details -> ModelID={model_id}")
        return self._repo.get_model_details(model_id)

    # =========================================================================
    # Genel İşlemler (Yeni AdminRepository'e Yönlendirilir)
    # =========================================================================
    def get_all_categories_with_models(self) -> List[Dict[str, Any]]:
        """Tüm kategorileri ve ilişkili modelleri getirir (ESKİ - Yönlendirme)."""
        # print("DEBUG (Eski AdminRepo): get_all_categories_with_models çağrıldı")
        return self._repo.get_all_categories_with_models()

    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        """Admin paneli için istatistikleri getirir (ESKİ - Yönlendirme)."""
        # print("DEBUG (Eski AdminRepo): get_admin_dashboard_stats çağrıldı")
        return self._repo.get_admin_dashboard_stats()

    # =========================================================================
    # İkon Yönetimi (Yeni AdminRepository'e Yönlendirilir - Eğer orada varsa)
    # =========================================================================
    def get_available_icons(self) -> List[Dict[str, str]]:
        """
        Kullanılabilir Bootstrap ikonlarını getirir (ESKİ - Yönlendirme).
        Bu metodun yeni `AdminRepository` içinde de olması beklenir.
        """
        # print("DEBUG (Eski AdminRepo): get_available_icons çağrıldı")
        # Eğer yeni _repo'da bu metot yoksa hasattr ile kontrol edilebilir veya doğrudan çağrılabilir.
        if hasattr(self._repo, 'get_available_icons') and callable(getattr(self._repo, 'get_available_icons')):
            return self._repo.get_available_icons()
        else:
            # print("UYARI (Eski AdminRepo): Yeni AdminRepository'de get_available_icons metodu bulunamadı. Boş liste döndürülüyor.")
            # Fallback olarak boş liste veya varsayılan bir liste döndürebilir.
            # Örnek varsayılan liste:
            # return [
            #     {"class": "bi bi-archive", "name": "Arşiv (Varsayılan)"},
            #     {"class": "bi bi-gear", "name": "Ayarlar (Varsayılan)"}
            # ]
            return []


if __name__ == '__main__':
    print("="*60)
    print("UYARI: Bu modül (admin_panel_database.py) eskidir ve KULLANIM DIŞIDIR.")
    print("         Lütfen doğrudan app.repositories.admin_repository.AdminRepository")
    print("         ve diğer yeni repository sınıflarını kullanın.")
    print("="*60)

    # # Örnek Test (Yeni AdminRepository'nin çalıştığını doğrulamak için - dikkatli olun, veritabanını etkileyebilir)
    # print("\nESKİ AdminRepository üzerinden YENİ AdminRepository test ediliyor...")
    # try:
    #     # Yeni bir veritabanı bağlantısı oluştur (opsiyonel, None da geçilebilir)
    #     # test_db_conn = NewDatabaseConnection()
    #     # test_db_conn.connect()
    #
    #     eski_admin_repo = AdminRepository() # db_connection=test_db_conn None olacak, yeni repo kendi bağlantısını kuracak
    #
    #     print("\nTest: get_admin_dashboard_stats...")
    #     stats = eski_admin_repo.get_admin_dashboard_stats()
    #     if stats:
    #         print(f"Toplam Kategori: {stats.get('total_category_count')}")
    #         print(f"Toplam Model: {stats.get('total_model_count')}")
    #     else:
    #         print("İstatistikler alınamadı.")
    #
    #     print("\nTest: get_available_icons...")
    #     icons = eski_admin_repo.get_available_icons()
    #     if icons:
    #         print(f"Mevcut ikonlardan bazıları: {icons[:2]}")
    #     else:
    #         print("İkon listesi boş veya alınamadı.")
    #
    #     # test_db_conn.close() # Eğer manuel bağlantı oluşturulduysa kapat
    #     print("\nEski AdminRepository testleri tamamlandı.")
    #
    # except Exception as e:
    #     print(f"Test sırasında bir hata oluştu: {e}")

