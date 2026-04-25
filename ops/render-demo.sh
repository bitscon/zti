#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CAST="${ROOT}/resources/demo/zti-demo.cast"
BUILD_DIR="${ROOT}/resources/demo/build"
GIF_OUTPUT="${BUILD_DIR}/zti-demo.gif"
MP4_OUTPUT="${BUILD_DIR}/zti-demo.mp4"
export PATH="${HOME}/.cargo/bin:${HOME}/.local/bin:${PATH}"

if ! command -v agg >/dev/null 2>&1; then
  echo "render-demo.sh requires agg on PATH." >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "render-demo.sh requires ffmpeg on PATH to produce MP4 output from the source-built agg GIF renderer." >&2
  exit 1
fi

mkdir -p "${BUILD_DIR}"
rm -f "${GIF_OUTPUT}" "${MP4_OUTPUT}"

agg "${CAST}" "${GIF_OUTPUT}"
ffmpeg -y -i "${GIF_OUTPUT}" -movflags +faststart -pix_fmt yuv420p "${MP4_OUTPUT}" >/dev/null 2>&1
