#!/usr/bin/env python3
"""
Demo of the Perplexity API Key Rotation System Structure
"""
import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_system():
    """Demonstrate the API key system structure"""
    
    print("🔑 PERPLEXITY API KEY ROTATION SYSTEM DEMO")
    print("=" * 60)
    
    # Show environment setup
    print("\n📋 Step 1: Environment Setup")
    print("-" * 30)
    print("The system looks for environment variables:")
    for i in range(1, 11):
        env_var = f"PERPLEXITY_API_KEY_{i}"
        value = os.getenv(env_var)
        if value:
            masked_value = f"****{value[-4:]}" if len(value) > 4 else "****"
            print(f"  ✅ {env_var}: {masked_value}")
        else:
            print(f"  ⚪ {env_var}: (empty)")
    
    # Show configuration structure
    print("\n🔧 Step 2: Configuration Structure")
    print("-" * 30)
    
    config_example = {
        "api_keys": [
            {
                "key_id": "key_1",
                "key_value": "your_api_key_here",
                "is_active": True,
                "error_count": 0,
                "credits_exhausted": False,
                "last_error": None,
                "last_used": None
            }
        ],
        "current_key_index": 0,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    print("Configuration file structure (perplexity_config.json):")
    print(json.dumps(config_example, indent=2))
    
    # Show rotation logic
    print("\n🔄 Step 3: Rotation Logic")
    print("-" * 30)
    print("1. System starts with first available key")
    print("2. On credit exhaustion (HTTP 429):")
    print("   → Mark key as exhausted")
    print("   → Set 24-hour retry cooldown")
    print("   → Immediately switch to next available key")
    print("3. On API errors:")
    print("   → Track error count")
    print("   → Temporary disable after 5 errors")
    print("   → 30-minute cooldown period")
    print("4. Empty slots are gracefully ignored")
    
    # Show usage examples
    print("\n💻 Step 4: Usage Examples")
    print("-" * 30)
    
    usage_examples = [
        "# Basic usage",
        "from api_key_manager import call_perplexity_api",
        "",
        "response = await call_perplexity_api(",
        "    'What is the latest Python version?',",
        "    max_tokens=1000,",
        "    temperature=0.2",
        ")",
        "",
        "# Advanced usage",
        "from api_key_manager import PerplexityAPIManager",
        "",
        "manager = PerplexityAPIManager()",
        "status = manager.get_status()",
        "print(f'Active keys: {status[\"active_keys\"]}')"
    ]
    
    for line in usage_examples:
        print(f"  {line}")
    
    # Show Agent Factory integration
    print("\n🏭 Step 5: Agent Factory Integration")
    print("-" * 30)
    print("All Agent Factory endpoints now use Perplexity API:")
    print("  ✅ /refine_prompt - Real AI prompt refinement")
    print("  ✅ /feasibility - Real AI feasibility analysis")
    print("  ✅ /optimize_prompt - Real AI technical specifications")
    print("  ✅ /generate_code - Real AI code generation")
    print("  ✅ /api-status - Monitor key rotation status")
    
    # Show setup instructions
    print("\n🚀 Step 6: Quick Setup")
    print("-" * 30)
    print("1. Get your Perplexity API keys from: https://perplexity.ai")
    print("2. Set environment variables:")
    print("   export PERPLEXITY_API_KEY_1='your_first_key'")
    print("   export PERPLEXITY_API_KEY_2='your_second_key'")
    print("   # ... up to 10 keys")
    print("3. Run the Agent Factory:")
    print("   cd agents && python main_service.py")
    print("4. Test the system:")
    print("   python test_perplexity_system.py")
    
    print("\n" + "=" * 60)
    print("🎉 PERPLEXITY API ROTATION SYSTEM READY!")
    print("📚 See API_KEY_SYSTEM.md for detailed documentation")
    print("=" * 60)

if __name__ == "__main__":
    demo_system()
