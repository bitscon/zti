#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CAST="${ROOT}/resources/demo/zti-demo.cast"
TERMINAL_MD="${ROOT}/resources/demo/terminal-output.md"
export PATH="${HOME}/.cargo/bin:${HOME}/.local/bin:${PATH}"

python3 "${ROOT}/resources/demo/generate.py" --check

if ! command -v asciinema >/dev/null 2>&1; then
  echo "verify-demo.sh requires asciinema on PATH." >&2
  exit 1
fi

TMP_TXT="$(mktemp)"
cleanup() {
  rm -f "${TMP_TXT}"
}
trap cleanup EXIT

asciinema convert --overwrite -f raw "${CAST}" "${TMP_TXT}" >/dev/null 2>&1

python3 - <<'PY' "${TERMINAL_MD}" "${TMP_TXT}"
from pathlib import Path
import re
import sys

terminal_md = Path(sys.argv[1]).read_text(encoding="utf-8")
converted = Path(sys.argv[2]).read_text(encoding="utf-8")
match = re.search(r"```text\n(.*?)\n```", terminal_md, re.DOTALL)
if match is None:
    raise SystemExit("Unable to find terminal transcript block in terminal-output.md")
expected = match.group(1).replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
ansi_re = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
actual = ansi_re.sub("", converted).replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
if actual != expected:
    raise SystemExit("asciinema text conversion does not match the canonical transcript")
PY
