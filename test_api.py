#!/usr/bin/env python3
"""
Simple test script for the Agent Factory API
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing Agent Factory API...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Refine prompt endpoint
    test_payload = {"goal": "I need a bot for GitHub."}
    
    try:
        response = requests.post(
            f"{base_url}/refine_prompt",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Refine prompt: {response.status_code}")
        result = response.json()
        print(f"📝 Input: {test_payload['goal']}")
        print(f"📝 Output: {result['refined_prompt']}")
        
    except Exception as e:
        print(f"❌ Refine prompt test failed: {e}")

    # Test 3: Feasibility endpoint
    feasibility_payload = {"prompt": "A bot to run a nightly sanity check on 10 internal APIs and post a summary to Slack."}
    
    try:
        response = requests.post(
            f"{base_url}/feasibility",
            json=feasibility_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n✅ Feasibility analysis: {response.status_code}")
        result = response.json()
        print(f"📝 Input: {feasibility_payload['prompt']}")
        print(f"📝 Analysis: {result['text']}")
        print(f"📝 Option 1: {result['option1_title']} ({result['option1_value']})")
        print(f"📝 Option 2: {result['option2_title']} ({result['option2_value']})")
        
    except Exception as e:
        print(f"❌ Feasibility analysis test failed: {e}")

    # Test 4: NEW - Optimize Prompt endpoint (The Architect)
    optimize_payload = {
        "prompt": "Check for rollback scripts in DB migration PRs.",
        "path": "Custom Python Agent"
    }
    
    try:
        response = requests.post(
            f"{base_url}/optimize_prompt",
            json=optimize_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n✅ Optimize prompt (Architect): {response.status_code}")
        result = response.json()
        print(f"📝 Input: {optimize_payload['prompt']}")
        print(f"📝 Path: {optimize_payload['path']}")
        print(f"📝 Final Prompt: {result['final_prompt'][:150]}...")
        
        # Verify expected output format
        expected_keywords = ["FastAPI", "GitHub", "webhook"]
        if any(keyword in result['final_prompt'] for keyword in expected_keywords):
            print("✅ Output contains expected technical specification keywords")
        else:
            print("⚠️  Output format may need adjustment")
            
    except Exception as e:
        print(f"❌ Optimize prompt test failed: {e}")

    # Test 5: Test Jira example specifically
    jira_payload = {
        "prompt": "When a new 'feature request' ticket is created in our 'PHOENIX' Jira project, add its details to my 'Q3 Planning' Google Sheet.",
        "path": "n8n-only workflow"
    }
    
    try:
        response = requests.post(
            f"{base_url}/optimize_prompt",
            json=jira_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n✅ Jira Example Test: {response.status_code}")
        result = response.json()
        print(f"📝 Jira Prompt: {result['final_prompt'][:150]}...")
        
        if "PHOENIX" in result['final_prompt'] and "Jira Trigger" in result['final_prompt']:
            print("✅ Jira example working correctly with specific details")
        else:
            print("⚠️  Jira example may need adjustment")
            
    except Exception as e:
        print(f"❌ Jira example test failed: {e}")

    # Test 6: Station 4 - Builder Agent (Code Generation)
    print("\n=== Testing Station 4 - Builder Agent ===")
    
    # Test n8n workflow generation
    n8n_payload = {
        "optimized_prompt": "Create an n8n JSON workflow that syncs Jira issues to a Google Sheet when new issues are created in the PHOENIX project."
    }
    
    try:
        response = requests.post(
            f"{base_url}/generate_code",
            json=n8n_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ n8n Generation Test: {response.status_code}")
        result = response.json()
        print(f"📝 Generated Type: {result['type']}")
        print(f"📝 Code Preview: {result['code'][:200]}...")
        
        if result['type'] == 'n8n_workflow' and 'nodes' in result['code']:
            print("✅ n8n workflow generation working correctly")
        else:
            print("⚠️  n8n workflow generation may need adjustment")
            
    except Exception as e:
        print(f"❌ n8n generation test failed: {e}")

    # Test Python FastAPI generation
    python_payload = {
        "optimized_prompt": "Create a Python FastAPI service that handles GitHub webhooks and sends security vulnerability alerts to Slack."
    }
    
    try:
        response = requests.post(
            f"{base_url}/generate_code",
            json=python_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n✅ Python Generation Test: {response.status_code}")
        result = response.json()
        print(f"📝 Generated Type: {result['type']}")
        print(f"📝 Code Preview: {result['code'][:200]}...")
        
        if result['type'] == 'python_agent' and 'FastAPI' in result['code']:
            print("✅ Python FastAPI generation working correctly")
        else:
            print("⚠️  Python FastAPI generation may need adjustment")
            
    except Exception as e:
        print(f"❌ Python generation test failed: {e}")

    print("\n=== AGENT FACTORY COMPLETE ===")
    print("🏭 All 4 stations tested:")
    print("   Station 1: Clarifier (Prompt Refinement)")
    print("   Station 2: Strategist (Feasibility Analysis)") 
    print("   Station 3: Architect (Technical Specification)")
    print("   Station 4: Builder (Code Generation)")

if __name__ == "__main__":
    test_api()
