#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db_connection import execute_query

def add_gemini_models():
    """
    Gemini modellerini veritabanına ekle
    """
    print("=== Adding Gemini Models ===")
    
    try:
        # Gemini 2.5 Flash
        print("\n1. Adding Gemini 2.5 Flash...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'gemini-2.5-flash',
            'TEXT',
            'Google',
            'YOUR_GEMINI_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ Gemini 2.5 Flash added")
        
        # Gemini 2.5 Pro
        print("\n2. Adding Gemini 2.5 Pro...")
        execute_query("""
            INSERT INTO models (model_name, model_type, provider_name, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'gemini-2.5-pro',
            'TEXT',
            'Google',
            'YOUR_GEMINI_API_KEY_HERE',  # Buraya API key'inizi yazın
            True
        ), fetch=False)
        print("  ✅ Gemini 2.5 Pro added")
        
        print("\n✅ All Gemini models added successfully!")
        print("\n⚠️  IMPORTANT: Don't forget to update the API keys in the database!")
        
    except Exception as e:
        print(f"\n❌ Error adding Gemini models: {e}")

if __name__ == "__main__":
    add_gemini_models()
