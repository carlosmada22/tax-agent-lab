from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.graph import GRAPH
from app.memory import load_history, save_history
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


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, debug: bool = Query(False)):
    thread = req.user_id  # changed user_id as thread_id
    history = load_history(thread)
    history = history + [f"user: {req.message}"]

    pv = normalize_prompt_version(req.prompt_version)

    state = {
        "user_id": req.user_id,
        "messages": history,
        "last_agent": "",
        "next": "general",
        "prompt_version": pv,
        "last_prompt": "",
        "pending_clarification": False,
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
