#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <enwiktionary_dump.bz2> <out_jsonl> [num_processes]" >&2
  exit 1
fi

DUMP_PATH="$1"
OUT_PATH="$2"
NUM_PROCESSES="${3:-}"

if ! command -v wiktwords >/dev/null 2>&1; then
  echo "Error: wiktwords not found in PATH." >&2
  echo "Install wiktextract (pip -e .) or add it to PATH." >&2
  exit 1
fi

ARGS=(--all --language-name Greek --edition en --out "$OUT_PATH" "$DUMP_PATH")

if [[ -n "$NUM_PROCESSES" ]]; then
  ARGS+=(--num-processes "$NUM_PROCESSES")
fi

echo "Running: wiktwords ${ARGS[*]}" >&2
wiktwords "${ARGS[@]}"
