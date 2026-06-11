from __future__ import annotations

from knowledge_base.reader import list_segment_catalog, read_segment, search_segments
from tools.base import Tool


def list_doc_segments(doc_ids: str, keywords: str = "") -> str:
    """Return the segment catalog for related documents, optionally filtered by keywords."""
    if keywords.strip():
        return search_segments(doc_ids, keywords.strip())
    return list_segment_catalog(doc_ids)


def read_doc_segment(doc_id: str) -> str:
    """Read one processed document segment by doc_id."""
    return read_segment(doc_id)


list_doc_segments_tool = Tool(
    name="list_doc_segments",
    description=(
        "List processed document segments for the given doc_ids. Each entry uses the "
        "document title as the catalog label and shows the processed JSON file path. "
        "Optionally pass keywords to filter relevant segments without embeddings."
    ),
    parameters={
        "type": "object",
        "properties": {
            "doc_ids": {
                "type": "string",
                "description": "Related document ids, comma-separated, e.g. text01,text02.",
            },
            "keywords": {
                "type": "string",
                "description": (
                    "Optional keywords for simple text filtering across titles and content."
                ),
            },
        },
        "required": ["doc_ids"],
    },
    fn=list_doc_segments,
)

read_doc_segment_tool = Tool(
    name="read_doc_segment",
    description="Read the full text of one processed document segment by doc_id.",
    parameters={
        "type": "object",
        "properties": {
            "doc_id": {
                "type": "string",
                "description": "Document id from list_doc_segments, e.g. text01.",
            },
        },
        "required": ["doc_id"],
    },
    fn=read_doc_segment,
)
