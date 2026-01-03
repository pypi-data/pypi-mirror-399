.PHONY: help build develop install test clean format lint docs docs-check docs-format docs-lint docs-serve

help:
	@echo "memalloy - Rust-based Local RAG Kernel"
	@echo ""
	@echo "Available commands:"
	@echo "  make develop      - Build and install in development mode"
	@echo "  make build        - Build release wheels"
	@echo "  make install      - Install from built wheels"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code"
	@echo "  make lint         - Lint code"
	@echo "  make docs         - Check and format all markdown docs"
	@echo "  make docs-check    - Check markdown files for issues"
	@echo "  make docs-format   - Format markdown files"
	@echo "  make docs-lint     - Lint markdown files"
	@echo "  make docs-build    - Build HTML documentation (generates index.html)"
	@echo "  make docs-serve    - Serve docs locally (requires mkdocs)"
	@echo "  make docs-setup    - Set up mkdocs for HTML generation"
	@echo "  make clean         - Clean build artifacts"

develop:
	maturin develop --release

build:
	maturin build --release

install:
	pip install target/wheels/memalloy-*.whl

test:
	pytest tests/

format:
	black python/
	cargo fmt

lint:
	ruff check python/
	cargo clippy

# Markdown documentation commands
docs: docs-check docs-format

docs-check:
	@echo "Checking markdown files..."
	@which markdownlint > /dev/null 2>&1 || (echo "markdownlint-cli not found. Install with: npm install -g markdownlint-cli" && exit 1)
	markdownlint "*.md" "docs/*.md" || true

docs-format:
	@echo "Formatting markdown files..."
	@which prettier > /dev/null 2>&1 || (echo "prettier not found. Install with: npm install -g prettier" && exit 1)
	prettier --write "*.md" "docs/*.md" || true

docs-lint: docs-check
	@echo "Linting markdown files complete"

docs-build:
	@echo "Building HTML documentation..."
	@which mkdocs > /dev/null 2>&1 || (echo "mkdocs not found. Install with: pip install mkdocs mkdocs-material" && exit 1)
	@if [ ! -f mkdocs.yml ]; then echo "mkdocs.yml not found. Run 'make docs-setup' first." && exit 1; fi
	@if [ ! -f docs_site/index.md ]; then cp README.md docs_site/index.md; fi
	mkdocs build
	@echo "✅ Documentation built! HTML files are in site/ directory"
	@echo ""
	@echo "⚠️  IMPORTANT: Buttons/navigation won't work if you open HTML files directly!"
	@echo "   Use 'make docs-serve' to view documentation properly"
	@echo "   Or use: cd site && python3 -m http.server 8000"

docs-serve:
	@echo "Serving documentation at http://127.0.0.1:8000..."
	@which mkdocs > /dev/null 2>&1 || (echo "mkdocs not found. Install with: pip install mkdocs mkdocs-material" && exit 1)
	@if [ ! -f mkdocs.yml ]; then echo "mkdocs.yml not found. Run 'make docs-setup' first." && exit 1; fi
	@if [ ! -f docs_site/index.md ]; then cp README.md docs_site/index.md; fi
	mkdocs serve

docs-setup:
	@echo "Setting up mkdocs..."
	@which mkdocs > /dev/null 2>&1 || pip install mkdocs mkdocs-material
	@mkdir -p docs_site
	@if [ ! -f docs_site/index.md ]; then cp README.md docs_site/index.md; fi
	@echo "✅ mkdocs setup complete!"
	@echo "   Run 'make docs-build' to generate HTML"
	@echo "   Run 'make docs-serve' to preview locally"

clean:
	rm -rf target/
	rm -rf dist/
	rm -rf build/
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
