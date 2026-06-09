from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agent.llm import call_llm, parse_tool_calls
from tools import Tool


@dataclass
class AgentLoop:
    tools: dict[str, Tool]
    max_steps: int = 10
    messages: list[dict[str, str]] = field(default_factory=list)

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(self.max_steps):
            response = call_llm(self.messages, list(self.tools.values()))
            self.messages.append({"role": "assistant", "content": response})

            tool_calls = parse_tool_calls(response)
            if not tool_calls:
                return response

            for call in tool_calls:
                result = self._execute_tool(call)
                self.messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(
                            {"tool": call["name"], "args": call["args"], "result": result},
                            ensure_ascii=False,
                        ),
                    }
                )

        return self.messages[-1]["content"]

    def _execute_tool(self, call: dict[str, Any]) -> str:
        tool = self.tools.get(call["name"])
        if tool is None:
            return f"Unknown tool: {call['name']}"
        try:
            return tool.fn(**call["args"])
        except TypeError as exc:
            return f"Invalid arguments: {exc}"
