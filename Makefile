.PHONY: help up down logs ps test test-backend test-frontend lint lint-backend lint-frontend fmt fmt-backend fmt-frontend migrate shell-backend shell-db

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Build and start all services
	docker compose up --build

down: ## Stop all services (preserves volumes)
	docker compose down

logs: ## Tail logs for all services
	docker compose logs -f

ps: ## List running services
	docker compose ps

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	docker compose run --rm backend pytest

test-frontend: ## Run frontend tests
	docker compose run --rm frontend npm test

lint: lint-backend lint-frontend ## Run all linters

lint-backend:
	docker compose run --rm backend ruff check app tests
	docker compose run --rm backend mypy app

lint-frontend:
	docker compose run --rm frontend npm run lint
	docker compose run --rm frontend npm run typecheck

fmt: fmt-backend fmt-frontend ## Format all code

fmt-backend:
	docker compose run --rm backend ruff format app tests

fmt-frontend:
	docker compose run --rm frontend npm run fmt

migrate: ## Create an alembic migration: make migrate m="add products"
	docker compose run --rm backend alembic revision --autogenerate -m "$(m)"

migrate-up: ## Apply migrations
	docker compose run --rm backend alembic upgrade head

shell-backend: ## Open a shell in the backend container
	docker compose run --rm backend bash

shell-db: ## Open psql in the postgres container
	docker compose exec postgres psql -U $${POSTGRES_USER:-app} -d $${POSTGRES_DB:-inventory}
