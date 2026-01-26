from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.fact_extractor import extract_facts
from app.graph import GRAPH
from app.memory import load_history, save_history
from app.profile_store import load_profile, save_profile
from app.prompts import normalize_prompt_version

app = FastAPI()

MEMORY = {}  # user_id -> list[str]


class ChatRequest(BaseModel):
    user_id: str
    message: str
    prompt_version: Optional[str] = None


class ChatResponse(BaseModel):
    assistant_message: str
    last_agent: str
    debug_prompt: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/history/{user_id}")
def history(user_id: str):
    return {"messages": load_history(user_id)}


@app.post("/debug/profile/{user_id}")
def debug_profile(user_id: str):
    # save_profile(user_id, {"age": 50, "residency": "DE"})
    return load_profile(user_id)


@app.post("/debug/extract")
def debug_extract(payload: dict):
    text = payload.get("text", "")
    return extract_facts(text)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, debug: bool = Query(False)):
    thread = req.user_id  # changed user_id as thread_id
    history = load_history(thread)
    history = history + [f"user: {req.message}"]

    # --- Extract and persist profile facts ---
    new_facts = extract_facts(req.message)
    if new_facts:
        current_profile = load_profile(thread)
        current_profile.update(new_facts)
        save_profile(thread, current_profile)

    profile = load_profile(thread)

    pv = normalize_prompt_version(req.prompt_version)

    state = {
        "user_id": req.user_id,
        "messages": history,
        "last_agent": "",
        "next": "general",
        "prompt_version": pv,
        "last_prompt": "",
        "pending_clarification": False,
        "profile": profile,
    }

    out = GRAPH.invoke(state)
    save_history(thread, out["messages"])

    # Último mensaje del asistente
    assistant_msg = ""
    for m in reversed(out["messages"]):
        if m.startswith("assistant:"):
            assistant_msg = m.replace("assistant:", "", 1).strip()
            break

    return ChatResponse(
        assistant_message=assistant_msg,
        last_agent=out["last_agent"],
        debug_prompt=out.get("last_prompt") if debug else None,
    )
