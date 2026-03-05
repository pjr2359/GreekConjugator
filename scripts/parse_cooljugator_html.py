#!/usr/bin/env python3
"""
Parse Cooljugator HTML pages and extract conjugation forms.

This parser relies on data-default attributes used in Cooljugator's
conjugation cells and ids like present2, future1, pastperfect3, etc.
"""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List


CELL_ID_MAP = {
    "infinitive": ("present", "indicative"),
    "present": ("present", "indicative"),
    "future": ("future", "indicative"),
    "pastperfect": ("aorist", "indicative"),
    "pastimperfect": ("imperfect", "indicative"),
    "commandimperfect": ("present", "imperative"),
    "commandperfect": ("aorist", "imperative"),
}

PERSON_NUMBER = {
    "0": ("1st", "singular"),
    "1": ("1st", "singular"),
    "2": ("2nd", "singular"),
    "3": ("3rd", "singular"),
    "4": ("1st", "plural"),
    "5": ("2nd", "plural"),
    "6": ("3rd", "plural"),
}


class CooljugatorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_mainform = False
        self.lemma = None
        self.forms: List[dict] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "h1" and attrs_dict.get("id") == "mainform":
            self.in_mainform = True
        if tag == "div" and "data-default" in attrs_dict and "id" in attrs_dict:
            cell_id = attrs_dict["id"]
            data_default = attrs_dict["data-default"].strip()
            if not data_default:
                return
            match = re.match(r"([a-z]+)(\d+)$", cell_id)
            if not match:
                return
            kind, slot = match.groups()
            if kind not in CELL_ID_MAP:
                return
            tense, mood = CELL_ID_MAP[kind]
            person, number = PERSON_NUMBER.get(slot, (None, None))
            self.forms.append(
                {
                    "form": data_default,
                    "tense": tense,
                    "mood": mood,
                    "voice": "active",
                    "person": person,
                    "number": number,
                }
            )

    def handle_endtag(self, tag):
        if tag == "h1" and self.in_mainform:
            self.in_mainform = False

    def handle_data(self, data):
        if self.in_mainform:
            text = data.strip()
            if text:
                self.lemma = text


def parse_html(path: Path) -> dict:
    parser = CooljugatorParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return {
        "lemma": parser.lemma or path.stem,
        "forms": parser.forms,
        "source": "cooljugator",
        "html_path": str(path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Cooljugator HTML pages.")
    parser.add_argument("--in-dir", required=True, help="Directory containing HTML files")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    args = parser.parse_args()

    in_dir = Path(args.in_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as out:
        for path in sorted(in_dir.glob("*.html")):
            record = parse_html(path)
            if not record["forms"]:
                continue
            out.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
