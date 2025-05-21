# =============================================================================
# Veritabanı Geçişleri Modülü (Database Migrations Module) - REVİZE EDİLMİŞ
# =============================================================================
# Bu modül, veritabanı tablolarının oluşturulması, güncellenmesi (geçişler)
# ve veritabanı durumunun kontrol edilmesi gibi işlemleri yönetir.
# `ai_models` tablosu yeni alanları içerecek şekilde güncellenmiştir.
#
# İçindekiler:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
#
# 2.0 DATABASEMIGRATIONS SINIFI (DATABASEMIGRATIONS CLASS)
#     2.1. __init__                        : Yapıcı Metot.
#     2.2. create_all_tables               : Tüm veritabanı tablolarını oluşturur.
#     2.3. _create_table_if_not_exists     : Bir tabloyu yoksa oluşturan yardımcı metot.
#     2.4. create_categories_table         : 'ai_categories' tablosunu oluşturur.
#     2.5. create_models_table             : 'ai_models' tablosunu oluşturur/günceller. (Güncellendi)
#     2.6. create_user_messages_table      : 'user_messages' tablosunu oluşturur/günceller.
#     2.7. migrate_user_messages_table     : 'user_messages' tablosu için geçişleri uygular.
#     2.8. check_database_status           : Veritabanının mevcut durumunu kontrol eder.
#
# 3.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
#     3.1. initialize_database             : Veritabanını başlatır ve tabloları oluşturur.
#     3.2. migrate_database                : Veritabanı geçişlerini uygular.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
from app.models.base import DatabaseConnection # Temel veritabanı bağlantı sınıfı
from mysql.connector import Error as MySQLError # MySQL hata yakalama
from typing import Tuple, List, Dict, Any, Callable # Tip ipuçları
import json # JSON işlemleri için

# =============================================================================
# 2.0 DATABASEMIGRATIONS SINIFI (DATABASEMIGRATIONS CLASS)
# =============================================================================
class DatabaseMigrations:
    """Veritabanı tablo oluşturma ve geçiş işlemleri için sınıf."""

    # -------------------------------------------------------------------------
    # 2.1. Yapıcı Metot (__init__)
    # -------------------------------------------------------------------------
    def __init__(self):
        """DatabaseMigrations sınıfını başlatır."""
        self.db = DatabaseConnection()

    # -------------------------------------------------------------------------
    # 2.2. Tüm veritabanı tablolarını oluşturur (create_all_tables)
    # -------------------------------------------------------------------------
    def create_all_tables(self) -> bool:
        """
        Gerekli tüm veritabanı tablolarını oluşturur.
        Returns:
            bool: Tüm tablolar başarıyla oluşturulduysa True, aksi halde False.
        """
        all_created_successfully = True
        try:
            self.db._ensure_connection()
            if not self._create_table_if_not_exists(self.create_categories_table, "ai_categories"):
                all_created_successfully = False
            if not self._create_table_if_not_exists(self.create_models_table, "ai_models"):
                all_created_successfully = False
            if not self._create_table_if_not_exists(self.create_user_messages_table, "user_messages"):
                all_created_successfully = False
            return all_created_successfully
        except MySQLError:
            # Hata detayları artık doğrudan ilgili metotlarda ele alınıyor.
            # Burada genel bir hata durumu olarak False dönülebilir.
            return False
        finally:
            self.db.close()

    # -------------------------------------------------------------------------
    # 2.3. Bir tabloyu yoksa oluşturan yardımcı metot (_create_table_if_not_exists)
    # -------------------------------------------------------------------------
    def _create_table_if_not_exists(self, creation_method: Callable[[], bool], table_name: str) -> bool:
        """
        Belirtilen tablo oluşturma metodunu çağırarak tabloyu oluşturur.
        Args:
            creation_method (Callable[[], bool]): Tabloyu oluşturan metot.
            table_name (str): Oluşturulacak tablonun adı (loglama için).
        Returns:
            bool: Tablo başarıyla oluşturulduysa veya zaten mevcutsa True.
        """
        if not creation_method():
            # Hata mesajı artık creation_method içinde veriliyor.
            return False
        return True

    # -------------------------------------------------------------------------
    # 2.4. 'ai_categories' tablosunu oluşturur (create_categories_table)
    # -------------------------------------------------------------------------
    def create_categories_table(self) -> bool:
        """
        'ai_categories' tablosunu, eğer mevcut değilse oluşturur.
        Returns:
            bool: Tablo başarıyla oluşturulduysa True, aksi halde False.
        """
        try:
            self.db._ensure_connection()
            if self.db.cursor is None:
                # Cursor None ise, bağlantı düzgün kurulmamış olabilir.
                return False
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL COMMENT 'Kategori adı',
                    icon VARCHAR(255) COMMENT 'Kategori ikonu (örn: FontAwesome sınıfı)'
                ) COMMENT = 'AI kategorilerini saklar';
            """)
            if self.db.connection: self.db.connection.commit()
            return True
        except MySQLError:
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                except MySQLError:
                    pass # Rollback hatasını yoksay
            return False

    # -------------------------------------------------------------------------
    # 2.5. 'ai_models' tablosunu oluşturur/günceller (create_models_table)
    # -------------------------------------------------------------------------
    def create_models_table(self) -> bool:
        """
        'ai_models' tablosunu, eğer mevcut değilse oluşturur veya mevcutsa günceller.
        Yeni alanlar: service_provider, external_model_name, prompt_template, status.
        Returns:
            bool: Tablo başarıyla oluşturuldu/güncellendiyse True, aksi halde False.
        """
        try:
            self.db._ensure_connection()
            if self.db.cursor is None: return False

            create_table_query = """
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Benzersiz tanımlayıcı',
                    category_id INT COMMENT 'Bağlı olduğu kategori ID',
                    name VARCHAR(255) NOT NULL COMMENT 'Kullanıcı dostu model adı',
                    icon VARCHAR(100) COMMENT 'Model ikonu (örn: fas fa-robot)',
                    description TEXT COMMENT 'Modelin kısa açıklaması',
                    details JSON COMMENT 'Model hakkında daha detaylı bilgi (JSON formatında)',
                    service_provider VARCHAR(100) COMMENT 'Hangi AI servisi sağlayıcısı (openai, gemini_sdk, custom_rest vb.)',
                    external_model_name VARCHAR(255) COMMENT 'Servis sağlayıcının kendi içindeki model adı (gpt-4o, gemini-1.5-pro)',
                    api_url VARCHAR(2048) COMMENT 'API endpoint URL (custom_rest veya farklı base_url için)',
                    request_method VARCHAR(10) DEFAULT 'POST' COMMENT 'HTTP istek metodu (GET, POST, vb.)',
                    request_headers JSON COMMENT 'İstek başlıkları (JSON formatında)',
                    request_body JSON COMMENT 'İstek gövdesi şablonu (JSON formatında)',
                    response_path VARCHAR(255) COMMENT 'JSON yanıtından veri çıkarma yolu (custom_rest için)',
                    api_key VARCHAR(512) COMMENT 'API anahtarı (İleride güvenli referans sistemi kullanılmalı)',
                    prompt_template TEXT COMMENT 'Model için varsayılan prompt şablonu',
                    status VARCHAR(50) DEFAULT 'active' COMMENT 'Modelin durumu (active, inactive, beta)',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Oluşturulma tarihi',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Güncellenme tarihi',
                    FOREIGN KEY (category_id) REFERENCES ai_categories(id)
                        ON DELETE SET NULL
                        ON UPDATE CASCADE,
                    INDEX idx_category_id (category_id),
                    INDEX idx_name (name),
                    INDEX idx_service_provider (service_provider)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='AI modellerini ve API yapılandırmalarını saklar (Revize Edilmiş)';
            """
            self.db.cursor.execute(create_table_query)

            alter_statements_modify = [
                "ALTER TABLE ai_models MODIFY COLUMN name VARCHAR(255) NOT NULL COMMENT 'Kullanıcı dostu model adı'",
                "ALTER TABLE ai_models MODIFY COLUMN icon VARCHAR(100) COMMENT 'Model ikonu (örn: fas fa-robot)'",
                "ALTER TABLE ai_models MODIFY COLUMN description TEXT COMMENT 'Modelin kısa açıklaması'",
                "ALTER TABLE ai_models MODIFY COLUMN details JSON COMMENT 'Model hakkında daha detaylı bilgi (JSON formatında)'",
                "ALTER TABLE ai_models MODIFY COLUMN api_url VARCHAR(2048) COMMENT 'API endpoint URL (custom_rest veya farklı base_url için)'",
                "ALTER TABLE ai_models MODIFY COLUMN request_method VARCHAR(10) DEFAULT 'POST' COMMENT 'HTTP istek metodu (GET, POST, vb.)'",
                "ALTER TABLE ai_models MODIFY COLUMN request_headers JSON COMMENT 'İstek başlıkları (JSON formatında)'",
                "ALTER TABLE ai_models MODIFY COLUMN request_body JSON COMMENT 'İstek gövdesi şablonu (JSON formatında)'",
                "ALTER TABLE ai_models MODIFY COLUMN response_path VARCHAR(255) COMMENT 'JSON yanıtından veri çıkarma yolu (custom_rest için)'",
                "ALTER TABLE ai_models MODIFY COLUMN api_key VARCHAR(512) COMMENT 'API anahtarı (İleride güvenli referans sistemi kullanılmalı)'",
            ]

            alter_statements_add = [
                ("service_provider", "VARCHAR(100) COMMENT 'Hangi AI servisi sağlayıcısı (openai, gemini_sdk, custom_rest vb.)' AFTER details"),
                ("external_model_name", "VARCHAR(255) COMMENT 'Servis sağlayıcının kendi içindeki model adı (gpt-4o, gemini-1.5-pro)' AFTER service_provider"),
                ("prompt_template", "TEXT COMMENT 'Model için varsayılan prompt şablonu' AFTER api_key"),
                ("status", "VARCHAR(50) DEFAULT 'active' COMMENT 'Modelin durumu (active, inactive, beta)' AFTER prompt_template"),
            ]

            if self.db.connection:
                self.db.cursor.execute(f"SELECT COUNT(*) AS count FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'ai_models'")
                result = self.db.cursor.fetchone()
                table_exists = result and result.get('count', 0) > 0

                if table_exists:
                    for stmt in alter_statements_modify:
                        try:
                            self.db.cursor.execute(stmt)
                        except MySQLError: # Hataları yoksay (sütun zaten doğru formatta olabilir)
                            pass
                    for col_name, col_definition in alter_statements_add:
                        try:
                            self.db.cursor.execute(f"SELECT COUNT(*) AS count FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ai_models' AND column_name = '{col_name}'")
                            result = self.db.cursor.fetchone()
                            column_exists = result and result.get('count', 0) > 0
                            if not column_exists:
                                self.db.cursor.execute(f"ALTER TABLE ai_models ADD COLUMN {col_name} {col_definition}")
                        except MySQLError: # Hataları yoksay
                            pass
                    try:
                        self.db.cursor.execute("SHOW INDEX FROM ai_models WHERE Key_name = 'idx_service_provider'")
                        if not self.db.cursor.fetchone():
                            self.db.cursor.execute("ALTER TABLE ai_models ADD INDEX idx_service_provider (service_provider)")
                    except MySQLError: # Hataları yoksay
                        pass
                self.db.connection.commit()
            return True
        except MySQLError:
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                except MySQLError: pass
            return False

    # -------------------------------------------------------------------------
    # 2.6. 'user_messages' tablosunu oluşturur/günceller (create_user_messages_table)
    # -------------------------------------------------------------------------
    def create_user_messages_table(self) -> bool:
        """
        'user_messages' tablosunu, eğer mevcut değilse oluşturur ve gerekli sütunları ekler/günceller.
        Returns:
            bool: Tablo başarıyla oluşturuldu/güncellendiyse True, aksi halde False.
        """
        try:
            self.db._ensure_connection()
            if self.db.cursor is None: return False

            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255) COMMENT 'Kullanıcı oturum tanımlayıcısı',
                    user_id VARCHAR(255) COMMENT 'Kullanıcı tanımlayıcısı (giriş yapmışsa)',
                    user_message TEXT COMMENT 'Kullanıcı tarafından gönderilen mesaj',
                    prompt TEXT COMMENT 'AIya gönderilen tam prompt (geçmişi içerebilir)',
                    ai_response TEXT COMMENT 'AIdan gelen yanıt',
                    ai_model_name VARCHAR(255) COMMENT 'Kullanılan AI modelinin adı (örn: gpt-4o, gemini-1.5-pro)',
                    model_id_used INT COMMENT 'Kullanılan ai_models tablosundaki modelin IDsi',
                    model_params JSON COMMENT 'AI modeli için kullanılan parametrelerin JSON dizesi',
                    request_json JSON COMMENT 'AIya gönderilen gerçek isteğin JSON dizesi',
                    response_json JSON COMMENT 'AIdan gelen gerçek yanıtın JSON dizesi',
                    tokens INT COMMENT 'Etkileşim için kullanılan token sayısı',
                    duration FLOAT COMMENT 'AI çağrısının saniye cinsinden süresi',
                    error_message TEXT COMMENT 'AI çağrısı başarısız olursa hata mesajı',
                    status VARCHAR(50) COMMENT 'Mesajın durumu (örn: success, error, pending)',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Mesajın zaman damgası',
                    FOREIGN KEY (model_id_used) REFERENCES ai_models(id) ON DELETE SET NULL
                ) COMMENT = 'Kullanıcıların AI modelleriyle etkileşimlerini saklar (Revize Edilmiş)';
            """)

            # Sütun varlığını kontrol et ve ekle/güncelle
            columns_to_ensure = {
                "model_id_used": "INT COMMENT 'Kullanılan ai_models tablosundaki modelin IDsi' AFTER ai_model_name",
            }
            foreign_keys_to_ensure = {
                "fk_user_messages_model_id": "FOREIGN KEY (model_id_used) REFERENCES ai_models(id) ON DELETE SET NULL"
            }
            columns_to_modify = {
                 "ai_model_name": "VARCHAR(255) COMMENT 'Kullanılan AI modelinin adı (örn: gpt-4o, gemini-1.5-pro)'"
            }

            for col_name, col_definition in columns_to_ensure.items():
                try:
                    self.db.cursor.execute(f"SELECT COUNT(*) AS count FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'user_messages' AND column_name = '{col_name}'")
                    result = self.db.cursor.fetchone()
                    if not (result and result.get('count', 0) > 0):
                        self.db.cursor.execute(f"ALTER TABLE user_messages ADD COLUMN {col_name} {col_definition}")
                except MySQLError: pass # Hataları yoksay

            for fk_name, fk_definition in foreign_keys_to_ensure.items():
                try:
                    self.db.cursor.execute(f"SELECT COUNT(*) AS count FROM information_schema.table_constraints WHERE constraint_schema = DATABASE() AND table_name = 'user_messages' AND constraint_name = '{fk_name}' AND constraint_type = 'FOREIGN KEY'")
                    result = self.db.cursor.fetchone()
                    if not (result and result.get('count', 0) > 0):
                         # Önce sütunun var olduğundan emin olalım (model_id_used)
                        self.db.cursor.execute(f"SELECT COUNT(*) AS count FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'user_messages' AND column_name = 'model_id_used'")
                        col_exists_result = self.db.cursor.fetchone()
                        if col_exists_result and col_exists_result.get('count', 0) > 0:
                            self.db.cursor.execute(f"ALTER TABLE user_messages ADD CONSTRAINT {fk_name} {fk_definition}")
                except MySQLError: pass # Hataları yoksay

            for col_name, col_definition in columns_to_modify.items():
                try:
                    self.db.cursor.execute(f"ALTER TABLE user_messages MODIFY COLUMN {col_name} {col_definition}")
                except MySQLError: pass # Hataları yoksay


            if self.db.connection: self.db.connection.commit()
            return True
        except MySQLError:
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                except MySQLError: pass
            return False

    # -------------------------------------------------------------------------
    # 2.7. 'user_messages' tablosu için geçişleri uygular (migrate_user_messages_table)
    # -------------------------------------------------------------------------
    def migrate_user_messages_table(self) -> Tuple[bool, List[str]]:
        """
        'user_messages' tablosu için gerekli geçişleri uygular.
        Şu anda bu metot, create_user_messages_table içindeki güncellemeler nedeniyle
        ek bir işlem yapmamaktadır.
        Returns:
            Tuple[bool, List[str]]: Başarı durumu ve eklenen sütunların listesi.
        """
        # create_user_messages_table zaten idempotent güncellemeleri yapıyor.
        return True, []

    # -------------------------------------------------------------------------
    # 2.8. Veritabanının mevcut durumunu kontrol eder (check_database_status)
    # -------------------------------------------------------------------------
    def check_database_status(self) -> Dict[str, Any]:
        """
        Veritabanının ve ana tabloların durumunu kontrol eder.
        Returns:
            Dict[str, Any]: Veritabanı durumu hakkında bilgi içeren bir sözlük.
        """
        status: Dict[str, Any] = {
            'database_name': None,
            'tables': {},
            'row_counts': {},
            'connection_status': 'Bağlantı Kesik',
            'overall_success': False
        }
        try:
            self.db._ensure_connection()
            status['connection_status'] = 'Bağlı'
            if self.db.connection and self.db.cursor:
                status['database_name'] = self.db.connection.database

                tables_to_check = ['ai_categories', 'ai_models', 'user_messages']
                for table_name in tables_to_check:
                    try:
                        self.db.cursor.execute(f"SELECT COUNT(*) AS count FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = %s", (table_name,))
                        table_info = self.db.cursor.fetchone()
                        table_exists = table_info['count'] > 0 if table_info else False

                        if table_exists:
                            self.db.cursor.execute(f"DESCRIBE {table_name}")
                            columns_data = self.db.cursor.fetchall()
                            column_details = {
                                col['Field']: {
                                    'type': col['Type'], 'null': col['Null'],
                                    'key': col['Key'], 'default': col['Default'],
                                    'extra': col['Extra']
                                } for col in columns_data
                            } if columns_data else {}
                            status['tables'][table_name] = {'exists': True, 'column_count': len(columns_data or []), 'columns': column_details}

                            self.db.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                            count_result = self.db.cursor.fetchone()
                            status['row_counts'][table_name] = count_result['count'] if count_result else 0
                        else:
                            status['tables'][table_name] = {'exists': False, 'column_count': 0, 'columns': {}}
                            status['row_counts'][table_name] = 0
                    except MySQLError as e:
                        status['tables'][table_name] = {'exists': False, 'error': str(e)}
                        status['row_counts'][table_name] = 0
                status['overall_success'] = True
        except MySQLError as e:
            status['connection_status'] = f"Hata: {str(e)}"
            status['overall_success'] = False
        finally:
            self.db.close()
        return status

# =============================================================================
# 3.0 YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# =============================================================================

# -------------------------------------------------------------------------
# 3.1. Veritabanını başlatır ve tabloları oluşturur (initialize_database)
# -------------------------------------------------------------------------
def initialize_database() -> bool:
    """
    DatabaseMigrations sınıfını kullanarak veritabanını başlatır ve tüm tabloları oluşturur.
    Returns:
        bool: Başarılı olursa True, aksi halde False.
    """
    migrations = DatabaseMigrations()
    success = migrations.create_all_tables()
    # Başarı/hata mesajları artık doğrudan çağrılan metotlarda veya loglama ile ele alınabilir.
    return success

# -------------------------------------------------------------------------
# 3.2. Veritabanı geçişlerini uygular (migrate_database)
# -------------------------------------------------------------------------
def migrate_database() -> Tuple[bool, List[str]]:
    """
    DatabaseMigrations sınıfını kullanarak veritabanı geçişlerini uygular.
    Returns:
        Tuple[bool, List[str]]: Başarı durumu ve eklenen sütunların listesi.
    """
    migrations = DatabaseMigrations()
    success_user_messages, added_cols_user_messages = migrations.migrate_user_messages_table()
    # Diğer geçişler buraya eklenebilir.
    return success_user_messages, added_cols_user_messages

if __name__ == '__main__':
    # Bu blok, modül doğrudan çalıştırıldığında test veya başlatma işlemleri için kullanılır.
    # print() çağrıları, bu özel __main__ bloğu içinde test amaçlı kalabilir,
    # ancak modül bir uygulamanın parçası olarak içe aktarıldığında çalışmazlar.
    # Uygulama genelinde loglama tercih edilmelidir.
    print("Veritabanı işlemleri başlatılıyor (migrations.py doğrudan çalıştırıldı)...")
    if initialize_database():
        print("Veritabanı başarıyla başlatıldı/kontrol edildi.")
        mig_success, mig_cols = migrate_database()
        if mig_success:
            if mig_cols:
                print(f"Veritabanı geçişi başarılı. Eklenen/değiştirilen sütunlar (user_messages): {', '.join(mig_cols)}")
            else:
                print("Veritabanı geçişi kontrol edildi, user_messages için ek işlem yapılmadı.")
        else:
            print("Veritabanı geçişi başarısız oldu.")

        print("\nVeritabanı durumu kontrol ediliyor...")
        db_status_checker = DatabaseMigrations() # Yeni bir örnek, çünkü önceki bağlantıyı kapattı.
        db_status = db_status_checker.check_database_status()
        print("Veritabanı Durumu:")
        print(json.dumps(db_status, indent=4, ensure_ascii=False)) # Detaylı JSON çıktısı
    else:
        print("Veritabanı başlatma veya tablo oluşturma başarısız oldu.")
