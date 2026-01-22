from __future__ import annotations

from typing import List


def build_context(
    system_prompt: str,
    objective: str,
    messages: List[str],
    max_messages: int = 8,
) -> str:
    """
    Build a single prompt string with a fixed structure:
      1) SYSTEM rules
      2) OBJECTIVE for this turn
      3) RECENT HISTORY (trimmed)
    """
    system_prompt = (system_prompt or "").strip()
    objective = (objective or "").strip()

    recent = messages[-max_messages:] if messages else []
    history_block = "\n".join(recent).strip()

    parts = [
        "SYSTEM:\n" + system_prompt,
        "OBJECTIVE:\n" + objective,
        "HISTORY:\n" + history_block,
    ]
    return "\n\n".join(parts).strip()
