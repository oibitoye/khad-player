.PHONY: help install check test lint compile deps

help:
	@echo "Targets: install check test lint compile deps"

install:
	python3 -m pip install --user -e ".[dev]"

deps:
	python3 scripts/check_dependencies.py

check: deps

test:
	python3 -m pytest tests/unit tests/integration -q

lint:
	python3 -m ruff check src tests || true

compile:
	python3 -m compileall -q src
