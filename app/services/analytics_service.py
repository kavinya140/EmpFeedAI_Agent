"""Analytics and HR report generation."""

from __future__ import annotations

from typing import Any, Dict

from app.db import chroma, mongodb
from app.llm.client import generate_report, hr_chat_response, is_llm_configured
from app.services.feedback_service import search_feedback


async def get_dashboard_analytics() -> Dict[str, Any]:
    summary = await mongodb.get_analytics_summary()
    summary["vector_index_count"] = chroma.get_index_count()
    summary["llm_configured"] = is_llm_configured()
    return summary


async def chat_with_agent(question: str) -> Dict[str, Any]:
    context = await search_feedback(question, top_k=8)
    if not context:
        context = await mongodb.list_feedback(limit=8)

    if is_llm_configured():
        answer = hr_chat_response(question, context)
    else:
        answer = (
            "LLM is not configured. Set GROQ_API_KEY in your .env file. "
            f"Found {len(context)} relevant feedback records in the database."
        )

    return {"question": question, "answer": answer, "context_count": len(context)}


async def generate_hr_report() -> Dict[str, Any]:
    analytics = await get_dashboard_analytics()
    recent = await mongodb.list_feedback(limit=10)
    summaries = [fb.get("summary", fb.get("feedback_text", "")[:100]) for fb in recent]

    if is_llm_configured() and analytics.get("total_feedback", 0) > 0:
        report = generate_report(analytics, summaries)
    else:
        report = (
            "## HR Feedback Report\n\n"
            f"Total feedback: {analytics.get('total_feedback', 0)}\n"
            f"Average sentiment: {analytics.get('avg_sentiment_score', 0)}\n\n"
            "Configure GROQ_API_KEY to generate AI-powered executive reports."
        )

    return {"report": report, "analytics": analytics}
