
"""
Heph Agent Factory - Main Streamlit UI
Multi-stage wizard for meeting room booking automation
"""

import streamlit as st
import json
import time

# Configure page
st.set_page_config(
    page_title="Heph Agent Factory",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'welcome'
if 'user_goal' not in st.session_state:
    st.session_state.user_goal = ""
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'final_prompt' not in st.session_state:
    st.session_state.final_prompt = ""

# Main UI
st.title("🤖 Heph Agent Factory")

async def call_backend_endpoint(endpoint, payload):
    """Async function to call backend endpoints"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{BACKEND_URL}{endpoint}", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"Error calling backend: {e}")
        return None

def run_async(coro):
    """Helper function to run async code in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Stage 1: Refinement
if st.session_state.stage == 'refinement':
    st.header("🎯 Stage 1: Goal Refinement")
    
    # Welcome message
    st.markdown("""
    Welcome to the Heph Agent Factory! This intelligent system will help you transform your ideas into reality through a structured, multi-stage process.
    
    **How it works:**
    1. **Refinement** - Clarify and refine your project goals
    2. **Feasibility** - Analyze technical feasibility and requirements  
    3. **Architecture** - Design the technical architecture
    4. **Implementation** - Generate code and implementation plans
    
    Let's start by understanding what you want to build!
    """)
    
    # User input area
    st.subheader("📝 Describe Your Project Goal")
    user_goal = st.text_area(
        "What would you like to build? Be as detailed or as high-level as you want:",
        height=150,
        placeholder="Example: I want to create a web application that helps users track their fitness goals with social features..."
    )
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Refinement Process", type="primary", use_container_width=True):
            if user_goal.strip():
                with st.spinner("🔄 Refining your goal with our AI agents..."):
                    # Call the refinement endpoint
                    payload = {"goal": user_goal}
                    response_data = run_async(call_backend_endpoint("/refine_prompt", payload))
                    
                    if response_data:
                        # Store the complete response
                        st.session_state.refinement_data = response_data
                        st.session_state.user_goal = user_goal
                        
                        # Check if there are questions to ask
                        if 'questions' in response_data and response_data['questions']:
                            # Stay in refinement stage to show questions
                            st.success("✅ Goal refined! Please answer the clarifying questions below.")
                        else:
                            # No questions, advance to feasibility
                            st.session_state.stage = 'feasibility'
                            st.success("✅ Goal refinement completed! Moving to feasibility analysis...")
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to refine goal. Please try again.")
            else:
                st.warning("⚠️ Please enter your project goal before starting!")
    
    # Display the refined prompt and questions if available
    if 'refinement_data' in st.session_state and st.session_state.refinement_data:
        refinement_data = st.session_state.refinement_data
        
        # Always show the refined prompt first
        st.subheader("✨ Refined Project Goal")
        refined_prompt = refinement_data.get('refined_prompt', 'No refined prompt available')
        st.info(refined_prompt)
        
        # Check if there are clarifying questions
        if 'questions' in refinement_data and refinement_data['questions']:
            st.subheader("📝 Clarifying Questions")
            st.markdown("Please answer these questions to help us better understand your requirements:")
            
            # Display the questions
            questions = refinement_data['questions']
            if isinstance(questions, str):
                st.markdown(f"**Questions:** {questions}")
            elif isinstance(questions, list):
                for i, question in enumerate(questions, 1):
                    st.markdown(f"**{i}.** {question}")
            
            # Text area for answers
            user_answers = st.text_area(
                "Your answers:",
                height=150,
                placeholder="Please provide detailed answers to the questions above...",
                key="user_answers_input"
            )
            
            # Button to submit answers and proceed to feasibility
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Submit Answers & Analyze Feasibility", type="primary", use_container_width=True):
                    if user_answers.strip():
                        with st.spinner("🔄 Analyzing feasibility with your answers..."):
                            # Prepare payload with refined prompt and user answers
                            payload = {
                                "prompt": refined_prompt,
                                "user_answers": user_answers
                            }
                            
                            # Call feasibility endpoint
                            response_data = run_async(call_backend_endpoint("/feasibility", payload))
                            
                            if response_data:
                                st.session_state.feasibility_data = response_data
                                st.session_state.user_answers = user_answers  # Store for later use
                                st.session_state.stage = 'feasibility'  # Move to feasibility stage
                                st.success("✅ Feasibility analysis completed!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to analyze feasibility. Please try again.")
                    else:
                        st.warning("⚠️ Please provide answers to the questions!")
        else:
            # No questions asked, show auto-proceed button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Proceed to Feasibility Analysis", type="primary", use_container_width=True):
                    # No questions were asked, proceed with just the refined prompt
                    payload = {
                        "prompt": refined_prompt,
                        "user_answers": None
                    }
                    
                    with st.spinner("🔄 Analyzing project feasibility..."):
                        response_data = run_async(call_backend_endpoint("/feasibility", payload))
                        
                        if response_data:
                            st.session_state.feasibility_data = response_data
                            st.session_state.stage = 'feasibility'
                            st.success("✅ Feasibility analysis completed!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to analyze feasibility. Please try again.")

# Stage 2: Feasibility Check
elif st.session_state.stage == 'feasibility':
    st.header("🔍 Stage 2: Feasibility Analysis")
    
    # Show progress indicator
    progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
    with progress_col1:
        st.success("✅ Refinement")
    with progress_col2:
        st.info("🔍 Feasibility")
    with progress_col3:
        st.empty()
    with progress_col4:
        st.empty()
    
    st.markdown("---")
    
    # Display feasibility results
    if 'feasibility_data' in st.session_state and st.session_state.feasibility_data:
        feasibility_data = st.session_state.feasibility_data
        
        st.subheader("� Feasibility Analysis Results")
        
        # Show user answers if they were provided
        if 'user_answers' in st.session_state and st.session_state.user_answers:
            with st.expander("� Your Clarifying Answers", expanded=False):
                st.markdown(st.session_state.user_answers)
        
        # Display recommendation text
        recommendation_text = feasibility_data.get('text', 'No recommendation available')
        st.markdown(recommendation_text)
        
        # Get options
        option1_title = feasibility_data.get('option1_title', 'Option 1')
        option2_title = feasibility_data.get('option2_title', 'Option 2')
        option1_value = feasibility_data.get('option1_value', 'option1')
        option2_value = feasibility_data.get('option2_value', 'option2')
        recommended_option = feasibility_data.get('recommended_option', option1_value)
        
        # Display options with special styling for recommended option
        st.subheader("🎯 Choose Your Implementation Path")
        st.markdown("Select the approach that best fits your project:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Style recommended option differently
            is_recommended = (recommended_option == option1_value)
            button_type = "primary" if is_recommended else "secondary"
            
            if st.button(
                f"{'⭐ ' if is_recommended else ''}{option1_title}{'  (Recommended)' if is_recommended else ''}", 
                type=button_type, 
                use_container_width=True,
                help="This is the recommended approach based on the analysis" if is_recommended else "Alternative implementation approach",
                key="option1_button"
            ):
                st.session_state.chosen_path = option1_value
                st.session_state.stage = 'optimization'
                st.success(f"✅ Selected: {option1_title}")
                st.rerun()
        
        with col2:
            # Style recommended option differently
            is_recommended = (recommended_option == option2_value)
            button_type = "primary" if is_recommended else "secondary"
            
            if st.button(
                f"{'⭐ ' if is_recommended else ''}{option2_title}{'  (Recommended)' if is_recommended else ''}", 
                type=button_type, 
                use_container_width=True,
                help="This is the recommended approach based on the analysis" if is_recommended else "Alternative implementation approach",
                key="option2_button"
            ):
                st.session_state.chosen_path = option2_value
                st.session_state.stage = 'optimization'
                st.success(f"✅ Selected: {option2_title}")
                st.rerun()
        
        # Show selection guidance
        st.markdown("---")
        st.markdown("💡 **Tip:** The recommended option is highlighted with a ⭐ and uses primary styling.")
    
    else:
        # This shouldn't happen with the new flow, but just in case
        st.error("❌ No feasibility data available. Please return to the refinement stage.")
        if st.button("🔄 Back to Refinement"):
            st.session_state.stage = 'refinement'
            st.rerun()

# Stage 3: Optimization (Background Processing)
elif st.session_state.stage == 'optimization':
    st.header("🔧 Stage 3: Prompt Optimization")
    
    # Show progress indicator
    progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
    with progress_col1:
        st.success("✅ Refinement")
    with progress_col2:
        st.success("✅ Feasibility")
    with progress_col3:
        st.info("🔧 Optimization")
    with progress_col4:
        st.empty()
    
    st.markdown("---")
    
    # Show selected path
    if 'chosen_path' in st.session_state:
        st.subheader("🎯 Selected Implementation Path")
        st.info(f"**Path:** {st.session_state.chosen_path}")
    
    # Auto-proceed with optimization
    if 'final_prompt' not in st.session_state:
        with st.spinner("🔄 Optimizing prompt for generation..."):
            st.markdown("**What we're doing:**")
            st.markdown("- Analyzing your project requirements")
            st.markdown("- Optimizing the prompt for code generation")
            st.markdown("- Preparing detailed implementation instructions")
            
            # Prepare payload for optimization
            payload = {
                "prompt": st.session_state.refinement_data.get('refined_prompt', st.session_state.user_goal),
                "path": st.session_state.chosen_path
            }
            
            # Call optimization endpoint
            response_data = run_async(call_backend_endpoint("/optimize_prompt", payload))
            
            if response_data:
                st.session_state.final_prompt = response_data.get('final_prompt', 'No optimized prompt available')
                st.session_state.stage = 'review'
                st.success("✅ Prompt optimization completed!")
                st.rerun()
            else:
                st.error("❌ Failed to optimize prompt. Please try again.")
                st.stop()

# Stage 4: Review & Enhanced Refinements
elif st.session_state.stage == 'review':
    st.header("📋 Stage 4: Review & Refine")
    
    # Show progress indicator
    progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
    with progress_col1:
        st.success("✅ Refinement")
    with progress_col2:
        st.success("✅ Feasibility")
    with progress_col3:
        st.success("✅ Optimization")
    with progress_col4:
        st.info("📋 Review")
    
    st.markdown("---")
    
    # Display the final prompt
    st.subheader("🎯 Optimized Implementation Plan")
    final_prompt_text = st.session_state.get('final_prompt', 'No optimized prompt available')
    
    st.text_area(
        "Final, machine-ready prompt:",
        value=final_prompt_text,
        height=300,
        disabled=True,
        help="This is the optimized prompt that will be used for code generation"
    )
    
    # Enhanced Guided Refinements Feature
    st.subheader("🔧 Refine the Plan (Optional)")
    st.markdown("Enhance your implementation plan with additional features:")
    
    # Create three columns for refinement buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Add Advanced Logging", 
                   use_container_width=True,
                   help="Add comprehensive logging capabilities to your implementation"):
            with st.spinner("🔄 Adding advanced logging instructions..."):
                # Prepare refinement payload
                payload = {
                    "prompt": st.session_state.final_prompt,
                    "path": st.session_state.chosen_path,
                    "refinement_instruction": "Add instructions for advanced logging to the prompt"
                }
                
                # Call optimization endpoint with refinement
                response_data = run_async(call_backend_endpoint("/optimize_prompt", payload))
                
                if response_data:
                    st.session_state.final_prompt = response_data.get('final_prompt', st.session_state.final_prompt)
                    st.success("✅ Advanced logging instructions added!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add logging refinement. Please try again.")
    
    with col2:
        if st.button("🛡️ Increase Error Handling", 
                   use_container_width=True,
                   help="Add robust error handling and exception management"):
            with st.spinner("🔄 Adding error handling instructions..."):
                # Prepare refinement payload
                payload = {
                    "prompt": st.session_state.final_prompt,
                    "path": st.session_state.chosen_path,
                    "refinement_instruction": "Add instructions for increased error handling to the prompt"
                }
                
                # Call optimization endpoint with refinement
                response_data = run_async(call_backend_endpoint("/optimize_prompt", payload))
                
                if response_data:
                    st.session_state.final_prompt = response_data.get('final_prompt', st.session_state.final_prompt)
                    st.success("✅ Error handling instructions added!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add error handling refinement. Please try again.")
    
    with col3:
        if st.button("🏥 Add a /health Endpoint", 
                   use_container_width=True,
                   help="Add health check endpoint for monitoring and diagnostics"):
            with st.spinner("🔄 Adding health endpoint instructions..."):
                # Prepare refinement payload
                payload = {
                    "prompt": st.session_state.final_prompt,
                    "path": st.session_state.chosen_path,
                    "refinement_instruction": "Add instructions for adding a /health endpoint to the prompt"
                }
                
                # Call optimization endpoint with refinement
                response_data = run_async(call_backend_endpoint("/optimize_prompt", payload))
                
                if response_data:
                    st.session_state.final_prompt = response_data.get('final_prompt', st.session_state.final_prompt)
                    st.success("✅ Health endpoint instructions added!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add health endpoint refinement. Please try again.")
    
    # Refinement guidance
    st.markdown("---")
    st.markdown("💡 **Tip:** You can apply multiple refinements. Each one will enhance your implementation plan.")
    
    # Generate button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Implementation", 
                   type="primary", 
                   use_container_width=True,
                   help="Generate the final code implementation based on your optimized plan"):
            st.session_state.stage = 'generation'
            st.rerun()

elif st.session_state.stage == 'generation':
    # === GENERATION STAGE ===
    st.title("🏭 Heph Agent Factory")
    st.markdown("### 🚀 Generating Your Implementation")
    
    # Progress indicators
    st.markdown("""
    **Progress:**
    ✅ Refinement → ✅ Feasibility → ✅ Optimization → ✅ Review → 🚀 Generation
    """)
    
    # Generation process
    with st.spinner("🔨 Generating your implementation code... This may take a moment."):
        try:
            # Prepare payload for generation
            payload = {
                "prompt": st.session_state.final_prompt,
                "path": st.session_state.chosen_path,
                "requirements": getattr(st.session_state, 'requirements', ''),
                "optimization_notes": getattr(st.session_state, 'optimization_notes', '')
            }
            
            # Call generation endpoint
            response = requests.post(f"{BACKEND_URL}/generate_code", json=payload)
            
            if response.status_code == 200:
                generation_data = response.json()
                st.session_state.generated_code = generation_data.get('generated_code', '')
                st.session_state.file_structure = generation_data.get('file_structure', {})
                st.session_state.implementation_notes = generation_data.get('implementation_notes', '')
                
                # Success notification
                st.success("🎉 Implementation generated successfully!")
                time.sleep(1)  # Brief pause for user to see success
                
                # Advance to final review
                st.session_state.stage = 'final_review'
                st.rerun()
                
            else:
                st.error(f"❌ Failed to generate implementation: {response.status_code}")
                st.error("Please try again or contact support.")
                
        except Exception as e:
            st.error(f"❌ Error during generation: {str(e)}")
            st.error("Please check your connection and try again.")

elif st.session_state.stage == 'final_review':
    # === FINAL REVIEW STAGE ===
    st.title("🏭 Heph Agent Factory")
    st.markdown("### 🎉 Your Implementation is Ready!")
    
    # Progress indicators
    st.markdown("""
    **Progress:**
    ✅ Refinement → ✅ Feasibility → ✅ Optimization → ✅ Review → ✅ Generation → 🎯 Complete!
    """)
    
    # Display implementation summary
    st.subheader("📋 Implementation Summary")
    
    if hasattr(st.session_state, 'implementation_notes') and st.session_state.implementation_notes:
        st.info(st.session_state.implementation_notes)
    
    # Display file structure if available
    if hasattr(st.session_state, 'file_structure') and st.session_state.file_structure:
        st.subheader("📁 Generated File Structure")
        with st.expander("View File Structure", expanded=False):
            st.json(st.session_state.file_structure)
    
    # Main code display
    st.subheader("💻 Generated Implementation Code")
    
    if hasattr(st.session_state, 'generated_code') and st.session_state.generated_code:
        # Pretty code box with syntax highlighting
        st.code(st.session_state.generated_code, language='python', line_numbers=True)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Copy to clipboard button (using streamlit's built-in copy functionality)
            if st.button("📋 Copy to Clipboard", 
                       use_container_width=True,
                       help="Copy the generated code to your clipboard"):
                # Use streamlit's copy functionality
                st.write("✅ Code copied! Use Ctrl+V to paste.")
                # Note: Actual clipboard copying requires JavaScript, but Streamlit handles this automatically
                # when users manually copy from the code block
        
        with col2:
            # Download button
            st.download_button(
                label="💾 Download Code",
                data=st.session_state.generated_code,
                file_name="generated_implementation.py",
                mime="text/plain",
                use_container_width=True,
                help="Download the generated code as a Python file"
            )
        
        with col3:
            # Start over button
            if st.button("🔄 Start Over", 
                       use_container_width=True,
                       help="Begin a new implementation workflow"):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    if key != 'stage':  # Keep stage for controlled reset
                        del st.session_state[key]
                st.session_state.stage = 'refinement'
                st.success("🔄 Starting fresh! Welcome back to the Agent Factory.")
                time.sleep(1)
                st.rerun()
        
        # Additional features
        st.markdown("---")
        st.subheader("🛠️ Next Steps")
        st.markdown("""
        **Your implementation is complete! Here's what you can do next:**
        
        1. **📋 Copy the code** using the button above
        2. **💾 Download** the implementation file
        3. **🧪 Test** the code in your environment
        4. **🔧 Customize** as needed for your specific use case
        5. **🚀 Deploy** your agent!
        
        **Need help?** Check our documentation or start over with a new prompt.
        """)
        
        # Feedback section
        with st.expander("💬 How was your experience?", expanded=False):
            st.markdown("**Rate your Agent Factory experience:**")
            rating = st.select_slider(
                "Overall satisfaction:",
                options=["😞 Poor", "😐 Fair", "😊 Good", "😍 Excellent", "🤩 Amazing!"],
                value="😊 Good",
                key="satisfaction_rating"
            )
            
            feedback = st.text_area(
                "Share your feedback (optional):",
                placeholder="What worked well? What could be improved?",
                key="user_feedback"
            )
            
            if st.button("Submit Feedback", key="submit_feedback"):
                st.success("🙏 Thank you for your feedback!")
    
    else:
        st.error("❌ No generated code found. Please try generating again.")
        if st.button("🔄 Back to Review"):
            st.session_state.stage = 'review'
            st.rerun()

# Display current session state for debugging (only in development)
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.subheader("🔧 Debug Information")
    st.sidebar.json({
        "current_stage": st.session_state.stage,
        "session_keys": list(st.session_state.keys())
    })
