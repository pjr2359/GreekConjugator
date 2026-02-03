#!/usr/bin/env python3
"""
Modern Greek conjugation generator (core indicative).

Pipeline:
1) Normalize lemma
2) Lookup lexicon entry (stems)
3) Build forms (stem + endings)
4) Apply phonology layer (augment/stress/orthography)
5) Apply irregular overrides
6) Record provenance
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .greek_conjugation_classes import get_conjugation_class
from .greek_text import GreekTextProcessor


PERSON_NUMBER = [
    ("1st", "singular"),
    ("2nd", "singular"),
    ("3rd", "singular"),
    ("1st", "plural"),
    ("2nd", "plural"),
    ("3rd", "plural"),
]

VOWEL_RE = re.compile(r"^[αεηιουωάέήίόύώ]")


@dataclass
class VerbLexiconEntry:
    lemma: str
    class_id: str
    stems: Dict[str, str]
    aorist_type: Optional[str] = None
    use_augment: Optional[bool] = None
    notes: Optional[str] = None
    provenance: Optional[str] = None

    @property
    def imperfective(self) -> str:
        return self.stems.get("imperfective", "")

    @property
    def perfective_active(self) -> str:
        return self.stems.get("perfective_active", "")

    @property
    def perfective_passive(self) -> str:
        return self.stems.get("perfective_passive", "")


def normalize_lemma(text: str) -> str:
    if not text:
        return ""
    normalized = GreekTextProcessor.normalize_unicode(text).strip().lower()
    normalized = GreekTextProcessor.remove_accents(normalized)
    normalized = normalized.replace("ς", "σ")
    return normalized


def load_lexicon(path: str) -> Dict[str, VerbLexiconEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries: Dict[str, VerbLexiconEntry] = {}
    for item in data.get("entries", []):
        entry = VerbLexiconEntry(
            lemma=item.get("lemma", ""),
            class_id=item.get("class_id", ""),
            stems=item.get("stems", {}),
            aorist_type=item.get("aorist_type"),
            use_augment=item.get("use_augment"),
            notes=item.get("notes"),
            provenance=item.get("provenance"),
        )
        entries[normalize_lemma(entry.lemma)] = entry
    return entries


def load_irregulars(path: str) -> Dict[str, dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    irregulars: Dict[str, dict] = {}
    for item in data.get("entries", []):
        key = normalize_lemma(item.get("lemma", ""))
        if key:
            irregulars[key] = item
    return irregulars


def derive_stems_fallback(lemma: str) -> Dict[str, str]:
    if lemma.endswith("ομαι"):
        base = lemma[:-4]
    elif lemma.endswith("μαι"):
        base = lemma[:-3]
    elif lemma.endswith("ώ"):
        base = lemma[:-1]
    elif lemma.endswith("ω"):
        base = lemma[:-1]
    else:
        base = lemma
    return {
        "imperfective": base,
        "perfective_active": base,
        "perfective_passive": base,
    }


def apply_augment(stem: str) -> str:
    if not stem:
        return stem
    if VOWEL_RE.match(stem):
        return stem
    return f"ε{stem}"


def apply_final_sigma(text: str) -> str:
    if not text:
        return text
    return re.sub(r"σ(?=$|\s|[.,;:!?])", "ς", text)


def _adjust_aorist_ending(entry: VerbLexiconEntry, ending: str) -> str:
    if entry.aorist_type == "sigmatic" and ending.startswith("σ"):
        return ending[1:]
    return ending


def _adjust_passive_aorist_ending(stem: str, ending: str) -> str:
    if stem.endswith("τ") and ending.startswith("θη"):
        return "τη" + ending[2:]
    if stem.endswith("τ") and ending.startswith("τη"):
        return ending[1:]
    return ending


def build_forms(entry: VerbLexiconEntry) -> List[dict]:
    conjugation_class = get_conjugation_class(entry.class_id)
    stems = {
        "imperfective": entry.imperfective or "",
        "perfective_active": entry.perfective_active or "",
        "perfective_passive": entry.perfective_passive or "",
    }
    if not stems["imperfective"] or not stems["perfective_active"] or not stems["perfective_passive"]:
        fallback = derive_stems_fallback(entry.lemma)
        for key, value in fallback.items():
            stems.setdefault(key, value)

    use_augment = entry.use_augment if entry.use_augment is not None else conjugation_class.use_augment

    forms: List[dict] = []
    for tense, voices in conjugation_class.endings.items():
        for voice, endings in voices.items():
            for (person, number), ending in zip(PERSON_NUMBER, endings):
                if tense in {"present", "imperfect"}:
                    stem = stems["imperfective"]
                elif tense == "aorist":
                    stem = stems["perfective_passive"] if voice == "passive" else stems["perfective_active"]
                elif tense == "future":
                    stem = stems["perfective_passive"] if voice == "passive" else stems["perfective_active"]
                else:
                    stem = stems["imperfective"]

                adjusted_ending = ending
                if tense == "aorist" and voice == "active":
                    adjusted_ending = _adjust_aorist_ending(entry, ending)
                if tense == "aorist" and voice == "passive":
                    adjusted_ending = _adjust_passive_aorist_ending(stem, adjusted_ending)

                stem_for_form = stem
                if tense == "aorist" and voice == "passive":
                    if stem_for_form.endswith("τ") and adjusted_ending.startswith("τη"):
                        stem_for_form = stem_for_form[:-1]

                form = f"{stem_for_form}{adjusted_ending}"
                if tense in {"imperfect", "aorist"} and use_augment:
                    form = f"{apply_augment(stem_for_form)}{adjusted_ending}"
                if tense == "future":
                    form = f"θα {form}"

                form = apply_final_sigma(form)
                forms.append(
                    {
                        "tense": tense,
                        "mood": "indicative",
                        "voice": voice,
                        "person": person,
                        "number": number,
                        "form": form,
                        "morphology": {
                            "class_id": entry.class_id,
                            "stems": stems,
                            "aorist_type": entry.aorist_type,
                            "use_augment": use_augment,
                        },
                    }
                )
    return forms


def apply_irregular_overrides(forms: List[dict], irregular: dict) -> List[dict]:
    if not irregular:
        return forms

    overrides = {
        ("aorist", "active", "1st", "singular"): irregular.get("aorist_active"),
        ("aorist", "passive", "1st", "singular"): irregular.get("aorist_passive"),
    }

    for item in forms:
        key = (item["tense"], item["voice"], item["person"], item["number"])
        replacement = overrides.get(key)
        if replacement and replacement != "–" and replacement != "-":
            item["form"] = replacement
            item["morphology"]["override"] = "philologist_irregulars"
    return forms


def generate_conjugations(
    lemma: str,
    lexicon: Dict[str, VerbLexiconEntry],
    irregulars: Optional[Dict[str, dict]] = None,
) -> List[dict]:
    normalized = normalize_lemma(lemma)
    entry = lexicon.get(normalized)
    if not entry:
        entry = VerbLexiconEntry(
            lemma=lemma,
            class_id="A",
            stems=derive_stems_fallback(lemma),
            notes="fallback_lexicon",
        )
    forms = build_forms(entry)
    irregular = irregulars.get(normalized) if irregulars else None
    return apply_irregular_overrides(forms, irregular)
