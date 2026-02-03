#!/usr/bin/env python3
"""
Validate generated conjugations against irregular overrides.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "greek-conjugator" / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.services.greek_conjugation_generator import (  # noqa: E402
    generate_conjugations,
    load_irregulars,
    load_lexicon,
    normalize_lemma,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated conjugations.")
    parser.add_argument("--lexicon", default="scripts/data/verb_lexicon.json")
    parser.add_argument("--irregulars", default="scripts/data/philologist_irregulars.json")
    args = parser.parse_args()

    lexicon = load_lexicon(args.lexicon)
    irregulars = load_irregulars(args.irregulars) if Path(args.irregulars).exists() else {}

    mismatches = 0
    checked = 0
    for lemma in lexicon.values():
        normalized = normalize_lemma(lemma.lemma)
        irregular = irregulars.get(normalized)
        if not irregular:
            continue
        checked += 1
        forms = generate_conjugations(lemma.lemma, lexicon, irregulars)
        aorist_active_1sg = next(
            (f["form"] for f in forms if f["tense"] == "aorist" and f["voice"] == "active" and f["person"] == "1st" and f["number"] == "singular"),
            None,
        )
        if irregular.get("aorist_active") and irregular.get("aorist_active") != aorist_active_1sg:
            mismatches += 1
            print(
                f"Mismatch {lemma.lemma}: expected {irregular.get('aorist_active')} got {aorist_active_1sg}"
            )

    print(f"Checked {checked} irregulars; mismatches={mismatches}")


if __name__ == "__main__":
    main()
