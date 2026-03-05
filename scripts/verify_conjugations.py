#!/usr/bin/env python3
"""
Cross-check generated conjugations against known sources.

Verification rule:
- A form is "verified" when at least two distinct sources agree on the same form.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "greek-conjugator" / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.services.greek_conjugation_generator import (  # noqa: E402
    generate_conjugations,
    load_irregulars,
    load_lexicon,
    normalize_lemma,
)
from app.services.greek_text import GreekTextProcessor  # noqa: E402

FormKey = Tuple[str, str, str, str, str]


OPTIONAL_PARENS_RE = re.compile(r"^(.*?)\(([^)]+)\)(.*)$")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_form(text: str) -> str:
    normalized = GreekTextProcessor.normalize_unicode(text).strip()
    return WHITESPACE_RE.sub(" ", normalized)


def comparable_form(text: str) -> str:
    normalized = normalize_form(text).lower()
    return GreekTextProcessor.remove_accents(normalized)


def expand_optional_parentheses(text: str) -> List[str]:
    variants = [text]
    while True:
        expanded = []
        changed = False
        for item in variants:
            match = OPTIONAL_PARENS_RE.match(item)
            if not match:
                expanded.append(item)
                continue
            changed = True
            prefix, optional, suffix = match.groups()
            expanded.append(f"{prefix}{suffix}")
            expanded.append(f"{prefix}{optional}{suffix}")
        variants = expanded
        if not changed:
            break
    return list(dict.fromkeys(variants))


def load_cooljugator_forms(path: str) -> Dict[str, dict]:
    forms: Dict[str, dict] = {}
    if not Path(path).exists():
        return forms
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            lemma = item.get("lemma", "")
            key = normalize_lemma(lemma)
            if key:
                forms[key] = item
    return forms


def collect_forms(
    bucket: Dict[FormKey, dict],
    forms: Iterable[dict],
    source: str,
    *,
    indicative_only: bool,
) -> None:
    for entry in forms:
        if indicative_only and entry.get("mood") != "indicative":
            continue
        key = (
            entry.get("tense", ""),
            entry.get("mood", ""),
            entry.get("voice", ""),
            entry.get("person", ""),
            entry.get("number", ""),
        )
        if key not in bucket:
            bucket[key] = {
                "sources": defaultdict(set),
                "comparables": defaultdict(set),
                "examples": {},
                "examples_by_source": defaultdict(dict),
                "generated": None,
            }
        form_text = entry.get("form", "")
        bucket[key]["sources"][source].add(form_text)
        if source == "generated" and not bucket[key]["generated"]:
            bucket[key]["generated"] = form_text
        for variant in expand_optional_parentheses(form_text):
            comp = comparable_form(variant)
            bucket[key]["comparables"][comp].add(source)
            bucket[key]["examples"].setdefault(comp, variant)
            bucket[key]["examples_by_source"][source].setdefault(comp, variant)


def select_verification(
    comparables: Dict[str, Set[str]]
) -> Tuple[bool, Optional[str], List[str]]:
    best_comp = None
    best_sources: List[str] = []
    for comp, sources in comparables.items():
        if len(sources) >= 2:
            if len(sources) > len(best_sources):
                best_sources = sorted(sources)
                best_comp = comp
    return bool(best_sources), best_comp, best_sources


def select_cooljugator_verification(
    comparables: Dict[str, Set[str]]
) -> Tuple[bool, Optional[str], List[str]]:
    for comp, sources in comparables.items():
        if "cooljugator" in sources:
            return True, comp, ["cooljugator"]
    return False, None, []


def select_display_form(
    comp: Optional[str],
    examples_by_source: Dict[str, Dict[str, str]],
    fallback_examples: Dict[str, str],
    preferred_sources: List[str],
) -> Optional[str]:
    if not comp:
        return None
    for source in preferred_sources:
        form = examples_by_source.get(source, {}).get(comp)
        if form:
            return form
    return fallback_examples.get(comp)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify conjugations using multiple sources.")
    parser.add_argument("--lexicon", default="scripts/data/verb_lexicon.json")
    parser.add_argument("--irregulars", default="scripts/data/philologist_irregulars.json")
    parser.add_argument("--cooljugator", default="scripts/data/cooljugator_forms.jsonl")
    parser.add_argument("--out", default="scripts/data/verification_report.jsonl")
    parser.add_argument("--verified-out", default="scripts/data/verified_forms.jsonl")
    parser.add_argument("--include-cooljugator-lemmas", action="store_true")
    parser.add_argument("--all-moods", action="store_true")
    args = parser.parse_args()

    lexicon = load_lexicon(args.lexicon)
    irregulars = load_irregulars(args.irregulars) if Path(args.irregulars).exists() else {}
    cooljugator = load_cooljugator_forms(args.cooljugator)

    lemma_keys = set(lexicon.keys())
    if args.include_cooljugator_lemmas:
        lemma_keys.update(cooljugator.keys())

    report_path = Path(args.out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    verified_path = Path(args.verified_out)
    verified_path.parent.mkdir(parents=True, exist_ok=True)

    totals = defaultdict(int)
    with report_path.open("w", encoding="utf-8") as report_handle, verified_path.open(
        "w", encoding="utf-8"
    ) as verified_handle:
        for lemma_key in sorted(lemma_keys):
            entry = lexicon.get(lemma_key)
            lemma = entry.lemma if entry else cooljugator.get(lemma_key, {}).get("lemma", lemma_key)

            forms_bucket: Dict[FormKey, dict] = {}
            generated_forms = generate_conjugations(lemma, lexicon, irregulars)
            collect_forms(
                forms_bucket,
                generated_forms,
                "generated",
                indicative_only=not args.all_moods,
            )

            cooljugator_entry = cooljugator.get(lemma_key)
            if cooljugator_entry:
                collect_forms(
                    forms_bucket,
                    cooljugator_entry.get("forms", []),
                    "cooljugator",
                    indicative_only=not args.all_moods,
                )

            for key, data in forms_bucket.items():
                totals["forms_total"] += 1
                sources_present = sorted(data["sources"].keys())
                has_other_sources = any(source != "generated" for source in sources_present)

                if "cooljugator" in sources_present:
                    verified, best_comp, supporting_sources = select_cooljugator_verification(
                        data["comparables"]
                    )
                else:
                    verified, best_comp, supporting_sources = select_verification(
                        data["comparables"]
                    )
                if verified:
                    totals["forms_verified"] += 1
                    verified_handle.write(
                        json.dumps(
                            {
                                "lemma": lemma,
                                "form_key": {
                                    "tense": key[0],
                                    "mood": key[1],
                                    "voice": key[2],
                                    "person": key[3],
                                    "number": key[4],
                                },
                                "form": select_display_form(
                                    best_comp,
                                    data["examples_by_source"],
                                    data["examples"],
                                    ["cooljugator", "generated"],
                                ),
                                "supporting_sources": supporting_sources,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                generated_form = data.get("generated")
                generated_match = any(
                    "generated" in sources and len(sources) >= 2
                    for sources in data["comparables"].values()
                )
                missing_generated = not generated_form and has_other_sources
                mismatch = bool(generated_form and has_other_sources and not generated_match)

                if missing_generated:
                    totals["missing_generated"] += 1
                if mismatch:
                    totals["mismatches"] += 1

                report_handle.write(
                    json.dumps(
                        {
                            "lemma": lemma,
                            "form_key": {
                                "tense": key[0],
                                "mood": key[1],
                                "voice": key[2],
                                "person": key[3],
                                "number": key[4],
                            },
                            "generated": generated_form,
                            "sources": {k: sorted(v) for k, v in data["sources"].items()},
                            "verified": verified,
                            "verified_form": (
                                select_display_form(
                                    best_comp,
                                    data["examples_by_source"],
                                    data["examples"],
                                    ["cooljugator", "generated"],
                                )
                                if verified
                                else None
                            ),
                            "supporting_sources": supporting_sources,
                            "mismatch": mismatch,
                            "missing_generated": missing_generated,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    print(
        "Verification summary:",
        f"total={totals['forms_total']}",
        f"verified={totals['forms_verified']}",
        f"mismatches={totals['mismatches']}",
        f"missing_generated={totals['missing_generated']}",
    )


if __name__ == "__main__":
    main()
