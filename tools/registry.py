from __future__ import annotations

from tools.base import Tool
from tools.weather import weather_tool

# Add new tools here to register them with the agent.
REGISTERED_TOOLS: tuple[Tool, ...] = (
    weather_tool,
)


def get_tools() -> dict[str, Tool]:
    tools: dict[str, Tool] = {}
    for tool in REGISTERED_TOOLS:
        if tool.name in tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")
        tools[tool.name] = tool
    return tools
