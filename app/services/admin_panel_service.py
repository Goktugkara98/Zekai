# =============================================================================
# Admin Paneli Servis Modülü (Admin Panel Service Module)
# =============================================================================
# Bu modül, yönetici paneliyle ilgili iş mantığını ve servis fonksiyonlarını içerir.
# Rota (route) katmanından gelen istekleri alır, gerekli işlemleri yapar
# (genellikle repository katmanını kullanarak) ve sonuçları rota katmanına döndürür.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Kimlik Doğrulama Servisleri (Authentication Services)
#    2.1. is_admin_authenticated     : Admin kullanıcısının kimliğinin doğrulanıp doğrulanmadığını kontrol eder.
#    2.2. verify_admin_credentials   : (Örnek) Admin kimlik bilgilerini doğrular (login için).
# 3. Kategori Yönetimi Servisleri (Category Management Services)
#    3.1. get_all_categories_with_model_counts : Tüm kategorileri model sayılarıyla birlikte getirir.
#    3.2. get_category_details_with_models     : Belirli bir kategorinin detaylarını ve modellerini getirir.
#    3.3. create_new_category                  : Yeni bir kategori oluşturur.
#    3.4. update_existing_category             : Mevcut bir kategoriyi günceller.
#    3.5. delete_existing_category             : Bir kategoriyi siler.
# 4. Model Yönetimi Servisleri (Model Management Services)
#    4.1. get_all_models_with_category_info    : Tüm modelleri kategori bilgileriyle birlikte getirir.
#    4.2. get_model_details_with_category      : Belirli bir modelin detaylarını kategori bilgisiyle getirir.
#    4.3. create_new_model                     : Yeni bir AI modeli oluşturur.
#    4.4. update_existing_model                : Mevcut bir AI modelini günceller.
#    4.5. delete_existing_model                : Bir AI modelini siler.
#    4.6. duplicate_existing_model             : Mevcut bir AI modelini çoğaltır.
# 5. Kullanıcı Mesajları Servisleri (User Message Services)
#    5.1. get_paginated_user_messages          : Kullanıcı mesajlarını sayfalamalı olarak getirir.
#    5.2. get_total_user_message_count       : Toplam kullanıcı mesajı sayısını getirir.
# 6. Dashboard Servisleri (Dashboard Services)
#    6.1. get_admin_dashboard_statistics       : Admin paneli dashboard için istatistikleri getirir.
# 7. Yardımcı Servisler (Utility Services)
#    7.1. get_available_icons_list             : Kullanılabilir ikonların listesini döndürür.
#
# Not: Orijinal koddaki @require_admin_auth decorator'ı kaldırıldı,
#      çünkü bu decorator Flask rotaları (@admin_bp.route) üzerinde kullanılmalıdır,
#      servis fonksiyonları üzerinde değil. Servis fonksiyonları çağrılmadan önce
#      rota seviyesinde kimlik doğrulaması yapılmış olmalıdır.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from flask import session # Admin kimlik doğrulaması için session kullanımı
from typing import Dict, List, Optional, Any, Tuple
import os # Ortam değişkenleri için (şifre yönetimi vb.)
# from werkzeug.security import check_password_hash # Eğer hash'li şifre kullanılacaksa

# Yeni Repository sınıflarını import et
from app.repositories import AdminRepository, UserMessageRepository # UserMessageRepository eklendi
# from app.models.admin_panel_database import AdminRepository as OldAdminRepository # ESKİ KULLANIM, KALDIRILDI

# print("DEBUG: admin_panel_service.py yükleniyor.")

# 2. Kimlik Doğrulama Servisleri (Authentication Services)
# =============================================================================

# 2.1. is_admin_authenticated
# -----------------------------------------------------------------------------
def is_admin_authenticated() -> bool:
    """
    Admin kullanıcısının oturumda kimliğinin doğrulanıp doğrulanmadığını kontrol eder.
    Returns:
        bool: Admin giriş yapmışsa True, aksi takdirde False.
    """
    authenticated = session.get('is_admin', False)
    # print(f"DEBUG (Servis): Admin kimlik durumu kontrol ediliyor: {authenticated}")
    return authenticated

# 2.2. verify_admin_credentials (Örnek Login Servisi)
# -----------------------------------------------------------------------------
def verify_admin_credentials(username: str, password_attempt: str) -> bool:
    """
    Sağlanan yönetici kimlik bilgilerini doğrular.
    Üretimde, şifreler güvenli bir şekilde (hash'lenmiş olarak) saklanmalı ve
    ortam değişkenlerinden okunmalıdır.
    Args:
        username (str): Kullanıcı tarafından girilen kullanıcı adı.
        password_attempt (str): Kullanıcı tarafından girilen şifre.
    Returns:
        bool: Kimlik bilgileri doğruysa True, aksi takdirde False.
    """
    # print(f"DEBUG (Servis): Admin kimlik bilgileri doğrulanıyor: KullanıcıAdı='{username}'")
    admin_username_env = os.environ.get('ADMIN_USERNAME', 'admin') # Varsayılan
    admin_password_env = os.environ.get('ADMIN_PASSWORD', 'zekaiadmin') # TEST AMAÇLI! Üretimde KULLANILMAMALI!
    # admin_password_hash_env = os.environ.get('ADMIN_PASSWORD_HASH') # Üretimde bu kullanılmalı

    # Üretim için:
    # if username == admin_username_env and admin_password_hash_env and \
    #    check_password_hash(admin_password_hash_env, password_attempt):
    #     return True

    # Sadece geliştirme/test için düz metin karşılaştırması:
    if username == admin_username_env and password_attempt == admin_password_env:
        # print("DEBUG (Servis): Admin kimlik bilgileri doğrulandı.")
        return True

    # print("DEBUG (Servis): Admin kimlik bilgileri geçersiz.")
    return False

# 3. Kategori Yönetimi Servisleri (Category Management Services)
# =============================================================================
# Bu servis fonksiyonları, AdminRepository (yeni olan) üzerinden işlemleri yapar.

# 3.1. get_all_categories_with_model_counts
# -----------------------------------------------------------------------------
def get_all_categories_with_model_counts() -> List[Dict[str, Any]]:
    """
    Tüm AI kategorilerini, her bir kategori için model sayısıyla birlikte getirir.
    Returns:
        List[Dict[str, Any]]: Kategori listesi. Hata durumunda boş liste.
    """
    # print("DEBUG (Servis): Tüm kategoriler model sayılarıyla birlikte alınıyor...")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        # Yeni AdminRepository.get_all_categories_with_models zaten bu işi yapıyor.
        categories = admin_repo.get_all_categories_with_models()
        # print(f"DEBUG (Servis): {len(categories)} kategori bulundu.")
        return categories
    except Exception as e:
        # print(f"HATA (Servis): Kategoriler alınırken: {e}")
        return []

# 3.2. get_category_details_with_models
# -----------------------------------------------------------------------------
def get_category_details_with_models(category_id: int) -> Optional[Dict[str, Any]]:
    """
    Belirli bir kategorinin detaylarını ve bu kategoriye ait modelleri getirir.
    Args:
        category_id (int): Kategori ID'si.
    Returns:
        Optional[Dict[str, Any]]: Kategori detayları veya bulunamazsa None.
    """
    # print(f"DEBUG (Servis): Kategori detayları alınıyor: ID={category_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        # Yeni AdminRepository.get_category_details zaten bu işi yapıyor.
        category = admin_repo.get_category_details(category_id)
        if not category:
            # print(f"DEBUG (Servis): ID'si {category_id} olan kategori bulunamadı.")
            return None
        # print(f"DEBUG (Servis): Kategori '{category.get('name')}' detayları bulundu.")
        return category
    except Exception as e:
        # print(f"HATA (Servis): Kategori detayları alınırken: {e}")
        return None

# 3.3. create_new_category
# -----------------------------------------------------------------------------
def create_new_category(name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
    """
    Yeni bir AI kategorisi oluşturur.
    Args:
        name (str): Kategori adı.
        icon (str): Kategori ikonu.
    Returns:
        Tuple[bool, str, Optional[int]]: (başarı durumu, mesaj, yeni kategori ID'si)
    """
    # print(f"DEBUG (Servis): Yeni kategori oluşturuluyor: Ad='{name}', İkon='{icon}'")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        success, message, category_id = admin_repo.create_category(name, icon)
        # print(f"DEBUG (Servis): Kategori oluşturma sonucu: Başarı={success}, Mesaj='{message}', ID={category_id}")
        return success, message, category_id
    except Exception as e:
        # print(f"HATA (Servis): Kategori oluşturulurken: {e}")
        return False, f"Kategori oluşturulurken beklenmedik bir hata oluştu: {str(e)}", None

# 3.4. update_existing_category
# -----------------------------------------------------------------------------
def update_existing_category(category_id: int, name: str, icon: str) -> Tuple[bool, str]:
    """
    Mevcut bir AI kategorisini günceller.
    Args:
        category_id (int): Güncellenecek kategori ID'si.
        name (str): Yeni kategori adı.
        icon (str): Yeni kategori ikonu.
    Returns:
        Tuple[bool, str]: (başarı durumu, mesaj)
    """
    # print(f"DEBUG (Servis): Kategori güncelleniyor: ID={category_id}, Ad='{name}'")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        success, message = admin_repo.update_category(category_id, name, icon)
        # print(f"DEBUG (Servis): Kategori güncelleme sonucu: Başarı={success}, Mesaj='{message}'")
        return success, message
    except Exception as e:
        # print(f"HATA (Servis): Kategori güncellenirken: {e}")
        return False, f"Kategori güncellenirken beklenmedik bir hata oluştu: {str(e)}"

# 3.5. delete_existing_category
# -----------------------------------------------------------------------------
def delete_existing_category(category_id: int) -> Tuple[bool, str]:
    """
    Bir AI kategorisini siler.
    Args:
        category_id (int): Silinecek kategori ID'si.
    Returns:
        Tuple[bool, str]: (başarı durumu, mesaj)
    """
    # print(f"DEBUG (Servis): Kategori siliniyor: ID={category_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        success, message = admin_repo.delete_category(category_id)
        # print(f"DEBUG (Servis): Kategori silme sonucu: Başarı={success}, Mesaj='{message}'")
        return success, message
    except Exception as e:
        # print(f"HATA (Servis): Kategori silinirken: {e}")
        return False, f"Kategori silinirken beklenmedik bir hata oluştu: {str(e)}"

# 4. Model Yönetimi Servisleri (Model Management Services)
# =============================================================================

# 4.1. get_all_models_with_category_info
# -----------------------------------------------------------------------------
def get_all_models_with_category_info() -> List[Dict[str, Any]]:
    """
    Tüm AI modellerini, ait oldukları kategori bilgileriyle birlikte getirir.
    Returns:
        List[Dict[str, Any]]: Model listesi. Hata durumunda boş liste.
    """
    # print("DEBUG (Servis): Tüm modeller kategori bilgileriyle alınıyor...")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        # Yeni AdminRepository.get_all_categories_with_models() zaten modelleri de içeriyor.
        # Eğer sadece model listesi ve her model için kategori adı gerekiyorsa,
        # AdminRepository'de buna özel bir metot (örn: get_all_models_with_category_name) olabilir.
        # Şimdilik, tüm kategorileri alıp içinden modelleri çekebiliriz veya AdminRepo'ya yeni metot ekleyebiliriz.

        # Geçici çözüm: Tüm kategorileri al ve modelleri düz bir listeye çıkar.
        # Bu, çok fazla model varsa verimsiz olabilir.
        all_categories_data = admin_repo.get_all_categories_with_models()
        all_models = []
        for cat_data in all_categories_data:
            for model_data in cat_data.get('models', []):
                model_data['category_name'] = cat_data.get('name') # Kategori adını ekle
                model_data['category_icon'] = cat_data.get('icon') # Kategori ikonunu ekle
                all_models.append(model_data)
        # print(f"DEBUG (Servis): Toplam {len(all_models)} model bulundu.")
        return all_models
    except Exception as e:
        # print(f"HATA (Servis): Modeller alınırken: {e}")
        return []

# 4.2. get_model_details_with_category
# -----------------------------------------------------------------------------
def get_model_details_with_category(model_id: int) -> Optional[Dict[str, Any]]:
    """
    Belirli bir AI modelinin detaylarını, ait olduğu kategori bilgisiyle birlikte getirir.
    Args:
        model_id (int): Model ID'si.
    Returns:
        Optional[Dict[str, Any]]: Model detayları veya bulunamazsa None.
    """
    # print(f"DEBUG (Servis): Model detayları alınıyor: ID={model_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        # AdminRepository.get_model_details zaten kategori adını ekliyor.
        model = admin_repo.get_model_details(model_id)
        if not model:
            # print(f"DEBUG (Servis): ID'si {model_id} olan model bulunamadı.")
            return None
        # print(f"DEBUG (Servis): Model '{model.get('name')}' detayları bulundu.")
        return model
    except Exception as e:
        # print(f"HATA (Servis): Model detayları alınırken: {e}")
        return None

# 4.3. create_new_model
# -----------------------------------------------------------------------------
def create_new_model(category_id: int, name: str,
                     icon: Optional[str] = None, api_url: Optional[str] = None,
                     data_ai_index: Optional[str] = None,
                     description: Optional[str] = None,
                     details: Optional[Dict] = None,
                     image_filename: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
    """
    Yeni bir AI modeli oluşturur.
    Returns:
        Tuple[bool, str, Optional[int]]: (başarı durumu, mesaj, yeni model ID'si)
    """
    # print(f"DEBUG (Servis): Yeni model oluşturuluyor: Ad='{name}', KategoriID={category_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        # AdminRepository.create_model, ModelRepository.create_model'i çağırır.
        # ModelRepository.create_model (bool, str, Optional[int]) döndürür.
        # AdminRepository.create_model (bool, str) döndürüyordu, bunu düzeltmek gerekebilir.
        # Şimdilik AdminRepository'nin (bool, str, Optional[int]) döndürdüğünü varsayalım.
        # Veya AdminRepository.create_model'in dönüşünü burada uyarlayalım.

        # Orijinal admin_panel_database.py'deki AdminRepository.create_model (bool, str) döndürüyordu.
        # Yeni app.repositories.AdminRepository.create_model (bool, str, Optional[int]) döndürüyor.
        # Bu servis fonksiyonu da (bool, str, Optional[int]) döndürmeli.
        success, message, model_id = admin_repo.create_model(
            category_id=category_id, name=name, icon=icon, api_url=api_url,
            data_ai_index=data_ai_index, description=description, details=details,
            image_filename=image_filename
        )
        # print(f"DEBUG (Servis): Model oluşturma sonucu: Başarı={success}, Mesaj='{message}', ID={model_id}")
        return success, message, model_id
    except Exception as e:
        # print(f"HATA (Servis): Model oluşturulurken: {e}")
        return False, f"Model oluşturulurken beklenmedik bir hata oluştu: {str(e)}", None


# 4.4. update_existing_model
# -----------------------------------------------------------------------------
def update_existing_model(model_id: int, name: Optional[str] = None,
                          category_id: Optional[int] = None,
                          icon: Optional[str] = None, api_url: Optional[str] = None,
                          data_ai_index: Optional[str] = None,
                          description: Optional[str] = None,
                          details: Optional[Dict] = None,
                          image_filename: Optional[str] = None) -> Tuple[bool, str]:
    """
    Mevcut bir AI modelini günceller.
    Returns:
        Tuple[bool, str]: (başarı durumu, mesaj)
    """
    # print(f"DEBUG (Servis): Model güncelleniyor: ID={model_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        success, message = admin_repo.update_model(
            model_id=model_id, name=name, category_id=category_id, icon=icon,
            api_url=api_url, data_ai_index=data_ai_index, description=description,
            details=details, image_filename=image_filename
        )
        # print(f"DEBUG (Servis): Model güncelleme sonucu: Başarı={success}, Mesaj='{message}'")
        return success, message
    except Exception as e:
        # print(f"HATA (Servis): Model güncellenirken: {e}")
        return False, f"Model güncellenirken beklenmedik bir hata oluştu: {str(e)}"

# 4.5. delete_existing_model
# -----------------------------------------------------------------------------
def delete_existing_model(model_id: int) -> Tuple[bool, str]:
    """
    Bir AI modelini siler.
    Returns:
        Tuple[bool, str]: (başarı durumu, mesaj)
    """
    # print(f"DEBUG (Servis): Model siliniyor: ID={model_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        success, message = admin_repo.delete_model(model_id)
        # print(f"DEBUG (Servis): Model silme sonucu: Başarı={success}, Mesaj='{message}'")
        return success, message
    except Exception as e:
        # print(f"HATA (Servis): Model silinirken: {e}")
        return False, f"Model silinirken beklenmedik bir hata oluştu: {str(e)}"

# 4.6. duplicate_existing_model
# -----------------------------------------------------------------------------
def duplicate_existing_model(model_id: int) -> Tuple[bool, str, Optional[int]]:
    """
    Mevcut bir AI modelini çoğaltır.
    Args:
        model_id (int): Çoğaltılacak modelin ID'si.
    Returns:
        Tuple[bool, str, Optional[int]]: (başarı durumu, mesaj, yeni model ID'si)
    """
    # print(f"DEBUG (Servis): Model çoğaltılıyor: ID={model_id}")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        original_model_details = admin_repo.get_model_details(model_id)

        if not original_model_details:
            return False, f"ID'si {model_id} olan orijinal model bulunamadı.", None

        new_name = f"{original_model_details.get('name', 'Model')} (Kopya)"
        # data_ai_index benzersiz olmalı, bu yüzden kopyalanan için None veya yeni bir değer atanmalı.
        # Şimdilik None olarak bırakalım, kullanıcı admin panelinden düzenleyebilir.
        new_data_ai_index = None # Veya f"{original_model_details.get('data_ai_index', '')}_kopya" gibi.
                                 # Ancak bu da çakışmaya neden olabilir. En iyisi kullanıcıya bırakmak.

        success, message, new_model_id = admin_repo.create_model(
            category_id=original_model_details.get('category_id'), # Kategori ID'si aynı kalır
            name=new_name,
            icon=original_model_details.get('icon'),
            api_url=original_model_details.get('api_url'),
            data_ai_index=new_data_ai_index, # Yeni model için data_ai_index
            description=original_model_details.get('description'),
            details=original_model_details.get('details'), # Detaylar kopyalanır
            image_filename=original_model_details.get('image_filename')
        )
        # print(f"DEBUG (Servis): Model çoğaltma sonucu: Başarı={success}, Mesaj='{message}', YeniID={new_model_id}")
        return success, message, new_model_id
    except Exception as e:
        # print(f"HATA (Servis): Model çoğaltılırken: {e}")
        return False, f"Model çoğaltılırken beklenmedik bir hata oluştu: {str(e)}", None

# 5. Kullanıcı Mesajları Servisleri (User Message Services)
# =============================================================================

# 5.1. get_paginated_user_messages
# -----------------------------------------------------------------------------
def get_paginated_user_messages(page: int = 1, per_page: int = 25) -> List[Dict[str, Any]]:
    """
    Kullanıcı mesajlarını sayfalamalı olarak getirir.
    Args:
        page (int): İstenen sayfa numarası.
        per_page (int): Sayfa başına mesaj sayısı.
    Returns:
        List[Dict[str, Any]]: Mesajların listesi. Hata durumunda boş liste.
    """
    # print(f"DEBUG (Servis): Kullanıcı mesajları alınıyor: Sayfa={page}, SayfaBaşına={per_page}")
    try:
        # UserMessageRepository doğrudan AdminRepository içinde değil, ayrı bir repo.
        user_msg_repo = UserMessageRepository()
        offset = (page - 1) * per_page
        messages_entities = user_msg_repo.get_all_user_messages(limit=per_page, offset=offset)
        messages_dicts = [msg.to_dict() for msg in messages_entities if msg]
        # print(f"DEBUG (Servis): {len(messages_dicts)} kullanıcı mesajı bulundu.")
        return messages_dicts
    except Exception as e:
        # print(f"HATA (Servis): Kullanıcı mesajları alınırken: {e}")
        return []

# 5.2. get_total_user_message_count
# -----------------------------------------------------------------------------
def get_total_user_message_count() -> int:
    """
    Toplam kullanıcı mesajı sayısını getirir.
    Returns:
        int: Toplam mesaj sayısı. Hata durumunda 0.
    """
    # print("DEBUG (Servis): Toplam kullanıcı mesaj sayısı alınıyor...")
    try:
        user_msg_repo = UserMessageRepository()
        count = user_msg_repo.get_message_count() # UserMessageRepository'de bu metot var.
        # print(f"DEBUG (Servis): Toplam {count} kullanıcı mesajı bulundu.")
        return count
    except Exception as e:
        # print(f"HATA (Servis): Toplam kullanıcı mesaj sayısı alınırken: {e}")
        return 0

# 6. Dashboard Servisleri (Dashboard Services)
# =============================================================================

# 6.1. get_admin_dashboard_statistics
# -----------------------------------------------------------------------------
def get_admin_dashboard_statistics() -> Dict[str, Any]:
    """
    Admin paneli dashboard için çeşitli istatistikleri toplar.
    Returns:
        Dict[str, Any]: Dashboard istatistikleri.
    """
    # print("DEBUG (Servis): Admin dashboard istatistikleri toplanıyor...")
    try:
        admin_repo = AdminRepository() # Yeni AdminRepository
        # AdminRepository.get_admin_dashboard_stats zaten bu işi yapıyor
        # ve UserMessageRepository'den istatistikleri de alıyor.
        stats = admin_repo.get_admin_dashboard_stats()
        # print(f"DEBUG (Servis): Dashboard istatistikleri: {stats}")
        return stats
    except Exception as e:
        # print(f"HATA (Servis): Dashboard istatistikleri alınırken: {e}")
        return {
            'total_category_count': 0,
            'total_model_count': 0,
            'recent_categories': [],
            'recent_models': [],
            'user_message_stats': {} # Hata durumunda boş istatistikler
        }

# 7. Yardımcı Servisler (Utility Services)
# =============================================================================

# 7.1. get_available_icons_list
# -----------------------------------------------------------------------------
def get_available_icons_list() -> List[Dict[str, str]]: # Dönüş tipi List[Dict] olarak güncellendi
    """
    Admin panelinde kullanılabilecek ikonların bir listesini döndürür.
    Bu liste statik olabilir veya bir yapılandırma dosyasından okunabilir.
    Returns:
        List[Dict[str, str]]: İkon listesi. Her ikon {'class': '...', 'name': '...'} formatındadır.
    """
    # print("DEBUG (Servis): Kullanılabilir ikon listesi alınıyor...")
    # Orijinal koddaki `get_available_icons` Tuple[bool, Dict] döndürüyordu.
    # Rota katmanı doğrudan ikon listesini bekliyor gibi görünüyor.
    # Bu yüzden burada doğrudan listeyi döndürelim.
    # Eğer AdminRepository'de bu metot varsa, onu çağırabiliriz.
    # admin_repo = AdminRepository()
    # icons = admin_repo.get_available_icons() # Bu metot AdminRepository'de tanımlı olmalı.
    # Şimdilik statik bir liste:
    icons = [
        {"class": "bi bi-google", "name": "Google"},
        {"class": "bi bi-chat-right-dots-fill", "name": "DeepSeek"},
        {"class": "bi bi-microsoft", "name": "Microsoft"},
        {"class": "bi bi-lightning", "name": "Lightning"},
        {"class": "bi bi-stars", "name": "Yıldızlar"},
        {"class": "bi bi-magic", "name": "Sihir"},
        {"class": "bi bi-gear", "name": "Ayarlar"},
        {"class": "bi bi-code-slash", "name": "Kod"}, # bi-code -> bi-code-slash
        {"class": "bi bi-file-earmark-text", "name": "Belge"}, # bi-file-text -> bi-file-earmark-text
        {"class": "bi bi-search", "name": "Arama"},
        {"class": "bi bi-translate", "name": "Çeviri"},
        {"class": "bi bi-folder", "name": "Klasör"},
        {"class": "bi bi-archive", "name": "Arşiv"},
        {"class": "bi bi-bar-chart-line", "name": "Grafik"},
        {"class": "bi bi-image-fill", "name": "Resim"}, # bi-image -> bi-image-fill
        {"class": "bi bi-soundwave", "name": "Ses Dalgası"}, # bi-music-note-beamed -> bi-soundwave
        {"class": "bi bi-cpu", "name": "İşlemci"},
        {"class": "bi bi-lightbulb", "name": "Ampul"},
        {"class": "bi bi-chat-dots", "name": "Sohbet Baloncuğu"},
        {"class": "bi bi-palette", "name": "Palet"},
        {"class": "bi bi-shield-lock", "name": "Güvenlik"}
    ]
    # print(f"DEBUG (Servis): {len(icons)} adet ikon bulundu.")
    return icons
