# PROJECT CONTEXT: The Agent Factory

## 1. Overall Goal
Our objective is to build a 5-stage Streamlit web application that serves as a user interface for an AI agent generation system. The backend is a FastAPI service (built by Archon) running on `http://localhost:8000`. This Streamlit app will orchestrate calls to the backend and manage the user's journey from an idea to generated code.

## 2. The 5-Stage User Journey & State Management
The application flow is a series of sequential stages. We will use Streamlit's `st.session_state` to manage the data flow between stages.

- **Stage 1: Prompt Refinement:** User enters a vague goal. We call the `/refine_prompt` endpoint. The state transitions from `goal` to `refined_prompt`.
- **Stage 2: Feasibility & Tooling:** The app shows the refined prompt. We call the `/feasibility` endpoint. The user makes a choice, which is stored as `chosen_path`.
- **Stage 3: Prompt Optimization (Background):** After user choice in Stage 2, we call `/optimize_prompt` in the background. The result is stored as `final_prompt`.
- **Stage 4: Review & Generation:** The app shows the final, machine-ready prompt. User clicks "Generate".
- **Stage 5: Code Review:** The app calls `/generate_code` and displays the output for final approval.

## 3. Agent Endpoints (Backend Service)
- `POST /refine_prompt`: Takes `{"goal": "..."}`. Returns `{"refined_prompt": "..."}` or `{"questions": [...]}`.
- `POST /feasibility`: Takes `{"prompt": "..."}`. Returns `{"recommendation": "..."}`.
- `POST /optimize_prompt`: Takes `{"prompt": "...", "path": "..."}`. Returns `{"final_prompt": "..."}`.
- `POST /generate_code`: Takes `{"prompt": "..."}`. Returns `{"code": "..."}`.
