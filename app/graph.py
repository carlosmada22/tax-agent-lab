from typing import List, Literal, TypedDict

from langgraph.graph import END, StateGraph

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
]


class AgentState(TypedDict):
    user_id: str
    messages: List[str]  # historial simple: "user: ..." / "assistant: ..."
    last_agent: str
    next: Literal["general", "tax_info"]


def supervisor(state: AgentState) -> AgentState:
    last = state["messages"][-1].lower() if state["messages"] else ""
    route = "tax_info" if any(k in last for k in TAX_KEYWORDS) else "general"
    state["last_agent"] = "supervisor"
    state["next"] = route
    return state


def general_agent(state: AgentState) -> AgentState:
    state["last_agent"] = "general"
    state["messages"].append(
        "assistant: I can help with general questions. Ask me anything."
    )
    return state


def tax_info_agent(state: AgentState) -> AgentState:
    state["last_agent"] = "tax_info"
    state["messages"].append(
        "assistant: Here is general tax information. I cannot provide personal tax advice, but I can explain rules and concepts."
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
