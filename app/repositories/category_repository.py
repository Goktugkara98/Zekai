# =============================================================================
# Kategori Deposu Modülü (Category Repository Module)
# =============================================================================
# Bu modül, AI kategorileriyle ilgili veritabanı işlemleri için bir depo
# sınıfı içerir. Kategorilerin oluşturulması, güncellenmesi, silinmesi ve
# sorgulanması gibi işlemleri yönetir.
#
# İçindekiler:
# -----------------------------------------------------------------------------
# 1.0 İÇE AKTARMALAR (IMPORTS)
#
# 2.0 CATEGORYREPOSITORY SINIFI (CATEGORYREPOSITORY CLASS)
#     2.1. __init__               : Başlatıcı metot (BaseRepository'den miras alınır).
#     2.2. create_category        : Yeni bir kategori oluşturur.
#     2.3. update_category        : Mevcut bir kategoriyi günceller.
#     2.4. delete_category        : Bir kategoriyi ve ilişkili modelleri siler.
#     2.5. get_category_by_id     : ID'ye göre bir kategori getirir.
#     2.6. get_category_by_name   : İsme göre bir kategori getirir.
#     2.7. get_all_categories     : Tüm kategorileri getirir.
#     2.8. count_all_categories   : Tüm kategorilerin sayısını döndürür.
# =============================================================================

# =============================================================================
# 1.0 İÇE AKTARMALAR (IMPORTS)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import Category # Kategori varlık sınıfı
from typing import List, Optional, Tuple
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi

# =============================================================================
# 2.0 CATEGORYREPOSITORY SINIFI (CATEGORYREPOSITORY CLASS)
# =============================================================================
class CategoryRepository(BaseRepository):
    """Kategori işlemleri için depo (repository) sınıfı."""

    # -------------------------------------------------------------------------
    # 2.1. Başlatıcı metot (__init__)
    #      BaseRepository'den miras alındığı için CategoryRepository'e özgü
    #      ek başlatma gerekmiyorsa yeniden tanımlanmasına gerek yoktur.
    #      Ancak, tutarlılık için içindekiler listesinde belirtilmiştir.
    # -------------------------------------------------------------------------
    # def __init__(self, db_connection: Optional[DatabaseConnection] = None):
    #     super().__init__(db_connection)

    # -------------------------------------------------------------------------
    # 2.2. Yeni bir kategori oluşturur (create_category)
    # -------------------------------------------------------------------------
    def create_category(self, name: str, icon: str) -> Tuple[bool, str, Optional[int]]:
        """
        Yeni bir kategori oluşturur.
        Args:
            name (str): Kategorinin adı.
            icon (str): Kategori için ikon sınıfı (örn: 'bi bi-robot').
        Returns:
            Tuple[bool, str, Optional[int]]: (başarı_durumu, mesaj, kategori_id)
        """
        try:
            if not name or not name.strip() or len(name) > 255:
                return False, "Kategori adı gereklidir ve 255 karakterden az olmalıdır.", None
            if not icon or not icon.strip() or len(icon) > 255:
                return False, "Kategori ikonu gereklidir ve 255 karakterden az olmalıdır.", None

            existing_category = self.get_category_by_name(name.strip())
            if existing_category:
                return False, f"'{name.strip()}' adında bir kategori zaten mevcut.", None

            query = "INSERT INTO ai_categories (name, icon) VALUES (%s, %s)"
            category_id = self.insert(query, (name.strip(), icon.strip()))

            if category_id:
                return True, f"Kategori '{name.strip()}' başarıyla oluşturuldu.", category_id
            else:
                return False, f"Kategori '{name.strip()}' oluşturulamadı.", None
        except MySQLError as e:
            return False, f"Veritabanı hatası: {str(e)}", None
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # -------------------------------------------------------------------------
    # 2.3. Mevcut bir kategoriyi günceller (update_category)
    # -------------------------------------------------------------------------
    def update_category(self, category_id: int, name: str, icon: str) -> Tuple[bool, str]:
        """
        Mevcut bir kategoriyi günceller.
        Args:
            category_id (int): Güncellenecek kategorinin ID'si.
            name (str): Kategorinin yeni adı.
            icon (str): Kategorinin yeni ikonu.
        Returns:
            Tuple[bool, str]: (başarı_durumu, mesaj)
        """
        try:
            if not category_id or not isinstance(category_id, int) or category_id <= 0:
                return False, "Geçerli bir kategori ID'si gereklidir."
            if not name or not name.strip() or len(name) > 255:
                return False, "Kategori adı gereklidir ve 255 karakterden az olmalıdır."
            if not icon or not icon.strip() or len(icon) > 255:
                return False, "Kategori ikonu gereklidir ve 255 karakterden az olmalıdır."

            category = self.get_category_by_id(category_id)
            if not category:
                return False, f"ID'si {category_id} olan kategori bulunamadı."

            query_check_name = "SELECT id FROM ai_categories WHERE name = %s AND id != %s"
            existing_with_same_name = self.fetch_one(query_check_name, (name.strip(), category_id))
            if existing_with_same_name:
                return False, f"'{name.strip()}' adında başka bir kategori zaten mevcut."

            query = "UPDATE ai_categories SET name = %s, icon = %s WHERE id = %s"
            rows_affected = self.execute_query(query, (name.strip(), icon.strip(), category_id))

            if rows_affected > 0:
                return True, "Kategori başarıyla güncellendi."
            else:
                # Eğer isim ve ikon aynıysa, değişiklik yapılmamış olabilir.
                if category.name == name.strip() and category.icon == icon.strip():
                    return True, "Kategoride herhangi bir değişiklik yapılmadı (veriler aynı)."
                return False, "Kategori güncellenemedi (veya veriler aynıydı)."
        except MySQLError as e:
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # -------------------------------------------------------------------------
    # 2.4. Bir kategoriyi ve ilişkili modelleri siler (delete_category)
    # -------------------------------------------------------------------------
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """
        Bir kategoriyi siler. İlişkili modellerin durumu (silinir mi, category_id'si NULL mu olur)
        veritabanı şemasındaki FOREIGN KEY tanımına bağlıdır (ON DELETE SET NULL varsayılır).
        Args:
            category_id (int): Silinecek kategorinin ID'si.
        Returns:
            Tuple[bool, str]: (başarı_durumu, mesaj)
        """
        try:
            if not category_id or not isinstance(category_id, int) or category_id <= 0:
                return False, "Geçerli bir kategori ID'si gereklidir."

            category = self.get_category_by_id(category_id)
            if not category:
                return False, f"ID'si {category_id} olan kategori bulunamadı."

            category_name = category.name

            query_model_count = "SELECT COUNT(*) as model_count FROM ai_models WHERE category_id = %s"
            count_result = self.fetch_one(query_model_count, (category_id,))
            model_count = count_result['model_count'] if count_result else 0

            query_delete = "DELETE FROM ai_categories WHERE id = %s"
            rows_affected = self.execute_query(query_delete, (category_id,))

            if rows_affected > 0:
                return True, (f"Kategori '{category_name}' başarıyla silindi. "
                              f"Bu kategoriye bağlı {model_count} modelin kategori bağlantısı kaldırıldı.")
            else:
                return False, f"Kategori '{category_name}' silinemedi."
        except MySQLError as e:
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # -------------------------------------------------------------------------
    # 2.5. ID'ye göre bir kategori getirir (get_category_by_id)
    # -------------------------------------------------------------------------
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """
        Verilen ID'ye sahip kategoriyi getirir.
        Args:
            category_id (int): Getirilecek kategorinin ID'si.
        Returns:
            Optional[Category]: Bulunan Category nesnesi veya bulunamazsa None.
        """
        if not category_id or not isinstance(category_id, int) or category_id <= 0:
            return None
        query = "SELECT id, name, icon FROM ai_categories WHERE id = %s"
        result = self.fetch_one(query, (category_id,))
        return Category.from_dict(result) if result else None

    # -------------------------------------------------------------------------
    # 2.6. İsme göre bir kategori getirir (get_category_by_name)
    # -------------------------------------------------------------------------
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        Verilen isme sahip kategoriyi getirir.
        Args:
            name (str): Getirilecek kategorinin adı.
        Returns:
            Optional[Category]: Bulunan Category nesnesi veya bulunamazsa None.
        """
        if not name or not name.strip():
            return None
        query = "SELECT id, name, icon FROM ai_categories WHERE name = %s"
        result = self.fetch_one(query, (name.strip(),))
        return Category.from_dict(result) if result else None

    # -------------------------------------------------------------------------
    # 2.7. Tüm kategorileri getirir (get_all_categories)
    # -------------------------------------------------------------------------
    def get_all_categories(self) -> List[Category]:
        """
        Tüm kategorileri ID'ye göre sıralanmış olarak getirir.
        Returns:
            List[Category]: Tüm Category nesnelerinin listesi.
        """
        query = "SELECT id, name, icon FROM ai_categories ORDER BY id"
        results = self.fetch_all(query)
        return [Category.from_dict(row) for row in results if row]

    # -------------------------------------------------------------------------
    # 2.8. Tüm kategorilerin sayısını döndürür (count_all_categories)
    # -------------------------------------------------------------------------
    def count_all_categories(self) -> int:
        """
        Tüm AI kategorilerinin sayısını döndürür.
        Returns:
            int: Toplam kategori sayısı.
        """
        query = "SELECT COUNT(*) as count FROM ai_categories"
        result = self.fetch_one(query)
        return result['count'] if result and 'count' in result else 0
