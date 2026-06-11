from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from knowledge_base.models import ProcessedDocument
from knowledge_base.paths import PROCESSED_DIR, PROJECT_ROOT


@dataclass(frozen=True)
class SegmentEntry:
    doc_id: str
    title: str
    path: str
    char_count: int
    preview: str


def load_document(doc_id: str) -> ProcessedDocument:
    doc_path = PROCESSED_DIR / f"{doc_id}.json"
    if not doc_path.exists():
        raise FileNotFoundError(f"Document not found: {doc_id}")

    payload = json.loads(doc_path.read_text(encoding="utf-8"))
    return ProcessedDocument(**payload)


def _entry_from_document(document: ProcessedDocument) -> SegmentEntry:
    preview = document.content.replace("\n", " ").strip()
    if len(preview) > 120:
        preview = preview[:120] + "..."
    return SegmentEntry(
        doc_id=document.doc_id,
        title=document.title,
        path=_relative_path(PROCESSED_DIR / f"{document.doc_id}.json"),
        char_count=len(document.content),
        preview=preview,
    )


def _parse_doc_ids(doc_ids: str) -> list[str]:
    return [item.strip() for item in re.split(r"[\s,，]+", doc_ids) if item.strip()]


def list_segment_catalog(doc_ids: str, *, keywords: str | None = None) -> str:
    ids = _parse_doc_ids(doc_ids)
    if not ids:
        raise ValueError("doc_ids is required")

    entries: list[SegmentEntry] = []
    missing: list[str] = []
    for doc_id in ids:
        try:
            entries.append(_entry_from_document(load_document(doc_id)))
        except FileNotFoundError:
            missing.append(doc_id)

    if keywords:
        entries = [entry for entry in entries if _matches_keywords(entry, keywords)]

    lines = [f"segment_count: {len(entries)}", ""]
    if missing:
        lines.insert(0, f"missing: {', '.join(missing)}")
        lines.insert(1, "")

    if not entries:
        if keywords:
            lines.append(f"No segments matched keywords: {keywords}")
        else:
            lines.append("No segments available.")
        return "\n".join(lines)

    for entry in entries:
        lines.append(
            f"- [{entry.doc_id}] {entry.title} "
            f"({entry.path}, {entry.char_count} chars)"
        )
        if entry.preview:
            lines.append(f"  preview: {entry.preview}")

    return "\n".join(lines)


def read_segment(doc_id: str) -> str:
    document = load_document(doc_id)
    return (
        f"doc_id: {document.doc_id}\n"
        f"title: {document.title}\n"
        f"path: {_relative_path(PROCESSED_DIR / f'{document.doc_id}.json')}\n"
        f"char_count: {len(document.content)}\n"
        f"\n{document.content}"
    )


def search_segments(doc_ids: str, keywords: str) -> str:
    """Keyword-based segment lookup without embeddings."""
    return list_segment_catalog(doc_ids, keywords=keywords)


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _matches_keywords(entry: SegmentEntry, keywords: str) -> bool:
    terms = [
        term.strip().lower()
        for term in re.split(r"[\s,，]+", keywords)
        if term.strip()
    ]
    if not terms:
        return True

    document = load_document(entry.doc_id)
    haystack = f"{entry.title}\n{document.content}".lower()
    return all(term in haystack for term in terms)
