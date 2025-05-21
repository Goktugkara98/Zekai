# =============================================================================
# Model Deposu Modülü (Model Repository Module) - REVİZE EDİLMİŞ
# =============================================================================
# Bu modül, AI modelleriyle ilgili veritabanı işlemleri için bir depo sınıfı
# içerir. Yeni alanlar (`service_provider`, `external_model_name` vb.) için
# destek eklenmiştir.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
#
# 2.0 MODELREPOSITORY SINIFI (MODELREPOSITORY CLASS)
#     2.1. __init__                     : Başlatıcı metot (BaseRepository'den miras alınır).
#     2.2. create_model                 : Yeni bir AI modeli oluşturur.
#     2.3. update_model                 : Mevcut bir AI modelini günceller.
#     2.4. delete_model                 : Bir AI modelini siler.
#     2.5. get_model_by_id              : ID'ye göre bir AI modeli getirir.
#     2.6. get_models_by_category_id    : Kategori ID'sine göre AI modellerini getirir.
#     2.7. get_all_models               : Tüm AI modellerini getirir.
#     2.8. count_all_models             : Tüm AI modellerinin sayısını döndürür.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities.model import Model # Revize edilmiş Model entity'si
from typing import List, Optional, Tuple, Dict, Any
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import json # JSON işlemleri için

# =============================================================================
# 2.0 MODELREPOSITORY SINIFI (MODELREPOSITORY CLASS)
# =============================================================================
class ModelRepository(BaseRepository):
    """Model işlemleri için depo (repository) sınıfı."""

    # -------------------------------------------------------------------------
    # 2.1. Başlatıcı metot (__init__)
    #      BaseRepository'den miras alındığı için özellikle tanımlanmamıştır.
    # -------------------------------------------------------------------------
    # def __init__(self, db_connection: Optional[DatabaseConnection] = None):
    #     super().__init__(db_connection)

    # -------------------------------------------------------------------------
    # 2.2. Yeni bir AI modeli oluşturur (create_model) (Güncellendi)
    # -------------------------------------------------------------------------
    def create_model(self,
                     category_id: int,
                     name: str,
                     icon: Optional[str] = None,
                     description: Optional[str] = None,
                     details: Optional[Dict[str, Any]] = None,
                     service_provider: Optional[str] = None,
                     external_model_name: Optional[str] = None,
                     api_url: Optional[str] = None,
                     request_method: str = 'POST',
                     request_headers: Optional[Dict[str, Any]] = None,
                     request_body: Optional[Dict[str, Any]] = None,
                     response_path: Optional[str] = None,
                     api_key: Optional[str] = None,
                     prompt_template: Optional[str] = None,
                     status: str = 'active'
                     ) -> Tuple[bool, str, Optional[int]]:
        """
        Yeni bir AI modeli oluşturur.
        """
        try:
            if not name or not name.strip(): return False, "Model adı boş olamaz.", None
            if not isinstance(category_id, int) or category_id <= 0: return False, "Geçerli bir kategori ID'si gereklidir.", None
            if not service_provider or not service_provider.strip(): return False, "Servis sağlayıcı (service_provider) boş olamaz.", None
            if not external_model_name or not external_model_name.strip(): return False, "Harici model adı (external_model_name) boş olamaz.", None

            if len(name.strip()) > 255: return False, "Model adı 255 karakterden uzun olamaz.", None
            if service_provider and len(service_provider.strip()) > 100: return False, "Servis sağlayıcı 100 karakterden uzun olamaz.", None
            if external_model_name and len(external_model_name.strip()) > 255: return False, "Harici model adı 255 karakterden uzun olamaz.", None
            if api_url and len(api_url) > 2048: return False, "API URL'si 2048 karakterden uzun olamaz.", None
            if icon and len(icon.strip()) > 100: return False, "İkon 100 karakterden uzun olamaz.", None
            if request_method and len(request_method.strip()) > 10: return False, "İstek metodu 10 karakterden uzun olamaz.", None
            if response_path and len(response_path.strip()) > 255: return False, "Yanıt yolu 255 karakterden uzun olamaz.", None
            if api_key and len(api_key) > 512: return False, "API anahtarı 512 karakterden uzun olamaz.", None # Güvenlik notu entity'de
            if status and len(status.strip()) > 50: return False, "Durum 50 karakterden uzun olamaz.", None


            query = """
                INSERT INTO ai_models (
                    category_id, name, icon, description, details,
                    service_provider, external_model_name,
                    api_url, request_method, request_headers,
                    request_body, response_path, api_key,
                    prompt_template, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            details_str = json.dumps(details) if details is not None else None
            request_headers_str = json.dumps(request_headers) if request_headers is not None else None
            request_body_str = json.dumps(request_body) if request_body is not None else None

            values = (
                category_id, name.strip(),
                icon.strip() if icon else None,
                description.strip() if description else None,
                details_str,
                service_provider.strip(),
                external_model_name.strip(),
                api_url.strip() if api_url else None,
                request_method.strip().upper() if request_method else 'POST',
                request_headers_str, request_body_str,
                response_path.strip() if response_path else None,
                api_key,
                prompt_template.strip() if prompt_template else None,
                status.strip() if status else 'active'
            )

            model_id = self.insert(query, values)

            if model_id:
                return True, f"Model '{name.strip()}' başarıyla oluşturuldu (ID: {model_id}).", model_id
            else:
                return False, f"Model '{name.strip()}' oluşturulamadı (ID alınamadı).", None
        except MySQLError as e:
            error_message = f"Veritabanı hatası: {str(e)}"
            if "foreign key constraint fails" in str(e).lower() and "ai_models_ibfk_1" in str(e).lower(): # Örnek kısıtlama adı
                error_message = f"Veritabanı hatası: Belirtilen kategori ID ({category_id}) 'ai_categories' tablosunda bulunmuyor."
            return False, error_message, None
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # -------------------------------------------------------------------------
    # 2.3. Mevcut bir AI modelini günceller (update_model) (Güncellendi)
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
                return True, "Güncellenecek herhangi bir alan sağlanmadı." # Değişiklik yok, başarılı sayılabilir

            update_fields_parts = []
            params = []
            allowed_fields = [
                "category_id", "name", "icon", "description", "details",
                "service_provider", "external_model_name",
                "api_url", "request_method", "request_headers",
                "request_body", "response_path", "api_key",
                "prompt_template", "status"
            ]

            for field, value in updates.items():
                if field not in allowed_fields:
                    continue

                # Alanlara özel doğrulamalar ve formatlamalar
                if field == "name":
                    if not value or not str(value).strip(): return False, "Model adı boş olamaz."
                    if len(str(value).strip()) > 255: return False, "Model adı 255 karakterden uzun olamaz."
                    params.append(str(value).strip())
                elif field == "service_provider":
                    if not value or not str(value).strip(): return False, "Servis sağlayıcı boş olamaz."
                    if len(str(value).strip()) > 100: return False, "Servis sağlayıcı 100 karakterden uzun olamaz."
                    params.append(str(value).strip())
                elif field == "external_model_name":
                    if not value or not str(value).strip(): return False, "Harici model adı boş olamaz."
                    if len(str(value).strip()) > 255: return False, "Harici model adı 255 karakterden uzun olamaz."
                    params.append(str(value).strip())
                elif field == "category_id":
                    if value is not None and (not isinstance(value, int) or value <= 0) : return False, "Geçerli bir kategori ID'si gereklidir veya None olmalıdır."
                    params.append(value) # Kategori ID'si None olabilir (ilişkiyi kaldırmak için)
                elif field == "api_url":
                    if value is not None and len(str(value)) > 2048: return False, "API URL'si 2048 karakterden uzun olamaz."
                    params.append(str(value).strip() if value is not None else None)
                elif field == "icon":
                    if value is not None and len(str(value).strip()) > 100: return False, "İkon 100 karakterden uzun olamaz."
                    params.append(str(value).strip() if value is not None else None)
                elif field == "request_method":
                    if value is not None and len(str(value).strip()) > 10: return False, "İstek metodu 10 karakterden uzun olamaz."
                    params.append(str(value).strip().upper() if value else 'POST')
                elif field == "response_path":
                    if value is not None and len(str(value).strip()) > 255: return False, "Yanıt yolu 255 karakterden uzun olamaz."
                    params.append(str(value).strip() if value is not None else None)
                elif field == "api_key": # API anahtarı güncellenirken dikkatli olunmalı
                    if value is not None and len(str(value)) > 512: return False, "API anahtarı 512 karakterden uzun olamaz."
                    params.append(value) # Strip yapmıyoruz, boşluklar önemli olabilir
                elif field == "status":
                    if value is not None and len(str(value).strip()) > 50: return False, "Durum 50 karakterden uzun olamaz."
                    params.append(str(value).strip() if value is not None else 'active')
                elif field in ["description", "prompt_template"]: # TEXT alanları
                     params.append(str(value).strip() if value is not None else None)
                elif field in ["details", "request_headers", "request_body"]: # JSON alanları
                    params.append(json.dumps(value) if value is not None else None)
                else:
                    params.append(value) # Diğerleri için doğrudan değer

                update_fields_parts.append(f"{field} = %s")

            if not update_fields_parts:
                return True, "Güncellenecek geçerli alan bulunamadı veya sağlanmadı."

            params.append(model_id)
            query = f"UPDATE ai_models SET {', '.join(update_fields_parts)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"

            rows_affected = self.execute_query(query, tuple(params))

            if rows_affected > 0:
                return True, "Model başarıyla güncellendi."
            else:
                check_exists_query = "SELECT id FROM ai_models WHERE id = %s"
                exists_result = self.fetch_one(check_exists_query, (model_id,))
                if not exists_result:
                    return False, f"ID'si {model_id} olan model bulunamadı."
                # Değişiklik yapılmadıysa (veriler aynıysa) başarılı say
                return True, "Modelde herhangi bir değişiklik yapılmadı (veriler aynı olabilir)."
        except MySQLError as e:
            error_message = f"Veritabanı hatası: {str(e)}"
            if "foreign key constraint fails" in str(e).lower() and "ai_models_ibfk_1" in str(e).lower():
                 updated_category_id = updates.get("category_id")
                 error_message = f"Veritabanı hatası: Belirtilen kategori ID ({updated_category_id}) 'ai_categories' tablosunda bulunmuyor."
            return False, error_message
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # -------------------------------------------------------------------------
    # 2.4. Bir AI modelini siler (delete_model)
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
                return True, f"Model '{model_name}' (ID: {model_id}) başarıyla silindi."
            else:
                return False, f"Model '{model_name}' (ID: {model_id}) silinemedi (muhtemelen daha önce silinmiş veya bulunamadı)."
        except MySQLError as e:
            # user_messages tablosundaki foreign key kısıtlaması nedeniyle silme hatası olabilir.
            if "foreign key constraint fails" in str(e).lower():
                 return False, f"Model silinemedi: Bu modele referans veren kullanıcı mesajları mevcut. Modelin silinebilmesi için önce bu mesajların silinmesi veya model bağlantılarının kaldırılması gerekir. Hata: {str(e)}"
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # -------------------------------------------------------------------------
    # 2.5. ID'ye göre bir AI modeli getirir (get_model_by_id) (Güncellendi)
    # -------------------------------------------------------------------------
    def get_model_by_id(self, model_id: int, include_api_key: bool = False) -> Optional[Model]:
        """
        Verilen ID'ye sahip modeli getirir.
        """
        if not model_id or not isinstance(model_id, int) or model_id <= 0:
            return None

        query = """
            SELECT id, category_id, name, icon, description, details,
                   service_provider, external_model_name,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   prompt_template, status,
                   created_at, updated_at
            FROM ai_models WHERE id = %s
        """
        try:
            row = self.fetch_one(query, (model_id,))
            if row:
                model_data = dict(row)
                if not include_api_key and model_data.get('api_key') is not None:
                    model_data['api_key'] = "***GİZLİ***"
                return Model.from_dict(model_data)
            return None
        except MySQLError:
            # Hata durumunda loglama yerine None dönmek daha uygun olabilir.
            return None
        except Exception:
            return None

    # -------------------------------------------------------------------------
    # 2.6. Kategori ID'sine göre AI modellerini getirir (get_models_by_category_id) (Güncellendi)
    # -------------------------------------------------------------------------
    def get_models_by_category_id(self, category_id: int, include_api_keys: bool = False) -> List[Model]:
        """
        Belirli bir kategoriye ait tüm modelleri getirir.
        """
        if not isinstance(category_id, int) or category_id <= 0:
            return []

        query = """
            SELECT id, category_id, name, icon, description, details,
                   service_provider, external_model_name,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   prompt_template, status,
                   created_at, updated_at
            FROM ai_models WHERE category_id = %s ORDER BY name
        """
        models = []
        try:
            rows = self.fetch_all(query, (category_id,))
            for row_dict in rows:
                if not include_api_keys and row_dict.get('api_key') is not None:
                    row_dict['api_key'] = "***GİZLİ***"
                models.append(Model.from_dict(row_dict))
            return models
        except MySQLError:
            return []
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # 2.7. Tüm AI modellerini getirir (get_all_models) (Güncellendi)
    # -------------------------------------------------------------------------
    def get_all_models(self, include_api_keys: bool = False) -> List[Model]:
        """
        Tüm AI modellerini getirir.
        """
        query = """
            SELECT id, category_id, name, icon, description, details,
                   service_provider, external_model_name,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   prompt_template, status,
                   created_at, updated_at
            FROM ai_models ORDER BY category_id, name, id
        """
        models = []
        try:
            rows = self.fetch_all(query)
            for row_dict in rows:
                if not include_api_keys and row_dict.get('api_key') is not None:
                    row_dict['api_key'] = "***GİZLİ***"
                models.append(Model.from_dict(row_dict))
            return models
        except MySQLError:
            return []
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # 2.8. Tüm AI modellerinin sayısını döndürür (count_all_models)
    # -------------------------------------------------------------------------
    def count_all_models(self) -> int:
        """
        Veritabanındaki toplam model sayısını döndürür.
        """
        query = "SELECT COUNT(*) as count FROM ai_models"
        try:
            result = self.fetch_one(query)
            return result['count'] if result and 'count' in result else 0
        except MySQLError:
            return 0
        except Exception:
            return 0
