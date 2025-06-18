set dotenv-load
set shell := ["bash", "-uc"]

# Variables initialized from env
poetry_run := if env("USE_POETRY", "0") == "1" { "poetry run" } else { "" }
docker_cmd := if env("USE_DOCKER", "0") == "1" { "docker compose exec -ti web" } else { "" }
host_url := env("HOST_URL", "localhost")
host_port := env("HOST_PORT", "8000")

# Default recipe
default:
    @just --list

# Other recipes
collectstatic:
    {{docker_cmd}} {{poetry_run}} python manage.py collectstatic --noinput --ignore=*.sass

coverage app="":
    {{poetry_run}} coverage run --source='.' manage.py test {{app}}
    {{poetry_run}} coverage html
    firefox htmlcov/index.html

createsuperuser:
    {{poetry_run}} python manage.py createsuperuser

demo:
	just init
	{{docker_cmd}} {{poetry_run}} python manage.py create_demo_pages

deploy:
    {{docker_cmd}} {{poetry_run}} python manage.py migrate
    just collectstatic
    {{docker_cmd}} {{poetry_run}} python manage.py import_dsfr_pictograms
    {{docker_cmd}} {{poetry_run}} python manage.py import_page_templates
    just index

first-deploy:
    {{docker_cmd}} {{poetry_run}} python manage.py migrate
    just collectstatic
    {{docker_cmd}} {{poetry_run}} python manage.py set_config
    {{docker_cmd}} {{poetry_run}} python manage.py import_dsfr_pictograms
    {{docker_cmd}} {{poetry_run}} python manage.py create_starter_pages
    {{docker_cmd}} {{poetry_run}} python manage.py import_page_templates
    just index

import_domain_whitelist:
	{{docker_cmd}} {{poetry_run}} python manage.py import_domain_whitelist

index:
    {{docker_cmd}} {{poetry_run}} python manage.py update_index

init:
    {{docker_cmd}} poetry install --no-root --without dev
    just first-deploy

init-dev:
    poetry install --no-root
    just first-deploy
    {{poetry_run}} pre-commit install

alias messages := makemessages
makemessages:
    {{docker_cmd}} {{poetry_run}} django-admin makemessages -l fr --ignore=manage.py --ignore=config --ignore=medias --ignore=__init__.py --ignore=setup.py --ignore=staticfiles
    {{docker_cmd}} {{poetry_run}} django-admin makemessages -d djangojs -l fr --ignore=config --ignore=medias --ignore=staticfiles

alias mm:= makemigrations
makemigrations app="":
    {{poetry_run}} python manage.py makemigrations {{app}}

alias mi := migrate
migrate app="" version="":
    {{poetry_run}} python manage.py migrate {{app}} {{version}}

mmi:
    just makemigrations
    just migrate

quality:
    {{docker_cmd}} pre-commit run --all-files

alias rs := runserver
runserver host_url=host_url host_port=host_port:
	{{docker_cmd}} {{poetry_run}} python manage.py runserver {{host_url}}:{{host_port}}

shell:
    {{docker_cmd}} {{poetry_run}} python manage.py shell

test app="":
    {{docker_cmd}} {{poetry_run}} python manage.py test {{app}} --buffer --parallel --settings config.settings_test

unittest app="":
    {{docker_cmd}} {{poetry_run}} python manage.py test {{app}} --settings config.settings_test

update:
    {{docker_cmd}} poetry install --no-root --without dev
    just deploy

upgrade:
    {{docker_cmd}} poetry update
    {{docker_cmd}} pre-commit autoupdate
    {{docker_cmd}} npm update

web-prompt:
	{{docker_cmd}} bash
