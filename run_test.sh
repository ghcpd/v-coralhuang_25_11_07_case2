#!/usr/bin/env bash
set -euo pipefail

# Install deps and run tests
python -m pip install -U pip
python -m pip install -r requirements.txt || true
pytest -q
