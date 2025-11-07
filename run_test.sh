#!/usr/bin/env bash

# One-click runner to install minimal deps and run tests.
# Note: This environment may not support running pytest with SQLAlchemy/app context.

set -e
python -m pip install --upgrade pip
pip install pytest flask_sqlalchemy
pytest -q
