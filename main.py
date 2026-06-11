#!/usr/bin/env python3
"""Entry point for the Qwen3.6-plus agent demo."""

from __future__ import annotations

import json
from pathlib import Path

from agent import AgentLoop, load_dotenv
from tools import get_tools

DEFAULT_QUESTION_PATH = Path(
    ".samples/questions/group_a/financial_contracts_questions.json"
)


def load_question(qid: str = "fc_a_001") -> dict:
    questions = json.loads(DEFAULT_QUESTION_PATH.read_text(encoding="utf-8"))
    for item in questions:
        if item["qid"] == qid:
            return item
    raise ValueError(f"Question not found: {qid}")


def format_question(question: dict) -> str:
    options = "\n".join(
        f"{key}. {value}" for key, value in question["options"].items()
    )
    doc_ids = ", ".join(question["doc_ids"])
    return (
        f"请回答以下{question['type']}。\n"
        f"相关文档 doc_ids: {doc_ids}\n"
        f"请先使用 list_doc_segments(doc_ids=\"{doc_ids}\") 查看分片目录，"
        f"再用 read_doc_segment 阅读相关片段。\n"
        f"问题: {question['question']}\n"
        f"选项:\n{options}\n"
        f"answer_format: {question['answer_format']}"
    )


def main() -> None:
    load_dotenv()
    agent = AgentLoop(tools=get_tools())

    question = load_question("fc_a_001")
    query = format_question(question)
    print(f"User: {query}\n")
    answer = agent.run(query)
    print(f"Agent: {answer}")


if __name__ == "__main__":
    main()
