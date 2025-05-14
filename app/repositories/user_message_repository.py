# =============================================================================
# Kullanıcı Mesajı Deposu Modülü (User Message Repository Module)
# =============================================================================
# Bu modül, kullanıcıların AI modelleriyle olan etkileşimlerini (mesajları)
# veritabanında yönetmek için bir depo sınıfı içerir. Mesajların kaydedilmesi,
# sorgulanması ve istatistiklerinin alınması gibi işlemleri kapsar.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. UserMessageRepository Sınıfı
#    2.1. __init__                       : Başlatıcı metot (BaseRepository'den miras alınır).
#    2.2. insert_user_message            : Yeni bir kullanıcı mesajı ve AI yanıtını kaydeder.
#    2.3. get_user_message_by_id         : ID'ye göre bir kullanıcı mesajını getirir.
#    2.4. get_all_user_messages          : Tüm kullanıcı mesajlarını sayfalamalı olarak getirir.
#    2.5. get_user_messages_by_session   : Belirli bir oturum ID'sine ait mesajları getirir.
#    2.6. get_user_messages_by_user      : Belirli bir kullanıcı ID'sine ait mesajları getirir.
#    2.7. get_message_count              : Toplam kullanıcı mesajı sayısını getirir.
#    2.8. get_message_stats              : Kullanıcı mesajları hakkında istatistikleri getirir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import UserMessage # Kullanıcı Mesajı varlık sınıfı
from typing import List, Optional, Tuple, Dict, Any # Tip ipuçları
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi
import json # model_params, request_json, response_json Dict ise string'e çevirmek için

# 2. UserMessageRepository Sınıfı
# =============================================================================
class UserMessageRepository(BaseRepository):
    """Kullanıcı mesajı işlemleri için depo (repository) sınıfı."""

    # 2.1. __init__ metodu BaseRepository'den miras alındığı için
    #      UserMessageRepository'e özgü ek başlatma gerekmiyorsa yeniden tanımlanmasına gerek yoktur.

    # 2.2. insert_user_message
    # -------------------------------------------------------------------------
    def insert_user_message(self, session_id: str, user_message: str, ai_response: str,
                            ai_model_name: str, user_id: Optional[str] = None,
                            prompt: Optional[str] = None,
                            model_params: Optional[str] = None, # Orijinalde str, JSON string bekleniyor
                            request_json: Optional[str] = None, # Orijinalde str, JSON string bekleniyor
                            response_json: Optional[str] = None, # Orijinalde str, JSON string bekleniyor
                            tokens: Optional[int] = None,
                            duration: Optional[float] = None,
                            error_message: Optional[str] = None,
                            status: Optional[str] = None) -> Optional[int]:
        """
        Yeni bir kullanıcı mesajını ve AI yanıtını veritabanına ekler.
        Args:
            session_id (str): Kullanıcı oturum tanımlayıcısı.
            user_message (str): Kullanıcı tarafından gönderilen mesaj.
            ai_response (str): AI tarafından verilen yanıt.
            ai_model_name (str): Kullanılan AI modelinin adı.
            user_id (Optional[str]): Kullanıcı tanımlayıcısı (giriş yapmışsa).
            prompt (Optional[str]): AI'ya gönderilen tam prompt.
            model_params (Optional[str]): AI modeli için kullanılan parametreler (JSON string).
            request_json (Optional[str]): AI'ya gönderilen gerçek isteğin JSON string'i.
            response_json (Optional[str]): AI'dan gelen gerçek yanıtın JSON string'i.
            tokens (Optional[int]): Etkileşim için kullanılan token sayısı.
            duration (Optional[float]): AI çağrısının saniye cinsinden süresi.
            error_message (Optional[str]): AI çağrısı başarısız olursa hata mesajı.
            status (Optional[str]): Mesajın durumu (örn: 'success', 'error').
        Returns:
            Optional[int]: Eklenen mesajın ID'si veya hata durumunda None.
        """
        # print(f"DEBUG: Kullanıcı mesajı ekleniyor: OturumID='{session_id}', Model='{ai_model_name}'")
        try:
            # Zorunlu alanlar için temel kontroller ve varsayılan değerler (orijinaldeki gibi)
            processed_session_id = session_id.strip() if session_id and session_id.strip() else "UNKNOWN_SESSION"
            processed_ai_model_name = ai_model_name.strip() if ai_model_name and ai_model_name.strip() else "UNKNOWN_MODEL"
            # user_message ve ai_response boş olabilir, bu yüzden doğrudan kullanılırlar.

            # Veritabanına eklenecek alanları ve değerleri dinamik olarak oluştur
            fields = ["session_id", "user_message", "ai_response", "ai_model_name"]
            values = [
                processed_session_id,
                user_message,
                ai_response,
                processed_ai_model_name
            ]

            # İsteğe bağlı alanlar
            # Bu alanlar veritabanında JSON tipinde olsa bile, mysql.connector Python string'lerini
            # (geçerli JSON formatındaysa) kabul eder.
            optional_data = {
                "user_id": user_id.strip() if user_id else None,
                "prompt": prompt,
                "model_params": model_params, # Doğrudan string olarak kullanılır
                "request_json": request_json, # Doğrudan string olarak kullanılır
                "response_json": response_json, # Doğrudan string olarak kullanılır
                "tokens": tokens,
                "duration": duration,
                "error_message": error_message,
                "status": status.strip() if status else None
            }

            for field, value in optional_data.items():
                if value is not None: # Sadece None olmayan değerleri ekle
                    fields.append(field)
                    values.append(value)

            placeholders = ", ".join(["%s"] * len(fields))
            query = f"INSERT INTO user_messages ({', '.join(fields)}) VALUES ({placeholders})"

            message_id = self.insert(query, tuple(values))
            if message_id:
                # print(f"DEBUG: Kullanıcı mesajı başarıyla eklendi. ID: {message_id}")
                return message_id
            else:
                # print("DEBUG: Kullanıcı mesajı eklenemedi, insert metodu ID döndürmedi.")
                return None
        except MySQLError as e:
            # print(f"DEBUG: Kullanıcı mesajı eklenirken veritabanı hatası: {e}")
            return None
        except Exception as ex: # Diğer beklenmedik hatalar için
            # print(f"DEBUG: Kullanıcı mesajı eklenirken beklenmedik hata: {ex}")
            return None

    # 2.3. get_user_message_by_id
    # -------------------------------------------------------------------------
    def get_user_message_by_id(self, message_id: int) -> Optional[UserMessage]:
        """
        Verilen ID'ye sahip kullanıcı mesajını getirir.
        Args:
            message_id (int): Getirilecek mesajın ID'si.
        Returns:
            Optional[UserMessage]: Bulunan UserMessage nesnesi veya bulunamazsa None.
        """
        if not message_id or not isinstance(message_id, int) or message_id <= 0:
            # print(f"DEBUG: get_user_message_by_id için geçersiz ID: {message_id}")
            return None
        query = "SELECT * FROM user_messages WHERE id = %s"
        result = self.fetch_one(query, (message_id,))
        # print(f"DEBUG: get_user_message_by_id({message_id}) sonucu: {'Bulundu' if result else 'Bulunamadı'}")
        return UserMessage.from_dict(result) if result else None

    # 2.4. get_all_user_messages
    # -------------------------------------------------------------------------
    def get_all_user_messages(self, limit: int = 100, offset: int = 0) -> List[UserMessage]:
        """
        Tüm kullanıcı mesajlarını zaman damgasına göre azalan sırada, sayfalamalı olarak getirir.
        Args:
            limit (int): Getirilecek maksimum mesaj sayısı.
            offset (int): Başlangıç noktası (kaydırma için).
        Returns:
            List[UserMessage]: UserMessage nesnelerinin listesi.
        """
        try:
            limit = int(limit)
            offset = int(offset)
            if limit <= 0: limit = 100 # Negatif veya sıfır limite izin verme
            if offset < 0: offset = 0   # Negatif offsete izin verme
        except ValueError:
            # print("DEBUG: get_all_user_messages için geçersiz limit veya offset değeri.")
            limit = 100
            offset = 0

        query = "SELECT * FROM user_messages ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        results = self.fetch_all(query, (limit, offset))
        # print(f"DEBUG: get_all_user_messages (limit={limit}, offset={offset}) sonucu: {len(results)} mesaj bulundu.")
        return [UserMessage.from_dict(row) for row in results if row]

    # 2.5. get_user_messages_by_session
    # -------------------------------------------------------------------------
    def get_user_messages_by_session(self, session_id: str, limit: int = 100) -> List[UserMessage]:
        """
        Belirli bir oturum ID'sine ait kullanıcı mesajlarını zaman damgasına göre
        azalan sırada, limitli olarak getirir.
        Args:
            session_id (str): Mesajların alınacağı oturum ID'si.
            limit (int): Getirilecek maksimum mesaj sayısı.
        Returns:
            List[UserMessage]: Belirtilen oturuma ait UserMessage nesnelerinin listesi.
        """
        if not session_id or not session_id.strip():
            # print(f"DEBUG: get_user_messages_by_session için geçersiz session_id: '{session_id}'")
            return []
        try:
            limit = int(limit)
            if limit <= 0: limit = 100
        except ValueError:
            # print("DEBUG: get_user_messages_by_session için geçersiz limit değeri.")
            limit = 100

        query = "SELECT * FROM user_messages WHERE session_id = %s ORDER BY timestamp DESC LIMIT %s"
        results = self.fetch_all(query, (session_id.strip(), limit))
        # print(f"DEBUG: get_user_messages_by_session(session_id='{session_id}', limit={limit}) sonucu: {len(results)} mesaj bulundu.")
        return [UserMessage.from_dict(row) for row in results if row]

    # 2.6. get_user_messages_by_user
    # -------------------------------------------------------------------------
    def get_user_messages_by_user(self, user_id: str, limit: int = 100) -> List[UserMessage]:
        """
        Belirli bir kullanıcı ID'sine ait kullanıcı mesajlarını zaman damgasına göre
        azalan sırada, limitli olarak getirir.
        Args:
            user_id (str): Mesajların alınacağı kullanıcı ID'si.
            limit (int): Getirilecek maksimum mesaj sayısı.
        Returns:
            List[UserMessage]: Belirtilen kullanıcıya ait UserMessage nesnelerinin listesi.
        """
        if not user_id or not user_id.strip():
            # print(f"DEBUG: get_user_messages_by_user için geçersiz user_id: '{user_id}'")
            return []
        try:
            limit = int(limit)
            if limit <= 0: limit = 100
        except ValueError:
            # print("DEBUG: get_user_messages_by_user için geçersiz limit değeri.")
            limit = 100

        query = "SELECT * FROM user_messages WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s"
        results = self.fetch_all(query, (user_id.strip(), limit))
        # print(f"DEBUG: get_user_messages_by_user(user_id='{user_id}', limit={limit}) sonucu: {len(results)} mesaj bulundu.")
        return [UserMessage.from_dict(row) for row in results if row]

    # 2.7. get_message_count
    # -------------------------------------------------------------------------
    def get_message_count(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> int:
        """
        Toplam kullanıcı mesajı sayısını veya belirtilen session_id/user_id için mesaj sayısını getirir.
        Args:
            session_id (Optional[str]): Belirli bir oturumun mesaj sayısını almak için.
            user_id (Optional[str]): Belirli bir kullanıcının mesaj sayısını almak için.
        Returns:
            int: Mesaj sayısı.
        """
        query = "SELECT COUNT(*) as count FROM user_messages"
        params = []
        conditions = []

        if session_id and session_id.strip():
            conditions.append("session_id = %s")
            params.append(session_id.strip())
        if user_id and user_id.strip():
            conditions.append("user_id = %s")
            params.append(user_id.strip())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        result = self.fetch_one(query, tuple(params) if params else None)
        count = result['count'] if result and 'count' in result else 0
        # print(f"DEBUG: get_message_count (session_id='{session_id}', user_id='{user_id}') sonucu: {count}")
        return count

    # 2.8. get_message_stats
    # -------------------------------------------------------------------------
    def get_message_stats(self) -> Dict[str, Any]:
        """
        Kullanıcı mesajları hakkında genel istatistikleri getirir.
        Returns:
            Dict[str, Any]: Mesaj istatistiklerini içeren bir sözlük.
        """
        stats = {
            'total_message_count': 0,
            'model_usage_counts': {}, # ai_model_name'e göre kullanım sayıları
            'distinct_session_count': 0,
            'distinct_user_count': 0, # user_id'si dolu olanlar için
            'average_tokens_per_message': 0.0, # Sadece tokens dolu olanlar için, float olarak başlat
            'average_duration_per_message': 0.0 # Sadece duration dolu olanlar için, float olarak başlat
        }
        # print("DEBUG: Kullanıcı mesaj istatistikleri alınıyor...")
        try:
            # Toplam mesaj sayısı
            stats['total_message_count'] = self.get_message_count()

            # AI modeline göre mesaj sayıları
            query_model_usage = """
                SELECT ai_model_name, COUNT(*) as count
                FROM user_messages
                WHERE ai_model_name IS NOT NULL AND ai_model_name != '' AND ai_model_name != 'UNKNOWN_MODEL'
                GROUP BY ai_model_name
                ORDER BY count DESC
            """
            model_results = self.fetch_all(query_model_usage)
            if model_results:
                for row in model_results:
                    if row and 'ai_model_name' in row and 'count' in row:
                        stats['model_usage_counts'][row['ai_model_name']] = row['count']

            # Benzersiz oturum sayısı
            query_session_count = "SELECT COUNT(DISTINCT session_id) as count FROM user_messages WHERE session_id IS NOT NULL AND session_id != 'UNKNOWN_SESSION'"
            session_count_result = self.fetch_one(query_session_count)
            stats['distinct_session_count'] = session_count_result['count'] if session_count_result and 'count' in session_count_result else 0

            # Benzersiz kullanıcı sayısı (user_id'si olanlar)
            query_user_count = "SELECT COUNT(DISTINCT user_id) as count FROM user_messages WHERE user_id IS NOT NULL AND user_id != ''"
            user_count_result = self.fetch_one(query_user_count)
            stats['distinct_user_count'] = user_count_result['count'] if user_count_result and 'count' in user_count_result else 0

            # Ortalama token sayısı (sadece tokens alanı dolu olan mesajlar için)
            query_avg_tokens = "SELECT AVG(tokens) as avg_tokens FROM user_messages WHERE tokens IS NOT NULL AND tokens > 0"
            avg_tokens_result = self.fetch_one(query_avg_tokens)
            stats['average_tokens_per_message'] = round(float(avg_tokens_result['avg_tokens']), 2) if avg_tokens_result and avg_tokens_result['avg_tokens'] is not None else 0.0

            # Ortalama süre (sadece duration alanı dolu olan mesajlar için)
            query_avg_duration = "SELECT AVG(duration) as avg_duration FROM user_messages WHERE duration IS NOT NULL AND duration > 0"
            avg_duration_result = self.fetch_one(query_avg_duration)
            stats['average_duration_per_message'] = round(float(avg_duration_result['avg_duration']), 2) if avg_duration_result and avg_duration_result['avg_duration'] is not None else 0.0

            # print(f"DEBUG: Mesaj istatistikleri: {stats}")
        except MySQLError as e:
            # print(f"DEBUG: Mesaj istatistikleri alınırken veritabanı hatası: {e}")
            # Hata durumunda mevcut (belki kısmi) istatistikleri döndür
            return stats
        except Exception as ex:
            # print(f"DEBUG: Mesaj istatistikleri alınırken beklenmedik hata: {ex}")
            return stats
        return stats

