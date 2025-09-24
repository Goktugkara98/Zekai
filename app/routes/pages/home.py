# =============================================================================
# HOME PAGES
# =============================================================================
# Ana sayfa ve chat sayfaları
# =============================================================================

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.services.auth_service import AuthService
from app.services.branding_service import BrandingService

# Main Blueprint (name 'main' kalıyor, URL'ler değişmiyor)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return "Ana sayfa yüklenirken hata oluştu", 500

@main_bp.route('/chat')
def chat():
    try:
        if not AuthService.is_authenticated():
            return redirect(url_for('auth.login'))

        user = AuthService.get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        if not user.get('is_active'):
            flash('Hesabınız aktif değil. Lütfen yönetici ile iletişime geçin.', 'error')
            return redirect(url_for('auth.login'))

        first = (user.get('first_name') or '').strip()
        last = (user.get('last_name') or '').strip()
        user_name = (first + ' ' + last).strip() if (first or last) else user.get('email')
        user_email = user.get('email')

        branding = BrandingService.get_settings()
        return render_template('chat.html', user_name=user_name, user_email=user_email, branding=branding)
    except Exception as e:
        return "Chat sayfası yüklenirken hata oluştu", 500

@main_bp.route('/login')
def login_redirect():
    try:
        return redirect('/auth/login')
    except Exception as e:
        return "Login sayfası yüklenirken hata oluştu", 500
