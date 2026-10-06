#!/bin/bash
# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Extract shadpy if it exists as a zip file
if [ -f "shadpy.zip" ]; then
    echo "Extracting shadpy.zip..."
    python -m zipfile -e shadpy.zip .
    echo "shadpy extracted successfully"
fi

echo "Build completed!"
