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
#    2.6. get_models_by_category_id: Kategori ID'sine göre modelleri getirir.
#    2.7. get_all_models           : Tüm modelleri getirir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import Model      # Model varlık sınıfı
from typing import List, Optional, Tuple, Dict, Any # Tip ipuçları için
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import json # JSON alanlarını işlemek için
from datetime import datetime # Tarih/saat işlemleri için

# 2. ModelRepository Sınıfı
# =============================================================================
class ModelRepository(BaseRepository):
    """Model işlemleri için depo (repository) sınıfı."""

    # 2.2. create_model
    # -------------------------------------------------------------------------
    def create_model(self,
                     category_id: int,
                     name: str,
                     icon: Optional[str] = None,
                     description: Optional[str] = None,
                     details: Optional[Dict[str, Any]] = None,
                     api_url: Optional[str] = None,
                     request_method: str = 'POST',
                     request_headers: Optional[Dict[str, Any]] = None,
                     request_body: Optional[Dict[str, Any]] = None,
                     response_path: Optional[str] = None,
                     api_key: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Yeni bir AI modeli oluşturur.
        
        Args:
            category_id (int): Modelin ait olduğu kategori ID'si.
            name (str): Modelin adı (zorunlu).
            icon (str, optional): Model ikonu (örn: 'fas fa-robot').
            description (str, optional): Modelin açıklaması.
            details (dict, optional): Model hakkında ek JSON detayları.
            api_url (str, optional): API endpoint URL'si.
            request_method (str, optional): HTTP istek metodu (varsayılan: 'POST').
            request_headers (dict, optional): İstek başlıkları (JSON formatında).
            request_body (dict, optional): İstek gövdesi şablonu (JSON formatında).
            response_path (str, optional): JSON yanıtından veri çıkarma yolu.
            api_key (str, optional): API anahtarı.
            
        Returns:
            Tuple[bool, str, Optional[int]]: (başarı_durumu, mesaj, model_id)
        """
        # print(f"DEBUG: Model oluşturuluyor: Ad='{name}', KategoriID='{category_id}'")
        try:
            # Giriş doğrulamaları
            if not name or not name.strip():
                return False, "Model adı boş olamaz.", None
            if not isinstance(category_id, int) or category_id <= 0:
                 return False, "Geçerli bir kategori ID'si gereklidir.", None
            if len(name.strip()) > 255:
                return False, "Model adı 255 karakterden uzun olamaz.", None
            if api_url and len(api_url) > 2048:
                return False, "API URL'si 2048 karakterden uzun olamaz.", None
            if api_key and len(api_key) > 512: # migrations.py'deki VARCHAR(512) ile uyumlu
                return False, "API anahtarı 512 karakterden uzun olamaz.", None
            if request_method and len(request_method) > 10:
                return False, "İstek metodu 10 karakterden uzun olamaz.", None
            if response_path and len(response_path) > 255:
                return False, "Yanıt yolu 255 karakterden uzun olamaz.", None


            # Kategori varlığını kontrol et (isteğe bağlı, foreign key kısıtlaması zaten bunu yapar)
            # query_check_category = "SELECT id FROM ai_categories WHERE id = %s"
            # category = self.fetch_one(query_check_category, (category_id,))
            # if not category:
            #     return False, f"ID'si {category_id} olan kategori bulunamadı.", None

            query = """
                INSERT INTO ai_models (
                    category_id, name, icon, description, details, 
                    api_url, request_method, request_headers, 
                    request_body, response_path, api_key
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # JSON alanlarını stringe çevir
            details_str = json.dumps(details) if details is not None else None
            request_headers_str = json.dumps(request_headers) if request_headers is not None else None
            request_body_str = json.dumps(request_body) if request_body is not None else None
            
            values = (
                category_id,
                name.strip(),
                icon.strip() if icon else None,
                description.strip() if description else None,
                details_str,
                api_url.strip() if api_url else None,
                request_method.strip().upper() if request_method else 'POST',
                request_headers_str,
                request_body_str,
                response_path.strip() if response_path else None,
                api_key # API anahtarı doğrudan saklanıyor (geliştirme için)
            )

            model_id = self.insert(query, values)
            if model_id:
                # print(f"DEBUG: Model '{name}' başarıyla oluşturuldu. ID: {model_id}")
                return True, f"Model '{name}' başarıyla oluşturuldu.", model_id
            else:
                # print(f"DEBUG: Model '{name}' oluşturulamadı, insert metodu ID döndürmedi.")
                return False, f"Model '{name}' oluşturulamadı (ID alınamadı).", None
        except MySQLError as e:
            # print(f"DEBUG: Model oluşturulurken veritabanı hatası: {e}")
            if e.errno == 1062: # Duplicate entry (örn: UNIQUE kısıtlaması olan bir alan için)
                 return False, f"Model oluşturulamadı: Benzersiz bir alan zaten mevcut. Hata: {str(e)}", None
            if e.errno == 1452: # Cannot add or update a child row: a foreign key constraint fails
                 return False, f"Model oluşturulamadı: Belirtilen kategori ID ({category_id}) 'ai_categories' tablosunda bulunamadı. Hata: {str(e)}", None
            return False, f"Veritabanı hatası: {str(e)}", None
        except Exception as ex: # Beklenmedik diğer hatalar
            # print(f"DEBUG: Model oluşturulurken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # 2.3. update_model
    # -------------------------------------------------------------------------
    def update_model(self, model_id: int, 
                     updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Mevcut bir AI modelini günceller. Sadece 'updates' sözlüğünde belirtilen alanlar güncellenir.
        
        Args:
            model_id (int): Güncellenecek modelin ID'si.
            updates (Dict[str, Any]): Güncellenecek alanları ve yeni değerlerini içeren sözlük.
                                      Örn: {'name': 'Yeni Model Adı', 'api_key': 'yeni_anahtar'}
                                      JSON alanları (details, request_headers, request_body) dict olarak verilmeli.
            
        Returns:
            Tuple[bool, str]: (başarı_durumu, mesaj)
        """
        # print(f"DEBUG: Model güncelleniyor: ID={model_id}, Güncellemeler={updates}")
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                return False, "Geçerli bir model ID'si gereklidir."
            if not updates or not isinstance(updates, dict):
                return True, "Güncellenecek herhangi bir alan sağlanmadı."

            # Modelin var olup olmadığını kontrol et (isteğe bağlı, execute_query zaten satır sayısını döner)
            # current_model = self.get_model_by_id(model_id) # Bu, API anahtarını çözer, gereksiz olabilir
            # if not current_model:
            #     return False, f"ID'si {model_id} olan model bulunamadı."

            update_fields_parts = []
            params = []
            
            allowed_fields = [
                "category_id", "name", "icon", "description", "details", 
                "api_url", "request_method", "request_headers", 
                "request_body", "response_path", "api_key"
            ]

            for field, value in updates.items():
                if field not in allowed_fields:
                    # print(f"UYARI: '{field}' alanı güncellenemez, yoksayılıyor.")
                    continue

                # Alan bazlı doğrulamalar ve dönüşümler
                if field == "name":
                    if not value or not str(value).strip(): return False, "Model adı boş olamaz."
                    if len(str(value).strip()) > 255: return False, "Model adı 255 karakterden uzun olamaz."
                    update_fields_parts.append("name = %s")
                    params.append(str(value).strip())
                elif field == "category_id":
                    if not isinstance(value, int) or value <= 0: return False, "Geçerli bir kategori ID'si gereklidir."
                    # Kategori varlığını kontrol et (isteğe bağlı)
                    # query_check_category = "SELECT id FROM ai_categories WHERE id = %s"
                    # category = self.fetch_one(query_check_category, (value,))
                    # if not category: return False, f"ID'si {value} olan kategori bulunamadı."
                    update_fields_parts.append("category_id = %s")
                    params.append(value)
                elif field in ["icon", "description", "api_url", "request_method", "response_path", "api_key"]:
                    if field == "api_url" and value and len(str(value)) > 2048: return False, "API URL'si 2048 karakterden uzun olamaz."
                    if field == "api_key" and value and len(str(value)) > 512: return False, "API anahtarı 512 karakterden uzun olamaz."
                    if field == "request_method" and value and len(str(value)) > 10: return False, "İstek metodu 10 karakterden uzun olamaz."
                    if field == "response_path" and value and len(str(value)) > 255: return False, "Yanıt yolu 255 karakterden uzun olamaz."
                    
                    update_fields_parts.append(f"{field} = %s")
                    params.append(str(value).strip() if value is not None else None)
                elif field in ["details", "request_headers", "request_body"]:
                    update_fields_parts.append(f"{field} = %s")
                    params.append(json.dumps(value) if value is not None else None)
            
            if not update_fields_parts:
                return True, "Güncellenecek geçerli alan bulunamadı veya sağlanmadı."

            params.append(model_id) # WHERE koşulu için model_id'yi sona ekle

            query = f"UPDATE ai_models SET {', '.join(update_fields_parts)} WHERE id = %s"
            rows_affected = self.execute_query(query, tuple(params))

            if rows_affected > 0:
                # print(f"DEBUG: Model ID {model_id} başarıyla güncellendi.")
                return True, f"Model başarıyla güncellendi."
            else:
                # print(f"DEBUG: Model ID {model_id} güncellenirken değişiklik yapılmadı (veriler aynı olabilir veya model bulunamadı).")
                # Modelin var olup olmadığını kontrol etmek için ayrı bir sorgu yapılabilir.
                check_exists_query = "SELECT id FROM ai_models WHERE id = %s"
                exists = self.fetch_one(check_exists_query, (model_id,))
                if not exists:
                    return False, f"ID'si {model_id} olan model bulunamadı."
                return True, "Modelde herhangi bir değişiklik yapılmadı (veriler aynı olabilir)."
        except MySQLError as e:
            # print(f"DEBUG: Model güncellenirken veritabanı hatası: {e}")
            if e.errno == 1062: return False, f"Model güncellenemedi: Benzersiz bir alan zaten mevcut. Hata: {str(e)}"
            if e.errno == 1452: return False, f"Model güncellenemedi: Belirtilen kategori ID geçersiz. Hata: {str(e)}"
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

            # Modelin adını almak için önce modeli çek (isteğe bağlı, mesaj için)
            # model_data = self.get_model_by_id(model_id) # Bu API key'i de çözer, gereksiz olabilir
            # model_name = model_data['name'] if model_data else f"ID {model_id}"
            
            query_select_name = "SELECT name FROM ai_models WHERE id = %s"
            model_info = self.fetch_one(query_select_name, (model_id,))
            if not model_info:
                 return False, f"ID'si {model_id} olan model bulunamadı."
            model_name = model_info['name']


            query_delete = "DELETE FROM ai_models WHERE id = %s"
            rows_affected = self.execute_query(query_delete, (model_id,))

            if rows_affected > 0:
                # print(f"DEBUG: Model '{model_name}' (ID: {model_id}) başarıyla silindi.")
                return True, f"Model '{model_name}' başarıyla silindi."
            else:
                # print(f"DEBUG: Model '{model_name}' (ID: {model_id}) silinemedi veya zaten yoktu.")
                # Bu durum genellikle yukarıdaki model_info kontrolü ile yakalanır.
                return False, f"Model '{model_name}' silinemedi (muhtemelen zaten silinmiş)."
        except MySQLError as e:
            # print(f"DEBUG: Model silinirken veritabanı hatası: {e}")
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            # print(f"DEBUG: Model silinirken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.5. get_model_by_id
    # -------------------------------------------------------------------------
    def get_model_by_id(self, model_id: int, include_api_key: bool = False) -> Optional[Model]:
        """
        Belirtilen ID'ye sahip modeli getirir.
        
        Args:
            model_id (int): Getirilecek modelin ID'si.
            include_api_key (bool): API anahtarının sonuca dahil edilip edilmeyeceği.
                                    Varsayılan olarak False (güvenlik için).
            
        Returns:
            Optional[Model]: Model nesnesi veya None (bulunamazsa).
        """
        if not model_id or not isinstance(model_id, int) or model_id <= 0:
            return None
            
        query = """
            SELECT 
                id, category_id, name, icon, description, details,
                api_url, request_method, request_headers, 
                request_body, response_path, api_key,
                created_at, updated_at
            FROM ai_models
            WHERE id = %s
        """
        row = self.fetch_one(query, (model_id,))
        
        if row:
            model_data = dict(row) # Satırı sözlüğe çevir
            if not include_api_key:
                model_data['api_key'] = None # API anahtarını gizle
            return Model.from_dict(model_data)
        return None

    # 2.6. get_models_by_category_id
    # -------------------------------------------------------------------------
    def get_models_by_category_id(self, category_id: int, include_api_keys: bool = False) -> List[Model]:
        """
        Belirtilen kategoriye ait tüm modelleri getirir.
        
        Args:
            category_id (int): Kategori ID'si.
            include_api_keys (bool): API anahtarlarının sonuca dahil edilip edilmeyeceği.
                                     Varsayılan olarak False.
            
        Returns:
            List[Model]: Model nesnelerinin listesi.
        """
        if not isinstance(category_id, int) or category_id <= 0:
            return []

        query = """
            SELECT 
                id, category_id, name, icon, description, details,
                api_url, request_method, request_headers, 
                request_body, response_path, api_key,
                created_at, updated_at
            FROM ai_models
            WHERE category_id = %s
            ORDER BY name
        """
        rows = self.fetch_all(query, (category_id,))
        
        models = []
        for row_dict in rows:
            if not include_api_keys:
                row_dict['api_key'] = None # API anahtarını gizle
            models.append(Model.from_dict(row_dict))
        return models

    # 2.7. get_all_models
    # -------------------------------------------------------------------------
    def get_all_models(self, include_api_keys: bool = False) -> List[Model]:
        """
        Tüm AI modellerini kategori ID'si ve model ID'sine göre sıralanmış olarak getirir.
        
        Args:
            include_api_keys (bool): API anahtarlarının sonuca dahil edilip edilmeyeceği.
                                     Varsayılan olarak False.
        Returns:
            List[Model]: Model nesnelerinin listesi.
        """
        query = """
            SELECT 
                id, category_id, name, icon, description, details,
                api_url, request_method, request_headers, 
                request_body, response_path, api_key,
                created_at, updated_at
            FROM ai_models
            ORDER BY category_id, id
        """
        rows = self.fetch_all(query)
        
        models = []
        for row_dict in rows:
            if not include_api_keys:
                row_dict['api_key'] = None # API anahtarını gizle
            models.append(Model.from_dict(row_dict))
        return models

