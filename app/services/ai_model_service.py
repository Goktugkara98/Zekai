# =============================================================================
# AI Model Servis Modülü (AI Model Service Module)
# =============================================================================
# Bu modül, AI modelleri ve kategorileriyle ilgili servis katmanı işlevlerini
# içerir. Depo (repository) katmanları üzerinden veri işlemlerini yönetir ve
# bu verileri genellikle diğer servis katmanlarına veya rota (route) katmanına
# sunulacak şekilde hazırlar.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Yardımcı Fonksiyonlar (Helper Functions - Eğer varsa, bu dosyada yok)
# 3. Servis Fonksiyonları (Service Functions)
#    3.1. get_ai_model_api_details: Bir AI modelinin API detaylarını getirir.
#    3.2. fetch_ai_categories_from_db: Tüm kategorileri ve modellerini listeler.
#    3.3. add_ai_model: Yeni bir AI modeli ekler (gerekirse kategorisini de oluşturur).
#    3.4. get_all_available_models: Tüm AI modellerini özet bilgilerle listeler.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import json # JSON işlemleri için (bu dosyada doğrudan kullanılmıyor gibi ama gelecekte gerekebilir)
from typing import Dict, List, Optional, Any, Tuple

from flask import current_app # Loglama ve uygulama context'i için

from app.repositories.model_repository import ModelRepository
from app.repositories.category_repository import CategoryRepository
# Entity sınıfları doğrudan burada kullanılmıyor, repository'ler entity nesneleri döndürüyor.
# from app.models.entities.model import Model as AIModelEntity
# from app.models.entities.category import Category as CategoryEntity

# 2. Yardımcı Fonksiyonlar (Helper Functions)
# =============================================================================
# Bu bölüme, bu servis modülüne özel yardımcı fonksiyonlar eklenebilir.
# Örneğin, `admin_dashboard_services.py` dosyasındaki `simple_model_to_dict`
# buraya taşınabilir veya ortak bir `utils` modülünde yer alabilir.
# Şimdilik bu dosyada özel bir yardımcı fonksiyon bulunmuyor.


# 3. Servis Fonksiyonları (Service Functions)
# =============================================================================

# 3.1. Model API Detaylarını Getirme
# -----------------------------------------------------------------------------
def get_ai_model_api_details(model_identifier: Any) -> Optional[Dict[str, Any]]:
    """
    Belirli bir AI modelinin API etkileşimi için gerekli detaylarını getirir.
    Model, ID veya `data_ai_index` gibi alternatif bir tanımlayıcı ile bulunabilir.
    API anahtarını da içerir.

    Args:
        model_identifier: Modelin ID'si (int veya string olarak sayısal) veya
                          alternatif bir tanımlayıcı (örn: 'txt_123', 'data_ai_index_degeri').

    Returns:
        Modelin API detaylarını içeren bir sözlük (api_url, request_method,
        headers, body_template, response_path, api_key vb.) veya model
        bulunamazsa None.
    """
    identifier_str = str(model_identifier).strip()
    ai_repo = ModelRepository()
    model_entity = None # ModelRepository'den dönen entity nesnesi

    try:
        # Öncelikle sayısal bir ID olup olmadığını kontrol et
        if identifier_str.isdigit():
            try:
                model_id = int(identifier_str)
                model_entity = ai_repo.get_model_by_id(model_id, include_api_key=True)
            except ValueError:
                current_app.logger.debug(f"get_ai_model_api_details: '{identifier_str}' sayısal ID'ye dönüştürülemedi.")
                pass # Sayısal değilse diğer yöntemlere geç

        # `data_ai_index` ile arama (eğer ModelRepository'de böyle bir metot varsa)
        if not model_entity and hasattr(ai_repo, 'get_model_by_data_ai_index'):
            try:
                # Bu metodun ModelRepository'de var olduğu ve API key dahil edebildiği varsayılır.
                model_entity = ai_repo.get_model_by_data_ai_index(identifier_str, include_api_key=True)
            except Exception as e:
                current_app.logger.warning(f"get_ai_model_api_details: data_ai_index '{identifier_str}' ile model aranırken hata: {e}")
                pass

        # 'txt_<ID>' formatındaki tanımlayıcılar için (örn: txt_123)
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

        # Model entity'sinden gerekli detayları çıkar
        # getattr ile güvenli erişim, alanlar entity'de olmayabilir veya None olabilir.
        model_details = {
            "id": getattr(model_entity, 'id', None),
            "name": getattr(model_entity, 'name', "N/A"),
            "api_url": getattr(model_entity, 'api_url', None),
            "request_method": getattr(model_entity, 'request_method', 'POST'),
            "request_headers": getattr(model_entity, 'request_headers', {}), # Genellikle dict olmalı
            "request_body_template": getattr(model_entity, 'request_body', {}), # Modeldeki 'request_body' alanı şablon olarak kullanılıyor
            "response_path": getattr(model_entity, 'response_path', None),
            "api_key": getattr(model_entity, 'api_key', None) # API anahtarını dahil et
        }
        current_app.logger.info(f"get_ai_model_api_details: Model '{model_details['name']}' (ID: {model_details['id']}) için API detayları bulundu.")
        return model_details

    except Exception as e:
        current_app.logger.error(f"get_ai_model_api_details: Model '{identifier_str}' için detaylar alınırken beklenmedik hata: {str(e)}", exc_info=True)
        return None

# 3.2. Kategori ve Modelleri Listeleme (Ana Sayfa İçin)
# -----------------------------------------------------------------------------
def fetch_ai_categories_from_db() -> List[Dict[str, Any]]:
    """
    Tüm AI kategorilerini ve bu kategorilere ait modelleri (özet bilgilerle)
    listeler. Genellikle ana sayfa gibi kullanıcı arayüzlerinde kullanılır.

    Returns:
        Her bir kategori için ID, isim, ikon ve o kategoriye ait modellerin
        (ID, isim, ikon, api_url) listesini içeren bir sözlük listesi.
        Hata durumunda boş liste döner.
    """
    category_repo = CategoryRepository()
    model_repo = ModelRepository()
    categories_data_for_display: List[Dict[str, Any]] = []

    try:
        all_categories = category_repo.get_all_categories()
        if not all_categories:
            current_app.logger.info("fetch_ai_categories_from_db: Hiç AI kategorisi bulunamadı.")
            return []

        for category_entity in all_categories:
            category_dict = {
                "id": category_entity.id,
                "name": category_entity.name,
                "icon": category_entity.icon, # Category entity'sinde icon alanı olmalı
                "models": []
            }

            # Kategoriye ait modelleri çek (API anahtarları olmadan)
            models_in_category = model_repo.get_models_by_category_id(category_entity.id, include_api_keys=False)

            for model_entity in models_in_category:
                model_dict = {
                    "id": model_entity.id,
                    "name": model_entity.name,
                    "icon": model_entity.icon, # Model entity'sinde icon alanı olmalı
                    "api_url": model_entity.api_url, # UI'da modelin ne yaptığına dair bir ipucu olabilir
                    # "description": model_entity.description # Gerekirse eklenebilir
                }
                category_dict["models"].append(model_dict)

            categories_data_for_display.append(category_dict)

        current_app.logger.info(f"fetch_ai_categories_from_db: {len(categories_data_for_display)} kategori ve modelleri başarıyla yüklendi.")
        return categories_data_for_display

    except Exception as e:
        current_app.logger.error(f"fetch_ai_categories_from_db: Kategoriler ve modeller yüklenirken hata: {str(e)}", exc_info=True)
        return [] # Hata durumunda boş liste döndür

# 3.3. Yeni AI Modeli Ekleme
# -----------------------------------------------------------------------------
def add_ai_model(category_name: str,
                 model_name: str,
                 model_icon: Optional[str] = None,
                 api_url: Optional[str] = None,
                 description: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None, # Modelin ek JSON detayları
                 request_method: str = 'POST',
                 request_headers: Optional[Dict[str, Any]] = None,
                 request_body: Optional[Dict[str, Any]] = None, # Bu, request_body_template olarak da düşünülebilir
                 response_path: Optional[str] = None,
                 api_key: Optional[str] = None
                 ) -> Tuple[bool, str, Optional[int]]:
    """
    Veritabanına yeni bir AI modeli ekler.
    Eğer belirtilen kategori adı mevcut değilse, varsayılan bir ikonla yeni bir kategori oluşturur.

    Args:
        category_name: Modelin ait olacağı kategori adı.
        model_name: Yeni modelin adı.
        model_icon: Model için ikon (opsiyonel).
        api_url: Modelin API endpoint URL'i (opsiyonel).
        description: Model açıklaması (opsiyonel).
        details: Model hakkında ek JSON tabanlı detaylar (opsiyonel).
        request_method: API isteği için HTTP metodu (varsayılan: 'POST').
        request_headers: API isteği için başlıklar (opsiyonel).
        request_body: API isteği için gövde şablonu (opsiyonel).
        response_path: API yanıtından veri çıkarmak için JSON Path ifadesi (opsiyonel).
        api_key: API anahtarı (opsiyonel).

    Returns:
        Bir tuple: (başarı_durumu: bool, mesaj: str, model_id: Optional[int]).
        Başarı durumunda model_id, eklenen modelin ID'sini içerir.
    """
    model_repo = ModelRepository()
    category_repo = CategoryRepository()
    category_id: Optional[int] = None

    try:
        # Mevcut kategoriyi adına göre bulmaya çalış
        category_entity = category_repo.get_category_by_name(category_name)

        if not category_entity:
            current_app.logger.info(f"add_ai_model: Kategori '{category_name}' bulunamadı, yeni kategori oluşturulacak.")
            # Kategori yoksa, varsayılan bir ikonla oluştur.
            # CategoryRepository'de `create_category` metodu (success, message, id) tuple'ı döndürmeli.
            if hasattr(category_repo, 'create_category'):
                # Varsayılan ikon, örneğin:
                default_category_icon = "bi-folder-plus" # Veya None
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
                # Eğer CategoryRepository'de create_category metodu yoksa, bu bir konfigürasyon sorunudur.
                error_msg = "Kategori oluşturma altyapısı (CategoryRepository.create_category) eksik."
                current_app.logger.error(f"add_ai_model: {error_msg}")
                return False, error_msg, None
        else:
            category_id = category_entity.id
            current_app.logger.info(f"add_ai_model: Mevcut kategori '{category_name}' (ID: {category_id}) kullanılacak.")

        if category_id is None: # Bu durumun oluşmaması gerekir ama bir güvenlik kontrolü
            error_msg = "Kategori ID'si belirlenemedi."
            current_app.logger.error(f"add_ai_model: {error_msg}")
            return False, error_msg, None

        # Yeni AI modelini oluştur
        # ModelRepository.create_model metodu (success, message, model_id) tuple'ı döndürmeli.
        success_model, msg_model, new_model_id = model_repo.create_model(
            category_id=category_id,
            name=model_name,
            icon=model_icon,
            description=description,
            details=details,
            api_url=api_url,
            request_method=request_method.upper(),
            request_headers=request_headers,
            request_body=request_body,
            response_path=response_path,
            api_key=api_key
        )

        if success_model:
            current_app.logger.info(f"add_ai_model: Yeni AI modeli '{model_name}' (ID: {new_model_id}) başarıyla eklendi. Mesaj: {msg_model}")
        else:
            current_app.logger.error(f"add_ai_model: AI modeli '{model_name}' eklenemedi. Mesaj: {msg_model}")

        return success_model, msg_model, new_model_id

    except Exception as e:
        current_app.logger.error(f"add_ai_model: Model '{model_name}' eklenirken beklenmedik bir hata oluştu: {str(e)}", exc_info=True)
        return False, f"Model eklenirken sunucuda beklenmedik bir hata oluştu: {str(e)}", None

# 3.4. Tüm Kullanılabilir Modelleri Getirme (Özet Liste)
# -----------------------------------------------------------------------------
def get_all_available_models() -> List[Dict[str, Any]]:
    """
    Tüm mevcut (aktif/kullanılabilir) AI modellerini, belirli özet alanları
    içeren düz bir liste formatında getirir. API anahtarlarını içermez.
    Bu fonksiyon, örneğin bir model seçme listesi için kullanılabilir.

    Returns:
        Her model için ID, isim, ikon, data_ai_index, api_url ve category_id
        içeren bir sözlük listesi. Hata durumunda boş liste döner.
    """
    model_repo = ModelRepository()
    models_summary_data: List[Dict[str, Any]] = []
    try:
        # `get_all_models` API key'leri varsayılan olarak gizler veya `include_api_keys=False` ile çağrılabilir.
        # Ayrıca, sadece "aktif" modelleri çekmek için repository'de bir filtreleme mekanizması olabilir.
        model_entities = model_repo.get_all_models(include_api_keys=False) # API key'leri dahil etme

        if not model_entities:
            current_app.logger.info("get_all_available_models: Hiç AI modeli bulunamadı.")
            return []

        for model_entity in model_entities:
            # `data_ai_index` alanı model entity'sinde olabilir veya burada oluşturulabilir.
            # Bu alan, UI'da modeli benzersiz bir şekilde tanımlamak için kullanılabilir.
            data_ai_index_val: str
            if hasattr(model_entity, 'data_ai_index') and model_entity.data_ai_index:
                data_ai_index_val = str(model_entity.data_ai_index)
            else:
                # 'data_ai_index' yoksa veya boşsa, model ID'sini kullanarak bir tanımlayıcı oluştur
                data_ai_index_val = f"id_{model_entity.id}"

            model_dict = {
                "id": model_entity.id,
                "name": model_entity.name,
                "icon": model_entity.icon,
                "data_ai_index": data_ai_index_val, # UI'da kullanılmak üzere
                "api_url": model_entity.api_url, # Bilgilendirme amaçlı
                "category_id": model_entity.category_id
                # "description": model_entity.description # Gerekirse eklenebilir
            }
            models_summary_data.append(model_dict)

        current_app.logger.info(f"get_all_available_models: {len(models_summary_data)} AI modeli başarıyla yüklendi.")
        return models_summary_data

    except Exception as e:
        current_app.logger.error(f"get_all_available_models: Modeller yüklenirken hata: {str(e)}", exc_info=True)
        return [] # Hata durumunda boş liste döndür
