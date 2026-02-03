#!/usr/bin/env python3
"""
Build a starter Modern Greek verb lexicon from available sources.

Sources (priority):
1) morph_extraction_matched_*.json (accented finite forms)
2) enwiktionary_greek_verbs.jsonl (wiktextract templates)
3) extracted_verbs.json (Kaikki extraction)
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, Optional


DEFAULT_MORPH = "morph_extraction_matched_20250716_190035.json"
DEFAULT_WIKT = "enwiktionary_greek_verbs.jsonl"
DEFAULT_KAIKKI = "greek-conjugator/extracted_verbs.json"
DEFAULT_OUT = "scripts/data/verb_lexicon.json"


VOWELS = "αεηιουωάέήίόύώ"
LEMMA_PATTERN = re.compile(r".*(άω|ώ|ω|ομαι|μαι)$")


def normalize_key(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text.strip().lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("ς", "σ")
    return unicodedata.normalize("NFC", text)


def strip_ending(form: str, endings: Iterable[str]) -> Optional[str]:
    for ending in sorted(endings, key=len, reverse=True):
        if form.endswith(ending):
            return form[: -len(ending)]
    return None


def infer_present_stem(form: str) -> Optional[str]:
    return strip_ending(form, ["άω", "ώ", "ω"])


def infer_aorist_active_stem(form: str) -> Optional[str]:
    endings = ["ήσα", "ίσα", "άσα", "έσα", "ώσα", "ξα", "ψα", "σα", "α"]
    return strip_ending(form, endings)


def infer_aorist_passive_stem(form: str) -> Optional[str]:
    endings = ["ήθηκα", "ηθηκα", "τήκα", "τηκα", "θήκα", "θηκα", "ηκα"]
    return strip_ending(form, endings)


def infer_aorist_type(form: str) -> Optional[str]:
    if any(form.endswith(suffix) for suffix in ["σα", "ξα", "ψα"]):
        return "sigmatic"
    return "non-sigmatic"


def infer_class_id(present_1sg: Optional[str], present_2sg: Optional[str]) -> str:
    if present_2sg and present_2sg.endswith("είς"):
        return "B2"
    if present_1sg and (present_1sg.endswith("άω") or present_1sg.endswith("ώ")):
        return "B1"
    return "A"


def is_likely_lemma(text: str) -> bool:
    if not text:
        return False
    if any(ch.isspace() for ch in text):
        return False
    if text.endswith("τω") and not text.endswith("τώ"):
        return False
    if not LEMMA_PATTERN.match(text):
        return False
    return True


def load_morph_extraction(path: str) -> Dict[str, dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries: Dict[str, dict] = {}
    for item in data:
        lemma = item.get("lemma")
        if not lemma:
            continue
        entries[normalize_key(lemma)] = item
    return entries


def load_wiktextract(path: str) -> Dict[str, dict]:
    entries: Dict[str, dict] = {}
    if not Path(path).exists():
        return entries
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            title = record.get("title")
            if not title:
                continue
            entries[normalize_key(title)] = record
    return entries


def load_kaikki(path: str) -> Dict[str, dict]:
    if not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries: Dict[str, dict] = {}
    for key, value in data.items():
        word = value.get("word") or key
        entries[normalize_key(word)] = value
    return entries


def extract_from_morph(item: dict) -> dict:
    present_1sg = None
    present_2sg = None
    aorist_active = None
    aorist_passive = None
    present_voice = None

    for form in item.get("finite_forms", []):
        tense = form.get("tense")
        mood = form.get("mood")
        voice = form.get("voice")
        person = form.get("person")
        number = form.get("number")
        form_text = form.get("form")
        if not form_text:
            continue

        if tense == "Pres" and mood == "Ind":
            if person == 1 and number == "Sing":
                present_1sg = form_text
                present_voice = voice
            if person == 2 and number == "Sing":
                present_2sg = form_text
        if tense == "Aor" and mood == "Ind" and voice == "Act":
            if person == 1 and number == "Sing":
                aorist_active = form_text
        if tense == "Aor" and mood == "Ind" and voice == "Pass":
            if person == 1 and number == "Sing":
                aorist_passive = form_text

    stems = {}
    if present_1sg:
        stems["imperfective"] = infer_present_stem(present_1sg)
    if aorist_active:
        stems["perfective_active"] = infer_aorist_active_stem(aorist_active)
    if aorist_passive:
        stems["perfective_passive"] = infer_aorist_passive_stem(aorist_passive)

    return {
        "present_1sg": present_1sg,
        "present_2sg": present_2sg,
        "aorist_active_1sg": aorist_active,
        "aorist_passive_1sg": aorist_passive,
        "present_voice": present_voice,
        "stems": stems,
        "aorist_type": infer_aorist_type(aorist_active) if aorist_active else None,
    }


def extract_from_wiktextract(record: dict) -> dict:
    stems = {}
    for section in record.get("verb_sections", []):
        for template in section.get("conjugation_templates", []):
            named = template.get("named", {})
            if "present" in named and not stems.get("imperfective"):
                stems["imperfective"] = named.get("present")
            if "a-simplepast" in named and not stems.get("perfective_active"):
                stems["perfective_active"] = named.get("a-simplepast")
            if "p-simplepast" in named and not stems.get("perfective_passive"):
                stems["perfective_passive"] = named.get("p-simplepast")
    return {"stems": stems}


def extract_from_kaikki(entry: dict) -> dict:
    present_1sg = None
    for form in entry.get("conjugations", []):
        if (
            form.get("tense") == "present"
            and form.get("mood") == "indicative"
            and form.get("voice") == "active"
            and form.get("person") == "1st"
            and form.get("number") == "singular"
        ):
            present_1sg = form.get("form")
            break
    stems = {}
    if present_1sg:
        stems["imperfective"] = infer_present_stem(present_1sg)
    return {"present_1sg": present_1sg, "stems": stems}


def build_lexicon(morph_path: str, wiktextract_path: str, kaikki_path: str) -> dict:
    morph = load_morph_extraction(morph_path)
    wikt = load_wiktextract(wiktextract_path)
    kaikki = load_kaikki(kaikki_path)

    lexicon: Dict[str, dict] = {}

    # 1) morph dict (primary)
    for key, item in morph.items():
        lemma = item.get("lemma")
        if not is_likely_lemma(lemma):
            continue
        extracted = extract_from_morph(item)
        if extracted.get("present_1sg") and lemma != extracted.get("present_1sg"):
            continue
        if (
            not extracted.get("stems")
            and not extracted.get("present_1sg")
            and not extracted.get("aorist_active_1sg")
            and not extracted.get("aorist_passive_1sg")
        ):
            continue
        class_id = infer_class_id(extracted.get("present_1sg"), extracted.get("present_2sg"))
        stems = {k: v for k, v in extracted.get("stems", {}).items() if v}
        lexicon[key] = {
            "lemma": lemma,
            "class_id": class_id,
            "stems": stems,
            "aorist_type": extracted.get("aorist_type"),
            "provenance": "morph_dict",
        }

    # 2) wiktextract templates (fill missing stems)
    for key, record in wikt.items():
        if not is_likely_lemma(record.get("title")):
            continue
        entry = lexicon.get(key)
        if not entry:
            entry = {
                "lemma": record.get("title"),
                "class_id": "A",
                "stems": {},
                "aorist_type": None,
                "provenance": "wiktextract",
            }
            lexicon[key] = entry

        extracted = extract_from_wiktextract(record)
        for stem_key, value in extracted.get("stems", {}).items():
            if value and not entry["stems"].get(stem_key):
                entry["stems"][stem_key] = value

    # 3) kaikki (lemma coverage)
    for key, record in kaikki.items():
        if not is_likely_lemma(record.get("word") or key):
            continue
        if key in lexicon:
            continue
        extracted = extract_from_kaikki(record)
        stems = {k: v for k, v in extracted.get("stems", {}).items() if v}
        class_id = infer_class_id(extracted.get("present_1sg"), None)
        lexicon[key] = {
            "lemma": record.get("word") or key,
            "class_id": class_id,
            "stems": stems,
            "aorist_type": None,
            "provenance": "kaikki",
        }

    return {"entries": list(lexicon.values())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build starter verb lexicon.")
    parser.add_argument("--morph", default=DEFAULT_MORPH)
    parser.add_argument("--wiktextract", default=DEFAULT_WIKT)
    parser.add_argument("--kaikki", default=DEFAULT_KAIKKI)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    lexicon = build_lexicon(args.morph, args.wiktextract, args.kaikki)
    output = {
        "schema_version": "1.0",
        "description": "Modern Greek verb lexicon (starter build).",
        "entries": lexicon["entries"],
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
