# Loading environment variables
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

ifeq ($(USE_DOCKER),1)
	EXEC_CMD := docker-compose exec -ti web
else
	EXEC_CMD :=
endif

.PHONY: web-prompt
web-prompt:
	$(EXEC_CMD) bash

.PHONY: test-unit
test-unit:
	$(EXEC_CMD) poetry run python manage.py test --settings config.settings_test

.PHONY: test-e2e
test-e2e:
	$(EXEC_CMD) poetry run python manage.py behave --settings config.settings_test

.PHONY: test
test: test-e2e test-unit

.PHONY: quality
quality:
	$(EXEC_CMD) black --check --exclude=venv .
	$(EXEC_CMD) isort --check --skip-glob="**/migrations" --extend-skip-glob="venv" .
	$(EXEC_CMD) flake8 --count --show-source --statistics --exclude=venv .

.PHONY: fix
fix:
	$(EXEC_CMD) black --exclude=venv .
	$(EXEC_CMD) isort --skip-glob="**/migrations" --extend-skip-glob="venv" .

runserver:
	$(EXEC_CMD) poetry run python manage.py runserver $(HOST_URL):$(HOST_PORT)
