#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db_connection import execute_query

def add_openrouter_models():
    """
    OpenRouter modellerini veritabanına ekle
    """
    print("=== Adding OpenRouter Models ===")
    
    try:
        # GPT-4o
        print("\n1. Adding GPT-4o...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'openai/gpt-4o',
            'TEXT',
            'OpenRouter',
            'YOUR_OPENROUTER_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ GPT-4o added")
        
        # GPT-4o Mini
        print("\n2. Adding GPT-4o Mini...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'openai/gpt-4o-mini',
            'TEXT',
            'OpenRouter',
            'YOUR_OPENROUTER_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ GPT-4o Mini added")
        
        # Claude 3.5 Sonnet
        print("\n3. Adding Claude 3.5 Sonnet...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'anthropic/claude-3.5-sonnet',
            'TEXT',
            'OpenRouter',
            'YOUR_OPENROUTER_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ Claude 3.5 Sonnet added")
        
        # Claude 3.5 Haiku
        print("\n4. Adding Claude 3.5 Haiku...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'anthropic/claude-3.5-haiku',
            'TEXT',
            'OpenRouter',
            'YOUR_OPENROUTER_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ Claude 3.5 Haiku added")
        
        # Llama 3.1 8B
        print("\n5. Adding Llama 3.1 8B...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'meta-llama/llama-3.1-8b-instruct',
            'TEXT',
            'OpenRouter',
            'YOUR_OPENROUTER_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ Llama 3.1 8B added")
        
        # Llama 3.1 70B
        print("\n6. Adding Llama 3.1 70B...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'meta-llama/llama-3.1-70b-instruct',
            'TEXT',
            'OpenRouter',
            'YOUR_OPENROUTER_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ Llama 3.1 70B added")
        
        print("\n✅ All OpenRouter models added successfully!")
        print("\n⚠️  IMPORTANT: Don't forget to update the API keys in the database!")
        
    except Exception as e:
        print(f"\n❌ Error adding OpenRouter models: {e}")

if __name__ == "__main__":
    add_openrouter_models()
