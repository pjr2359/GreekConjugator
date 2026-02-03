#!/usr/bin/env python3
"""
Scrape irregular verb table from philologist-ina.gr into JSON.
"""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional
from urllib.request import Request, urlopen


SOURCE_URL = "https://philologist-ina.gr/%ce%ba%ce%bb%ce%af%cf%83%ce%b7-%cf%81%ce%b7%ce%bc%ce%ac%cf%84%cf%89%ce%bd/"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row: List[str] = []
        self.rows: List[List[str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.current_row = []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            self.in_table = False
        elif tag == "tr":
            if self.in_row and self.current_row:
                self.rows.append(self.current_row)
            self.in_row = False
        elif tag in {"td", "th"}:
            self.in_cell = False

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            text = data.strip()
            if text:
                self.current_row.append(text)


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "GreekConjugator/1.0"})
    with urlopen(request, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_irregular_table(html: str) -> List[List[str]]:
    parser = TableParser()
    parser.feed(html)

    for idx, row in enumerate(parser.rows):
        if len(row) >= 4 and row[0].lower().startswith("ενεστώ"):
            return parser.rows[idx + 1 :]
    return []


def normalize_row(row: List[str]) -> Optional[dict]:
    if len(row) < 4:
        return None
    return {
        "lemma": row[0],
        "aorist_active": row[1],
        "aorist_passive": row[2],
        "participle": row[3],
        "source": SOURCE_URL,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Philologist irregular verbs table.")
    parser.add_argument("--out", default="scripts/data/philologist_irregulars.json")
    args = parser.parse_args()

    html = fetch_html(SOURCE_URL)
    rows = extract_irregular_table(html)
    entries = []
    for row in rows:
        item = normalize_row(row)
        if item:
            entries.append(item)

    payload = {
        "schema_version": "1.0",
        "source": SOURCE_URL,
        "entries": entries,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
