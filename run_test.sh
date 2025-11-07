#!/usr/bin/env bash
set -euo pipefail
python -m pip install -U pip
pip install -r requirements.txt
pytest -q
