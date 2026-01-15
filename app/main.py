from fastapi import FastAPI
from pydantic import BaseModel

from app.graph import GRAPH
from app.memory import load_history, save_history

app = FastAPI()

# "memoria" mínima para semana 1 (in-memory)
MEMORY = {}  # user_id -> list[str]


class ChatRequest(BaseModel):
    user_id: str
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    assistant_message: str
    last_agent: str


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/history/{user_id}")
def history(user_id: str):
    return {"messages": load_history(user_id)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    thread = req.thread_id or req.user_id
    history = load_history(thread)
    history = history + [f"user: {req.message}"]

    state = {
        "user_id": req.user_id,
        "messages": history,
        "last_agent": "",
        "next": "general",
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
    )
