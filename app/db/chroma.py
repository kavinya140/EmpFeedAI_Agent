"""Lightweight feedback index with a Chroma-compatible fallback interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import get_settings

_collection = None


def _get_store_path() -> Path:
    settings = get_settings()
    path = Path(settings.chroma_persist_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / "feedback_index.json"


def _load_store() -> List[Dict[str, Any]]:
    store_path = _get_store_path()
    if not store_path.exists():
        return []
    try:
        with store_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_store(items: List[Dict[str, Any]]) -> None:
    store_path = _get_store_path()
    with store_path.open("w", encoding="utf-8") as handle:
        json.dump(items, handle, indent=2)


def get_collection():
    global _collection
    if _collection is None:
        _collection = {"items": _load_store()}
    return _collection


def index_feedback(
    feedback_id: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    collection = get_collection()
    meta = metadata or {}
    meta["feedback_id"] = feedback_id
    items = collection["items"]
    existing = next((item for item in items if item.get("feedback_id") == feedback_id), None)
    record = {
        "feedback_id": feedback_id,
        "text": text,
        "metadata": {k: str(v) for k, v in meta.items()},
    }
    if existing is None:
        items.append(record)
    else:
        existing.update(record)
    _save_store(items)


def search_similar(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    collection = get_collection()
    items = collection["items"]
    if not items:
        return []

    query_terms = {term for term in query.lower().split() if term}
    ranked: List[tuple[int, Dict[str, Any]]] = []
    for item in items:
        text = (item.get("text") or "").lower()
        terms = {term for term in text.split() if term}
        overlap = len(query_terms & terms)
        if overlap == 0 and query_terms:
            continue
        ranked.append((overlap, item))

    ranked.sort(key=lambda entry: (-entry[0], entry[1].get("text", "")))
    return [
        {
            "text": item.get("text"),
            "metadata": item.get("metadata", {}),
            "distance": None,
        }
        for _, item in ranked[:top_k]
    ]


def get_index_count() -> int:
    return len(get_collection()["items"])
