# =============================================================================
# Veritabanı Modülü (ESKİ - DEPRECATED)
# =============================================================================
# NOT: Bu modül artık kullanılmamaktadır.
# Yeni geliştirmeler için lütfen aşağıdaki modülleri kullanın:
#
# - app/models/base.py: Temel veritabanı bağlantı sınıfları
# - app/models/entities/: Veri modelleri (Category, Model, UserMessage)
# - app/models/migrations.py: Tablo oluşturma ve migration işlemleri
# - app/repositories/: Repository sınıfları (veritabanı işlemleri)
#
# Örnek kullanım:
# from app.repositories import CategoryRepository, ModelRepository, AdminRepository
# from app.models.migrations import initialize_database
#
# # Veritabanını başlat
# initialize_database()
#
# # Repository'leri kullan
# category_repo = CategoryRepository()
# categories = category_repo.get_all_categories()
# =============================================================================

import mysql.connector
from mysql.connector import Error
from app.config import DB_CONFIG
from typing import Dict, List, Optional, Any, Tuple

# Yeni yapıyı import et (geriye dönük uyumluluk için)
from app.models.base import DatabaseConnection as NewDatabaseConnection
from app.repositories import CategoryRepository, ModelRepository, UserMessageRepository

class DatabaseConnection:
    """Veritabanı bağlantısı için sınıf (ESKİ - DEPRECATED).
    
    Bu sınıf artık kullanılmamaktadır.
    Yeni geliştirmeler için app.models.base.DatabaseConnection sınıfını kullanın.
    """
    
    def __init__(self):
        # Yeni DatabaseConnection sınıfını kullan
        self._new_db = NewDatabaseConnection()
        self.connection = None
        self.cursor = None
        self.db_config = DB_CONFIG
    
    def connect(self):
        """Veritabanına bağlanır."""
        self._new_db.connect()
        self.connection = self._new_db.connection
        self.cursor = self._new_db.cursor
    
    def close(self):
        """Veritabanı bağlantısını kapatır."""
        self._new_db.close()
        self.connection = None
        self.cursor = None
    
    def _ensure_connection(self):
        """Bağlantının açık olduğundan emin olur."""
        if not self.connection or not self.cursor:
            self.connect()
    
    def create_all_tables(self):
        """Tüm tabloları oluşturur."""
        from app.models.migrations import initialize_database
        initialize_database()


class AIModelRepository:
    """AI modelleri için repository sınıfı (ESKİ - DEPRECATED).
    
    Bu sınıf artık kullanılmamaktadır.
    Yeni geliştirmeler için aşağıdaki sınıfları kullanın:
    - app.repositories.CategoryRepository
    - app.repositories.ModelRepository
    - app.repositories.UserMessageRepository
    """
    
    def __init__(self, db_connection=None):
        # Yeni repository sınıflarını kullan
        self._category_repo = CategoryRepository(db_connection)
        self._model_repo = ModelRepository(db_connection)
        self._user_message_repo = UserMessageRepository(db_connection)
        
        # Geriye dönük uyumluluk için
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
    
    def _ensure_connection(self):
        """Bağlantının açık olduğundan emin olur."""
        self.db._ensure_connection()
    
    def _close_if_owned(self):
        """Bağlantıyı kapatır (eğer bu sınıf tarafından oluşturulduysa)."""
        if self.own_connection:
            self.db.close()
    
    # -------------------------------------------------------------------------
    # Tablo Yönetimi
    # -------------------------------------------------------------------------
    def create_ai_categories_table(self):
        """AI kategorileri tablosunu oluşturur."""
        from app.models.migrations import DatabaseMigrations
        migrations = DatabaseMigrations()
        migrations.create_categories_table()
    
    def create_ai_models_table(self):
        """AI modelleri tablosunu oluşturur."""
        from app.models.migrations import DatabaseMigrations
        migrations = DatabaseMigrations()
        migrations.create_models_table()
    
    def create_user_messages_table(self):
        """Kullanıcı mesajları tablosunu oluşturur."""
        from app.models.migrations import DatabaseMigrations
        migrations = DatabaseMigrations()
        migrations.create_user_messages_table()
    
    # -------------------------------------------------------------------------
    # Kategori İşlemleri
    # -------------------------------------------------------------------------
    def insert_ai_category(self, name, icon):
        """Yeni bir kategori ekler."""
        success, _, _ = self._category_repo.create_category(name, icon)
        return success
    
    def get_ai_category_by_name(self, name):
        """İsme göre kategori getirir."""
        return self._category_repo.get_category_by_name(name)
    
    def get_all_ai_categories(self):
        """Tüm kategorileri getirir."""
        categories = self._category_repo.get_all_categories()
        return [category.to_dict() for category in categories]
    
    # -------------------------------------------------------------------------
    # Model İşlemleri
    # -------------------------------------------------------------------------
    def insert_ai_model(self, category_id, name, icon, data_ai_index, api_url, 
                     request_method='POST', request_headers=None, request_body_template=None, response_path=None):
        """Yeni bir model ekler."""
        success, _, _ = self._model_repo.create_model(
            category_id, name, icon, data_ai_index, api_url, 
            request_method, request_headers, request_body_template, response_path
        )
        return success
    
    def get_ai_model_by_data_ai_index(self, data_ai_index):
        """data_ai_index'e göre model getirir."""
        model = self._model_repo.get_model_by_data_ai_index(data_ai_index)
        return model.to_dict() if model else None
    
    def get_ai_models_by_category_id(self, category_id):
        """Kategori ID'sine göre modelleri getirir."""
        models = self._model_repo.get_models_by_category_id(category_id)
        return [model.to_dict() for model in models]
    
    def get_all_ai_models(self):
        """Tüm modelleri getirir."""
        models = self._model_repo.get_all_models()
        return [model.to_dict() for model in models]
    
    # -------------------------------------------------------------------------
    # Kullanıcı Mesaj İşlemleri
    # -------------------------------------------------------------------------
    def insert_user_message(self, session_id, user_message, ai_response, ai_model_name):
        """Kullanıcı mesajı ve AI yanıtını ekler."""
        return self._user_message_repo.insert_user_message(
            session_id, user_message, ai_response, ai_model_name
        )
    
    def get_all_user_messages(self, limit=100, offset=0):
        """Tüm kullanıcı mesajlarını getirir."""
        messages = self._user_message_repo.get_all_user_messages(limit, offset)
        return [message.to_dict() for message in messages]


# -----------------------------------------------------------------------------
# Legacy functions for backward compatibility
# -----------------------------------------------------------------------------
def get_db_connection():
    """Veritabanı bağlantısı oluşturur (ESKİ)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error:
        return None

def initialize_database():
    """Veritabanını başlatır (ESKİ)."""
    from app.models.migrations import initialize_database as init_db
    init_db()
