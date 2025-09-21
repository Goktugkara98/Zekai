# =============================================================================
# AUTHENTICATION ROUTES (Pages)
# =============================================================================
# Giriş yap, kayıt ol ve çıkış işlemleri (HTML)
# =============================================================================

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from app.services.auth_service import AuthService

# Auth Blueprint oluştur
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Giriş yap sayfası ve işlemi.
    """
    try:
        # Zaten giriş yapılmışsa chat sayfasına yönlendir
        if AuthService.is_authenticated():
            return redirect(url_for('main.chat'))
        
        if request.method == 'POST':
            # JSON isteği (AJAX)
            if request.is_json:
                data = request.get_json()
                email = data.get('email', '').strip()
                password = data.get('password', '')
                
                # Doğrulama
                if not email or not password:
                    return jsonify({
                        'success': False,
                        'message': 'E-posta ve şifre gereklidir'
                    }), 400
                
                # Kimlik doğrulama
                result = AuthService.authenticate_user(email, password)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'message': result['message'],
                        'redirect_url': url_for('main.chat')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': result['message']
                    }), 401
            
            # Form isteği (normal POST)
            else:
                email = request.form.get('email', '').strip()
                password = request.form.get('password', '')
                
                # Doğrulama
                if not email or not password:
                    flash('E-posta ve şifre gereklidir', 'error')
                    return render_template('login.html')
                
                # Kimlik doğrulama
                result = AuthService.authenticate_user(email, password)
                
                if result['success']:
                    flash('Giriş başarılı!', 'success')
                    return redirect(url_for('main.chat'))
                else:
                    flash(result['message'], 'error')
                    return render_template('login.html')
        
        # GET isteği - login sayfasını göster
        return render_template('login.html')
        
    except Exception as e:
        if request.is_json:
            return jsonify({
                'success': False,
                'message': 'Giriş yapılırken hata oluştu'
            }), 500
        else:
            flash('Giriş yapılırken hata oluştu', 'error')
            return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Kayıt ol sayfası ve işlemi.
    """
    try:
        # Zaten giriş yapılmışsa chat sayfasına yönlendir
        if AuthService.is_authenticated():
            return redirect(url_for('main.chat'))
        
        if request.method == 'POST':
            # JSON isteği (AJAX)
            if request.is_json:
                data = request.get_json()
                email = data.get('email', '').strip()
                password = data.get('password', '')
                first_name = data.get('first_name', '').strip()
                last_name = data.get('last_name', '').strip()
                
                # Doğrulama
                if not email or not password:
                    return jsonify({
                        'success': False,
                        'message': 'E-posta ve şifre gereklidir'
                    }), 400
                
                # Kullanıcı oluştur
                result = AuthService.create_user(email, password, first_name, last_name)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'message': result['message'],
                        'redirect_url': url_for('auth.login')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': result['message']
                    }), 400
            
            # Form isteği (normal POST)
            else:
                email = request.form.get('email', '').strip()
                password = request.form.get('password', '')
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                
                # Doğrulama
                if not email or not password:
                    flash('E-posta ve şifre gereklidir', 'error')
                    return render_template('register.html')
                
                # Kullanıcı oluştur
                result = AuthService.create_user(email, password, first_name, last_name)
                
                if result['success']:
                    flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash(result['message'], 'error')
                    return render_template('register.html')
        
        # GET isteği - kayıt sayfasını göster
        return render_template('register.html')
        
    except Exception as e:
        if request.is_json:
            return jsonify({
                'success': False,
                'message': 'Kayıt olurken hata oluştu'
            }), 500
        else:
            flash('Kayıt olurken hata oluştu', 'error')
            return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """
    Çıkış yap işlemi.
    """
    try:
        AuthService.logout_user()
        flash('Başarıyla çıkış yaptınız', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash('Çıkış yapılırken hata oluştu', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/check-auth')
def check_auth():
    """
    Kimlik doğrulama durumunu kontrol eder (AJAX).
    """
    try:
        if AuthService.is_authenticated():
            user = AuthService.get_current_user()
            return jsonify({
                'authenticated': True,
                'user': user
            })
        else:
            return jsonify({
                'authenticated': False
            })
            
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': 'Kimlik doğrulama kontrol edilemedi'
        }), 500
