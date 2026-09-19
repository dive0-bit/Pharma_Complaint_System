import os
import json
from groq import Groq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Dict

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def process_chat_message(user_message: str):
    system_prompt = """You are an expert AI Copilot for a Pharmaceutical Quality Management System (QMS).
    Extract relevant information from the customer's raw complaint text and output it STRICTLY as a valid JSON object. 
    Do not add any markdown blocks like ```json or ```, just return the raw JSON string.
    
    The JSON must have EXACTLY these keys (leave value as empty string "" if info is missing):
    - "product_name"
    - "batch_number"
    - "originating_site"
    - "impacted_npm"
    - "complaint_category"
    - "product_defect"
    - "complaint_description"
    - "severity" (Analyze and suggest: Minor, Major, or Critical)
    - "suggested_next_action"
    - "initial_risk_assessment"
    """

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_completion_tokens=2048,
        )

        raw_content = completion.choices[0].message.content.strip()

        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        raw_content = raw_content.strip()

        return json.loads(raw_content)

    except Exception as e:
        return {"error": f"Failed to process with Groq: {str(e)}"}


class AgentState(TypedDict):
    user_message: str
    result: Optional[Dict]


def log_complaint_node(state: AgentState) -> AgentState:
    """
    Tool 1: Log Complaint Tool
    Trigger: Jab user pehli baar raw complaint narrative deta hai.
    """
    state["result"] = process_chat_message(state["user_message"])
    return state


def edit_complaint_node(state: AgentState) -> AgentState:
    """
    Tool 2: Edit Complaint Tool
    Trigger: Jab user pehle diye gaye data mein correction/addition karta hai
    (jaise "sorry, batch number galat tha...").
    Same extraction logic use hota hai — sirf naye/corrected fields nikalta hai;
    frontend ka Redux smart-merge purani values preserve karke
    inhe overwrite karta hai.
    """
    state["result"] = process_chat_message(state["user_message"])
    return state


def route_intent(state: AgentState) -> str:
    """
    Simple keyword-based intent router.
    Correction/edit-signalling words milne par 'edit' tool,
    warna default 'log' tool (naya complaint).
    """
    text = state["user_message"].lower()
    edit_signals = [
        "sorry", "correction", "wrong", "actually", "galat",
        "update", "mistake", "not ", "instead", "correct"
    ]
    if any(word in text for word in edit_signals):
        return "edit"
    return "log"

_graph = StateGraph(AgentState)
_graph.add_node("log", log_complaint_node)
_graph.add_node("edit", edit_complaint_node)
_graph.set_conditional_entry_point(
    route_intent,
    {"log": "log", "edit": "edit"}
)
_graph.add_edge("log", END)
_graph.add_edge("edit", END)

complaint_graph = _graph.compile()


def run_agent(user_message: str) -> Dict:
    """
    Backend endpoint isi function ko call karega.
    Yeh LangGraph ke through Log/Edit tool ko route karke
    result return karta hai.
    """
    final_state = complaint_graph.invoke({
        "user_message": user_message,
        "result": None
    })
    return final_state["result"]