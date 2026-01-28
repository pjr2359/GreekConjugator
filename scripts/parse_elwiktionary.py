#!/usr/bin/env python3
"""
Parse elwiktionary dump and extract verb conjugation templates.

This script scans the elwiktionary pages-articles XML dump (bz2) and emits
JSONL records for pages that appear to be verbs or contain conjugation
templates. It does not expand templates; it captures raw template names and
parameters for later normalization.
"""

import argparse
import bz2
import json
import re
import xml.etree.ElementTree as ET

EL_SECTION_PATTERN = re.compile(r"\{\{-el-\}\}")
TENSE_LABEL_PATTERN = re.compile(
    r"(Ενεστώτας|Παρατατικός|Μέλλοντας|Αόριστος|Παρακείμενος|Υπερσυντέλικος)\s*:",
    re.MULTILINE,
)
GREEK_LETTER_PATTERN = re.compile(r"[Α-Ωα-ω]")

VERB_TEMPLATES = {
    "ρήμα",
    "ρημα",
    "el-ρήμα",
}

CONJ_TEMPLATES = {
    "κλίση",
    "κλίση-αρχή",
    "κλίση-τέλος",
}

INFO_TEMPLATES = {
    "κλίση",
    "κλίση-αρχή",
}


def normalize_template_name(name: str) -> str:
    return name.strip().lower().replace("_", " ")


def is_conjugation_template(name: str) -> bool:
    normalized = normalize_template_name(name)
    return normalized in CONJ_TEMPLATES


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


def extract_el_section(text: str) -> str:
    if "{{-el-}}" not in text:
        return ""
    parts = text.split("{{-el-}}", 1)
    after = parts[1]
    next_lang = re.search(r"\{\{-[a-z]{2,3}-\}\}", after)
    if next_lang:
        return after[: next_lang.start()]
    return after


def extract_link_forms(text: str) -> list[str]:
    forms = []
    for match in re.finditer(r"\{\{λ\|([^|}]+)", text):
        forms.append(match.group(1))
    for match in re.finditer(r"\[\[([^|\]]+)", text):
        forms.append(match.group(1))
    filtered = [form for form in forms if GREEK_LETTER_PATTERN.search(form)]
    return list(dict.fromkeys(filtered))


def extract_tense_groups(text: str) -> list[dict]:
    matches = list(TENSE_LABEL_PATTERN.finditer(text))
    if not matches:
        return []
    groups = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        label = match.group(1)
        chunk = text[start:end]
        forms = extract_link_forms(chunk)
        groups.append(
            {
                "label": label,
                "forms": forms,
            }
        )
    return groups


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


def extract_records(dump_path: str, limit: int | None = None):
    count = 0
    for title, ns, text in iter_pages(dump_path):
        if ns != "0":
            continue
        if not text:
            continue

        if not EL_SECTION_PATTERN.search(text):
            continue
        el_section = extract_el_section(text)
        if not el_section:
            continue

        templates = extract_templates(el_section)
        parsed_templates = [parse_template(template) for template in templates]
        verb_markers = [t for t in parsed_templates if t["name"] in VERB_TEMPLATES]
        klishi_blocks = [t for t in parsed_templates if t["name"] in INFO_TEMPLATES]
        klishi_groups = []
        for block in klishi_blocks:
            block_text = " | ".join(block["positional"])
            if not block_text:
                continue
            groups = extract_tense_groups(block_text)
            if groups:
                klishi_groups.extend(groups)

        if verb_markers or klishi_blocks:
            yield {
                "title": title,
                "has_el_section": True,
                "verb_markers": [t["raw_name"] for t in verb_markers],
                "klishi_groups": klishi_groups,
                "klishi_blocks": klishi_blocks,
            }
            count += 1
            if limit and count >= limit:
                break


def main():
    parser = argparse.ArgumentParser(
        description="Extract elwiktionary verb conjugation templates into JSONL."
    )
    parser.add_argument("--dump", required=True, help="Path to elwiktionary XML dump (.bz2)")
    parser.add_argument("--out", required=True, help="Output JSONL file path")
    parser.add_argument("--limit", type=int, default=None, help="Optional max pages to emit")
    args = parser.parse_args()

    with open(args.out, "w", encoding="utf-8") as out:
        for record in extract_records(args.dump, args.limit):
            out.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
