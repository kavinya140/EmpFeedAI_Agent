"""MongoDB connection and feedback document operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_mongodb() -> AsyncIOMotorDatabase:
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db]
    await _db.feedback.create_index("created_at")
    await _db.feedback.create_index("department")
    await _db.feedback.create_index("sentiment")
    return _db


async def close_mongodb() -> None:
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB not connected. Call connect_mongodb() first.")
    return _db


async def insert_feedback(doc: Dict[str, Any]) -> str:
    db = get_db()
    doc.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    result = await db.feedback.insert_one(doc)
    return str(result.inserted_id)


async def get_feedback_by_id(feedback_id: str) -> Optional[Dict[str, Any]]:
    from bson import ObjectId

    db = get_db()
    try:
        doc = await db.feedback.find_one({"_id": ObjectId(feedback_id)})
    except Exception:
        return None
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def list_feedback(
    limit: int = 50,
    department: Optional[str] = None,
    sentiment: Optional[str] = None,
) -> List[Dict[str, Any]]:
    db = get_db()
    query: Dict[str, Any] = {}
    if department:
        query["department"] = department
    if sentiment:
        query["sentiment"] = sentiment

    cursor = db.feedback.find(query).sort("created_at", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def get_analytics_summary() -> Dict[str, Any]:
    db = get_db()
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total": {"$sum": 1},
                "avg_sentiment_score": {"$avg": "$sentiment_score"},
            }
        }
    ]
    totals = await db.feedback.aggregate(pipeline).to_list(1)
    total_info = totals[0] if totals else {"total": 0, "avg_sentiment_score": 0}

    by_sentiment = await db.feedback.aggregate(
        [{"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}]
    ).to_list(20)

    by_department = await db.feedback.aggregate(
        [{"$group": {"_id": "$department", "count": {"$sum": 1}}}]
    ).to_list(20)

    by_category = await db.feedback.aggregate(
        [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    ).to_list(20)

    return {
        "total_feedback": total_info.get("total", 0),
        "avg_sentiment_score": round(total_info.get("avg_sentiment_score") or 0, 2),
        "by_sentiment": {item["_id"] or "unknown": item["count"] for item in by_sentiment},
        "by_department": {item["_id"] or "unknown": item["count"] for item in by_department},
        "by_category": {item["_id"] or "unknown": item["count"] for item in by_category},
    }
