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
        """'ai_models' tablosunu, eğer mevcut değilse oluşturur."""
        try:
            self.db._ensure_connection()
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category_id INT,
                    name VARCHAR(255) NOT NULL COMMENT 'Model adı',
                    icon VARCHAR(255) COMMENT 'Model ikonu',
                    data_ai_index VARCHAR(255) UNIQUE COMMENT 'AI model tanımlaması için benzersiz indeks (önceden 50 idi, genişletildi)',
                    api_url VARCHAR(2048) COMMENT 'API uç nokta URLsi',
                    description TEXT COMMENT 'Modelin açıklaması',
                    details JSON COMMENT 'Modelin diğer detayları (JSON formatında)',
                    image_filename VARCHAR(255) COMMENT 'Model için görsel dosya adı',
                    request_method VARCHAR(10) DEFAULT 'POST' COMMENT 'HTTP istek metodu',
                    request_headers JSON COMMENT 'JSON formatında istek başlıkları',
                    request_body_template JSON COMMENT 'JSON formatında istek gövdesi şablonu',
                    response_path VARCHAR(255) COMMENT 'JSONdan yanıtı ayıklama yolu (örn: candidates[0].text)',
                    FOREIGN KEY (category_id) REFERENCES ai_categories(id)
                        ON DELETE SET NULL  -- Kategori silindiğinde modellerin category_id'si NULL olur
                        ON UPDATE CASCADE   -- Kategori ID'si güncellenirse modellerdeki ID de güncellenir
                ) COMMENT = 'AI modellerini ve yapılandırmalarını saklar';
            """)
            # data_ai_index için NOT NULL kaldırıldı, çünkü create_model içinde opsiyonel olarak ele alınıyor.
            # Eğer zorunluysa, UNIQUE NOT NULL olarak kalmalı ve create_model mantığı güncellenmeli.
            # Şimdilik UNIQUE olarak bırakıldı, bu da NULL değerlerin birden fazla olmasına izin verir (genellikle istenmez).
            # Eğer data_ai_index her zaman dolu olacaksa UNIQUE NOT NULL daha uygun.
            # ON DELETE CASCADE yerine ON DELETE SET NULL kullanıldı.
            # Bu, bir kategori silindiğinde ilişkili modellerin otomatik silinmesini engeller,
            # bunun yerine category_id'lerini NULL yapar. Bu, veri kaybını önleyebilir.
            if self.db.connection: self.db.connection.commit()
            return True
        except MySQLError as e:
            # print(f"DEBUG: 'ai_models' tablosu oluşturulurken hata: {e}")
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
            # status için VARCHAR(32)'den VARCHAR(50)'ye genişletildi.
            # model_params, request_json, response_json için TEXT yerine JSON tipi kullanıldı (MySQL 5.7.8+).
            # Eğer daha eski bir MySQL sürümü kullanılıyorsa TEXT olarak kalmalı.
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
            # Eklenecek sütunlar, türleri, konumları ve yorumları
            columns_to_add = [
                # Örnek sütunlar (mevcut şemanızda zaten var gibi görünüyor, bu bölümü ihtiyaca göre güncelleyin)
                # ("new_column_example", "VARCHAR(255)", "AFTER status", "Bu yeni bir örnek sütundur"),
            ]
            # Mevcut şemanızda 'user_id', 'prompt', 'model_params', 'request_json', 'response_json',
            # 'tokens', 'duration', 'error_message', 'status' sütunları zaten var.
            # Bu nedenle, columns_to_add listesi şimdilik boş bırakıldı.
            # Eğer gerçekten eksik sütunlar varsa, yukarıdaki listeye ekleyebilirsiniz.

            if not columns_to_add:
                # print("DEBUG: 'user_messages' tablosuna eklenecek yeni sütun tanımlanmamış.")
                return True, [] # Eklenecek sütun yoksa başarılı sayılır

            for col_name, col_type, col_position, col_comment in columns_to_add:
                try:
                    # Önce sütunun var olup olmadığını kontrol et
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
                    migration_successful = False # Bir hata olursa genel başarıyı false yap
                    # if "Duplicate column name" in str(e): pass # Eğer hata zaten var olduğundan kaynaklanıyorsa yoksayılabilir

            if migration_successful and added_columns:
                if self.db.connection: self.db.connection.commit()
                # print(f"DEBUG: Geçiş başarılı. Eklenen sütunlar: {added_columns}")
            elif not added_columns and migration_successful:
                # print("DEBUG: Geçiş kontrol edildi. Eklenecek yeni sütun yok.")
                pass
            else: # Hata oluştu veya commit atlandı
                if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()
                # print("DEBUG: Geçiş sırasında hata oluştu veya değişiklik yapılmadı, rollback yapıldı.")

            return migration_successful, added_columns
        except MySQLError as e:
            # print(f"DEBUG: migrate_user_messages_table sırasında genel hata: {e}")
            if self.db.connection and self.db.connection.is_connected(): self.db.connection.rollback()
            return False, added_columns # Hata durumunda eklenen sütunlar listesi boş olabilir veya kısmi olabilir
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
            'connection_status': 'Bağlantı Kesik', # 'Disconnected' yerine Türkçe
            'overall_success': False
        }
        # print("DEBUG: Veritabanı durumu kontrol ediliyor...")
        try:
            self.db._ensure_connection()
            status['connection_status'] = 'Bağlı' # 'Connected' yerine Türkçe
            if self.db.connection: # Bağlantı nesnesinin varlığından emin ol
                status['database_name'] = self.db.connection.database

            tables_to_check = ['ai_categories', 'ai_models', 'user_messages']
            for table_name in tables_to_check:
                try:
                    # Tablonun varlığını kontrol et
                    self.db.cursor.execute(f"""
                        SELECT COUNT(*) AS count
                        FROM information_schema.tables
                        WHERE table_schema = DATABASE() AND table_name = %s
                    """, (table_name,))
                    table_exists = self.db.cursor.fetchone()['count'] > 0

                    if table_exists:
                        # Tablo yapısını (sütunları) al
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
                        # Satır sayısını al
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
            status['overall_success'] = True # Eğer buraya kadar hatasız gelindiyse genel başarı True
        except MySQLError as e:
            # print(f"DEBUG: check_database_status içinde veritabanı bağlantı hatası: {e}")
            status['connection_status'] = f"Hata: {str(e)}"
            status['overall_success'] = False # Bağlantı hatası varsa genel başarı False
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
    success, added_columns = migrations.migrate_user_messages_table()
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
    # Bu blok, modül doğrudan çalıştırıldığında (örn: python app/models/migrations.py)
    # veritabanını başlatmak, geçişleri uygulamak ve durumu kontrol etmek için kullanılır.
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
        db_status_checker = DatabaseMigrations() # Yeni bir örnek oluştur
        db_status = db_status_checker.check_database_status()
        print("Veritabanı Durumu:")
        print(json.dumps(db_status, indent=4, ensure_ascii=False)) # ensure_ascii=False Türkçe karakterler için
    else:
        print("Veritabanı başlatma başarısız oldu.")

