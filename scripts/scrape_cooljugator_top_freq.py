#!/usr/bin/env python3
"""
Fetch Cooljugator pages for top-frequency Greek verbs.

This script downloads HTML pages for later parsing. It does not rely on
Cooljugator-specific HTML structure, which can change. It writes a JSONL
log with fetch results.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


BASE_URL = "https://cooljugator.com/gr/"
DEFAULT_FREQ = "greek-conjugator/greek_frequency_list.txt"
DEFAULT_OUT_DIR = "scripts/data/cooljugator_html"
DEFAULT_LOG = "scripts/data/cooljugator_fetch.jsonl"
DEFAULT_FORMS = "scripts/data/cooljugator_forms.jsonl"


def load_frequency_list(path: str) -> list[str]:
    words = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        words.append(line.split("\t")[0].strip())
    return words


def normalize_lemma(text: str) -> str:
    return text.strip().lower()


def load_existing_lemmas(
    forms_path: str,
    log_path: str,
    html_dir: str,
) -> set[str]:
    existing: set[str] = set()
    forms_file = Path(forms_path)
    if forms_file.exists():
        for line in forms_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            lemma = item.get("lemma", "")
            if lemma:
                existing.add(normalize_lemma(lemma))

    log_file = Path(log_path)
    if log_file.exists():
        for line in log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("status") != "ok":
                continue
            lemma = item.get("lemma", "")
            if lemma:
                existing.add(normalize_lemma(lemma))

    html_path = Path(html_dir)
    if html_path.exists():
        for path in html_path.glob("*.html"):
            existing.add(normalize_lemma(path.stem))

    return existing


def fetch_url(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": "GreekConjugator/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Cooljugator pages for top frequency verbs.")
    parser.add_argument("--freq", default=DEFAULT_FREQ, help="Path to frequency list")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Output directory for HTML files")
    parser.add_argument("--log", default=DEFAULT_LOG, help="JSONL log of fetch results")
    parser.add_argument("--limit", type=int, default=None, help="Optional max verbs to fetch")
    parser.add_argument("--max-new", type=int, default=None, help="Fetch at most N new verbs")
    parser.add_argument(
        "--require-new",
        action="store_true",
        help="Exit nonzero if fewer than --max-new new verbs were fetched",
    )
    parser.add_argument("--sleep", type=float, default=1.5, help="Seconds to sleep between requests")
    parser.add_argument("--skip-existing", action="store_true", help="Skip lemmas already fetched")
    parser.add_argument("--existing-forms", default=DEFAULT_FORMS, help="Existing forms JSONL")
    parser.add_argument("--existing-log", default=DEFAULT_LOG, help="Existing fetch log JSONL")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    words = load_frequency_list(args.freq)
    if args.limit:
        words = words[: args.limit]

    existing = set()
    if args.skip_existing:
        existing = load_existing_lemmas(args.existing_forms, args.existing_log, args.out_dir)

    fetched_new = 0
    with log_path.open("a", encoding="utf-8") as log:
        for word in words:
            if args.skip_existing and normalize_lemma(word) in existing:
                continue
            if args.max_new is not None and fetched_new >= args.max_new:
                break
            url = BASE_URL + quote(word)
            html_path = out_dir / f"{word}.html"
            status = "ok"
            error = None
            try:
                html = fetch_url(url)
                html_path.write_text(html, encoding="utf-8")
            except Exception as exc:
                status = "error"
                error = str(exc)

            log.write(
                json.dumps(
                    {
                        "lemma": word,
                        "url": url,
                        "status": status,
                        "html_path": str(html_path) if status == "ok" else None,
                        "error": error,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            if status == "ok":
                fetched_new += 1
            time.sleep(args.sleep)

    if args.max_new is not None:
        print(f"Fetched {fetched_new} new verbs (target={args.max_new}).")
        if args.require_new and fetched_new < args.max_new:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
