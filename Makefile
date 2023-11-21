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
	$(EXEC_CMD) poetry run black --check --exclude=venv .
	$(EXEC_CMD) poetry run isort --check --skip-glob="**/migrations" --extend-skip-glob="venv" .
	$(EXEC_CMD) poetry run flake8 --count --show-source --statistics --exclude="venv,**/migrations" .

.PHONY: fix
fix:
	$(EXEC_CMD) poetry run black --exclude=venv .
	$(EXEC_CMD) poetry run isort --skip-glob="**/migrations" --extend-skip-glob="venv" .


.PHONY: init
init:
	$(EXEC_CMD) poetry install
	$(EXEC_CMD) poetry run pre-commit install
	$(EXEC_CMD) poetry run python manage.py migrate
	$(EXEC_CMD) poetry run python manage.py collectstatic --noinput

.PHONY: runserver
runserver:
	$(EXEC_CMD) poetry run python manage.py runserver $(HOST_URL):$(HOST_PORT)
