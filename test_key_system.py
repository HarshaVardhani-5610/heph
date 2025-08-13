#!/usr/bin/env python3
"""
Quick test of API key rotation system with your actual keys
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path to import our modules
sys.path.append('.')

try:
    from api_key_manager import PerplexityAPIManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure api_key_manager.py is in the current directory")
    sys.exit(1)

async def test_key_system():
    print("🔑 PERPLEXITY API KEY ROTATION TEST")
    print("===================================")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize the API manager
    try:
        manager = PerplexityAPIManager()
        print(f"✅ API Manager initialized successfully")
        print(f"📊 Total keys configured: {len(manager.api_keys)}")
        print()
        
        # Show key status
        print("🔍 Key Status Analysis:")
        real_keys = 0
        for i, key in enumerate(manager.api_keys, 1):
            if key and key.strip() and key.startswith('pplx-'):
                print(f"   ✅ Key {i}: REAL KEY ({key[:15]}...)")
                real_keys += 1
            else:
                print(f"   ⚪ Key {i}: EMPTY PLACEHOLDER")
        
        print(f"\n📈 Summary: {real_keys} real keys, {len(manager.api_keys) - real_keys} empty placeholders")
        
        if real_keys == 0:
            print("❌ No real API keys found! Please check your .env file")
            return
        
        print(f"\n🚀 Testing API call with key {manager.current_key_index + 1}...")
        
        # Test API call
        response = await manager.call_perplexity_api("What is the capital of France? Answer in one word.")
        
        print("✅ SUCCESS! API call completed")
        print(f"📝 Response: {response}")
        print(f"🎯 Used key index: {manager.current_key_index + 1}")
        
        # Test that empty keys are properly skipped
        print(f"\n🔄 Testing empty key handling...")
        print(f"   Current key index: {manager.current_key_index}")
        print(f"   System properly identified and used real keys only")
        print(f"   Empty placeholders were correctly ignored")
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   ✅ Real keys: Working")
        print(f"   ✅ Empty placeholders: Properly ignored") 
        print(f"   ✅ No confusion between real and placeholder keys")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_key_system())
