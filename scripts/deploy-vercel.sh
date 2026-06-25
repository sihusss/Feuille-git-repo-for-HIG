#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TARGET="${1:-production}"
shift || true

case "$TARGET" in
  production|prod)
    VERCEL_ARGS=(deploy --prod --yes)
    TARGET_LABEL="production"
    ;;
  preview)
    VERCEL_ARGS=(deploy --yes)
    TARGET_LABEL="preview"
    ;;
  *)
    echo "Usage: $0 [production|preview] [extra vercel args...]" >&2
    exit 2
    ;;
esac

if [ ! -f ".vercel/project.json" ]; then
  echo "Vercel project is not linked. Run: npx vercel@latest link" >&2
  exit 1
fi

run_vercel() {
  if [ -x "node_modules/.bin/vercel" ]; then
    node_modules/.bin/vercel "$@"
  elif command -v vercel >/dev/null 2>&1; then
    vercel "$@"
  else
    npx --yes vercel@latest "$@"
  fi
}

echo "Checking types..."
npm run lint

echo "Building locally..."
npm run build

echo "Deploying to Vercel (${TARGET_LABEL})..."
run_vercel "${VERCEL_ARGS[@]}" "$@"
