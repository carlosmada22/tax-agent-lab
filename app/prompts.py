from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

PromptVersion = Literal["v1", "v2"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # .../app -> project root
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def normalize_prompt_version(v: Optional[str]) -> PromptVersion:
    if not v:
        return "v1"
    v = v.strip().lower()
    if v in ("v1", "1", "system_v1", "system-v1"):
        return "v1"
    if v in ("v2", "2", "system_v2", "system-v2"):
        return "v2"
    # default safe:
    return "v1"


def load_system_prompt(version: Optional[str]) -> str:
    v = normalize_prompt_version(version)
    path = PROMPTS_DIR / f"system_{v}.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt file: {path}")
    return path.read_text(encoding="utf-8")
