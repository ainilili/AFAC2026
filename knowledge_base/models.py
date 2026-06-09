from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ProcessedDocument:
    doc_id: str
    source_relpath: str
    format: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    processed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
