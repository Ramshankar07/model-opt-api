#!/bin/bash
set -e

echo "Setting up Federated API locally..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11 or later"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
python3 -m venv venv

echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo "Step 3: Upgrading pip..."
python -m pip install --upgrade pip

echo "Step 4: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the server:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run: python run_local.py"
echo ""
echo "Or set API key and run:"
echo "  export FEDERATED_API_KEY=your-secret-key"
echo "  python run_local.py"
echo ""

