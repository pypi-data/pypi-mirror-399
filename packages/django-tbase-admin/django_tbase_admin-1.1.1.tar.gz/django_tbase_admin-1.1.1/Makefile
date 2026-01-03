.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  install     - Install package"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code quality checks"
	@echo "  format      - Format code with black"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build package"
	@echo "  upload      - Upload to PyPI"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	flake8 src/tbase_admin/
	mypy src/tbase_admin/

format:
	black src/tbase_admin/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*