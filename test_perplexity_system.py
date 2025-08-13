#!/usr/bin/env python3
"""
Test Suite for Perplexity API Key Rotation System
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_key_manager import PerplexityAPIManager, call_perplexity_api

async def test_api_key_rotation():
    """Test the API key rotation system comprehensively"""
    
    print("🔄 PERPLEXITY API KEY ROTATION TEST SUITE")
    print("=" * 60)
    
    # Test 1: Manager Initialization
    print("\n📋 Test 1: Manager Initialization")
    print("-" * 40)
    
    try:
        manager = PerplexityAPIManager()
        status = manager.get_status()
        
        print(f"✅ Manager initialized successfully")
        print(f"📊 Total keys configured: {status['total_keys']}")
        print(f"📊 Active keys: {status['active_keys']}")
        print(f"📊 Exhausted keys: {status['exhausted_keys']}")
        
        if status['total_keys'] == 0:
            print("⚠️  No API keys configured! Please set PERPLEXITY_API_KEY_1 through PERPLEXITY_API_KEY_10")
            print("   Run: export PERPLEXITY_API_KEY_1='your-api-key-here'")
            return False
            
    except Exception as e:
        print(f"❌ Manager initialization failed: {e}")
        return False
    
    # Test 2: API Call
    print("\n🔗 Test 2: Basic API Call")
    print("-" * 40)
    
    try:
        start_time = time.time()
        
        response = await call_perplexity_api(
            "What is the latest version of Python? Give a brief answer.",
            max_tokens=200,
            temperature=0.1
        )
        
        duration = time.time() - start_time
        
        print(f"✅ API call successful")
        print(f"⏱️  Response time: {duration:.2f}s")
        print(f"📄 Response preview: {str(response)[:200]}...")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False
    
    # Test 3: Key Status Tracking
    print("\n📊 Test 3: Key Status Tracking")
    print("-" * 40)
    
    try:
        status = manager.get_status()
        
        print("Key Status Details:")
        for i, key_info in enumerate(status['keys']):
            print(f"  Key {i+1} ({key_info['key_id']}):")
            print(f"    Active: {key_info['is_active']}")
            print(f"    Credits Exhausted: {key_info['credits_exhausted']}")
            print(f"    Error Count: {key_info['error_count']}")
            print(f"    Last Used: {key_info['last_used'] or 'Never'}")
            print(f"    Last Error: {key_info['last_error'] or 'None'}")
            print()
        
    except Exception as e:
        print(f"❌ Status tracking failed: {e}")
        return False
    
    # Test 4: Multiple API Calls (stress test)
    print("\n🔥 Test 4: Multiple API Calls (Stress Test)")
    print("-" * 40)
    
    try:
        questions = [
            "What is FastAPI?",
            "Explain n8n workflow automation.",
            "What are webhooks?",
            "How does API key rotation work?",
            "What is the latest Python version?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"  📤 Call {i}: {question}")
            
            try:
                start_time = time.time()
                response = await call_perplexity_api(
                    question,
                    max_tokens=150,
                    temperature=0.2
                )
                duration = time.time() - start_time
                
                print(f"    ✅ Success ({duration:.2f}s)")
                
                # Brief delay between calls
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Failed: {e}")
        
        # Show final status
        final_status = manager.get_status()
        print(f"\n📊 Final Status: {final_status['active_keys']}/{final_status['total_keys']} keys active")
        
    except Exception as e:
        print(f"❌ Stress test failed: {e}")
        return False
    
    # Test 5: Configuration Persistence
    print("\n💾 Test 5: Configuration Persistence")
    print("-" * 40)
    
    try:
        # Check if config file exists
        config_file = "perplexity_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"✅ Config file exists: {config_file}")
                print(f"📅 Last updated: {config.get('last_updated', 'Unknown')}")
                print(f"🔢 Keys in config: {len(config.get('api_keys', []))}")
        else:
            print(f"⚠️  Config file not found: {config_file}")
            
    except Exception as e:
        print(f"❌ Config persistence test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 API KEY ROTATION TEST SUITE COMPLETE!")
    print("=" * 60)
    
    return True

async def test_integration_with_agent_factory():
    """Test integration with the Agent Factory"""
    
    print("\n🏭 AGENT FACTORY INTEGRATION TEST")
    print("=" * 60)
    
    try:
        import requests
        import time
        
        # Check if Agent Factory is running
        base_url = "http://localhost:8000"
        
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code != 200:
                print("⚠️  Agent Factory not running. Start it with:")
                print("   cd agents && python main_service.py")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️  Agent Factory not running. Start it with:")
            print("   cd agents && python main_service.py")
            return False
        
        # Test API status endpoint
        print("\n📊 Testing API Status Endpoint")
        print("-" * 30)
        
        try:
            response = requests.get(f"{base_url}/api-status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ API Status accessible")
                print(f"📊 Active keys: {status.get('active_keys', 0)}")
                print(f"📊 Total keys: {status.get('total_keys', 0)}")
            else:
                print(f"❌ API Status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ API Status error: {e}")
        
        # Test Agent Factory endpoints with real API
        print("\n🔧 Testing Agent Factory with Real API")
        print("-" * 30)
        
        test_cases = [
            {
                "endpoint": "/refine_prompt",
                "payload": {"goal": "I want automation for GitHub notifications"},
                "description": "Prompt Refinement"
            },
            {
                "endpoint": "/feasibility", 
                "payload": {"prompt": "Send Slack messages when GitHub issues are created"},
                "description": "Feasibility Analysis"
            },
            {
                "endpoint": "/optimize_prompt",
                "payload": {
                    "prompt": "Monitor GitHub for new pull requests and send Slack alerts",
                    "path": "n8n-only workflow"
                },
                "description": "Prompt Optimization"
            }
        ]
        
        for test in test_cases:
            print(f"\n  📤 Testing {test['description']}")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{base_url}{test['endpoint']}",
                    json=test['payload'],
                    timeout=30
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"    ✅ Success ({duration:.2f}s)")
                    result = response.json()
                    # Show preview of response
                    if isinstance(result, dict):
                        for key, value in list(result.items())[:2]:  # Show first 2 fields
                            if isinstance(value, str):
                                preview = value[:100] + "..." if len(value) > 100 else value
                                print(f"    📄 {key}: {preview}")
                else:
                    print(f"    ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        print("\n✅ Agent Factory integration test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("🧪 PERPLEXITY API SYSTEM TEST SUITE")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Run basic API tests
    api_success = await test_api_key_rotation()
    
    if api_success:
        # Run integration tests
        await test_integration_with_agent_factory()
    
    print(f"\n🏁 ALL TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
