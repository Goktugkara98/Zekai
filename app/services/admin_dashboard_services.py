# =============================================================================
# Admin Dashboard Servisleri Modülü (Admin Dashboard Services Module)
# =============================================================================
# Bu modül, yönetici paneli için backend iş mantığını ve servislerini içerir.
# Veritabanı işlemleri, veri dönüşümleri ve rota katmanına veri sağlama
# gibi görevleri yerine getiren servis sınıflarını barındırır.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
#     2.1. simple_model_to_dict        : Bir model nesnesini sözlüğe dönüştürür.
# 3.0 SERVİS SINIFLARI (SERVICE CLASSES)
#     3.1. CategoryService
#          3.1.1. __init__                       : Başlatıcı metot.
#          3.1.2. get_all_categories_for_display : Tüm kategorileri gösterim için hazırlar.
#          3.1.3. add_category                   : Yeni bir kategori ekler.
#          3.1.4. delete_category                : Bir kategoriyi siler.
#          3.1.5. update_category                : Bir kategoriyi günceller.
#     3.2. AIModelService
#          3.2.1. __init__                       : Başlatıcı metot.
#          3.2.2. get_all_models_for_display     : Tüm AI modellerini gösterim için hazırlar.
#          3.2.3. add_model_via_dict             : Sözlük verisinden yeni bir AI modeli ekler.
#          3.2.4. delete_model                   : Bir AI modelini siler.
#          3.2.5. update_model_via_dict          : Sözlük verisiyle bir AI modelini günceller.
#     3.3. UserService
#          3.3.1. __init__                       : Başlatıcı metot.
#          3.3.2. get_all_users_for_display      : Tüm kullanıcıları gösterim için hazırlar.
#     3.4. DashboardService
#          3.4.1. __init__                       : Başlatıcı metot.
#          3.4.2. get_dashboard_stats            : Dashboard için genel istatistikleri toplar.
#     3.5. SettingsService
#          3.5.1. get_settings_for_display       : Uygulama ayarlarını gösterim için hazırlar.
#          3.5.2. save_settings                  : Uygulama ayarlarını kaydeder.
# 4.0 VERİTABANI OTURUMU YÖNETİMİ NOTLARI (DATABASE SESSION MANAGEMENT NOTES)
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
import json
import traceback
from typing import Dict, Any, List, Optional, Union

from flask import current_app

from app.models.base import DatabaseConnection
from app.models.entities.category import Category
from app.models.entities.model import Model as AIModelEntity
# from app.models.entities.user import User # Kullanıcı modeli eklendiğinde

from app.repositories.category_repository import CategoryRepository
from app.repositories.model_repository import ModelRepository
# from app.repositories.user_repository import UserRepository # Kullanıcı deposu eklendiğinde

# =============================================================================
# 2.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# =============================================================================

# -----------------------------------------------------------------------------
# 2.1. Bir model nesnesini sözlüğe dönüştürür (simple_model_to_dict)
# -----------------------------------------------------------------------------
def simple_model_to_dict(instance: Optional[Any],
                         columns: Optional[List[str]] = None,
                         relationships: Optional[Dict[str, Union[List[str], Dict[str, Any]]]] = None) -> Optional[Dict[str, Any]]:
    """
    Bir SQLAlchemy model nesnesini veya benzeri bir nesneyi basit bir sözlüğe dönüştürür.
    """
    if not instance:
        return None

    data: Dict[str, Any] = {}

    if columns:
        for col_name in columns:
            if hasattr(instance, col_name):
                data[col_name] = getattr(instance, col_name)
            else:
                data[col_name] = None
    elif hasattr(instance, 'to_dict') and callable(getattr(instance, 'to_dict')):
        try:
            data = instance.to_dict()
        except Exception as e:
            current_app.logger.error(f"simple_model_to_dict: {instance.__class__.__name__}.to_dict() error: {e}", exc_info=True)
            data = {k: v for k, v in instance.__dict__.items() if not k.startswith('_')}
    else:
        data = {k: v for k, v in instance.__dict__.items() if not k.startswith('_')}

    if relationships:
        for rel_name, rel_config in relationships.items():
            related_instance = getattr(instance, rel_name, None)
            if related_instance:
                rel_cols: Optional[List[str]] = None
                rel_rels: Optional[Dict[str, Any]] = None

                if isinstance(rel_config, list):
                    rel_cols = rel_config
                elif isinstance(rel_config, dict):
                    rel_cols = rel_config.get('columns')
                    rel_rels = rel_config.get('relationships')

                if isinstance(related_instance, list):
                    data[rel_name] = [
                        simple_model_to_dict(item, columns=rel_cols, relationships=rel_rels)
                        for item in related_instance if item is not None # None kontrolü eklendi
                    ]
                else:
                    data[rel_name] = simple_model_to_dict(related_instance, columns=rel_cols, relationships=rel_rels)
            else:
                data[rel_name] = None
    return data

# =============================================================================
# 3.0 SERVİS SINIFLARI (SERVICE CLASSES)
# =============================================================================

# -----------------------------------------------------------------------------
# 3.1. CategoryService
# -----------------------------------------------------------------------------
class CategoryService:
    """Kategori ile ilgili işlemleri yöneten servis sınıfı."""
    # -------------------------------------------------------------------------
    # 3.1.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self):
        self.category_repo = CategoryRepository()
        self.model_repo = ModelRepository()

    # -------------------------------------------------------------------------
    # 3.1.2. Tüm kategorileri gösterim için hazırlar (get_all_categories_for_display)
    # -------------------------------------------------------------------------
    def get_all_categories_for_display(self) -> List[Dict[str, Any]]:
        """
        Tüm kategorileri, her bir kategoriye ait model sayısı ile birlikte
        gösterim için hazırlar.
        """
        db_connection_instance_category: Optional[DatabaseConnection] = None
        db_connection_instance_model: Optional[DatabaseConnection] = None
        try:
            # Repolar için ayrı bağlantı örnekleri oluşturulabilir veya aynı bağlantı paylaşılabilir.
            # Bu örnekte, her repo kendi bağlantısını yönetiyorsa bu satırlara gerek yok.
            # Eğer servis katmanı bağlantıyı yönetiyorsa:
            db_connection_instance_category = DatabaseConnection()
            self.category_repo.db = db_connection_instance_category # Repoya bağlantıyı ata

            db_connection_instance_model = DatabaseConnection()
            self.model_repo.db = db_connection_instance_model


            categories_raw: List[Category] = self.category_repo.get_all_categories()
            categories_data: List[Dict[str, Any]] = []
            for cat_entity in categories_raw:
                # Category entity'sinin 'icon' ve 'description' alanları olmayabilir,
                # bu yüzden simple_model_to_dict'e columns parametresi vermek daha güvenli.
                # Category entity'sinde bu alanlar varsa, bu şekilde kullanılabilir.
                cat_dict = simple_model_to_dict(cat_entity, columns=['id', 'name', 'icon']) # 'description' çıkarıldı, Category entity'sinde yoksa
                if cat_dict and cat_entity.id is not None: # id None değilse devam et
                    cat_dict['model_count'] = self.model_repo.count_all_models()
                    categories_data.append(cat_dict)
            return categories_data
        except Exception as e:
            current_app.logger.error(f"Kategoriler yüklenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise
        finally:
            if db_connection_instance_category:
                db_connection_instance_category.close()
            if db_connection_instance_model and db_connection_instance_model != db_connection_instance_category:
                db_connection_instance_model.close()


    # -------------------------------------------------------------------------
    # 3.1.3. Yeni bir kategori ekler (add_category)
    # -------------------------------------------------------------------------
    def add_category(self, name: str, description: Optional[str] = None, icon: Optional[str] = None) -> Dict[str, Any]:
        """
        Yeni bir kategori ekler. 'description' Category entity'sinde yoksa kaldırılmalı.
        """
        db_connection_instance: Optional[DatabaseConnection] = None
        try:
            db_connection_instance = DatabaseConnection()
            self.category_repo.db = db_connection_instance

            existing_category = self.category_repo.get_category_by_name(name)
            if existing_category:
                raise ValueError(f"'{name}' adında bir kategori zaten mevcut.")

            # create_category 'icon' parametresini almalı.
            # CategoryRepository.create_category metodu (bool, str, Optional[int]) döndürüyor.
            success, message, category_id = self.category_repo.create_category(name=name, icon=icon or "") # icon None ise boş string
            if not success or category_id is None:
                raise ValueError(message or "Kategori oluşturulamadı.")

            new_category_entity = self.category_repo.get_category_by_id(category_id)
            if not new_category_entity:
                raise Exception(f"Kategori oluşturuldu (ID: {category_id}) ancak veritabanından çekilemedi.")

            # Category entity'sinde 'description' yoksa buradan da çıkarılmalı.
            return simple_model_to_dict(new_category_entity, columns=['id', 'name', 'icon'])  # 'description' çıkarıldı
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori eklenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise Exception("Kategori eklenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_connection_instance:
                db_connection_instance.close()

    # -------------------------------------------------------------------------
    # 3.1.4. Bir kategoriyi siler (delete_category)
    # -------------------------------------------------------------------------
    def delete_category(self, category_id: int) -> bool:
        """Bir kategoriyi ID'sine göre siler."""
        db_connection_instance_category: Optional[DatabaseConnection] = None
        db_connection_instance_model: Optional[DatabaseConnection] = None
        try:
            db_connection_instance_category = DatabaseConnection()
            self.category_repo.db = db_connection_instance_category
            db_connection_instance_model = DatabaseConnection()
            self.model_repo.db = db_connection_instance_model

            category_to_delete = self.category_repo.get_category_by_id(category_id)
            if not category_to_delete:
                raise ValueError(f"ID'si {category_id} olan kategori bulunamadı.")

            if self.model_repo.count_models_by_category_id(category_id) > 0:
                raise ValueError("Bu kategoriye bağlı AI modelleri bulunmaktadır. Önce modelleri silin veya başka bir kategoriye taşıyın.")

            success, message = self.category_repo.delete_category(category_id)
            if not success:
                 raise Exception(message or f"Kategori (ID: {category_id}) silinemedi.")
            return True
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori (ID: {category_id}) silinirken hata (CategoryService): {str(e)}", exc_info=True)
            raise Exception(f"Kategori (ID: {category_id}) silinirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_connection_instance_category:
                db_connection_instance_category.close()
            if db_connection_instance_model and db_connection_instance_model != db_connection_instance_category:
                db_connection_instance_model.close()

    # -------------------------------------------------------------------------
    # 3.1.5. Bir kategoriyi günceller (update_category)
    # -------------------------------------------------------------------------
    def update_category(self, category_id: int, name: str, description: Optional[str] = None, icon: Optional[str] = None) -> Dict[str, Any]:
        """
        Mevcut bir kategoriyi ID'sine göre günceller.
        'description' Category entity'sinde yoksa kaldırılmalı.
        """
        db_connection_instance: Optional[DatabaseConnection] = None
        try:
            db_connection_instance = DatabaseConnection()
            self.category_repo.db = db_connection_instance

            category_to_update = self.category_repo.get_category_by_id(category_id)
            if not category_to_update:
                raise ValueError(f"Güncellenecek kategori (ID: {category_id}) bulunamadı.")

            if name != category_to_update.name:
                existing_category_with_new_name = self.category_repo.get_category_by_name(name)
                if existing_category_with_new_name and existing_category_with_new_name.id != category_id:
                    raise ValueError(f"'{name}' adında başka bir kategori zaten mevcut.")

            # CategoryRepository.update_category metodu (bool, str) döndürüyor ve sadece name, icon alıyor.
            # Eğer description da güncellenecekse, repository metodu da güncellenmeli.
            # Şimdilik sadece name ve icon güncelleniyor.
            success, message = self.category_repo.update_category(category_id, name, icon or "") # icon None ise boş string

            if not success:
                # "değişiklik yapılmadı" mesajı başarılı bir durum olarak ele alınabilir.
                if "değişiklik yapılmadı" not in message.lower() and "veriler aynı" not in message.lower() :
                    raise Exception(message or f"Kategori (ID: {category_id}) güncellenemedi.")

            updated_category_entity = self.category_repo.get_category_by_id(category_id)
            if not updated_category_entity:
                raise Exception(f"Kategori güncellendi ancak veritabanından çekilemedi (ID: {category_id}).")

            return simple_model_to_dict(updated_category_entity, columns=['id', 'name', 'icon']) # 'description' çıkarıldı
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori (ID: {category_id}) güncellenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise Exception(f"Kategori (ID: {category_id}) güncellenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_connection_instance:
                db_connection_instance.close()

# -----------------------------------------------------------------------------
# 3.2. AIModelService
# -----------------------------------------------------------------------------
class AIModelService:
    """AI Modelleri ile ilgili işlemleri yöneten servis sınıfı."""
    # -------------------------------------------------------------------------
    # 3.2.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()

    # -------------------------------------------------------------------------
    # 3.2.2. Tüm AI modellerini gösterim için hazırlar (get_all_models_for_display)
    # -------------------------------------------------------------------------
    def get_all_models_for_display(self) -> List[Dict[str, Any]]:
        """
        Tüm AI modellerini, bağlı oldukları kategori adı ile birlikte
        gösterim için hazırlar.
        """
        db_conn_model: Optional[DatabaseConnection] = None
        db_conn_category: Optional[DatabaseConnection] = None
        try:
            db_conn_model = DatabaseConnection()
            self.model_repo.db = db_conn_model
            db_conn_category = DatabaseConnection()
            self.category_repo.db = db_conn_category

            models_raw: List[AIModelEntity] = self.model_repo.get_all_models(include_api_keys=False)
            models_data: List[Dict[str, Any]] = []

            category_ids = list(set(model.category_id for model in models_raw if model.category_id))
            categories_map: Dict[int, Category] = {}
            if category_ids:
                for cat_id in category_ids: # Tek tek çekmek yerine toplu çekme metodu (get_categories_by_ids) daha verimli olurdu.
                    cat = self.category_repo.get_category_by_id(cat_id)
                    if cat and cat.id is not None: # cat.id None kontrolü
                        categories_map[cat.id] = cat

            for model_entity in models_raw:
                model_dict = simple_model_to_dict(model_entity)
                if model_dict:
                    category_id = model_entity.category_id
                    if category_id and category_id in categories_map:
                        model_dict['category_name'] = categories_map[category_id].name
                    elif category_id:
                         model_dict['category_name'] = f"Kategori ID: {category_id} (Bulunamadı)"
                    else:
                        model_dict['category_name'] = "N/A (Kategori Belirtilmemiş)"
                    models_data.append(model_dict)
            return models_data
        except Exception as e:
            current_app.logger.error(f"AI Modelleri yüklenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise
        finally:
            if db_conn_model:
                db_conn_model.close()
            if db_conn_category and db_conn_category != db_conn_model:
                db_conn_category.close()

    # -------------------------------------------------------------------------
    # 3.2.3. Sözlük verisinden yeni bir AI modeli ekler (add_model_via_dict)
    # -------------------------------------------------------------------------
    def add_model_via_dict(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verilen sözlükteki verileri kullanarak yeni bir AI modeli ekler.
        """
        db_connection_instance_model: Optional[DatabaseConnection] = None
        db_connection_instance_category: Optional[DatabaseConnection] = None
        try:
            db_connection_instance_model = DatabaseConnection()
            self.model_repo.db = db_connection_instance_model
            db_connection_instance_category = DatabaseConnection()
            self.category_repo.db = db_connection_instance_category

            # Zorunlu alanların kontrolü
            required_fields = ['name', 'category_id', 'service_provider', 'external_model_name']
            for field in required_fields:
                if not model_data.get(field) or (isinstance(model_data.get(field), str) and not str(model_data[field]).strip()):
                    raise ValueError(f"'{field}' alanı zorunludur ve boş olamaz.")
            if not isinstance(model_data['category_id'], int) or model_data['category_id'] <= 0:
                raise ValueError("Geçerli bir kategori ID'si girilmelidir.")

            category = self.category_repo.get_category_by_id(model_data['category_id'])
            if not category:
                raise ValueError(f"Belirtilen kategori (ID: {model_data['category_id']}) bulunamadı.")

            # ModelRepository.create_model metodu tüm bu alanları kabul etmeli
            success, message, model_id = self.model_repo.create_model(
                category_id=model_data['category_id'],
                name=str(model_data['name']).strip(),
                icon=str(model_data.get('icon', '')).strip() or None,
                description=str(model_data.get('description', '')).strip() or None,
                details=model_data.get('details'), # JSON olabilir
                service_provider=str(model_data['service_provider']).strip(),
                external_model_name=str(model_data['external_model_name']).strip(),
                api_url=str(model_data.get('api_url', '')).strip() or None,
                request_method=str(model_data.get('request_method', 'POST')).upper().strip(),
                request_headers=model_data.get('request_headers'), # JSON olabilir
                request_body=model_data.get('request_body'), # JSON olabilir
                response_path=str(model_data.get('response_path', '')).strip() or None,
                api_key=model_data.get('api_key'),
                prompt_template=str(model_data.get('prompt_template', '')).strip() or None,
                status=str(model_data.get('status', 'active')).lower().strip()
            )

            if not success or model_id is None:
                raise ValueError(message or "AI Modeli oluşturulamadı.")

            new_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False)
            if not new_model_entity:
                raise Exception(f"AI Modeli oluşturuldu (ID: {model_id}) ancak veritabanından çekilemedi.")

            return simple_model_to_dict(new_model_entity)
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli eklenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise Exception("AI Modeli eklenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_connection_instance_model:
                db_connection_instance_model.close()
            if db_connection_instance_category and db_connection_instance_category != db_connection_instance_model:
                db_connection_instance_category.close()

    # -------------------------------------------------------------------------
    # 3.2.4. Bir AI modelini siler (delete_model)
    # -------------------------------------------------------------------------
    def delete_model(self, model_id: int) -> bool:
        """Bir AI modelini ID'sine göre siler."""
        db_connection_instance: Optional[DatabaseConnection] = None
        try:
            db_connection_instance = DatabaseConnection()
            self.model_repo.db = db_connection_instance

            model_to_delete = self.model_repo.get_model_by_id(model_id)
            if not model_to_delete:
                raise ValueError(f"Silinecek AI modeli (ID: {model_id}) bulunamadı.")

            success, message = self.model_repo.delete_model(model_id)
            if not success:
                raise Exception(message or f"AI Modeli (ID: {model_id}) silinemedi.")
            return True
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli (ID: {model_id}) silinirken hata (AIModelService): {str(e)}", exc_info=True)
            raise Exception(f"AI Modeli (ID: {model_id}) silinirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_connection_instance:
                db_connection_instance.close()

    # -------------------------------------------------------------------------
    # 3.2.5. Sözlük verisiyle bir AI modelini günceller (update_model_via_dict)
    # -------------------------------------------------------------------------
    def update_model_via_dict(self, model_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mevcut bir AI modelini ID'sine göre günceller.
        """
        db_connection_instance_model: Optional[DatabaseConnection] = None
        db_connection_instance_category: Optional[DatabaseConnection] = None
        try:
            db_connection_instance_model = DatabaseConnection()
            self.model_repo.db = db_connection_instance_model


            model_to_update = self.model_repo.get_model_by_id(model_id) # API key olmadan çek
            if not model_to_update:
                raise ValueError(f"Güncellenecek AI modeli (ID: {model_id}) bulunamadı.")

            if 'category_id' in updates:
                new_category_id = updates['category_id']
                if not isinstance(new_category_id, int) or new_category_id <= 0:
                    raise ValueError("Geçersiz yeni kategori ID'si.")
                db_connection_instance_category = DatabaseConnection() # Kategori repo için ayrı bağlantı
                self.category_repo.db = db_connection_instance_category
                category = self.category_repo.get_category_by_id(new_category_id)
                if not category:
                    raise ValueError(f"Belirtilen yeni kategori (ID: {new_category_id}) bulunamadı.")
                if db_connection_instance_category: # Kategori bağlantısını kapat
                    db_connection_instance_category.close()
                    db_connection_instance_category = None # Tekrar kullanılmaması için None yap

            # ModelRepository.update_model tüm dict'i alır ve kendi içinde işler.
            success, message = self.model_repo.update_model(model_id, updates)
            if not success:
                if "değişiklik yapılmadı" not in message.lower() and "veriler aynı" not in message.lower():
                    raise Exception(message or f"AI Modeli (ID: {model_id}) güncellenemedi.")

            updated_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False)
            if not updated_model_entity:
                raise Exception(f"AI Modeli güncellendi ancak veritabanından çekilemedi (ID: {model_id}).")

            return simple_model_to_dict(updated_model_entity)
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli (ID: {model_id}) güncellenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise Exception(f"AI Modeli (ID: {model_id}) güncellenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_connection_instance_model:
                db_connection_instance_model.close()
            if db_connection_instance_category: # Eğer yukarıda açıldı ve kapatılmadıysa
                db_connection_instance_category.close()


# -----------------------------------------------------------------------------
# 3.3. UserService
# -----------------------------------------------------------------------------
class UserService:
    """Kullanıcı ile ilgili işlemleri yöneten servis sınıfı."""
    # -------------------------------------------------------------------------
    # 3.3.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self):
        # self.user_repo = UserRepository() # Gerçek UserRepository eklendiğinde
        pass

    # -------------------------------------------------------------------------
    # 3.3.2. Tüm kullanıcıları gösterim için hazırlar (get_all_users_for_display) (Örnek Veri)
    # -------------------------------------------------------------------------
    def get_all_users_for_display(self) -> List[Dict[str, Any]]:
        """
        Tüm kullanıcıları gösterim için hazırlar. (Şu an için örnek veri)
        """
        current_app.logger.info("UserService.get_all_users_for_display: Örnek kullanıcı verisi kullanılıyor.")
        return [
            {'id': 1, 'username': 'goktugkara', 'email': 'goktug@example.com', 'role': 'Admin', 'created_at': '2024-01-10T10:00:00Z', 'is_active': True},
            {'id': 2, 'username': 'aysee', 'email': 'ayse.yilmaz@example.com', 'role': 'Editor', 'created_at': '2024-02-15T11:30:00Z', 'is_active': True},
            {'id': 3, 'username': 'mehmet_c', 'email': 'mehmet@example.com', 'role': 'User', 'created_at': '2024-03-20T14:45:00Z', 'is_active': False}
        ]

# -----------------------------------------------------------------------------
# 3.4. DashboardService
# -----------------------------------------------------------------------------
class DashboardService:
    """Yönetici paneli (dashboard) için genel istatistikleri sağlayan servis."""
    # -------------------------------------------------------------------------
    # 3.4.1. Başlatıcı metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()
        self.user_service = UserService() # Gerçek UserRepository eklendiğinde değiştirilecek

    # -------------------------------------------------------------------------
    # 3.4.2. Dashboard için genel istatistikleri toplar (get_dashboard_stats)
    # -------------------------------------------------------------------------
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Dashboard için temel istatistikleri toplar.
        """
        db_conn_model: Optional[DatabaseConnection] = None
        db_conn_category: Optional[DatabaseConnection] = None
        try:
            db_conn_model = DatabaseConnection()
            self.model_repo.db = db_conn_model
            db_conn_category = DatabaseConnection()
            self.category_repo.db = db_conn_category

            total_users = len(self.user_service.get_all_users_for_display()) # Örnek veri
            total_models = self.model_repo.count_all_models()
            total_categories = self.category_repo.count_all_categories()
            active_tasks_placeholder = 15

            return {
                "total_users": total_users,
                "total_models": total_models,
                "total_categories": total_categories,
                "active_tasks": active_tasks_placeholder
            }
        except Exception as e:
            current_app.logger.error(f"Dashboard istatistikleri alınırken hata: {str(e)}", exc_info=True)
            return {
                "total_users": 0, "total_models": 0, "total_categories": 0,
                "active_tasks": 0, "error": "İstatistikler yüklenemedi."
            }
        finally:
            if db_conn_model:
                db_conn_model.close()
            if db_conn_category and db_conn_category != db_conn_model:
                db_conn_category.close()

# -----------------------------------------------------------------------------
# 3.5. SettingsService
# -----------------------------------------------------------------------------
class SettingsService:
    """Uygulama ayarlarını yöneten servis sınıfı."""
    # -------------------------------------------------------------------------
    # 3.5.1. Uygulama ayarlarını gösterim için hazırlar (get_settings_for_display) (Örnek Veri)
    # -------------------------------------------------------------------------
    def get_settings_for_display(self) -> Dict[str, Any]:
        """
        Uygulama ayarlarını gösterim için hazırlar. (Şu an için örnek veri)
        """
        current_app.logger.info("SettingsService.get_settings_for_display: Örnek ayar verisi kullanılıyor.")
        return {
            'site_name': 'Zekai Yönetim Paneli',
            'admin_email': 'admin@example.com',
            'maintenance_mode': False,
            'default_user_role': 'User',
            'items_per_page': 20
        }

    # -------------------------------------------------------------------------
    # 3.5.2. Uygulama ayarlarını kaydeder (save_settings) (Örnek İşlev)
    # -------------------------------------------------------------------------
    def save_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        Verilen ayarları kaydeder. (Şu an için örnek işlev)
        """
        try:
            current_app.logger.info(f"Ayarlar kaydediliyor (SettingsService - Demo): {settings_data}")
            # Gerçek kaydetme işlemleri burada yapılmalı
            return True
        except Exception as e:
            current_app.logger.error(f"Ayarlar kaydedilirken hata: {str(e)}", exc_info=True)
            raise Exception("Ayarlar kaydedilirken bir sunucu hatası oluştu.")

# =============================================================================
# 4.0 VERİTABANI OTURUMU YÖNETİMİ NOTLARI (DATABASE SESSION MANAGEMENT NOTES)
# =============================================================================
# Bu servislerde DatabaseConnection örnekleri oluşturulup kapatılmaktadır.
# Flask uygulamalarında veritabanı oturum yönetimi genellikle merkezi olarak
# `@app.teardown_appcontext` dekoratörü ile veya Flask-SQLAlchemy gibi
# eklentiler aracılığıyla request bazında yönetilir.
#
# Öneri:
# - Repository katmanının veritabanı oturumunu (session) almaktan ve temel
#   CRUD işlemlerini (add, delete, flush vb.) yönetmekten sorumlu olması.
# - Servis katmanının iş mantığını uygulaması, birden fazla repository
#   metodunu koordine etmesi.
# - Veritabanı bağlantısının oluşturulması ve kapatılmasının (remove) merkezi
#   olarak (örn: Flask app context'i ile veya her request için rota seviyesinde)
#   yönetilmesi. Bu durumda servisler ve repository'ler bağlantıyı parametre
#   olarak alabilir veya bir request context'inden erişebilir.
#
# Bu koddaki mevcut yaklaşım, her servis metodunda veya ilgili repository'ye
# erişimden önce yeni bir DatabaseConnection oluşturup işi bitince kapatmaktır.
# Bu, basit senaryolar için çalışabilir ancak daha karmaşık işlemlerde veya
# "unit of work" paterninin gerektiği durumlarda yetersiz kalabilir.
