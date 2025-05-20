# app/services/admin_panel_services.py

from app.models.base import DatabaseConnection
from app.models.entities.category import Category
from app.models.entities.model import Model as AIModel
# from app.models.entities.user import User # Kullanıcı modeli eklendiğinde
from app.repositories.category_repository import CategoryRepository
from app.repositories.model_repository import ModelRepository
# from app.repositories.user_repository import UserRepository # Kullanıcı repository eklendiğinde

# --- Yardımcı Fonksiyon ---
def simple_model_to_dict(instance, columns=None, relationships=None):
    """
    Model nesnesini basit bir sözlüğe dönüştürür.
    columns: Özel olarak alınacak sütunların listesi.
    relationships: {'iliski_adi': ['iliski_kolonu1', 'iliski_kolonu2']} formatında ilişkiler.
    """
    if not instance:
        return None
    
    data = {}
    
    # Eğer model nesnesinin to_dict metodu varsa, onu kullan
    if hasattr(instance, 'to_dict') and callable(getattr(instance, 'to_dict')):
        data = instance.to_dict()
    else:
        # Aksi takdirde, __dict__ kullanarak tüm öznitelikleri al
        # Özel ve gizli öznitelikleri (örn. _xyz veya __xyz) hariç tut
        data = {k: v for k, v in instance.__dict__.items() 
                if not k.startswith('_')}
    
    # Eğer belirli sütunlar istendiyse, sadece onları al
    if columns:
        data = {k: getattr(instance, k, None) for k in columns if hasattr(instance, k)}

    if relationships:
        for rel_name, rel_attr_config in relationships.items():
            related_instance = getattr(instance, rel_name, None)
            if related_instance:
                # rel_attr_config can be a list of attributes or a sub-dictionary for deeper serialization
                rel_cols = rel_attr_config if isinstance(rel_attr_config, list) else None
                rel_rels = rel_attr_config if isinstance(rel_attr_config, dict) else None

                if isinstance(related_instance, list): # one-to-many or many-to-many
                    data[rel_name] = [simple_model_to_dict(item, columns=rel_cols, relationships=rel_rels) for item in related_instance]
                else: # one-to-one or many-to-one
                    data[rel_name] = simple_model_to_dict(related_instance, columns=rel_cols, relationships=rel_rels)
            else:
                data[rel_name] = None
    return data

# --- Servis Sınıfları ---

class CategoryService:
    def __init__(self):
        self.category_repo = CategoryRepository()
        self.model_repo = ModelRepository()

    def get_all_categories_for_display(self):
        """Kategorileri, model sayılarıyla birlikte gösterim için hazırlar."""
        categories_raw = self.category_repo.get_all_categories()
        categories_data = []
        for cat in categories_raw:
            cat_dict = simple_model_to_dict(cat, ['id', 'name', 'description'])
            # 'models' ilişkisi Category entity'sinde tanımlıysa doğrudan kullanılabilir.
            cat_dict['model_count'] = len(cat.models) if hasattr(cat, 'models') and cat.models else 0
            # Alternatif olarak: self.model_repo.count_by_category_id(cat.id)
            categories_data.append(cat_dict)
        return categories_data

    def add_category(self, name, description=None):
        """Yeni bir kategori ekler."""
        # Aynı isimde kategori var mı kontrolü (isteğe bağlı)
        # existing_category = self.category_repo.get_by_name(name)
        # if existing_category:
        #     raise ValueError(f"'{name}' adında bir kategori zaten mevcut.")
        try:
            new_category = self.category_repo.add(name=name, description=description)
            db_session.commit()
            return simple_model_to_dict(new_category, ['id', 'name', 'description'])
        except Exception as e:
            db_session.rollback()
            raise e # Hatanın yukarıya fırlatılması daha iyi olabilir veya burada loglanabilir.
        finally:
            db_session.remove() # Her işlem sonrası session kapatılmalı (route'larda @teardown_appcontext ile yönetiliyorsa burada gerekmeyebilir)

    def delete_category(self, category_id):
        """Bir kategoriyi siler. Kategoriye bağlı model varsa silmeyi engeller."""
        category_to_delete = self.category_repo.get_by_id(category_id)
        if not category_to_delete:
            raise ValueError("Kategori bulunamadı.") # Veya özel bir exception
        
        if self.model_repo.count_by_category_id(category_id) > 0:
            raise ValueError("Bu kategoriye bağlı AI modelleri bulunmaktadır. Önce modelleri silin veya başka bir kategoriye taşıyın.")
        
        try:
            self.category_repo.delete(category_id)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.remove()
            
    def update_category(self, category_id, name, description=None):
        """Var olan bir kategoriyi günceller."""
        category_to_update = self.category_repo.get_by_id(category_id)
        if not category_to_update:
            raise ValueError("Güncellenecek kategori bulunamadı.")
        
        # İsim değişikliği varsa ve yeni isim başka bir kategoriye aitse kontrol eklenebilir.
        
        try:
            updated_category = self.category_repo.update(category_id, name=name, description=description)
            db_session.commit()
            return simple_model_to_dict(updated_category, ['id', 'name', 'description'])
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.remove()


class AIModelService:
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository() # Kategori varlığını kontrol etmek için

    def get_all_models_for_display(self):
        """Tüm AI modellerini, kategori bilgileriyle birlikte gösterim için hazırlar."""
        models_raw = self.model_repo.get_all_models()
        models_data = []
        
        # Kategori ID'lerini topla
        category_ids = set()
        for model_entity in models_raw:
            if hasattr(model_entity, 'category_id') and model_entity.category_id:
                category_ids.add(model_entity.category_id)
        
        # Kategorileri önceden yükle
        categories = {}
        for cat_id in category_ids:
            category = self.category_repo.get_category_by_id(cat_id)
            if category:
                categories[cat_id] = category
        
        # Model verilerini oluştur
        for model_entity in models_raw:
            # Model nesnesinden sözlük oluştur
            model_dict = simple_model_to_dict(model_entity)
            
            # Kategori adını ekle
            category_id = getattr(model_entity, 'category_id', None)
            if category_id and category_id in categories:
                model_dict['category_name'] = categories[category_id].name
            else:
                model_dict['category_name'] = "N/A"
                
            models_data.append(model_dict)
        return models_data

    def add_model(self, name, category_id, description=None, api_url=None, status='active'):
        """Yeni bir AI modeli ekler."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError("Belirtilen kategori bulunamadı.")
        
        try:
            new_model = self.model_repo.add(
                name=name, 
                category_id=category_id, 
                description=description, 
                api_url=api_url, 
                status=status
            )
            db_session.commit()
            return simple_model_to_dict(new_model) # Tüm alanları dönebilir
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.remove()

    def delete_model(self, model_id):
        """Bir AI modelini siler."""
        model_to_delete = self.model_repo.get_by_id(model_id)
        if not model_to_delete:
            raise ValueError("Model bulunamadı.")
        
        try:
            self.model_repo.delete(model_id)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.remove()
            
    def update_model(self, model_id, data):
        """Var olan bir AI modelini günceller. `data` bir sözlük olmalıdır."""
        model_to_update = self.model_repo.get_by_id(model_id)
        if not model_to_update:
            raise ValueError("Güncellenecek model bulunamadı.")

        if 'category_id' in data:
            category = self.category_repo.get_by_id(data['category_id'])
            if not category:
                raise ValueError("Belirtilen yeni kategori bulunamadı.")
        
        try:
            # Repository'deki update metodu kwargs kabul etmeli
            updated_model = self.model_repo.update(model_id, **data)
            db_session.commit()
            return simple_model_to_dict(updated_model)
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.remove()


class UserService: # Gerçek User modeli ve repository eklendiğinde geliştirilecek
    def __init__(self):
        # self.user_repo = UserRepository()
        pass

    def get_all_users_for_display(self):
        """Kullanıcıları gösterim için hazırlar (şimdilik örnek veri)."""
        # users_raw = self.user_repo.get_all()
        # users_data = [simple_model_to_dict(user, ['id', 'username', 'email', 'role', 'created_at']) for user in users_raw]
        # return users_data
        return [
            {'id': 1, 'username': 'goktugkara', 'email': 'goktug@example.com', 'role': 'Admin', 'created_at': '2024-01-10'},
            {'id': 2, 'username': 'aysee', 'email': 'ayse.yilmaz@example.com', 'role': 'Editor', 'created_at': '2024-02-15'},
            {'id': 3, 'username': 'mehmet_c', 'email': 'mehmet@example.com', 'role': 'User', 'created_at': '2024-03-20'}
        ]
    
    # add_user, delete_user, update_user metodları eklenecek


class DashboardService:
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()
        # self.user_repo = UserRepository() # Eklendiğinde

    def get_dashboard_stats(self):
        """Dashboard için istatistikleri toplar."""
        # Gerçek sayımlar veritabanından yapılmalı
        total_users = 0 # self.user_repo.count_all()
        # Örnek kullanıcı sayısı (UserService'ten alınabilir veya burada direkt repo kullanılabilir)
        temp_user_service = UserService()
        total_users = len(temp_user_service.get_all_users_for_display())


        return {
            "total_users": total_users,
            "total_models": self.model_repo.count_all_models(),
            "total_categories": self.category_repo.count_all_categories(),
            "active_tasks": 15 # Örnek statik veri, dinamikleştirilebilir
        }

class SettingsService:
    def get_settings_for_display(self):
        # Ayarlar veritabanından veya bir config dosyasından çekilebilir
        # Şimdilik statik
        return {
            'site_name': 'Zekai Admin',
            'admin_email': 'admin@example.com',
            'maintenance_mode': False
        }
    
    def save_settings(self, settings_data):
        # Ayarları kaydetme mantığı (veritabanı veya dosyaya)
        # Örnek:
        # for key, value in settings_data.items():
        #     # Config_Model.update_setting(key, value)
        # db_session.commit()
        print(f"Ayarlar kaydediliyor (demo): {settings_data}")
        return True

