#!/bin/bash

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is required but not installed."
    echo "Install it with: brew install ffmpeg (Mac) or apt install ffmpeg (Linux)"
    exit 1
fi

# Start the converter
echo "Starting Web Media Converter..."
echo "Opening browser at http://127.0.0.1:8080"
python3 converter.py