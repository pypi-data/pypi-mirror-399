#!/bin/bash
# Script to format markdown documentation files

set -e

echo "🎨 Formatting markdown files..."

# Check if prettier is installed
if ! command -v prettier &> /dev/null; then
    echo "❌ prettier not found"
    echo "   Install with: npm install -g prettier"
    exit 1
fi

# Find all markdown files
MD_FILES=$(find . -name "*.md" -not -path "./target/*" -not -path "./.git/*" -not -path "./node_modules/*")

echo ""
echo "📄 Formatting markdown files..."

# Format with prettier
prettier --write "*.md" "docs/*.md" 2>&1 || {
    echo "⚠️  Some files couldn't be formatted automatically"
}

echo ""
echo "✨ Markdown formatting complete!"
