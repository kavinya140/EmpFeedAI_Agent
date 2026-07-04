"""FastAPI application entry point."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db.mongodb import close_mongodb, connect_mongodb
from app.routes.api import router

log = structlog.get_logger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    log.info("starting_app", host=settings.app_host, port=settings.app_port)

    for attempt in range(10):
        try:
            await connect_mongodb()
            log.info("mongodb_connected")
            break
        except Exception as exc:
            log.warning("mongodb_retry", attempt=attempt + 1, error=str(exc))
            if attempt == 9:
                raise
            await asyncio.sleep(3)

    yield

    await close_mongodb()
    log.info("app_shutdown")


app = FastAPI(
    title="Employee Feedback Agent",
    description="AI-powered HR feedback collection and analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/health")
async def health():
    return {"status": "healthy"}
