from fastapi import FastAPI
from pydantic import BaseModel

from app.graph import GRAPH

app = FastAPI()

# "memoria" mínima para semana 1 (in-memory)
MEMORY = {}  # user_id -> list[str]


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    assistant_message: str
    last_agent: str


@app.get("/health")
def health():
    return {"status": "OK"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = MEMORY.get(req.user_id, [])
    history = history + [f"user: {req.message}"]

    state = {
        "user_id": req.user_id,
        "messages": history,
        "last_agent": "",
        "next": "general",
    }

    out = GRAPH.invoke(state)

    # Guardar historial actualizado
    MEMORY[req.user_id] = out["messages"]

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
