#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.chat_service import ChatService
from app.database.db_connection import execute_query

def test_model_name_consistency():
    print("=== Model Name Consistency Test ===")
    
    # 1. Database'deki model'leri kontrol et
    print("\n1. Database models:")
    try:
        models = execute_query('SELECT model_id, model_name FROM models', fetch=True)
        for model in models:
            print(f"  ID: {model['model_id']}, Name: {model['model_name']}")
    except Exception as e:
        print(f"  Error: {e}")
        return
    
    # 2. Chat oluştur
    print("\n2. Creating chat...")
    try:
        chat_service = ChatService()
        result = chat_service.create_chat(1, 'Test Chat')
        print(f"  Chat creation result: {result}")
        
        if result['success']:
            # 3. Chat'i al ve model_name'i kontrol et
            print("\n3. Getting chat details...")
            chat_result = chat_service.get_chat(result['chat_id'])
            print(f"  Chat details: {chat_result}")
            
            if chat_result['success']:
                chat_data = chat_result['chat']
                print(f"  Model ID: {chat_data['model_id']}")
                print(f"  Model Name: {chat_data['model_name']}")
                print(f"  Provider Name: {chat_data['provider_name']}")
            else:
                print(f"  Error getting chat: {chat_result['error']}")
        else:
            print(f"  Error creating chat: {result['error']}")
            
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    test_model_name_consistency()
