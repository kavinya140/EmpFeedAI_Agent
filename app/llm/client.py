"""Groq LLM client with retry logic."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings


def _get_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")
    return Groq(api_key=settings.groq_api_key)


def _extract_json(text: str) -> Any:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        text = fence_match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if brace_match:
            return json.loads(brace_match.group(1))
        raise


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def chat_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    settings = get_settings()
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def analyze_feedback_json(feedback_text: str, department: str = "") -> Dict[str, Any]:
    from app.llm.prompts import FEEDBACK_ANALYST_SYSTEM, build_feedback_analysis_prompt

    prompt = build_feedback_analysis_prompt(feedback_text, department)
    raw = chat_completion(FEEDBACK_ANALYST_SYSTEM, prompt, temperature=0.2)
    result = _extract_json(raw)
    if not isinstance(result, dict):
        raise ValueError("Expected JSON object from LLM")
    return result


def hr_chat_response(question: str, context_feedbacks: list) -> str:
    from app.llm.prompts import HR_CHAT_SYSTEM, build_hr_chat_prompt

    prompt = build_hr_chat_prompt(question, context_feedbacks)
    return chat_completion(HR_CHAT_SYSTEM, prompt, temperature=0.4, max_tokens=800)


def generate_report(analytics: Dict[str, Any], recent_summaries: list) -> str:
    from app.llm.prompts import REPORT_GENERATOR_SYSTEM, build_report_prompt

    prompt = build_report_prompt(analytics, recent_summaries)
    return chat_completion(REPORT_GENERATOR_SYSTEM, prompt, temperature=0.5, max_tokens=1500)


def is_llm_configured() -> bool:
    settings = get_settings()
    return bool(settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here")
