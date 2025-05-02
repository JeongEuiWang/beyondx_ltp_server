POETRY_VERSION=2.1.1

.PHONY: clean
clean: ## Remove all caches and other files:
	rm -r -f .pytest_cache
	rm -f .coverage

.PHONY: build
build: ## Create vevn 
	python3 -m poetry install

.PHONY: package
package: ## Create whl packages
	python3 -m poetry build --format=wheel

.PHONY: pre 
pre: ## Installs or upgrades environment dependencies like Poetry
	python3 -m pip install poetry==$(POETRY_VERSION) setuptools

.PHONY: dev prod
dev: 
	ENV=dev poetry run uvicorn --host=localhost --port=8000 app.main:app

prod: 
	ENV=prod poetry run uvicorn --host=0.0.0.0 --port=8000 app.main:app

.PHONY: migration-dev migration-prod
migration-dev: 
	ENV=dev poetry run alembic upgrade head

migration-prod: 
	ENV=prod poetry run alembic upgrade head

.PHONY: reset-dev reset-prod
reset-dev: 
	ENV=dev poetry run alembic downgrade base

reset-prod: 
	ENV=prod poetry run alembic downgrade base

## Ryns clean, build, and package
.PHONY: ci
ci: clean build package

# Run tests
.PHONY: test 
test:
	pytest -q

.PHONY: help ## Prints help for targets with comments
help: 
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
