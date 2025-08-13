#!/usr/bin/env python3
"""
Comprehensive Test of the 4-Station Agent Factory
"""
import requests
import json

def main():
    base_url = "http://localhost:8000"
    
    print("🏭 AGENT FACTORY - COMPREHENSIVE DEMONSTRATION")
    print("=" * 60)
    
    # Test all 4 stations in sequence
    test_stations(base_url)
    
def test_stations(base_url):
    """Test all 4 stations of the Agent Factory"""
    
    # Test Station 1 - Clarifier
    print("\n🔧 STATION 1 - CLARIFIER (Prompt Refinement)")
    print("-" * 50)
    
    station1_payload = {
        "vague_prompt": "I want automation for my GitHub and Slack"
    }
    
    try:
        response = requests.post(f"{base_url}/refine_prompt", json=station1_payload)
        if response.status_code == 200:
            result = response.json()
            refined_prompt = result['refined_prompt']
            print(f"✅ Status: SUCCESS")
            print(f"📝 Original: {station1_payload['vague_prompt']}")
            print(f"🎯 Refined: {refined_prompt[:200]}...")
            
            # Use refined prompt for next station
            prompt_for_station2 = refined_prompt
        else:
            print(f"❌ Station 1 failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Station 1 error: {e}")
        return
    
    # Test Station 2 - Strategist
    print("\n📊 STATION 2 - STRATEGIST (Feasibility Analysis)")
    print("-" * 50)
    
    station2_payload = {
        "prompt": prompt_for_station2
    }
    
    try:
        response = requests.post(f"{base_url}/feasibility", json=station2_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: SUCCESS")
            print(f"📈 Feasibility Score: {result['feasibility_score']}/10")
            print(f"⚡ Complexity: {result['complexity_level']}")
            print(f"⏱️  Timeline: {result['estimated_timeline']}")
            print(f"💡 Key Requirements: {', '.join(result['key_requirements'][:3])}...")
            
            # Use refined prompt for next station
            prompt_for_station3 = prompt_for_station2
        else:
            print(f"❌ Station 2 failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Station 2 error: {e}")
        return
    
    # Test Station 3 - Architect
    print("\n🏗️ STATION 3 - ARCHITECT (Technical Specification)")
    print("-" * 50)
    
    station3_payload = {
        "prompt": prompt_for_station3
    }
    
    try:
        response = requests.post(f"{base_url}/optimize_prompt", json=station3_payload)
        if response.status_code == 200:
            result = response.json()
            technical_spec = result['final_prompt']
            print(f"✅ Status: SUCCESS")
            print(f"📋 Technical Spec Preview: {technical_spec[:300]}...")
            
            # Use technical spec for final station
            prompt_for_station4 = technical_spec
        else:
            print(f"❌ Station 3 failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Station 3 error: {e}")
        return
    
    # Test Station 4 - Builder (Code Generation)
    print("\n🚀 STATION 4 - BUILDER (Code Generation)")
    print("-" * 50)
    
    station4_payload = {
        "optimized_prompt": prompt_for_station4
    }
    
    try:
        response = requests.post(f"{base_url}/generate_code", json=station4_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: SUCCESS")
            print(f"🔧 Generated Type: {result['type']}")
            print(f"📏 Code Length: {len(result['code'])} characters")
            print(f"📝 Code Preview:")
            print(result['code'][:500] + "..." if len(result['code']) > 500 else result['code'])
            
            if 'deployment' in result:
                print(f"\n🚀 Deployment Instructions Preview:")
                print(result['deployment'][:300] + "..." if len(result['deployment']) > 300 else result['deployment'])
                
        else:
            print(f"❌ Station 4 failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Station 4 error: {e}")
        return
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 AGENT FACTORY ASSEMBLY LINE COMPLETE!")
    print("=" * 60)
    print("✅ Station 1: Vague idea → Clear requirements")
    print("✅ Station 2: Requirements → Feasibility analysis")  
    print("✅ Station 3: Analysis → Technical specification")
    print("✅ Station 4: Specification → Production code")
    print("\n🏭 The Agent Factory successfully transformed a vague idea")
    print("   into production-ready automation code!")

if __name__ == "__main__":
    main()
