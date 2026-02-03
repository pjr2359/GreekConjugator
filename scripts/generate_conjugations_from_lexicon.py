#!/usr/bin/env python3
"""
Generate core indicative conjugations from a lexicon JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "greek-conjugator" / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.services.greek_conjugation_generator import (  # noqa: E402
    generate_conjugations,
    load_irregulars,
    load_lexicon,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate conjugations from lexicon JSON.")
    parser.add_argument("--lexicon", default="scripts/data/verb_lexicon.json")
    parser.add_argument("--irregulars", default="scripts/data/philologist_irregulars.json")
    parser.add_argument("--out", default="scripts/data/generated_conjugations.jsonl")
    args = parser.parse_args()

    lexicon = load_lexicon(args.lexicon)
    irregulars = load_irregulars(args.irregulars) if Path(args.irregulars).exists() else {}

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as handle:
        for entry in lexicon.values():
            forms = generate_conjugations(entry.lemma, lexicon, irregulars)
            for form in forms:
                handle.write(json.dumps(form, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
