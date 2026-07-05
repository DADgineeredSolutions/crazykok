#!/bin/sh

set -eu

baseline=${1:-}
candidate=${2:-/tmp/crazykok-openapi.json}
baseline_path=docs/api/openapi/openapi.json
temporary_baseline=

if ! command -v oasdiff >/dev/null 2>&1; then
  echo "oasdiff 1.21.0 is required: https://github.com/oasdiff/oasdiff/releases/tag/v1.21.0" >&2
  exit 2
fi

case "$(oasdiff --version)" in
  *"1.21.0"*) ;;
  *) echo "oasdiff 1.21.0 is required; found $(oasdiff --version)" >&2; exit 2 ;;
esac

if [ -z "$baseline" ]; then
  if git cat-file -e "HEAD:$baseline_path" 2>/dev/null; then
    temporary_baseline=$(mktemp "${TMPDIR:-/tmp}/crazykok-openapi-base.XXXXXX")
    trap 'rm -f "$temporary_baseline"' EXIT
    git show "HEAD:$baseline_path" > "$temporary_baseline"
    baseline=$temporary_baseline
  else
    baseline=$baseline_path
  fi
fi

python3 scripts/export_openapi.py --output "$candidate"
oasdiff breaking "$baseline" "$candidate" --fail-on ERR
