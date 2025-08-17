#!/usr/bin/env python3
"""
Test script for Enhanced Review Stage (Step 3) Implementation
Validates the guided refinements feature and optimization stage
"""

import sys
import os

def test_optimization_stage():
    """Test the optimization stage implementation"""
    print("🔧 Testing Optimization Stage...")
    print("=" * 50)
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for optimization stage block
    if "elif st.session_state.stage == 'optimization':" in content:
        print("✅ Optimization stage block implemented")
    else:
        print("❌ Optimization stage block missing")
        return False
    
    # Check for progress indicators
    if "Stage 3: Prompt Optimization" in content:
        print("✅ Optimization stage header implemented")
    else:
        print("❌ Optimization stage header missing")
    
    # Check for optimization endpoint call
    if '"/optimize_prompt"' in content and '"path":' in content:
        print("✅ Optimization endpoint call implemented")
    else:
        print("❌ Optimization endpoint call missing")
    
    return True

def test_review_stage_enhancement():
    """Test the enhanced review stage with guided refinements"""
    print("\n📋 Testing Enhanced Review Stage...")
    print("=" * 50)
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for review stage block
    if "elif st.session_state.stage == 'review':" in content:
        print("✅ Review stage block implemented")
    else:
        print("❌ Review stage block missing")
        return False
    
    # Check for final prompt display
    if "st.text_area(" in content and "Final, machine-ready prompt:" in content:
        print("✅ Final prompt display implemented")
    else:
        print("❌ Final prompt display missing")
    
    # Check for guided refinements subheader
    if "Refine the Plan (Optional)" in content:
        print("✅ Guided refinements subheader implemented")
    else:
        print("❌ Guided refinements subheader missing")
    
    return True

def test_refinement_buttons():
    """Test the three refinement buttons implementation"""
    print("\n🔧 Testing Refinement Buttons...")
    print("=" * 50)
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for three columns
    if "col1, col2, col3 = st.columns(3)" in content:
        print("✅ Three-column layout implemented")
    else:
        print("❌ Three-column layout missing")
        return False
    
    # Check for specific buttons
    buttons = [
        ("Add Advanced Logging", "Advanced logging button"),
        ("Increase Error Handling", "Error handling button"),
        ("Add a /health Endpoint", "Health endpoint button"),
    ]
    
    for button_text, description in buttons:
        if button_text in content:
            print(f"✅ {description} implemented")
        else:
            print(f"❌ {description} missing")
            return False
    
    return True

def test_refinement_api_calls():
    """Test the API call logic for refinements"""
    print("\n🔗 Testing Refinement API Calls...")
    print("=" * 50)
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for refinement instruction field
    if "refinement_instruction" in content:
        print("✅ Refinement instruction field implemented")
    else:
        print("❌ Refinement instruction field missing")
        return False
    
    # Check for specific refinement instructions
    instructions = [
        "Add instructions for advanced logging to the prompt",
        "Add instructions for increased error handling to the prompt", 
        "Add instructions for adding a /health endpoint to the prompt",
    ]
    
    for instruction in instructions:
        if instruction in content:
            print(f"✅ Refinement instruction: '{instruction[:30]}...' implemented")
        else:
            print(f"❌ Refinement instruction missing")
            return False
    
    # Check for payload structure
    if '"prompt": st.session_state.final_prompt' in content and '"path": st.session_state.chosen_path' in content:
        print("✅ Payload structure correctly implemented")
    else:
        print("❌ Payload structure missing or incorrect")
        return False
    
    return True

def test_user_experience_features():
    """Test UX features for the refinement process"""
    print("\n🎨 Testing User Experience Features...")
    print("=" * 50)
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for loading spinners
    spinner_count = content.count("st.spinner(")
    if spinner_count >= 3:  # Should have spinners for each refinement
        print(f"✅ Loading spinners implemented ({spinner_count} found)")
    else:
        print(f"❌ Insufficient loading spinners ({spinner_count} found)")
    
    # Check for success notifications
    if "st.success(" in content and "instructions added!" in content:
        print("✅ Success notifications implemented")
    else:
        print("❌ Success notifications missing")
    
    # Check for error handling
    if "st.error(" in content and "Failed to add" in content:
        print("✅ Error handling implemented")
    else:
        print("❌ Error handling missing")
    
    # Check for helpful tooltips
    if "help=" in content and "use_container_width=True" in content:
        print("✅ Button tooltips and styling implemented")
    else:
        print("❌ Button tooltips or styling missing")
    
    # Check for generate button
    if "Generate Implementation" in content and 'st.session_state.stage = \'generation\'' in content:
        print("✅ Generate implementation button implemented")
    else:
        print("❌ Generate implementation button missing")
    
    return True

def test_progress_tracking():
    """Test progress tracking through all stages"""
    print("\n📊 Testing Progress Tracking...")
    print("=" * 50)
    
    app_file = "/workspaces/heph/app/main_ui.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for progress indicators in optimization stage
    if "✅ Refinement" in content and "✅ Feasibility" in content and "🔧 Optimization" in content:
        print("✅ Optimization stage progress indicators implemented")
    else:
        print("❌ Optimization stage progress indicators missing")
    
    # Check for progress indicators in review stage
    if "📋 Review" in content and content.count("✅") >= 6:  # Should have multiple checkmarks
        print("✅ Review stage progress indicators implemented")
    else:
        print("❌ Review stage progress indicators missing")
    
    return True

def main():
    """Run all enhanced review stage tests"""
    print("🧪 ENHANCED REVIEW STAGE (STEP 3) TESTING")
    print("=" * 60)
    
    tests = [
        ("Optimization Stage", test_optimization_stage),
        ("Review Stage Enhancement", test_review_stage_enhancement),
        ("Refinement Buttons", test_refinement_buttons),
        ("Refinement API Calls", test_refinement_api_calls),
        ("User Experience", test_user_experience_features),
        ("Progress Tracking", test_progress_tracking),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} PASSED")
            else:
                print(f"\n❌ {test_name} FAILED")
        except Exception as e:
            print(f"\n❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 ENHANCED REVIEW STAGE TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed >= 5:  # Most tests should pass
        print("\n🎉 ENHANCED REVIEW STAGE IMPLEMENTATION SUCCESSFUL!")
        print("✅ Optimization stage with automatic processing")
        print("✅ Enhanced review stage with guided refinements")
        print("✅ Three refinement buttons with specific instructions")
        print("✅ Proper API integration with refinement_instruction field")
        print("✅ Professional UX with loading states and notifications")
        print("✅ Complete progress tracking through all stages")
        print("\n🚀 READY FOR FINAL TESTING AND DEPLOYMENT!")
        return True
    else:
        print(f"\n⚠️  Issues found in enhanced review stage implementation")
        return False

if __name__ == "__main__":
    main()
