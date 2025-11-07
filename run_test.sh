#!/usr/bin/env bash
# Simple test runner for the repo
set -e
python -m pip install --upgrade pip
pip install pytest flask flask_sqlalchemy
pytest -q
