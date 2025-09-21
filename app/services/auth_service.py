# =============================================================================
# AUTHENTICATION SERVICE
# =============================================================================
# Bu dosya, kullanıcı kimlik doğrulama işlemlerini yönetir.
# Werkzeug ile şifreleme ve session yönetimi yapar.
# =============================================================================

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from app.database.db_connection import execute_query, get_connection, get_cursor

class AuthService:
    """
    Kimlik doğrulama servisi
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Şifreyi hash'ler.
        
        Args:
            password (str): Düz şifre
            
        Returns:
            str: Hash'lenmiş şifre
        """
        try:
            return generate_password_hash(password)
        except Exception as e:
            raise
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Şifreyi doğrular.
        
        Args:
            password (str): Düz şifre
            password_hash (str): Hash'lenmiş şifre
            
        Returns:
            bool: Şifre doğru ise True
        """
        try:
            return check_password_hash(password_hash, password)
        except Exception as e:
            return False
    
    @staticmethod
    def create_user(email: str, password: str, first_name: str = None, last_name: str = None) -> dict:
        """
        Yeni kullanıcı oluşturur.
        
        Args:
            email (str): E-posta adresi
            password (str): Şifre
            first_name (str, optional): Ad
            last_name (str, optional): Soyad
            
        Returns:
            dict: Sonuç bilgisi
        """
        try:
            # E-posta kontrolü
            if not AuthService._is_valid_email(email):
                return {
                    'success': False,
                    'message': 'Geçersiz e-posta adresi'
                }
            
            # Şifre kontrolü
            if not AuthService._is_valid_password(password):
                return {
                    'success': False,
                    'message': 'Şifre en az 6 karakter olmalıdır'
                }
            
            # Kullanıcı var mı kontrol et
            existing_user = AuthService.get_user_by_email(email)
            if existing_user:
                return {
                    'success': False,
                    'message': 'Bu e-posta adresi zaten kullanılıyor'
                }
            
            # Şifreyi hash'le
            password_hash = AuthService.hash_password(password)
            
            # Kullanıcıyı veritabanına ekle
            insert_sql = """
                INSERT INTO users (email, password_hash, first_name, last_name, is_active, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            execute_query(
                insert_sql, 
                (email, password_hash, first_name, last_name, True, False),
                fetch=False
            )
            
            return {
                'success': True,
                'message': 'Kullanıcı başarıyla oluşturuldu'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Kullanıcı oluşturulurken hata oluştu'
            }
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """
        Kullanıcıyı doğrular.
        
        Args:
            email (str): E-posta adresi
            password (str): Şifre
            
        Returns:
            dict: Sonuç bilgisi
        """
        try:
            # Kullanıcıyı bul
            user = AuthService.get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'message': 'E-posta veya şifre hatalı'
                }
            
            # Kullanıcı aktif mi kontrol et
            if not user.get('is_active'):
                return {
                    'success': False,
                    'message': 'Hesabınız deaktif durumda'
                }
            
            # Şifreyi doğrula
            if not AuthService.verify_password(password, user.get('password_hash')):
                return {
                    'success': False,
                    'message': 'E-posta veya şifre hatalı'
                }
            
            # Son giriş zamanını güncelle
            AuthService._update_last_login(user['user_id'])
            
            # Session'a kullanıcı bilgilerini kaydet
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['first_name'] = user.get('first_name', '')
            session['last_name'] = user.get('last_name', '')
            session['is_admin'] = bool(user.get('is_admin', False))
            session['is_authenticated'] = True
            # Basit kontrol isteyen yapılar için ek bayrak
            session['logged_in'] = True
            
            return {
                'success': True,
                'message': 'Giriş başarılı',
                'user': {
                    'user_id': user['user_id'],
                    'email': user['email'],
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'is_admin': bool(user.get('is_admin', False))
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Giriş yapılırken hata oluştu'
            }
    
    @staticmethod
    def get_user_by_email(email: str) -> dict:
        """
        E-posta ile kullanıcıyı bulur.
        
        Args:
            email (str): E-posta adresi
            
        Returns:
            dict: Kullanıcı bilgileri veya None
        """
        try:
            select_sql = """
                SELECT user_id, email, password_hash, first_name, last_name, 
                       is_active, is_verified, is_admin, created_at, last_login
                FROM users 
                WHERE email = %s
            """
            
            result = execute_query(select_sql, (email,), fetch=True)
            
            if result and len(result) > 0:
                return result[0]
            return None
            
        except Exception as e:
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """
        ID ile kullanıcıyı bulur.
        
        Args:
            user_id (int): Kullanıcı ID'si
            
        Returns:
            dict: Kullanıcı bilgileri veya None
        """
        try:
            select_sql = """
                SELECT user_id, email, first_name, last_name, 
                       is_active, is_verified, is_admin, created_at, last_login
                FROM users 
                WHERE user_id = %s
            """
            
            result = execute_query(select_sql, (user_id,), fetch=True)
            
            if result and len(result) > 0:
                return result[0]
            return None
            
        except Exception as e:
            return None
    
    @staticmethod
    def logout_user():
        """
        Kullanıcıyı çıkış yapar.
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            session.clear()
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def is_authenticated() -> bool:
        """
        Kullanıcının giriş yapıp yapmadığını kontrol eder.
        
        Returns:
            bool: Giriş yapılmış ise True
        """
        return bool(session.get('is_authenticated') or session.get('logged_in'))
    
    @staticmethod
    def get_current_user() -> dict:
        """
        Mevcut kullanıcı bilgilerini döndürür.
        
        Returns:
            dict: Kullanıcı bilgileri veya None
        """
        if not AuthService.is_authenticated():
            return None
        
        user_id = session.get('user_id')
        if user_id:
            return AuthService.get_user_by_id(user_id)
        return None
    
    @staticmethod
    def is_admin() -> bool:
        """
        Kullanıcının admin olup olmadığını kontrol eder.
        """
        return bool(session.get('is_admin', False))
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        E-posta formatını kontrol eder.
        
        Args:
            email (str): E-posta adresi
            
        Returns:
            bool: Geçerli ise True
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """
        Şifre güvenliğini kontrol eder.
        
        Args:
            password (str): Şifre
            
        Returns:
            bool: Geçerli ise True
        """
        return len(password) >= 6
    
    @staticmethod
    def _update_last_login(user_id: int):
        """
        Son giriş zamanını günceller.
        
        Args:
            user_id (int): Kullanıcı ID'si
        """
        try:
            update_sql = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
            execute_query(update_sql, (user_id,), fetch=False)
        except Exception:
            pass

 
