# =============================================================================
# AI Model Service Module
# =============================================================================
# Bu modül, AI modelleri ve kategorileriyle ilgili servis katmanı
# işlevlerini içerir. Depo katmanları üzerinden veri işlemlerini yönetir.
#
# İçindekiler:
# 1. Imports
# 2. AI Model Yönetimi
#    2.1. Model Detayları Getirme (get_ai_model_api_details)
#    2.2. Kategori ve Model Listeleme (fetch_ai_categories_from_db)
# 3. Model ve Kategori İşlemleri
#    3.1. Model Ekleme (add_ai_model)
#    3.2. Tüm Kullanılabilir Modelleri Getirme (get_all_available_models)
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from app.repositories.model_repository import ModelRepository
from app.repositories.category_repository import CategoryRepository
from typing import Dict, List, Optional, Any

# -----------------------------------------------------------------------------
# 2. AI Model Yönetimi
# -----------------------------------------------------------------------------

# 2.1. Model Detayları Getirme
# -----------------------------------------------------------------------------
def get_ai_model_api_details(model_identifier: Any) -> Optional[Dict[str, Any]]:
    """
    Belirli bir AI modelinin API detaylarını model_id veya alternatif
    tanımlayıcılar ile getirir.
    """
    identifier_str = str(model_identifier)
    ai_repo = ModelRepository()
    model = None
    
    if identifier_str.isdigit():
        try:
            model_id = int(identifier_str)
            model = ai_repo.get_model_by_id(model_id, include_api_key=True)
        except ValueError:
            pass # Sayısal değilse veya ID'ye çevrilemiyorsa diğer yöntemlere geç
        except Exception:
            # Model ID ile ararken oluşan hatalar burada ele alınabilir
            # veya None döndürülerek devam edilir.
            pass
            
    if not model and hasattr(ai_repo, 'get_model_by_data_ai_index'):
        try:
            # Bu metodun ModelRepository'de var olduğu varsayılır.
            model = ai_repo.get_model_by_data_ai_index(identifier_str, include_api_key=True)
        except Exception:
            pass

    if not model and identifier_str.startswith('txt_'):
        potential_id_str_from_txt = identifier_str.replace('txt_', '')
        if potential_id_str_from_txt.isdigit():
            try:
                model_id_from_txt = int(potential_id_str_from_txt)
                model = ai_repo.get_model_by_id(model_id_from_txt, include_api_key=True)
            except ValueError:
                pass
            except Exception:
                pass
    
    if not model:
        return None

    # Model entity'sinden gerekli detayları çıkar
    # request_body_template ve api_key alanları için getattr ile güvenli erişim
    model_details = {
        "id": model.id,
        "name": model.name,
        "api_url": model.api_url,
        "request_method": model.request_method,
        "request_headers": getattr(model, 'request_headers', None),
        "request_body_template": getattr(model, 'request_body', None), # Modeldeki request_body alanı şablon olarak kullanılıyor
        "response_path": getattr(model, 'response_path', None),
        "api_key": getattr(model, 'api_key', None) # API anahtarını dahil et
    }
    return model_details
        
# 2.2. Kategori ve Model Listeleme
# -----------------------------------------------------------------------------
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """Tüm AI kategorilerini ve bu kategorilere ait modelleri listeler."""
    category_repo = CategoryRepository()
    model_repo = ModelRepository()
    
    categories_data = []
    try:
        categories = category_repo.get_all_categories()
        
        for category_entity in categories:
            category_dict = {
                "id": category_entity.id,
                "name": category_entity.name,
                "icon": category_entity.icon,
                "models": []
            }
            
            models_in_category = model_repo.get_models_by_category_id(category_entity.id) # API key'ler varsayılan olarak gizli
            
            for model_entity in models_in_category:
                model_dict = {
                    "id": model_entity.id,
                    "name": model_entity.name,
                    "icon": model_entity.icon,
                    "api_url": model_entity.api_url
                    # "description": model_entity.description # Gerekirse eklenebilir
                }
                category_dict["models"].append(model_dict)
                
            categories_data.append(category_dict)
        
        return categories_data
        
    except Exception:
        # Hata durumunda boş liste döndür. Gerçek uygulamada bu hata loglanmalıdır.
        return []

# -----------------------------------------------------------------------------
# 3. Model ve Kategori İşlemleri
# -----------------------------------------------------------------------------

# 3.1. Model Ekleme
# -----------------------------------------------------------------------------
def add_ai_model(category_name: str,
                 model_name: str,
                 model_icon: Optional[str] = None,
                 api_url: Optional[str] = None,
                 description: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 request_method: str = 'POST',
                 request_headers: Optional[Dict[str, Any]] = None,
                 request_body: Optional[Dict[str, Any]] = None,
                 response_path: Optional[str] = None,
                 api_key: Optional[str] = None
                 ) -> tuple[bool, str, Optional[int]]:
    """Veritabanına yeni bir AI modeli ekler. Kategori yoksa oluşturur."""
    model_repo = ModelRepository()
    category_repo = CategoryRepository()
    
    try:
        category_entity = category_repo.get_category_by_name(category_name)
        category_id: Optional[int] = None

        if not category_entity:
            # Kategori yoksa oluştur. CategoryRepository'de uygun bir metot olmalı.
            # Örnek: success, message, cat_id = category_repo.create_category(name=category_name, icon="bi-folder-plus")
            if hasattr(category_repo, 'create_category'):
                 success_cat, msg_cat, new_cat_id = category_repo.create_category(name=category_name, icon="bi-folder-plus")
                 if not success_cat:
                     return False, f"Kategori '{category_name}' oluşturulamadı: {msg_cat}", None
                 category_id = new_cat_id
            elif hasattr(category_repo, 'insert_category'): # Alternatif, ID döndürmeli
                 new_cat_id = category_repo.insert_category(category_name, "bi-folder-plus")
                 if not new_cat_id:
                     return False, f"Kategori '{category_name}' oluşturulamadı (ID alınamadı).", None
                 category_id = new_cat_id
            else:
                return False, "Kategori oluşturma altyapısı eksik.", None
        else:
            category_id = category_entity.id

        if category_id is None: # Kategori ID'si hala None ise bir sorun var demektir.
            return False, "Kategori ID'si belirlenemedi.", None

        success, message, model_id = model_repo.create_model(
            category_id=category_id,
            name=model_name,
            icon=model_icon,
            description=description,
            details=details,
            api_url=api_url,
            request_method=request_method,
            request_headers=request_headers,
            request_body=request_body, # Bu, ModelRepository'de 'request_body_template' olarak kullanılabilir.
            response_path=response_path,
            api_key=api_key
        )
        
        return success, message, model_id
        
    except Exception as e:
        # Gerçek uygulamada bu hata loglanmalıdır.
        return False, f"Model eklenirken beklenmedik bir hata oluştu: {str(e)}", None

# 3.2. Tüm Kullanılabilir Modelleri Getirme
# -----------------------------------------------------------------------------
def get_all_available_models() -> List[Dict[str, Any]]:
    """Tüm mevcut AI modellerini, belirli alanları içeren düz bir liste formatında getirir."""
    model_repo = ModelRepository()
    models_data = []
    try:
        model_entities = model_repo.get_all_models(include_api_keys=False) # API key'leri dahil etme
        
        for model_entity in model_entities:
            data_ai_index_val = None
            if hasattr(model_entity, 'data_ai_index') and model_entity.data_ai_index:
                data_ai_index_val = model_entity.data_ai_index
            else:
                # 'data_ai_index' yoksa veya boşsa, model ID'sini kullanarak bir tanımlayıcı oluştur
                data_ai_index_val = f"id_{model_entity.id}"

            model_dict = {
                "id": model_entity.id,
                "name": model_entity.name,
                "icon": model_entity.icon,
                "data_ai_index": data_ai_index_val,
                "api_url": model_entity.api_url,
                "category_id": model_entity.category_id
            }
            models_data.append(model_dict)
            
        return models_data
        
    except Exception:
        # Gerçek uygulamada bu hata loglanmalıdır.
        return []