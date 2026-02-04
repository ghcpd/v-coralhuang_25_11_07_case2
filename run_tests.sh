#!/bin/bash
# Bash test runner script for Flask SearchableMixin tests
# Usage: ./run_tests.sh [--coverage] [--verbose]

set -e

COVERAGE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "================================================"
echo "Flask SearchableMixin Test Runner"
echo "================================================"
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q flask flask-sqlalchemy pytest

# Run tests
echo ""
echo "Running tests..."
echo "================================================"
echo ""

if [ "$COVERAGE" = true ]; then
    echo "Installing coverage tools..."
    pip install -q pytest-cov
    
    echo "Running tests with coverage..."
    pytest test_search_empty.py -v --cov=models --cov-report=term-missing
else
    if [ "$VERBOSE" = true ]; then
        pytest test_search_empty.py -v --tb=short
    else
        pytest test_search_empty.py -v --tb=line
    fi
fi

TEST_EXIT_CODE=$?

echo ""
echo "================================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Tests failed with exit code: $TEST_EXIT_CODE"
fi

echo "================================================"

exit $TEST_EXIT_CODE
