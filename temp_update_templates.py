import sqlite3
import json # json modülünü import etmeyi unutmayın

db_path = 'zekai.db'  # VEYA 'instance/zekai.db' gibi doğru yol
updates = [
    (6, {'model': 'openrouter/deepseek/deepseek-coder', 'messages': '$messages'}),
    (7, {'model': 'google/llama-4-maverick', 'messages': '$messages', 'max_tokens': 150}),
    (8, {'model': 'deepseek/deepseek-r1:free', 'messages': '$messages'})
]

conn = None
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"Veritabanına bağlandı: {db_path}")

    for model_id, template_dict in updates:
        # Python dict'ini JSON string'ine çevirirken $messages'ı korumak için geçici bir placeholder kullanalım
        placeholder = "__MESSAGES_PLACEHOLDER__"
        if template_dict.get("messages") == "$messages":
            template_dict["messages"] = placeholder

        # Python dict'ini JSON string'ine çevir
        template_str = json.dumps(template_dict)

        # Geçici placeholder'ı gerçek $messages (tırnaksız) ile değiştir
        template_str = template_str.replace(f'"{placeholder}"', '$messages')

        print(f"ID {model_id} için template güncelleniyor: {template_str}")
        cursor.execute("UPDATE ai_models SET request_body_template = ? WHERE id = ?", (template_str, model_id))
        if cursor.rowcount == 0:
            print(f"Uyarı: ID {model_id} bulunamadı veya güncelleme yapılmadı.")
        else:
            print(f"ID {model_id} başarıyla güncellendi.")

    conn.commit()
    print("Değişiklikler başarıyla kaydedildi.")

except sqlite3.Error as e:
    print(f"SQLite hatası: {e}")
    if conn:
        conn.rollback() # Hata durumunda geri al
        print("Değişiklikler geri alındı.")
finally:
    if conn:
        conn.close()
        print("Veritabanı bağlantısı kapatıldı.")
