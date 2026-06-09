from __future__ import annotations

import re
from pathlib import Path

from knowledge_base.models import ProcessedDocument
from knowledge_base.processors.base import BaseProcessor
from knowledge_base.utils import (
    doc_id_from_path,
    html_to_text,
    normalize_text,
    read_text_with_fallback,
)


class HtmlProcessor(BaseProcessor):
    extensions = (".html", ".htm")

    def process(self, path: Path, source_relpath: str) -> ProcessedDocument:
        html = read_text_with_fallback(path)
        title = self._extract_title(html) or path.stem
        content = self._extract_content(html)
        return ProcessedDocument(
            doc_id=doc_id_from_path(path),
            source_relpath=source_relpath,
            format="html",
            title=title,
            content=content,
            metadata={"char_count": len(content), "line_count": content.count("\n") + 1},
        )

    def _extract_title(self, html: str) -> str:
        for pattern in (
            r'<meta\s+name="ArticleTitle"\s+content="([^"]*)"',
            r"<title>([^<]+)</title>",
            r"<h2[^>]*>([^<]+)</h2>",
        ):
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                return normalize_text(match.group(1))
        return ""

    def _extract_content(self, html: str) -> str:
        for pattern in (
            r'<div\s+class="detail-news"[^>]*>(.*?)</div>\s*<div\s+class="xxgk-down-box"',
            r'<div\s+class="content"[^>]*>(.*?)</div>\s*</div>\s*</div>',
        ):
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                return html_to_text(match.group(1))
        return html_to_text(html)
