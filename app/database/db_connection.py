# =============================================================================
# VERİTABANI BAĞLANTI YÖNETİCİSİ (DATABASE CONNECTION MANAGER)
# =============================================================================
# Bu dosya, basit veritabanı bağlantı işlemlerini yönetir.
# .env dosyasından veritabanı konfigürasyonunu alır.
# =============================================================================

import os
import mysql.connector
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

# .env dosyasını yükle
load_dotenv()

# Logger ayarla
logger = logging.getLogger(__name__)

def get_db_config():
    """
    Veritabanı konfigürasyonunu döndürür.
    
    Returns:
        dict: Veritabanı konfigürasyonu
    """
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'zekai_db'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': True
    }

def get_connection():
    """
    Veritabanı bağlantısı oluşturur.
    
    Returns:
        MySQLConnection: Veritabanı bağlantı nesnesi
    """
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        logger.info(f"Veritabanı bağlantısı oluşturuldu: {config['database']}")
        return connection
    except Exception as e:
        logger.error(f"Veritabanı bağlantı hatası: {str(e)}")
        raise

def get_cursor(connection, dictionary=True):
    """
    Veritabanı cursor'ı oluşturur.
    
    Args:
        connection: MySQL bağlantı nesnesi
        dictionary: Sonuçları dictionary olarak döndür (varsayılan: True)
        
    Returns:
        MySQLCursor: Veritabanı cursor nesnesi
    """
    if dictionary:
        return connection.cursor(dictionary=True)
    return connection.cursor()

def execute_query(query, params=None, fetch=True):
    """
    Tek bir sorgu çalıştırır ve sonucu döndürür.
    
    Args:
        query: SQL sorgusu
        params: Sorgu parametreleri
        fetch: Sonucu getir (varsayılan: True)
        
    Returns:
        list: Sorgu sonucu (fetch=True ise)
    """
    connection = None
    try:
        connection = get_connection()
        cursor = get_cursor(connection)
        
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            cursor.close()
            return None
            
    except Exception as e:
        logger.error(f"Sorgu çalıştırma hatası: {str(e)}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


def test_connection():
    """
    Veritabanı bağlantısını test eder.
    
    Returns:
        bool: Bağlantı başarılı ise True
    """
    try:
        result = execute_query("SELECT 1", fetch=True)
        return result is not None and len(result) > 0
    except Exception as e:
        logger.error(f"Veritabanı bağlantı testi başarısız: {str(e)}")
        return False

def get_database_info():
    """
    Veritabanı bilgilerini döndürür.
    
    Returns:
        dict: Veritabanı bilgileri
    """
    try:
        # Veritabanı adı
        db_name_result = execute_query("SELECT DATABASE()", fetch=True)
        db_name = db_name_result[0]['DATABASE()'] if db_name_result else 'Bilinmiyor'
        
        # MySQL versiyonu
        version_result = execute_query("SELECT VERSION()", fetch=True)
        version = version_result[0]['VERSION()'] if version_result else 'Bilinmiyor'
        
        return {
            'database_name': db_name,
            'mysql_version': version
        }
    except Exception as e:
        logger.error(f"Veritabanı bilgisi alınamadı: {str(e)}")
        return {}

# Modül import edildiğinde bağlantıyı test et
if __name__ == "__main__":
    if test_connection():
        print("✅ Veritabanı bağlantısı başarılı!")
        info = get_database_info()
        print(f"📊 Veritabanı: {info.get('database_name', 'Bilinmiyor')}")
        print(f"🔧 MySQL Versiyonu: {info.get('mysql_version', 'Bilinmiyor')}")
    else:
        print("❌ Veritabanı bağlantısı başarısız!")
        print("🔧 Lütfen .env dosyasındaki veritabanı ayarlarını kontrol edin.")
