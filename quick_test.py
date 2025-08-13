#!/usr/bin/env python3
import requests
import json

def quick_test():
    base_url = "http://localhost:8000"
    
    print("=== Quick Test of Agent Factory ===")
    
    # Test health
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"Health failed: {e}")
        return
    
    # Test Station 4 - Builder
    print("\n=== Testing Station 4 - Builder ===")
    payload = {"optimized_prompt": "Create an n8n workflow for Jira to Google Sheets sync"}
    
    try:
        response = requests.post(f"{base_url}/generate_code", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Type: {result.get('type', 'unknown')}")
            print(f"Code length: {len(result.get('code', ''))}")
            print("✅ Station 4 working!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Station 4 failed: {e}")

if __name__ == "__main__":
    quick_test()
