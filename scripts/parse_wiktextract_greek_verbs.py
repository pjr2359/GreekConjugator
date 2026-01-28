#!/usr/bin/env python3
"""
Parse Wiktextract JSONL and extract Greek verb forms.

Input: Wiktextract JSONL from `wiktwords` (expanded templates/Lua).
Output: JSONL records per Greek verb entry with inflected forms.
"""

import argparse
import json
import re

GREEK_CHAR_PATTERN = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")
GREEK_WORD_PATTERN = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]+")
GREEK_PHRASE_PATTERN = re.compile(
    r"^[\u0370-\u03FF\u1F00-\u1FFF\s··'’ʼ]+$"
)
HYPHEN_CHARS = {"-", "‐", "‑", "‒", "–", "—", "―"}


def normalize_form_text(form: str) -> list[str]:
    cleaned = form.strip()
    if not cleaned:
        return []
    if cleaned[0] in HYPHEN_CHARS:
        return []
    cleaned = cleaned.strip("{}")
    cleaned = cleaned.strip()
    if not cleaned or cleaned[0] in HYPHEN_CHARS:
        return []

    cleaned = re.sub(r"\s+", " ", cleaned)
    if GREEK_PHRASE_PATTERN.match(cleaned):
        return [cleaned]

    tokens = [m.group(0) for m in GREEK_WORD_PATTERN.finditer(cleaned)]
    tokens = [token for token in tokens if len(token) >= 2]
    return list(dict.fromkeys(tokens))


def iter_entries(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def extract_records(path: str, limit: int | None = None):
    count = 0
    for entry in iter_entries(path):
        if entry.get("lang") != "Greek":
            continue
        if entry.get("pos") != "verb":
            continue

        forms = []
        seen = set()
        for form_entry in entry.get("forms", []):
            form = form_entry.get("form")
            tags = set(form_entry.get("tags", []))
            source = form_entry.get("source")
            if source != "conjugation":
                continue
            if not form or form in {"-", "no-table-tags"}:
                continue
            if form.startswith("el-conjug-"):
                continue
            if "table-tags" in tags or "inflection-template" in tags:
                continue
            if not GREEK_CHAR_PATTERN.search(form):
                continue

            for normalized in normalize_form_text(form):
                key = (normalized, tuple(sorted(tags)), source)
                if key in seen:
                    continue
                seen.add(key)
                normalized_entry = dict(form_entry)
                normalized_entry["form"] = normalized
                forms.append(normalized_entry)

        record = {
            "word": entry.get("word"),
            "lang": entry.get("lang"),
            "pos": entry.get("pos"),
            "forms": forms,
            "inflection_templates": entry.get("inflection_templates", []),
            "head_templates": entry.get("head_templates", []),
        }
        yield record
        count += 1
        if limit and count >= limit:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Extract Greek verb forms from Wiktextract JSONL."
    )
    parser.add_argument("--in", dest="in_path", required=True, help="Input JSONL path")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    parser.add_argument("--limit", type=int, default=None, help="Optional max records")
    args = parser.parse_args()

    with open(args.out, "w", encoding="utf-8") as out:
        for record in extract_records(args.in_path, args.limit):
            out.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
