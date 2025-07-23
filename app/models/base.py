# =============================================================================
# İyileştirilmiş Temel Veritabanı Modülü (Improved Database Base Module)
# =============================================================================
# Bu modül, veritabanı bağlantı havuzu (connection pooling), transaction yönetimi
# ve gelişmiş hata işleme ile optimize edilmiş veritabanı işlemleri sağlar.
#
# İYİLEŞTİRMELER:
# - Connection pooling eklendi
# - Transaction management iyileştirildi
# - Retry mechanism eklendi
# - Performance monitoring
# - Proper logging sistemi
# - Context manager iyileştirmeleri
# =============================================================================

import mysql.connector
from mysql.connector import Error, pooling
from mysql.connector.pooling import MySQLConnectionPool
import logging
import time
import threading
from typing import Optional, Any, Dict, List, Type, Union
from contextlib import contextmanager
from app.config import DB_CONFIG

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

# =============================================================================
# CONNECTION POOL MANAGER
# =============================================================================
class ConnectionPoolManager:
    """
    MySQL connection pool'unu yöneten singleton sınıf
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.pool = None
            self.pool_config = None
            self._stats = {
                'total_connections': 0,
                'active_connections': 0,
                'pool_hits': 0,
                'pool_misses': 0
            }
            self._initialized = True
    
    def initialize_pool(self, config: Dict[str, Any] = None) -> None:
        """
        Connection pool'unu başlatır
        
        Args:
            config: Database konfigürasyonu
        """
        if self.pool is not None:
            logger.warning("Connection pool already initialized")
            return
            
        pool_config = config or DB_CONFIG.copy()
        
        # Pool-specific konfigürasyon
        pool_config.update({
            'pool_name': 'zekai_pool',
            'pool_size': pool_config.get('pool_size', 10),
            'pool_reset_session': True,
            'autocommit': False,  # Transaction control için
            'use_unicode': True,
            'charset': 'utf8mb4'
        })
        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            self.pool_config = pool_config
            logger.info(f"Connection pool initialized with size: {pool_config['pool_size']}")
        except Error as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise
    
    def get_connection(self) -> mysql.connector.MySQLConnection:
        """
        Pool'dan connection alır
        
        Returns:
            MySQL connection
        """
        if self.pool is None:
            self.initialize_pool()
        
        try:
            connection = self.pool.get_connection()
            self._stats['pool_hits'] += 1
            self._stats['active_connections'] += 1
            logger.debug("Connection acquired from pool")
            return connection
        except Error as e:
            self._stats['pool_misses'] += 1
            logger.error(f"Failed to get connection from pool: {str(e)}")
            raise
    
    def return_connection(self, connection: mysql.connector.MySQLConnection) -> None:
        """
        Connection'ı pool'a geri döndürür
        
        Args:
            connection: MySQL connection
        """
        if connection and connection.is_connected():
            try:
                # Rollback any uncommitted transactions
                connection.rollback()
                connection.close()  # Pool'a geri döndürür
                self._stats['active_connections'] = max(0, self._stats['active_connections'] - 1)
                logger.debug("Connection returned to pool")
            except Error as e:
                logger.warning(f"Error returning connection to pool: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Pool istatistiklerini döndürür"""
        stats = self._stats.copy()
        if self.pool:
            stats.update({
                'pool_size': self.pool_config.get('pool_size', 0),
                'pool_name': self.pool_config.get('pool_name', 'unknown')
            })
        return stats
    
    def close_pool(self) -> None:
        """Pool'u kapatır"""
        if self.pool:
            # Pool'daki tüm connection'ları kapat
            # MySQL Connector/Python pool'u otomatik olarak temizler
            self.pool = None
            self.pool_config = None
            logger.info("Connection pool closed")

# Global pool manager instance
pool_manager = ConnectionPoolManager()

# =============================================================================
# IMPROVED DATABASE CONNECTION CLASS
# =============================================================================
class DatabaseConnection:
    """
    Geliştirilmiş veritabanı bağlantı yöneticisi.
    Connection pooling, transaction management ve retry logic içerir.
    """

    def __init__(self, use_pool: bool = True, auto_commit: bool = False):
        """
        DatabaseConnection'ı başlatır
        
        Args:
            use_pool: Connection pool kullanılsın mı
            auto_commit: Otomatik commit yapılsın mı
        """
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursorDict] = None
        self.use_pool = use_pool
        self.auto_commit = auto_commit
        self.in_transaction = False
        self._connection_start_time = None
        
        # Pool'u başlat
        if use_pool:
            pool_manager.initialize_pool()

    def connect(self, retry_count: int = 3, retry_delay: float = 1.0) -> None:
        """
        Veritabanına bağlantı kurar (retry logic ile)
        
        Args:
            retry_count: Yeniden deneme sayısı
            retry_delay: Yeniden deneme arasındaki bekleme süresi
        """
        last_error = None
        
        for attempt in range(retry_count):
            try:
                self._connection_start_time = time.time()
                
                if self.use_pool:
                    self.connection = pool_manager.get_connection()
                else:
                    self.connection = mysql.connector.connect(**DB_CONFIG)
                
                if self.connection.is_connected():
                    self.connection.autocommit = self.auto_commit
                    self.cursor = self.connection.cursor(dictionary=True)
                    logger.debug(f"Database connection established (attempt {attempt + 1})")
                    return
                else:
                    raise Error("Failed to establish connection")
                    
            except Error as e:
                last_error = e
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All connection attempts failed. Last error: {str(e)}")
        
        if last_error:
            raise last_error

    def close(self) -> None:
        """Bağlantıyı kapatır"""
        connection_duration = None
        if self._connection_start_time:
            connection_duration = time.time() - self._connection_start_time
        
        if self.cursor:
            try:
                self.cursor.close()
                logger.debug("Database cursor closed")
            except Error as e:
                logger.warning(f"Error closing cursor: {str(e)}")
            self.cursor = None
        
        if self.connection and self.connection.is_connected():
            try:
                if self.in_transaction:
                    self.connection.rollback()
                    logger.debug("Transaction rolled back during connection close")
                
                if self.use_pool:
                    pool_manager.return_connection(self.connection)
                else:
                    self.connection.close()
                
                if connection_duration:
                    logger.debug(f"Connection closed after {connection_duration:.3f}s")
                    
            except Error as e:
                logger.warning(f"Error closing connection: {str(e)}")
            
            self.connection = None
            self.in_transaction = False

    def _ensure_connection(self) -> None:
        """Aktif bağlantı olduğundan emin olur"""
        if not self.connection or not self.connection.is_connected() or not self.cursor:
            logger.debug("Re-establishing database connection")
            self.connect()

    @contextmanager
    def transaction(self):
        """
        Transaction context manager
        
        Usage:
            with db.transaction():
                # database operations
        """
        self._ensure_connection()
        
        if self.in_transaction:
            # Nested transaction - sadece yield et
            yield
            return
        
        try:
            self.in_transaction = True
            logger.debug("Transaction started")
            yield
            
            if self.connection:
                self.connection.commit()
                logger.debug("Transaction committed")
                
        except Exception as e:
            if self.connection and self.connection.is_connected():
                try:
                    self.connection.rollback()
                    logger.debug("Transaction rolled back due to error")
                except Error as rollback_error:
                    logger.error(f"Error during rollback: {str(rollback_error)}")
            raise
        finally:
            self.in_transaction = False

    def __enter__(self) -> 'DatabaseConnection':
        """Context manager entry"""
        self._ensure_connection()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[Any]) -> None:
        """Context manager exit"""
        if exc_type:
            logger.debug(f"Exception in context manager: {exc_type.__name__}: {exc_val}")
        self.close()

# =============================================================================
# IMPROVED BASE REPOSITORY CLASS
# =============================================================================
class BaseRepository:
    """
    Geliştirilmiş temel repository sınıfı.
    Transaction support, retry logic ve performance monitoring içerir.
    """

    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        BaseRepository'yi başlatır
        
        Args:
            db_connection: Mevcut database connection (opsiyonel)
        """
        if db_connection:
            self.db = db_connection
            self.own_connection = False
        else:
            self.db = DatabaseConnection(use_pool=True)
            self.own_connection = True
        
        self._query_stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'average_query_time': 0.0
        }

    def _ensure_connection(self) -> None:
        """Veritabanı bağlantısının aktif olduğundan emin olur"""
        try:
            self.db._ensure_connection()
        except Error as e:
            logger.error(f"Failed to ensure database connection: {str(e)}")
            raise

    def _close_if_owned(self) -> None:
        """Sahip olunan bağlantıyı kapatır"""
        if self.own_connection:
            self.db.close()

    def _execute_with_retry(self, operation, *args, **kwargs):
        """
        Database operasyonunu retry logic ile çalıştırır
        
        Args:
            operation: Çalıştırılacak fonksiyon
            *args, **kwargs: Fonksiyon parametreleri
        """
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Error as e:
                if attempt < max_retries - 1 and "Lost connection" in str(e):
                    logger.warning(f"Database operation failed (attempt {attempt + 1}), retrying: {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    self._ensure_connection()
                else:
                    raise

    def _update_query_stats(self, query_time: float, success: bool) -> None:
        """Query istatistiklerini günceller"""
        self._query_stats['total_queries'] += 1
        
        if success:
            self._query_stats['successful_queries'] += 1
        else:
            self._query_stats['failed_queries'] += 1
        
        # Average query time güncelle
        total = self._query_stats['total_queries']
        current_avg = self._query_stats['average_query_time']
        self._query_stats['average_query_time'] = (
            (current_avg * (total - 1) + query_time) / total
        )

    def execute_query(self, query: str, params: tuple = None, use_transaction: bool = True) -> int:
        """
        Veri değiştiren sorguyu çalıştırır
        
        Args:
            query: SQL sorgusu
            params: Query parametreleri
            use_transaction: Transaction kullanılsın mı
            
        Returns:
            Etkilenen satır sayısı
        """
        start_time = time.time()
        
        def _execute():
            self._ensure_connection()
            if not self.db.cursor:
                raise Error("Cursor not available for query execution")
            
            self.db.cursor.execute(query, params or ())
            
            if not self.db.auto_commit and not self.db.in_transaction and use_transaction:
                self.db.connection.commit()
            
            return self.db.cursor.rowcount
        
        try:
            if use_transaction and not self.db.in_transaction:
                with self.db.transaction():
                    result = self._execute_with_retry(_execute)
            else:
                result = self._execute_with_retry(_execute)
            
            query_time = time.time() - start_time
            self._update_query_stats(query_time, True)
            
            logger.debug(f"Query executed successfully in {query_time:.3f}s, affected rows: {result}")
            return result
            
        except Error as e:
            query_time = time.time() - start_time
            self._update_query_stats(query_time, False)
            logger.error(f"Query execution failed after {query_time:.3f}s: {str(e)}")
            raise
        finally:
            self._close_if_owned()

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Tek sonuç getiren sorguyu çalıştırır
        
        Args:
            query: SQL sorgusu
            params: Query parametreleri
            
        Returns:
            Sonuç dictionary'si veya None
        """
        start_time = time.time()
        
        def _fetch():
            self._ensure_connection()
            if not self.db.cursor:
                raise Error("Cursor not available for fetch operation")
            
            self.db.cursor.execute(query, params or ())
            return self.db.cursor.fetchone()
        
        try:
            result = self._execute_with_retry(_fetch)
            
            query_time = time.time() - start_time
            self._update_query_stats(query_time, True)
            
            logger.debug(f"fetch_one completed in {query_time:.3f}s, result: {'found' if result else 'not found'}")
            return result
            
        except Error as e:
            query_time = time.time() - start_time
            self._update_query_stats(query_time, False)
            logger.error(f"fetch_one failed after {query_time:.3f}s: {str(e)}")
            return None
        finally:
            self._close_if_owned()

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Tüm sonuçları getiren sorguyu çalıştırır
        
        Args:
            query: SQL sorgusu
            params: Query parametreleri
            
        Returns:
            Sonuç listesi
        """
        start_time = time.time()
        
        def _fetch():
            self._ensure_connection()
            if not self.db.cursor:
                raise Error("Cursor not available for fetch operation")
            
            self.db.cursor.execute(query, params or ())
            return self.db.cursor.fetchall()
        
        try:
            results = self._execute_with_retry(_fetch)
            
            query_time = time.time() - start_time
            self._update_query_stats(query_time, True)
            
            logger.debug(f"fetch_all completed in {query_time:.3f}s, rows: {len(results)}")
            return results
            
        except Error as e:
            query_time = time.time() - start_time
            self._update_query_stats(query_time, False)
            logger.error(f"fetch_all failed after {query_time:.3f}s: {str(e)}")
            return []
        finally:
            self._close_if_owned()

    def insert(self, query: str, params: tuple = None, use_transaction: bool = True) -> Optional[int]:
        """
        INSERT sorgusu çalıştırır
        
        Args:
            query: SQL INSERT sorgusu
            params: Query parametreleri
            use_transaction: Transaction kullanılsın mı
            
        Returns:
            Son eklenen satırın ID'si
        """
        start_time = time.time()
        
        def _insert():
            self._ensure_connection()
            if not self.db.cursor:
                raise Error("Cursor not available for insert operation")
            
            self.db.cursor.execute(query, params or ())
            
            if not self.db.auto_commit and not self.db.in_transaction and use_transaction:
                self.db.connection.commit()
            
            return self.db.cursor.lastrowid
        
        try:
            if use_transaction and not self.db.in_transaction:
                with self.db.transaction():
                    result = self._execute_with_retry(_insert)
            else:
                result = self._execute_with_retry(_insert)
            
            query_time = time.time() - start_time
            self._update_query_stats(query_time, True)
            
            logger.debug(f"Insert completed in {query_time:.3f}s, last_row_id: {result}")
            return result
            
        except Error as e:
            query_time = time.time() - start_time
            self._update_query_stats(query_time, False)
            logger.error(f"Insert failed after {query_time:.3f}s: {str(e)}")
            raise
        finally:
            self._close_if_owned()

    def get_stats(self) -> Dict[str, Any]:
        """Repository istatistiklerini döndürür"""
        return {
            'query_stats': self._query_stats.copy(),
            'pool_stats': pool_manager.get_stats(),
            'success_rate': (
                self._query_stats['successful_queries'] / 
                max(self._query_stats['total_queries'], 1) * 100
            )
        }

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

@contextmanager
def get_db_connection(use_pool: bool = True) -> DatabaseConnection:
    """
    Database connection context manager
    
    Usage:
        with get_db_connection() as db:
            # database operations
    """
    db = DatabaseConnection(use_pool=use_pool)
    try:
        db.connect()
        yield db
    finally:
        db.close()

def close_all_connections():
    """Tüm connection pool'ları kapatır"""
    pool_manager.close_pool()
    logger.info("All database connections closed")

def get_database_stats() -> Dict[str, Any]:
    """Database istatistiklerini döndürür"""
    return pool_manager.get_stats()

