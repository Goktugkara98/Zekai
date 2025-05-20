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
#    2.8. count_all_models         : Tüm modellerin sayısını döndürür.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import Model      # Model varlık sınıfı
from typing import List, Optional, Tuple, Dict, Any # Tip ipuçları için
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import json # JSON alanlarını işlemek için
from datetime import datetime # Tarih/saat işlemleri için (Model entity'si için gerekebilir)

# 2. ModelRepository Sınıfı
# =============================================================================
class ModelRepository(BaseRepository):
    """Model işlemleri için depo (repository) sınıfı."""

    # __init__ metodu BaseRepository'den miras alınır, gerekirse burada override edilebilir.
    # def __init__(self, db_config: Dict[str, Any]):
    #     super().__init__(db_config)

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
        """
        try:
            if not name or not name.strip():
                return False, "Model adı boş olamaz.", None
            if not isinstance(category_id, int) or category_id <= 0:
                return False, "Geçerli bir kategori ID'si gereklidir.", None
            if len(name.strip()) > 255:
                return False, "Model adı 255 karakterden uzun olamaz.", None
            if api_url and len(api_url) > 2048:
                return False, "API URL'si 2048 karakterden uzun olamaz.", None
            if api_key and len(api_key) > 512:
                return False, "API anahtarı 512 karakterden uzun olamaz.", None
            if request_method and len(request_method) > 10:
                return False, "İstek metodu 10 karakterden uzun olamaz.", None
            if response_path and len(response_path) > 255:
                return False, "Yanıt yolu 255 karakterden uzun olamaz.", None

            query = """
                INSERT INTO ai_models (
                    category_id, name, icon, description, details,
                    api_url, request_method, request_headers,
                    request_body, response_path, api_key
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            details_str = json.dumps(details) if details is not None else None
            request_headers_str = json.dumps(request_headers) if request_headers is not None else None
            request_body_str = json.dumps(request_body) if request_body is not None else None

            values = (
                category_id, name.strip(),
                icon.strip() if icon else None,
                description.strip() if description else None,
                details_str,
                api_url.strip() if api_url else None,
                request_method.strip().upper() if request_method else 'POST',
                request_headers_str, request_body_str,
                response_path.strip() if response_path else None,
                api_key
            )

            model_id = self.insert(query, values)

            if model_id:
                return True, f"Model '{name}' başarıyla oluşturuldu.", model_id
            else:
                return False, f"Model '{name}' oluşturulamadı (ID alınamadı).", None
        except MySQLError as e:
            error_message = f"Veritabanı hatası: {str(e)}"
            if e.errno == 1062: # Unique constraint violation
                 error_message = f"Model oluşturulamadı: Benzersiz bir alan zaten mevcut. Hata: {str(e)}"
            elif e.errno == 1452: # Foreign key constraint violation
                 error_message = f"Model oluşturulamadı: Belirtilen kategori ID ({category_id}) 'ai_categories' tablosunda bulunamadı. Hata: {str(e)}"
            return False, error_message, None
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # 2.3. update_model
    # -------------------------------------------------------------------------
    def update_model(self, model_id: int,
                     updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Mevcut bir AI modelini günceller.
        """
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                return False, "Geçerli bir model ID'si gereklidir."
            if not updates or not isinstance(updates, dict):
                return True, "Güncellenecek herhangi bir alan sağlanmadı."

            update_fields_parts = []
            params = []
            allowed_fields = [
                "category_id", "name", "icon", "description", "details",
                "api_url", "request_method", "request_headers",
                "request_body", "response_path", "api_key"
            ]

            for field, value in updates.items():
                if field not in allowed_fields:
                    # Bilinmeyen alanları yoksay veya hata döndür, şimdilik yoksayılıyor.
                    continue

                if field == "name":
                    if not value or not str(value).strip():
                        return False, "Model adı boş olamaz."
                    if len(str(value).strip()) > 255:
                         return False, "Model adı 255 karakterden uzun olamaz."
                    update_fields_parts.append("name = %s")
                    params.append(str(value).strip())
                elif field == "category_id":
                    if not isinstance(value, int) or value <= 0:
                        return False, "Geçerli bir kategori ID'si gereklidir."
                    update_fields_parts.append("category_id = %s")
                    params.append(value)
                elif field == "api_url" and value and len(str(value)) > 2048:
                    return False, "API URL'si 2048 karakterden uzun olamaz."
                elif field == "api_key" and value and len(str(value)) > 512:
                     return False, "API anahtarı 512 karakterden uzun olamaz."
                elif field == "request_method" and value and len(str(value)) > 10:
                     return False, "İstek metodu 10 karakterden uzun olamaz."
                elif field == "response_path" and value and len(str(value)) > 255:
                     return False, "Yanıt yolu 255 karakterden uzun olamaz."
                elif field in ["icon", "description"]: # Diğer string alanlar için genel strip
                    update_fields_parts.append(f"{field} = %s")
                    params.append(str(value).strip() if value is not None else None)
                elif field in ["details", "request_headers", "request_body"]: # JSON alanları
                    update_fields_parts.append(f"{field} = %s")
                    params.append(json.dumps(value) if value is not None else None)
                else: # api_url, api_key, request_method, response_path için (yukarıda zaten uzunluk kontrolü yapıldı)
                    update_fields_parts.append(f"{field} = %s")
                    params.append(value)


            if not update_fields_parts:
                return True, "Güncellenecek geçerli alan bulunamadı veya sağlanmadı."

            params.append(model_id)
            query = f"UPDATE ai_models SET {', '.join(update_fields_parts)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
            rows_affected = self.execute_query(query, tuple(params))

            if rows_affected > 0:
                return True, "Model başarıyla güncellendi."
            else:
                check_exists_query = "SELECT id FROM ai_models WHERE id = %s"
                exists = self.fetch_one(check_exists_query, (model_id,))
                if not exists:
                    return False, f"ID'si {model_id} olan model bulunamadı."
                return True, "Modelde herhangi bir değişiklik yapılmadı (veriler aynı olabilir)."
        except MySQLError as e:
            error_message = f"Veritabanı hatası: {str(e)}"
            if e.errno == 1062:
                error_message = f"Model güncellenemedi: Benzersiz bir alan zaten mevcut. Hata: {str(e)}"
            elif e.errno == 1452:
                error_message = f"Model güncellenemedi: Belirtilen kategori ID geçersiz. Hata: {str(e)}"
            return False, error_message
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.4. delete_model
    # -------------------------------------------------------------------------
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """
        Bir AI modelini siler.
        """
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                return False, "Geçerli bir model ID'si gereklidir."

            query_select_name = "SELECT name FROM ai_models WHERE id = %s"
            model_info = self.fetch_one(query_select_name, (model_id,))
            if not model_info:
                 return False, f"ID'si {model_id} olan model bulunamadı."
            model_name = model_info['name']

            query_delete = "DELETE FROM ai_models WHERE id = %s"
            rows_affected = self.execute_query(query_delete, (model_id,))

            if rows_affected > 0:
                return True, f"Model '{model_name}' başarıyla silindi."
            else:
                return False, f"Model '{model_name}' silinemedi (muhtemelen zaten silinmiş)."
        except MySQLError as e:
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.5. get_model_by_id
    # -------------------------------------------------------------------------
    def get_model_by_id(self, model_id: int, include_api_key: bool = False) -> Optional[Model]:
        """
        Belirtilen ID'ye sahip modeli getirir.
        """
        if not model_id or not isinstance(model_id, int) or model_id <= 0:
            return None

        query = """
            SELECT id, category_id, name, icon, description, details,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   created_at, updated_at
            FROM ai_models WHERE id = %s
        """
        try:
            row = self.fetch_one(query, (model_id,))
            if row:
                model_data = dict(row)
                if not include_api_key and model_data.get('api_key'):
                    model_data['api_key'] = "***GİZLİ***"

                for field in ['details', 'request_headers', 'request_body']:
                    if isinstance(model_data.get(field), str):
                        try:
                            model_data[field] = json.loads(model_data[field])
                        except json.JSONDecodeError:
                            # JSON parse hatası durumunda alanı None yap
                            model_data[field] = None
                return Model.from_dict(model_data)
            else:
                return None
        except MySQLError:
            # Veritabanı hatalarında None döndür
            return None
        except Exception:
            # Diğer beklenmedik hatalarda None döndür
            return None

    # 2.6. get_models_by_category_id
    # -------------------------------------------------------------------------
    def get_models_by_category_id(self, category_id: int, include_api_keys: bool = False) -> List[Model]:
        """
        Belirtilen kategoriye ait tüm modelleri getirir.
        """
        if not isinstance(category_id, int) or category_id <= 0:
            return []

        query = """
            SELECT id, category_id, name, icon, description, details,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   created_at, updated_at
            FROM ai_models WHERE category_id = %s ORDER BY name
        """
        models = []
        try:
            rows = self.fetch_all(query, (category_id,))
            for row_dict in rows:
                if not include_api_keys and row_dict.get('api_key'):
                    row_dict['api_key'] = "***GİZLİ***"

                for field in ['details', 'request_headers', 'request_body']:
                    if isinstance(row_dict.get(field), str):
                        try:
                            row_dict[field] = json.loads(row_dict[field])
                        except json.JSONDecodeError:
                            row_dict[field] = None
                models.append(Model.from_dict(row_dict))
            return models
        except MySQLError:
            return []
        except Exception:
            return []

    # 2.7. get_all_models
    # -------------------------------------------------------------------------
    def get_all_models(self, include_api_keys: bool = False) -> List[Model]:
        """
        Tüm AI modellerini getirir.
        """
        query = """
            SELECT id, category_id, name, icon, description, details,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   created_at, updated_at
            FROM ai_models ORDER BY category_id, id
        """
        models = []
        try:
            rows = self.fetch_all(query)
            for row_dict in rows:
                if not include_api_keys and row_dict.get('api_key'):
                    row_dict['api_key'] = "***GİZLİ***"

                for field in ['details', 'request_headers', 'request_body']:
                    if isinstance(row_dict.get(field), str):
                        try:
                            row_dict[field] = json.loads(row_dict[field])
                        except json.JSONDecodeError:
                            row_dict[field] = None
                models.append(Model.from_dict(row_dict))
            return models
        except MySQLError:
            return []
        except Exception:
            return []
    
    # 2.8. count_all_models
    # -------------------------------------------------------------------------
    def count_all_models(self) -> int:
        """
        Tüm AI modellerin sayısını döndürür.
        """
        query = "SELECT COUNT(*) as count FROM ai_models"
        result = self.fetch_one(query)
        return result['count'] if result else 0