#!/usr/bin/env python3
"""
Conjugation class definitions for Modern Greek (core indicative).

This module focuses on stem-based morphology and ending sets, aligned with
lexicalist analyses (e.g., Ralli's overview).
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ConjugationClass:
    class_id: str
    description: str
    endings: Dict[str, Dict[str, List[str]]]
    use_augment: bool = True


def _core_endings_group_a() -> Dict[str, Dict[str, List[str]]]:
    return {
        "present": {
            "active": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
            "passive": ["ομαι", "εσαι", "εται", "ομαστε", "εστε", "ονται"],
        },
        "imperfect": {
            "active": ["α", "ες", "ε", "αμε", "ατε", "αν"],
            "passive": ["ομουν", "οσουν", "οταν", "ομασταν", "οσασταν", "ονταν"],
        },
        "aorist": {
            "active": ["σα", "σες", "σε", "σαμε", "σατε", "σαν"],
            "passive": ["θηκα", "θηκες", "θηκε", "θηκαμε", "θηκατε", "θηκαν"],
        },
        "future": {
            "active": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
            "passive": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
        },
    }


def _core_endings_group_b1() -> Dict[str, Dict[str, List[str]]]:
    return {
        "present": {
            "active": ["ω", "ας", "α", "αμε", "ατε", "ουν"],
            "passive": ["ιεμαι", "ιεσαι", "ιεται", "ιομαστε", "ιεστε", "ιουνται"],
        },
        "imperfect": {
            "active": ["αγα", "αγες", "αγε", "αγαμε", "αγατε", "αγαν"],
            "passive": ["ιομουν", "ιοσουν", "ιοταν", "ιομασταν", "ιοσασταν", "ιονταν"],
        },
        "aorist": {
            "active": ["ησα", "ησες", "ησε", "ησαμε", "ησατε", "ησαν"],
            "passive": ["ηθηκα", "ηθηκες", "ηθηκε", "ηθηκαμε", "ηθηκατε", "ηθηκαν"],
        },
        "future": {
            "active": ["ω", "ας", "α", "αμε", "ατε", "ουν"],
            "passive": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
        },
    }


def _core_endings_group_b2() -> Dict[str, Dict[str, List[str]]]:
    return {
        "present": {
            "active": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
            "passive": ["ουμαι", "εισαι", "ειται", "ουμαστε", "ειστε", "ουνται"],
        },
        "imperfect": {
            "active": ["ουσα", "ουσες", "ουσε", "ουσαμε", "ουσατε", "ουσαν"],
            "passive": ["ουμουν", "ουσουν", "ουταν", "ουμασταν", "ουσασταν", "ουνταν"],
        },
        "aorist": {
            "active": ["ησα", "ησες", "ησε", "ησαμε", "ησατε", "ησαν"],
            "passive": ["ηθηκα", "ηθηκες", "ηθηκε", "ηθηκαμε", "ηθηκατε", "ηθηκαν"],
        },
        "future": {
            "active": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
            "passive": ["ω", "εις", "ει", "ουμε", "ετε", "ουν"],
        },
    }


CONJUGATION_CLASSES: Dict[str, ConjugationClass] = {
    "A": ConjugationClass(
        class_id="A",
        description="Group A (non‑accented -ω)",
        endings=_core_endings_group_a(),
        use_augment=True,
    ),
    "B1": ConjugationClass(
        class_id="B1",
        description="Group B1 (accented -άω/-ώ)",
        endings=_core_endings_group_b1(),
        use_augment=True,
    ),
    "B2": ConjugationClass(
        class_id="B2",
        description="Group B2 (accented -ώ with -είς)",
        endings=_core_endings_group_b2(),
        use_augment=True,
    ),
}


def get_conjugation_class(class_id: str) -> ConjugationClass:
    if class_id not in CONJUGATION_CLASSES:
        raise ValueError(f"Unknown conjugation class: {class_id}")
    return CONJUGATION_CLASSES[class_id]
