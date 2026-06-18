"""
agent.py — AI Agent using Groq (llama-3.3-70b-versatile) that conducts
the patient triage conversation.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from tools import get_followup_questions, classify_urgency, estimate_treatment_and_cost

load_dotenv()

SYSTEM_PROMPT = """You are a compassionate AI health triage assistant.
Your role is NOT to replace a doctor — it is to help patients understand their symptoms,
decide how urgently they need to see one, and know which type of specialist is relevant.

CONVERSATION FLOW:
1. When a patient first describes their symptoms, call get_followup_questions to retrieve
   relevant questions. Ask them ONE question at a time — do not bombard the patient.
   Cover: how long symptoms have lasted, how severe they are, any related symptoms,
   and any relevant medical history.
2. After 3-5 patient replies, you should have enough information.
   Call classify_urgency with a summary of all symptoms and their pain level.
3. Then call estimate_treatment_and_cost to get the likely condition, the relevant
   specialist, treatment options, and costs.
4. Finally, present a clear, kind, easy-to-understand summary to the patient.

FINAL SUMMARY MUST INCLUDE ALL OF THESE PARTS, IN THIS ORDER:
1. Urgency classification (Normal / Urgent / Emergency) and what timeframe to act within
2. The likely condition, explained in simple language
3. Which specialist or doctor type the patient should see (e.g. "You should see a
   General Dentist" or "You should see a Cardiologist"), and whether a routine GP visit
   would be enough first, or whether they need a specialist directly
4. The likely treatment and an estimated cost range (in LKR, and USD if useful)
5. A reassuring but honest closing note

RULES:
- Always be empathetic. Patients may be scared.
- Never give a definitive diagnosis. Use words like "this may be", "it could indicate".
- If pain level is 9 or 10, or you detect emergency symptoms, escalate immediately and
  tell them to go to Emergency / call emergency services rather than book a specialist visit.
- Keep medical terms simple — explain them in plain language.
- Do NOT ask more than 5 follow-up questions total before giving a triage result.
- Always name a specific specialist type (not just "a doctor") once you call
  estimate_treatment_and_cost.

Always end your final summary with:
"⚕️ This is AI-generated guidance only. Please consult a qualified doctor for a proper diagnosis and treatment plan."
"""


def run_agent(user_message: str, chat_history: list, pain_level: int = 5) -> str:
    """
    Run one turn of the triage agent.
    user_message  — what the patient just typed
    chat_history  — full list of prior LangChain messages
    pain_level    — slider value from the UI (1-10)
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )

    tools = [get_followup_questions, classify_urgency, estimate_treatment_and_cost]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    enriched_message = f"{user_message}\n[Patient pain level: {pain_level}/10]"

    messages = chat_history + [{"role": "user", "content": enriched_message}]

    try:
        result = agent.invoke({"messages": messages})
        last_message = result["messages"][-1]
        return last_message.content
    except Exception as e:
        return f"An error occurred: {str(e)}. Please try rephrasing your symptoms."