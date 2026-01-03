#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation complete."
echo "To run the app: source venv/Scripts/activate && python main.py"
