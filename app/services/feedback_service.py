"""Feedback submission and retrieval service."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.db import chroma, mongodb
from app.llm.client import analyze_feedback_json, is_llm_configured


def _fallback_analysis(feedback_text: str) -> Dict[str, Any]:
    """Rule-based fallback when LLM is unavailable."""
    text_lower = feedback_text.lower()
    negative_words = ["bad", "terrible", "hate", "awful", "toxic", "stress", "unfair"]
    positive_words = ["great", "love", "excellent", "amazing", "happy", "supportive"]

    neg_count = sum(1 for w in negative_words if w in text_lower)
    pos_count = sum(1 for w in positive_words if w in text_lower)

    if neg_count > pos_count:
        sentiment, score = "negative", max(0.1, 0.4 - neg_count * 0.05)
    elif pos_count > neg_count:
        sentiment, score = "positive", min(0.9, 0.6 + pos_count * 0.05)
    else:
        sentiment, score = "neutral", 0.5

    return {
        "sentiment": sentiment,
        "sentiment_score": round(score, 2),
        "category": "other",
        "themes": ["general feedback"],
        "urgency": "high" if neg_count >= 2 else "medium",
        "summary": feedback_text[:150] + ("..." if len(feedback_text) > 150 else ""),
        "action_items": ["Review feedback manually", "Follow up with employee if not anonymous"],
        "is_anonymous_safe": True,
        "analysis_mode": "fallback",
    }


async def submit_feedback(
    feedback_text: str,
    department: str = "General",
    employee_name: Optional[str] = None,
    is_anonymous: bool = True,
) -> Dict[str, Any]:
    if is_llm_configured():
        analysis = analyze_feedback_json(feedback_text, department)
        analysis["analysis_mode"] = "llm"
    else:
        analysis = _fallback_analysis(feedback_text)

    doc = {
        "feedback_text": feedback_text,
        "department": department,
        "employee_name": None if is_anonymous else employee_name,
        "is_anonymous": is_anonymous,
        **analysis,
    }

    feedback_id = await mongodb.insert_feedback(doc)

    try:
        chroma.index_feedback(
            feedback_id=feedback_id,
            text=feedback_text,
            metadata={
                "department": department,
                "sentiment": analysis.get("sentiment", "unknown"),
                "category": analysis.get("category", "other"),
            },
        )
    except Exception:
        pass

    doc["_id"] = feedback_id
    return doc


async def get_all_feedback(
    limit: int = 50,
    department: Optional[str] = None,
    sentiment: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return await mongodb.list_feedback(limit=limit, department=department, sentiment=sentiment)


async def search_feedback(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    results = chroma.search_similar(query, top_k=top_k)
    enriched = []
    for item in results:
        fb_id = item.get("metadata", {}).get("feedback_id")
        if fb_id:
            doc = await mongodb.get_feedback_by_id(fb_id)
            if doc:
                enriched.append(doc)
                continue
        enriched.append({"feedback_text": item.get("text"), "metadata": item.get("metadata")})
    return enriched
