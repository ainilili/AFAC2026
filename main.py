#!/usr/bin/env python3
"""Entry point for the Qwen3.6-plus agent demo."""

from agent import AgentLoop, load_dotenv
from tools import get_tools


def main() -> None:
    load_dotenv()
    agent = AgentLoop(tools=get_tools())

    query = "What is the weather in Shanghai?"
    print(f"User: {query}")
    answer = agent.run(query)
    print(f"Agent: {answer}")


if __name__ == "__main__":
    main()
