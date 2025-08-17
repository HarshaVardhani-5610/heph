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

# Custom CSS
st.markdown("""
<style>
.glowy-box {
    border: 2px solid #ff4444;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 0 20px rgba(255, 68, 68, 0.3);
    background-color: rgba(255, 255, 255, 0.05);
}

.glowy-green-box {
    border: 2px solid #44ff44;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 0 20px rgba(68, 255, 68, 0.3);
    background-color: rgba(255, 255, 255, 0.05);
}

.stTextArea textarea {
    background-color: #f8f9fa !important;
    color: #2c3e50 !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}

.stTextInput > div > div > input {
    border: 2px solid #ff4444 !important;
    box-shadow: 0 0 10px rgba(255, 68, 68, 0.2) !important;
    border-radius: 8px !important;
}

.stSelectbox > div > div > select {
    border: 2px solid #ff4444 !important;
    box-shadow: 0 0 10px rgba(255, 68, 68, 0.2) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

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

# Stage 1: The Conversational Welcome
if st.session_state.stage == 'welcome':
    st.markdown("---")
    st.subheader("Welcome to Heph! What automations are you trying to build today?")
    
    # User input for their goal
    user_goal = st.text_input(
        "Tell us about your automation goal:",
        placeholder="Example: I want to automate meeting room bookings...",
        key="goal_input_area"
    )
    
    if st.button("🚀 Start", type="primary", disabled=not user_goal.strip()):
        if user_goal.strip():
            st.session_state.user_goal = user_goal
            st.rerun()
    
    # Show clarifying questions if goal is entered
    if st.session_state.user_goal:
        st.markdown("### Great! To help you build this automation, I need a few details:")
        
        st.markdown("**1. What is the email address of the shared office calendar?**")
        answer1 = st.text_input("Calendar email:", key="answer1")
        
        st.markdown("**2. Could you please provide the URL of the Google Sheet for recording bookings?**")
        answer2 = st.text_input("Google Sheet URL:", key="answer2")
        
        st.markdown("**3. For conflict warnings, should I email both people involved?**")
        answer3 = st.selectbox("Email both organizers?", ["Yes", "No"], key="answer3")
        
        if st.button("✅ Continue", key="continue_btn"):
            st.session_state.user_answers = {
                "calendar_email": answer1,
                "sheet_url": answer2,
                "email_both": answer3
            }
            st.session_state.stage = 'feasibility'
            st.rerun()

# Stage 2: The Strategic Recommendation
elif st.session_state.stage == 'feasibility':
    st.markdown("---")
    st.subheader("🎯 Strategic Recommendation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### n8n Workflow")
        st.success("**RECOMMENDED**")
        st.markdown('<div class="glowy-box">', unsafe_allow_html=True)
        st.markdown("""
        Based on your request, an n8n Workflow is the perfect tool. It's designed to connect standard cloud applications like Outlook and Google Sheets reliably and efficiently.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔧 Custom Python Agent")
        st.markdown('<div class="glowy-box">', unsafe_allow_html=True)
        st.markdown("""
        This option is available for tasks requiring complex, custom logic that goes beyond standard API connections.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("✅ Continue with Recommended", type="primary"):
        st.session_state.stage = 'optimization'
        st.rerun()

# Stage 3: The Final Blueprint Review & Edit
elif st.session_state.stage == 'optimization':
    st.markdown("---")
    st.subheader("📋 Final Blueprint Review & Edit")
    
    machine_prompt = """SYSTEM: You are an expert n8n JSON generator. Create a workflow that triggers on a new Outlook Calendar event. The workflow must: 1. Use the 'Google Calendar' node to create an identical event on the calendar `office-calendar@mycompany.com`. 2. Use the 'Google Sheets' node to search for any existing events in the sheet at `https://docs.google.com/spreadsheets/d/123abc...` that overlap with the new event's start and end times. 3. Use an 'If' node to check if the search found any overlapping events. 4. If a conflict exists: Use two 'Email' nodes to send a conflict alert email to both the new event's organizer and the existing event's organizer. 5. If no conflict exists: Use the 'Google Sheets' node to append the new booking details as a new row. Then, use a 'Wait' node to pause the workflow until 30 minutes before the event's start time. After the wait, use an 'Email' node to send a reminder to the event's organizer. The final output must be a single, valid n8n JSON object."""
    
    st.markdown("**Technical Implementation Plan:**")
    
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    
    prompt_text = st.text_area(
        "Machine-optimized prompt:",
        value=machine_prompt,
        height=200,
        disabled=not st.session_state.edit_mode,
        key="prompt_editor"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 Make Changes"):
            st.session_state.edit_mode = True
            st.rerun()
    
    with col2:
        if st.button("✅ Approve & Build", type="primary"):
            st.session_state.final_prompt = prompt_text
            st.session_state.stage = 'generation'
            st.rerun()

# Stage 4: The Final Product Display
elif st.session_state.stage == 'generation':
    st.markdown("---")
    st.subheader("🔄 Building Your Workflow")
    
    with st.spinner('Building your custom workflow...'):
        time.sleep(3)
    
    st.session_state.stage = 'final_review'
    st.rerun()

elif st.session_state.stage == 'final_review':
    st.markdown("---")
    st.subheader("🎉 Your Custom n8n Workflow is Ready!")
    
    final_workflow = {
      "name": "Meeting Room Booking Manager",
      "nodes": [
        {
          "parameters": {},
          "name": "Start",
          "type": "n8n-nodes-base.start",
          "typeVersion": 1,
          "position": [250, 300]
        },
        {
          "parameters": {"calendar": "primary", "authentication": "oAuth2", "options": {}},
          "name": "Outlook Trigger",
          "type": "n8n-nodes-base.microsoftOutlookCalendarTrigger",
          "typeVersion": 1,
          "position": [450, 300],
          "credentials": {"microsoftOutlookCalendarOAuth2Api": {"id": "YOUR_OUTLOOK_CREDENTIAL_ID", "name": "Outlook Account"}}
        }
      ],
      "connections": {
        "Outlook Trigger": {"main": [[{"node": "Add to Shared Calendar", "type": "main", "index": 0}]]}
      }
    }
    
    st.markdown("**Complete n8n Workflow JSON:**")
    st.markdown('<div class="glowy-green-box">', unsafe_allow_html=True)
    workflow_json_str = json.dumps(final_workflow, indent=2)
    st.code(workflow_json_str, language='json')
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copy to Clipboard"):
            st.text_area("Copy this JSON:", value=workflow_json_str, height=100, key="copy_area")
            st.info("👆 Select all text above and copy with Ctrl+C (Cmd+C on Mac)")
    
    with col2:
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                if key.startswith('stage') or key.startswith('user_') or key.startswith('final_'):
                    del st.session_state[key]
            st.session_state.stage = 'welcome'
            st.rerun()
