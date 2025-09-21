# =============================================================================
# ROUTE DECORATORS
# =============================================================================
# Admin ve auth kontrolleri için dekoratörler
# =============================================================================

from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
from app.services.auth_service import AuthService


def admin_required(fn):
    """
    Sadece admin kullanıcıların erişebileceği endpointler için dekoratör.
    JSON isteklerde 403 JSON hata döner, sayfa isteklerinde login'e yönlendirir veya 403 verir.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not AuthService.is_authenticated():
            # JSON istek ise 401
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Kimlik doğrulama gerekli'}), 401
            # Aksi halde login'e yönlendir
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'error')
            return redirect(url_for('auth.login'))
        if not AuthService.is_admin():
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Yetki yok (admin gerekli)'}), 403
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.index'))
        return fn(*args, **kwargs)
    return wrapper
