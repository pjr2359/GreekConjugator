#!/usr/bin/env python3
"""
Import verified Cooljugator conjugations into the SQLite database.

This loads only lemmas that have full indicative + imperative coverage
from scripts/data/cooljugator_forms.jsonl and inserts them into the
verbs/conjugations tables.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple


PERSON_NUMBER = [
    ("1st", "singular"),
    ("2nd", "singular"),
    ("3rd", "singular"),
    ("1st", "plural"),
    ("2nd", "plural"),
    ("3rd", "plural"),
]


def expected_indicative_keys() -> Set[Tuple[str, str, str, str, str]]:
    keys = set()
    for tense in ["present", "imperfect", "aorist", "future"]:
        for person, number in PERSON_NUMBER:
            keys.add((tense, "indicative", "active", person, number))
    return keys


def expected_imperative_keys() -> Set[Tuple[str, str, str, str, str]]:
    keys = set()
    for tense in ["present", "aorist"]:
        for person, number in [("2nd", "singular"), ("1st", "plural")]:
            keys.add((tense, "imperative", "active", person, number))
    return keys


def load_cooljugator_forms(path: str) -> Dict[str, List[dict]]:
    by_lemma: Dict[str, List[dict]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        lemma = item.get("lemma")
        if not lemma:
            continue
        by_lemma[lemma] = item.get("forms", [])
    return by_lemma


def connect_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(conn: sqlite3.Connection) -> None:
    # Tables should already exist via app setup; fail loudly if not.
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verbs'")
    if not cursor.fetchone():
        raise RuntimeError("Table 'verbs' not found. Run backend setup first.")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conjugations'")
    if not cursor.fetchone():
        raise RuntimeError("Table 'conjugations' not found. Run backend setup first.")


def upsert_verb(cursor: sqlite3.Cursor, lemma: str) -> int:
    cursor.execute("SELECT id FROM verbs WHERE infinitive = ?", (lemma,))
    row = cursor.fetchone()
    if row:
        return row["id"]
    cursor.execute(
        """
        INSERT INTO verbs (infinitive, english, frequency, difficulty, verb_group, transitivity, tags, audio_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (lemma, f"to {lemma}", None, 3, None, None, None, None),
    )
    return cursor.lastrowid


def conjugation_exists(
    cursor: sqlite3.Cursor,
    verb_id: int,
    tense: str,
    mood: str,
    voice: str,
    person: str | None,
    number: str | None,
    form: str,
) -> bool:
    cursor.execute(
        """
        SELECT id FROM conjugations
        WHERE verb_id = ? AND tense = ? AND mood = ? AND voice = ?
          AND person IS ? AND number IS ? AND form = ?
        """,
        (verb_id, tense, mood, voice, person, number, form),
    )
    return cursor.fetchone() is not None


def insert_conjugation(cursor: sqlite3.Cursor, verb_id: int, data: dict) -> None:
    cursor.execute(
        """
        INSERT INTO conjugations (verb_id, tense, mood, voice, person, number, form, audio_url, stress_pattern, morphology)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            verb_id,
            data.get("tense"),
            data.get("mood"),
            data.get("voice"),
            data.get("person"),
            data.get("number"),
            data.get("form"),
            None,
            None,
            None,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import verified Cooljugator conjugations.")
    parser.add_argument(
        "--db",
        default="greek_conjugator_dev.db",
        help="Path to SQLite database (run from backend/)",
    )
    parser.add_argument(
        "--cooljugator",
        default="../scripts/data/cooljugator_forms.jsonl",
        help="Cooljugator forms JSONL",
    )
    args = parser.parse_args()

    expected_ind = expected_indicative_keys()
    expected_imp = expected_imperative_keys()

    forms_by_lemma = load_cooljugator_forms(args.cooljugator)
    eligible: Dict[str, List[dict]] = {}

    for lemma, forms in forms_by_lemma.items():
        keys = {
            (f.get("tense"), f.get("mood"), f.get("voice"), f.get("person"), f.get("number"))
            for f in forms
        }
        if expected_ind.issubset(keys) and expected_imp.issubset(keys):
            eligible[lemma] = forms

    conn = connect_db(args.db)
    ensure_tables(conn)
    cursor = conn.cursor()

    verbs_added = 0
    conjugations_added = 0
    for lemma, forms in eligible.items():
        verb_id = upsert_verb(cursor, lemma)
        if verb_id:
            verbs_added += 1
        for form in forms:
            if conjugation_exists(
                cursor,
                verb_id,
                form.get("tense"),
                form.get("mood"),
                form.get("voice"),
                form.get("person"),
                form.get("number"),
                form.get("form"),
            ):
                continue
            insert_conjugation(cursor, verb_id, form)
            conjugations_added += 1

    conn.commit()
    conn.close()

    print(
        f"Imported {len(eligible)} verbs with full conjugations; "
        f"added {verbs_added} verbs and {conjugations_added} conjugations."
    )


if __name__ == "__main__":
    main()
