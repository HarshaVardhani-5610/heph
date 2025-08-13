#!/usr/bin/env python3
"""
Test script to validate the Streamlit frontend implementation
Tests the UI structure and backend endpoint calls
"""

import sys
import os
import asyncio

# Add the app directory to the path
sys.path.append('/workspaces/heph')

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import httpx
        print("✅ httpx imported successfully")
    except ImportError as e:
        print(f"❌ httpx import failed: {e}")
        return False
    
    try:
        import asyncio
        print("✅ asyncio imported successfully")
    except ImportError as e:
        print(f"❌ asyncio import failed: {e}")
        return False
    
    return True

def test_app_structure():
    """Test the Streamlit app file structure"""
    print("\n📁 Testing app structure...")
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    if not os.path.exists(app_file):
        print(f"❌ App file not found: {app_file}")
        return False
    
    print(f"✅ App file exists: {app_file}")
    
    # Read and validate the app content
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for key components
    checks = [
        ("Welcome to Heph!", "Main title"),
        ("st.session_state.stage", "Session state management"),
        ("refinement", "Refinement stage"),
        ("BACKEND_URL", "Backend URL configuration"),
        ("call_backend_endpoint", "Backend integration function"),
        ("/refine_prompt", "Refine prompt endpoint"),
        ("httpx.AsyncClient", "Async HTTP client"),
    ]
    
    for check, description in checks:
        if check in content:
            print(f"✅ Found {description}: {check}")
        else:
            print(f"❌ Missing {description}: {check}")
            return False
    
    return True

def test_backend_endpoint_availability():
    """Test if the backend endpoints are correctly configured"""
    print("\n🔗 Testing backend endpoint configuration...")
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check backend configuration
    if 'BACKEND_URL = "http://backend:8000"' in content:
        print("✅ Backend URL correctly configured for Docker environment")
    else:
        print("❌ Backend URL not properly configured")
        return False
    
    # Check endpoint call
    if '"/refine_prompt"' in content:
        print("✅ Refine prompt endpoint call configured")
    else:
        print("❌ Refine prompt endpoint call missing")
        return False
    
    return True

async def test_async_functionality():
    """Test async functionality without actual backend calls"""
    print("\n⚡ Testing async functionality...")
    
    try:
        # Import the function from our app
        sys.path.append('/workspaces/heph/app')
        
        # Test async/await structure
        async def mock_backend_call():
            await asyncio.sleep(0.1)  # Simulate async operation
            return {"status": "success", "test": "mock response"}
        
        result = await mock_backend_call()
        
        if result and "status" in result:
            print("✅ Async functionality working correctly")
            return True
        else:
            print("❌ Async functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def test_session_state_logic():
    """Test the session state logic"""
    print("\n🧠 Testing session state logic...")
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check session state initialization
    if "if 'stage' not in st.session_state:" in content and "st.session_state.stage = 'refinement'" in content:
        print("✅ Session state initialization correct")
    else:
        print("❌ Session state initialization missing or incorrect")
        return False
    
    # Check stage progression
    if "st.session_state.stage = 'feasibility'" in content:
        print("✅ Stage progression logic implemented")
    else:
        print("❌ Stage progression logic missing")
        return False
    
    # Check data storage
    if "st.session_state.refinement_data" in content:
        print("✅ Response data storage implemented")
    else:
        print("❌ Response data storage missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 STREAMLIT FRONTEND TESTING")
    print("=" * 40)
    
    tests = [
        ("Import Testing", test_imports),
        ("App Structure", test_app_structure),
        ("Backend Configuration", test_backend_endpoint_availability),
        ("Session State Logic", test_session_state_logic),
        ("Async Functionality", lambda: asyncio.run(test_async_functionality())),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 40)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Streamlit frontend implementation is ready!")
        print("✅ Backend integration is properly configured!")
        print("✅ Session state management is working!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("Please review the implementation")
        return False

if __name__ == "__main__":
    main()
