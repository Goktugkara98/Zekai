#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db_connection import execute_query

def update_api_keys():
    """
    API anahtarlarını güncelle
    """
    print("=== Update API Keys ===")
    
    try:
        # Mevcut modelleri listele
        print("\n1. Current models in database:")
        models = execute_query("""
            SELECT model_id, model_name, provider_name, api_key 
            FROM models 
            ORDER BY provider_name, model_name
        """, fetch=True)
        
        if not models:
            print("  No models found in database!")
            return
        
        for model in models:
            model_id = model['model_id']
            model_name = model['model_name']
            provider_name = model['provider_name']
            api_key = model['api_key']
            
            print(f"  ID: {model_id} | {model_name} | {provider_name} | API Key: {'✅' if api_key and api_key != 'YOUR_GEMINI_API_KEY_HERE' and api_key != 'YOUR_OPENROUTER_API_KEY_HERE' else '❌'}")
        
        print("\n2. API Key Update Options:")
        print("  [1] Update Gemini API key")
        print("  [2] Update OpenRouter API key")
        print("  [3] Update specific model API key")
        print("  [4] Show current models")
        print("  [0] Exit")
        
        while True:
            choice = input("\nEnter your choice (0-4): ").strip()
            
            if choice == '0':
                print("Exiting...")
                break
            elif choice == '1':
                update_gemini_key()
            elif choice == '2':
                update_openrouter_key()
            elif choice == '3':
                update_specific_model_key()
            elif choice == '4':
                show_models()
            else:
                print("Invalid choice. Please try again.")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")

def update_gemini_key():
    """Gemini API key'ini güncelle"""
    try:
        api_key = input("Enter Gemini API key: ").strip()
        if not api_key:
            print("API key cannot be empty!")
            return
        
        execute_query("""
            UPDATE models 
            SET api_key = %s 
            WHERE provider_name = 'Google'
        """, (api_key,), fetch=False)
        
        print("✅ Gemini API key updated for all Gemini models!")
        
    except Exception as e:
        print(f"❌ Error updating Gemini key: {e}")

def update_openrouter_key():
    """OpenRouter API key'ini güncelle"""
    try:
        api_key = input("Enter OpenRouter API key: ").strip()
        if not api_key:
            print("API key cannot be empty!")
            return
        
        execute_query("""
            UPDATE models 
            SET api_key = %s 
            WHERE provider_name = 'OpenRouter'
        """, (api_key,), fetch=False)
        
        print("✅ OpenRouter API key updated for all OpenRouter models!")
        
    except Exception as e:
        print(f"❌ Error updating OpenRouter key: {e}")

def update_specific_model_key():
    """Belirli bir modelin API key'ini güncelle"""
    try:
        model_id = input("Enter model ID: ").strip()
        if not model_id.isdigit():
            print("Model ID must be a number!")
            return
        
        api_key = input("Enter API key: ").strip()
        if not api_key:
            print("API key cannot be empty!")
            return
        
        execute_query("""
            UPDATE models 
            SET api_key = %s 
            WHERE model_id = %s
        """, (api_key, model_id), fetch=False)
        
        print(f"✅ API key updated for model ID {model_id}!")
        
    except Exception as e:
        print(f"❌ Error updating model key: {e}")

def show_models():
    """Mevcut modelleri göster"""
    try:
        models = execute_query("""
            SELECT model_id, model_name, provider_name, api_key 
            FROM models 
            ORDER BY provider_name, model_name
        """, fetch=True)
        
        print("\n📋 Current Models:")
        print("-" * 80)
        print(f"{'ID':<3} | {'Model Name':<30} | {'Provider':<15} | {'API Key':<10}")
        print("-" * 80)
        
        for model in models:
            model_id = model['model_id']
            model_name = model['model_name']
            provider_name = model['provider_name']
            api_key = model['api_key']
            
            api_status = '✅' if api_key and api_key not in ['YOUR_GEMINI_API_KEY_HERE', 'YOUR_OPENROUTER_API_KEY_HERE'] else '❌'
            
            print(f"{model_id:<3} | {model_name:<30} | {provider_name:<15} | {api_status:<10}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error showing models: {e}")

if __name__ == "__main__":
    update_api_keys()
