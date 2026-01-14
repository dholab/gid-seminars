#!/bin/bash
# GID Seminars Aggregator Pipeline Script
# Runs the complete pipeline: collect -> generate -> upload

set -e  # Exit on error

echo "============================================="
echo "GID Seminars Aggregator - $(date)"
echo "============================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect Python environment
if command -v uv &> /dev/null; then
    echo "Using uv for Python environment"
    PYTHON_CMD="uv run python"
else
    echo "Using system Python"
    PYTHON_CMD="python3"
fi

# Run the main pipeline
$PYTHON_CMD main.py "$@"

exit_code=$?

echo ""
echo "============================================="
if [ $exit_code -eq 0 ]; then
    echo "Pipeline completed successfully!"
else
    echo "Pipeline failed with exit code $exit_code"
fi
echo "============================================="

exit $exit_code
