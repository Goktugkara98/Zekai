# =============================================================================
# Admin Dashboard Servisleri Modülü (Admin Dashboard Services Module)
# =============================================================================
# Bu modül, yönetici paneli için backend iş mantığını ve servislerini içerir.
# Veritabanı işlemleri, veri dönüşümleri ve rota katmanına veri sağlama
# gibi görevleri yerine getiren servis sınıflarını barındırır.
#
# Yapı:
# 1. İçe Aktarmalar (Imports)
# 2. Yardımcı Fonksiyonlar (Helper Functions)
#    2.1. simple_model_to_dict
# 3. Servis Sınıfları (Service Classes)
#    3.1. CategoryService
#    3.2. AIModelService
#    3.3. UserService
#    3.4. DashboardService
#    3.5. SettingsService
# 4. Veritabanı Oturumu Yönetimi Notları
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import json # JSON işlemleri için
import traceback # Hata ayıklama için
from typing import Dict, Any, List, Optional, Union # Tip ipuçları için

from flask import current_app # Loglama ve uygulama context'i için

# Veritabanı bağlantısı ve model/entity sınıfları
# Not: DatabaseConnection doğrudan burada kullanılmıyor gibi,
# repository'ler kendi bağlantılarını yönetiyor olabilir.
# from app.models.base import DatabaseConnection

# SQLAlchemy session yönetimi için (eğer kullanılıyorsa)
# Bu import, uygulamanın session'ı nasıl yönettiğine bağlıdır.
# Örnek: from app.extensions import db_session
# Veya her repository kendi session'ını yönetiyorsa bu gerekmeyebilir.
# Şimdilik, orijinal koddaki gibi global bir db_session varsayımıyla
# ilgili yorumlar korunacak, ancak bu uygulamanın genel yapısına göre
# düzenlenmelidir.
from app.models.base import DatabaseConnection # Orijinal koddaki varsayılan import

# Entity (Varlık) Sınıfları
from app.models.entities.category import Category
from app.models.entities.model import Model as AIModelEntity # AIModel ismiyle çakışmaması için
# from app.models.entities.user import User # Kullanıcı modeli eklendiğinde aktifleşecek

# Repository (Depo) Sınıfları
from app.repositories.category_repository import CategoryRepository
from app.repositories.model_repository import ModelRepository
# from app.repositories.user_repository import UserRepository # Kullanıcı deposu eklendiğinde aktifleşecek

# 2. Yardımcı Fonksiyonlar (Helper Functions)
# =============================================================================

# 2.1. simple_model_to_dict
# -----------------------------------------------------------------------------
def simple_model_to_dict(instance: Optional[Any],
                         columns: Optional[List[str]] = None,
                         relationships: Optional[Dict[str, Union[List[str], Dict[str, Any]]]] = None) -> Optional[Dict[str, Any]]:
    """
    Bir SQLAlchemy model nesnesini veya benzeri bir nesneyi basit bir sözlüğe dönüştürür.

    Args:
        instance: Dönüştürülecek model nesnesi.
        columns: Sözlüğe dahil edilecek özel sütunların (alanların) listesi.
                 None ise, modelin `to_dict` metodu varsa o kullanılır, yoksa __dict__ kullanılır.
        relationships: İlişkili nesnelerin nasıl serileştirileceğini tanımlar.
                       Format: {'iliski_adi': ['iliski_kolonu1', 'iliski_kolonu2']} veya
                               {'iliski_adi': {'columns': [...], 'relationships': {...}}}
                       Bu, iç içe serileştirmeye olanak tanır.

    Returns:
        Modelin sözlük temsili veya instance None ise None.
    """
    if not instance:
        return None

    data: Dict[str, Any] = {}

    if columns:
        # Sadece belirtilen sütunları al
        for col_name in columns:
            if hasattr(instance, col_name):
                data[col_name] = getattr(instance, col_name)
            else:
                data[col_name] = None # Sütun yoksa None ata
    elif hasattr(instance, 'to_dict') and callable(getattr(instance, 'to_dict')):
        # Modelin kendi to_dict metodu varsa onu kullan
        try:
            data = instance.to_dict()
        except Exception as e:
            current_app.logger.error(f"simple_model_to_dict: {instance.__class__.__name__}.to_dict() hatası: {e}")
            # Fallback to __dict__ if to_dict fails or not comprehensive
            data = {k: v for k, v in instance.__dict__.items() if not k.startswith('_')}
    else:
        # __dict__ kullanarak tüm öznitelikleri al (özel ve gizli olanlar hariç)
        data = {k: v for k, v in instance.__dict__.items() if not k.startswith('_')}

    # İlişkili nesneleri serileştir
    if relationships:
        for rel_name, rel_config in relationships.items():
            related_instance = getattr(instance, rel_name, None)
            if related_instance:
                rel_cols: Optional[List[str]] = None
                rel_rels: Optional[Dict[str, Any]] = None

                if isinstance(rel_config, list): # Sadece sütun listesi verilmişse
                    rel_cols = rel_config
                elif isinstance(rel_config, dict): # Daha detaylı konfigürasyon (iç içe)
                    rel_cols = rel_config.get('columns')
                    rel_rels = rel_config.get('relationships')

                if isinstance(related_instance, list):  # One-to-many veya many-to-many
                    data[rel_name] = [
                        simple_model_to_dict(item, columns=rel_cols, relationships=rel_rels)
                        for item in related_instance
                    ]
                else:  # One-to-one veya many-to-one
                    data[rel_name] = simple_model_to_dict(related_instance, columns=rel_cols, relationships=rel_rels)
            else:
                data[rel_name] = None # İlişki yoksa veya boşsa None ata
    return data

# 3. Servis Sınıfları (Service Classes)
# =============================================================================

# 3.1. CategoryService
# -----------------------------------------------------------------------------
class CategoryService:
    """Kategori ile ilgili işlemleri yöneten servis sınıfı."""
    def __init__(self):
        # Servis başlatıldığında ilgili repository'lerin örnekleri oluşturulur.
        # Bu, repository'lerin stateless olduğu varsayımına dayanır.
        self.category_repo = CategoryRepository()
        self.model_repo = ModelRepository() # Kategoriye bağlı model sayısını almak için

    def get_all_categories_for_display(self) -> List[Dict[str, Any]]:
        """
        Tüm kategorileri, her bir kategoriye ait model sayısı ile birlikte
        gösterim için hazırlar.

        Returns:
            Kategori bilgilerini ve model sayılarını içeren sözlük listesi.
        """
        try:
            categories_raw: List[Category] = self.category_repo.get_all_categories()
            categories_data: List[Dict[str, Any]] = []
            for cat_entity in categories_raw:
                cat_dict = simple_model_to_dict(cat_entity, columns=['id', 'name', 'description', 'icon'])
                if cat_dict: # simple_model_to_dict None döndürmediyse
                    # Kategoriye bağlı model sayısını al
                    # Category entity'sinde 'models' ilişkisi (backref) tanımlıysa:
                    if hasattr(cat_entity, 'models') and cat_entity.models is not None:
                         cat_dict['model_count'] = len(cat_entity.models)
                    else:
                        # Alternatif olarak, model repository üzerinden sayım yapılabilir:
                        cat_dict['model_count'] = self.model_repo.count_models_by_category_id(cat_entity.id)
                    categories_data.append(cat_dict)
            return categories_data
        except Exception as e:
            current_app.logger.error(f"Kategoriler yüklenirken hata (CategoryService): {str(e)}", exc_info=True)
            raise # Hatanın üst katmana (örn: route) iletilmesi

    def add_category(self, name: str, description: Optional[str] = None, icon: Optional[str] = None) -> Dict[str, Any]:
        """
        Yeni bir kategori ekler.

        Args:
            name: Kategori adı.
            description: Kategori açıklaması (opsiyonel).
            icon: Kategori ikonu (opsiyonel).

        Returns:
            Eklenen kategorinin sözlük temsili.

        Raises:
            ValueError: Kategori adı zaten mevcutsa veya geçersiz veri sağlanırsa.
            Exception: Veritabanı işlemi sırasında bir hata oluşursa.
        """
        try:
            # İsim benzersizliği kontrolü (repository katmanında da olabilir)
            existing_category = self.category_repo.get_category_by_name(name)
            if existing_category:
                raise ValueError(f"'{name}' adında bir kategori zaten mevcut.")

            # CategoryRepository.add metodu bir Category entity nesnesi döndürmeli
            success, message, category_id = self.category_repo.create_category(name=name, description=description, icon=icon)
            if not success or category_id is None:
                raise ValueError(message or "Kategori oluşturulamadı.")

            # Yeni eklenen kategoriyi ID ile çek
            new_category_entity = self.category_repo.get_category_by_id(category_id)
            if not new_category_entity:
                raise Exception(f"Kategori oluşturuldu (ID: {category_id}) ancak veritabanından çekilemedi.")

            return simple_model_to_dict(new_category_entity, columns=['id', 'name', 'description', 'icon'])
        except ValueError: # Yakalanan ValueError'ı doğrudan fırlat
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori eklenirken hata (CategoryService): {str(e)}", exc_info=True)
            # db_session.rollback() # Repository katmanında yapılmalı
            raise Exception(f"Kategori eklenirken beklenmedik bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove() # Merkezi oturum yönetimi varsa burada gereksiz

    def delete_category(self, category_id: int) -> bool:
        """
        Bir kategoriyi ID'sine göre siler.
        Kategoriye bağlı AI modelleri varsa silme işlemi engellenir.

        Args:
            category_id: Silinecek kategorinin ID'si.

        Returns:
            Silme işlemi başarılıysa True.

        Raises:
            ValueError: Kategori bulunamazsa veya bağlı modeller varsa.
            Exception: Veritabanı işlemi sırasında bir hata oluşursa.
        """
        try:
            category_to_delete = self.category_repo.get_category_by_id(category_id)
            if not category_to_delete:
                raise ValueError(f"ID'si {category_id} olan kategori bulunamadı.")

            # Kategoriye bağlı model olup olmadığını kontrol et
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
            # db_session.rollback()
            raise Exception(f"Kategori (ID: {category_id}) silinirken beklenmedik bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove()

    def update_category(self, category_id: int, name: str, description: Optional[str] = None, icon: Optional[str] = None) -> Dict[str, Any]:
        """
        Mevcut bir kategoriyi ID'sine göre günceller.

        Args:
            category_id: Güncellenecek kategorinin ID'si.
            name: Yeni kategori adı.
            description: Yeni kategori açıklaması (opsiyonel).
            icon: Yeni kategori ikonu (opsiyonel).

        Returns:
            Güncellenmiş kategorinin sözlük temsili.

        Raises:
            ValueError: Kategori bulunamazsa, isim zaten başkası tarafından kullanılıyorsa.
            Exception: Veritabanı işlemi sırasında bir hata oluşursa.
        """
        try:
            category_to_update = self.category_repo.get_category_by_id(category_id)
            if not category_to_update:
                raise ValueError(f"Güncellenecek kategori (ID: {category_id}) bulunamadı.")

            # İsim değişikliği varsa ve yeni isim başka bir kategoriye aitse kontrol et
            if name != category_to_update.name:
                existing_category_with_new_name = self.category_repo.get_category_by_name(name)
                if existing_category_with_new_name and existing_category_with_new_name.id != category_id:
                    raise ValueError(f"'{name}' adında başka bir kategori zaten mevcut.")

            updates = {"name": name}
            if description is not None:
                updates["description"] = description
            if icon is not None:
                updates["icon"] = icon
            
            success, message = self.category_repo.update_category(category_id, updates)

            if not success:
                raise Exception(message or f"Kategori (ID: {category_id}) güncellenemedi.")

            updated_category_entity = self.category_repo.get_category_by_id(category_id)
            if not updated_category_entity:
                raise Exception(f"Kategori güncellendi ancak veritabanından çekilemedi (ID: {category_id}).")

            return simple_model_to_dict(updated_category_entity, columns=['id', 'name', 'description', 'icon'])
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Kategori (ID: {category_id}) güncellenirken hata (CategoryService): {str(e)}", exc_info=True)
            # db_session.rollback()
            raise Exception(f"Kategori (ID: {category_id}) güncellenirken beklenmedik bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove()

# 3.2. AIModelService
# -----------------------------------------------------------------------------
class AIModelService:
    """AI Modelleri ile ilgili işlemleri yöneten servis sınıfı."""
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository() # Kategori varlığını kontrol etmek için

    def get_all_models_for_display(self) -> List[Dict[str, Any]]:
        """
        Tüm AI modellerini, bağlı oldukları kategori adı ile birlikte
        gösterim için hazırlar.

        Returns:
            AI Modeli bilgilerini ve kategori adlarını içeren sözlük listesi.
        """
        try:
            models_raw: List[AIModelEntity] = self.model_repo.get_all_models(include_api_keys=False) # API key'leri gösterme
            models_data: List[Dict[str, Any]] = []

            # Kategori bilgilerini toplu çekmek için ID listesi oluştur
            category_ids = list(set(model.category_id for model in models_raw if model.category_id))
            categories_map: Dict[int, Category] = {}
            if category_ids:
                # Bu metodun CategoryRepository'de olması gerekir
                # categories_list = self.category_repo.get_categories_by_ids(category_ids)
                # for cat in categories_list:
                #    categories_map[cat.id] = cat
                # Şimdilik tek tek çekiyoruz, optimize edilebilir.
                for cat_id in category_ids:
                    cat = self.category_repo.get_category_by_id(cat_id)
                    if cat:
                        categories_map[cat.id] = cat


            for model_entity in models_raw:
                # Model entity'sini sözlüğe dönüştür
                # API anahtarını gizlemek için `get_model_by_id` kullanılabilir veya
                # `simple_model_to_dict` içinde bu mantık eklenebilir.
                # Şimdilik `get_all_models` zaten gizliyor.
                model_dict = simple_model_to_dict(model_entity) # Tüm alanları alır
                if model_dict:
                    # Kategori adını ekle
                    category_id = model_entity.category_id
                    if category_id and category_id in categories_map:
                        model_dict['category_name'] = categories_map[category_id].name
                    else:
                        model_dict['category_name'] = "N/A (Kategori Bulunamadı)"
                    models_data.append(model_dict)
            return models_data
        except Exception as e:
            current_app.logger.error(f"AI Modelleri yüklenirken hata (AIModelService): {str(e)}", exc_info=True)
            raise

    def add_model(self,
                  name: str,
                  category_id: int,
                  api_url: str,
                  description: Optional[str] = None,
                  api_method: str = 'POST',
                  api_key: Optional[str] = None,
                  request_headers: Optional[Union[str, Dict[str, Any]]] = None,
                  request_body: Optional[Union[str, Dict[str, Any]]] = None,
                  response_path: Optional[str] = None,
                  status: str = 'active',
                  icon: Optional[str] = None) -> Dict[str, Any]:
        """
        Yeni bir AI modeli ekler.

        Args:
            name: Model adı.
            category_id: Bağlı olduğu kategori ID'si.
            api_url: Modelin API endpoint URL'i.
            description: Model açıklaması (opsiyonel).
            api_method: API isteği için HTTP metodu (varsayılan: 'POST').
            api_key: API anahtarı (opsiyonel).
            request_headers: API isteği için başlıklar (JSON string veya dict).
            request_body: API isteği için gövde (JSON string veya dict).
            response_path: API yanıtından veri çıkarmak için JSON Path ifadesi (opsiyonel).
            status: Modelin durumu ('active', 'inactive' vb. - varsayılan: 'active').
            icon: Model için ikon (opsiyonel).

        Returns:
            Eklenen AI modelinin sözlük temsili.

        Raises:
            ValueError: Kategori bulunamazsa, geçersiz JSON formatı veya diğer validasyon hataları.
            Exception: Veritabanı işlemi sırasında bir hata oluşursa.
        """
        try:
            # Kategori varlığını kontrol et
            category = self.category_repo.get_category_by_id(category_id)
            if not category:
                raise ValueError(f"Belirtilen kategori (ID: {category_id}) bulunamadı.")

            # JSON stringlerini Python dict'lerine dönüştür
            parsed_headers: Optional[Dict[str, Any]] = None
            if isinstance(request_headers, str) and request_headers.strip():
                try:
                    parsed_headers = json.loads(request_headers)
                except json.JSONDecodeError:
                    raise ValueError("Geçersiz istek başlığı (request_headers) formatı. JSON formatında olmalıdır.")
            elif isinstance(request_headers, dict):
                parsed_headers = request_headers

            parsed_body: Optional[Dict[str, Any]] = None
            if isinstance(request_body, str) and request_body.strip():
                try:
                    parsed_body = json.loads(request_body)
                except json.JSONDecodeError:
                    raise ValueError("Geçersiz istek gövdesi (request_body) formatı. JSON formatında olmalıdır.")
            elif isinstance(request_body, dict):
                parsed_body = request_body

            # ModelRepository.create_model bir tuple döndürür: (success, message, model_id)
            success, message, model_id = self.model_repo.create_model(
                name=name,
                category_id=category_id,
                icon=icon,
                description=description,
                details=None, # `details` alanı için ayrı bir parametre eklenebilir veya request_body'den türetilebilir
                api_url=api_url,
                request_method=api_method.upper(),
                request_headers=parsed_headers,
                request_body=parsed_body,
                response_path=response_path,
                api_key=api_key
                # `status` alanı ModelRepository.create_model'a eklenmeli
            )

            if not success or model_id is None:
                raise ValueError(message or "AI Modeli oluşturulamadı.")

            # Başarılı ise, yeni eklenen modeli ID ile çek (API anahtarı olmadan)
            new_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False)
            if not new_model_entity:
                raise Exception(f"AI Modeli oluşturuldu (ID: {model_id}) ancak veritabanından çekilemedi.")

            # Status güncellemesi (eğer create_model desteklemiyorsa)
            if hasattr(new_model_entity, 'status') and new_model_entity.status != status:
                 self.model_repo.update_model(model_id, {"status": status}) # update_model tuple döndürüyor
                 # Güncellenmiş modeli tekrar çek
                 new_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False)


            return simple_model_to_dict(new_model_entity)
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli eklenirken hata (AIModelService): {str(e)}", exc_info=True)
            # db_session.rollback()
            raise Exception(f"AI Modeli eklenirken beklenmedik bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove()

    def delete_model(self, model_id: int) -> bool:
        """
        Bir AI modelini ID'sine göre siler.

        Args:
            model_id: Silinecek AI modelinin ID'si.

        Returns:
            Silme işlemi başarılıysa True.

        Raises:
            ValueError: Model bulunamazsa.
            Exception: Veritabanı işlemi sırasında bir hata oluşursa.
        """
        try:
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
            # db_session.rollback()
            raise Exception(f"AI Modeli (ID: {model_id}) silinirken beklenmedik bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove()

    def update_model(self, model_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mevcut bir AI modelini ID'sine göre günceller.

        Args:
            model_id: Güncellenecek AI modelinin ID'si.
            updates: Güncellenecek alanları içeren bir sözlük.
                     Örn: {"name": "Yeni Ad", "description": "Yeni Açıklama"}

        Returns:
            Güncellenmiş AI modelinin sözlük temsili (API anahtarı olmadan).

        Raises:
            ValueError: Model bulunamazsa, kategori bulunamazsa (eğer güncelleniyorsa),
                        geçersiz JSON formatı veya diğer validasyon hataları.
            Exception: Veritabanı işlemi sırasında bir hata oluşursa.
        """
        try:
            model_to_update = self.model_repo.get_model_by_id(model_id)
            if not model_to_update:
                raise ValueError(f"Güncellenecek AI modeli (ID: {model_id}) bulunamadı.")

            # Kategori ID'si güncelleniyorsa, yeni kategorinin varlığını kontrol et
            if 'category_id' in updates:
                new_category_id = updates['category_id']
                if not isinstance(new_category_id, int) or new_category_id <= 0:
                    raise ValueError("Geçersiz yeni kategori ID'si.")
                category = self.category_repo.get_category_by_id(new_category_id)
                if not category:
                    raise ValueError(f"Belirtilen yeni kategori (ID: {new_category_id}) bulunamadı.")

            # JSON stringlerini Python dict'lerine dönüştür (eğer string olarak gelirse)
            for field in ['request_headers', 'request_body', 'details']:
                if field in updates and isinstance(updates[field], str):
                    if updates[field].strip():
                        try:
                            updates[field] = json.loads(updates[field])
                        except json.JSONDecodeError:
                            raise ValueError(f"Geçersiz '{field}' formatı. JSON formatında olmalıdır.")
                    else: # Boş string ise None yap
                        updates[field] = None
            
            # HTTP methodunu büyük harfe çevir
            if 'request_method' in updates and isinstance(updates['request_method'], str):
                updates['request_method'] = updates['request_method'].upper()


            # ModelRepository.update_model bir tuple döndürür: (success, message)
            success, message = self.model_repo.update_model(model_id, updates)
            if not success:
                # Eğer mesaj "değişiklik yapılmadı" ise bu bir hata değil.
                if "değişiklik yapılmadı" not in message.lower():
                    raise Exception(message or f"AI Modeli (ID: {model_id}) güncellenemedi.")

            updated_model_entity = self.model_repo.get_model_by_id(model_id, include_api_key=False)
            if not updated_model_entity:
                 # Bu durum, güncelleme başarılı olsa bile modelin çekilememesi anlamına gelir, nadir olmalı.
                raise Exception(f"AI Modeli güncellendi ancak veritabanından çekilemedi (ID: {model_id}).")

            return simple_model_to_dict(updated_model_entity)
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"AI Modeli (ID: {model_id}) güncellenirken hata (AIModelService): {str(e)}", exc_info=True)
            # db_session.rollback()
            raise Exception(f"AI Modeli (ID: {model_id}) güncellenirken beklenmedik bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove()

# 3.3. UserService
# -----------------------------------------------------------------------------
class UserService:
    """Kullanıcı ile ilgili işlemleri yöneten servis sınıfı."""
    def __init__(self):
        # Gerçek UserRepository eklendiğinde:
        # self.user_repo = UserRepository()
        pass # Şimdilik repository yok

    def get_all_users_for_display(self) -> List[Dict[str, Any]]:
        """
        Tüm kullanıcıları gösterim için hazırlar.
        NOT: Bu bölüm, gerçek User modeli ve UserRepository eklendiğinde geliştirilmelidir.
             Şu an için örnek (mock) veri döndürmektedir.

        Returns:
            Kullanıcı bilgilerini içeren sözlük listesi.
        """
        # Gerçek implementasyon:
        # try:
        #     users_raw: List[User] = self.user_repo.get_all_users()
        #     users_data: List[Dict[str, Any]] = [
        #         simple_model_to_dict(user, columns=['id', 'username', 'email', 'role', 'created_at', 'is_active'])
        #         for user in users_raw
        #     ]
        #     return users_data
        # except Exception as e:
        #     current_app.logger.error(f"Kullanıcılar yüklenirken hata (UserService): {str(e)}", exc_info=True)
        #     raise

        # Örnek (Mock) Veri:
        current_app.logger.info("UserService.get_all_users_for_display: Örnek kullanıcı verisi kullanılıyor.")
        return [
            {'id': 1, 'username': 'goktugkara', 'email': 'goktug@example.com', 'role': 'Admin', 'created_at': '2024-01-10T10:00:00Z', 'is_active': True},
            {'id': 2, 'username': 'aysee', 'email': 'ayse.yilmaz@example.com', 'role': 'Editor', 'created_at': '2024-02-15T11:30:00Z', 'is_active': True},
            {'id': 3, 'username': 'mehmet_c', 'email': 'mehmet@example.com', 'role': 'User', 'created_at': '2024-03-20T14:45:00Z', 'is_active': False}
        ]

    # TODO: add_user, delete_user, update_user, get_user_by_id gibi metodlar eklenecek.

# 3.4. DashboardService
# -----------------------------------------------------------------------------
class DashboardService:
    """Yönetici paneli (dashboard) için genel istatistikleri sağlayan servis."""
    def __init__(self):
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()
        # self.user_repo = UserRepository() # Gerçek User repository eklendiğinde
        self.user_service = UserService() # Geçici olarak UserService'i kullan

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Dashboard için temel istatistikleri toplar.

        Returns:
            Toplam kullanıcı, model, kategori sayıları ve aktif görevler gibi
            istatistikleri içeren bir sözlük.
        """
        try:
            # Gerçek kullanıcı sayısı (UserRepository eklendiğinde):
            # total_users = self.user_repo.count_all_users()

            # Şimdilik UserService'deki örnek veriden kullanıcı sayısını al
            total_users = len(self.user_service.get_all_users_for_display())

            total_models = self.model_repo.count_all_models()
            total_categories = self.category_repo.count_all_categories()

            # Aktif görevler gibi diğer dinamik veriler buraya eklenebilir.
            # Örneğin, bir görev kuyruğu veya log tablosundan çekilebilir.
            active_tasks_placeholder = 15 # Örnek statik veri

            return {
                "total_users": total_users,
                "total_models": total_models,
                "total_categories": total_categories,
                "active_tasks": active_tasks_placeholder
                # Gelecekte eklenebilecekler:
                # "recent_activities": [...],
                # "system_health": "OK"
            }
        except Exception as e:
            current_app.logger.error(f"Dashboard istatistikleri alınırken hata: {str(e)}", exc_info=True)
            # Hata durumunda boş veya varsayılan değerler döndür
            return {
                "total_users": 0,
                "total_models": 0,
                "total_categories": 0,
                "active_tasks": 0,
                "error": "İstatistikler yüklenemedi."
            }

# 3.5. SettingsService
# -----------------------------------------------------------------------------
class SettingsService:
    """Uygulama ayarlarını yöneten servis sınıfı."""
    def get_settings_for_display(self) -> Dict[str, Any]:
        """
        Uygulama ayarlarını gösterim için hazırlar.
        NOT: Ayarlar veritabanından veya bir yapılandırma dosyasından çekilmelidir.
             Şu an için örnek (mock) veri döndürmektedir.

        Returns:
            Site adı, admin e-postası gibi ayarları içeren bir sözlük.
        """
        # Gerçek implementasyon:
        # settings_from_db = ConfigModel.get_all_settings()
        # return {setting.key: setting.value for setting in settings_from_db}

        current_app.logger.info("SettingsService.get_settings_for_display: Örnek ayar verisi kullanılıyor.")
        return {
            'site_name': 'Zekai Yönetim Paneli',
            'admin_email': 'admin@example.com',
            'maintenance_mode': False,
            'default_user_role': 'User',
            'items_per_page': 20
        }

    def save_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        Verilen ayarları kaydeder.
        NOT: Bu metod, ayarların veritabanına veya yapılandırma dosyasına
             kaydedilmesi için geliştirilmelidir.

        Args:
            settings_data: Kaydedilecek ayarları içeren bir sözlük.
                           Örn: {'site_name': 'Yeni Site Adı', 'maintenance_mode': True}

        Returns:
            Kaydetme işlemi başarılıysa True.

        Raises:
            Exception: Kaydetme sırasında bir hata oluşursa.
        """
        try:
            current_app.logger.info(f"Ayarlar kaydediliyor (SettingsService - Demo): {settings_data}")
            # Gerçek implementasyon:
            # for key, value in settings_data.items():
            #     ConfigModel.update_setting(key, value) # Veya repository üzerinden
            # db_session.commit() # Eğer repository'ler otomatik commit yapmıyorsa
            # current_app.config.update(settings_data) # Flask config'i de güncellemek gerekebilir
            return True
        except Exception as e:
            current_app.logger.error(f"Ayarlar kaydedilirken hata: {str(e)}", exc_info=True)
            # db_session.rollback()
            raise Exception("Ayarlar kaydedilirken bir sunucu hatası oluştu.")
        # finally:
            # db_session.remove()

# 4. Veritabanı Oturumu Yönetimi Notları
# =============================================================================
# Bu servislerde `db_session.commit()`, `db_session.rollback()`, ve
# `db_session.remove()` gibi çağrılar bulunmaktadır.
# Flask uygulamalarında veritabanı oturum yönetimi genellikle merkezi olarak
# `@app.teardown_appcontext` dekoratörü ile veya Flask-SQLAlchemy gibi
# eklentiler aracılığıyla request bazında yönetilir.

# Eğer merkezi bir oturum yönetimi varsa:
# 1. Servis metodları içindeki `db_session.commit()` çağrıları, işlemin
#    başarılı olduğunu belirtmek için kalabilir (eğer repository'ler otomatik
#    commit yapmıyorsa). Ancak, genellikle commit işlemi request sonunda
#    merkezi olarak yapılır.
# 2. `db_session.rollback()` çağrıları, hata durumunda işlemleri geri almak
#    için önemlidir ve kalmalıdır (yine, eğer merkezi yönetim bunu
#    otomatik yapmıyorsa).
# 3. `db_session.remove()` çağrıları, her servis metodu sonunda genellikle
#    gereksizdir ve oturumun erken kapatılmasına neden olabilir. Oturum,
#    request sonunda merkezi olarak kapatılmalıdır.

# Öneri:
# - Repository katmanının veritabanı oturumunu (session) almaktan ve temel
#   CRUD işlemlerini (add, delete, flush vb.) yönetmekten sorumlu olması.
# - Servis katmanının iş mantığını uygulaması, birden fazla repository
#   metodunu koordine etmesi ve gerektiğinde `db_session.commit()` veya
#   `db_session.rollback()` çağrılarını yapması (eğer işlemler bir "unit of work"
#   olarak ele alınıyorsa ve repository'ler commit/rollback yapmıyorsa).
# - Veritabanı oturumunun oluşturulması ve kapatılmasının (remove) merkezi
#   olarak (örn: Flask app context'i ile) yönetilmesi.

# Bu koddaki `db_session` çağrıları, projenin genel veritabanı yönetim
# stratejisine göre gözden geçirilmelidir. Şimdilik, orijinal yapıya
# sadık kalınarak yorumlar eklenmiştir.
