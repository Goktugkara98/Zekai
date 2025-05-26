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
# 3.0 SERVİS SINIFLARI (SERVICE CLASSES)
#     3.1. CategoryService
#          3.1.6. get_category_by_id_for_display : Bir kategoriyi ID ile gösterim için hazırlar. (YENİ)
#     ... diğer metotlar ...
# =============================================================================

import json
import traceback
from typing import Dict, Any, List, Optional, Union

from flask import current_app

from app.models.base import DatabaseConnection # Varsayılan import
from app.models.entities.category import Category
from app.models.entities.model import Model as AIModelEntity
# from app.models.entities.user import User

from app.repositories.category_repository import CategoryRepository
from app.repositories.model_repository import ModelRepository
# from app.repositories.user_repository import UserRepository

# =============================================================================
# 2.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# =============================================================================
def simple_model_to_dict(instance: Optional[Any],
                         columns: Optional[List[str]] = None,
                         relationships: Optional[Dict[str, Union[List[str], Dict[str, Any]]]] = None) -> Optional[Dict[str, Any]]:
    if not instance:
        return None
    data: Dict[str, Any] = {}
    if columns:
        for col_name in columns:
            if hasattr(instance, col_name):
                data[col_name] = getattr(instance, col_name)
            else:
                data[col_name] = None # Sütun yoksa None ata
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
                    data[rel_name] = [simple_model_to_dict(item, columns=rel_cols, relationships=rel_rels) for item in related_instance if item is not None]
                else:
                    data[rel_name] = simple_model_to_dict(related_instance, columns=rel_cols, relationships=rel_rels)
            else:
                data[rel_name] = None
    return data

# =============================================================================
# 3.0 SERVİS SINIFLARI (SERVICE CLASSES)
# =============================================================================

class CategoryService:
    def __init__(self):
        self.category_repo = CategoryRepository()
        self.model_repo = ModelRepository() # Model sayısını almak için

    def get_all_categories_for_display(self) -> List[Dict[str, Any]]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.category_repo.db = db_conn
            self.model_repo.db = db_conn # Aynı bağlantıyı kullanabilir

            categories_raw: List[Category] = self.category_repo.get_all_categories()
            categories_data: List[Dict[str, Any]] = []
            for cat_entity in categories_raw:
                # Category entity'sinde 'status' alanı varsa ekleyin
                cat_dict = simple_model_to_dict(cat_entity, columns=['id', 'name', 'icon', 'status'])
                if cat_dict and cat_entity.id is not None:
                    # Her kategori için model sayısını al (performans için optimize edilebilir)
                    cat_dict['model_count'] = self.model_repo.count_models_by_category_id(cat_entity.id)
                    categories_data.append(cat_dict)
            return categories_data
        except Exception as e:
            current_app.logger.error(f"Kategoriler yüklenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise
        finally:
            if db_conn:
                db_conn.close()

    def add_category(self, name: str, description: Optional[str] = None, icon: Optional[str] = None, status: str = 'active') -> Dict[str, Any]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.category_repo.db = db_conn

            existing_category = self.category_repo.get_category_by_name(name)
            if existing_category:
                raise ValueError(f"'{name}' adında bir kategori zaten mevcut.")

            # CategoryRepository.create_category metodu icon ve status parametrelerini almalı
            success, message, category_id = self.category_repo.create_category(
                name=name,
                icon=icon or "", # None ise boş string
                # status=status # Eğer repository'de status varsa
            )
            if not success or category_id is None:
                raise ValueError(message or "Kategori oluşturulamadı.")

            new_category_entity = self.category_repo.get_category_by_id(category_id)
            if not new_category_entity:
                raise Exception(f"Kategori oluşturuldu (ID: {category_id}) ancak veritabanından çekilemedi.")
            
            # Entity'de 'status' alanı varsa ekleyin
            return simple_model_to_dict(new_category_entity, columns=['id', 'name', 'icon', 'status'])
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori eklenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise Exception("Kategori eklenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_conn:
                db_conn.close()

    def delete_category(self, category_id: int) -> bool:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.category_repo.db = db_conn
            self.model_repo.db = db_conn

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
            if db_conn:
                db_conn.close()

    def update_category(self, category_id: int, name: str, description: Optional[str] = None, icon: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.category_repo.db = db_conn

            category_to_update = self.category_repo.get_category_by_id(category_id)
            if not category_to_update:
                raise ValueError(f"Güncellenecek kategori (ID: {category_id}) bulunamadı.")

            if name != category_to_update.name: # Ad değişiyorsa kontrol et
                existing_category_with_new_name = self.category_repo.get_category_by_name(name)
                if existing_category_with_new_name and existing_category_with_new_name.id != category_id:
                    raise ValueError(f"'{name}' adında başka bir kategori zaten mevcut.")
            
            # CategoryRepository.update_category metodu icon ve status parametrelerini almalı
            update_data = {"name": name}
            if icon is not None:
                update_data["icon"] = icon
            # if status is not None: # Eğer status güncellenecekse
            #     update_data["status"] = status
            
            # Repository'deki update_category metodu bu dict'i alacak şekilde güncellenmeli
            # Şimdilik sadece name ve icon güncelleniyor varsayalım
            success, message = self.category_repo.update_category(
                category_id,
                name, # Eski metot imzasına göre
                icon or (category_to_update.icon if hasattr(category_to_update, 'icon') else "") # Mevcut ikonu koru veya boş string
                # status # Eğer status güncellenecekse
            )

            if not success:
                if "değişiklik yapılmadı" not in (message or "").lower() and "veriler aynı" not in (message or "").lower() :
                    raise Exception(message or f"Kategori (ID: {category_id}) güncellenemedi.")

            updated_category_entity = self.category_repo.get_category_by_id(category_id)
            if not updated_category_entity:
                raise Exception(f"Kategori güncellendi ancak veritabanından çekilemedi (ID: {category_id}).")
            
            # Entity'de 'status' alanı varsa ekleyin
            return simple_model_to_dict(updated_category_entity, columns=['id', 'name', 'icon', 'status'])
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori (ID: {category_id}) güncellenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise Exception(f"Kategori (ID: {category_id}) güncellenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_conn:
                db_conn.close()

    # YENİ EKLENEN METOT: Bir kategoriyi ID ile gösterim için hazırlar
    def get_category_by_id_for_display(self, category_id: int) -> Optional[Dict[str, Any]]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.category_repo.db = db_conn
            category_entity = self.category_repo.get_category_by_id(category_id)
            if not category_entity:
                return None
            # Category entity'sinde 'status' alanı varsa ekleyin
            # Ayrıca, Category entity'nizin 'icon' ve 'status' gibi alanlara sahip olduğundan emin olun.
            return simple_model_to_dict(category_entity, columns=['id', 'name', 'icon', 'status'])
        except Exception as e:
            current_app.logger.error(f"Kategori (ID: {category_id}) alınırken hata (CategoryService): {str(e)}", exc_info=True)
            # Hata durumunda None döndürmek yerine hatayı yükseltmek daha iyi olabilir,
            # böylece rota katmanı uygun bir HTTP hatası döndürebilir.
            raise
        finally:
            if db_conn:
                db_conn.close()

class AIModelService:
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()

    def get_all_models_for_display(self) -> List[Dict[str, Any]]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.model_repo.db = db_conn
            self.category_repo.db = db_conn

            models_raw: List[AIModelEntity] = self.model_repo.get_all_models(include_api_keys=False)
            models_data: List[Dict[str, Any]] = []

            # Kategori bilgilerini toplu çekmek daha verimli olabilir
            category_ids = list(set(model.category_id for model in models_raw if model.category_id))
            categories_map: Dict[int, Category] = {}
            if category_ids:
                # Varsayım: category_repo'da get_categories_by_ids gibi bir metot var
                # Yoksa, mevcut get_category_by_id ile tek tek çekilebilir.
                # fetched_categories = self.category_repo.get_categories_by_ids(category_ids)
                # for cat in fetched_categories:
                #     if cat and cat.id is not None: categories_map[cat.id] = cat
                # Şimdilik tek tek çekme:
                for cat_id_val in category_ids:
                    cat = self.category_repo.get_category_by_id(cat_id_val)
                    if cat and cat.id is not None:
                         categories_map[cat.id] = cat


            for model_entity in models_raw:
                model_dict = simple_model_to_dict(model_entity) # API key olmadan
                if model_dict:
                    category_id = model_entity.category_id
                    if category_id and category_id in categories_map:
                        model_dict['category_name'] = categories_map[category_id].name
                    elif category_id:
                         model_dict['category_name'] = f"ID: {category_id} (Bulunamadı)"
                    else:
                        model_dict['category_name'] = "N/A"
                    models_data.append(model_dict)
            return models_data
        except Exception as e:
            current_app.logger.error(f"AI Modelleri yüklenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise
        finally:
            if db_conn:
                db_conn.close()
    
    def get_model_by_id(self, model_id: int, include_api_key: bool = False) -> Optional[Dict[str, Any]]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.model_repo.db = db_conn
            model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=include_api_key)
            if not model_entity:
                return None
            return simple_model_to_dict(model_entity) # API key ile veya olmadan
        except Exception as e:
            current_app.logger.error(f"Model (ID: {model_id}) alınırken hata (AIModelService): {str(e)}", exc_info=True)
            raise
        finally:
            if db_conn:
                db_conn.close()

    def add_model_via_dict(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.model_repo.db = db_conn
            self.category_repo.db = db_conn # Kategori kontrolü için

            required_fields = ['name', 'category_id', 'service_provider', 'external_model_name']
            for field in required_fields:
                if not model_data.get(field) or (isinstance(model_data.get(field), str) and not str(model_data[field]).strip()):
                    raise ValueError(f"'{field}' alanı zorunludur ve boş olamaz.")
            if not isinstance(model_data['category_id'], int) or model_data['category_id'] <= 0:
                raise ValueError("Geçerli bir kategori ID'si girilmelidir.")

            category = self.category_repo.get_category_by_id(model_data['category_id'])
            if not category:
                raise ValueError(f"Belirtilen kategori (ID: {model_data['category_id']}) bulunamadı.")

            # ModelRepository.create_model tüm bu alanları kabul etmeli
            success, message, model_id = self.model_repo.create_model(
                category_id=model_data['category_id'],
                name=str(model_data['name']).strip(),
                icon=str(model_data.get('icon', '')).strip() or None,
                description=str(model_data.get('description', '')).strip() or None,
                details=model_data.get('details'),
                service_provider=str(model_data['service_provider']).strip(),
                external_model_name=str(model_data['external_model_name']).strip(),
                api_url=str(model_data.get('api_url', '')).strip() or None,
                request_method=str(model_data.get('request_method', 'POST')).upper().strip(),
                request_headers=model_data.get('request_headers'),
                request_body=model_data.get('request_body'),
                response_path=str(model_data.get('response_path', '')).strip() or None,
                api_key=model_data.get('api_key'), # API key burada gönderiliyor
                prompt_template=str(model_data.get('prompt_template', '')).strip() or None,
                status=str(model_data.get('status', 'active')).lower().strip()
            )

            if not success or model_id is None:
                raise ValueError(message or "AI Modeli oluşturulamadı.")

            new_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False) # Dönerken API key'i hariç tut
            if not new_model_entity:
                raise Exception(f"AI Modeli oluşturuldu (ID: {model_id}) ancak veritabanından çekilemedi.")

            return simple_model_to_dict(new_model_entity)
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli eklenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise Exception("AI Modeli eklenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_conn:
                db_conn.close()

    def delete_model(self, model_id: int) -> bool:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.model_repo.db = db_conn

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
            if db_conn:
                db_conn.close()

    def update_model_via_dict(self, model_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.model_repo.db = db_conn
            self.category_repo.db = db_conn # Kategori kontrolü için

            model_to_update = self.model_repo.get_model_by_id(model_id)
            if not model_to_update:
                raise ValueError(f"Güncellenecek AI modeli (ID: {model_id}) bulunamadı.")

            if 'category_id' in updates:
                new_category_id = updates['category_id']
                if not isinstance(new_category_id, int) or new_category_id <= 0:
                    raise ValueError("Geçersiz yeni kategori ID'si.")
                category = self.category_repo.get_category_by_id(new_category_id)
                if not category:
                    raise ValueError(f"Belirtilen yeni kategori (ID: {new_category_id}) bulunamadı.")
            
            # API key güncellemesi geliyorsa, onu ayrı handle et veya repository'ye bırak
            # Genellikle API key'ler bu şekilde güncellenmez, ayrı bir mekanizma olur.
            # Şimdilik updates dict'i olduğu gibi repository'ye gönderiyoruz.
            success, message = self.model_repo.update_model(model_id, updates)
            if not success:
                if "değişiklik yapılmadı" not in (message or "").lower() and "veriler aynı" not in (message or "").lower():
                    raise Exception(message or f"AI Modeli (ID: {model_id}) güncellenemedi.")

            updated_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False) # Dönerken API key'i hariç tut
            if not updated_model_entity:
                raise Exception(f"AI Modeli güncellendi ancak veritabanından çekilemedi (ID: {model_id}).")

            return simple_model_to_dict(updated_model_entity)
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli (ID: {model_id}) güncellenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise Exception(f"AI Modeli (ID: {model_id}) güncellenirken beklenmedik bir sunucu hatası oluştu.")
        finally:
            if db_conn:
                db_conn.close()

class UserService:
    def __init__(self):
        # self.user_repo = UserRepository() # Gerçek UserRepository eklendiğinde
        pass

    def get_all_users_for_display(self) -> List[Dict[str, Any]]:
        current_app.logger.info("UserService.get_all_users_for_display: Örnek kullanıcı verisi kullanılıyor.")
        return [
            {'id': 1, 'username': 'goktugkara', 'email': 'goktug@example.com', 'role': 'Admin', 'created_at': '2024-01-10T10:00:00Z', 'is_active': True},
            {'id': 2, 'username': 'aysee', 'email': 'ayse.yilmaz@example.com', 'role': 'Editor', 'created_at': '2024-02-15T11:30:00Z', 'is_active': True},
            {'id': 3, 'username': 'mehmet_c', 'email': 'mehmet@example.com', 'role': 'User', 'created_at': '2024-03-20T14:45:00Z', 'is_active': False}
        ]

class DashboardService:
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()
        self.user_service = UserService()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        db_conn: Optional[DatabaseConnection] = None
        try:
            db_conn = DatabaseConnection()
            self.model_repo.db = db_conn
            self.category_repo.db = db_conn

            total_users = len(self.user_service.get_all_users_for_display())
            total_models = self.model_repo.count_all_models()
            total_categories = self.category_repo.count_all_categories()
            active_tasks_placeholder = 15 # Örnek veri

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
            if db_conn:
                db_conn.close()

class SettingsService:
    def get_settings_for_display(self) -> Dict[str, Any]:
        current_app.logger.info("SettingsService.get_settings_for_display: Örnek ayar verisi kullanılıyor.")
        return {
            'site_name': 'Zekai Yönetim Paneli',
            'admin_email': 'admin@example.com',
            'maintenance_mode': False,
            'default_user_role': 'User',
            'items_per_page': 20
        }

    def save_settings(self, settings_data: Dict[str, Any]) -> bool:
        try:
            current_app.logger.info(f"Ayarlar kaydediliyor (SettingsService - Demo): {settings_data}")
            # Gerçek kaydetme işlemleri burada yapılmalı
            return True
        except Exception as e:
            current_app.logger.error(f"Ayarlar kaydedilirken hata: {str(e)}", exc_info=True)
            raise Exception("Ayarlar kaydedilirken bir sunucu hatası oluştu.")

