from __future__ import annotations

from pathlib import Path

from knowledge_base.models import ProcessedDocument
from knowledge_base.processors.base import BaseProcessor
from knowledge_base.utils import doc_id_from_path, normalize_text


class PdfProcessor(BaseProcessor):
    extensions = (".pdf",)

    def process(self, path: Path, source_relpath: str) -> ProcessedDocument:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF processing requires pypdf. Install with: pip install pypdf"
            ) from exc

        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)

        content = normalize_text("\n\n".join(pages))
        title = path.stem
        return ProcessedDocument(
            doc_id=doc_id_from_path(path),
            source_relpath=source_relpath,
            format="pdf",
            title=title,
            content=content,
            metadata={
                "char_count": len(content),
                "page_count": len(reader.pages),
                "line_count": content.count("\n") + 1 if content else 0,
            },
        )
