# =============================================================================
# Admin Paneli Rotaları Modülü (Admin Panel Routes Module)
# =============================================================================
# Bu modül, yönetici paneli için Flask rotalarını tanımlar.
# Kullanıcı arayüzü (HTML) ve API (JSON) endpoint'lerini içerir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. Blueprint Tanımı (Blueprint Definition)
# 3. Kimlik Doğrulama (Authentication)
#    3.1. admin_login_required (Decorator) : Admin girişi gerektiren rotalar için.
# 4. Arayüz Rotaları (View Routes - HTML Rendering)
#    4.1. /login (GET, POST)               : Admin giriş sayfası.
#    4.2. /logout (GET)                    : Admin çıkış işlemi.
#    4.3. / (GET)                          : Admin paneli ana sayfası (Dashboard).
#    4.4. /messages (GET)                  : Kullanıcı mesajlarını listeler.
#    4.5. /settings (GET, POST)            : (Örnek) Admin ayarları sayfası.
# 5. Kategori API Rotaları (Category API Routes - JSON)
#    5.1. GET    /api/categories                 : Tüm kategorileri getirir.
#    5.2. GET    /api/categories/count           : Toplam kategori sayısını getirir.
#    5.3. GET    /api/categories/<int:category_id> : Belirli bir kategoriyi getirir.
#    5.4. POST   /api/categories                 : Yeni bir kategori oluşturur.
#    5.5. PUT    /api/categories/<int:category_id> : Bir kategoriyi günceller.
#    5.6. DELETE /api/categories/<int:category_id> : Bir kategoriyi siler.
# 6. Model API Rotaları (Model API Routes - JSON)
#    6.1. GET    /api/models                     : Tüm modelleri getirir.
#    6.2. GET    /api/models/count               : Toplam model sayısını getirir.
#    6.3. GET    /api/models/<int:model_id>      : Belirli bir modeli getirir.
#    6.4. POST   /api/models                     : Yeni bir model oluşturur.
#    6.5. PUT    /api/models/<int:model_id>      : Bir modeli günceller.
#    6.6. DELETE /api/models/<int:model_id>      : Bir modeli siler.
#    6.7. POST   /api/models/<int:model_id>/duplicate : Bir modeli çoğaltır.
# 7. Yardımcı API Rotaları (Utility API Routes - JSON)
#    7.1. GET  /api/icons                      : Kullanılabilir ikonları listeler.
#    7.2. POST /api/logout                     : AJAX ile admin çıkış işlemi.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from flask import (
    Blueprint, render_template, request, jsonify, session,
    redirect, url_for, flash
)
from functools import wraps
import os
from werkzeug.utils import secure_filename # Dosya yükleme için (eğer kullanılacaksa)
# from werkzeug.security import check_password_hash, generate_password_hash # Eğer veritabanında hash'li şifre tutulacaksa

# Servis katmanı importları
from app.services.admin_panel_service import (
    get_paginated_user_messages, get_total_user_message_count
)

# Repository importları
from app.repositories.user_message_repository import UserMessageRepository

from app.services.admin_panel_service import (
    is_admin_authenticated,
    get_admin_dashboard_statistics, # Dashboard için eklendi
    get_all_categories_with_model_counts, # Kategori listesi için güncellendi
    get_category_details_with_models, # Tek kategori detayı için güncellendi
    create_new_category,
    update_existing_category,
    delete_existing_category,
    get_all_models_with_category_info, # Model listesi için güncellendi
    get_model_details_with_category, # Tek model detayı için güncellendi
    create_new_model,
    update_existing_model,
    delete_existing_model,
    duplicate_existing_model, # Model çoğaltma servisi
    get_available_icons_list, # İkon listesi servisi
    get_paginated_user_messages, # Mesaj listeleme servisi
    get_total_user_message_count # Toplam mesaj sayısı servisi
)
# from app.models.database import AIModelRepository # Direkt repository kullanımı yerine servis katmanı tercih edilir.
                                                 # Ancak get_paginated_user_messages bunu zaten kullanıyor olmalı.

# 2. Blueprint Tanımı (Blueprint Definition)
# =============================================================================
admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin', # Tüm admin rotaları /admin altında olacak
    template_folder='templates/admin', # Admin paneline özel şablonlar için (opsiyonel)
    static_folder='static/admin'       # Admin paneline özel statik dosyalar için (opsiyonel)
)
# print("DEBUG: Admin Blueprint oluşturuldu.")

# 3. Kimlik Doğrulama (Authentication)
# =============================================================================

# 3.1. admin_login_required (Decorator)
# -----------------------------------------------------------------------------
def admin_login_required(f):
    """
    Admin kullanıcısının giriş yapmış olmasını gerektiren bir decorator.
    Giriş yapılmamışsa login sayfasına yönlendirir.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated(): # Bu fonksiyon admin_panel_service içinde tanımlı olmalı
            flash('Bu sayfaya erişmek için yönetici olarak giriş yapmanız gerekmektedir.', 'warning')
            return redirect(url_for('admin.login_page')) # Rota adı login_page olarak güncellendi
        return f(*args, **kwargs)
    return decorated_function

# 4. Arayüz Rotaları (View Routes - HTML Rendering)
# =============================================================================

# 4.1. /login (GET, POST) - Admin Giriş Sayfası
# -----------------------------------------------------------------------------
@admin_bp.route('/login', methods=['GET', 'POST'])
def login_page(): # Fonksiyon adı login_page olarak değiştirildi (login decorator ile karışmaması için)
    """Admin giriş sayfasını yönetir."""
    if is_admin_authenticated():
        return redirect(url_for('admin.dashboard_page')) # Rota adı dashboard_page olarak güncellendi

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '') # Şifrede strip() genellikle yapılmaz

        # Admin kimlik bilgileri (güvenli bir yerden alınmalı)
        # ÖNEMLİ: Şifreler ASLA doğrudan koda yazılmamalıdır.
        # Ortam değişkenleri ve hash'lenmiş şifreler kullanılmalıdır.
        admin_username_env = os.environ.get('ADMIN_USERNAME', 'admin') # Varsayılan kullanıcı adı
        admin_password_env = os.environ.get('ADMIN_PASSWORD', 'zekaiadmin') # Varsayılan şifre (TEST AMAÇLI)
        # admin_password_hash_env = os.environ.get('ADMIN_PASSWORD_HASH') # Üretimde bu kullanılmalı

        # Üretim için: check_password_hash(admin_password_hash_env, password)
        if username == admin_username_env and password == admin_password_env:
            session['is_admin'] = True # Oturumu başlat
            session.permanent = True # Oturumun kalıcı olmasını sağla (tarayıcı kapanınca silinmesin)
            flash('Yönetici olarak başarıyla giriş yaptınız.', 'success')
            return redirect(url_for('admin.dashboard_page'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'danger')

    return render_template('login_page.html', title='Admin Girişi')  # Updated to use the new login_page.html

# 4.2. /logout (GET) - Admin Çıkış İşlemi
# -----------------------------------------------------------------------------
@admin_bp.route('/logout')
@admin_login_required
def logout_route(): # Fonksiyon adı logout_route olarak değiştirildi
    """Admin çıkış işlemini gerçekleştirir."""
    session.pop('is_admin', None) # Oturumu sonlandır
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('admin.login_page'))

# 4.3. / (GET) - Admin Paneli Ana Sayfası (Dashboard)
# -----------------------------------------------------------------------------
@admin_bp.route('/')
@admin_login_required
def dashboard_page(): # Fonksiyon adı panel -> dashboard_page olarak değiştirildi
    """Admin paneli ana sayfasını (Dashboard) gösterir."""
    try:
        stats = get_admin_dashboard_statistics() # Servis fonksiyonundan istatistikleri al
    except Exception as e:
        # print(f"DEBUG: Dashboard istatistikleri alınırken hata: {e}")
        flash(f"Dashboard verileri yüklenirken bir hata oluştu: {str(e)}", "danger")
        stats = { # Hata durumunda boş veya varsayılan istatistikler
            'total_category_count': 0,
            'total_model_count': 0,
            'recent_categories': [],
            'recent_models': [],
            'user_message_stats': {}
        }
    return render_template('admin_dashboard.html', title='Admin Paneli', stats=stats)  # Template is in the root templates directory

# 4.4. /messages (GET) - Kullanıcı Mesajlarını Listeler
# -----------------------------------------------------------------------------
@admin_bp.route('/messages')
@admin_login_required
def list_messages_page(): # Fonksiyon adı list_messages -> list_messages_page
    """Kullanıcı mesajlarını sayfalamalı olarak listeler."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int) # Sayfa başına öğe sayısı da parametrik olabilir
        if page < 1: page = 1
        if per_page < 1: per_page = 25

        messages_data = get_paginated_user_messages(page, per_page) # Servis fonksiyonu
        total_messages = get_total_user_message_count() # Toplam mesaj sayısı
        total_pages = (total_messages + per_page - 1) // per_page

    except Exception as e:
        # print(f"DEBUG: Mesajlar listelenirken hata: {e}")
        flash(f'Mesajlar yüklenirken bir hata oluştu: {str(e)}', 'danger')
        messages_data = []
        total_pages = 0
        page = 1 # Hata durumunda sayfayı başa al

    return render_template(
        'messages.html', # Şablon adı messages.html varsayıldı
        title='Kullanıcı Mesajları',
        messages=messages_data,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page
    )

# 4.5. /settings (GET, POST) - (Örnek) Admin Ayarları Sayfası
# -----------------------------------------------------------------------------
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_login_required
def settings_page():
    """Admin ayarları sayfasını yönetir (Örnek)."""
    if request.method == 'POST':
        # Ayarları kaydetme mantığı buraya eklenecek
        # Örnek: os.environ['SOME_SETTING'] = request.form.get('some_setting')
        flash('Ayarlar başarıyla kaydedildi.', 'success')
        return redirect(url_for('admin.settings_page'))

    # Kayıtlı ayarları yükleme mantığı buraya eklenecek
    # current_settings = {"some_setting": os.environ.get('SOME_SETTING', 'default_value')}
    current_settings = {} # Boş örnek
    return render_template('settings.html', title='Ayarlar', settings=current_settings)


# 5. Kullanıcı Mesajları API Rotaları (User Messages API Routes - JSON)
# =============================================================================
# Kullanıcı mesajlarını yönetmek için API endpoint'leri.

# 5.1. GET /api/user_messages - Tüm Kullanıcı Mesajlarını Getir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/user_messages', methods=['GET'])
@admin_login_required
def api_get_user_messages():
    """Tüm kullanıcı mesajlarını sayfalamalı olarak JSON formatında döndürür."""
    try:
        # Sayfalama parametrelerini al (varsayılan: 1. sayfa, sayfa başına 25 öğe)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        
        # Servis katmanından mesajları al
        messages = get_paginated_user_messages(page=page, per_page=per_page)
        
        # Toplam mesaj sayısını al
        total_messages = get_total_user_message_count()
        
        return jsonify({
            'success': True,
            'messages': messages,
            'total': total_messages,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_messages + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 5.2. DELETE /api/user_messages/<int:message_id> - Bir Kullanıcı Mesajını Sil
# -----------------------------------------------------------------------------
@admin_bp.route('/api/user_messages/<int:message_id>', methods=['DELETE'])
@admin_login_required
def api_delete_user_message(message_id):
    """Belirtilen ID'ye sahip kullanıcı mesajını siler."""
    try:
        # UserMessageRepository örneği oluştur
        message_repo = UserMessageRepository()
        
        # Mesajı sil
        success = message_repo.delete_user_message(message_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Mesaj başarıyla silindi.'})
        else:
            return jsonify({'success': False, 'error': 'Mesaj silinirken bir hata oluştu veya mesaj bulunamadı.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 6. Kategori API Rotaları (Category API Routes - JSON)
# =============================================================================
# Bu API endpoint'leri genellikle admin panelindeki AJAX istekleri için kullanılır.

# 5.1. GET /api/categories - Tüm Kategorileri Getirir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['GET'])
@admin_login_required
def api_get_all_categories():
    """Tüm kategorileri (model sayılarıyla birlikte) JSON formatında döndürür."""
    try:
        categories = get_all_categories_with_model_counts() # Servis fonksiyonu
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        # print(f"DEBUG: API /api/categories GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 5.2. GET /api/categories/count - Toplam Kategori Sayısını Getirir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/count', methods=['GET'])
@admin_login_required
def api_get_category_count():
    """Toplam kategori sayısını JSON formatında döndürür."""
    try:
        categories = get_all_categories_with_model_counts() # Bu zaten sayıyı içeriyor olabilir veya ayrı bir servis
        return jsonify({'success': True, 'count': len(categories)})
    except Exception as e:
        # print(f"DEBUG: API /api/categories/count GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 5.3. GET /api/categories/<int:category_id> - Belirli Bir Kategoriyi Getirir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['GET'])
@admin_login_required
def api_get_category_by_id(category_id: int):
    """Belirli bir kategoriyi (modelleriyle birlikte) JSON formatında döndürür."""
    try:
        category_details = get_category_details_with_models(category_id)
        if category_details:
            return jsonify({'success': True, 'category': category_details})
        else:
            return jsonify({'success': False, 'error': 'Kategori bulunamadı.'}), 404
    except Exception as e:
        # print(f"DEBUG: API /api/categories/{category_id} GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 5.4. POST /api/categories - Yeni Bir Kategori Oluşturur
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories', methods=['POST'])
@admin_login_required
def api_create_new_category():
    """Yeni bir kategori oluşturur ve sonucu JSON formatında döndürür."""
    data = request.json
    if not data or not data.get('name') or not data.get('name').strip():
        return jsonify({'success': False, 'error': 'Kategori adı gereklidir.'}), 400

    name = data['name'].strip()
    icon = data.get('icon', '').strip() # İkon opsiyonel, varsayılan boş string

    success, message, category_id = create_new_category(name, icon)
    if success:
        return jsonify({'success': True, 'message': message, 'category_id': category_id}), 201
    else:
        # Servis katmanı hatayı daha detaylı dönebilir (örn: zaten var)
        status_code = 409 if "zaten mevcut" in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code

# 5.5. PUT /api/categories/<int:category_id> - Bir Kategoriyi Günceller
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@admin_login_required
def api_update_existing_category(category_id: int):
    """Mevcut bir kategoriyi günceller ve sonucu JSON formatında döndürür."""
    data = request.json
    if not data or not data.get('name') or not data.get('name').strip(): # İkon güncellenmeyebilir
        return jsonify({'success': False, 'error': 'Kategori adı gereklidir.'}), 400

    name = data['name'].strip()
    icon = data.get('icon', '').strip() # Eğer ikon gönderilmezse mevcut ikon korunmalı (servis katmanında)

    success, message = update_existing_category(category_id, name, icon)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        status_code = 404 if "bulunamadı" in message.lower() else 400
        status_code = 409 if "zaten mevcut" in message.lower() else status_code
        return jsonify({'success': False, 'error': message}), status_code

# 5.6. DELETE /api/categories/<int:category_id> - Bir Kategoriyi Siler
# -----------------------------------------------------------------------------
@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@admin_login_required
def api_delete_existing_category(category_id: int):
    """Bir kategoriyi siler ve sonucu JSON formatında döndürür."""
    success, message = delete_existing_category(category_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        status_code = 404 if "bulunamadı" in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


# 6. Model API Rotaları (Model API Routes - JSON)
# =============================================================================

# 6.1. GET /api/models - Tüm Modelleri Getirir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['GET'])
@admin_login_required
def api_get_all_models():
    """Tüm modelleri (kategori bilgileriyle birlikte) JSON formatında döndürür."""
    try:
        models = get_all_models_with_category_info() # Servis fonksiyonu
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        # print(f"DEBUG: API /api/models GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 6.2. GET /api/models/count - Toplam Model Sayısını Getirir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/count', methods=['GET'])
@admin_login_required
def api_get_model_count():
    """Toplam model sayısını JSON formatında döndürür."""
    try:
        models = get_all_models_with_category_info()
        return jsonify({'success': True, 'count': len(models)})
    except Exception as e:
        # print(f"DEBUG: API /api/models/count GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 6.3. GET /api/models/<int:model_id> - Belirli Bir Modeli Getirir
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['GET'])
@admin_login_required
def api_get_model_by_id(model_id: int):
    """Belirli bir modeli (kategori bilgisiyle) JSON formatında döndürür."""
    try:
        model_details = get_model_details_with_category(model_id)
        if model_details:
            return jsonify({'success': True, 'model': model_details})
        else:
            return jsonify({'success': False, 'error': 'Model bulunamadı.'}), 404
    except Exception as e:
        # print(f"DEBUG: API /api/models/{model_id} GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 6.4. POST /api/models - Yeni Bir Model Oluşturur
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models', methods=['POST'])
@admin_login_required
def api_create_new_model():
    """Yeni bir AI modeli oluşturur ve sonucu JSON formatında döndürür."""
    data = request.json
    required_fields = ['name', 'category_id'] # Temel zorunlu alanlar
    if not data or not all(field in data for field in required_fields) or \
       not data['name'].strip() or not isinstance(data['category_id'], int):
        return jsonify({'success': False, 'error': 'Model adı ve kategori ID zorunludur ve geçerli olmalıdır.'}), 400

    name = data['name'].strip()
    category_id = data['category_id']
    # Opsiyonel alanlar
    icon = data.get('icon', '').strip()
    api_url = data.get('api_url', '').strip()
    data_ai_index = data.get('data_ai_index', '').strip()
    description = data.get('description', '').strip()
    details = data.get('details') # Bu bir sözlük olmalı, servis katmanı doğrular
    image_filename = data.get('image_filename', '').strip()

    success, message, model_id = create_new_model(
        category_id=category_id, name=name, icon=icon, api_url=api_url,
        data_ai_index=data_ai_index if data_ai_index else None, # Boşsa None gönder
        description=description, details=details, image_filename=image_filename
    )
    if success:
        return jsonify({'success': True, 'message': message, 'model_id': model_id}), 201
    else:
        status_code = 400
        if "bulunamadı" in message.lower(): status_code = 404 # Kategori bulunamadı gibi
        if "zaten mevcut" in message.lower(): status_code = 409 # data_ai_index çakışması gibi
        return jsonify({'success': False, 'error': message}), status_code

# 6.5. PUT /api/models/<int:model_id> - Bir Modeli Günceller
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['PUT'])
@admin_login_required
def api_update_existing_model(model_id: int):
    """Mevcut bir AI modelini günceller ve sonucu JSON formatında döndürür."""
    data = request.json
    if not data: # En az bir alan güncellenmeli
        return jsonify({'success': False, 'error': 'Güncellenecek veri bulunamadı.'}), 400

    # Servis katmanı None olan değerleri dikkate almayacak şekilde tasarlanmalı
    name = data.get('name')
    category_id = data.get('category_id')
    icon = data.get('icon')
    api_url = data.get('api_url')
    data_ai_index = data.get('data_ai_index')
    description = data.get('description')
    details = data.get('details')
    image_filename = data.get('image_filename')

    success, message = update_existing_model(
        model_id=model_id, name=name, category_id=category_id, icon=icon,
        api_url=api_url, data_ai_index=data_ai_index, description=description,
        details=details, image_filename=image_filename
    )
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        status_code = 404 if "bulunamadı" in message.lower() else 400
        status_code = 409 if "zaten mevcut" in message.lower() else status_code
        return jsonify({'success': False, 'error': message}), status_code

# 6.6. DELETE /api/models/<int:model_id> - Bir Modeli Siler
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>', methods=['DELETE'])
@admin_login_required
def api_delete_existing_model(model_id: int):
    """Bir AI modelini siler ve sonucu JSON formatında döndürür."""
    success, message = delete_existing_model(model_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        status_code = 404 if "bulunamadı" in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code

# 6.7. POST /api/models/<int:model_id>/duplicate - Bir Modeli Çoğaltır
# -----------------------------------------------------------------------------
@admin_bp.route('/api/models/<int:model_id>/duplicate', methods=['POST'])
@admin_login_required
def api_duplicate_existing_model(model_id: int):
    """Mevcut bir AI modelini çoğaltır."""
    try:
        success, message, new_model_id = duplicate_existing_model(model_id)
        if success:
            return jsonify({'success': True, 'message': message, 'new_model_id': new_model_id}), 201
        else:
            status_code = 404 if "bulunamadı" in message.lower() else 400
            return jsonify({'success': False, 'error': message}), status_code
    except Exception as e:
        # print(f"DEBUG: Model çoğaltma API hatası: {e}")
        return jsonify({'success': False, 'error': f"Model çoğaltılırken bir hata oluştu: {str(e)}"}), 500


# 7. Yardımcı API Rotaları (Utility API Routes - JSON)
# =============================================================================

# 7.1. GET /api/icons - Kullanılabilir İkonları Listeler
# -----------------------------------------------------------------------------
@admin_bp.route('/api/icons', methods=['GET'])
@admin_login_required
def api_get_available_icons():
    """Kullanılabilir ikonların listesini JSON formatında döndürür."""
    try:
        icons = get_available_icons_list() # Servis fonksiyonu
        return jsonify({'success': True, 'icons': icons})
    except Exception as e:
        # print(f"DEBUG: API /api/icons GET hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 7.2. POST /api/logout - AJAX ile Admin Çıkış İşlemi
# -----------------------------------------------------------------------------
@admin_bp.route('/api/logout', methods=['POST']) # State değiştirdiği için POST
@admin_login_required
def api_admin_logout():
    """AJAX istekleri için admin çıkış işlemini gerçekleştirir."""
    session.pop('is_admin', None)
    return jsonify({'success': True, 'message': 'Başarıyla çıkış yapıldı.'})

# Blueprint'i Flask uygulamasına kaydetmek için bu dosyanın __init__.py'da
# veya ana uygulama dosyasında import edilmesi ve register_blueprint() ile kaydedilmesi gerekir.
# Örnek: from .admin_routes import admin_bp; app.register_blueprint(admin_bp)
