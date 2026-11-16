"""Operational request intake and tracking API (rule-based MVP)."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.workflow import classify_request

DATABASE_PATH = Path(os.getenv("OPERATIONS_DB_PATH", "operations.db"))


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY,
                department TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Enterprise AI Operations Agent", version="0.1.0", lifespan=lifespan)


class RequestInput(BaseModel):
    department: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=5, max_length=2000)


@app.get("/health")
def health():
    return {"status": "ok", "stage": "rule-based-mvp"}


@app.post("/requests", status_code=201)
def create_request(payload: RequestInput):
    classification = classify_request(payload.department, payload.description)
    request = {
        "id": str(uuid.uuid4()),
        "department": payload.department.strip(),
        "description": payload.description.strip(),
        **classification,
        "status": "pending_review",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO requests
               (id, department, description, category, priority, status, created_at)
               VALUES (:id, :department, :description, :category, :priority, :status, :created_at)""",
            request,
        )
    return request


@app.get("/requests")
def list_requests():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM requests ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]


@app.get("/requests/{request_id}")
def get_request(request_id: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    return dict(row)
