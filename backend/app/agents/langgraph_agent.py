"""
LangGraph agent that powers the AI Complaint Intake Assistant.

Graph shape (see build_intake_graph):

    START -> extract -> completeness -> risk -> summary -> root_cause_capa -> END

Each node calls Groq with a focused prompt and merges its output into the shared
state. gemma2-9b-it (fast/cheap) is used for the more mechanical steps
(extraction, completeness). llama-3.3-70b-versatile (stronger reasoning) is used
for risk classification, summarization and root-cause/CAPA suggestions, per the
assignment's "you may also consider llama-3.3-70b-versatile for context" note.

Duplicate detection is intentionally NOT an LLM node - it's a deterministic
lookup against the DB (see agents/tools.py) run by the router after the graph
finishes, since it needs a DB session that isn't part of the LLM state.
"""
import json
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END

from app.config import get_settings
from app.services.groq_client import chat_completion, chat_completion_json
from app.agents import prompts

settings = get_settings()

REQUIRED_FIELDS = [
    "complaint_source", "customer_name", "product_name", "product_strength",
    "batch_number", "manufacturing_date", "expiry_date", "quantity_affected",
    "complaint_type", "complaint_date", "complaint_description",
    "initial_severity", "priority",
]


class IntakeState(TypedDict, total=False):
    raw_text: str
    fields: dict
    completeness_score: int
    missing_fields: list
    completeness_notes: str
    risk_classification: str
    risk_rationale: str
    ai_summary: str
    root_cause_suggestion: str
    capa_recommendation: str
    progress_log: list


def _log(state: IntakeState, message: str) -> None:
    state.setdefault("progress_log", []).append(message)


def node_extract(state: IntakeState) -> IntakeState:
    _log(state, "Analyzing document content and extracting key details...")
    messages = [
        {"role": "system", "content": prompts.EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": state["raw_text"][:12000]},
    ]
    fields = chat_completion_json(messages, model=settings.groq_extraction_model)
    clean = {k: fields.get(k, "") for k in REQUIRED_FIELDS}
    state["fields"] = clean
    _log(state, "Field extraction complete.")
    return state


def node_completeness(state: IntakeState) -> IntakeState:
    _log(state, "Checking record completeness against QMS intake requirements...")
    messages = [
        {"role": "system", "content": prompts.COMPLETENESS_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(state["fields"])},
    ]
    result = chat_completion_json(messages, model=settings.groq_extraction_model)
    state["completeness_score"] = result.get("completeness_score", 0)
    state["missing_fields"] = result.get("missing_fields", [])
    state["completeness_notes"] = result.get("notes", "")
    return state


def node_risk(state: IntakeState) -> IntakeState:
    _log(state, "Running AI risk classification...")
    messages = [
        {"role": "system", "content": prompts.RISK_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(state["fields"])},
    ]
    result = chat_completion_json(messages, model=settings.groq_reasoning_model)
    state["risk_classification"] = result.get("risk_classification", "")
    state["risk_rationale"] = result.get("risk_rationale", "")
    return state


def node_summary(state: IntakeState) -> IntakeState:
    _log(state, "Generating complaint summary...")
    messages = [
        {"role": "system", "content": prompts.SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(state["fields"])},
    ]
    text = chat_completion(messages, model=settings.groq_reasoning_model, json_mode=False)
    state["ai_summary"] = text.strip()
    return state


def node_root_cause_capa(state: IntakeState) -> IntakeState:
    _log(state, "Drafting root cause hypotheses and CAPA recommendation...")
    messages = [
        {"role": "system", "content": prompts.ROOT_CAUSE_CAPA_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(state["fields"])},
    ]
    result = chat_completion_json(messages, model=settings.groq_reasoning_model)
    state["root_cause_suggestion"] = result.get("root_cause_suggestion", "")
    state["capa_recommendation"] = result.get("capa_recommendation", "")
    _log(state, "Analysis complete.")
    return state


_graph = None


def build_intake_graph():
    global _graph
    if _graph is not None:
        return _graph

    builder = StateGraph(IntakeState)
    builder.add_node("extract", node_extract)
    builder.add_node("completeness", node_completeness)
    builder.add_node("risk", node_risk)
    builder.add_node("summary", node_summary)
    builder.add_node("root_cause_capa", node_root_cause_capa)

    builder.add_edge(START, "extract")
    builder.add_edge("extract", "completeness")
    builder.add_edge("completeness", "risk")
    builder.add_edge("risk", "summary")
    builder.add_edge("summary", "root_cause_capa")
    builder.add_edge("root_cause_capa", END)

    _graph = builder.compile()
    return _graph


def run_intake_pipeline(raw_text: str) -> IntakeState:
    graph = build_intake_graph()
    initial_state: IntakeState = {"raw_text": raw_text, "progress_log": []}
    final_state = graph.invoke(initial_state)
    return final_state


def run_chat_turn(user_message: str, current_fields: Optional[dict]) -> dict:
    """Single-turn conversational node used by the 'Ask me anything about this
    complaint' box. Not part of the intake StateGraph since it's reactive/ad-hoc
    rather than a fixed pipeline, but reuses the same Groq client + JSON contract
    style as the graph nodes."""
    context = json.dumps(current_fields or {}, indent=2)
    messages = [
        {"role": "system", "content": prompts.CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Current complaint form fields:\n{context}\n\nAnalyst message:\n{user_message}"},
    ]
    result = chat_completion_json(messages, model=settings.groq_reasoning_model)
    if not result:
        result = {"reply": "Sorry, I couldn't process that just now. Could you rephrase?", "field_updates": {}}
    result.setdefault("field_updates", {})
    return result
