# -------------------------------
# Project meta
# -------------------------------
PROJECT	?= "adif-mcp"
PYTHON	?= python3

# Updated Paths for the Silo structure
SRC_DIR     := src/adif_mcp
SCRIPTS_DIR := scripts
TEST_DIR    := test

# Persona Variables
PERSONA ?= Primary
PROVIDERS := eqsl lotw qrz clublog

# Pull versions from pyproject.toml
PY_PROJ_VERSION := $(shell $(PYTHON) -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])" 2>/dev/null)
ADIF_SPEC_VERSION := $(shell $(PYTHON) -c "import tomllib;d=tomllib.load(open('pyproject.toml','rb'));print(d.get('tool',{}).get('adif',{}).get('spec_version','unknown'))" 2>/dev/null)

# -------------------------------
# Color Helpers
# -------------------------------
C_R='\033[01;31m'
C_G='\033[01;32m'
C_Y='\033[01;33m'
C_C='\033[01;36m'
C_NC='\033[0m'

# -------------------------------
# Environment / deps
# -------------------------------
.PHONY: bootstrap setup-dev sync add init
bootstrap: ## Ensure dev tools are installed [cite: 1, 2]
	uv sync --group dev || uv sync

setup-dev: ## Create venv, sync deps, install pre-commit hooks [cite: 2, 3]
	uv sync --group dev
	pre-commit install -t pre-commit -t commit-msg
	@echo "Dev environment ready."

sync: ## uv sync dependencies [cite: 4]
	uv sync

add: ## Add a runtime dep [cite: 5]
	@test -n "$(DEP)" || (echo "Usage: make add DEP=<package>"; exit 1)
	uv add "$(DEP)"

init: ## One-time bootstrap [cite: 6]
	$(MAKE) setup-dev
	$(MAKE) smoke-all
	@echo $(C_G)"init complete"$(C_NC)

# -------------------------------
# Quality gates
# -------------------------------
.PHONY: lint format type test smoke gate smoke-all
lint: ## Ruff lint [cite: 7]
	uv run ruff check $(SRC_DIR) $(SCRIPTS_DIR) $(TEST_DIR)

format: ## Ruff format [cite: 8]
	uv run ruff format $(SRC_DIR) $(SCRIPTS_DIR) $(TEST_DIR)

type: ## mypy check [cite: 9]
	uv run mypy $(SRC_DIR)

test: ## pytest [cite: 10]
	uv run pytest -q $(TEST_DIR)

smoke: lint type ## quick local gate (lint+type) [cite: 11]
	@echo "[smoke] OK"

smoke-all: ## Run smoke checks in a reproducible env [cite: 12, 13]
	@echo "[smoke] lint (ruff)"
	uv run ruff check $(SRC_DIR)
	@echo "[smoke] type check (mypy)"
	uv run mypy $(SRC_DIR)
	@echo "[smoke] docstrings (interrogate)"
	uv run interrogate -c pyproject.toml
	@echo "[smoke-all] OK"

gate: ## CI parity gate [cite: 11]
	$(MAKE) lint
	$(MAKE) type
	uv run interrogate -c pyproject.toml
	$(MAKE) test

# -------------------------------
# Keychain test (macOS only)
# -------------------------------
.PHONY: keychain-test
keychain-test: ## Test keychain for credentials [cite: 31, 32, 33, 34]
ifneq ($(shell uname),Darwin)
	@echo "[keychain-test] skipping (not macOS)"
else
	@set -euo pipefail; \
	echo "[keychain-test] starting..."; \
	uv run adif-mcp persona remove-all --yes; \
	uv run adif-mcp persona add --name Primary; \
	uv run adif-mcp creds set Primary lotw --username W7X --password testpw; \
	uv run adif-mcp persona list --verbose; \
	uv run adif-mcp persona remove-all --yes; \
	echo "[keychain-test] done."
endif

# -------------------------------
# Clean
# -------------------------------
.PHONY: clean clean-pyc clean-all
clean: ## Remove build artifacts [cite: 44]
	rm -rf dist build *.egg-info site/ .venv .mypy_cache .pytest_cache .ruff_cache

clean-pyc: ## Remove Python bytecode [cite: 45, 46]
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.py[co]' -delete 2>/dev/null || true

clean-all: clean clean-pyc ## Deep clean [cite: 47]

# -------------------------------
# Help
# -------------------------------
.PHONY: help
help: ## Show this help [cite: 47]
	@clear
	@echo "Silo Developer Commands: $(PROJECT)"
	@echo "--------------------------------------------------------------------------------"
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
