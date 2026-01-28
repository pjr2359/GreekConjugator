Wiktextract local expansion (Greek verbs)

This workflow runs Wiktextract locally to expand templates/Lua and emit
JSONL with inflection data. The `wiktwords` tool performs template expansion
and outputs structured data per word and part of speech.

Install (recommended: wiktextract from source)
1) git clone https://github.com/tatuylonen/wiktextract.git
2) cd wiktextract
3) python -m venv .venv
4) source .venv/bin/activate
5) python -m pip install -U pip
6) python -m pip install -e .

Run expansion (Greek only, English Wiktionary edition)
./scripts/run_wiktextract_en_greek.sh \
  enwiktionary-20260101-pages-articles.xml.bz2 \
  wiktextract_el.jsonl \
  4

Notes:
- `--language-name Greek` limits extraction to Greek entries.
- `--all` enables inflections and expands tables.
- Use a small `--num-processes` on limited RAM (about 4-10GB per process).

Next step: parse output JSONL for Greek verbs and their forms.
Use `scripts/parse_wiktextract_greek_verbs.py` once generated.
