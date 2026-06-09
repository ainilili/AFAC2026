from __future__ import annotations

from tools.base import Tool


def get_weather(city: str) -> str:
    return f"{city}: sunny, 25C"


weather_tool = Tool(
    name="get_weather",
    description="Get current weather for a city.",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
    fn=get_weather,
)
