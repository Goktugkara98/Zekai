# =============================================================================
# Admin Deposu Modülü (Admin Repository Module)
# =============================================================================
# Bu modül, yönetici paneli işlemleri için bir depo sınıfı içerir.
# Kategori ve model yönetimi ile admin paneli istatistiklerinin alınması
# gibi işlevleri bir araya getirir. Diğer özelleşmiş depo sınıflarını kullanır.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. AdminRepository Sınıfı
#    2.1. __init__
#    2.2. Kategori Yönetimi (Category Management)
#         2.2.1. create_category                 : Yeni bir kategori oluşturur.
#         2.2.2. update_category                 : Mevcut bir kategoriyi günceller.
#         2.2.3. delete_category                 : Bir kategoriyi siler.
#         2.2.4. get_category_details            : Kategori detaylarını ve ilişkili modelleri getirir.
#         2.2.5. get_all_categories_with_models  : Tüm kategorileri ve ilişkili modellerini getirir.
#    2.3. Model Yönetimi (Model Management)
#         2.3.1. create_model                    : Yeni bir model oluşturur.
#         2.3.2. update_model                    : Mevcut bir modeli günceller.
#         2.3.3. delete_model                    : Bir modeli siler.
#         2.3.4. get_model_details               : Model detaylarını getirir.
#    2.4. Admin Paneli İstatistikleri (Admin Panel Statistics)
#         2.4.1. get_admin_dashboard_stats       : Admin paneli için genel istatistikleri getirir.
#    2.5. İkon Yönetimi (Icon Management) - Orijinal kodda vardı, gerekirse eklenebilir.
#         (2.5.1. get_available_icons)
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository, DatabaseConnection # Temel depo ve veritabanı bağlantısı
from app.repositories.category_repository import CategoryRepository # Kategori deposu
from app.repositories.model_repository import ModelRepository       # Model deposu
from app.models.entities import Category, Model # Varlık sınıfları
from typing import List, Optional, Tuple, Dict, Any
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import json # Detayları JSON olarak işlemek için

# 2. AdminRepository Sınıfı
# =============================================================================
class AdminRepository(BaseRepository):
    """Yönetici paneli işlemleri için depo (repository) sınıfı."""

    # 2.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        AdminRepository sınıfını başlatır.
        Eğer bir db_connection sağlanmazsa, BaseRepository kendi bağlantısını oluşturur.
        CategoryRepository ve ModelRepository örnekleri, aynı veritabanı bağlantısını
        kullanacak şekilde başlatılır.
        """
        super().__init__(db_connection) # BaseRepository'nin __init__ metodunu çağır
        # print(f"DEBUG: AdminRepository başlatılıyor. Harici bağlantı: {'Var' if db_connection else 'Yok'}")
        # self.db (DatabaseConnection örneği) BaseRepository tarafından ayarlanır.
        self.category_repo = CategoryRepository(self.db) # Aynı db bağlantısını kullan
        self.model_repo = ModelRepository(self.db)       # Aynı db bağlantısını kullan
        # print("DEBUG: CategoryRepository ve ModelRepository AdminRepository içinde başlatıldı.")

    # 2.2. Kategori Yönetimi (Category Management)
    # -------------------------------------------------------------------------
    # Bu metotlar doğrudan CategoryRepository'deki ilgili metotları çağırır.
    # AdminRepository, bu işlemleri merkezi bir noktadan sunar.

    # 2.2.1. create_category
    def create_category(self, name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
        """Yeni bir kategori oluşturur."""
        # print(f"DEBUG: AdminRepo -> create_category çağrıldı: Ad='{name}'")
        return self.category_repo.create_category(name, icon)

    # 2.2.2. update_category
    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """Mevcut bir kategoriyi günceller."""
        # print(f"DEBUG: AdminRepo -> update_category çağrıldı: ID={category_id}")
        return self.category_repo.update_category(category_id, name, icon)

    # 2.2.3. delete_category
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """
        Bir kategoriyi siler. CategoryRepository.delete_category metodu,
        ilişkili modellerin durumunu (SET NULL veya CASCADE) veritabanı şemasına göre yönetir.
        """
        # print(f"DEBUG: AdminRepo -> delete_category çağrıldı: ID={category_id}")
        return self.category_repo.delete_category(category_id)

    # 2.2.4. get_category_details
    def get_category_details(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Belirli bir kategorinin detaylarını ve bu kategoriye ait modelleri getirir.
        Args:
            category_id (int): Detayları alınacak kategori ID'si.
        Returns:
            Optional[Dict[str, Any]]: Kategori ve model bilgilerini içeren bir sözlük
                                      veya kategori bulunamazsa None.
        """
        # print(f"DEBUG: AdminRepo -> get_category_details çağrıldı: ID={category_id}")
        if not category_id or not isinstance(category_id, int) or category_id <= 0:
            # print("DEBUG: get_category_details için geçersiz ID.")
            return None

        category = self.category_repo.get_category_by_id(category_id)
        if not category:
            # print(f"DEBUG: ID'si {category_id} olan kategori bulunamadı (AdminRepo).")
            return None

        models = self.model_repo.get_models_by_category_id(category_id)
        # print(f"DEBUG: Kategori {category.name} için {len(models)} model bulundu.")

        return {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "models": [model.to_dict() for model in models if model] # model None değilse to_dict çağır
        }

    # 2.2.5. get_all_categories_with_models
    def get_all_categories_with_models(self) -> List[Dict[str, Any]]:
        """
        Tüm kategorileri ve her bir kategoriye ait modelleri listeler.
        Returns:
            List[Dict[str, Any]]: Her bir öğesi bir kategori ve o kategoriye ait
                                  modelleri içeren sözlüklerden oluşan bir liste.
        """
        # print("DEBUG: AdminRepo -> get_all_categories_with_models çağrıldı.")
        all_categories = self.category_repo.get_all_categories()
        result_list = []

        for category_entity in all_categories:
            if not category_entity: continue # Olası None durumunu atla

            models_in_category = self.model_repo.get_models_by_category_id(category_entity.id)
            result_list.append({
                "id": category_entity.id,
                "name": category_entity.name,
                "icon": category_entity.icon,
                "models": [model.to_dict() for model in models_in_category if model],
                "model_count": len(models_in_category) # Model sayısını da ekleyelim
            })
        # print(f"DEBUG: Toplam {len(result_list)} kategori ve modelleri getirildi.")
        return result_list

    # 2.3. Model Yönetimi (Model Management)
    # -------------------------------------------------------------------------
    # Bu metotlar doğrudan ModelRepository'deki ilgili metotları çağırır.

    # 2.3.1. create_model
    def create_model(self, category_id: int, name: str,
                     icon: Optional[str] = None, api_url: Optional[str] = None,
                     data_ai_index: Optional[str] = None,
                     description: Optional[str] = None,
                     details: Optional[Dict] = None,
                     image_filename: Optional[str] = None) -> Tuple[bool, str, Optional[int]]: # model_id eklendi
        """Yeni bir AI modeli oluşturur."""
        # print(f"DEBUG: AdminRepo -> create_model çağrıldı: Ad='{name}', KategoriID={category_id}")
        return self.model_repo.create_model(
            category_id=category_id, name=name, icon=icon, api_url=api_url,
            data_ai_index=data_ai_index, description=description, details=details,
            image_filename=image_filename
        )

    # 2.3.2. update_model
    def update_model(self, model_id: int, name: Optional[str] = None,
                     category_id: Optional[int] = None,
                     icon: Optional[str] = None, api_url: Optional[str] = None,
                     data_ai_index: Optional[str] = None,
                     description: Optional[str] = None,
                     details: Optional[Dict] = None,
                     image_filename: Optional[str] = None) -> Tuple[bool, str]:
        """Mevcut bir AI modelini günceller."""
        # print(f"DEBUG: AdminRepo -> update_model çağrıldı: ModelID={model_id}")
        return self.model_repo.update_model(
            model_id=model_id, name=name, category_id=category_id, icon=icon,
            api_url=api_url, data_ai_index=data_ai_index, description=description,
            details=details, image_filename=image_filename
        )

    # 2.3.3. delete_model
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """Bir AI modelini siler."""
        # print(f"DEBUG: AdminRepo -> delete_model çağrıldı: ModelID={model_id}")
        return self.model_repo.delete_model(model_id)

    # 2.3.4. get_model_details
    def get_model_details(self, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Belirli bir modelin detaylarını ve ait olduğu kategori bilgilerini getirir.
        Args:
            model_id (int): Detayları alınacak model ID'si.
        Returns:
            Optional[Dict[str, Any]]: Model ve kategori bilgilerini içeren bir sözlük
                                      veya model bulunamazsa None.
        """
        # print(f"DEBUG: AdminRepo -> get_model_details çağrıldı: ModelID={model_id}")
        if not model_id or not isinstance(model_id, int) or model_id <= 0:
            # print("DEBUG: get_model_details için geçersiz ID.")
            return None

        model = self.model_repo.get_model_by_id(model_id)
        if not model:
            # print(f"DEBUG: ID'si {model_id} olan model bulunamadı (AdminRepo).")
            return None

        model_dict = model.to_dict()

        if model.category_id: # category_id None olabilir (SET NULL nedeniyle)
            category = self.category_repo.get_category_by_id(model.category_id)
            model_dict['category_name'] = category.name if category else "Bilinmeyen Kategori"
            model_dict['category_icon'] = category.icon if category else None # Kategori ikonunu da ekleyelim
        else:
            model_dict['category_name'] = "Kategorisiz"
            model_dict['category_icon'] = None

        # print(f"DEBUG: Model {model.name} detayları: {model_dict}")
        return model_dict

    # 2.4. Admin Paneli İstatistikleri (Admin Panel Statistics)
    # -------------------------------------------------------------------------
    # 2.4.1. get_admin_dashboard_stats
    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        """
        Yönetici paneli için genel istatistikleri (toplam kategori, model sayıları
        ve son eklenen birkaç kategori/model) getirir.
        Returns:
            Dict[str, Any]: İstatistikleri içeren bir sözlük.
        """
        # print("DEBUG: AdminRepo -> get_admin_dashboard_stats çağrıldı.")
        stats = {
            'total_category_count': 0,
            'total_model_count': 0,
            'recent_categories': [], # Son eklenen kategoriler (örnek)
            'recent_models': [],     # Son eklenen modeller (örnek)
            'user_message_stats': {} # Kullanıcı mesaj istatistikleri
        }
        try:
            # Toplam kategori sayısı
            query_cat_count = "SELECT COUNT(*) as count FROM ai_categories"
            cat_count_result = self.fetch_one(query_cat_count)
            stats['total_category_count'] = cat_count_result['count'] if cat_count_result else 0

            # Toplam model sayısı
            query_model_count = "SELECT COUNT(*) as count FROM ai_models"
            model_count_result = self.fetch_one(query_model_count)
            stats['total_model_count'] = model_count_result['count'] if model_count_result else 0

            # Son 5 kategori (ID'ye göre tersten sıralı)
            recent_categories_entities = self.category_repo.get_all_categories() # Tümünü alıp Python'da sıralayabiliriz
            stats['recent_categories'] = [
                cat.to_dict() for cat in sorted(recent_categories_entities, key=lambda c: c.id, reverse=True)[:5]
            ]


            # Son 5 model (ID'ye göre tersten sıralı), kategori bilgisiyle birlikte
            query_recent_models = """
                SELECT m.id, m.name, m.icon as model_icon, m.data_ai_index,
                       c.name as category_name, c.icon as category_icon
                FROM ai_models m
                LEFT JOIN ai_categories c ON m.category_id = c.id
                ORDER BY m.id DESC
                LIMIT 5
            """
            # LEFT JOIN kullanıldı, böylece category_id'si NULL olan modeller de listelenebilir.
            recent_models_data = self.fetch_all(query_recent_models)
            stats['recent_models'] = recent_models_data if recent_models_data else []

            # Kullanıcı mesaj istatistikleri
            # UserMessageRepository'yi burada başlatmak yerine __init__ içinde de tutabiliriz.
            # Şimdilik burada oluşturalım. Eğer sık kullanılacaksa __init__ daha iyi olabilir.
            from app.repositories.user_message_repository import UserMessageRepository
            user_message_repo = UserMessageRepository(self.db)
            stats['user_message_stats'] = user_message_repo.get_message_stats()

            # print(f"DEBUG: Admin dashboard istatistikleri: {stats}")
        except MySQLError as e:
            # print(f"DEBUG: Admin dashboard istatistikleri alınırken veritabanı hatası: {e}")
            # Hata durumunda istatistiklerin bir kısmı dolu, bir kısmı boş olabilir.
            return stats
        except Exception as ex:
            # print(f"DEBUG: Admin dashboard istatistikleri alınırken beklenmedik hata: {ex}")
            return stats
        return stats

    # 2.5. İkon Yönetimi (Icon Management)
    # -------------------------------------------------------------------------
    # Orijinal admin_panel_database.py dosyasında get_available_icons metodu vardı.
    # Eğer bu işlevsellik hala gerekiyorsa, buraya eklenebilir.
    # Bu genellikle sabit bir listeden veya bir yapılandırma dosyasından okunur.
    # def get_available_icons(self) -> List[Dict[str, str]]:
    #     """Kullanılabilir Bootstrap ikonlarını (veya başka bir ikon setini) getirir."""
    #     # print("DEBUG: AdminRepo -> get_available_icons çağrıldı.")
    #     # Bu örnek, ikonların bir listesini döndürür.
    #     # Gerçek uygulamada bu liste bir yapılandırma dosyasından veya
    #     # veritabanındaki ayrı bir tablodan gelebilir.
    #     bootstrap_icons = [
    #         {"class": "bi bi-robot", "name": "Robot"},
    #         {"class": "bi bi-cpu", "name": "CPU"},
    #         {"class": "bi bi-lightbulb", "name": "Ampul"},
    #         {"class": "bi bi-chat-dots", "name": "Sohbet Baloncuğu"},
    #         {"class": "bi bi-image", "name": "Resim"},
    #         {"class": "bi bi-music-note-beamed", "name": "Müzik Notası"},
    #         # ... daha fazla ikon ...
    #     ]
    #     return bootstrap_icons

