#!/bin/sh
# Inject Google Analytics snippet into all static HTML files after build.
# Usage: sh scripts/inject-ga.sh [out-dir]

OUT_DIR="${1:-out}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "${SCRIPT_DIR}/inject-ga.py" "${OUT_DIR}"
