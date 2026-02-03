#!/usr/bin/env python3
"""
Chunked, resumable parser for enwiktionary Greek verb sections.

This script performs a single pass over the dump, writing JSONL chunks
to an output directory. It also writes a checkpoint JSON so you can resume
after interruption.
"""

import argparse
import json
import sys
from pathlib import Path

from parse_enwiktionary import (
    ANCIENT_GREEK_MARKER,
    GREEK_HEADING,
    extract_language_sections,
    extract_tables,
    extract_templates,
    extract_verb_sections,
    is_conjugation_template,
    iter_pages,
    parse_template,
)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def chunk_filename(out_dir: Path, chunk_index: int) -> Path:
    return out_dir / f"wiktextract_el_chunk_{chunk_index:06d}.jsonl"


def write_checkpoint(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def load_checkpoint(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chunked parser for enwiktionary Greek verb sections."
    )
    parser.add_argument("--dump", required=True, help="Path to enwiktionary XML dump (.bz2)")
    parser.add_argument("--out-dir", required=True, help="Output directory for chunk JSONL files")
    parser.add_argument(
        "--chunk-pages",
        type=int,
        default=50000,
        help="Number of scanned pages per chunk file",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=0,
        help="Skip the first N pages (manual resume)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional max pages to scan",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max records to emit",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10000,
        help="Log progress every N pages (stderr)",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=10000,
        help="Write a checkpoint JSON every N scanned pages",
    )
    parser.add_argument(
        "--checkpoint-path",
        default=None,
        help="Path to write checkpoint JSON (default: <out-dir>/checkpoint.json)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint (overrides --start-page)",
    )
    parser.add_argument(
        "--include-ancient",
        action="store_true",
        help="Include Ancient Greek references inside Greek verb sections",
    )
    parser.add_argument(
        "--emit-empty",
        action="store_true",
        help="Emit verb sections even without conjugation templates/tables",
    )
    parser.add_argument(
        "--require-conj-templates",
        action="store_true",
        help="Only keep sections that include el-conj/el-verb templates",
    )
    parser.add_argument(
        "--include-text",
        action="store_true",
        help="Include verb section text (use --text-limit to truncate)",
    )
    parser.add_argument(
        "--text-limit",
        type=int,
        default=2000,
        help="Max characters of verb section text when --include-text is set",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    checkpoint_path = Path(args.checkpoint_path) if args.checkpoint_path else out_dir / "checkpoint.json"
    checkpoint = load_checkpoint(checkpoint_path) if args.resume else None

    scanned = 0
    matched = 0
    start_page = args.start_page
    chunk_index = 0
    chunk_start_scanned = 0
    current_out = None
    current_path = None

    if checkpoint:
        scanned = int(checkpoint.get("scanned", 0))
        matched = int(checkpoint.get("matched", 0))
        start_page = scanned
        chunk_index = int(checkpoint.get("chunk_index", 0))
        chunk_start_scanned = int(checkpoint.get("chunk_start_scanned", 0))
        current_path = Path(checkpoint.get("out_file", "")) if checkpoint.get("out_file") else None

        if current_path and current_path.exists():
            current_out = current_path.open("a", encoding="utf-8")
        else:
            current_path = chunk_filename(out_dir, chunk_index)
            current_out = current_path.open("a", encoding="utf-8")

        print(
            f"Resuming at scanned={scanned} matched={matched} chunk={chunk_index}",
            file=sys.stderr,
        )

    for title, ns, text in iter_pages(args.dump):
        scanned += 1

        if start_page and scanned <= start_page:
            continue

        if args.progress_every and scanned % args.progress_every == 0:
            print(
                f"scanned={scanned} matched={matched} last_title={title}",
                file=sys.stderr,
            )

        if args.max_pages and scanned >= args.max_pages:
            break

        if ns != "0" or not text:
            continue

        greek_sections = extract_language_sections(text, GREEK_HEADING)
        if not greek_sections:
            continue

        verb_sections = []
        for section in greek_sections:
            verb_sections.extend(extract_verb_sections(section))

        if not verb_sections:
            continue

        verb_payload = []
        has_conj_data = False
        for verb_section in verb_sections:
            section_text = verb_section["text"]
            if not args.include_ancient and ANCIENT_GREEK_MARKER.search(section_text):
                continue
            if (
                not args.emit_empty
                and not args.include_text
                and "el-conj" not in section_text
                and "el-verb" not in section_text
                and "{|" not in section_text
            ):
                continue
            if args.require_conj_templates and "el-conj" not in section_text and "el-verb" not in section_text:
                continue
            templates = extract_templates(section_text)
            parsed_templates = [parse_template(t) for t in templates]
            conjugation_templates = [
                t for t in parsed_templates if is_conjugation_template(t["name"])
            ]
            tables = extract_tables(section_text)
            if conjugation_templates or tables:
                has_conj_data = True
            payload = {
                "heading": verb_section["heading"],
                "conjugation_templates": conjugation_templates,
                "tables": tables,
            }
            if args.include_text:
                payload["text"] = (
                    section_text
                    if args.text_limit is None
                    else section_text[: args.text_limit]
                )
            verb_payload.append(payload)

        if not verb_payload:
            continue

        if has_conj_data or args.emit_empty:
            if current_out is None:
                current_path = chunk_filename(out_dir, chunk_index)
                current_out = current_path.open("a", encoding="utf-8")
                chunk_start_scanned = scanned

            record = {
                "title": title,
                "language": GREEK_HEADING,
                "verb_sections": verb_payload,
            }
            current_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            matched += 1

            if args.limit and matched >= args.limit:
                break

        if args.chunk_pages and scanned - chunk_start_scanned >= args.chunk_pages:
            if current_out:
                current_out.close()
            current_out = None
            current_path = None
            chunk_index += 1
            chunk_start_scanned = scanned

        if args.checkpoint_every and scanned % args.checkpoint_every == 0:
            write_checkpoint(
                checkpoint_path,
                {
                    "scanned": scanned,
                    "matched": matched,
                    "chunk_index": chunk_index,
                    "chunk_start_scanned": chunk_start_scanned,
                    "out_file": str(current_path) if current_path else "",
                    "last_title": title,
                },
            )

    if current_out:
        current_out.close()

    write_checkpoint(
        checkpoint_path,
        {
            "scanned": scanned,
            "matched": matched,
            "chunk_index": chunk_index,
            "chunk_start_scanned": chunk_start_scanned,
            "out_file": str(current_path) if current_path else "",
            "last_title": title if "title" in locals() else "",
        },
    )


if __name__ == "__main__":
    main()
