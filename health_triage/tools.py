"""
tools.py — Agent tools for the health triage system.
These are functions the AI agent calls automatically during conversation.
"""

import json
import os
from langchain.tools import tool

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "symptoms_db.json")


def _load_db() -> dict:
    with open(DB_PATH, "r") as f:
        return json.load(f)


def _find_category(symptom_text: str):
    db = _load_db()
    text_lower = symptom_text.lower()
    for category, data in db.items():
        for keyword in data.get("keywords", []):
            if keyword in text_lower:
                return category, data
    return None, None


@tool
def get_followup_questions(symptom_text: str) -> str:
    """
    Given a patient's initial symptom description, returns a list of
    follow-up questions the AI should ask to better understand the case.
    Use this at the beginning of the conversation.
    """
    category, data = _find_category(symptom_text)
    if not data:
        return (
            "I couldn't match these symptoms to my knowledge base. "
            "Please ask general follow-up questions: How long have you had this? "
            "How severe is it on a scale of 1-10? Any other symptoms? "
            "Any relevant medical history?"
        )
    questions = data.get("follow_up_questions", [])
    return "Ask the patient these follow-up questions one by one:\n" + "\n".join(
        f"- {q}" for q in questions
    )


@tool
def classify_urgency(symptom_summary: str, pain_level: int) -> str:
    """
    Classifies the urgency of a patient's condition based on their symptoms
    and pain level (1-10). Returns urgency level and recommended timeframe
    to see a doctor.
    """
    emergency_keywords = [
        "chest pain", "can't breathe", "cannot breathe", "unconscious",
        "seizure", "stroke", "heart attack", "severe bleeding", "worst headache",
        "thunderclap", "stiff neck with fever", "swelling face", "abscess",
        "above 40", "40 degrees"
    ]
    text_lower = symptom_summary.lower()
    for kw in emergency_keywords:
        if kw in text_lower:
            return json.dumps({
                "urgency": "emergency",
                "urgency_label": "EMERGENCY",
                "see_doctor_within": "Go to emergency / call services IMMEDIATELY",
                "reason": f"Detected high-risk symptom: '{kw}'"
            })

    if pain_level >= 9:
        return json.dumps({
            "urgency": "emergency",
            "urgency_label": "EMERGENCY",
            "see_doctor_within": "Seek immediate medical attention",
            "reason": "Pain level 9-10 is considered a medical emergency."
        })
    elif pain_level >= 7:
        urgency, label, timeframe = "urgent", "URGENT", "See a doctor within 24 hours"
    elif pain_level >= 4:
        urgency, label, timeframe = "urgent", "URGENT", "See a doctor within 2-3 days"
    else:
        urgency, label, timeframe = "normal", "NORMAL", "Schedule an appointment within 1-2 weeks"

    return json.dumps({
        "urgency": urgency,
        "urgency_label": label,
        "see_doctor_within": timeframe,
        "reason": f"Pain level {pain_level}/10 with symptoms: {symptom_summary[:100]}"
    })


@tool
def estimate_treatment_and_cost(symptom_summary: str, pain_level: int) -> str:
    """
    Based on the patient's symptom summary and pain level, returns the most
    likely condition, the relevant specialist to see, treatment options,
    and estimated costs in both LKR and USD.
    """
    db = _load_db()
    text_lower = symptom_summary.lower()

    matched_category = None
    matched_data = None
    for category, data in db.items():
        for keyword in data.get("keywords", []):
            if keyword in text_lower:
                matched_category = category
                matched_data = data
                break
        if matched_category:
            break

    if not matched_data:
        return json.dumps({
            "condition": "Unknown",
            "specialist": "General Practitioner (GP)",
            "treatment": "General consultation recommended",
            "description": "Symptoms did not match our database. Please consult a doctor.",
            "urgency_label": "URGENT" if pain_level >= 5 else "NORMAL",
            "see_doctor_within": "Within 1-3 days" if pain_level >= 5 else "Within 1-2 weeks",
            "cost_range_lkr": "N/A",
            "cost_range_usd": "N/A"
        }, ensure_ascii=False)

    best_match = None
    best_score = -1
    for condition_name, condition_data in matched_data["conditions"].items():
        score = 0
        for trigger in condition_data.get("triggers", []):
            if trigger.lower() in text_lower:
                score += 1
        if pain_level >= 8 and condition_data["urgency"] == "emergency":
            score += 3
        elif pain_level >= 5 and condition_data["urgency"] == "urgent":
            score += 2
        elif pain_level < 5 and condition_data["urgency"] == "normal":
            score += 1

        if score > best_score:
            best_score = score
            best_match = condition_data.copy()
            best_match["condition_name"] = condition_name

    if not best_match:
        best_match = list(matched_data["conditions"].values())[0].copy()
        best_match["condition_name"] = list(matched_data["conditions"].keys())[0]

    return json.dumps({
        "condition": str(best_match.get("condition_name", "Unknown")).replace("_", " ").title(),
        "specialist": str(best_match.get("specialist", "General Practitioner (GP)")),
        "treatment": str(best_match.get("treatment", "Consult a doctor")),
        "description": str(best_match.get("description", "")),
        "urgency_label": str(best_match.get("urgency_label", "Normal")),
        "see_doctor_within": str(best_match.get("see_doctor_within", "As needed")),
        "cost_range_lkr": str(best_match.get("cost_range_lkr", "N/A")),
        "cost_range_usd": str(best_match.get("cost_range_usd", "N/A"))
    }, ensure_ascii=False)