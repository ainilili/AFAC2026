from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from knowledge_base.models import ProcessedDocument


class BaseProcessor(ABC):
    extensions: tuple[str, ...] = ()

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    @abstractmethod
    def process(self, path: Path, source_relpath: str) -> ProcessedDocument:
        raise NotImplementedError
