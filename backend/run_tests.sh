#!/bin/bash
# Script to run backend tests

# Navigate to the script's directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed (httpx is required for TestClient)
echo "Installing/Updating dependencies..."
pip install -r requirements.txt
pip install httpx pytest

# Run tests
echo "Running backend tests..."
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/test_analytics.py
