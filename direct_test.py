#!/usr/bin/env python3
"""
Direct test of the FastAPI functionality without network calls
"""
import sys
import os
sys.path.insert(0, '/workspaces/heph')

# Test direct import and function call
try:
    from agents.main_service import mock_refine_prompt
    import asyncio
    
    # Test the mock function directly
    async def test():
        result = await mock_refine_prompt("I need a bot for GitHub.")
        print("✅ Mock function works!")
        print(f"Input: 'I need a bot for GitHub.'")
        print(f"Output: {result}")
        
        # Test with different input
        result2 = await mock_refine_prompt("I want to automate my workflow.")
        print(f"\n✅ Second test:")
        print(f"Input: 'I want to automate my workflow.'")
        print(f"Output: {result2}")
    
    asyncio.run(test())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
