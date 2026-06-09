from __future__ import annotations

from pathlib import Path

KNOWLEDGE_BASE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = KNOWLEDGE_BASE_ROOT.parent
RAW_DIR = KNOWLEDGE_BASE_ROOT / "raw"
PROCESSED_DIR = KNOWLEDGE_BASE_ROOT / "processed"
