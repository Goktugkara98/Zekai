# =============================================================================
# Temel Veritabanı Modülü (Database Base Module)
# =============================================================================
# Bu modül, veritabanı bağlantısını yönetmek ve temel veritabanı işlemleri
# için bir temel depo (repository) sınıfı sağlamak üzere tasarlanmıştır.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. DatabaseConnection Sınıfı
#    2.1. __init__             : Başlatıcı metot.
#    2.2. connect              : Veritabanı bağlantısı kurar.
#    2.3. close                : Veritabanı bağlantısını kapatır.
#    2.4. _ensure_connection   : Bağlantının aktif olduğundan emin olur.
#    2.5. __enter__            : Context manager için giriş metodu.
#    2.6. __exit__             : Context manager için çıkış metodu.
# 3. BaseRepository Sınıfı
#    3.1. __init__             : Başlatıcı metot.
#    3.2. _ensure_connection   : Depo için bağlantının aktif olduğundan emin olur.
#    3.3. _close_if_owned      : Eğer bağlantı bu sınıf tarafından yönetiliyorsa kapatır.
#    3.4. execute_query        : Veri değiştiren sorguları (UPDATE, DELETE) çalıştırır.
#    3.5. fetch_one            : Tek bir sonuç getiren sorguyu çalıştırır.
#    3.6. fetch_all            : Tüm sonuçları getiren sorguyu çalıştırır.
#    3.7. insert               : INSERT sorgusunu çalıştırır ve son eklenen satırın ID'sini döndürür.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
import mysql.connector
from mysql.connector import Error, pooling # pooling import edilmiş ancak kullanılmıyor, gerekirse kaldırılabilir.
from app.config import DB_CONFIG # Uygulama yapılandırmasından veritabanı ayarlarını alır.
from typing import Optional, Any, Dict, List, Type # Tip ipuçları için.

# 2. DatabaseConnection Sınıfı
# =============================================================================
class DatabaseConnection:
    """
    Tek bir veritabanı bağlantısını yönetir.
    Aynı örnek, harici kilitleme olmadan thread'ler arasında paylaşılırsa
    doğası gereği thread-safe (iş parçacığı güvenli) değildir. Çoklu thread uygulamaları için,
    bir bağlantı havuzu (connection pool) kullanmayı veya her thread/görev için yeni bir örnek
    oluşturmayı düşünün.
    """

    # 2.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self):
        """DatabaseConnection sınıfını başlatır."""
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursorDict] = None # Sonuçları sözlük olarak almak için MySQLCursorDict
        self.db_config: Dict[str, Any] = DB_CONFIG
        # print("DEBUG: DatabaseConnection örneği oluşturuldu.") # Geliştirme sırasında loglama için

    # 2.2. connect
    # -------------------------------------------------------------------------
    def connect(self) -> None:
        """
        Veritabanına bir bağlantı kurar.
        Raises:
            mysql.connector.Error: Bağlantı başarısız olursa.
        """
        try:
            # print(f"DEBUG: Veritabanına bağlanmaya çalışılıyor: {self.db_config.get('database')}@{self.db_config.get('host')}")
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True) # Sonuçları sözlük olarak almak için
                # print("DEBUG: Veritabanı bağlantısı başarılı.")
            else:
                # print("DEBUG: Veritabanı bağlantısı başarısız: Bağlantı kurulamadı.")
                # Bu durum nadirdir çünkü connect() zaten Error fırlatır.
                raise Error("Veritabanına bağlanılamadı.")
        except Error as e:
            # print(f"DEBUG: Veritabanı bağlantı hatası: {e}")
            self.connection = None # Bağlantı başarısız olursa connection'ı None yap
            self.cursor = None
            raise # İstisnayı çağıran tarafından işlenmesi için yeniden fırlat

    # 2.3. close
    # -------------------------------------------------------------------------
    def close(self) -> None:
        """Veritabanı cursor'ını ve bağlantısını açıksa kapatır."""
        if self.cursor:
            try:
                self.cursor.close()
                # print("DEBUG: Veritabanı cursor'ı kapatıldı.")
            except Error as e:
                # print(f"DEBUG: Cursor kapatılırken hata: {e}")
                pass # Cursor kapatma hatalarını yoksay, ancak logla
            self.cursor = None
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
                # print("DEBUG: Veritabanı bağlantısı kapatıldı.")
            except Error as e:
                # print(f"DEBUG: Bağlantı kapatılırken hata: {e}")
                pass # Bağlantı kapatma hatalarını yoksay, ancak logla
            self.connection = None
        # print("DEBUG: DatabaseConnection kaynakları serbest bırakıldı.")

    # 2.4. _ensure_connection
    # -------------------------------------------------------------------------
    def _ensure_connection(self) -> None:
        """
        Aktif bir veritabanı bağlantısının mevcut olduğundan emin olur.
        Bağlı değilse, yeni bir bağlantı kurmaya çalışır.
        """
        if not self.connection or not self.connection.is_connected() or not self.cursor:
            # print("DEBUG: Aktif bağlantı bulunamadı veya cursor eksik. Yeniden bağlanmaya çalışılıyor...")
            self.connect()

    # 2.5. __enter__ (Context Manager)
    # -------------------------------------------------------------------------
    def __enter__(self) -> 'DatabaseConnection':
        """
        Context yönetim protokolü. Girişte bağlantıyı sağlar.
        'with DatabaseConnection() as db:' sözdizimine izin verir.
        """
        self._ensure_connection()
        return self

    # 2.6. __exit__ (Context Manager)
    # -------------------------------------------------------------------------
    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[Any]) -> None:
        """
        Context yönetim protokolü. Çıkışta bağlantıyı kapatır.
        """
        self.close()
        # if exc_type:
        #     print(f"DEBUG: 'with' bloğu içinde istisna oluştu: {exc_type}, {exc_val}")
        # İstisnaları yaymak için None (veya False), bastırmak için True döndür.

# 3. BaseRepository Sınıfı
# =============================================================================
class BaseRepository:
    """
    Tüm depo (repository) sınıfları için temel sınıf, ortak veritabanı işlemleri sağlar.
    Eğer bir bağlantı sağlanmazsa kendi veritabanı bağlantı yaşam döngüsünü yönetir.
    """

    # 3.1. __init__
    # -------------------------------------------------------------------------
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        BaseRepository sınıfını başlatır.
        Args:
            db_connection: İsteğe bağlı mevcut bir DatabaseConnection örneği.
                           Eğer None ise, bu depo tarafından yeni bir bağlantı oluşturulur ve yönetilir.
        """
        if db_connection:
            self.db: DatabaseConnection = db_connection
            self.own_connection: bool = False # Bağlantı harici olarak yönetiliyor
            # print("DEBUG: BaseRepository harici bir DatabaseConnection ile başlatıldı.")
        else:
            self.db: DatabaseConnection = DatabaseConnection()
            self.own_connection: bool = True # Bağlantı bu örnek tarafından sahiplenilir ve yönetilir
            # print("DEBUG: BaseRepository yeni bir dahili DatabaseConnection ile başlatıldı.")

    # 3.2. _ensure_connection (Depo için)
    # -------------------------------------------------------------------------
    def _ensure_connection(self) -> None:
        """Veritabanı bağlantısının aktif olduğundan emin olur, özellikle depo sahibi ise."""
        try:
            # self.db (DatabaseConnection örneği) zaten kendi _ensure_connection metoduna sahip.
            # Bu metot, self.db.connect() çağrısını içerir, bu yüzden burada doğrudan
            # self.db._ensure_connection() çağırmak yeterlidir.
            self.db._ensure_connection()
        except Error as e:
            # print(f"DEBUG: BaseRepository._ensure_connection içinde veritabanı bağlantı hatası: {e}")
            raise Error(f"Veritabanı bağlantısı sağlanamadı: {str(e)}")


    # 3.3. _close_if_owned
    # -------------------------------------------------------------------------
    def _close_if_owned(self) -> None:
        """
        Eğer bu depo örneği tarafından oluşturulmuş ve yönetiliyorsa veritabanı bağlantısını kapatır.
        Bu metot genellikle finally bloklarında çağrılır.
        """
        if self.own_connection:
            self.db.close()
            # print("DEBUG: Dahili DatabaseConnection, BaseRepository tarafından kapatıldı.")

    # 3.4. execute_query (Örn: UPDATE, DELETE)
    # -------------------------------------------------------------------------
    def execute_query(self, query: str, params: tuple = None) -> int:
        """
        Veriyi değiştiren bir sorguyu (UPDATE, DELETE) veya DDL (Veri Tanımlama Dili) çalıştırır.
        Args:
            query: SQL sorgu dizesi.
            params: Sorguya bağlanacak parametrelerden oluşan bir demet (tuple).
        Returns:
            Sorgudan etkilenen satır sayısı.
        Raises:
            mysql.connector.Error: Sorgu çalıştırılması başarısız olursa.
        """
        # print(f"DEBUG: Sorgu çalıştırılıyor: {query} parametreler: {params}")
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # print("DEBUG: Hata: Sorgu çalıştırmak için cursor mevcut değil.")
                raise Error("Sorgu çalıştırmak için cursor mevcut değil.")
            self.db.cursor.execute(query, params or ())
            if self.db.connection: # Bağlantının varlığından emin ol
                 self.db.connection.commit()
            affected_rows = self.db.cursor.rowcount
            # print(f"DEBUG: Sorgu başarıyla çalıştırıldı. Etkilenen satır sayısı: {affected_rows}")
            return affected_rows
        except Error as e:
            # print(f"DEBUG: Sorgu çalıştırılırken hata: {e}. İşlem geri alınıyor.")
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                    # print("DEBUG: İşlem geri alındı.")
                except Error as rb_error:
                    # print(f"DEBUG: Geri alma sırasında hata: {rb_error}")
                    pass
            raise # Orijinal hatayı yeniden fırlat
        finally:
            self._close_if_owned()

    # 3.5. fetch_one
    # -------------------------------------------------------------------------
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Bir sorgu çalıştırır ve tek bir sonuç getirir.
        Args:
            query: SQL sorgu dizesi.
            params: Sorguya bağlanacak parametrelerden oluşan bir demet.
        Returns:
            Satırı temsil eden bir sözlük veya sonuç bulunamazsa ya da hata oluşursa None.
        """
        # print(f"DEBUG: Tek sonuç getiriliyor: {query} parametreler: {params}")
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # print("DEBUG: Hata: fetch_one için cursor mevcut değil.")
                # Davranışa göre None döndür veya Error fırlat:
                # raise Error("fetch_one için cursor mevcut değil.")
                return None
            self.db.cursor.execute(query, params or ())
            result = self.db.cursor.fetchone()
            # print(f"DEBUG: fetch_one sonucu: {'Bulundu' if result else 'Bulunamadı'}")
            return result
        except Error as e:
            # print(f"DEBUG: fetch_one içinde hata: {e}")
            return None # Hatayı bastır ve orijinal davranışa göre None döndür
        finally:
            self._close_if_owned()

    # 3.6. fetch_all
    # -------------------------------------------------------------------------
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Bir sorgu çalıştırır ve tüm sonuçları getirir.
        Args:
            query: SQL sorgu dizesi.
            params: Sorguya bağlanacak parametrelerden oluşan bir demet.
        Returns:
            Her biri bir satırı temsil eden sözlüklerden oluşan bir liste.
            Sonuç bulunamazsa veya hata oluşursa boş bir liste döndürür.
        """
        # print(f"DEBUG: Tüm sonuçlar getiriliyor: {query} parametreler: {params}")
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # print("DEBUG: Hata: fetch_all için cursor mevcut değil.")
                # Davranışa göre boş liste döndür veya Error fırlat:
                # raise Error("fetch_all için cursor mevcut değil.")
                return []
            self.db.cursor.execute(query, params or ())
            results = self.db.cursor.fetchall()
            # print(f"DEBUG: fetch_all sonucu: {len(results)} satır bulundu.")
            return results
        except Error as e:
            # print(f"DEBUG: fetch_all içinde hata: {e}")
            return [] # Hatayı bastır ve orijinal davranışa göre boş liste döndür
        finally:
            self._close_if_owned()

    # 3.7. insert
    # -------------------------------------------------------------------------
    def insert(self, query: str, params: tuple = None) -> Optional[int]:
        """
        Bir INSERT sorgusu çalıştırır ve son eklenen satırın ID'sini döndürür.
        Args:
            query: SQL INSERT sorgu dizesi.
            params: Sorguya bağlanacak parametrelerden oluşan bir demet.
        Returns:
            Son eklenen satırın ID'si veya sorgu bir ID üretmiyorsa
            (örn: lastrowid desteği olmayan çok satırlı ekleme veya hata) None.
        Raises:
            mysql.connector.Error: Sorgu çalıştırılması başarısız olursa.
        """
        # print(f"DEBUG: Ekleme yapılıyor: {query} parametreler: {params}")
        try:
            self._ensure_connection()
            if not self.db.cursor:
                # print("DEBUG: Hata: insert için cursor mevcut değil.")
                raise Error("Ekleme işlemi için cursor mevcut değil.")
            self.db.cursor.execute(query, params or ())
            if self.db.connection: # Bağlantının varlığından emin ol
                self.db.connection.commit()
            last_row_id = self.db.cursor.lastrowid
            # print(f"DEBUG: Ekleme başarılı. Son satır ID: {last_row_id}")
            return last_row_id
        except Error as e:
            # print(f"DEBUG: Ekleme sırasında hata: {e}. İşlem geri alınıyor.")
            if self.db.connection and self.db.connection.is_connected():
                try:
                    self.db.connection.rollback()
                    # print("DEBUG: Ekleme hatası nedeniyle işlem geri alındı.")
                except Error as rb_error:
                    # print(f"DEBUG: Ekleme hatası sonrası geri alma sırasında hata: {rb_error}")
                    pass
            raise # Orijinal hatayı yeniden fırlat
        finally:
            self._close_if_owned()
