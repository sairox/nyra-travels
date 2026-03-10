"""
api/server.py

FastAPI server for TripMind.

Endpoints:
  POST /chat          — Send a message, get a response
  GET  /trip/{id}     — Get current trip state
  POST /trip/reset    — Start a fresh trip

Sessions are stored in-memory (dict keyed by session_id).
In Phase 2, replace with PostgreSQL + Redis for persistence.
"""

from __future__ import annotations
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from models.trip import TripState
from agent.loop import run_agent

app = FastAPI(title="TripMind AI", version="0.1.0")

# Allow all origins for local dev — tighten this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store ────────────────────────────────────────────────────
# Each session holds: messages, trip state, search cache
sessions: dict[str, dict] = {}


def get_or_create_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "trip": TripState(),
            "search_cache": {},
        }
    return sessions[session_id]


# ── Request / Response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None   # omit to start a new session


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    trip_summary: str


class TripResponse(BaseModel):
    session_id: str
    trip: dict


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "TripMind API is running", "version": "0.1.0"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Send a message to TripMind and get a response.
    Pass session_id to continue an existing conversation.
    Omit session_id to start a new one.
    """
    session_id = req.session_id or uuid.uuid4().hex
    session = get_or_create_session(session_id)

    # Append user message
    session["messages"].append({
        "role": "user",
        "content": req.message,
    })

    # Run the agent (may call tools internally before responding)
    reply, updated_messages = run_agent(
        messages=session["messages"],
        trip=session["trip"],
        search_cache=session["search_cache"],
    )

    # Update message history (agent loop may have added tool messages)
    session["messages"] = updated_messages

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        trip_summary=session["trip"].summary(),
    )


@app.get("/trip/{session_id}", response_model=TripResponse)
def get_trip(session_id: str):
    """Get the current trip state for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return TripResponse(
        session_id=session_id,
        trip=sessions[session_id]["trip"].model_dump(),
    )


@app.post("/trip/reset")
def reset_trip(session_id: str):
    """Start a fresh trip for an existing session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    sessions[session_id]["trip"] = TripState()
    sessions[session_id]["messages"] = []
    sessions[session_id]["search_cache"] = {}
    return {"message": "Trip reset", "session_id": session_id}
