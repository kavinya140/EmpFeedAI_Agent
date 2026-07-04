"""
Prompt Engineering Module
──────────────────────────
Structured prompts following best practices:
  • Role assignment (system persona)
  • Few-shot examples
  • Chain-of-thought reasoning
  • JSON output formatting with schema
  • Temperature-controlled task separation
"""

from __future__ import annotations

from typing import Any, Dict, List

# ── System Personas ──────────────────────────────────────────────────────────

FEEDBACK_ANALYST_SYSTEM = """You are an expert HR Feedback Analyst AI assistant.
Your role is to analyze employee feedback with empathy, objectivity, and actionable insight.
You understand workplace dynamics, employee engagement, and organizational psychology.
Always respond in valid JSON only — no markdown, no extra text."""

HR_CHAT_SYSTEM = """You are the Employee Feedback Agent — an AI assistant for HR teams.
You help HR professionals understand employee sentiment, identify trends, and recommend actions.
Base your answers ONLY on the feedback data provided in context.
If data is insufficient, say so clearly. Be concise, professional, and actionable."""

REPORT_GENERATOR_SYSTEM = """You are an HR Report Writer AI.
Generate executive-ready summaries from employee feedback analytics.
Use clear headings, bullet points, and data-driven recommendations.
Tone: professional, constructive, and forward-looking."""


# ── Few-Shot Examples for Feedback Analysis ──────────────────────────────────

FEEDBACK_ANALYSIS_FEW_SHOT = """
Example 1:
Input: "I love the flexible work hours but the onboarding process was confusing and nobody explained benefits."
Output:
{
  "sentiment": "mixed",
  "sentiment_score": 0.55,
  "category": "onboarding",
  "themes": ["flexible work", "onboarding confusion", "benefits communication"],
  "urgency": "medium",
  "summary": "Employee appreciates flexible hours but experienced onboarding gaps around benefits.",
  "action_items": ["Improve onboarding checklist", "Assign benefits buddy for new hires"],
  "is_anonymous_safe": true
}

Example 2:
Input: "My manager constantly takes credit for my work. This is affecting my mental health."
Output:
{
  "sentiment": "negative",
  "sentiment_score": 0.15,
  "category": "management",
  "themes": ["credit attribution", "manager behavior", "mental health"],
  "urgency": "high",
  "summary": "Serious concern about manager taking credit for employee work, impacting wellbeing.",
  "action_items": ["Schedule confidential HR review", "Offer EAP resources", "Investigate management practices"],
  "is_anonymous_safe": true
}
"""


def build_feedback_analysis_prompt(feedback_text: str, department: str = "") -> str:
    """Chain-of-thought prompt for structured feedback analysis."""
    dept_context = f"\nDepartment: {department}" if department else ""
    return f"""Analyze the following employee feedback step by step:
1. Identify overall sentiment (positive/negative/neutral/mixed)
2. Assign sentiment score (0.0 = very negative, 1.0 = very positive)
3. Categorize (workplace_culture, compensation, management, work_life_balance, onboarding, tools, other)
4. Extract key themes
5. Assess urgency (low/medium/high)
6. Write a one-sentence summary
7. Suggest 2-3 actionable HR recommendations

{FEEDBACK_ANALYSIS_FEW_SHOT}

Now analyze this feedback:{dept_context}
Feedback: "{feedback_text}"

Respond with ONLY this JSON schema:
{{
  "sentiment": "positive|negative|neutral|mixed",
  "sentiment_score": 0.0-1.0,
  "category": "string",
  "themes": ["theme1", "theme2"],
  "urgency": "low|medium|high",
  "summary": "one sentence",
  "action_items": ["action1", "action2"],
  "is_anonymous_safe": true
}}"""


def build_hr_chat_prompt(question: str, context_feedbacks: List[Dict[str, Any]]) -> str:
    """RAG-augmented prompt for HR chat assistant."""
    context_block = ""
    for i, fb in enumerate(context_feedbacks[:8], 1):
        context_block += (
            f"\n[{i}] Dept: {fb.get('department', 'N/A')} | "
            f"Sentiment: {fb.get('sentiment', 'N/A')} | "
            f"Category: {fb.get('category', 'N/A')}\n"
            f"Summary: {fb.get('summary', fb.get('feedback_text', ''))[:300]}\n"
        )

    return f"""Using ONLY the employee feedback records below, answer the HR team's question.

RELEVANT FEEDBACK CONTEXT:
{context_block if context_block else "No feedback records available yet."}

HR QUESTION: {question}

Provide a helpful, actionable answer. Reference specific themes when possible.
If the context doesn't contain enough information, acknowledge the limitation."""


def build_report_prompt(analytics: Dict[str, Any], recent_summaries: List[str]) -> str:
    """Executive report generation prompt."""
    summaries_text = "\n".join(f"- {s}" for s in recent_summaries[:10])
    return f"""Generate an HR Executive Feedback Report based on this data:

ANALYTICS:
- Total feedback entries: {analytics.get('total_feedback', 0)}
- Average sentiment score: {analytics.get('avg_sentiment_score', 0)} (0=negative, 1=positive)
- By sentiment: {analytics.get('by_sentiment', {})}
- By department: {analytics.get('by_department', {})}
- By category: {analytics.get('by_category', {})}

RECENT FEEDBACK SUMMARIES:
{summaries_text or "No summaries available."}

Structure your report with:
1. Executive Summary (2-3 sentences)
2. Key Findings (3-5 bullet points)
3. Department Highlights
4. Recommended Actions (prioritized)
5. Risk Areas to Monitor"""


def build_sentiment_batch_prompt(feedback_items: List[str]) -> str:
    """Batch sentiment classification for dashboard trends."""
    items = "\n".join(f"{i+1}. {text[:200]}" for i, text in enumerate(feedback_items))
    return f"""Classify sentiment for each feedback item below.
Return JSON array with objects: {{"index": N, "sentiment": "positive|negative|neutral|mixed", "score": 0.0-1.0}}

Items:
{items}

Respond with ONLY a JSON array."""
