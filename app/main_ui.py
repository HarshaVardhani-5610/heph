
import streamlit as st
import httpx
import asyncio
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Heph Agent Factory",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🏭 Welcome to Heph!")

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'refinement'

# Backend URL configuration
BACKEND_URL = "http://backend:8000"

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
                        
                        # Advance to next stage
                        st.session_state.stage = 'feasibility'
                        
                        # Show success message
                        st.success("✅ Goal refinement completed! Moving to feasibility analysis...")
                        st.rerun()
                    else:
                        st.error("❌ Failed to refine goal. Please try again.")
            else:
                st.warning("⚠️ Please enter your project goal before starting!")

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
    
    # Display refined prompt or questions from refinement_data
    if 'refinement_data' in st.session_state and st.session_state.refinement_data:
        refinement_data = st.session_state.refinement_data
        
        # Check if there are clarifying questions
        has_questions = 'questions' in refinement_data and refinement_data['questions']
        
        if has_questions:
            st.subheader("📝 Clarifying Questions")
            st.info("Our AI agents have some questions to better understand your project:")
            
            # Display the questions
            questions = refinement_data['questions']
            if isinstance(questions, str):
                st.markdown(f"**Questions:** {questions}")
            elif isinstance(questions, list):
                for i, question in enumerate(questions, 1):
                    st.markdown(f"**{i}.** {question}")
            
            # Text area for answers
            user_answers = st.text_area(
                "Please provide your answers:",
                height=150,
                placeholder="Answer the questions above to help us better understand your requirements..."
            )
            
            # Button to submit answers and proceed
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Submit Answers & Analyze Feasibility", type="primary", use_container_width=True):
                    if user_answers.strip():
                        with st.spinner("🔄 Analyzing feasibility with your answers..."):
                            # Prepare payload with original goal and answers
                            payload = {
                                "prompt": refinement_data.get('refined_prompt', st.session_state.user_goal),
                                "answers": user_answers,
                                "original_goal": st.session_state.user_goal
                            }
                            
                            # Call feasibility endpoint
                            response_data = run_async(call_backend_endpoint("/feasibility", payload))
                            
                            if response_data:
                                st.session_state.feasibility_data = response_data
                                st.success("✅ Feasibility analysis completed!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to analyze feasibility. Please try again.")
                    else:
                        st.warning("⚠️ Please provide answers to the questions!")
        
        else:
            # No questions - show refined prompt and proceed automatically
            st.subheader("✨ Refined Project Goal")
            refined_prompt = refinement_data.get('refined_prompt', 'No refined prompt available')
            st.info(refined_prompt)
            
            # Auto-proceed to feasibility analysis if not already done
            if 'feasibility_data' not in st.session_state:
                with st.spinner("🔄 Analyzing project feasibility..."):
                    payload = {
                        "prompt": refined_prompt,
                        "original_goal": st.session_state.user_goal
                    }
                    
                    response_data = run_async(call_backend_endpoint("/feasibility", payload))
                    
                    if response_data:
                        st.session_state.feasibility_data = response_data
                        st.success("✅ Feasibility analysis completed!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to analyze feasibility. Please try again.")
                        st.stop()
    
    # Display feasibility results if available
    if 'feasibility_data' in st.session_state and st.session_state.feasibility_data:
        feasibility_data = st.session_state.feasibility_data
        
        st.markdown("---")
        st.subheader("📊 Feasibility Analysis Results")
        
        # Display recommendation text
        recommendation_text = feasibility_data.get('text', feasibility_data.get('recommendation', 'No recommendation available'))
        st.markdown(recommendation_text)
        
        # Get options
        option1_title = feasibility_data.get('option1_title', 'Option 1')
        option2_title = feasibility_data.get('option2_title', 'Option 2')
        option1_value = feasibility_data.get('option1_value', 'option1')
        option2_value = feasibility_data.get('option2_value', 'option2')
        recommended_option = feasibility_data.get('recommended_option', 'option1')
        
        # Display options with special styling for recommended option
        st.subheader("🎯 Choose Your Implementation Path")
        st.markdown("Select the approach that best fits your project:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Style recommended option differently
            if recommended_option == option1_value or recommended_option == 'option1':
                if st.button(f"⭐ {option1_title} (Recommended)", 
                           type="primary", 
                           use_container_width=True,
                           help="This is our recommended approach based on the analysis"):
                    st.session_state.chosen_path = option1_value
                    st.session_state.stage = 'optimization'
                    st.success(f"✅ Selected: {option1_title}")
                    st.rerun()
            else:
                if st.button(option1_title, 
                           use_container_width=True,
                           help="Alternative implementation approach"):
                    st.session_state.chosen_path = option1_value
                    st.session_state.stage = 'optimization'
                    st.success(f"✅ Selected: {option1_title}")
                    st.rerun()
        
        with col2:
            # Style recommended option differently
            if recommended_option == option2_value or recommended_option == 'option2':
                if st.button(f"⭐ {option2_title} (Recommended)", 
                           type="primary", 
                           use_container_width=True,
                           help="This is our recommended approach based on the analysis"):
                    st.session_state.chosen_path = option2_value
                    st.session_state.stage = 'optimization'
                    st.success(f"✅ Selected: {option2_title}")
                    st.rerun()
            else:
                if st.button(option2_title, 
                           use_container_width=True,
                           help="Alternative implementation approach"):
                    st.session_state.chosen_path = option2_value
                    st.session_state.stage = 'optimization'
                    st.success(f"✅ Selected: {option2_title}")
                    st.rerun()
        
        # Show selection guidance
        st.markdown("---")
        st.markdown("💡 **Tip:** The recommended option is highlighted with a ⭐ and uses our primary styling.")

# Display current session state for debugging (only in development)
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.subheader("🔧 Debug Information")
    st.sidebar.json({
        "current_stage": st.session_state.stage,
        "session_keys": list(st.session_state.keys())
    })
