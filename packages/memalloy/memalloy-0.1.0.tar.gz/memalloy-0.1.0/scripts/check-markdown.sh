#!/bin/bash
# Script to check markdown documentation files

set -e

echo "🔍 Checking markdown files..."

# Check if markdownlint is installed
if ! command -v markdownlint &> /dev/null; then
    echo "❌ markdownlint-cli not found"
    echo "   Install with: npm install -g markdownlint-cli"
    exit 1
fi

# Check if prettier is installed
if ! command -v prettier &> /dev/null; then
    echo "⚠️  prettier not found (optional)"
    echo "   Install with: npm install -g prettier"
else
    echo "✅ prettier found"
fi

# Find all markdown files
MD_FILES=$(find . -name "*.md" -not -path "./target/*" -not -path "./.git/*" -not -path "./node_modules/*")

echo ""
echo "📄 Found markdown files:"
echo "$MD_FILES" | wc -l | xargs echo "   Total files:"

echo ""
echo "🔎 Running markdownlint..."

# Run markdownlint
if markdownlint "*.md" "docs/*.md" 2>&1; then
    echo "✅ All markdown files passed linting!"
else
    echo "❌ Some markdown files have issues"
    echo "   Run 'make docs-format' to auto-fix some issues"
    exit 1
fi

echo ""
echo "✨ Markdown check complete!"
