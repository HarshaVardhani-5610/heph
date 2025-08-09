
import streamlit as st
import requests

st.title("The Agent Factory")

# Initialize session state
if 'stage' not in st.session_state:
	st.session_state.stage = 'refinement'

if st.session_state.stage == 'refinement':

	st.subheader("Stage 1: Prompt Refinement")
	goal = st.text_area("Describe your goal:", key="goal_input")
	if st.button("Refine Prompt"):
		if goal.strip():
			try:
				response = requests.post(
					"http://localhost:8000/refine_prompt",
					json={"goal": goal}
				)
				response.raise_for_status()
				data = response.json()
				st.session_state.refined_prompt = data.get("refined_prompt")
				st.session_state.stage = 'feasibility'
				st.rerun()
			except Exception as e:
				st.error(f"Error refining prompt: {e}")
		else:
			st.warning("Please enter a goal before refining.")

# Stage 2: Feasibility & Tooling
elif st.session_state.stage == 'feasibility':
	st.subheader("Stage 2: Feasibility & Tooling")
	st.info(st.session_state.refined_prompt)

	if 'recommendation' not in st.session_state:
		with st.spinner("Analyzing feasibility and tooling..."):
			try:
				response = requests.post(
					"http://localhost:8000/feasibility",
					json={"prompt": st.session_state.refined_prompt}
				)
				response.raise_for_status()
				st.session_state.recommendation = response.json()
			except Exception as e:
				st.error(f"Error fetching recommendation: {e}")
				st.stop()

	rec = st.session_state.recommendation
	st.write(rec.get('text', ''))

	col1, col2 = st.columns(2)
	with col1:
		if st.button(rec.get('option1_title', 'Option 1')):
			st.session_state.chosen_path = rec.get('option1_value')
			st.session_state.stage = 'optimization'
			st.rerun()
	with col2:
		if st.button(rec.get('option2_title', 'Option 2')):
			st.session_state.chosen_path = rec.get('option2_value')
			st.session_state.stage = 'optimization'
			st.rerun()

# Stage 3: Prompt Optimization (Background)
elif st.session_state.stage == 'optimization':
	with st.spinner("Optimizing prompt for generation..."):
		try:
			response = requests.post(
				"http://localhost:8000/optimize_prompt",
				json={
					"prompt": st.session_state.refined_prompt,
					"path": st.session_state.chosen_path
				}
			)
			response.raise_for_status()
			data = response.json()
			st.session_state.final_prompt = data.get("final_prompt")
			st.session_state.stage = 'review'
			st.rerun()
		except Exception as e:
			st.error(f"Error optimizing prompt: {e}")
			st.stop()

# Stage 4: Review & Generation
elif st.session_state.stage == 'review':
	st.subheader("Stage 4: Review & Generation")
	st.text_area(
		"Final, machine-ready prompt:",
		value=st.session_state.final_prompt or "",
		height=300,
		disabled=True
	)
	if st.button("Generate Automation", type="primary"):
		st.session_state.stage = 'generation'
		st.rerun()

# Stage 5: Code Review & Human-in-the-Loop
elif st.session_state.stage == 'generation':
	with st.spinner('Your agent is being generated... Please wait.'):
		try:
			response = requests.post(
				"http://localhost:8000/generate_code",
				json={"prompt": st.session_state.final_prompt}
			)
			response.raise_for_status()
			st.session_state.generated_code = response.json()
			st.session_state.stage = 'final_review'
			st.rerun()
		except Exception as e:
			st.error(f"Error generating code: {e}")
			st.stop()

elif st.session_state.stage == 'final_review':
	st.subheader("Stage 5: Code Review & Approval")
	st.success("Your agent has been generated! Please review the code below.")
	code = st.session_state.generated_code.get('code', '') if 'generated_code' in st.session_state else ''
	st.code(code, language='python')
	if st.button("Start Over"):
		st.session_state.stage = 'refinement'
		st.rerun()
