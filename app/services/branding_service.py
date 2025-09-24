# =============================================================================
# BRANDING SERVICE
# =============================================================================
# Admin tarafında yapılandırılan marka/logoyu saklar ve okur.
# settings (key-value) tablosunu kullanır.
# =============================================================================

import os
import time
from typing import Dict, Any
from werkzeug.utils import secure_filename
from flask import url_for

from app.database.repositories.settings_repository import SettingsRepository


class BrandingService:
    SETTINGS_KEY = 'branding_settings'
    UPLOAD_DIR = os.path.join('app', 'static', 'img', 'branding')

    @staticmethod
    def ensure_storage():
        SettingsRepository.ensure_table()
        try:
            os.makedirs(BrandingService.UPLOAD_DIR, exist_ok=True)
        except Exception:
            pass

    @staticmethod
    def get_settings() -> Dict[str, Any]:
        BrandingService.ensure_storage()
        defaults = {
            'variant': 'text',  # 'logo' | 'logo+text' | 'text'
            'brand_text': 'zekai',
            'logo_path': None,  # relative static path like 'img/branding/logo.png'
            'text_color_light': '#0f172a',
            'text_color_dark': '#e8eaf0',
            'border_color_light': '#e5e7eb',
            'border_color_dark': '#243049',
        }
        data = SettingsRepository.get_json(BrandingService.SETTINGS_KEY, defaults) or defaults
        # sanity
        if data.get('variant') not in ('logo', 'logo+text', 'text'):
            data['variant'] = 'text'
        if not isinstance(data.get('brand_text'), str):
            data['brand_text'] = defaults['brand_text']
        return data

    @staticmethod
    def set_settings(payload: Dict[str, Any]) -> Dict[str, Any]:
        BrandingService.ensure_storage()
        current = BrandingService.get_settings()
        variant = payload.get('variant') or current.get('variant')
        brand_text = payload.get('brand_text') if payload.get('brand_text') is not None else current.get('brand_text')
        logo_path = payload.get('logo_path') if payload.get('logo_path') is not None else current.get('logo_path')
        text_color_light = payload.get('text_color_light') or current.get('text_color_light') or '#0f172a'
        text_color_dark = payload.get('text_color_dark') or current.get('text_color_dark') or '#e8eaf0'
        border_color_light = payload.get('border_color_light') or current.get('border_color_light') or '#e5e7eb'
        border_color_dark = payload.get('border_color_dark') or current.get('border_color_dark') or '#243049'

        if variant not in ('logo', 'logo+text', 'text'):
            variant = 'text'
        if not isinstance(brand_text, str) or not brand_text.strip():
            brand_text = current.get('brand_text') or 'zekai'

        data = {
            'variant': variant,
            'brand_text': brand_text.strip(),
            'logo_path': logo_path,
            'text_color_light': text_color_light,
            'text_color_dark': text_color_dark,
            'border_color_light': border_color_light,
            'border_color_dark': border_color_dark,
        }
        ok = SettingsRepository.set_json(BrandingService.SETTINGS_KEY, data)
        return {'success': bool(ok), 'data': data}

    @staticmethod
    def save_logo(file_storage) -> Dict[str, Any]:
        """Save uploaded logo to static/img/branding and update settings with new path."""
        BrandingService.ensure_storage()
        if not file_storage:
            return {'success': False, 'error': 'Dosya bulunamadı'}
        filename = secure_filename(file_storage.filename or '')
        if not filename:
            return {'success': False, 'error': 'Geçersiz dosya adı'}
        name, ext = os.path.splitext(filename)
        if ext.lower() not in ('.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif'):
            return {'success': False, 'error': 'Desteklenmeyen dosya türü'}
        # make unique
        ts = int(time.time())
        unique = f"logo_{ts}{ext.lower()}"
        abs_path = os.path.join(BrandingService.UPLOAD_DIR, unique)
        try:
            file_storage.save(abs_path)
        except Exception:
            return {'success': False, 'error': 'Dosya kaydedilemedi'}
        # relative static path for url_for
        rel = os.path.join('img', 'branding', unique).replace('\\', '/')
        # update settings with new path
        cur = BrandingService.get_settings()
        cur['logo_path'] = rel
        SettingsRepository.set_json(BrandingService.SETTINGS_KEY, cur)
        # build absolute URL
        try:
            logo_url = url_for('static', filename=rel)
        except Exception:
            logo_url = f"/static/{rel}"
        return {'success': True, 'data': {'logo_path': rel, 'logo_url': logo_url}}
