# =============================================================================
# Veritabanı Modülü (ESKİ - KULLANIM DIŞI)
# =============================================================================
# DİKKAT: Bu modül artık aktif olarak geliştirilmemekte ve kullanılmamaktadır.
#          Gelecekteki geliştirmeler ve mevcut kullanımlar için lütfen
#          aşağıdaki daha yeni ve modüler yapıyı tercih edin:
#
# YENİ YAPI:
# ----------
# - app.models.base:
#   - DatabaseConnection: Temel veritabanı bağlantı yönetimi.
#   - BaseRepository:     Temel depo (repository) sınıfı.
#
# - app.models.entities:
#   - Category, Model, UserMessage gibi varlık (entity) sınıfları.
#
# - app.models.migrations:
#   - DatabaseMigrations: Tablo oluşturma ve veritabanı şeması geçişleri.
#   - initialize_database(), migrate_database() yardımcı fonksiyonları.
#
# - app.repositories:
#   - CategoryRepository:     Kategori veritabanı işlemleri.
#   - ModelRepository:        Model veritabanı işlemleri.
#   - UserMessageRepository:  Kullanıcı mesajları veritabanı işlemleri.
#   - AdminRepository:        Yönetici paneli için genel veritabanı işlemleri.
#
# ÖRNEK KULLANIM (YENİ YAPI):
# --------------------------
# from app.models.base import DatabaseConnection
# from app.repositories import CategoryRepository, ModelRepository
# from app.models.migrations import initialize_database
#
# # Veritabanını ve tabloları başlat (eğer henüz yapılmadıysa)
# # initialize_database()
#
# # Bir veritabanı bağlantısı oluştur (veya BaseRepository'nin kendi bağlantısını kullanmasına izin ver)
# # db_conn = DatabaseConnection()
# # db_conn.connect()
#
# # Repository örneklerini oluştur
# # category_repo = CategoryRepository(db_conn)
# # model_repo = ModelRepository(db_conn)
#
# # # Tüm kategorileri al
# # categories = category_repo.get_all_categories()
# # for cat in categories:
# #     print(f"Kategori: {cat.name}")
#
# # # Bağlantıyı kapat (eğer manuel yönetiliyorsa)
# # db_conn.close()
# =============================================================================

import mysql.connector
from mysql.connector import Error as MySQLError # MySQLError olarak yeniden adlandırıldı
from app.config import DB_CONFIG
from typing import Dict, List, Optional, Any, Tuple

# Yeni yapıya ait modüllerin import edilmesi (geriye dönük uyumluluk veya yönlendirme için)
from app.models.base import DatabaseConnection as NewDatabaseConnection
from app.repositories import CategoryRepository, ModelRepository, UserMessageRepository
# AdminRepository de kullanılabilir, ancak bu eski modülde doğrudan bir karşılığı yok gibi.

# -----------------------------------------------------------------------------
# ESKİ SINIFLAR (KULLANIM DIŞI)
# -----------------------------------------------------------------------------

class DatabaseConnection:
    """
    Veritabanı bağlantısı için sınıf (ESKİ - KULLANIM DIŞI).

    Bu sınıf artık kullanılmamaktadır.
    Yeni geliştirmeler için app.models.base.DatabaseConnection sınıfını kullanın.
    """
    def __init__(self):
        # print("UYARI: Eski DatabaseConnection sınıfı başlatıldı. Lütfen app.models.base.DatabaseConnection kullanın.")
        self._new_db_conn = NewDatabaseConnection() # Yeni sınıfı dahili olarak kullanır
        self.connection = None
        self.cursor = None
        # self.db_config = DB_CONFIG # _new_db_conn zaten kendi yapılandırmasını kullanıyor

    def connect(self):
        """Veritabanına bağlanır (ESKİ YÖNTEM)."""
        try:
            self._new_db_conn.connect()
            self.connection = self._new_db_conn.connection
            self.cursor = self._new_db_conn.cursor
            # print("DEBUG (Eski): Veritabanı bağlantısı yeni metot üzerinden kuruldu.")
        except MySQLError as e:
            # print(f"HATA (Eski): Veritabanına bağlanırken hata: {e}")
            self.connection = None
            self.cursor = None
            raise # Hatayı yukarıya bildir

    def close(self):
        """Veritabanı bağlantısını kapatır (ESKİ YÖNTEM)."""
        self._new_db_conn.close()
        self.connection = None
        self.cursor = None
        # print("DEBUG (Eski): Veritabanı bağlantısı yeni metot üzerinden kapatıldı.")

    def _ensure_connection(self):
        """Bağlantının açık olduğundan emin olur (ESKİ YÖNTEM)."""
        # Bu metot, yeni _new_db_conn._ensure_connection çağrısını delege etmeli
        if not self.connection or not self.connection.is_connected() or not self.cursor:
            # print("DEBUG (Eski): Bağlantı yok veya kapalı, yeniden bağlanılıyor...")
            self.connect()

    def create_all_tables(self):
        """
        Tüm tabloları oluşturur (ESKİ YÖNTEM - Yeni migration modülünü çağırır).
        Bu metot doğrudan app.models.migrations.initialize_database() fonksiyonunu çağırır.
        """
        # print("UYARI: Eski create_all_tables çağrıldı. app.models.migrations.initialize_database() kullanılıyor.")
        from app.models.migrations import initialize_database as init_db_new
        init_db_new()


class AIModelRepository:
    """
    AI modelleri için repository sınıfı (ESKİ - KULLANIM DIŞI).

    Bu sınıf artık kullanılmamaktadır.
    Yeni geliştirmeler için aşağıdaki sınıfları kullanın:
    - app.repositories.CategoryRepository
    - app.repositories.ModelRepository
    - app.repositories.UserMessageRepository
    """
    def __init__(self, db_connection: Optional[DatabaseConnection] = None): # Tip ipucu DatabaseConnection (eski)
        # print("UYARI: Eski AIModelRepository sınıfı başlatıldı. Lütfen yeni repository sınıflarını kullanın.")

        # Eğer dışarıdan bir db_connection (eski tip) verildiyse,
        # onun _new_db_conn (yeni tip) özelliğini alıp yeni repolara verelim.
        # Eğer verilmediyse, yeni repolar kendi bağlantılarını oluşturacaklar.
        new_db_conn_instance = None
        if db_connection and hasattr(db_connection, '_new_db_conn'):
            new_db_conn_instance = db_connection._new_db_conn
        elif db_connection and isinstance(db_connection, NewDatabaseConnection): # Yanlışlıkla yeni tip verilirse
             new_db_conn_instance = db_connection


        self._category_repo = CategoryRepository(new_db_conn_instance)
        self._model_repo = ModelRepository(new_db_conn_instance)
        self._user_message_repo = UserMessageRepository(new_db_conn_instance)

        # Geriye dönük uyumluluk için db ve own_connection özellikleri (çok önerilmez)
        # Bu kısım, eski kodun bu özelliklere doğrudan erişip erişmediğine bağlı.
        # İdealde, bu eski sınıfın metotları sadece yeni repoları çağırmalı.
        if db_connection:
            self.db = db_connection # Eski tip bağlantıyı tutar
            self.own_connection = False
        else:
            # Eğer eski AIModelRepository kendi bağlantısını oluşturuyorsa,
            # bu eski tip bir DatabaseConnection olur.
            self.db = DatabaseConnection() # Eski tip bir bağlantı oluşturur
            self.own_connection = True
            # print("DEBUG (Eski AIModelRepo): Yeni dahili (eski tip) DatabaseConnection oluşturuldu.")

    def _ensure_connection(self):
        """Bağlantının açık olduğundan emin olur (ESKİ YÖNTEM)."""
        if self.own_connection: # Sadece kendi oluşturduğu bağlantıyı yönetir
            self.db._ensure_connection()

    def _close_if_owned(self):
        """Bağlantıyı kapatır (eğer bu sınıf tarafından oluşturulduysa) (ESKİ YÖNTEM)."""
        if self.own_connection:
            self.db.close()

    # -------------------------------------------------------------------------
    # Tablo Yönetimi (ESKİ - Yeni migration modülüne yönlendirilmeli)
    # -------------------------------------------------------------------------
    def create_ai_categories_table(self):
        """AI kategorileri tablosunu oluşturur (ESKİ - Yeni migration'ı çağırır)."""
        # print("UYARI: Eski create_ai_categories_table çağrıldı. app.models.migrations kullanılıyor.")
        from app.models.migrations import DatabaseMigrations
        migrations = DatabaseMigrations() # Kendi bağlantısını kullanır
        migrations.create_categories_table()

    def create_ai_models_table(self):
        """AI modelleri tablosunu oluşturur (ESKİ - Yeni migration'ı çağırır)."""
        # print("UYARI: Eski create_ai_models_table çağrıldı. app.models.migrations kullanılıyor.")
        from app.models.migrations import DatabaseMigrations
        migrations = DatabaseMigrations()
        migrations.create_models_table()

    def create_user_messages_table(self):
        """Kullanıcı mesajları tablosunu oluşturur (ESKİ - Yeni migration'ı çağırır)."""
        # print("UYARI: Eski create_user_messages_table çağrıldı. app.models.migrations kullanılıyor.")
        from app.models.migrations import DatabaseMigrations
        migrations = DatabaseMigrations()
        migrations.create_user_messages_table()

    # -------------------------------------------------------------------------
    # Kategori İşlemleri (ESKİ - Yeni CategoryRepository'e yönlendirir)
    # -------------------------------------------------------------------------
    def insert_ai_category(self, name: str, icon: str) -> bool:
        """Yeni bir kategori ekler (ESKİ)."""
        success, _, _ = self._category_repo.create_category(name, icon)
        return success

    def get_ai_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """İsme göre kategori getirir (ESKİ)."""
        category_entity = self._category_repo.get_category_by_name(name)
        return category_entity.to_dict() if category_entity else None

    def get_all_ai_categories(self) -> List[Dict[str, Any]]:
        """Tüm kategorileri getirir (ESKİ)."""
        categories_entities = self._category_repo.get_all_categories()
        return [cat.to_dict() for cat in categories_entities if cat]

    # -------------------------------------------------------------------------
    # Model İşlemleri (ESKİ - Yeni ModelRepository'e yönlendirir)
    # -------------------------------------------------------------------------
    def insert_ai_model(self, category_id: int, name: str, icon: str,
                        data_ai_index: str, api_url: str,
                        # Eski sürümde bu parametreler ModelRepository.create_model'de yoktu.
                        # Eğer eski kod bunları bekliyorsa, ModelRepository.create_model güncellenmeli
                        # veya burada bir uyarlama yapılmalı. Şimdilik ModelRepository'nin
                        # mevcut imzasına göre yönlendirme yapılıyor.
                        request_method: str = 'POST', # Bu parametreler yeni ModelRepo'da yok
                        request_headers: Optional[Dict] = None, # Bu parametreler yeni ModelRepo'da yok
                        request_body_template: Optional[Dict] = None, # Bu parametreler yeni ModelRepo'da yok
                        response_path: Optional[str] = None # Bu parametreler yeni ModelRepo'da yok
                        ) -> bool:
        """Yeni bir model ekler (ESKİ)."""
        # print(f"UYARI: Eski insert_ai_model çağrıldı. Parametreler: category_id={category_id}, name='{name}', data_ai_index='{data_ai_index}'")
        # Yeni ModelRepository.create_model metodu farklı parametreler alıyor olabilir.
        # Uyum sağlamak için details parametresini kullanabiliriz.
        details_payload = {}
        if request_method != 'POST': details_payload['request_method'] = request_method
        if request_headers: details_payload['request_headers'] = request_headers
        if request_body_template: details_payload['request_body_template'] = request_body_template
        if response_path: details_payload['response_path'] = response_path

        success, _, _ = self._model_repo.create_model(
            category_id=category_id,
            name=name,
            icon=icon,
            api_url=api_url,
            data_ai_index=data_ai_index,
            details=details_payload if details_payload else None
            # description ve image_filename için eski metodda parametre yoktu.
        )
        return success

    def get_ai_model_by_data_ai_index(self, data_ai_index: str) -> Optional[Dict[str, Any]]:
        """data_ai_index'e göre model getirir (ESKİ)."""
        model_entity = self._model_repo.get_model_by_data_ai_index(data_ai_index)
        return model_entity.to_dict() if model_entity else None

    def get_ai_models_by_category_id(self, category_id: int) -> List[Dict[str, Any]]:
        """Kategori ID'sine göre modelleri getirir (ESKİ)."""
        models_entities = self._model_repo.get_models_by_category_id(category_id)
        return [model.to_dict() for model in models_entities if model]

    def get_all_ai_models(self) -> List[Dict[str, Any]]:
        """Tüm modelleri getirir (ESKİ)."""
        models_entities = self._model_repo.get_all_models()
        return [model.to_dict() for model in models_entities if model]

    # -------------------------------------------------------------------------
    # Kullanıcı Mesaj İşlemleri (ESKİ - Yeni UserMessageRepository'e yönlendirir)
    # -------------------------------------------------------------------------
    def insert_user_message(self, session_id: str, user_message: str,
                            ai_response: str, ai_model_name: str) -> Optional[int]:
        """Kullanıcı mesajı ve AI yanıtını ekler (ESKİ)."""
        # Yeni UserMessageRepository.insert_user_message daha fazla parametre alıyor.
        # Eski çağrılar için temel parametrelerle yönlendirme yapılıyor.
        return self._user_message_repo.insert_user_message(
            session_id=session_id,
            user_message=user_message,
            ai_response=ai_response,
            ai_model_name=ai_model_name
            # Diğer opsiyonel parametreler None olarak gidecek.
        )

    def get_all_user_messages(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Tüm kullanıcı mesajlarını getirir (ESKİ)."""
        messages_entities = self._user_message_repo.get_all_user_messages(limit, offset)
        return [msg.to_dict() for msg in messages_entities if msg]


# -----------------------------------------------------------------------------
# ESKİ YARDIMCI FONKSİYONLAR (KULLANIM DIŞI)
# -----------------------------------------------------------------------------
def get_db_connection() -> Optional[mysql.connector.MySQLConnection]: # Dönüş tipi düzeltildi
    """
    Veritabanı bağlantısı oluşturur (ESKİ - KULLANIM DIŞI).
    app.models.base.DatabaseConnection().connect() kullanılmalıdır.
    """
    # print("UYARI: Eski get_db_connection fonksiyonu çağrıldı. Lütfen yeni bağlantı yöntemlerini kullanın.")
    try:
        # Bu fonksiyon doğrudan bir mysql.connector bağlantısı döndürüyor,
        # DatabaseConnection sınıfımızı değil. Bu, eski kodun nasıl çalıştığına bağlı.
        # İdealde, bu da yeni DatabaseConnection sınıfını kullanmalı.
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except MySQLError as e:
        # print(f"HATA (Eski get_db_connection): Bağlantı hatası: {e}")
        return None

def initialize_database():
    """
    Veritabanını başlatır (ESKİ - KULLANIM DIŞI).
    app.models.migrations.initialize_database() kullanılmalıdır.
    """
    # print("UYARI: Eski initialize_database fonksiyonu çağrıldı. app.models.migrations.initialize_database() kullanılıyor.")
    from app.models.migrations import initialize_database as init_db_new
    init_db_new()

# Modül doğrudan çalıştırılırsa (genellikle test veya tek seferlik işlemler için)
if __name__ == '__main__':
    print("="*50)
    print("UYARI: Bu modül (database.py) eskidir ve KULLANIM DIŞIDIR.")
    print("Lütfen app.models ve app.repositories altındaki yeni modülleri kullanın.")
    print("="*50)

    # Örnek olarak eski initialize_database çağrılabilir, ancak yeni yapıyı kullanmaya teşvik eder.
    # print("\nEski initialize_database() fonksiyonu test ediliyor (yeni migration'ı çağıracak)...")
    # initialize_database()
    # print("Eski initialize_database() testi tamamlandı.")

    # print("\nEski DatabaseConnection sınıfı test ediliyor...")
    # old_conn = DatabaseConnection()
    # try:
    #     old_conn.connect()
    #     if old_conn.cursor:
    #         old_conn.cursor.execute("SELECT CURDATE();")
    #         print(f"Eski bağlantı üzerinden tarih sorgusu: {old_conn.cursor.fetchone()}")
    #     old_conn.close()
    #     print("Eski DatabaseConnection testi tamamlandı.")
    # except Exception as e:
    #     print(f"Eski DatabaseConnection testi sırasında hata: {e}")

