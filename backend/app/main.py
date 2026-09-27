"""Lumi AI-core backend — FastAPI application entrypoint.

Run with: uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import data as data_router
from app.api import health as health_router
from app.api import memory as memory_router
from app.models.database import init_db

app = FastAPI(
    title="Lumi AI Core",
    description="Privacy-first personal AI companion backend.",
    version="0.1.0",
)

# Permissive CORS for hackathon/local dev so the frontend (Vite dev server,
# a different port) can call this API directly once realApi.ts exists.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health_router.router)
app.include_router(data_router.router)
app.include_router(memory_router.router)
