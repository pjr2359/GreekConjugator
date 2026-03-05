#!/usr/bin/env python3
"""
Backfill missing lexicon stems using verified conjugation forms.

Uses verified forms (trusted from Cooljugator) to infer stems by stripping
known class endings. Only fills missing stems; never overwrites existing ones.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "greek-conjugator" / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.services.greek_conjugation_classes import get_conjugation_class  # noqa: E402
from app.services.greek_conjugation_generator import normalize_lemma  # noqa: E402
from app.services.greek_text import GreekTextProcessor  # noqa: E402


PERSON_NUMBER = [
    ("1st", "singular"),
    ("2nd", "singular"),
    ("3rd", "singular"),
    ("1st", "plural"),
    ("2nd", "plural"),
    ("3rd", "plural"),
]
PERSON_INDEX = {pair: idx for idx, pair in enumerate(PERSON_NUMBER)}


def load_verified_forms(path: str) -> Dict[str, List[dict]]:
    forms_by_lemma: Dict[str, List[dict]] = defaultdict(list)
    if not Path(path).exists():
        return forms_by_lemma
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        lemma = item.get("lemma", "")
        form_key = item.get("form_key", {})
        form = item.get("form", "")
        if not lemma or not form:
            continue
        forms_by_lemma[normalize_lemma(lemma)].append(
            {
                "tense": form_key.get("tense"),
                "mood": form_key.get("mood"),
                "voice": form_key.get("voice"),
                "person": form_key.get("person"),
                "number": form_key.get("number"),
                "form": form,
            }
        )
    return forms_by_lemma


def normalize_form(text: str) -> str:
    return GreekTextProcessor.normalize_unicode(text).strip()


def strip_future_prefix(text: str) -> str:
    cleaned = normalize_form(text)
    if cleaned.startswith("θα "):
        return cleaned[3:].lstrip()
    if cleaned.startswith("θα"):
        return cleaned[2:].lstrip()
    return cleaned


def infer_stems_from_forms(
    forms: Iterable[dict],
    class_id: str,
    use_augment: bool,
) -> Dict[str, Optional[str]]:
    conjugation_class = get_conjugation_class(class_id)
    endings = conjugation_class.endings

    candidates: Dict[str, Counter[str]] = {
        "imperfective": Counter(),
        "perfective_active": Counter(),
        "perfective_passive": Counter(),
    }

    for item in forms:
        if item.get("mood") != "indicative":
            continue
        tense = item.get("tense")
        voice = item.get("voice")
        person = item.get("person")
        number = item.get("number")
        if tense not in endings or voice not in endings[tense]:
            continue
        idx = PERSON_INDEX.get((person, number))
        if idx is None:
            continue
        ending = endings[tense][voice][idx]
        form = normalize_form(item.get("form", ""))
        if not form:
            continue

        if tense == "future":
            form = strip_future_prefix(form)

        stem_targets: List[str] = []
        if form.endswith(ending):
            stem_targets.append(form[: -len(ending)] if ending else form)

        if tense in {"imperfect", "aorist"} and use_augment:
            if form.startswith("ε") and form[1:].endswith(ending):
                stem_targets.append(form[1 : -len(ending)] if ending else form[1:])

        if not stem_targets:
            continue

        if tense in {"present", "imperfect"}:
            key = "imperfective"
        elif tense == "aorist":
            key = "perfective_passive" if voice == "passive" else "perfective_active"
        elif tense == "future":
            key = "perfective_passive" if voice == "passive" else "perfective_active"
        else:
            continue

        for stem in stem_targets:
            if stem:
                candidates[key][stem] += 1

    inferred: Dict[str, Optional[str]] = {}
    for key, counter in candidates.items():
        if not counter:
            inferred[key] = None
            continue
        most_common = counter.most_common()
        best_count = most_common[0][1]
        best_candidates = [stem for stem, count in most_common if count == best_count]
        best = max(best_candidates, key=len)
        inferred[key] = best
    return inferred


def update_provenance(entry: dict, label: str) -> None:
    provenance = entry.get("provenance")
    if not provenance:
        entry["provenance"] = label
    elif label not in provenance:
        entry["provenance"] = f"{provenance}+{label}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill lexicon stems from verified forms.")
    parser.add_argument("--lexicon", default="scripts/data/verb_lexicon.json")
    parser.add_argument("--verified", default="scripts/data/verified_forms.jsonl")
    parser.add_argument("--out", default=None, help="Output lexicon path (defaults to in-place)")
    args = parser.parse_args()

    lexicon_path = Path(args.lexicon)
    data = json.loads(lexicon_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    forms_by_lemma = load_verified_forms(args.verified)

    updated = 0
    for entry in entries:
        lemma = entry.get("lemma", "")
        if not lemma:
            continue
        key = normalize_lemma(lemma)
        forms = forms_by_lemma.get(key)
        if not forms:
            continue

        class_id = entry.get("class_id") or "A"
        stems = entry.setdefault("stems", {})
        use_augment = True

        inferred = infer_stems_from_forms(forms, class_id, use_augment)
        changed = False
        for stem_key in ("imperfective", "perfective_active", "perfective_passive"):
            if stems.get(stem_key):
                continue
            candidate = inferred.get(stem_key)
            if candidate:
                stems[stem_key] = candidate
                changed = True

        if changed:
            update_provenance(entry, "cooljugator_verified")
            updated += 1

    out_path = Path(args.out) if args.out else lexicon_path
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {updated} entries with inferred stems.")


if __name__ == "__main__":
    main()
