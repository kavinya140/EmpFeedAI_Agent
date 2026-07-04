"""FastAPI route handlers."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import analytics_service, feedback_service

router = APIRouter()


class FeedbackSubmit(BaseModel):
    feedback_text: str = Field(..., min_length=10, max_length=5000)
    department: str = Field(default="General", max_length=100)
    employee_name: Optional[str] = Field(default=None, max_length=100)
    is_anonymous: bool = True


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


@router.get("/status")
async def api_status():
    analytics = await analytics_service.get_dashboard_analytics()
    return {
        "status": "ok",
        "service": "Employee Feedback Agent",
        "version": "1.0.0",
        **analytics,
    }


@router.post("/feedback")
async def submit_feedback(payload: FeedbackSubmit):
    try:
        result = await feedback_service.submit_feedback(
            feedback_text=payload.feedback_text,
            department=payload.department,
            employee_name=payload.employee_name,
            is_anonymous=payload.is_anonymous,
        )
        return {"success": True, "feedback": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {exc}")


@router.get("/feedback")
async def list_feedback(
    limit: int = 50,
    department: Optional[str] = None,
    sentiment: Optional[str] = None,
):
    items = await feedback_service.get_all_feedback(
        limit=min(limit, 100),
        department=department,
        sentiment=sentiment,
    )
    return {"count": len(items), "feedback": items}


@router.get("/feedback/search")
async def search_feedback(q: str, top_k: int = 5):
    if len(q.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters.")
    results = await feedback_service.search_feedback(q, top_k=min(top_k, 20))
    return {"query": q, "count": len(results), "results": results}


@router.get("/analytics")
async def get_analytics():
    return await analytics_service.get_dashboard_analytics()


@router.post("/chat")
async def hr_chat(payload: ChatRequest):
    try:
        return await analytics_service.chat_with_agent(payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}")


@router.get("/report")
async def generate_report():
    try:
        return await analytics_service.generate_hr_report()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")
