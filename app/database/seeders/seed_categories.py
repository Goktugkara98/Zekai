# =============================================================================
# CATEGORIES SEEDER
# =============================================================================
# Bu dosya, categories tablosuna başlangıç verilerini ekler.
# Migration'lardan bağımsızdır ve güvenle tekrar çalıştırılabilir (idempotent).
# =============================================================================

import logging
from typing import List, Tuple
from app.database.db_connection import execute_query

logger = logging.getLogger(__name__)


def seed_categories() -> bool:
    """
    Kategorileri başlangıç verisi olarak ekler. Mevcut kayıtlar atlanır.
    Returns True on success.
    """
    try:
        categories: List[Tuple[str, str]] = [
            ("Genel Sohbet & Bilgi", "genel-sohbet-bilgi"),
            ("Metin & İçerik Üretimi", "metin-icerik-uretimi"),
            ("Çeviri & Özetleme", "ceviri-ozetleme"),
            ("Yazılım Geliştirme", "yazilim-gelistirme"),
            ("Kod Hata Analizi", "kod-hata-analizi"),
            ("Veri & Matematiksel Analiz", "veri-matematiksel-analiz"),
            ("Görsel Tasarım & Üretim", "gorsel-tasarim-uretim"),
            ("Video & Animasyon", "video-animasyon"),
            ("Ses & Konuşma Teknolojileri", "ses-konusma-teknolojileri"),
            ("Sağlık & Tıp", "saglik-tip"),
            ("Hukuk & Mevzuat", "hukuk-mevzuat"),
            ("Finans & Ekonomi", "finans-ekonomi"),
            ("Eğitim & Öğrenme", "egitim-ogrenme"),
            ("Bilim & Araştırma", "bilim-arastirma"),
            ("Web Arama & Bilgi Erişimi", "web-arama-bilgi-erisimi"),
            ("Kaynaklı & Doğrulama Odaklı Bilgi", "kaynakli-dogrulama-odakli-bilgi"),
            ("Hikâye & Yaratıcı Yazım", "hikaye-yaratici-yazim"),
            ("Rol Yapma & Sanal Karakterler", "rol-yapma-sanal-karakterler"),
            ("Kişisel Asistan & Verimlilik", "kisisel-asistan-verimlilik"),
        ]

        values_clause = ",".join(["(%s, %s)"] * len(categories))
        flat_params = []
        for name, slug in categories:
            flat_params.extend([name, slug])

        insert_sql = f"""
            INSERT IGNORE INTO categories (name, slug)
            VALUES {values_clause}
        """
        execute_query(insert_sql, params=tuple(flat_params), fetch=False)
        logger.info("Categories başlangıç verileri eklendi (var olanlar atlandı)")
        return True
    except Exception as e:
        logger.error(f"Categories başlangıç verileri eklenemedi: {str(e)}")
        return False
