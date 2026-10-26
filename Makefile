.PHONY: help install check test lint compile deps build verify-wheel release-check

help:
	@echo "Targets: install check test lint compile deps build verify-wheel release-check"

install:
	python3 -m pip install -e ".[dev]"

deps:
	python3 scripts/check_dependencies.py

check: deps

test:
	python3 -m pytest tests/unit tests/integration -q

lint:
	python3 -m ruff check src tests

compile:
	python3 -m compileall -q src

build:
	python3 -m build

verify-wheel: build
	chmod +x scripts/verify_wheel_install.sh
	./scripts/verify_wheel_install.sh

release-check: lint compile test verify-wheel
	@echo "Release checks passed for local prep (GUI/playback still manual)."
