# =============================================================================
# AI Model Servis Modülü (AI Model Service Module)
# =============================================================================
# Bu modül, AI modelleri ve kategorileriyle ilgili servis katmanı işlevlerini
# içerir. Depo (repository) katmanları üzerinden veri işlemlerini yönetir ve
# bu verileri genellikle diğer servis katmanlarına veya rota (route) katmanına
# sunulacak şekilde hazırlar.
#
# İÇİNDEKİLER:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
# 2.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
#     (Bu dosyada özel bir yardımcı fonksiyon bulunmamaktadır)
# 3.0 SERVİS FONKSİYONLARI (SERVICE FUNCTIONS)
#     3.1. get_ai_model_api_details    : Bir AI modelinin API detaylarını getirir.
#     3.2. fetch_ai_categories_from_db : Tüm kategorileri ve modellerini listeler.
#     3.3. add_ai_model                : Yeni bir AI modeli ekler (gerekirse kategorisini de oluşturur).
#     3.4. get_all_available_models    : Tüm AI modellerini özet bilgilerle listeler.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
import json
from typing import Dict, List, Optional, Any, Tuple

from flask import current_app

from app.repositories.model_repository import ModelRepository
from app.repositories.category_repository import CategoryRepository
from app.models.base import DatabaseConnection # Veritabanı bağlantısı için
# Entity sınıfları doğrudan burada kullanılmıyor, repository'ler entity nesneleri döndürüyor.
# from app.models.entities.model import Model as AIModelEntity
# from app.models.entities.category import Category as CategoryEntity

# =============================================================================
# 2.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# =============================================================================
# Bu bölüme, bu servis modülüne özel yardımcı fonksiyonlar eklenebilir.
# Şimdilik bu dosyada özel bir yardımcı fonksiyon bulunmuyor.

# =============================================================================
# 3.0 SERVİS FONKSİYONLARI (SERVICE FUNCTIONS)
# =============================================================================

# -----------------------------------------------------------------------------
# 3.1. Bir AI modelinin API detaylarını getirir (get_ai_model_api_details)
# -----------------------------------------------------------------------------
def get_ai_model_api_details(model_identifier: Any) -> Optional[Dict[str, Any]]:
    """
    Belirli bir AI modelinin API etkileşimi için gerekli detaylarını getirir.
    Model, ID veya `data_ai_index` gibi alternatif bir tanımlayıcı ile bulunabilir.
    API anahtarını da içerir.
    """
    identifier_str = str(model_identifier).strip()
    db_connection_instance: Optional[DatabaseConnection] = None
    model_entity = None

    try:
        db_connection_instance = DatabaseConnection()
        ai_repo = ModelRepository(db_connection_instance) # Bağlantıyı repoya ver

        if identifier_str.isdigit():
            try:
                model_id = int(identifier_str)
                model_entity = ai_repo.get_model_by_id(model_id, include_api_key=True)
            except ValueError:
                current_app.logger.debug(f"get_ai_model_api_details: '{identifier_str}' sayısal ID'ye dönüştürülemedi.")
                pass

        # `data_ai_index` ile arama (eğer ModelRepository'de böyle bir metot varsa)
        # Bu metodun ModelRepository'de tanımlı olması gerekir. Şimdilik varsayımsal.
        if not model_entity and hasattr(ai_repo, 'get_model_by_data_ai_index'):
            try:
                model_entity = ai_repo.get_model_by_data_ai_index(identifier_str, include_api_key=True)
            except Exception as e: # Spesifik olmayan bir hata yakalama
                current_app.logger.warning(f"get_ai_model_api_details: data_ai_index '{identifier_str}' ile model aranırken hata: {e}")
                pass

        if not model_entity and identifier_str.startswith('txt_'):
            potential_id_str = identifier_str.replace('txt_', '', 1)
            if potential_id_str.isdigit():
                try:
                    model_id_from_txt = int(potential_id_str)
                    model_entity = ai_repo.get_model_by_id(model_id_from_txt, include_api_key=True)
                except ValueError:
                    current_app.logger.debug(f"get_ai_model_api_details: '{potential_id_str}' (txt_ prefixinden sonra) ID'ye dönüştürülemedi.")
                    pass

        if not model_entity:
            current_app.logger.info(f"get_ai_model_api_details: '{identifier_str}' ile eşleşen AI modeli bulunamadı.")
            return None

        model_details = {
            "id": getattr(model_entity, 'id', None),
            "name": getattr(model_entity, 'name', "N/A"),
            "api_url": getattr(model_entity, 'api_url', None),
            "request_method": getattr(model_entity, 'request_method', 'POST'),
            "request_headers": getattr(model_entity, 'request_headers', {}),
            "request_body_template": getattr(model_entity, 'request_body', {}),
            "response_path": getattr(model_entity, 'response_path', None),
            "api_key": getattr(model_entity, 'api_key', None),
            "service_provider": getattr(model_entity, 'service_provider', None),
            "external_model_name": getattr(model_entity, 'external_model_name', None),
            "prompt_template": getattr(model_entity, 'prompt_template', None)
        }
        current_app.logger.info(f"get_ai_model_api_details: Model '{model_details['name']}' (ID: {model_details['id']}) için API detayları bulundu.")
        return model_details

    except Exception as e:
        current_app.logger.error(f"get_ai_model_api_details: Model '{identifier_str}' için detaylar alınırken beklenmedik hata: {str(e)}", exc_info=True)
        return None
    finally:
        if db_connection_instance:
            db_connection_instance.close()

# -----------------------------------------------------------------------------
# 3.2. Tüm kategorileri ve modellerini listeler (fetch_ai_categories_from_db)
# -----------------------------------------------------------------------------
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """
    Tüm AI kategorilerini ve bu kategorilere ait modelleri (özet bilgilerle) listeler.
    """
    db_conn_cat: Optional[DatabaseConnection] = None
    db_conn_model: Optional[DatabaseConnection] = None
    categories_data_for_display: List[Dict[str, Any]] = []

    try:
        db_conn_cat = DatabaseConnection()
        category_repo = CategoryRepository(db_conn_cat)

        db_conn_model = DatabaseConnection()
        model_repo = ModelRepository(db_conn_model)

        all_categories = category_repo.get_all_categories()
        if not all_categories:
            current_app.logger.info("fetch_ai_categories_from_db: Hiç AI kategorisi bulunamadı.")
            return []

        for category_entity in all_categories:
            if category_entity.id is None: continue # ID'si olmayan kategoriyi atla

            category_dict = {
                "id": category_entity.id,
                "name": category_entity.name,
                "icon": category_entity.icon,
                "models": []
            }

            models_in_category = model_repo.get_models_by_category_id(category_entity.id, include_api_keys=False)

            for model_entity in models_in_category:
                if model_entity.id is None: continue # ID'si olmayan modeli atla
                model_dict = {
                    "id": model_entity.id,
                    "name": model_entity.name,
                    "icon": model_entity.icon,
                    "api_url": model_entity.api_url,
                    "service_provider": model_entity.service_provider,
                    "external_model_name": model_entity.external_model_name,
                    "description": model_entity.description,
                }
                category_dict["models"].append(model_dict)
            categories_data_for_display.append(category_dict)

        current_app.logger.info(f"fetch_ai_categories_from_db: {len(categories_data_for_display)} kategori ve modelleri başarıyla yüklendi.")
        return categories_data_for_display

    except Exception as e:
        current_app.logger.error(f"fetch_ai_categories_from_db: Kategoriler ve modeller yüklenirken hata: {str(e)}", exc_info=True)
        return []
    finally:
        if db_conn_cat:
            db_conn_cat.close()
        if db_conn_model and db_conn_model != db_conn_cat: # Aynı bağlantı değilse kapat
            db_conn_model.close()

# -----------------------------------------------------------------------------
# 3.3. Yeni bir AI modeli ekler (add_ai_model)
# -----------------------------------------------------------------------------
def add_ai_model(category_name: str,
                 model_name: str,
                 model_icon: Optional[str] = None,
                 api_url: Optional[str] = None, # Zorunlu olmalı mı? Model entity'sine göre değişir.
                 description: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 service_provider: Optional[str] = None, # Zorunlu
                 external_model_name: Optional[str] = None, # Zorunlu
                 request_method: str = 'POST',
                 request_headers: Optional[Dict[str, Any]] = None,
                 request_body: Optional[Dict[str, Any]] = None,
                 response_path: Optional[str] = None,
                 api_key: Optional[str] = None,
                 prompt_template: Optional[str] = None,
                 status: str = 'active'
                 ) -> Tuple[bool, str, Optional[int]]:
    """
    Veritabanına yeni bir AI modeli ekler.
    Eğer belirtilen kategori adı mevcut değilse, yeni bir kategori oluşturur.
    """
    db_conn_model: Optional[DatabaseConnection] = None
    db_conn_category: Optional[DatabaseConnection] = None
    category_id: Optional[int] = None

    try:
        if not service_provider or not service_provider.strip():
            return False, "Servis sağlayıcı (service_provider) zorunludur.", None
        if not external_model_name or not external_model_name.strip():
            return False, "Harici model adı (external_model_name) zorunludur.", None

        db_conn_category = DatabaseConnection()
        category_repo = CategoryRepository(db_conn_category)
        category_entity = category_repo.get_category_by_name(category_name)

        if not category_entity:
            current_app.logger.info(f"add_ai_model: Kategori '{category_name}' bulunamadı, yeni kategori oluşturulacak.")
            default_category_icon = "bi-folder-plus"
            success_cat, msg_cat, new_cat_id = category_repo.create_category(
                name=category_name,
                icon=default_category_icon
            )
            if not success_cat or new_cat_id is None:
                error_msg = f"Yeni kategori '{category_name}' oluşturulamadı: {msg_cat}"
                current_app.logger.error(f"add_ai_model: {error_msg}")
                return False, error_msg, None
            category_id = new_cat_id
            current_app.logger.info(f"add_ai_model: Yeni kategori '{category_name}' (ID: {category_id}) başarıyla oluşturuldu.")
        else:
            if category_entity.id is None: # Var olan kategorinin ID'si yoksa hata
                 error_msg = f"Mevcut kategori '{category_name}' için geçerli bir ID bulunamadı."
                 current_app.logger.error(f"add_ai_model: {error_msg}")
                 return False, error_msg, None
            category_id = category_entity.id
            current_app.logger.info(f"add_ai_model: Mevcut kategori '{category_name}' (ID: {category_id}) kullanılacak.")
        
        # Kategori bağlantısını burada kapatabiliriz, model repo için yeni bağlantı açılacak.
        if db_conn_category:
            db_conn_category.close()
            db_conn_category = None


        db_conn_model = DatabaseConnection()
        model_repo = ModelRepository(db_conn_model)

        success_model, msg_model, new_model_id = model_repo.create_model(
            category_id=category_id, # type: ignore # category_id'nin None olmayacağı garanti edildi
            name=model_name,
            icon=model_icon,
            description=description,
            details=details,
            service_provider=service_provider,
            external_model_name=external_model_name,
            api_url=api_url,
            request_method=request_method.upper(),
            request_headers=request_headers,
            request_body=request_body,
            response_path=response_path,
            api_key=api_key,
            prompt_template=prompt_template,
            status=status
        )

        if success_model:
            current_app.logger.info(f"add_ai_model: Yeni AI modeli '{model_name}' (ID: {new_model_id}) başarıyla eklendi. Mesaj: {msg_model}")
        else:
            current_app.logger.error(f"add_ai_model: AI modeli '{model_name}' eklenemedi. Mesaj: {msg_model}")

        return success_model, msg_model, new_model_id

    except Exception as e:
        current_app.logger.error(f"add_ai_model: Model '{model_name}' eklenirken beklenmedik bir hata oluştu: {str(e)}", exc_info=True)
        return False, f"Model eklenirken sunucuda beklenmedik bir hata oluştu: {str(e)}", None
    finally:
        if db_conn_category: # Eğer yukarıda kapatılmadıysa (hata durumunda)
            db_conn_category.close()
        if db_conn_model:
            db_conn_model.close()

# -----------------------------------------------------------------------------
# 3.4. Tüm AI modellerini özet bilgilerle listeler (get_all_available_models)
# -----------------------------------------------------------------------------
def get_all_available_models() -> List[Dict[str, Any]]:
    """
    Tüm mevcut (aktif/kullanılabilir) AI modellerini, belirli özet alanları
    içeren düz bir liste formatında getirir. API anahtarlarını içermez.
    """
    db_connection_instance: Optional[DatabaseConnection] = None
    models_summary_data: List[Dict[str, Any]] = []
    try:
        db_connection_instance = DatabaseConnection()
        model_repo = ModelRepository(db_connection_instance)
        model_entities = model_repo.get_all_models(include_api_keys=False)

        if not model_entities:
            current_app.logger.info("get_all_available_models: Hiç AI modeli bulunamadı.")
            return []

        for model_entity in model_entities:
            if model_entity.id is None: continue # ID'si olmayan modeli atla

            # data_ai_index için bir mantık gerekiyor. Model entity'sinde bu alan varsa kullanılır,
            # yoksa ID'den türetilebilir. Şimdilik ID'den türetiyoruz.
            data_ai_index_val = f"id_{model_entity.id}"
            if hasattr(model_entity, 'data_ai_index') and model_entity.data_ai_index: # type: ignore
                data_ai_index_val = str(model_entity.data_ai_index) # type: ignore

            model_dict = {
                "id": model_entity.id,
                "name": model_entity.name,
                "icon": model_entity.icon,
                "data_ai_index": data_ai_index_val,
                "api_url": model_entity.api_url,
                "category_id": model_entity.category_id,
                "service_provider": model_entity.service_provider,
                "external_model_name": model_entity.external_model_name,
                "description": model_entity.description
            }
            models_summary_data.append(model_dict)

        current_app.logger.info(f"get_all_available_models: {len(models_summary_data)} AI modeli başarıyla yüklendi.")
        return models_summary_data

    except Exception as e:
        current_app.logger.error(f"get_all_available_models: Modeller yüklenirken hata: {str(e)}", exc_info=True)
        return []
    finally:
        if db_connection_instance:
            db_connection_instance.close()
