from __future__ import annotations

from pathlib import Path

from knowledge_base.processors.base import BaseProcessor
from knowledge_base.processors.html import HtmlProcessor
from knowledge_base.processors.pdf import PdfProcessor
from knowledge_base.processors.txt import TxtProcessor

PROCESSORS: tuple[BaseProcessor, ...] = (
    TxtProcessor(),
    HtmlProcessor(),
    PdfProcessor(),
)


def get_processor(path: Path) -> BaseProcessor | None:
    for processor in PROCESSORS:
        if processor.supports(path):
            return processor
    return None
