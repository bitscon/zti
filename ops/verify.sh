#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="${ROOT}/dev/site/_dist"

fail() {
  echo "VERIFY FAILED: $1" >&2
  exit 1
}

[[ ! -e "${ROOT}/dev/site/_preview" ]] || fail "legacy output dev/site/_preview still exists"
[[ ! -e "${ROOT}/dev/site/_dist_prod" ]] || fail "legacy output dev/site/_dist_prod still exists"
[[ ! -e "${ROOT}/site" ]] || fail "legacy website tree site/ still exists"

python3 -m zti.demo.cli reset --profile recording
python3 "${ROOT}/dev/site/build.py" --out "${DIST}"
python3 "${ROOT}/dev/site/build.py" --check

required_paths=(
  ".htaccess"
  "index.html"
  "adopt/index.html"
  "adopt/demo/index.html"
  "adopt/request-access/index.html"
  "adopt/request-access/success/index.html"
  "core/index.html"
  "assets/site.css"
  "assets/site.js"
  "assets/demo-output.txt"
)

for rel_path in "${required_paths[@]}"; do
  [[ -f "${DIST}/${rel_path}" ]] || fail "missing required artifact file ${rel_path}"
done

if rg -n '/dev/site/|localhost|127\.0\.0\.1|barn\.workshop\.home' "${DIST}" >/dev/null; then
  fail "artifact contains local-only path or host references"
fi

python3 - <<'PY' "${ROOT}" "${DIST}"
from pathlib import Path
import sys

from zti.demo.narrative import (
    build_recording_script_markdown,
    build_script_markdown,
    build_terminal_output_markdown,
    build_terminal_output_text,
)

root = Path(sys.argv[1])
dist = Path(sys.argv[2])

checks = {
    root / "resources" / "demo" / "script.md": build_script_markdown(),
    root / "resources" / "demo" / "recording-script.md": build_recording_script_markdown(),
    root / "resources" / "demo" / "terminal-output.md": build_terminal_output_markdown(),
    dist / "assets" / "demo-output.txt": build_terminal_output_text(),
}

for path, expected in checks.items():
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        raise SystemExit(f"artifact drift detected in {path}")
PY

echo "Verification passed."
