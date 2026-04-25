#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="${ROOT}/dev/site/_dist"
ENV_FILE="${ROOT}/ops/deploy.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy ops/deploy.env.example to ops/deploy.env and fill in your barn-local deploy settings." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${ENV_FILE}"

: "${DEPLOY_SSH_TARGET:?Set DEPLOY_SSH_TARGET in ops/deploy.env}"
: "${DEPLOY_DOCROOT:?Set DEPLOY_DOCROOT in ops/deploy.env}"

"${ROOT}/ops/verify.sh"

ARCHIVE="$(mktemp "${TMPDIR:-/tmp}/zti-site.XXXXXX.tar.gz")"
cleanup_local() {
  rm -f "${ARCHIVE}"
}
trap cleanup_local EXIT

tar -C "${DIST}" -czf "${ARCHIVE}" .
REMOTE_TMP="$(ssh "${DEPLOY_SSH_TARGET}" 'mktemp -d /tmp/zti-site.XXXXXX')"

cleanup_remote() {
  ssh "${DEPLOY_SSH_TARGET}" "rm -rf '${REMOTE_TMP}'" >/dev/null 2>&1 || true
}
trap 'cleanup_remote; cleanup_local' EXIT

scp "${ARCHIVE}" "${DEPLOY_SSH_TARGET}:${REMOTE_TMP}/site.tar.gz"
ssh "${DEPLOY_SSH_TARGET}" DEPLOY_DOCROOT="${DEPLOY_DOCROOT}" REMOTE_TMP="${REMOTE_TMP}" 'bash -s' <<'EOF_REMOTE'
set -euo pipefail
mkdir -p "${DEPLOY_DOCROOT}" "${REMOTE_TMP}/extracted"
tar -xzf "${REMOTE_TMP}/site.tar.gz" -C "${REMOTE_TMP}/extracted"
find "${DEPLOY_DOCROOT}" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
cp -a "${REMOTE_TMP}/extracted"/. "${DEPLOY_DOCROOT}/"
rm -rf "${REMOTE_TMP}"
EOF_REMOTE

echo "Deployment complete."
