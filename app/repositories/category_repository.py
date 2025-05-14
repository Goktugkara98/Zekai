# =============================================================================
# Kategori Deposu Modülü (Category Repository Module)
# =============================================================================
# Bu modül, AI kategorileriyle ilgili veritabanı işlemleri için bir depo
# sınıfı içerir. Kategorilerin oluşturulması, güncellenmesi, silinmesi ve
# sorgulanması gibi işlemleri yönetir.
#
# İçindekiler:
# 1. İçe Aktarmalar (Imports)
# 2. CategoryRepository Sınıfı
#    2.1. __init__             : Başlatıcı metot (BaseRepository'den miras alınır).
#    2.2. create_category      : Yeni bir kategori oluşturur.
#    2.3. update_category      : Mevcut bir kategoriyi günceller.
#    2.4. delete_category      : Bir kategoriyi ve ilişkili modelleri siler.
#    2.5. get_category_by_id   : ID'ye göre bir kategori getirir.
#    2.6. get_category_by_name : İsme göre bir kategori getirir.
#    2.7. get_all_categories   : Tüm kategorileri getirir.
# =============================================================================

# 1. İçe Aktarmalar (Imports)
# =============================================================================
from app.models.base import BaseRepository # Temel depo sınıfı
from app.models.entities import Category # Kategori varlık sınıfı
from typing import List, Optional, Tuple
from mysql.connector import Error as MySQLError # MySQL'e özgü hata tipi

# 2. CategoryRepository Sınıfı
# =============================================================================
class CategoryRepository(BaseRepository):
    """Kategori işlemleri için depo (repository) sınıfı."""

    # 2.1. __init__ metodu BaseRepository'den miras alındığı için
    #      CategoryRepository'e özgü ek başlatma gerekmiyorsa yeniden tanımlanmasına gerek yoktur.

    # 2.2. create_category
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
        # print(f"DEBUG: Kategori oluşturuluyor: Ad='{name}', İkon='{icon}'")
        try:
            if not name or not name.strip() or len(name) > 255:
                return False, "Kategori adı gereklidir ve 255 karakterden az olmalıdır.", None
            if not icon or not icon.strip() or len(icon) > 255: # İkon için de boşluk kontrolü eklendi
                return False, "Kategori ikonu gereklidir ve 255 karakterden az olmalıdır.", None

            # Aynı isimde bir kategori olup olmadığını kontrol et
            existing_category = self.get_category_by_name(name)
            if existing_category:
                # print(f"DEBUG: '{name}' adında bir kategori zaten mevcut.")
                return False, f"'{name}' adında bir kategori zaten mevcut.", None

            query = "INSERT INTO ai_categories (name, icon) VALUES (%s, %s)"
            category_id = self.insert(query, (name.strip(), icon.strip())) # strip() eklendi

            if category_id:
                # print(f"DEBUG: Kategori '{name}' başarıyla oluşturuldu. ID: {category_id}")
                return True, f"Kategori '{name}' başarıyla oluşturuldu.", category_id
            else:
                # print(f"DEBUG: Kategori '{name}' oluşturulamadı, insert metodu ID döndürmedi.")
                # Bu durum genellikle insert metodunda bir sorun varsa veya veritabanı bir ID döndürmüyorsa oluşur.
                # BaseRepository.insert metodunun lastrowid döndürdüğünü varsayıyoruz.
                return False, f"Kategori '{name}' oluşturulamadı.", None
        except MySQLError as e:
            # print(f"DEBUG: Kategori oluşturulurken veritabanı hatası: {e}")
            return False, f"Veritabanı hatası: {str(e)}", None
        except Exception as ex: # Beklenmedik diğer hatalar için
            # print(f"DEBUG: Kategori oluşturulurken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}", None

    # 2.3. update_category
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
        # print(f"DEBUG: Kategori güncelleniyor: ID={category_id}, Ad='{name}', İkon='{icon}'")
        try:
            if not category_id or not isinstance(category_id, int) or category_id <= 0:
                return False, "Geçerli bir kategori ID'si gereklidir."
            if not name or not name.strip() or len(name) > 255:
                return False, "Kategori adı gereklidir ve 255 karakterden az olmalıdır."
            if not icon or not icon.strip() or len(icon) > 255: # İkon için de boşluk kontrolü eklendi
                return False, "Kategori ikonu gereklidir ve 255 karakterden az olmalıdır."

            # Kategorinin var olup olmadığını kontrol et
            category = self.get_category_by_id(category_id)
            if not category:
                # print(f"DEBUG: ID'si {category_id} olan kategori bulunamadı.")
                return False, f"ID'si {category_id} olan kategori bulunamadı."

            # Güncellenmek istenen isimle başka bir kategori (mevcut kategori hariç) olup olmadığını kontrol et
            query_check_name = "SELECT id FROM ai_categories WHERE name = %s AND id != %s"
            existing_with_same_name = self.fetch_one(query_check_name, (name.strip(), category_id))
            if existing_with_same_name:
                # print(f"DEBUG: '{name}' adında başka bir kategori zaten mevcut.")
                return False, f"'{name}' adında başka bir kategori zaten mevcut."

            query = "UPDATE ai_categories SET name = %s, icon = %s WHERE id = %s"
            rows_affected = self.execute_query(query, (name.strip(), icon.strip(), category_id))

            if rows_affected > 0:
                # print(f"DEBUG: Kategori ID {category_id} başarıyla güncellendi.")
                return True, "Kategori başarıyla güncellendi."
            else:
                # print(f"DEBUG: Kategori ID {category_id} güncellenirken değişiklik yapılmadı (veriler aynı olabilir).")
                # Eğer veriler aynıysa ve bir değişiklik yapılmadıysa bunu başarılı sayabiliriz.
                return True, "Kategoride herhangi bir değişiklik yapılmadı (veriler aynı olabilir)."
        except MySQLError as e:
            # print(f"DEBUG: Kategori güncellenirken veritabanı hatası: {e}")
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            # print(f"DEBUG: Kategori güncellenirken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.4. delete_category
    # -------------------------------------------------------------------------
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """
        Bir kategoriyi siler. İlişkili modellerin durumu (silinir mi, category_id'si NULL mu olur)
        veritabanı şemasındaki FOREIGN KEY tanımına bağlıdır (ON DELETE CASCADE veya ON DELETE SET NULL).
        Mevcut migrations.py'de ON DELETE SET NULL olarak ayarlanmıştır.
        Args:
            category_id (int): Silinecek kategorinin ID'si.
        Returns:
            Tuple[bool, str]: (başarı_durumu, mesaj)
        """
        # print(f"DEBUG: Kategori siliniyor: ID={category_id}")
        try:
            if not category_id or not isinstance(category_id, int) or category_id <= 0:
                return False, "Geçerli bir kategori ID'si gereklidir."

            category = self.get_category_by_id(category_id)
            if not category:
                # print(f"DEBUG: Silinecek kategori bulunamadı: ID={category_id}")
                return False, f"ID'si {category_id} olan kategori bulunamadı."
            
            category_name = category.name # Mesaj için sakla

            # İlişkili modellerin sayısını al (bilgilendirme amaçlı)
            query_model_count = "SELECT COUNT(*) as model_count FROM ai_models WHERE category_id = %s"
            count_result = self.fetch_one(query_model_count, (category_id,))
            model_count = count_result['model_count'] if count_result else 0
            # print(f"DEBUG: '{category_name}' kategorisine bağlı {model_count} model bulunuyor.")

            # Kategoriyi sil
            # migrations.py'de ai_models.category_id için ON DELETE SET NULL tanımlandığından,
            # bu işlem ilişkili modellerin category_id'sini NULL yapacaktır, modelleri silmeyecektir.
            query_delete = "DELETE FROM ai_categories WHERE id = %s"
            rows_affected = self.execute_query(query_delete, (category_id,))

            if rows_affected > 0:
                # print(f"DEBUG: Kategori '{category_name}' (ID: {category_id}) başarıyla silindi.")
                return True, (f"Kategori '{category_name}' başarıyla silindi. "
                              f"Bu kategoriye bağlı {model_count} modelin kategori bağlantısı kaldırıldı (NULL yapıldı).")
            else:
                # print(f"DEBUG: Kategori '{category_name}' (ID: {category_id}) silinemedi veya zaten yoktu.")
                # Bu durum normalde get_category_by_id kontrolü ile yakalanır, ama yine de bir güvenlik önlemi.
                return False, f"Kategori '{category_name}' silinemedi."
        except MySQLError as e:
            # print(f"DEBUG: Kategori silinirken veritabanı hatası: {e}")
            # Yabancı anahtar kısıtlamaları gibi hatalar burada yakalanabilir.
            return False, f"Veritabanı hatası: {str(e)}"
        except Exception as ex:
            # print(f"DEBUG: Kategori silinirken beklenmedik hata: {ex}")
            return False, f"Beklenmedik bir hata oluştu: {str(ex)}"

    # 2.5. get_category_by_id
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
            # print(f"DEBUG: get_category_by_id için geçersiz ID: {category_id}")
            return None
        query = "SELECT id, name, icon FROM ai_categories WHERE id = %s"
        result = self.fetch_one(query, (category_id,))
        # print(f"DEBUG: get_category_by_id({category_id}) sonucu: {'Bulundu' if result else 'Bulunamadı'}")
        return Category.from_dict(result) if result else None

    # 2.6. get_category_by_name
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
            # print(f"DEBUG: get_category_by_name için geçersiz isim: '{name}'")
            return None
        query = "SELECT id, name, icon FROM ai_categories WHERE name = %s"
        result = self.fetch_one(query, (name.strip(),))
        # print(f"DEBUG: get_category_by_name('{name}') sonucu: {'Bulundu' if result else 'Bulunamadı'}")
        return Category.from_dict(result) if result else None

    # 2.7. get_all_categories
    # -------------------------------------------------------------------------
    def get_all_categories(self) -> List[Category]:
        """
        Tüm kategorileri ID'ye göre sıralanmış olarak getirir.
        Returns:
            List[Category]: Tüm Category nesnelerinin listesi.
        """
        query = "SELECT id, name, icon FROM ai_categories ORDER BY id" # İsteğe bağlı olarak name'e göre de sıralanabilir
        results = self.fetch_all(query)
        # print(f"DEBUG: get_all_categories sonucu: {len(results)} kategori bulundu.")
        return [Category.from_dict(row) for row in results if row] # row kontrolü eklendi
