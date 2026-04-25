#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CAST="${ROOT}/resources/demo/zti-demo.cast"
export PATH="${HOME}/.cargo/bin:${HOME}/.local/bin:${PATH}"

if ! command -v asciinema >/dev/null 2>&1; then
  echo "play-demo.sh requires asciinema on PATH." >&2
  exit 1
fi

asciinema play "${CAST}" "$@"
