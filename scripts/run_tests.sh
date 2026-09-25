#!/usr/bin/env bash
# run_tests.sh — Run the full test suite and linters.

set -euo pipefail

echo "=== LinkBridge Test Suite ==="
echo ""

echo "--- ruff ---"
ruff check .

echo ""
echo "--- mypy ---"
mypy debian relay --ignore-missing-imports

echo ""
echo "--- pytest ---"
pytest -v "$@"

echo ""
echo "=== All checks passed ==="
