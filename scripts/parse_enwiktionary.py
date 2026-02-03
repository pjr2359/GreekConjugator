#!/usr/bin/env python3
"""
Parse enwiktionary dump and extract Greek verb conjugation data.

This script scans the enwiktionary pages-articles XML dump (bz2) and emits
JSONL records for pages that contain a Greek verb section. It captures raw
template names/parameters and any wikitable blocks from the verb section.
It does not expand templates.
"""

import argparse
import bz2
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

LANG_HEADING_PATTERN = re.compile(
    r"^\s*(=+)\s*([^=].*?)\s*\1\s*$",
    re.MULTILINE,
)
GREEK_HEADING = "Greek"
ANCIENT_GREEK_MARKER = re.compile(
    r"\bAncient Greek\b|\{\{\s*(?:m|lang|grc)\s*\|\s*grc\b",
    re.IGNORECASE,
)

CONJ_TEMPLATE_PREFIXES = ("el-conj", "el-verb")
CONJ_TEMPLATE_EXACT = {
    "el-conjugation",
}


def normalize_template_name(name: str) -> str:
    return name.strip().lower().replace("_", " ")


def extract_templates(text: str) -> list[str]:
    templates = []
    depth = 0
    start = None
    i = 0
    while i < len(text) - 1:
        if text[i : i + 2] == "{{":
            if depth == 0:
                start = i
            depth += 1
            i += 2
            continue
        if text[i : i + 2] == "}}" and depth > 0:
            depth -= 1
            i += 2
            if depth == 0 and start is not None:
                templates.append(text[start:i])
                start = None
            continue
        i += 1
    return templates


def split_template_parts(template_body: str) -> list[str]:
    parts = []
    current = []
    depth = 0
    i = 0
    while i < len(template_body):
        if template_body[i : i + 2] == "{{":
            depth += 1
            current.append("{{")
            i += 2
            continue
        if template_body[i : i + 2] == "}}" and depth > 0:
            depth -= 1
            current.append("}}")
            i += 2
            continue
        if template_body[i] == "|" and depth == 0:
            parts.append("".join(current))
            current = []
            i += 1
            continue
        current.append(template_body[i])
        i += 1
    parts.append("".join(current))
    return parts


def parse_template(template_text: str) -> dict:
    body = template_text.strip()[2:-2]  # remove outer {{ }}
    parts = split_template_parts(body)
    name = parts[0].strip()
    positional = []
    named = {}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            named[key.strip()] = value.strip()
        else:
            positional.append(part.strip())
    return {
        "name": normalize_template_name(name),
        "raw_name": name.strip(),
        "positional": positional,
        "named": named,
    }


def is_conjugation_template(name: str) -> bool:
    normalized = normalize_template_name(name)
    return normalized.startswith(CONJ_TEMPLATE_PREFIXES) or normalized in CONJ_TEMPLATE_EXACT


def extract_tables(text: str) -> list[str]:
    tables = []
    i = 0
    while i < len(text) - 1:
        start = text.find("{|", i)
        if start == -1:
            break
        end = text.find("|}", start)
        if end == -1:
            break
        tables.append(text[start : end + 2])
        i = end + 2
    return tables


def extract_language_sections(text: str, language: str) -> list[str]:
    matches = list(LANG_HEADING_PATTERN.finditer(text))
    sections = []
    for i, match in enumerate(matches):
        title = match.group(2).strip()
        if title != language:
            continue
        level = len(match.group(1))
        start = match.end()
        end = len(text)
        for next_match in matches[i + 1 :]:
            next_level = len(next_match.group(1))
            if next_level <= level:
                end = next_match.start()
                break
        sections.append(text[start:end])
    return sections


def extract_heading_spans(section: str) -> list[dict]:
    headings = []
    for match in LANG_HEADING_PATTERN.finditer(section):
        level = len(match.group(1))
        title = match.group(2).strip()
        headings.append(
            {
                "start": match.start(),
                "end": match.end(),
                "level": level,
                "title": title,
            }
        )
    return headings


def extract_verb_sections(language_section: str) -> list[dict]:
    headings = extract_heading_spans(language_section)
    verb_sections = []
    for idx, heading in enumerate(headings):
        if heading["level"] < 3:
            continue
        if not heading["title"].startswith("Verb"):
            continue
        start = heading["end"]
        end = len(language_section)
        for next_heading in headings[idx + 1 :]:
            if next_heading["level"] <= heading["level"]:
                end = next_heading["start"]
                break
        verb_sections.append(
            {
                "heading": heading["title"],
                "text": language_section[start:end],
            }
        )
    return verb_sections


def iter_pages(dump_path: str):
    with bz2.open(dump_path, "rb") as handle:
        context = ET.iterparse(handle, events=("end",))
        for _, elem in context:
            if elem.tag.endswith("page"):
                title = elem.findtext("./{*}title") or ""
                ns = elem.findtext("./{*}ns") or ""
                text = elem.findtext(".//{*}text") or ""
                yield title, ns, text
                elem.clear()


def extract_records(
    dump_path: str,
    limit: int | None = None,
    max_pages: int | None = None,
    progress_every: int | None = None,
    skip_pages: int = 0,
    checkpoint_every: int | None = None,
    checkpoint_path: str | None = None,
    exclude_ancient: bool = True,
    emit_empty: bool = False,
    include_text: bool = False,
    text_limit: int | None = None,
):
    count = 0
    scanned = 0
    for title, ns, text in iter_pages(dump_path):
        scanned += 1
        if skip_pages and scanned <= skip_pages:
            continue
        if progress_every and scanned % progress_every == 0:
            print(
                f"scanned={scanned} matched={count} last_title={title}",
                file=sys.stderr,
            )
        if checkpoint_every and checkpoint_path and scanned % checkpoint_every == 0:
            Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, "w", encoding="utf-8") as checkpoint:
                json.dump(
                    {
                        "scanned": scanned,
                        "matched": count,
                        "last_title": title,
                    },
                    checkpoint,
                )
        if max_pages and scanned >= max_pages:
            break
        if ns != "0":
            continue
        if not text:
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
            if exclude_ancient and ANCIENT_GREEK_MARKER.search(verb_section["text"]):
                continue
            templates = extract_templates(verb_section["text"])
            parsed_templates = [parse_template(t) for t in templates]
            conjugation_templates = [
                t for t in parsed_templates if is_conjugation_template(t["name"])
            ]
            tables = extract_tables(verb_section["text"])
            if conjugation_templates or tables:
                has_conj_data = True
            payload = {
                "heading": verb_section["heading"],
                "conjugation_templates": conjugation_templates,
                "tables": tables,
            }
            if include_text:
                if text_limit is None:
                    payload["text"] = verb_section["text"]
                else:
                    payload["text"] = verb_section["text"][:text_limit]
            verb_payload.append(payload)

        if not verb_payload:
            continue

        if has_conj_data or emit_empty:
            yield {
                "title": title,
                "language": GREEK_HEADING,
                "verb_sections": verb_payload,
            }
            count += 1
            if limit and count >= limit:
                break


def main():
    parser = argparse.ArgumentParser(
        description="Extract enwiktionary Greek verb conjugation data into JSONL."
    )
    parser.add_argument("--dump", required=True, help="Path to enwiktionary XML dump (.bz2)")
    parser.add_argument("--out", required=True, help="Output JSONL file path")
    parser.add_argument("--limit", type=int, default=None, help="Optional max pages to emit")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional max pages to scan",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=None,
        help="Log progress every N pages (stderr)",
    )
    parser.add_argument(
        "--skip-pages",
        type=int,
        default=0,
        help="Skip the first N pages (for chunking/resume)",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=None,
        help="Write a checkpoint JSON every N scanned pages",
    )
    parser.add_argument(
        "--checkpoint-path",
        default=None,
        help="Path to write checkpoint JSON (used with --checkpoint-every)",
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

    with open(args.out, "w", encoding="utf-8") as out:
        for record in extract_records(
            args.dump,
            limit=args.limit,
            max_pages=args.max_pages,
            progress_every=args.progress_every,
            skip_pages=args.skip_pages,
            checkpoint_every=args.checkpoint_every,
            checkpoint_path=args.checkpoint_path,
            exclude_ancient=not args.include_ancient,
            emit_empty=args.emit_empty,
            include_text=args.include_text,
            text_limit=args.text_limit if args.include_text else None,
        ):
            out.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
