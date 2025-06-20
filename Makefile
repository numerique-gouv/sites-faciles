# Loading environment variables
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

ifeq ($(USE_DOCKER),1)
	EXEC_CMD := docker compose exec -ti web
else
	EXEC_CMD :=
endif

ifeq ($(USE_POETRY),1)
	POETRY_CMD := poetry run
else
	POETRY_CMD :=
endif

.PHONY: web-prompt
web-prompt:
	$(EXEC_CMD) bash

.PHONY: collectstatic
collectstatic:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py collectstatic --noinput

.PHONY: messages
messages:
	$(EXEC_CMD) $(POETRY_CMD) django-admin makemessages -l fr --ignore=manage.py --ignore=config --ignore=medias --ignore=__init__.py --ignore=setup.py --ignore=staticfiles
	$(EXEC_CMD) $(POETRY_CMD) django-admin makemessages -d djangojs -l fr --ignore=config --ignore=medias --ignore=staticfiles

.PHONY: quality
quality:
	$(EXEC_CMD) ruff check .
	$(EXEC_CMD) $(POETRY_CMD) black --check --exclude=venv .

.PHONY: fix
fix:
	$(EXEC_CMD) ruff check . --fix
	$(EXEC_CMD) $(POETRY_CMD) black --exclude=venv .

.PHONY: index
index:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py update_index

.PHONY: first-deploy
first-deploy:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py migrate
	make collectstatic
	$(EXEC_CMD) $(POETRY_CMD) python manage.py set_config
	$(EXEC_CMD) $(POETRY_CMD) python manage.py import_dsfr_pictograms
	$(EXEC_CMD) $(POETRY_CMD) python manage.py create_starter_pages
	$(EXEC_CMD) $(POETRY_CMD) python manage.py import_page_templates
	make index

.PHONY: init
init:
	$(EXEC_CMD) poetry install --no-root --without dev
	make first-deploy

.PHONY: init-dev
init-dev:
	$(EXEC_CMD) poetry install --no-root
	make first-deploy
	$(EXEC_CMD) $(POETRY_CMD) pre-commit install

.PHONY: deploy
deploy:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py migrate
	make collectstatic
	$(EXEC_CMD) $(POETRY_CMD) python manage.py import_dsfr_pictograms
	$(EXEC_CMD) $(POETRY_CMD) python manage.py import_page_templates
	make index

.PHONY: update
update:
	$(EXEC_CMD) poetry install --no-root --without dev
	make deploy

.PHONY: upgrade
upgrade:
	$(EXEC_CMD) poetry update
	$(EXEC_CMD) pre-commit autoupdate
	$(EXEC_CMD) npm update

.PHONY: demo
demo:
	make init
	$(EXEC_CMD) $(POETRY_CMD) python manage.py create_demo_pages

.PHONY: runserver
runserver:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py runserver $(HOST_URL):$(HOST_PORT)


.PHONY: shell
shell:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py shell

.PHONY: test
test:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py test --buffer --parallel --settings config.settings_test

.PHONY: test-unit
test-unit:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py test --settings config.settings_test

.PHONY: import_domain_whitelist
import_domain_whitelist:
	$(EXEC_CMD) $(POETRY_CMD) python manage.py import_domain_whitelist
