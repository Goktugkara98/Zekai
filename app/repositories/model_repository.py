# =============================================================================
# Model Deposu Modülü (Model Repository Module)
# =============================================================================
# Bu modül, AI modelleriyle ilgili veritabanı işlemleri için bir depo sınıfı
# içerir. Modellerin oluşturulması, güncellenmesi, silinmesi ve sorgulanması
# gibi işlemleri yönetir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. ModelRepository Sınıfı
#    2.1. __init__                 : Başlatıcı metot (BaseRepository'den miras alınır).
#    2.2. create_model             : Yeni bir model oluşturur.
#    2.3. update_model             : Mevcut bir modeli günceller.
#    2.4. delete_model             : Bir modeli siler.
#    2.5. get_model_by_id          : ID'ye göre bir model getirir.
#    2.6. get_model_by_data_ai_index : 'data_ai_index'e göre bir model getirir.
#    2.7. get_models_by_category_id: Kategori ID'sine göre modelleri getirir.
#    2.8. get_all_models           : Tüm modelleri getirir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import Model      # Model varlık sınıfı
from typing import List, Optional, Tuple, Dict # Tip ipuçları için Dict eklendi
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import re # data_ai_index doğrulaması için (orijinal kodda vardı, kaldırılmıştı, geri eklenebilir)
import json # 'details' alanını JSON string olarak saklamak/okumak için

# 2. ModelRepository Sınıfı
# =============================================================================
class ModelRepository(BaseRepository):
    """Model işlemleri için depo (repository) sınıfı."""

    # 2.1. __init__ metodu BaseRepository'den miras alındığı için
    #      ModelRepository'e özgü ek başlatma gerekmiyorsa yeniden tanımlanmasına gerek yoktur.

    # 2.2. create_model
    # -------------------------------------------------------------------------
    def create_model(self, category_id: int, name: str,
                     icon: Optional[str] = None, api_url: Optional[str] = None,
                     data_ai_index: Optional[str] = None, # data_ai_index eklendi
                     description: Optional[str] = None,
                     details: Optional[Dict] = None, # Dict olarak tip ipucu
                     image_filename: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Yeni bir AI modeli oluşturur.
        Args:
            category_id (int): Modelin ait olduğu kategori ID'si.
            name (str): Modelin adı.
            icon (Optional[str]): Model için ikon sınıfı.
            api_url (Optional[str]): Modelin API uç nokta URL'si.
            data_ai_index (Optional[str]): Model için benzersiz tanımlayıcı (ön yüzde kullanılır).
            description (Optional[str]): Modelin açıklaması.
            details (Optional[Dict]): Model hakkında ek JSON detayları.
            image_filename (Optional[str]): Model için görsel dosya adı.
        Returns:
            Tuple[bool, str, Optional[int]]: (başarı_durumu, mesaj, model_id)
        """
        print(f"DEBUG: Model oluşturuluyor: KategoriID={category_id}, Ad='{name}', DataAIIndex='{data_ai_index}'")
        try:
            # Kategori varlığını kontrol et
            query_check_category = "SELECT id FROM ai_categories WHERE id = %s"
            category = self.fetch_one(query_check_category, (category_id,))
            if not category:
                return False, f"ID'si {category_id} olan kategori bulunamadı.", None

            # Temel doğrulamalar
            if not name or not name.strip() or len(name) > 255:
                return False, "Model adı gereklidir ve 255 karakterden az olmalıdır.", None
            if data_ai_index and (not data_ai_index.strip() or len(data_ai_index) > 255): # data_ai_index için uzunluk kontrolü güncellendi
                return False, "Model 'data_ai_index' alanı 255 karakterden az olmalıdır.", None
            if api_url and len(api_url) > 2048:
                return False, "API URL'si 2048 karakterden az olmalıdır.", None

            # data_ai_index benzersiz olmalı (eğer doluysa)
            if data_ai_index and data_ai_index.strip():
                existing_model_by_index = self.get_model_by_data_ai_index(data_ai_index.strip())
                if existing_model_by_index:
                    return False, f"'{data_ai_index}' data_ai_index değerine sahip bir model zaten mevcut.", None
            else:
                # Eğer data_ai_index boş veya None ise, migrations.py'deki tablo tanımında
                # UNIQUE NOT NULL yerine UNIQUE olması gerekir (NULL değerler birden fazla olabilir).
                # Eğer her modelin benzersiz bir data_ai_index'i olması gerekiyorsa, bu alan zorunlu olmalı.
                # Şimdilik, boş olmasına izin veriyoruz (tablo tanımına göre).
                data_ai_index = None # Boş string yerine None olarak sakla

            # Model ekleme sorgusu
            # details alanı JSON olarak saklanacaksa json.dumps kullanılmalı.
            query = """
                INSERT INTO ai_models
                (category_id, name, icon, api_url, data_ai_index, description, details, image_filename)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                category_id,
                name.strip(),
                icon.strip() if icon else None,
                api_url.strip() if api_url else None,
                data_ai_index.strip() if data_ai_index else None, # strip eklendi
                description.strip() if description else None,
                json.dumps(details) if details is not None else None, # None kontrolü eklendi
                image_filename.strip() if image_filename else None
            )

            model_id = self.insert(query, values)
            if model_id:
                print(f"DEBUG: Model '{name}' başarıyla oluşturuldu. ID: {model_id}")
                return True, f"Model '{name}' başarıyla oluşturuldu.", model_id
            else:
                print(f"DEBUG: Model '{name}' oluşturulamadı, insert metodu ID döndürmedi.")
                return False, f"Model '{name}' oluşturulamadı (ID alınamadı).", None
        except MySQLError as e:
            print(f"DEBUG: Model oluşturulurken veritabanı hatası: {e}")
            # Spesifik MySQL hatalarını burada daha detaylı işleyebilirsiniz (örn: duplicate entry)
            if e.errno == 1062: # Duplicate entry
                 return False, f"Model oluşturulamadı: Benzersiz olması gereken bir alan (örn: data_ai_index veya başka bir UNIQUE kısıtlaması) zaten mevcut. Hata: {str(e)}", None
            return False, f"Veritabanı hatası: {str(e)}", None
        except Exception as ex:
            print(f"DEBUG: Model oluşturulurken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # 2.3. update_model
    # -------------------------------------------------------------------------
    def update_model(self, model_id: int, name: Optional[str] = None,
                     category_id: Optional[int] = None,
                     icon: Optional[str] = None, api_url: Optional[str] = None,
                     data_ai_index: Optional[str] = None, # data_ai_index eklendi
                     description: Optional[str] = None,
                     details: Optional[Dict] = None, # Dict olarak tip ipucu
                     image_filename: Optional[str] = None) -> Tuple[bool, str]:
        """
        Mevcut bir AI modelini günceller. Sadece None olmayan değerler güncellenir.
        Args:
            model_id (int): Güncellenecek modelin ID'si.
            name (Optional[str]): Modelin yeni adı.
            category_id (Optional[int]): Modelin yeni kategori ID'si.
            icon (Optional[str]): Modelin yeni ikonu.
            api_url (Optional[str]): Modelin yeni API URL'si.
            data_ai_index (Optional[str]): Modelin yeni data_ai_index'i.
            description (Optional[str]): Modelin yeni açıklaması.
            details (Optional[Dict]): Modelin yeni JSON detayları.
            image_filename (Optional[str]): Modelin yeni görsel dosya adı.
        Returns:
            Tuple[bool, str]: (başarı_durumu, mesaj)
        """
        # print(f"DEBUG: Model güncelleniyor: ID={model_id}")
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                return False, "Geçerli bir model ID'si gereklidir."

            # Modelin var olup olmadığını kontrol et
            current_model = self.get_model_by_id(model_id)
            if not current_model:
                return False, f"ID'si {model_id} olan model bulunamadı."

            update_fields = []
            params = []

            if name is not None:
                if not name.strip() or len(name) > 255:
                    return False, "Model adı boş olamaz ve 255 karakterden az olmalıdır."
                update_fields.append("name = %s")
                params.append(name.strip())
            if category_id is not None:
                if not isinstance(category_id, int) or category_id <= 0:
                     return False, "Geçerli bir kategori ID'si gereklidir."
                # Kategori varlığını kontrol et
                query_check_category = "SELECT id FROM ai_categories WHERE id = %s"
                category = self.fetch_one(query_check_category, (category_id,))
                if not category:
                    return False, f"ID'si {category_id} olan kategori bulunamadı."
                update_fields.append("category_id = %s")
                params.append(category_id)
            if icon is not None: # Boş string olarak güncellenmesine izin verilebilir (ikonu kaldırmak için)
                update_fields.append("icon = %s")
                params.append(icon.strip() if icon else None) # Eğer icon boş string ise None olarak ayarla
            if api_url is not None:
                if len(api_url) > 2048:
                     return False, "API URL'si 2048 karakterden az olmalıdır."
                update_fields.append("api_url = %s")
                params.append(api_url.strip() if api_url else None)
            if data_ai_index is not None:
                if not data_ai_index.strip() or len(data_ai_index) > 255:
                    return False, "Model 'data_ai_index' alanı boş olamaz ve 255 karakterden az olmalıdır."
                # data_ai_index benzersiz olmalı (mevcut model hariç)
                query_check_index = "SELECT id FROM ai_models WHERE data_ai_index = %s AND id != %s"
                existing_with_index = self.fetch_one(query_check_index, (data_ai_index.strip(), model_id))
                if existing_with_index:
                    return False, f"'{data_ai_index}' data_ai_index değerine sahip başka bir model zaten mevcut."
                update_fields.append("data_ai_index = %s")
                params.append(data_ai_index.strip())
            if description is not None:
                update_fields.append("description = %s")
                params.append(description.strip() if description else None)
            if details is not None: # details bir sözlük olmalı
                update_fields.append("details = %s")
                params.append(json.dumps(details))
            if image_filename is not None:
                update_fields.append("image_filename = %s")
                params.append(image_filename.strip() if image_filename else None)

            if not update_fields:
                return True, "Güncellenecek herhangi bir alan sağlanmadı." # Hata değil, bilgilendirme

            params.append(model_id) # WHERE koşulu için model_id'yi sona ekle

            query = f"UPDATE ai_models SET {', '.join(update_fields)} WHERE id = %s"
            rows_affected = self.execute_query(query, tuple(params))

            if rows_affected > 0:
                # print(f"DEBUG: Model ID {model_id} başarıyla güncellendi.")
                return True, f"Model başarıyla güncellendi."
            else:
                # print(f"DEBUG: Model ID {model_id} güncellenirken değişiklik yapılmadı (veriler aynı olabilir).")
                return True, "Modelde herhangi bir değişiklik yapılmadı (veriler aynı olabilir)."
        except MySQLError as e:
            # print(f"DEBUG: Model güncellenirken veritabanı hatası: {e}")
            if e.errno == 1062: # Duplicate entry
                 return False, f"Model güncellenemedi: Benzersiz olması gereken bir alan (örn: data_ai_index) zaten mevcut. Hata: {str(e)}"
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            # print(f"DEBUG: Model güncellenirken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.4. delete_model
    # -------------------------------------------------------------------------
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """
        Bir AI modelini siler.
        Args:
            model_id (int): Silinecek modelin ID'si.
        Returns:
            Tuple[bool, str]: (başarı_durumu, mesaj)
        """
        # print(f"DEBUG: Model siliniyor: ID={model_id}")
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                return False, "Geçerli bir model ID'si gereklidir."

            model = self.get_model_by_id(model_id)
            if not model:
                return False, f"ID'si {model_id} olan model bulunamadı."

            model_name = model.name # Mesaj için sakla

            query = "DELETE FROM ai_models WHERE id = %s"
            rows_affected = self.execute_query(query, (model_id,))

            if rows_affected > 0:
                # print(f"DEBUG: Model '{model_name}' (ID: {model_id}) başarıyla silindi.")
                return True, f"Model '{model_name}' başarıyla silindi."
            else:
                # print(f"DEBUG: Model '{model_name}' (ID: {model_id}) silinemedi veya zaten yoktu.")
                # Bu durum get_model_by_id ile yakalanır, ama ek kontrol.
                return False, f"Model '{model_name}' silinemedi."
        except MySQLError as e:
            # print(f"DEBUG: Model silinirken veritabanı hatası: {e}")
            # Örneğin, eğer bu model başka bir tabloda FOREIGN KEY ile kullanılıyorsa ve ON DELETE RESTRICT ise.
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            # print(f"DEBUG: Model silinirken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.5. get_model_by_id
    # -------------------------------------------------------------------------
    def get_model_by_id(self, model_id: int) -> Optional[Model]:
        """
        Verilen ID'ye sahip modeli getirir.
        Args:
            model_id (int): Getirilecek modelin ID'si.
        Returns:
            Optional[Model]: Bulunan Model nesnesi veya bulunamazsa None.
        """
        if not model_id or not isinstance(model_id, int) or model_id <= 0:
            # print(f"DEBUG: get_model_by_id için geçersiz ID: {model_id}")
            return None
        query = "SELECT * FROM ai_models WHERE id = %s" # Tüm sütunları seç
        result = self.fetch_one(query, (model_id,))
        # print(f"DEBUG: get_model_by_id({model_id}) sonucu: {'Bulundu' if result else 'Bulunamadı'}")
        return Model.from_dict(result) if result else None

    # 2.6. get_model_by_data_ai_index
    # -------------------------------------------------------------------------
    def get_model_by_data_ai_index(self, data_ai_index: str) -> Optional[Model]:
        """
        Verilen 'data_ai_index' değerine sahip modeli getirir.
        Args:
            data_ai_index (str): Modelin benzersiz 'data_ai_index'i.
        Returns:
            Optional[Model]: Bulunan Model nesnesi veya bulunamazsa None.
        """
        if not data_ai_index or not data_ai_index.strip():
            # print(f"DEBUG: get_model_by_data_ai_index için geçersiz data_ai_index: '{data_ai_index}'")
            return None
        query = "SELECT * FROM ai_models WHERE data_ai_index = %s" # Tüm sütunları seç
        result = self.fetch_one(query, (data_ai_index.strip(),))
        # print(f"DEBUG: get_model_by_data_ai_index('{data_ai_index}') sonucu: {'Bulundu' if result else 'Bulunamadı'}")
        return Model.from_dict(result) if result else None

    # 2.7. get_models_by_category_id
    # -------------------------------------------------------------------------
    def get_models_by_category_id(self, category_id: int) -> List[Model]:
        """
        Belirli bir kategori ID'sine ait tüm modelleri ID'ye göre sıralanmış olarak getirir.
        Args:
            category_id (int): Modellerin alınacağı kategori ID'si.
        Returns:
            List[Model]: Belirtilen kategoriye ait Model nesnelerinin listesi.
        """
        if not category_id or not isinstance(category_id, int) or category_id <= 0:
            # print(f"DEBUG: get_models_by_category_id için geçersiz category_id: {category_id}")
            return []
        query = "SELECT * FROM ai_models WHERE category_id = %s ORDER BY id" # Tüm sütunları seç
        results = self.fetch_all(query, (category_id,))
        # print(f"DEBUG: get_models_by_category_id({category_id}) sonucu: {len(results)} model bulundu.")
        return [Model.from_dict(row) for row in results if row]

    # 2.8. get_all_models
    # -------------------------------------------------------------------------
    def get_all_models(self) -> List[Model]:
        """
        Tüm AI modellerini kategori ID'sine ve ardından model ID'sine göre sıralanmış olarak getirir.
        Returns:
            List[Model]: Tüm Model nesnelerinin listesi.
        """
        query = "SELECT * FROM ai_models ORDER BY category_id, id" # Tüm sütunları seç
        results = self.fetch_all(query)
        # print(f"DEBUG: get_all_models sonucu: {len(results)} model bulundu.")
        return [Model.from_dict(row) for row in results if row]
