from __future__ import annotations

from typing import List, Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.context_builder import build_context
from app.prompts import load_system_prompt

TAX_KEYWORDS = [
    "tax",
    "refund",
    "deduction",
    "income",
    "vat",
    "steuern",
    "steuer",
    "erstattung",
    "abzug",
    "deduct",
    "deductible",
    "deductions",
]

GENERAL_OBJECTIVE = (
    "Answer the user in a helpful general way. "
    "If you are not sure or details are missing, ask exactly one clarifying question."
)

TAX_OBJECTIVE = (
    "Provide general tax information only. Do not give personal tax/legal advice. "
    "If details are missing, ask exactly one clarifying question."
)


def extract_last_user_message(messages: list[str]) -> str:
    for m in reversed(messages):
        if m.lower().startswith("user:"):
            return m.split(":", 1)[1].strip()
    return ""


def needs_clarification_for_tax(user_text: str) -> bool:
    t = user_text.lower()

    # Señales típicas de "esto depende de detalles"
    # (ej: "Can I...?", "In my case...", "My ...")
    triggers = [
        "can i",
        "should i",
        "my ",
        "in my case",
        "for me",
        "deduct my",
        "deduct it",
        "am i allowed",
        "is it possible",
    ]
    return any(x in t for x in triggers)


class AgentState(TypedDict):
    user_id: str
    messages: List[str]
    last_agent: str
    next: Literal["general", "tax_info"]
    prompt_version: Literal["v1", "v2"]
    last_prompt: str  # debug: last built prompt text
    pending_clarification: bool
    profile: dict


def supervisor(state: AgentState) -> AgentState:
    last = state["messages"][-1].lower() if state["messages"] else ""
    if state.get("pending_clarification", False):
        route = "tax_info"
    else:
        route = "tax_info" if any(k in last for k in TAX_KEYWORDS) else "general"
    state["last_agent"] = "supervisor"
    state["next"] = route
    return state


def general_agent(state: AgentState) -> AgentState:
    system_prompt = load_system_prompt(state.get("prompt_version"))
    context_text = build_context(
        system_prompt=system_prompt,
        objective=GENERAL_OBJECTIVE,
        messages=state["messages"],
        max_messages=8,
    )
    state["last_prompt"] = context_text
    state["last_agent"] = "general"
    pv = state.get("prompt_version", "v1")

    if pv == "v2":
        state["messages"].append(
            "assistant: I can help with general questions. Ask me anything."
        )
    else:
        state["messages"].append(
            "assistant: I can help with general questions. Ask me anything."
            "Depending on where you are located and your current conditions, the answer may vary."
        )
    return state


def tax_info_agent(state: AgentState) -> AgentState:
    system_prompt = load_system_prompt(state.get("prompt_version"))
    context_text = build_context(
        system_prompt=system_prompt,
        objective=TAX_OBJECTIVE,
        messages=state["messages"],
        max_messages=8,
    )
    state["last_prompt"] = context_text

    state["last_agent"] = "tax_info"
    pv = state.get("prompt_version", "v1")

    user_text = extract_last_user_message(state["messages"])

    # Si falta contexto, 1 pregunta y parar
    if needs_clarification_for_tax(user_text):
        state["pending_clarification"] = True
        question = "Which country’s tax rules should I use (for example Germany)?"
        state["messages"].append(f"assistant: {question}")
        return state

    # Si hay suficiente contexto, responde (v2 más corto)
    state["pending_clarification"] = False
    if pv == "v2":
        state["messages"].append(
            "assistant: Deductions generally reduce taxable income if specific conditions are met. "
            "Rules vary by country and deduction type."
        )
    else:
        state["messages"].append(
            "assistant: Here is general tax information. Deductions typically reduce your taxable income, "
            "but eligibility depends on your country and the specific expense type. "
            "I cannot provide personal tax advice, but I can explain general rules and concepts."
        )

    return state


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("supervisor", supervisor)
    g.add_node("general", general_agent)
    g.add_node("tax_info", tax_info_agent)

    g.set_entry_point("supervisor")

    g.add_conditional_edges(
        "supervisor",
        lambda s: s["next"],
        {
            "general": "general",
            "tax_info": "tax_info",
        },
    )

    g.add_edge("general", END)
    g.add_edge("tax_info", END)

    return g.compile()


GRAPH = build_graph()
