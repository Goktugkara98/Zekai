#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db_connection import execute_query
from app.services.provider_factory import ProviderFactory

def test_models():
    """
    Modelleri test et
    """
    print("=== Test Models ===")
    
    try:
        # Modelleri listele
        print("\n1. Available models:")
        models = execute_query("""
            SELECT model_id, model_name, provider_name, api_key 
            FROM models 
            WHERE is_active = TRUE
            ORDER BY provider_name, model_name
        """, fetch=True)
        
        if not models:
            print("  No active models found!")
            return
        
        for model in models:
            model_id = model['model_id']
            model_name = model['model_name']
            provider_name = model['provider_name']
            api_key = model['api_key']
            
            api_status = '✅' if api_key and api_key not in ['YOUR_GEMINI_API_KEY_HERE', 'YOUR_OPENROUTER_API_KEY_HERE'] else '❌'
            
            print(f"  ID: {model_id} | {model_name} | {provider_name} | API: {api_status}")
        
        # Provider testleri
        print("\n2. Testing providers...")
        
        # Gemini test
        print("\n  Testing Gemini provider...")
        gemini_service = ProviderFactory.get_service('gemini')
        if gemini_service:
            print("    ✅ Gemini service created")
        else:
            print("    ❌ Gemini service failed")
        
        # OpenRouter test
        print("\n  Testing OpenRouter provider...")
        openrouter_service = ProviderFactory.get_service('openrouter')
        if openrouter_service:
            print("    ✅ OpenRouter service created")
        else:
            print("    ❌ OpenRouter service failed")
        
        # API key testleri (sadece geçerli key'ler varsa)
        print("\n3. Testing API connections...")
        
        for model in models:
            model_id = model['model_id']
            model_name = model['model_name']
            provider_name = model['provider_name']
            api_key = model['api_key']
            
            # Provider type'ı provider_name'den belirle
            if provider_name == 'Google':
                provider_type = 'gemini'
            elif provider_name == 'OpenRouter':
                provider_type = 'openrouter'
            else:
                provider_type = 'unknown'
            
            if api_key and api_key not in ['YOUR_GEMINI_API_KEY_HERE', 'YOUR_OPENROUTER_API_KEY_HERE']:
                print(f"\n  Testing {model_name} ({provider_type})...")
                
                try:
                    result = ProviderFactory.test_provider_connection(
                        provider_type=provider_type,
                        api_key=api_key,
                        model=model_name
                    )
                    
                    if result['success']:
                        print(f"    ✅ {model_name} connection successful")
                    else:
                        print(f"    ❌ {model_name} connection failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"    ❌ {model_name} test error: {e}")
            else:
                print(f"  ⚠️  {model_name} - API key not set")
        
        print("\n✅ Model testing complete!")
        
    except Exception as e:
        print(f"\n❌ Error testing models: {e}")

if __name__ == "__main__":
    test_models()
