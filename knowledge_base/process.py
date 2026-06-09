#!/usr/bin/env python3
"""Process knowledge base raw files into structured text artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from knowledge_base.models import ProcessedDocument
from knowledge_base.paths import PROCESSED_DIR, RAW_DIR
from knowledge_base.processors.registry import get_processor


def iter_source_files(raw_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if get_processor(path) is not None:
            files.append(path)
    return files


def output_path_for(processed_dir: Path, source_relpath: str) -> Path:
    rel = Path(source_relpath)
    return processed_dir / rel.with_suffix(".json")


def process_file(
    source_path: Path, raw_dir: Path, processed_dir: Path, force: bool
) -> ProcessedDocument | None:
    processor = get_processor(source_path)
    if processor is None:
        return None

    source_relpath = str(source_path.relative_to(raw_dir))
    output_path = output_path_for(processed_dir, source_relpath)
    if output_path.exists() and not force:
        return None

    document = processor.process(source_path, source_relpath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return document


def write_index(processed_dir: Path, documents: list[ProcessedDocument]) -> None:
    index = {
        "total": len(documents),
        "documents": [
            {
                "doc_id": doc.doc_id,
                "source_relpath": doc.source_relpath,
                "format": doc.format,
                "title": doc.title,
                "char_count": doc.metadata.get("char_count", len(doc.content)),
                "processed_at": doc.processed_at,
            }
            for doc in sorted(documents, key=lambda item: item.source_relpath)
        ],
    }
    (processed_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run(raw_dir: Path, processed_dir: Path, force: bool) -> int:
    if not raw_dir.exists():
        print(f"Raw directory not found: {raw_dir}", file=sys.stderr)
        return 1

    source_files = iter_source_files(raw_dir)
    if not source_files:
        print(f"No supported files found under: {raw_dir}", file=sys.stderr)
        return 1

    processed: list[ProcessedDocument] = []
    skipped = 0
    failed = 0

    for source_path in source_files:
        source_relpath = str(source_path.relative_to(raw_dir))
        output_path = output_path_for(processed_dir, source_relpath)
        if output_path.exists() and not force:
            skipped += 1
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            processed.append(ProcessedDocument(**payload))
            continue

        try:
            document = process_file(source_path, raw_dir, processed_dir, force=True)
        except Exception as exc:  # noqa: BLE001 - report per-file failures
            failed += 1
            print(f"[FAIL] {source_relpath}: {exc}", file=sys.stderr)
            continue

        if document is not None:
            processed.append(document)
            print(f"[OK] {source_relpath}")

    write_index(processed_dir, processed)
    print(
        f"Done. processed={len(processed) - skipped}, "
        f"skipped={skipped}, failed={failed}, index={processed_dir / 'index.json'}"
    )
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process knowledge base raw files.")
    parser.add_argument(
        "--input",
        type=Path,
        default=RAW_DIR,
        help=f"Directory containing original files (default: {RAW_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROCESSED_DIR,
        help=f"Directory for processed JSON output (default: {PROCESSED_DIR})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess files even if output already exists",
    )
    args = parser.parse_args(argv)
    return run(args.input.resolve(), args.output.resolve(), args.force)


if __name__ == "__main__":
    raise SystemExit(main())
