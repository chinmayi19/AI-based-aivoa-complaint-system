"""
Thin wrapper around the Groq chat-completions API.

Two models are used across the LangGraph agent (see app/agents/langgraph_agent.py):
- GROQ_EXTRACTION_MODEL (gemma2-9b-it)  -> fast, cheap, used for structured field
  extraction and completeness checks.
- GROQ_REASONING_MODEL (llama-3.3-70b-versatile) -> used for the heavier reasoning
  steps: risk classification, root-cause suggestion, CAPA recommendation, summary.
"""
import json
import logging
from groq import Groq
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def chat_completion(messages: list[dict], model: str, json_mode: bool = False, temperature: float = 0.2) -> str:
    """Call Groq chat completions and return the raw text content."""
    client = get_client()
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(**kwargs)
    return completion.choices[0].message.content


def chat_completion_json(messages: list[dict], model: str, temperature: float = 0.1) -> dict:
    """Call Groq expecting a strict JSON object back. Falls back to best-effort
    parsing if the model wraps the JSON in prose/markdown fences."""
    raw = chat_completion(messages, model=model, json_mode=True, temperature=temperature)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Groq response: %s", raw)
            return {}
