from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from tools import Tool

QWEN_MODEL = "qwen3.6-plus"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


def parse_tool_calls(text: str) -> list[dict[str, Any]]:
    """Parse tool calls from fenced JSON blocks in model output."""
    pattern = r"```json\s*(\{.*?\})\s*```"
    calls: list[dict[str, Any]] = []
    for match in re.finditer(pattern, text, re.DOTALL):
        payload = json.loads(match.group(1))
        if payload.get("type") != "tool_call":
            continue
        calls.append({"name": payload["name"], "args": payload.get("args", {})})
    return calls


def build_system_prompt(tools: list[Tool]) -> str:
    tool_specs = [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
        for tool in tools
    ]
    return (
        "You are a helpful assistant with tools.\n"
        "When you need a tool, reply with one or more fenced JSON blocks:\n"
        '```json\n{"type": "tool_call", "name": "<tool_name>", "args": {...}}\n```\n'
        "When the task is complete, reply with plain text only (no tool_call blocks).\n"
        f"Available tools:\n{json.dumps(tool_specs, ensure_ascii=False, indent=2)}"
    )


def call_llm(messages: list[dict[str, str]], tools: list[Tool]) -> str:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is required. "
            "Get one at https://help.aliyun.com/zh/model-studio/get-api-key"
        )
    return call_qwen(messages, tools, api_key)


def call_qwen(
    messages: list[dict[str, str]], tools: list[Tool], api_key: str
) -> str:
    base_url = os.environ.get("DASHSCOPE_BASE_URL", DASHSCOPE_BASE_URL)
    url = f"{base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": QWEN_MODEL,
        "messages": [{"role": "system", "content": build_system_prompt(tools)}]
        + messages,
        "temperature": 0,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"DashScope API error ({QWEN_MODEL}): {exc.code} {detail}"
        ) from exc

    return body["choices"][0]["message"]["content"]
