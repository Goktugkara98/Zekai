#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db_connection import execute_query

def add_all_models():
    """
    Tüm modelleri veritabanına ekle (Gemini + OpenRouter)
    """
    print("=== Adding All Models ===")
    
    try:
        # Önce mevcut modelleri temizle
        print("\n1. Clearing existing models...")
        execute_query("DELETE FROM models", fetch=False)
        print("  ✅ Existing models cleared")
        
        # Gemini modelleri
        print("\n2. Adding Gemini models...")
        
        # Gemini 2.5 Flash
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'gemini-2.5-flash',
            'TEXT',
            'Google',
            'YOUR_GEMINI_API_KEY_HERE',
            True
        ), fetch=False)
        print("  ✅ Gemini 2.5 Flash added")
        
        # Gemini 2.5 Pro
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'gemini-2.5-pro',
            'TEXT',
            'Google',
            'YOUR_GEMINI_API_KEY_HERE',
            True
        ), fetch=False)
        print("  ✅ Gemini 2.5 Pro added")
        
        # OpenRouter modelleri
        print("\n3. Adding OpenRouter models...")
        
        openrouter_models = [
            ('openai/gpt-4o', 'OpenRouter', 'TEXT'),
            ('openai/gpt-4o-mini', 'OpenRouter', 'TEXT'),
            ('anthropic/claude-3.5-sonnet', 'OpenRouter', 'TEXT'),
            ('anthropic/claude-3.5-haiku', 'OpenRouter', 'TEXT'),
            ('meta-llama/llama-3.1-8b-instruct', 'OpenRouter', 'TEXT'),
            ('meta-llama/llama-3.1-70b-instruct', 'OpenRouter', 'TEXT'),
            ('google/gemini-pro', 'OpenRouter', 'TEXT'),
            ('google/gemini-pro-vision', 'OpenRouter', 'MULTIMODAL'),
            ('mistralai/mistral-7b-instruct', 'OpenRouter', 'TEXT'),
            ('mistralai/mixtral-8x7b-instruct', 'OpenRouter', 'TEXT'),
        ]
        
        for model_name, provider_name, model_type in openrouter_models:
            execute_query("""
                INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                model_name,
                model_type,
                provider_name,
                'YOUR_OPENROUTER_API_KEY_HERE',
                True
            ), fetch=False)
            print(f"  ✅ {model_name} added")
        
        print("\n✅ All models added successfully!")
        print("\n⚠️  IMPORTANT: Don't forget to update the API keys in the database!")
        print("\n📝 Next steps:")
        print("  1. Update Gemini API keys in the database")
        print("  2. Update OpenRouter API keys in the database")
        print("  3. Test the models in the chat interface")
        
    except Exception as e:
        print(f"\n❌ Error adding models: {e}")

if __name__ == "__main__":
    add_all_models()
