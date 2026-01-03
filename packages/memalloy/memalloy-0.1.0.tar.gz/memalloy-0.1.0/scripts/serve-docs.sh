#!/bin/bash
# Simple script to serve documentation locally

set -e

echo "🌐 Starting documentation server..."
echo ""

# Check if site directory exists
if [ ! -d "site" ]; then
    echo "❌ site/ directory not found. Building documentation first..."
    make docs-build
fi

cd site

# Try different methods to serve
if command -v python3 &> /dev/null; then
    echo "✅ Using Python 3 HTTP server"
    echo "📖 Documentation available at: http://127.0.0.1:8000"
    echo "   Press Ctrl+C to stop"
    echo ""
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "✅ Using Python HTTP server"
    echo "📖 Documentation available at: http://127.0.0.1:8000"
    echo "   Press Ctrl+C to stop"
    echo ""
    python -m SimpleHTTPServer 8000
elif command -v mkdocs &> /dev/null; then
    echo "✅ Using mkdocs serve (better option)"
    cd ..
    mkdocs serve
else
    echo "❌ No suitable server found"
    echo "   Install Python or use: make docs-serve"
    exit 1
fi
