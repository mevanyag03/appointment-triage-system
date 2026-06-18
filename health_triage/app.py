"""
app.py — Main Streamlit UI for the AI Health Triage System.
Run with: streamlit run app.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import run_agent

st.set_page_config(page_title="MediAI Triage", page_icon="🏥", layout="centered")

st.markdown("# 🏥 MediAI Health Triage")
st.markdown("**Describe your symptoms and our AI will guide you on urgency, specialist, and next steps.**")

st.info("⚕️ **Disclaimer:** This tool provides *guidance only* and does not replace a qualified doctor. Always consult a medical professional for diagnosis and treatment.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "lc_history" not in st.session_state:
    st.session_state.lc_history = []
if "pain_level" not in st.session_state:
    st.session_state.pain_level = 5
if "triage_started" not in st.session_state:
    st.session_state.triage_started = False
if "patient_name" not in st.session_state:
    st.session_state.patient_name = ""

if not st.session_state.triage_started:
    st.subheader("📋 Tell us about your symptoms")

    patient_name = st.text_input("Your name (optional)", placeholder="e.g. Kamal")
    age = st.number_input("Your age", min_value=1, max_value=120, value=25)
    symptom_text = st.text_area(
        "Describe your symptoms in your own words *",
        placeholder="e.g. I have a sharp toothache on my lower left side. It started 2 days ago.",
        height=120
    )
    pain_level = st.slider("Pain level (1 = minimal, 10 = worst)", min_value=1, max_value=10, value=5)

    if pain_level <= 3:
        st.success(f"Pain level {pain_level}/10 — Mild")
    elif pain_level <= 6:
        st.warning(f"Pain level {pain_level}/10 — Moderate")
    else:
        st.error(f"Pain level {pain_level}/10 — Severe")

    start_btn = st.button("🔍 Start Triage", type="primary")

    if start_btn:
        if not symptom_text.strip():
            st.error("Please describe your symptoms before continuing.")
        else:
            st.session_state.pain_level = pain_level
            st.session_state.patient_name = patient_name
            st.session_state.triage_started = True

            greeting = f"Hi, I'm {patient_name}. " if patient_name else ""
            first_message = (
                f"{greeting}I am {age} years old. "
                f"My symptoms: {symptom_text} "
                f"My pain level is {pain_level} out of 10."
            )

            st.session_state.messages.append({
                "role": "user",
                "content": f"**Symptoms:** {symptom_text}\n\n**Pain level:** {pain_level}/10"
            })

            with st.spinner("Analysing your symptoms..."):
                response = run_agent(first_message, st.session_state.lc_history, pain_level)

            st.session_state.lc_history.append(HumanMessage(content=first_message))
            st.session_state.lc_history.append(AIMessage(content=response))
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

else:
    name_display = f" — {st.session_state.patient_name}" if st.session_state.patient_name else ""
    pain = st.session_state.pain_level
    pain_color = "🔴" if pain >= 7 else ("🟡" if pain >= 4 else "🟢")
    st.caption(f"Patient{name_display} | Pain level: {pain_color} {pain}/10")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🏥"):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your reply here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner("Thinking..."):
                response = run_agent(user_input, st.session_state.lc_history, st.session_state.pain_level)
            st.markdown(response)

        st.session_state.lc_history.append(HumanMessage(content=user_input))
        st.session_state.lc_history.append(AIMessage(content=response))
        st.session_state.messages.append({"role": "assistant", "content": response})

    with st.sidebar:
        st.markdown("## 🏥 MediAI Triage")
        st.caption("Urgency • Specialist • Cost estimate")
        st.divider()
        st.markdown("### 📊 Session Info")
        if st.session_state.patient_name:
            st.markdown(f"**Patient:** {st.session_state.patient_name}")
        st.markdown(f"**Pain level:** {st.session_state.pain_level}/10")
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")
        st.divider()
        st.markdown("### 🚨 Emergency Numbers")
        st.markdown("- **Sri Lanka:** 1990 (Suwa Seriya)\n- **Police:** 119\n- **Fire:** 110")
        st.divider()
        if st.button("🔄 Start New Triage", use_container_width=True):
            for key in ["messages", "lc_history", "triage_started", "patient_name", "pain_level"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.caption("⚕️ Guidance only. Always consult a qualified doctor.")