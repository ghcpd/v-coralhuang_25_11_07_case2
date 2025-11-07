#!/usr/bin/env pwsh
# Simple test runner for PowerShell on Windows
python -m pip install --upgrade pip ; \
pip install pytest flask_sqlalchemy flask ; \
pytest -q
