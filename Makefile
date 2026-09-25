.PHONY: help dev-debian dev-relay test lint typecheck format android-build clean install

help:
	@echo "LinkBridge (Debian-Android Bridge)"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dev dependencies
	pip install -e ".[dev]"

dev-debian: ## Run Debian assistant core (local dev)
	uvicorn debian.api.main:app --reload --host 0.0.0.0 --port 8000

dev-relay: ## Run relay gateway (local dev)
	uvicorn relay.gateway.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run test suite
	pytest -v

lint: ## Run linters
	ruff check .

typecheck: ## Run type checker
	mypy debian relay --ignore-missing-imports

format: ## Format code
	ruff format .

android-build: ## Build Android app
	cd android && ./gradlew assembleDebug

clean: ## Clean build artifacts
	rm -rf debian/__pycache__ relay/__pycache__ tests/__pycache__ .venv build dist *.egg-info
	cd android && ./gradlew clean 2>/dev/null || true
