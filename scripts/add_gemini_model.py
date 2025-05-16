"""
Gemini API Model Ekleme Scripti

Bu script, Gemini API'sini kullanmak için gerekli model yapılandırmasını
veritabanına ekler.
"""

import os
import sys
import json
from dotenv import load_dotenv
from pathlib import Path

# Proje kök dizinini bul
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Ortam değişkenlerini yükle
load_dotenv()

# Veritabanı bağlantısı için gerekli modülleri içe aktar
from app.models.base import DatabaseConnection
from app.repositories.model_repository import ModelRepository
from app.repositories.category_repository import CategoryRepository

def ensure_ai_category_exists(db_conn):
    """AI kategorisinin varlığını kontrol eder, yoksa oluşturur."""
    category_repo = CategoryRepository(db_conn)
    
    try:
        # AI kategorisini kontrol et
        categories = category_repo.get_all_categories()
        
        ai_category = next((cat for cat in categories if cat.name.lower() == 'ai models'), None)
        
        # Eğer AI kategorisi yoksa oluştur
        if not ai_category:
            success, message, category_id = category_repo.create_category(
                name="AI Models",
                icon="fas fa-robot"  # Varsayılan bir ikon
            )
            if not success:
                print(f"AI kategorisi oluşturulamadı: {message}")
                return None
            print("AI kategorisi oluşturuldu.")
            return category_id
        
        # Kategori zaten varsa mevcut ID'yi döndür
        return ai_category.id
        
    except Exception as e:
        print(f"Kategori kontrolü sırasında hata oluştu: {str(e)}")
        return None

def add_gemini_model(db_conn, category_id):
    """Gemini modelini veritabanına ekler."""
    model_repo = ModelRepository(db_conn)
    
    # API yapılandırmasını details içinde sakla
    api_config = {
        'request_method': 'POST',
        'request_headers': {
            'Content-Type': 'application/json'
        },
        'request_body_template': {
            'contents': [{
                'parts': [{
                    'text': '{user_message}'
                }]
            }],
            'generationConfig': {
                'temperature': 0.9,
                'topK': 1,
                'topP': 1,
                'maxOutputTokens': 2048,
                'stopSequences': []
            },
            'safetySettings': [
                {
                    'category': 'HARM_CATEGORY_HARASSMENT',
                    'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                },
                {
                    'category': 'HARM_CATEGORY_HATE_SPEECH',
                    'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                },
                {
                    'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                },
                {
                    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                    'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                }
            ]
        },
        'response_path': 'candidates.0.content.parts.0.text'
    }
    
    # Modeli veritabanına ekle
    success, message, model_id = model_repo.create_model(
        category_id=category_id,
        name='Gemini 2.0 Flash',
        icon='fas fa-robot',
        api_url='https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
        data_ai_index='gemini-2.0-flash',
        description='Google\'un gelişmiş çoklu modlu AI modeli',
        details=api_config
    )
    
    if success:
        print(f"Gemini modeli başarıyla eklendi. Model ID: {model_id}")
    else:
        print(f"Gemini modeli eklenirken hata oluştu: {message}")

def main():
    # Veritabanı bağlantısını oluştur
    db_conn = DatabaseConnection()
    
    try:
        # AI kategorisini kontrol et ve gerekirse oluştur
        category_id = ensure_ai_category_exists(db_conn)
        if not category_id:
            print("Hata: AI kategorisi oluşturulamadı.")
            return
        
        # Gemini modelini ekle
        add_gemini_model(db_conn, category_id)
        
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {str(e)}")
    finally:
        # Veritabanı bağlantısını kapat
        if db_conn:
            db_conn.close()

if __name__ == "__main__":
    main()
