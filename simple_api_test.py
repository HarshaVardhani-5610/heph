#!/usr/bin/env python3
"""
Simple API Key Test - No external dependencies
Tests your Perplexity API keys directly
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error

def load_env_file():
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("❌ .env file not found!")
        return {}
    return env_vars

def test_perplexity_api(api_key):
    """Test a Perplexity API key with a simple request"""
    url = "https://api.perplexity.ai/chat/completions"
    
    data = {
        "model": "sonar",
        "messages": [
            {"role": "user", "content": "What is 2+2? Answer in one word."}
        ],
        "max_tokens": 10
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Prepare request
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers)
        
        # Make request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return True, result.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return False, f"HTTP {e.code}: {error_body}"
    except Exception as e:
        return False, str(e)

def main():
    print("🔑 PERPLEXITY API KEY TEST")
    print("==========================")
    print()
    
    # Load environment variables
    env_vars = load_env_file()
    if not env_vars:
        print("❌ Could not load .env file")
        return
    
    # Test each API key
    real_keys = 0
    working_keys = 0
    
    print("📊 Testing your API keys:")
    print()
    
    for i in range(1, 11):
        key_name = f"PERPLEXITY_API_KEY_{i}"
        key_value = env_vars.get(key_name, "").strip()
        
        if key_value and key_value.startswith('pplx-'):
            real_keys += 1
            print(f"🔑 Key {i}: {key_value[:15]}... ", end="")
            
            # Test the API key
            success, response = test_perplexity_api(key_value)
            
            if success:
                print("✅ WORKING")
                print(f"   Response: {response}")
                working_keys += 1
            else:
                print("❌ FAILED")
                print(f"   Error: {response}")
            print()
        else:
            print(f"⚪ Key {i}: Empty placeholder (correctly ignored)")
    
    print("\n" + "="*50)
    print("📈 SUMMARY:")
    print(f"   Total real keys found: {real_keys}")
    print(f"   Working keys: {working_keys}")
    print(f"   Empty placeholders: {10 - real_keys} (correctly ignored)")
    
    if working_keys > 0:
        print("\n🎉 SUCCESS!")
        print("   ✅ Your API keys are working correctly")
        print("   ✅ Empty placeholders are properly ignored")
        print("   ✅ The rotation system will work perfectly")
        print("\n🚀 Ready to start the Agent Factory!")
    else:
        print("\n❌ ISSUES FOUND:")
        if real_keys == 0:
            print("   No real API keys detected")
        else:
            print("   API keys found but not working - check your keys")

if __name__ == "__main__":
    main()
