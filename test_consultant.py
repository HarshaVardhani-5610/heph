#!/usr/bin/env python3
"""
Test the new intelligent consultant behavior for Stage 1
"""

import requests
import json

# Test cases to validate the intelligent consultant behavior
test_cases = [
    {
        "name": "Vague website check - should ask for specifics",
        "goal": "I need to check my website"
    },
    {
        "name": "Detailed API monitoring - should ask minimal questions",
        "goal": "Monitor https://api.myapp.com every 5 minutes and send alerts to Slack when down"
    },
    {
        "name": "Clear backup task - should ask for technical details only",
        "goal": "Backup my PostgreSQL database daily at 2 AM"
    },
    {
        "name": "Very clear goal - should ask no questions",
        "goal": "Send a GET request to https://httpbin.org/get every hour and log the response"
    }
]

def test_consultant_behavior():
    """Test the new intelligent consultant behavior"""
    base_url = "http://localhost:8001"
    
    print("🤖 Testing Intelligent Consultant Behavior")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Goal: '{test_case['goal']}'")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/refine_prompt",
                json={"goal": test_case["goal"]},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Analysis: {result['refined_prompt']}")
                if result['questions']:
                    print(f"❓ Questions: {result['questions']}")
                else:
                    print("✨ No questions needed - goal is clear!")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Consultant Behavior Test Complete")

if __name__ == "__main__":
    test_consultant_behavior()
