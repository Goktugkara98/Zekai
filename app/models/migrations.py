# =============================================================================
# Veritabanı Geçişleri Modülü (Database Migrations Module)
# =============================================================================
# Bu modül, veritabanı tablolarının oluşturulması, güncellenmesi (geçişler)
# ve veritabanı durumunun kontrol edilmesi gibi işlemleri yönetir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. DatabaseMigrations Sınıfı
#    2.1. __init__                       : Başlatıcı metot.
#    2.2. create_all_tables              : Gerekli tüm veritabanı tablolarını oluşturur.
#    2.3. create_categories_table        : 'ai_categories' tablosunu oluşturur.
#    2.4. create_models_table            : 'ai_models' tablosunu oluşturur.
#    2.5. create_user_messages_table     : 'user_messages' tablosunu oluşturur.
#    2.6. migrate_user_messages_table    : 'user_messages' tablosuna yeni sütunlar ekler (basit geçiş).
#    2.7. check_database_status          : Veritabanı durumunu kontrol eder (tablo varlığı, satır sayıları).
# 3. Yardımcı Fonksiyonlar (Helper Functions)
#    3.1. initialize_database            : Veritabanını başlatır ve tabloları oluşturur.
#    3.2. migrate_database               : Veritabanı geçişlerini çalıştırır.
#    3.3. main (Örnek Çalıştırma Bloğu)   : Modülün doğrudan çalıştırılması durumunda örnek işlemler yapar.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import DatabaseConnection # Temel veritabanı bağlantı sınıfı
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi, daha belirgin olması için yeniden adlandırıldı
from typing import Tuple, List, Dict, Any
import json # check_database_status sonuçlarını formatlı yazdırmak için

# 2. DatabaseMigrations Sınıfı
# =============================================================================
class DatabaseMigrations:
    """Veritabanı tablo oluşturma ve geçiş işlemleri için sınıf."""

    # 2.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self):
        """DatabaseMigrations sınıfını başlatır."""
        self.db = DatabaseConnection()
        # print("DEBUG: DatabaseMigrations örneği oluşturuldu.")

    # 2.2. create_all_tables
    # -------------------------------------------------------------------------
    def create_all_tables(self) -> bool:
        """
        Gerekli tüm veritabanı tablolarını, eğer mevcut değillerse oluşturur.
        Yabancı anahtar kısıtlamaları nedeniyle oluşturma sırası önemlidir.
        Returns:
            bool: Tüm tablolar başarıyla oluşturulduysa True, aksi takdirde False.
        """
        all_created_successfully = True
        # print("DEBUG: Tüm tablolar oluşturuluyor...")
        try:
            self.db._ensure_connection() # Bağlantının aktif olduğundan emin ol

            # Tablo oluşturma sırası önemli (yabancı anahtar kısıtlamaları nedeniyle)
            if not self._create_table_if_not_exists(self.create_categories_table, "ai_categories"):
                all_created_successfully = False
            if not self._create_table_if_not_exists(self.create_models_table, "ai_models"):
                all_created_successfully = False
            if not self._create_table_if_not_exists(self.create_user_messages_table, "user_messages"):
                all_created_successfully = False

            if all_created_successfully:
                # print("DEBUG: Tüm tablolar başarıyla kontrol edildi/oluşturuldu.")
                pass
            else:
                # print("DEBUG: Bazı tablolar oluşturulurken hata oluştu.")
                pass
            return all_created_successfully
        except MySQLError as e:
            # print(f"DEBUG: create_all_tables sırasında genel hata: {e}")
            return False
        finally:
            self.db.close() # Bağlantıyı her zaman kapat

    def _create_table_if_not_exists(self, creation_method: callable, table_name: str) -> bool:
        """Belirli bir tablo oluşturma metodunu çağırır ve sonucu loglar."""
        # print(f"DEBUG: '{table_name}' tablosu kontrol ediliyor/oluşturuluyor...")
        if not creation_method():
            # print(f"DEBUG: '{table_name}' tablosu oluşturulamadı.")
            return False
        # print(f"DEBUG: '{table_name}' tablosu başarıyla kontrol edildi/oluşturuldu.")
        return True

    # 2.3. create_categories_table
    # -------------------------------------------------------------------------
    def create_categories_table(self) -> bool:
        """'ai_categories' tablosunu, eğer mevcut değilse oluşturur."""
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL COMMENT 'Kategori adı',
                    icon VARCHAR(255) COMMENT 'Kategori ikonu (örn: FontAwesome sınıfı)'
                ) COMMENT = 'AI kategorilerini saklar';
            """)
            if self.db.connection: self.db.connection.commit()
            return True
        except MySQLError as e:
            # print(f"DEBUG: 'ai_categories' tablosu oluşturulurken hata: {e}")
            if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()
            return False

    # 2.4. create_models_table
    # -------------------------------------------------------------------------
    def create_models_table(self) -> bool:
        """'ai_models' tablosunu, eğer mevcut değilse oluşturur.
        
        Tablo yapısı:
        - id: Benzersiz tanımlayıcı (otomatik artan)
        - category_id: Bağlı olduğu kategorinin ID'si
        - name: Modelin adı
        - icon: Model ikonu (Font Awesome sınıfı)
        - description: Modelin kısa açıklaması
        - details: Model hakkında daha detaylı bilgi (JSON formatında)
        - api_url: API endpoint URL'si
        - request_method: HTTP istek metodu (GET, POST, vb.)
        - request_headers: İstek başlıkları (JSON formatında)
        - request_body: İstek gövdesi şablonu (JSON formatında)
        - response_path: JSON yanıtından veri çıkarma yolu (örn: 'choices.0.message.content')
        - api_key: API anahtarı (geliştirme aşamasında doğrudan, sonra şifrelenmiş)
        - created_at: Oluşturulma tarihi
        - updated_at: Güncellenme tarihi
        """
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Benzersiz tanımlayıcı',
                    category_id INT COMMENT 'Bağlı olduğu kategori ID',
                    name VARCHAR(255) NOT NULL COMMENT 'Model adı',
                    icon VARCHAR(100) COMMENT 'Model ikonu (örn: fas fa-robot)',
                    description TEXT COMMENT 'Modelin kısa açıklaması',
                    details JSON COMMENT 'Model hakkında daha detaylı bilgi (JSON formatında)',
                    api_url VARCHAR(2048) COMMENT 'API endpoint URL',
                    request_method VARCHAR(10) DEFAULT 'POST' COMMENT 'HTTP istek metodu (GET, POST, PUT, DELETE)',
                    request_headers JSON COMMENT 'İstek başlıkları (JSON formatında)',
                    request_body JSON COMMENT 'İstek gövdesi şablonu (JSON formatında)',
                    response_path VARCHAR(255) COMMENT 'JSON yanıtından veri çıkarma yolu',
                    api_key VARCHAR(512) COMMENT 'API anahtarı (geliştirme için düz metin, sonra şifrelenecek)',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Oluşturulma tarihi',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Güncellenme tarihi',
                    FOREIGN KEY (category_id) REFERENCES ai_categories(id)
                        ON DELETE SET NULL  -- Kategori silinirse modelin category_id'si NULL olur
                        ON UPDATE CASCADE,  -- Kategori ID'si güncellenirse buradaki de güncellenir
                    INDEX idx_category_id (category_id),
                    INDEX idx_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                COMMENT='AI modellerini ve API yapılandırmalarını saklar';
            """)
            
            # Mevcut tabloyu yeni sütunlarla güncellemek için ALTER TABLE sorguları (eğer tablo zaten varsa)
            # Bu, idempotent bir şekilde sütunların varlığını kontrol eder ve yoksa ekler/değiştirir.
            alter_statements = [
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS description TEXT COMMENT 'Modelin kısa açıklaması' AFTER icon",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS details JSON COMMENT 'Model hakkında daha detaylı bilgi (JSON formatında)' AFTER description",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS api_url VARCHAR(2048) COMMENT 'API endpoint URL' AFTER details",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS request_method VARCHAR(10) DEFAULT 'POST' COMMENT 'HTTP istek metodu (GET, POST, PUT, DELETE)' AFTER api_url",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS request_headers JSON COMMENT 'İstek başlıkları (JSON formatında)' AFTER request_method",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS request_body JSON COMMENT 'İstek gövdesi şablonu (JSON formatında)' AFTER request_headers",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS response_path VARCHAR(255) COMMENT 'JSON yanıtından veri çıkarma yolu' AFTER request_body",
                "ALTER TABLE ai_models ADD COLUMN IF NOT EXISTS api_key VARCHAR(512) COMMENT 'API anahtarı (geliştirme için düz metin, sonra şifrelenecek)' AFTER response_path",
                "ALTER TABLE ai_models MODIFY COLUMN icon VARCHAR(100) COMMENT 'Model ikonu (örn: fas fa-robot)'", # Varolan sütunun tipini/commentini güncellemek
                "ALTER TABLE ai_models MODIFY COLUMN name VARCHAR(255) NOT NULL COMMENT 'Model adı'",
            ]
            
            if self.db.connection: # Bağlantının varlığından emin ol
                # Tablonun var olup olmadığını kontrol et
                self.db.cursor.execute(f"""
                    SELECT COUNT(*) AS count
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE() AND table_name = 'ai_models'
                """)
                table_exists = self.db.cursor.fetchone()['count'] > 0

                if table_exists:
                    for alter_query in alter_statements:
                        try:
                            # print(f"DEBUG: ALTER TABLE sorgusu çalıştırılıyor: {alter_query}")
                            self.db.cursor.execute(alter_query)
                        except MySQLError as e:
                            # print(f"UYARI: '{alter_query}' sorgusu çalıştırılırken hata (muhtemelen sütun zaten var veya uyumsuz değişiklik): {e}")
                            # Hata "Duplicate column name" ise veya "Column already exists" ise genellikle güvenle yoksayılabilir.
                            # Diğer hatalar için loglama/inceleme gerekebilir.
                            if "Duplicate column name" not in str(e) and "already exists" not in str(e):
                                # print(f"KRİTİK UYARI: Beklenmedik ALTER TABLE hatası: {e}")
                                pass # Geliştirme aşamasında bu tür hataları yoksayabiliriz, ancak üretimde dikkatli olunmalı.
                
                self.db.connection.commit()
            return True
        except MySQLError as e:
            # print(f"DEBUG: 'ai_models' tablosu oluşturulurken/güncellenirken hata: {e}")
            if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()
            return False

    # 2.5. create_user_messages_table
    # -------------------------------------------------------------------------
    def create_user_messages_table(self) -> bool:
        """'user_messages' tablosunu, eğer mevcut değilse oluşturur."""
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255) COMMENT 'Kullanıcı oturum tanımlayıcısı',
                    user_id VARCHAR(255) COMMENT 'Kullanıcı tanımlayıcısı (giriş yapmışsa)',
                    user_message TEXT COMMENT 'Kullanıcı tarafından gönderilen mesaj',
                    prompt TEXT COMMENT 'AIya gönderilen tam prompt (geçmişi içerebilir)',
                    ai_response TEXT COMMENT 'AIdan gelen yanıt',
                    ai_model_name VARCHAR(255) COMMENT 'Kullanılan AI modelinin adı (data_ai_index olabilir)',
                    model_params JSON COMMENT 'AI modeli için kullanılan parametrelerin JSON dizesi',
                    request_json JSON COMMENT 'AIya gönderilen gerçek isteğin JSON dizesi',
                    response_json JSON COMMENT 'AIdan gelen gerçek yanıtın JSON dizesi',
                    tokens INT COMMENT 'Etkileşim için kullanılan token sayısı',
                    duration FLOAT COMMENT 'AI çağrısının saniye cinsinden süresi',
                    error_message TEXT COMMENT 'AI çağrısı başarısız olursa hata mesajı',
                    status VARCHAR(50) COMMENT 'Mesajın durumu (örn: success, error, pending)',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Mesajın zaman damgası'
                ) COMMENT = 'Kullanıcıların AI modelleriyle etkileşimlerini saklar';
            """)
            if self.db.connection: self.db.connection.commit()
            return True
        except MySQLError as e:
            # print(f"DEBUG: 'user_messages' tablosu oluşturulurken hata: {e}")
            if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()
            return False

    # 2.6. migrate_user_messages_table
    # -------------------------------------------------------------------------
    def migrate_user_messages_table(self) -> Tuple[bool, List[str]]:
        """
        'user_messages' tablosuna, eğer mevcut değillerse yeni sütunlar ekler.
        Bu basit bir geçiş örneğidir; daha karmaşık geçişler için özel bir kütüphane gerekebilir.
        Returns:
            Tuple[bool, List[str]]: (başarı_durumu, eklenen_sütunların_listesi)
        """
        added_columns = []
        migration_successful = True
        # print("DEBUG: 'user_messages' tablosu için geçiş başlatılıyor...")
        try:
            self.db._ensure_connection()
            columns_to_add = [] # Bu örnekte user_messages için yeni sütun eklenmiyor.

            if not columns_to_add:
                # print("DEBUG: 'user_messages' tablosuna eklenecek yeni sütun tanımlanmamış.")
                return True, [] 

            for col_name, col_type, col_position, col_comment in columns_to_add:
                try:
                    self.db.cursor.execute(f"""
                        SELECT COUNT(*) AS count
                        FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = 'user_messages'
                        AND COLUMN_NAME = %s;
                    """, (col_name,))
                    if self.db.cursor.fetchone()['count'] == 0:
                        # print(f"DEBUG: '{col_name}' sütunu 'user_messages' tablosuna ekleniyor...")
                        self.db.cursor.execute(
                            f"ALTER TABLE user_messages ADD COLUMN {col_name} {col_type} "
                            f"COMMENT %s {col_position};", (col_comment,)
                        )
                        added_columns.append(col_name)
                    else:
                        # print(f"DEBUG: '{col_name}' sütunu 'user_messages' tablosunda zaten mevcut.")
                        pass
                except MySQLError as e:
                    # print(f"DEBUG: '{col_name}' sütunu 'user_messages' tablosuna eklenirken hata: {e}")
                    migration_successful = False 
            
            if migration_successful and added_columns:
                if self.db.connection: self.db.connection.commit()
            elif not added_columns and migration_successful:
                pass
            else: 
                if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()

            return migration_successful, added_columns
        except MySQLError as e:
            # print(f"DEBUG: migrate_user_messages_table sırasında genel hata: {e}")
            if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()
            return False, added_columns 
        finally:
            self.db.close()

    # 2.7. check_database_status
    # -------------------------------------------------------------------------
    def check_database_status(self) -> Dict[str, Any]:
        """
        Veritabanının durumunu kontrol eder; tablo varlığı ve satır sayıları dahil.
        Returns:
            Dict[str, Any]: Veritabanı durumu hakkında bilgi içeren bir sözlük.
        """
        status = {
            'database_name': None,
            'tables': {},
            'row_counts': {},
            'connection_status': 'Bağlantı Kesik',
            'overall_success': False
        }
        # print("DEBUG: Veritabanı durumu kontrol ediliyor...")
        try:
            self.db._ensure_connection()
            status['connection_status'] = 'Bağlı' 
            if self.db.connection: 
                status['database_name'] = self.db.connection.database

            tables_to_check = ['ai_categories', 'ai_models', 'user_messages']
            for table_name in tables_to_check:
                try:
                    self.db.cursor.execute(f"""
                        SELECT COUNT(*) AS count
                        FROM information_schema.tables
                        WHERE table_schema = DATABASE() AND table_name = %s
                    """, (table_name,))
                    table_exists = self.db.cursor.fetchone()['count'] > 0

                    if table_exists:
                        self.db.cursor.execute(f"DESCRIBE {table_name}")
                        columns_data = self.db.cursor.fetchall()
                        column_details = {
                            col['Field']: {
                                'type': col['Type'],
                                'null': col['Null'],
                                'key': col['Key'],
                                'default': col['Default'],
                                'extra': col['Extra']
                            } for col in columns_data
                        }
                        status['tables'][table_name] = {
                            'exists': True,
                            'column_count': len(columns_data),
                            'columns': column_details
                        }
                        self.db.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                        count_result = self.db.cursor.fetchone()
                        status['row_counts'][table_name] = count_result['count'] if count_result else 0
                    else:
                        status['tables'][table_name] = {'exists': False, 'column_count': 0, 'columns': {}}
                        status['row_counts'][table_name] = 0
                except MySQLError as e:
                    # print(f"DEBUG: '{table_name}' tablosu kontrol edilirken hata: {e}")
                    status['tables'][table_name] = {'exists': False, 'error': str(e)}
                    status['row_counts'][table_name] = 0
            status['overall_success'] = True 
        except MySQLError as e:
            # print(f"DEBUG: check_database_status içinde veritabanı bağlantı hatası: {e}")
            status['connection_status'] = f"Hata: {str(e)}"
            status['overall_success'] = False 
        finally:
            self.db.close()
        # print(f"DEBUG: Veritabanı durumu: {json.dumps(status, indent=2, ensure_ascii=False)}")
        return status

# 3. Yardımcı Fonksiyonlar (Helper Functions)
# =============================================================================

# 3.1. initialize_database
# -----------------------------------------------------------------------------
def initialize_database() -> bool:
    """
    Veritabanını başlatır ve gerekli tabloları oluşturur.
    Returns:
        bool: Tüm tablolar başarıyla oluşturulduysa True, aksi takdirde False.
    """
    # print("INFO: Veritabanı başlatılıyor...")
    migrations = DatabaseMigrations()
    success = migrations.create_all_tables()
    if success:
        # print("INFO: Veritabanı başarıyla başlatıldı.")
        pass
    else:
        # print("ERROR: Veritabanı başlatma başarısız oldu.")
        pass
    return success

# 3.2. migrate_database
# -----------------------------------------------------------------------------
def migrate_database() -> Tuple[bool, List[str]]:
    """
    Veritabanı geçişlerini çalıştırır (örn: mevcut tablolara yeni sütunlar ekleme).
    Returns:
        Tuple[bool, List[str]]: (başarı_durumu, eklenen_sütunların_listesi).
    """
    # print("INFO: Veritabanı geçişi başlatılıyor...")
    migrations = DatabaseMigrations()
    # Şu anda sadece user_messages için bir geçiş fonksiyonu var, gerekirse ai_models için de eklenebilir.
    success_user_messages, added_cols_user_messages = migrations.migrate_user_messages_table()
    
    # ai_models için ayrı bir migrate fonksiyonu olsaydı burada çağrılabilirdi:
    # success_ai_models, added_cols_ai_models = migrations.migrate_ai_models_table() 
    # success = success_user_messages and success_ai_models
    # added_columns = added_cols_user_messages + added_cols_ai_models

    success = success_user_messages # Şimdilik sadece user_messages sonucunu kullanıyoruz
    added_columns = added_cols_user_messages

    if success:
        if added_columns:
            # print(f"INFO: Veritabanı geçişi başarılı. Eklenen sütunlar: {', '.join(added_columns)}")
            pass
        else:
            # print("INFO: Veritabanı geçişi kontrol edildi. Eklenecek yeni sütun yok.")
            pass
    else:
        # print("ERROR: Veritabanı geçişi başarısız oldu.")
        pass
    return success, added_columns

# 3.3. main (Örnek Çalıştırma Bloğu)
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print("Veritabanı başlatılıyor...")
    if initialize_database():
        print("Veritabanı başarıyla başlatıldı.")

        print("\nGeçişler çalıştırılıyor...")
        mig_success, mig_cols = migrate_database()
        if mig_success:
            if mig_cols:
                print(f"Geçişler uygulandı. Eklenen sütunlar: {', '.join(mig_cols)}")
            else:
                print("Uygulanacak yeni geçiş yok.")
        else:
            print("Geçişler başarısız oldu.")

        print("\nVeritabanı durumu kontrol ediliyor...")
        db_status_checker = DatabaseMigrations() 
        db_status = db_status_checker.check_database_status()
        print("Veritabanı Durumu:")
        print(json.dumps(db_status, indent=4, ensure_ascii=False)) 
    else:
        print("Veritabanı başlatma başarısız oldu.")
