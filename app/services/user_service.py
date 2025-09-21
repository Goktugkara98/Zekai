# =============================================================================
# USER SERVICE
# =============================================================================
# Kullanıcı işlemleri için servis sınıfı.
# =============================================================================

import logging
from typing import Dict, Any
from app.database.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserService:
    def list_users(self) -> Dict[str, Any]:
        try:
            users = UserRepository.list_users()
            return {'success': True, 'data': users, 'count': len(users)}
        except Exception as e:
            logger.error(f"Kullanıcıları listeleme hatası: {str(e)}")
            return {'success': False, 'error': 'Kullanıcılar getirilemedi'}

    def get_user(self, user_id: int) -> Dict[str, Any]:
        try:
            user = UserRepository.get_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'Kullanıcı bulunamadı'}
            return {'success': True, 'data': user}
        except Exception as e:
            logger.error(f"Kullanıcı getirme hatası: {str(e)}")
            return {'success': False, 'error': 'Kullanıcı getirilemedi'}

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            email = (data.get('email') or '').strip()
            password = data.get('password')
            first_name = (data.get('first_name') or '').strip() or None
            last_name = (data.get('last_name') or '').strip() or None
            is_admin = bool(data.get('is_admin', False))
            is_active = bool(data.get('is_active', True))
            is_verified = bool(data.get('is_verified', False))

            if not email or not password:
                return {'success': False, 'error': 'email ve password zorunludur'}

            # Eşsiz email kontrolü
            if UserRepository.get_by_email(email):
                return {'success': False, 'error': 'Bu e-posta zaten kayıtlı'}

            password_hash = AuthService.hash_password(password)
            new_id = UserRepository.create_user(email, password_hash, first_name, last_name, is_admin, is_active, is_verified)
            if new_id:
                return {'success': True, 'data': {'user_id': new_id}, 'message': 'Kullanıcı oluşturuldu'}
            return {'success': False, 'error': 'Kullanıcı oluşturulamadı'}
        except Exception as e:
            logger.error(f"Kullanıcı oluşturma hatası: {str(e)}")
            return {'success': False, 'error': 'Kullanıcı oluşturulamadı'}

    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not data:
                return {'success': False, 'error': 'Güncellenecek veri gönderilmedi'}
            ok = UserRepository.update_user(user_id, data)
            return {'success': True, 'message': 'Kullanıcı güncellendi'} if ok else {'success': False, 'error': 'Kullanıcı güncellenemedi'}
        except Exception as e:
            logger.error(f"Kullanıcı güncelleme hatası: {str(e)}")
            return {'success': False, 'error': 'Kullanıcı güncellenemedi'}

    def update_password(self, user_id: int, new_password: str) -> Dict[str, Any]:
        try:
            if not new_password or len(new_password) < 6:
                return {'success': False, 'error': 'Şifre en az 6 karakter olmalı'}
            ph = AuthService.hash_password(new_password)
            ok = UserRepository.update_password(user_id, ph)
            return {'success': True, 'message': 'Şifre güncellendi'} if ok else {'success': False, 'error': 'Şifre güncellenemedi'}
        except Exception as e:
            logger.error(f"Şifre güncelleme hatası: {str(e)}")
            return {'success': False, 'error': 'Şifre güncellenemedi'}

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        try:
            ok = UserRepository.delete_user(user_id)
            return {'success': True, 'message': 'Kullanıcı silindi'} if ok else {'success': False, 'error': 'Kullanıcı silinemedi'}
        except Exception as e:
            logger.error(f"Kullanıcı silme hatası: {str(e)}")
            return {'success': False, 'error': 'Kullanıcı silinemedi'}
