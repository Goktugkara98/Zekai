# =============================================================================
# SETTINGS REPOSITORY (Key-Value)
# =============================================================================
# Basit bir anahtar-değer tablosu üzerinde ayarları saklamak için yardımcı sınıf.
# Değerler JSON olarak saklanabilir.
# =============================================================================

from typing import Any, Optional
import json
from app.database.db_connection import execute_query


class SettingsRepository:
    TABLE = 'settings'

    @staticmethod
    def ensure_table() -> bool:
        try:
            sql = f"""
                CREATE TABLE IF NOT EXISTS {SettingsRepository.TABLE} (
                    `key` VARCHAR(100) PRIMARY KEY,
                    `value` TEXT,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            execute_query(sql, fetch=False)
            return True
        except Exception:
            return False

    @staticmethod
    def get_value(key: str) -> Optional[str]:
        try:
            rows = execute_query("SELECT `value` FROM settings WHERE `key` = %s", (key,), fetch=True)
            if rows:
                return rows[0].get('value')
            return None
        except Exception:
            return None

    @staticmethod
    def set_value(key: str, value: str) -> bool:
        try:
            # Upsert
            sql = (
                "INSERT INTO settings(`key`, `value`) VALUES(%s, %s) "
                "ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)"
            )
            execute_query(sql, (key, value), fetch=False)
            return True
        except Exception:
            return False

    @staticmethod
    def get_json(key: str, default: Any = None) -> Any:
        raw = SettingsRepository.get_value(key)
        if not raw:
            return default
        try:
            return json.loads(raw)
        except Exception:
            return default

    @staticmethod
    def set_json(key: str, data: Any) -> bool:
        try:
            raw = json.dumps(data, ensure_ascii=False)
            return SettingsRepository.set_value(key, raw)
        except Exception:
            return False
