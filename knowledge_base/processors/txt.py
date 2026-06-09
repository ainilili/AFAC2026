from __future__ import annotations

from pathlib import Path

from knowledge_base.models import ProcessedDocument
from knowledge_base.processors.base import BaseProcessor
from knowledge_base.utils import doc_id_from_path, normalize_text, read_text_with_fallback


class TxtProcessor(BaseProcessor):
    extensions = (".txt",)

    def process(self, path: Path, source_relpath: str) -> ProcessedDocument:
        content = normalize_text(read_text_with_fallback(path))
        title = path.stem
        return ProcessedDocument(
            doc_id=doc_id_from_path(path),
            source_relpath=source_relpath,
            format="txt",
            title=title,
            content=content,
            metadata={"char_count": len(content), "line_count": content.count("\n") + 1},
        )
