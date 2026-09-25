#!/usr/bin/env bash
# setup_relay.sh — Set up the relay server environment (Debian/Ubuntu).

set -euo pipefail

echo "=== LinkBridge Relay Setup ==="

# --- Check system ---
if [[ "$(uname -s)" != "Linux" ]]; then
    echo "WARNING: This script is designed for Debian/Ubuntu Linux."
    echo "         Proceeding anyway for development purposes."
fi

# --- Python deps ---
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "ERROR: $PYTHON not found. Install Python 3.11+."
    exit 1
fi

echo "Using: $($PYTHON --version)"

# --- pip / venv ---
if ! "$PYTHON" -m venv --help >/dev/null 2>&1; then
    echo "ERROR: python3-venv not available."
    exit 1
fi

VENV="${VENV:-.venv}"
if [[ ! -d "$VENV" ]]; then
    "$PYTHON" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --upgrade pip

# --- Install project deps ---
pip install -e ".[dev]"

echo ""
echo "=== Setup complete ==="
echo "Activate with: source $VENV/bin/activate"
echo "Run relay:     uvicorn relay.gateway.main:app --host 0.0.0.0 --port 8000"
