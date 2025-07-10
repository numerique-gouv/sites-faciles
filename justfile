set dotenv-load
set shell := ["bash", "-uc"]

#### Variables initialized from env

uv_run := if env("USE_UV", "0") == "1" { "uv run" } else { "" }
docker_cmd := if env("USE_DOCKER", "0") == "1" { "docker compose exec -ti web" } else { "" }
host_url := env("HOST_URL", "localhost")
host_port := env("HOST_PORT", "8000")

#### Default recipe

default:
    @just --list

#### Other recipes

collectstatic:
    {{docker_cmd}} {{uv_run}} python manage.py collectstatic --noinput

createsuperuser:
    {{docker_cmd}} {{uv_run}} python manage.py createsuperuser

demo:
    just init
    {{docker_cmd}} {{uv_run}} python manage.py create_demo_pages

alias first-deploy := deploy
deploy:
    just migrate
    just collectstatic
    {{docker_cmd}} {{uv_run}} python manage.py create_starter_pages
    {{docker_cmd}} {{uv_run}} python manage.py import_page_templates
    just index

import_domain_whitelist:
    {{docker_cmd}} {{uv_run}} python manage.py import_domain_whitelist

index:
    {{docker_cmd}} {{uv_run}} python manage.py update_index

init:
    {{docker_cmd}} uv sync --no-group dev
    just deploy

init-dev:
    {{docker_cmd}} uv sync
    just deploy
    {{docker_cmd}} {{uv_run}} pre-commit install

alias messages := makemessages
makemessages:
    {{docker_cmd}} {{uv_run}} django-admin makemessages -l fr --ignore=manage.py --ignore=config --ignore=medias --ignore=__init__.py --ignore=setup.py --ignore=staticfiles
    {{docker_cmd}} {{uv_run}} django-admin makemessages -d djangojs -l fr --ignore=config --ignore=medias --ignore=staticfiles

alias mm:= makemigrations
makemigrations app="":
    {{docker_cmd}} {{uv_run}} python manage.py makemigrations {{app}}

alias mi := migrate
migrate app="" version="":
    {{docker_cmd}} {{uv_run}} python manage.py migrate {{app}} {{version}}

mmi:
    just makemigrations
    just migrate

quality:
    {{docker_cmd}} {{uv_run}} pre-commit run --all-files

alias rs := runserver
runserver host_url=host_url host_port=host_port:
    {{docker_cmd}} {{uv_run}} python manage.py runserver {{host_url}}:{{host_port}}

scalingo-postdeploy:
    python manage.py migrate
    python manage.py create_starter_pages
    python manage.py import_page_templates
    python manage.py update_index

shell:
    {{docker_cmd}} {{uv_run}} python manage.py shell


# Update the app to the latest version
update:
    {{docker_cmd}} uv sync --no-group dev
    just deploy

# Upgrade the dependencies
upgrade:
    {{docker_cmd}} uv lock --upgrade
    {{docker_cmd}} {{uv_run}} pre-commit autoupdate
    {{docker_cmd}} npm update

web-prompt:
    {{docker_cmd}} bash

#### Tests

# Check unit test coverage
coverage app="":
    {{uv_run}} coverage run --source='.' manage.py test {{app}}
    {{uv_run}} coverage html
    firefox htmlcov/index.html

# Runs unit tests in parallel
test app="":
    {{docker_cmd}} {{uv_run}} python manage.py test {{app}} --buffer --parallel --settings config.settings_test

# Runs unit tests one by one
unittest app="":
    {{docker_cmd}} {{uv_run}} python manage.py test {{app}} --settings config.settings_test



#### K8s stuff

# build the kubernetes cluster using kind
build-k8s-cluster:
	./bin/start-kind.sh

# start the kubernetes cluster using kind
tilt-start:
	tilt up -f ./bin/Tiltfile

# start the kubernetes cluster using kind
tilt-stop:
	tilt down -f ./bin/Tiltfile
