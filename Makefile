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
	$(EXEC_CMD) pipenv run python manage.py test --settings config.settings_test

.PHONY: collectstatic
collectstatic:
	$(EXEC_CMD) pipenv run python manage.py collectstatic --noinput --ignore=*.sass


.PHONY: messages
messages:
	$(EXEC_CMD) pipenv run django-admin makemessages -l fr --ignore=manage.py --ignore=medias --ignore=setup.py --ignore=staticfiles --ignore=templates

.PHONY: sass
sass:
	$(EXEC_CMD) pipenv run python manage.py compilescss
	make collectstatic

.PHONY: quality
quality:
	$(EXEC_CMD) pipenv run black --check --exclude=venv .
	$(EXEC_CMD) pipenv run isort --check --skip-glob="**/migrations" --extend-skip-glob="venv" .
	$(EXEC_CMD) pipenv run flake8 --count --show-source --statistics --exclude="venv,**/migrations" .

.PHONY: fix
fix:
	$(EXEC_CMD) pipenv run black --exclude=venv .
	$(EXEC_CMD) pipenv run isort --skip-glob="**/migrations" --extend-skip-glob="venv" .


.PHONY: dev-init
dev-init:
	$(EXEC_CMD) pipenv sync --dev
	$(EXEC_CMD) pipenv run pre-commit install

.PHONY: init
init:
	$(EXEC_CMD) pipenv sync
	$(EXEC_CMD) pipenv run python manage.py migrate
	make collectstatic
	$(EXEC_CMD) pipenv run python manage.py set_config
	$(EXEC_CMD) pipenv run python manage.py create_starter_pages

.PHONY: update
update:
	$(EXEC_CMD) pipenv run python manage.py migrate
	$(EXEC_CMD) pipenv run python manage.py update_index
	$(EXEC_CMD) pipenv run python manage.py compilemessages
	make collectstatic

.PHONY: demo
demo:
	make init
	$(EXEC_CMD) pipenv run python manage.py create_demo_pages

.PHONY: runserver
runserver:
	$(EXEC_CMD) pipenv run python manage.py runserver $(HOST_URL):$(HOST_PORT)


.PHONY: test
test:
	$(EXEC_CMD) pipenv run python manage.py test
