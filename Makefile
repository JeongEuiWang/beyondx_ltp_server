POETRY_VERSION=2.1.1

.PHONY: clean
clean:
	rm -r -f .pytest_cache
	rm -f .coverage

.PHONY: build
build:
	python3 -m poetry install

.PHONY: package
package:
	python3 -m poetry build --format=wheel

.PHONY: pre 
pre:
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


.PHONY: ci
ci: clean build package


.PHONY: test 
test:
	pytest -q

.PHONY: help
help: 
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?
