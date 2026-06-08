import streamlit as st
import pandas as pd
import os
from triage_logic import assign_priority

st.title("AI-Based Appointment Triage System")
st.write("This system gives appointment numbers based on patient urgency.")

file_name = "patients.csv"

if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
    df = pd.DataFrame(columns=[
        "Name", "Age", "Symptom", "Pain Level", "Fever",
        "Chest Pain", "Breathing Difficulty", "Chronic Disease",
        "Priority", "Urgency"
    ])
    df.to_csv(file_name, index=False)

st.header("Enter Patient Details")

name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=1, max_value=120, step=1)
symptom = st.text_input("Main Symptom")
pain_level = st.slider("Pain Level", 1, 10)

fever = st.selectbox("Fever?", ["No", "Yes"])
chest_pain = st.selectbox("Chest Pain?", ["No", "Yes"])
breathing_difficulty = st.selectbox("Breathing Difficulty?", ["No", "Yes"])
chronic_disease = st.selectbox("Diabetes / Heart Disease?", ["No", "Yes"])

if st.button("Book Appointment"):
    if name.strip() == "" or symptom.strip() == "":
        st.warning("Please enter patient name and symptom.")
    else:
        priority, urgency = assign_priority(
            age, pain_level, fever, chest_pain,
            breathing_difficulty, chronic_disease
        )

        new_patient = pd.DataFrame([{
            "Name": name,
            "Age": age,
            "Symptom": symptom,
            "Pain Level": pain_level,
            "Fever": fever,
            "Chest Pain": chest_pain,
            "Breathing Difficulty": breathing_difficulty,
            "Chronic Disease": chronic_disease,
            "Priority": priority,
            "Urgency": urgency
        }])

        df = pd.read_csv(file_name)
        df = pd.concat([df, new_patient], ignore_index=True)
        df.to_csv(file_name, index=False)

        st.success(f"Appointment booked successfully! Urgency Level: {urgency}")

st.header("Doctor Appointment Queue")

df = pd.read_csv(file_name)

if not df.empty:
    df = df.sort_values(by=["Priority"]).reset_index(drop=True)
    df["Appointment Number"] = df.index + 1

    st.dataframe(df[[
        "Appointment Number", "Name", "Age", "Symptom",
        "Pain Level", "Urgency"
    ]])
else:
    st.info("No appointments yet.")