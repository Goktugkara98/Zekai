# =============================================================================
# Model Deposu Modülü (Model Repository Module)
# =============================================================================
# Bu modül, AI modelleriyle ilgili veritabanı işlemleri için bir depo sınıfı
# içerir. Modellerin oluşturulması, güncellenmesi, silinmesi ve sorgulanması
# gibi işlemleri yönetir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Logger Yapılandırması (Logger Configuration)
# 3. Çağrı Bilgisi Yardımcı Fonksiyonu (Caller Info Helper)
# 4. ModelRepository Sınıfı
#    4.1. __init__                 : Başlatıcı metot (BaseRepository'den miras alınır).
#    4.2. create_model             : Yeni bir model oluşturur.
#    4.3. update_model             : Mevcut bir modeli günceller.
#    4.4. delete_model             : Bir modeli siler.
#    4.5. get_model_by_id          : ID'ye göre bir model getirir.
#    4.6. get_models_by_category_id: Kategori ID'sine göre modelleri getirir.
#    4.7. get_all_models           : Tüm modelleri getirir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import Model      # Model varlık sınıfı
from typing import List, Optional, Tuple, Dict, Any # Tip ipuçları için
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import json # JSON alanlarını işlemek için
from datetime import datetime # Tarih/saat işlemleri için
import logging # Logging modülü
import inspect # Çağrı yığınını incelemek için

# 2. Logger Yapılandırması (Logger Configuration)
# =============================================================================
# Temel logger yapılandırması
# Log formatı: ZAMAN DAMGASI - LOGGER ADI - LOG SEVİYESİ - MESAJ
# Tarih formatı: YYYY-AA-GG SS:DD:ss
logging.basicConfig(
    level=logging.DEBUG, # Loglanacak minimum seviye (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Bu modül için özel bir logger oluşturuluyor
logger = logging.getLogger(__name__) # __name__ mevcut modülün adını alır (örn: app.repositories.model_repository)

# 3. Çağrı Bilgisi Yardımcı Fonksiyonu (Caller Info Helper)
# =============================================================================
def log_caller_info(class_name: str, func_name: str, params_summary: Optional[Dict[str, Any]] = None):
    """
    Bir metodun çağrıldığını '----' ayırıcıları ile loglar ve çağrı kaynağı
    hakkında detayları içerir. İsteğe bağlı olarak parametre özeti de loglanabilir.
    """
    method_qualname = f"{class_name}.{func_name}"
    caller_info_log_str = ""
    try:
        # inspect.stack()[0] -> log_caller_info
        # inspect.stack()[1] -> çağıran metot (örn: create_model)
        # inspect.stack()[2] -> çağıran metodu çağıran yer (örn: bir servis katmanı)
        caller_frame = inspect.stack()[2]
        caller_function_name = caller_frame.function
        caller_filename = caller_frame.filename
        caller_lineno = caller_frame.lineno
        caller_info_log_str = f"  └── Called from: {caller_filename} -> {caller_function_name}() -> line {caller_lineno}"
    except IndexError:
        caller_info_log_str = "  └── Caller info: Not available (possibly top-level or direct script call)."
    except Exception as e:
        caller_info_log_str = f"  └── Caller info: Error retrieving - {e}."

    params_log_str = ""
    if params_summary:
        try:
            # Parametrelerin logda çok uzun olmasını engellemek için basit formatlama
            formatted_params = {
                k: (str(v)[:75] + '...' if isinstance(v, str) and len(v) > 75 else v)
                for k, v in params_summary.items()
            }
            params_log_str = f"\n  └── Params: {formatted_params}"
        except Exception as e:
            params_log_str = f"\n  └── Params: Error formatting - {e}"

    logger.debug(
        f"---- Method Invoked: {method_qualname}() ----{params_log_str}\n{caller_info_log_str}\n"
    )


# 4. ModelRepository Sınıfı
# =============================================================================
class ModelRepository(BaseRepository):
    """Model işlemleri için depo (repository) sınıfı."""

    # __init__ metodu BaseRepository'den miras alınır, gerekirse burada override edilebilir.
    # def __init__(self, db_config: Dict[str, Any]):
    #     super().__init__(db_config)
    #     # Sınıf başlatıldığında loglama
    #     logger.info(f"==== {self.__class__.__name__} Initialized ====\n  └── DB Config Keys: {list(db_config.keys()) if db_config else 'None'}\n")

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
        current_method_name = inspect.currentframe().f_code.co_name
        log_caller_info(self.__class__.__name__, current_method_name,
                        params_summary={"category_id": category_id, "name": name, "api_url": api_url})

        logger.info(f"==== Operation: Create AI Model ====\n  └── Name='{name}', CategoryID='{category_id}'\n")
        try:
            # Giriş doğrulamaları
            if not name or not name.strip():
                logger.warning("Model adı boş olamaz.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: Model name cannot be empty.\n")
                return False, "Model adı boş olamaz.", None
            if not isinstance(category_id, int) or category_id <= 0:
                logger.warning("Geçersiz kategori ID'si sağlandı.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: Invalid category ID ({category_id}).\n")
                return False, "Geçerli bir kategori ID'si gereklidir.", None
            if len(name.strip()) > 255:
                logger.warning(f"Model adı çok uzun: {len(name.strip())} karakter.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: Model name too long.\n")
                return False, "Model adı 255 karakterden uzun olamaz.", None
            # Diğer doğrulamalar için benzer loglama eklenebilir
            if api_url and len(api_url) > 2048:
                logger.warning("API URL'si çok uzun.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: API URL too long.\n")
                return False, "API URL'si 2048 karakterden uzun olamaz.", None
            if api_key and len(api_key) > 512:
                logger.warning("API anahtarı çok uzun.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: API key too long.\n")
                return False, "API anahtarı 512 karakterden uzun olamaz.", None
            if request_method and len(request_method) > 10:
                logger.warning("İstek metodu çok uzun.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: Request method too long.\n")
                return False, "İstek metodu 10 karakterden uzun olamaz.", None
            if response_path and len(response_path) > 255:
                logger.warning("Yanıt yolu çok uzun.\n")
                logger.warning(f"==== Result: Create AI Model - Validation Failed ====\n  └── Reason: Response path too long.\n")
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

            logger.debug(f"Executing INSERT query for model '{name}'.\n")
            model_id = self.insert(query, values)

            if model_id:
                logger.info(f"Model '{name}' başarıyla oluşturuldu. ID: {model_id}\n")
                logger.info(f"==== Result: Create AI Model - Success ====\n  └── Model ID: {model_id}\n")
                return True, f"Model '{name}' başarıyla oluşturuldu.", model_id
            else:
                logger.error(f"Model '{name}' oluşturulamadı, insert metodu ID döndürmedi.\n")
                logger.error(f"==== Result: Create AI Model - Failure ====\n  └── Reason: No ID returned from insert operation.\n")
                return False, f"Model '{name}' oluşturulamadı (ID alınamadı).", None
        except MySQLError as e:
            logger.error(f"Model oluşturulurken veritabanı hatası (errno: {e.errno}): {e}\n", exc_info=False) # exc_info=False to avoid duplicate stack trace if not needed here
            error_message = f"Veritabanı hatası: {str(e)}"
            if e.errno == 1062:
                 error_message = f"Model oluşturulamadı: Benzersiz bir alan zaten mevcut. Hata: {str(e)}"
            if e.errno == 1452:
                 error_message = f"Model oluşturulamadı: Belirtilen kategori ID ({category_id}) 'ai_categories' tablosunda bulunamadı. Hata: {str(e)}"
            logger.error(f"==== Result: Create AI Model - Database Error ====\n  └── MySQL ErrorNo {e.errno}: {e.msg}\n")
            return False, error_message, None
        except Exception as ex:
            logger.critical(f"Model oluşturulurken beklenmedik kritik hata: {ex}\n", exc_info=True)
            logger.critical(f"==== Result: Create AI Model - Unexpected Critical Error ====\n  └── Error: {str(ex)}\n")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # 2.3. update_model
    # -------------------------------------------------------------------------
    def update_model(self, model_id: int,
                     updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Mevcut bir AI modelini günceller.
        """
        current_method_name = inspect.currentframe().f_code.co_name
        log_caller_info(self.__class__.__name__, current_method_name,
                        params_summary={"model_id": model_id, "update_keys": list(updates.keys())})

        logger.info(f"==== Operation: Update AI Model ====\n  └── ID={model_id}, Updates='{list(updates.keys())}'\n")
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                logger.warning("Geçersiz model ID'si sağlandı.\n")
                logger.warning(f"==== Result: Update AI Model - Validation Failed ====\n  └── Reason: Invalid model ID ({model_id}).\n")
                return False, "Geçerli bir model ID'si gereklidir."
            if not updates or not isinstance(updates, dict):
                logger.info("Güncellenecek herhangi bir alan sağlanmadı.\n")
                # Bu bir hata durumu değil, işlem yapılmadı olarak kabul edilebilir.
                logger.info(f"==== Result: Update AI Model - No Action ====\n  └── Reason: No fields provided for update.\n")
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
                    logger.warning(f"'{field}' alanı güncellenemez, yoksayılıyor.\n")
                    continue

                # Alan bazlı doğrulamalar (create_model'deki gibi)
                # Örnek: name alanı için
                if field == "name":
                    if not value or not str(value).strip():
                        logger.warning("Model adı güncellenirken boş bırakılamaz.\n")
                        logger.warning(f"==== Result: Update AI Model - Validation Failed ====\n  └── Reason: Model name cannot be empty during update.\n")
                        return False, "Model adı boş olamaz."
                    if len(str(value).strip()) > 255:
                         logger.warning(f"Model adı güncellenirken çok uzun: {len(str(value).strip())} karakter.\n")
                         logger.warning(f"==== Result: Update AI Model - Validation Failed ====\n  └── Reason: Model name too long for update.\n")
                         return False, "Model adı 255 karakterden uzun olamaz."
                    update_fields_parts.append("name = %s")
                    params.append(str(value).strip())
                elif field == "category_id":
                    if not isinstance(value, int) or value <= 0:
                        logger.warning("Geçersiz kategori ID'si sağlandı.\n")
                        logger.warning(f"==== Result: Update AI Model - Validation Failed ====\n  └── Reason: Invalid category ID ({value}) for update.\n")
                        return False, "Geçerli bir kategori ID'si gereklidir."
                    update_fields_parts.append("category_id = %s")
                    params.append(value)
                elif field == "api_url" and value and len(str(value)) > 2048:
                    logger.warning("API URL'si güncellenirken çok uzun.\n")
                    logger.warning(f"==== Result: Update AI Model - Validation Failed ====\n  └── Reason: API URL too long for update.\n")
                    return False, "API URL'si 2048 karakterden uzun olamaz."
                # Diğer alanlar için benzer doğrulamalar eklenebilir.
                elif field in ["icon", "description", "request_method", "response_path", "api_key"]:
                    update_fields_parts.append(f"{field} = %s")
                    params.append(str(value).strip() if value is not None else None)
                elif field in ["details", "request_headers", "request_body"]:
                    update_fields_parts.append(f"{field} = %s")
                    params.append(json.dumps(value) if value is not None else None)

            if not update_fields_parts:
                logger.info("Güncellenecek geçerli alan bulunamadı veya sağlanmadı.\n")
                logger.info(f"==== Result: Update AI Model - No Action ====\n  └── Reason: No valid fields found for update.\n")
                return True, "Güncellenecek geçerli alan bulunamadı veya sağlanmadı."

            params.append(model_id) # WHERE clause için model_id
            query = f"UPDATE ai_models SET {', '.join(update_fields_parts)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
            logger.debug(f"Executing UPDATE query for model ID {model_id} with fields: {update_fields_parts}.\n")
            rows_affected = self.execute_query(query, tuple(params))

            if rows_affected > 0:
                logger.info(f"Model ID {model_id} başarıyla güncellendi. Etkilenen satır: {rows_affected}\n")
                logger.info(f"==== Result: Update AI Model - Success ====\n  └── Model ID: {model_id}, Rows Affected: {rows_affected}\n")
                return True, f"Model başarıyla güncellendi."
            else:
                check_exists_query = "SELECT id FROM ai_models WHERE id = %s"
                exists = self.fetch_one(check_exists_query, (model_id,))
                if not exists:
                    logger.warning(f"Güncellenmek istenen model ID {model_id} bulunamadı.\n")
                    logger.warning(f"==== Result: Update AI Model - Failure ====\n  └── Reason: Model ID {model_id} not found.\n")
                    return False, f"ID'si {model_id} olan model bulunamadı."

                logger.info(f"Model ID {model_id} güncellenirken değişiklik yapılmadı (veriler aynı olabilir).\n")
                logger.info(f"==== Result: Update AI Model - No Change ====\n  └── Model ID: {model_id} (data might be identical).\n")
                return True, "Modelde herhangi bir değişiklik yapılmadı (veriler aynı olabilir)."
        except MySQLError as e:
            logger.error(f"Model güncellenirken veritabanı hatası (errno: {e.errno}): {e}\n", exc_info=False)
            error_message = f"Veritabanı hatası: {str(e)}"
            if e.errno == 1062: error_message = f"Model güncellenemedi: Benzersiz bir alan zaten mevcut. Hata: {str(e)}"
            if e.errno == 1452: error_message = f"Model güncellenemedi: Belirtilen kategori ID geçersiz. Hata: {str(e)}"
            logger.error(f"==== Result: Update AI Model - Database Error ====\n  └── MySQL ErrorNo {e.errno}: {e.msg}\n")
            return False, error_message
        except Exception as ex:
            logger.critical(f"Model güncellenirken beklenmedik kritik hata: {ex}\n", exc_info=True)
            logger.critical(f"==== Result: Update AI Model - Unexpected Critical Error ====\n  └── Error: {str(ex)}\n")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.4. delete_model
    # -------------------------------------------------------------------------
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """
        Bir AI modelini siler.
        """
        current_method_name = inspect.currentframe().f_code.co_name
        log_caller_info(self.__class__.__name__, current_method_name, params_summary={"model_id": model_id})

        logger.info(f"==== Operation: Delete AI Model ====\n  └── ID={model_id}\n")
        try:
            if not model_id or not isinstance(model_id, int) or model_id <= 0:
                logger.warning("Geçersiz model ID'si sağlandı.\n")
                logger.warning(f"==== Result: Delete AI Model - Validation Failed ====\n  └── Reason: Invalid model ID ({model_id}).\n")
                return False, "Geçerli bir model ID'si gereklidir."

            query_select_name = "SELECT name FROM ai_models WHERE id = %s"
            logger.debug(f"Checking existence of model ID {model_id} before deletion.\n")
            model_info = self.fetch_one(query_select_name, (model_id,))
            if not model_info:
                 logger.warning(f"Silinmek istenen model ID {model_id} bulunamadı.\n")
                 logger.warning(f"==== Result: Delete AI Model - Failure ====\n  └── Reason: Model ID {model_id} not found.\n")
                 return False, f"ID'si {model_id} olan model bulunamadı."
            model_name = model_info['name']
            logger.info(f"Model '{model_name}' (ID: {model_id}) silinmek üzere bulundu.\n")

            query_delete = "DELETE FROM ai_models WHERE id = %s"
            logger.debug(f"Executing DELETE query for model ID {model_id}.\n")
            rows_affected = self.execute_query(query_delete, (model_id,))

            if rows_affected > 0:
                logger.info(f"Model '{model_name}' (ID: {model_id}) başarıyla silindi.\n")
                logger.info(f"==== Result: Delete AI Model - Success ====\n  └── Model '{model_name}' (ID: {model_id}) deleted.\n")
                return True, f"Model '{model_name}' başarıyla silindi."
            else:
                # Bu durum fetch_one kontrolü ile yakalanmış olmalı ama ek bir güvenlik.
                logger.warning(f"Model '{model_name}' (ID: {model_id}) silinemedi veya zaten yoktu (etkilenen satır: 0).\n")
                logger.warning(f"==== Result: Delete AI Model - No Action ====\n  └── Reason: Model ID {model_id} not deleted (possibly already gone, rows_affected: 0).\n")
                return False, f"Model '{model_name}' silinemedi (muhtemelen zaten silinmiş)."
        except MySQLError as e:
            logger.error(f"Model silinirken veritabanı hatası: {e}\n", exc_info=True)
            logger.error(f"==== Result: Delete AI Model - Database Error ====\n  └── MySQL Error: {str(e)}\n")
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            logger.critical(f"Model silinirken beklenmedik kritik hata: {ex}\n", exc_info=True)
            logger.critical(f"==== Result: Delete AI Model - Unexpected Critical Error ====\n  └── Error: {str(ex)}\n")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.5. get_model_by_id
    # -------------------------------------------------------------------------
    def get_model_by_id(self, model_id: int, include_api_key: bool = False) -> Optional[Model]:
        """
        Belirtilen ID'ye sahip modeli getirir.
        """
        current_method_name = inspect.currentframe().f_code.co_name
        log_caller_info(self.__class__.__name__, current_method_name,
                        params_summary={"model_id": model_id, "include_api_key": include_api_key})

        logger.info(f"==== Operation: Get Model by ID ====\n  └── ID={model_id}, IncludeAPIKey={include_api_key}\n")
        if not model_id or not isinstance(model_id, int) or model_id <= 0:
            logger.warning("Geçersiz model ID'si sağlandı.\n")
            logger.warning(f"==== Result: Get Model by ID - Validation Failed ====\n  └── Reason: Invalid model ID ({model_id}).\n")
            return None

        query = """
            SELECT id, category_id, name, icon, description, details,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   created_at, updated_at
            FROM ai_models WHERE id = %s
        """
        try:
            logger.debug(f"Executing SELECT query for model ID {model_id}.\n")
            row = self.fetch_one(query, (model_id,))
            if row:
                model_data = dict(row)
                if not include_api_key:
                    if model_data.get('api_key'):
                        model_data['api_key'] = "***GİZLİ***"
                        logger.debug(f"API key for model ID {model_id} is being masked.\n")
                else:
                    if model_data.get('api_key'):
                        logger.warning(f"API key for model ID {model_id} is being included in the result.\n")

                for field in ['details', 'request_headers', 'request_body']:
                    if isinstance(model_data.get(field), str):
                        try:
                            model_data[field] = json.loads(model_data[field])
                        except json.JSONDecodeError:
                            logger.warning(f"Model ID {model_id}, alan '{field}' için JSON parse hatası. Ham veri: {model_data[field]}\n")
                            model_data[field] = None

                logger.info(f"Model ID {model_id} bulundu: {model_data['name']}\n")
                logger.info(f"==== Result: Get Model by ID - Success ====\n  └── Model '{model_data['name']}' found.\n")
                return Model.from_dict(model_data)
            else:
                logger.info(f"Model ID {model_id} bulunamadı.\n")
                logger.info(f"==== Result: Get Model by ID - Not Found ====\n  └── Model ID {model_id} does not exist.\n")
                return None
        except MySQLError as e:
            logger.error(f"Model ID {model_id} getirilirken veritabanı hatası: {e}\n", exc_info=True)
            logger.error(f"==== Result: Get Model by ID - Database Error ====\n  └── MySQL Error: {str(e)}\n")
            return None
        except Exception as ex:
            logger.critical(f"Model ID {model_id} getirilirken beklenmedik hata: {ex}\n", exc_info=True)
            logger.critical(f"==== Result: Get Model by ID - Unexpected Critical Error ====\n  └── Error: {str(ex)}\n")
            return None

    # 2.6. get_models_by_category_id
    # -------------------------------------------------------------------------
    def get_models_by_category_id(self, category_id: int, include_api_keys: bool = False) -> List[Model]:
        """
        Belirtilen kategoriye ait tüm modelleri getirir.
        """
        current_method_name = inspect.currentframe().f_code.co_name
        log_caller_info(self.__class__.__name__, current_method_name,
                        params_summary={"category_id": category_id, "include_api_keys": include_api_keys})

        logger.info(f"==== Operation: Get Models by Category ID ====\n  └── CategoryID={category_id}, IncludeAPIKeys={include_api_keys}\n")
        if not isinstance(category_id, int) or category_id <= 0:
            logger.warning("Geçersiz kategori ID'si sağlandı.\n")
            logger.warning(f"==== Result: Get Models by Category ID - Validation Failed ====\n  └── Reason: Invalid category ID ({category_id}).\n")
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
            logger.debug(f"Executing SELECT query for models in category ID {category_id}.\n")
            rows = self.fetch_all(query, (category_id,))
            for row_dict in rows:
                if not include_api_keys:
                    if row_dict.get('api_key'):
                        row_dict['api_key'] = "***GİZLİ***"
                else:
                    if row_dict.get('api_key'):
                         logger.warning(f"API key for model ID {row_dict['id']} is being included in the results for category {category_id}.\n")

                for field in ['details', 'request_headers', 'request_body']:
                    if isinstance(row_dict.get(field), str):
                        try:
                            row_dict[field] = json.loads(row_dict[field])
                        except json.JSONDecodeError:
                            logger.warning(f"Model ID {row_dict['id']}, alan '{field}' için JSON parse hatası. Ham veri: {row_dict[field]}\n")
                            row_dict[field] = None
                models.append(Model.from_dict(row_dict))

            logger.info(f"Kategori ID {category_id} için {len(models)} model bulundu.\n")
            logger.info(f"==== Result: Get Models by Category ID - Success ====\n  └── Found {len(models)} models for Category ID {category_id}.\n")
            return models
        except MySQLError as e:
            logger.error(f"Kategori ID {category_id} için modeller getirilirken veritabanı hatası: {e}\n", exc_info=True)
            logger.error(f"==== Result: Get Models by Category ID - Database Error ====\n  └── MySQL Error: {str(e)}\n")
            return []
        except Exception as ex:
            logger.critical(f"Kategori ID {category_id} için modeller getirilirken beklenmedik hata: {ex}\n", exc_info=True)
            logger.critical(f"==== Result: Get Models by Category ID - Unexpected Critical Error ====\n  └── Error: {str(ex)}\n")
            return []

    # 2.7. get_all_models
    # -------------------------------------------------------------------------
    def get_all_models(self, include_api_keys: bool = False) -> List[Model]:
        """
        Tüm AI modellerini getirir.
        """
        current_method_name = inspect.currentframe().f_code.co_name
        log_caller_info(self.__class__.__name__, current_method_name,
                        params_summary={"include_api_keys": include_api_keys})

        logger.info(f"==== Operation: Get All Models ====\n  └── IncludeAPIKeys={include_api_keys}\n")
        query = """
            SELECT id, category_id, name, icon, description, details,
                   api_url, request_method, request_headers,
                   request_body, response_path, api_key,
                   created_at, updated_at
            FROM ai_models ORDER BY category_id, id
        """
        models = []
        try:
            logger.debug("Executing SELECT query to fetch all models.\n")
            rows = self.fetch_all(query)
            for row_dict in rows:
                if not include_api_keys:
                    if row_dict.get('api_key'):
                        row_dict['api_key'] = "***GİZLİ***"
                else:
                    if row_dict.get('api_key'):
                        logger.warning(f"API key for model ID {row_dict['id']} is being included in 'get_all_models' result.\n")

                for field in ['details', 'request_headers', 'request_body']:
                    if isinstance(row_dict.get(field), str):
                        try:
                            row_dict[field] = json.loads(row_dict[field])
                        except json.JSONDecodeError:
                            logger.warning(f"Model ID {row_dict['id']}, alan '{field}' için JSON parse hatası. Ham veri: {row_dict[field]}\n")
                            row_dict[field] = None
                models.append(Model.from_dict(row_dict))

            logger.info(f"Toplam {len(models)} model bulundu.\n")
            logger.info(f"==== Result: Get All Models - Success ====\n  └── Found {len(models)} models in total.\n")
            return models
        except MySQLError as e:
            logger.error(f"Tüm modeller getirilirken veritabanı hatası: {e}\n", exc_info=True)
            logger.error(f"==== Result: Get All Models - Database Error ====\n  └── MySQL Error: {str(e)}\n")
            return []
        except Exception as ex:
            logger.critical(f"Tüm modeller getirilirken beklenmedik hata: {ex}\n", exc_info=True)
            logger.critical(f"==== Result: Get All Models - Unexpected Critical Error ====\n  └── Error: {str(ex)}\n")
            return []