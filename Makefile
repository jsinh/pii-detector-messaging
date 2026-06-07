.DEFAULT_GOAL := help

.PHONY: install dev run eval test lint format docker-build docker-run help

install:  ## Install the package in editable mode with dev tools
	pip install -e ".[dev]"

dev:      ## Run the API locally with auto-reload
	fastapi dev src/pii_detector/api/app.py

run:      ## Run the API via the installed console command
	pii-detector

eval:     ## Run the evaluation on the sample dataset
	pii-eval data/eval/sample.jsonl

test:     ## Run the test suite
	pytest

lint:     ## Lint with ruff
	ruff check src tests

format:   ## Auto-format with ruff
	ruff format src tests

docker-build: ## Build the Docker image
	docker build -t pii-detector-messaging:latest .

docker-run:   ## Run the Docker image, mapping port 8000
	docker run --rm -p 8000:8000 pii-detector-messaging:latest

help:     ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
