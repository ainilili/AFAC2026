from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolFn = Callable[..., str]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: ToolFn
