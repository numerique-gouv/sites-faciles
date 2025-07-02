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

ifeq ($(USE_UV),1)
	UV_CMD := uv run
else
	UV_CMD :=
endif

MAKEFLAGS += --no-print-directory
NO_FORMAT=\033[0m
C_ORANGERED1=\033[38;5;202m

.PHONY: deprecation-warning
deprecation-warning:
	@echo "${C_ORANGERED1}WARNING: this project now uses just instead of make. \
	This recipe is obsolete and will be removed in a future major version. \
	Please use the equivalent recipe through just.${NO_FORMAT}"

.PHONY: deletion-warning
deletion-warning:
	@echo "${C_ORANGERED1}WARNING: this recipe is obsolete \
	and will be removed in a future major version.${NO_FORMAT}"

.PHONY: web-prompt
web-prompt:
	$(EXEC_CMD) bash
	@make deprecation-warning

.PHONY: collectstatic
collectstatic:
	$(EXEC_CMD) $(UV_CMD) python manage.py collectstatic --noinput
	@make deprecation-warning

.PHONY: messages
messages:
	$(EXEC_CMD) $(UV_CMD) django-admin makemessages -l fr --ignore=manage.py --ignore=config --ignore=medias --ignore=__init__.py --ignore=setup.py --ignore=staticfiles
	$(EXEC_CMD) $(UV_CMD) django-admin makemessages -d djangojs -l fr --ignore=config --ignore=medias --ignore=staticfiles
	@make deprecation-warning

.PHONY: quality
quality:
	$(EXEC_CMD) ruff check .
	$(EXEC_CMD) $(UV_CMD) black --check --exclude=venv .
	@make deprecation-warning

.PHONY: fix
fix:
	$(EXEC_CMD) ruff check . --fix
	$(EXEC_CMD) $(UV_CMD) black --exclude=venv .
	@make deletion-warning

.PHONY: index
index:
	$(EXEC_CMD) $(UV_CMD) python manage.py update_index
	@make deprecation-warning

.PHONY: first-deploy
first-deploy:
	$(EXEC_CMD) $(UV_CMD) python manage.py migrate
	make collectstatic
	$(EXEC_CMD) $(UV_CMD) python manage.py create_starter_pages
	$(EXEC_CMD) $(UV_CMD) python manage.py import_page_templates
	make index
	@make deletion-warning

.PHONY: init
init:
	$(EXEC_CMD) uv sync --no-group dev
	make deploy
	@make deprecation-warning

.PHONY: init-dev
init-dev:
	$(EXEC_CMD) uv sync
	make deploy
	$(EXEC_CMD) $(UV_CMD) pre-commit install
	@make deprecation-warning

.PHONY: deploy
deploy:
	$(EXEC_CMD) $(UV_CMD) python manage.py migrate
	make collectstatic
	$(EXEC_CMD) $(UV_CMD) python manage.py create_starter_pages
	$(EXEC_CMD) $(UV_CMD) python manage.py import_page_templates
	make index
	@make deprecation-warning

.PHONY: update
update:
	$(EXEC_CMD) uv sync --no-group dev
	make deploy
	@make deprecation-warning

.PHONY: upgrade
upgrade:
	$(EXEC_CMD) uv lock --upgrade
	$(EXEC_CMD) pre-commit autoupdate
	$(EXEC_CMD) npm update
	@make deprecation-warning

.PHONY: demo
demo:
	make init
	$(EXEC_CMD) $(UV_CMD) python manage.py create_demo_pages
	@make deprecation-warning

.PHONY: runserver
runserver:
	$(EXEC_CMD) $(UV_CMD) python manage.py runserver $(HOST_URL):$(HOST_PORT)
	@make deprecation-warning

.PHONY: shell
shell:
	$(EXEC_CMD) $(UV_CMD) python manage.py shell
	@make deprecation-warning

.PHONY: test
test:
	$(EXEC_CMD) $(UV_CMD) python manage.py test --buffer --parallel --settings config.settings_test
	@make deprecation-warning

.PHONY: test-unit
test-unit:
	$(EXEC_CMD) $(UV_CMD) python manage.py test --settings config.settings_test
	@make deprecation-warning

.PHONY: import_domain_whitelist
import_domain_whitelist:
	$(EXEC_CMD) $(UV_CMD) python manage.py import_domain_whitelist
	@make deprecation-warning
