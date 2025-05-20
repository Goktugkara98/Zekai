# =============================================================================
# AI Model Service Module
# =============================================================================
# İçindekiler:
# 1. Imports
# 2. Logger Yapılandırması ve Dekoratör
# 3. AI Model Yönetimi
#    3.1. Model Detayları Getirme
#    3.2. Kategori ve Model Listeleme
# 4. Yardımcı Fonksiyonlar (Model Ekleme, Tüm Modelleri Getirme vb.)
#    4.1. Model Ekleme
#    4.2. Tüm Modelleri Getirme
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------
from app.repositories.model_repository import ModelRepository
from app.repositories.category_repository import CategoryRepository
from typing import Dict, List, Optional, Any
import logging
import functools
import json # Argümanları daha okunaklı loglamak için

# 2. Logger Yapılandırması ve Dekoratör
# =============================================================================
logging.basicConfig(
    level=logging.DEBUG, # Geliştirme aşamasında DEBUG iyi bir seçenektir
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_service_call(func):
    """
    Servis fonksiyonlarının çağrılarını, argümanlarını ve sonuçlarını/hatalarını
    loglayan bir dekoratör.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # Argümanları loglarken hassas verilere dikkat edin.
        # repr() veya str() ile güvenli bir şekilde loglamaya çalışın.
        # Karmaşık nesneler için özel bir serileştirme gerekebilir.
        args_summary = []
        try:
            for i, arg in enumerate(args):
                if hasattr(arg, '__class__') and arg.__class__.__name__ == 'DataFrame': # Pandas DataFrame ise
                    args_summary.append(f"args[{i}]: DataFrame(shape={arg.shape if hasattr(arg, 'shape') else 'N/A'})")
                elif isinstance(arg, (list, dict)) and len(json.dumps(arg, default=str)) > 100: # Çok büyükse kısalt
                     args_summary.append(f"args[{i}]: {type(arg).__name__} (kısaltıldı, ilk 100 char): {str(arg)[:100]}...")
                else:
                    args_summary.append(f"args[{i}]: {str(arg)}")
        except Exception: # str() veya repr() başarısız olursa
            args_summary.append(f"args[{i}]: (loglanamayan argüman)")
            
        kwargs_summary = {}
        try:
            for k, v in kwargs.items():
                if hasattr(v, '__class__') and v.__class__.__name__ == 'DataFrame':
                    kwargs_summary[k] = f"DataFrame(shape={v.shape if hasattr(v, 'shape') else 'N/A'})"
                elif isinstance(v, (list, dict)) and len(json.dumps(v, default=str)) > 100:
                    kwargs_summary[k] = f"{type(v).__name__} (kısaltıldı, ilk 100 char): {str(v)[:100]}..."
                else:
                    kwargs_summary[k] = str(v)
        except Exception:
            kwargs_summary[k] = "(loglanamayan kwarg)"

        separator_line = f"{'—'*25} SERVICE CALL: {func_name} {'—'*25}"
        logger.debug(f"\n{separator_line}")
        if args_summary: logger.debug(f"   Args: {args_summary}")
        if kwargs_summary: logger.debug(f"   Kwargs: {kwargs_summary}")
        logger.debug("-" * len(separator_line)) # İç ayraç

        try:
            result = func(*args, **kwargs)
            # Sonucu loglamak isteğe bağlıdır ve büyük sonuçlar için dikkatli olunmalıdır.
            # logger.debug(f"   Result (type: {type(result).__name__}, value: {str(result)[:200]}...)") # İlk 200 karakter
            return result
        except Exception as e:
            logger.error(f"SERVİS HATASI ({func_name}): {type(e).__name__} - {e}", exc_info=True)
            raise # Hatanın yukarıya yayılmasına izin ver
        finally:
            logger.debug(f"{'—'*25} END SERVICE: {func_name} {'—'*25}\n")
    return wrapper

# -----------------------------------------------------------------------------
# 3. AI Model Yönetimi
# -----------------------------------------------------------------------------

# 3.1. Model Detayları Getirme
# -----------------------------------------------------------------------------
@log_service_call
def get_ai_model_api_details(model_identifier: Any) -> Optional[Dict[str, Any]]: # Tip Any olarak güncellendi
    """
    Belirli bir AI modelinin API detaylarını model_id veya data_ai_index (varsayılan) ile getirir.
    Not: ModelRepository'de 'get_model_by_data_ai_index' metodunun var olduğu varsayılır.
    """
    # Fonksiyona gelen tanımlayıcının tipini logla
    logger.info(f"AI model API detayları isteniyor: '{model_identifier}' (gelen tip: {type(model_identifier).__name__})")
    
    # model_identifier'ı string'e çevirerek .isdigit() ve diğer string metotlarının güvenle kullanılmasını sağla
    # Bu, gelen değer int olsa bile .isdigit() çağrısının hata vermesini engeller.
    identifier_str = str(model_identifier)

    ai_repo = ModelRepository() 
    model = None
    
    # Önce model_id olarak (sayısal ise) deneyelim
    # Artık identifier_str (her zaman string olan kopya) üzerinde çalışıyoruz
    if identifier_str.isdigit(): 
        try:
            model_id = int(identifier_str)
            logger.debug(f"'{identifier_str}' ID'si ile model aranıyor...")
            model = ai_repo.get_model_by_id(model_id)
            if model:
                logger.info(f"Model ID '{model_id}' ile bulundu: {model.name}")
        except ValueError: 
            logger.warning(f"'{identifier_str}' sayısal olmasına rağmen ID'ye çevrilemedi.")
        except Exception as e_id: 
            logger.error(f"Model ID '{identifier_str}' ile aranırken hata: {e_id}", exc_info=True)
            
    # Eğer ID ile bulunamadıysa veya sayısal değilse, data_ai_index olarak deneyelim
    if not model:
        logger.debug(f"'{identifier_str}' data_ai_index'i ile model aranıyor...")
        try:
            if hasattr(ai_repo, 'get_model_by_data_ai_index'):
                model = ai_repo.get_model_by_data_ai_index(identifier_str) # identifier_str kullan
                if model:
                    logger.info(f"Model data_ai_index '{identifier_str}' ile bulundu: {model.name}")
            else:
                logger.warning("'get_model_by_data_ai_index' metodu ModelRepository'de bulunamadı.")
        except Exception as e_index:
            logger.error(f"Model data_ai_index '{identifier_str}' ile aranırken hata: {e_index}", exc_info=True)

    # 'txt_' öneki ile ID denemesi
    if not model and identifier_str.startswith('txt_'):
        potential_id_str_from_txt = identifier_str.replace('txt_', '') # identifier_str kullan
        if potential_id_str_from_txt.isdigit():
            try:
                model_id_from_txt = int(potential_id_str_from_txt)
                logger.debug(f"'{identifier_str}' için 'txt_' öneki kaldırılarak ID '{model_id_from_txt}' ile model aranıyor...")
                model = ai_repo.get_model_by_id(model_id_from_txt)
                if model:
                    logger.info(f"Model (txt_ prefixli) ID '{model_id_from_txt}' ile bulundu: {model.name}")
            except ValueError:
                logger.warning(f"'{potential_id_str_from_txt}' (txt_ sonrası) ID'ye çevrilemedi.")
            except Exception as e_txt_id:
                 logger.error(f"Model (txt_ prefixli) ID '{potential_id_str_from_txt}' ile aranırken hata: {e_txt_id}", exc_info=True)
    
    if not model:
        logger.warning(f"Model '{identifier_str}' için hiçbir yöntemle detay bulunamadı.")
        return None

    model_details = {
        "id": model.id,
        "name": model.name,
        "api_url": model.api_url,
        "request_method": model.request_method,
        "request_headers": model.request_headers, 
        "request_body_template": model.request_body, 
        "response_path": model.response_path
    }
    logger.info(f"Model '{model.name}' için API detayları başarıyla hazırlandı.")
    logger.debug(f"Döndürülen model detayları: {model_details}")
    return model_details
        
# -----------------------------------------------------------------------------
# 2.2. Kategori ve Model Listeleme
# -----------------------------------------------------------------------------
@log_service_call
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """Tüm AI kategorilerini ve bu kategorilere ait modelleri listeler."""
    logger.info("Tüm AI kategorileri ve ilişkili modelleri veritabanından getirme işlemi başlatıldı.")
    category_repo = CategoryRepository()
    model_repo = ModelRepository()
    
    categories_data = []
    try:
        categories = category_repo.get_all_categories()
        logger.info(f"Toplam {len(categories)} kategori bulundu.")
        
        for i, category_entity in enumerate(categories):
            logger.debug(f"Kategori {i+1}/{len(categories)} işleniyor: ID={category_entity.id}, Ad='{category_entity.name}'")
            
            category_dict = {
                "id": category_entity.id,
                "name": category_entity.name,
                "icon": category_entity.icon,
                "models": []
            }
            
            # İlgili kategori için modelleri getir
            # ModelRepository.get_models_by_category_id API anahtarlarını varsayılan olarak gizler.
            models_in_category = model_repo.get_models_by_category_id(category_entity.id)
            logger.debug(f"   '{category_entity.name}' kategorisi için {len(models_in_category)} model bulundu.")
            
            for j, model_entity in enumerate(models_in_category):
                # API URL'sindeki tırnak işaretlerini JSON için escape etme (Bu frontend'de parse edilecekse önemli olabilir)
                # Ancak, bu genellikle frontend tarafında veya JSON serileştirme sırasında otomatik halledilir.
                # api_url = model_entity.api_url
                # if api_url and '"' in api_url:
                #     logger.warning(f"Model '{model_entity.name}' API URL'sinde çift tırnak içeriyor: '{api_url}'. Escape ediliyor.")
                #     api_url = api_url.replace('"', '\\"') 
                
                model_dict = {
                    "id": model_entity.id, # Frontend'de seçtirmek için ID önemli
                    "name": model_entity.name,
                    "icon": model_entity.icon,
                    "api_url": model_entity.api_url # Ham URL'yi bırakmak daha iyi olabilir.
                    # "description": model_entity.description # Gerekirse eklenebilir
                }
                category_dict["models"].append(model_dict)
                logger.debug(f"      Model eklendi: ID={model_entity.id}, Ad='{model_entity.name}'")
                
            categories_data.append(category_dict)
        
        logger.info(f"Toplam {len(categories_data)} kategori (modelleriyle birlikte) başarıyla listelendi.")
        return categories_data
        
    except Exception as e:
        logger.error(f"Kategoriler ve modeller listelenirken genel bir hata oluştu: {e}", exc_info=True)
        return [] # Hata durumunda boş liste döndür

# -----------------------------------------------------------------------------
# 4. Yardımcı Fonksiyonlar (Model Ekleme, Tüm Modelleri Getirme vb.)
# -----------------------------------------------------------------------------

# 4.1. Model Ekleme
# Not: Bu fonksiyonun argümanları ModelRepository.create_model ile tam uyumlu olmalı
# veya burada bir dönüşüm yapılmalı. Mevcut ModelRepository.create_model daha fazla parametre bekliyor.
# data_ai_index gibi bir alan Model entity'sinde veya DB'de yoksa bu fonksiyon çalışmaz.
# -----------------------------------------------------------------------------
@log_service_call
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
                 # data_ai_index: str, # Bu parametre ModelRepository'de yok, kaldırıldı veya eklenmeli
                 ) -> tuple[bool, str, Optional[int]]:
    """Veritabanına yeni bir AI modeli ekler. Kategori yoksa oluşturur."""
    logger.info(f"Yeni AI modeli ekleme isteği: Model Adı='{model_name}', Kategori Adı='{category_name}'")
    model_repo = ModelRepository()
    category_repo = CategoryRepository() # Kategori işlemleri için doğru depo
    
    try:
        # Kategori var mı kontrol et, yoksa oluştur
        category_entity = category_repo.get_category_by_name(category_name)
        if not category_entity:
            logger.info(f"'{category_name}' adında kategori bulunamadı, oluşturuluyor...")
            # Varsayılan bir ikonla kategori oluşturma
            # CategoryRepository'de insert_category veya create_category gibi bir metod olmalı.
            # Örnek: success, message, cat_id = category_repo.create_category(name=category_name, icon="bi-folder-plus")
            # Bu metodun var olduğunu ve ID döndürdüğünü varsayalım.
            # Geçici olarak ModelRepository'deki (eski kodunuzdaki) mantığı kullanıyoruz,
            # ama bu CategoryRepository'ye taşınmalı.
            if hasattr(category_repo, 'create_category'): # Tercih edilen
                 success, msg, new_cat_id = category_repo.create_category(name=category_name, icon="bi-folder-plus")
                 if not success:
                     logger.error(f"Kategori '{category_name}' oluşturulamadı: {msg}")
                     return False, f"Kategori '{category_name}' oluşturulamadı: {msg}", None
                 category_id = new_cat_id
                 logger.info(f"Kategori '{category_name}' başarıyla oluşturuldu. ID: {category_id}")
            elif hasattr(category_repo, 'insert_category'): # Alternatif
                 new_cat_id = category_repo.insert_category(category_name, "bi-folder-plus") # Bu metod ID döndürmeli
                 if not new_cat_id:
                     logger.error(f"Kategori '{category_name}' oluşturulamadı (insert_category ID döndürmedi).")
                     return False, f"Kategori '{category_name}' oluşturulamadı.", None
                 category_id = new_cat_id
                 logger.info(f"Kategori '{category_name}' başarıyla oluşturuldu. ID: {category_id}")
            else:
                logger.error("CategoryRepository'de kategori oluşturma metodu (create_category veya insert_category) bulunamadı.")
                return False, "Kategori oluşturma altyapısı eksik.", None
        else:
            category_id = category_entity.id
            logger.info(f"Mevcut kategori '{category_name}' kullanılacak. ID: {category_id}")

        # Modeli ekle
        # ModelRepository.create_model çağrısı orijinaldeki gibi tüm parametreleri alacak şekilde güncellendi.
        success, message, model_id = model_repo.create_model(
            category_id=category_id,
            name=model_name,
            icon=model_icon,
            description=description,
            details=details,
            api_url=api_url,
            request_method=request_method,
            request_headers=request_headers,
            request_body=request_body,
            response_path=response_path,
            api_key=api_key
        )
        
        if success:
            logger.info(f"Model '{model_name}' başarıyla eklendi. ID: {model_id}. Mesaj: {message}")
        else:
            logger.error(f"Model '{model_name}' eklenemedi. Mesaj: {message}")
            
        return success, message, model_id
        
    except Exception as e:
        logger.critical(f"Model ekleme sırasında beklenmedik kritik hata: {e}", exc_info=True)
        return False, f"Model eklenirken beklenmedik bir hata oluştu: {str(e)}", None

# -----------------------------------------------------------------------------
# 4.2. Tüm Modelleri Getirme
# Not: Model entity'sinde 'data_ai_index' alanı yoksa bu fonksiyon hata verir.
# Bu alanın ModelRepository.get_all_models tarafından döndürülen dict'lerde olduğunu varsayıyoruz.
# -----------------------------------------------------------------------------
@log_service_call
def get_all_available_models() -> List[Dict[str, Any]]:
    """Tüm mevcut AI modellerini, belirli alanları içeren düz bir liste formatında getirir."""
    logger.info("Tüm mevcut AI modelleri listeleniyor.")
    model_repo = ModelRepository()
    
    models_data = []
    try:
        # ModelRepository.get_all_models() Model nesneleri listesi döndürür.
        # API anahtarlarını varsayılan olarak gizler.
        model_entities = model_repo.get_all_models(include_api_keys=False) # API anahtarlarını dahil etme
        logger.info(f"Toplam {len(model_entities)} model entity'si bulundu.")
        
        for model_entity in model_entities:
            # data_ai_index alanı Model entity'sinde veya DB'de tanımlı olmalı.
            # Eğer yoksa, bu model_entity.data_ai_index AttributeError verecektir.
            # Şimdilik varsayılan bir değer atayalım veya loglayalım.
            data_ai_index_val = None
            if hasattr(model_entity, 'data_ai_index'):
                data_ai_index_val = model_entity.data_ai_index
            else:
                # logger.debug(f"Model '{model_entity.name}' (ID: {model_entity.id}) için 'data_ai_index' alanı bulunamadı.")
                # Alternatif olarak, model ID'sini kullanabiliriz:
                data_ai_index_val = f"id_{model_entity.id}"


            model_dict = {
                "id": model_entity.id,
                "name": model_entity.name,
                "icon": model_entity.icon,
                "data_ai_index": data_ai_index_val, # Bu alanın varlığını kontrol et
                "api_url": model_entity.api_url,
                "category_id": model_entity.category_id # Ek bilgi olarak faydalı olabilir
            }
            models_data.append(model_dict)
            logger.debug(f"   Model listeye eklendi: ID={model_entity.id}, Ad='{model_entity.name}'")
            
        logger.info(f"Toplam {len(models_data)} model başarıyla listelendi.")
        return models_data
        
    except Exception as e:
        logger.error(f"Tüm modeller listelenirken genel bir hata oluştu: {e}", exc_info=True)
        return []
