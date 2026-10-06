#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install jdatetime httpx

echo "Extracting shadpy..."
if [ -f "shadpy.zip" ]; then
    python3 -m zipfile -e shadpy.zip .
    echo "shadpy extracted"
else
    echo "WARNING: shadpy.zip not found!"
fi

echo "Build complete!"
