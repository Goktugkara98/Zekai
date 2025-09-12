#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db_connection import execute_query
from app.services.provider_factory import ProviderFactory
from app.services.chat_service import ChatService

def test_provider_system():
    print("=== Provider System Test ===")
    
    # 1. Database'i güncelle (migration)
    print("\n1. Updating database schema...")
    try:
        # Eski tabloyu sil ve yeniden oluştur
        execute_query("DROP TABLE IF EXISTS models", fetch=False)
        execute_query("DROP TABLE IF EXISTS chats", fetch=False)
        execute_query("DROP TABLE IF EXISTS messages", fetch=False)
        
        # Models tablosunu oluştur
        create_models_sql = """
            CREATE TABLE IF NOT EXISTS models (
                model_id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(255) NOT NULL,
                model_type VARCHAR(100),
                provider_name VARCHAR(100) NOT NULL,
                provider_type ENUM('gemini', 'openrouter', 'openai', 'anthropic') NOT NULL,
                api_key VARCHAR(500),
                base_url VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_model_name (model_name),
                INDEX idx_provider_name (provider_name),
                INDEX idx_provider_type (provider_type),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        execute_query(create_models_sql, fetch=False)
        
        # Chats tablosunu oluştur
        create_chats_sql = """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id VARCHAR(36) PRIMARY KEY,
                model_id INT,
                title VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP NULL,
                FOREIGN KEY (model_id) REFERENCES models(model_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        execute_query(create_chats_sql, fetch=False)
        
        # Messages tablosunu oluştur
        create_messages_sql = """
            CREATE TABLE IF NOT EXISTS messages (
                message_id INT AUTO_INCREMENT PRIMARY KEY,
                chat_id VARCHAR(36),
                model_id INT,
                content TEXT NOT NULL,
                is_user BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
                FOREIGN KEY (model_id) REFERENCES models(model_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        execute_query(create_messages_sql, fetch=False)
        
        print("  ✅ Database schema updated")
        
    except Exception as e:
        print(f"  ❌ Database update error: {e}")
        return
    
    # 2. Test modelleri ekle
    print("\n2. Adding test models...")
    try:
        # Gemini model
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, provider_type, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'gemini-2.5-flash',
            'TEXT',
            'Google',
            'gemini',
            'AIzaSyDj_W8-D5BbPZYTmJ7YCrjnkaiDsVsEix0',
            True
        ), fetch=False)
        
        # OpenRouter model
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, provider_type, api_key, base_url, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'openai/gpt-4o',
            'TEXT',
            'OpenAI',
            'openrouter',
            'sk-or-v1-1234567890abcdef',  # Test key
            'https://openrouter.ai/api/v1',
            True
        ), fetch=False)
        
        print("  ✅ Test models added")
        
    except Exception as e:
        print(f"  ❌ Model addition error: {e}")
        return
    
    # 3. Provider factory test
    print("\n3. Testing provider factory...")
    try:
        # Gemini test
        gemini_service = ProviderFactory.get_service('gemini')
        print(f"  Gemini service: {'✅' if gemini_service else '❌'}")
        
        # OpenRouter test
        openrouter_service = ProviderFactory.get_service('openrouter')
        print(f"  OpenRouter service: {'✅' if openrouter_service else '❌'}")
        
        # Unsupported provider test
        unsupported_service = ProviderFactory.get_service('unsupported')
        print(f"  Unsupported provider: {'✅' if not unsupported_service else '❌'}")
        
    except Exception as e:
        print(f"  ❌ Provider factory error: {e}")
    
    # 4. Chat service test
    print("\n4. Testing chat service...")
    try:
        chat_service = ChatService()
        
        # Chat oluştur
        result = chat_service.create_chat(1, 'Test Chat')
        print(f"  Chat creation: {'✅' if result['success'] else '❌'}")
        
        if result['success']:
            chat_id = result['chat_id']
            print(f"  Chat ID: {chat_id}")
            
            # Chat detaylarını al
            chat_details = chat_service.get_chat(chat_id)
            print(f"  Chat details: {'✅' if chat_details['success'] else '❌'}")
            
            if chat_details['success']:
                chat_data = chat_details['chat']
                print(f"    Model: {chat_data['model_name']}")
                print(f"    Provider: {chat_data['provider_type']}")
        
    except Exception as e:
        print(f"  ❌ Chat service error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_provider_system()
