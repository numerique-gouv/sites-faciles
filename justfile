set dotenv-load
set shell := ["bash", "-uc"]

poetry_run := if env("USE_POETRY", "0") == "1" { "poetry run" } else { "" }
docker_cmd := if env("USE_DOCKER", "0") == "1" { "docker compose exec -ti web" } else { "" }

default:
    just -l

collectstatic:
    {{docker_cmd}} {{poetry_run}} python manage.py collectstatic --noinput --ignore=*.sass

coverage app="":
    {{poetry_run}} coverage run --source='.' manage.py test {{app}}
    {{poetry_run}} coverage html
    firefox htmlcov/index.html

createsuperuser:
    {{poetry_run}} python manage.py createsuperuser

deploy:
    {{poetry_run}} python manage.py migrate
    just collectstatic
    {{poetry_run}} python manage.py import_dsfr_pictograms
    {{poetry_run}} python manage.py import_page_templates
    just index

first-deploy:
    {{poetry_run}} python manage.py migrate
    just collectstatic
    {{poetry_run}} python manage.py set_config
    {{poetry_run}} python manage.py import_dsfr_pictograms
    {{poetry_run}} python manage.py create_starter_pages
    {{poetry_run}} python manage.py import_page_templates
    just index

index:
    {{poetry_run}} python manage.py update_index

init:
    poetry install --no-root --without dev
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
    {{poetry_run}} pre-commit run --all-files

sass:
    {{docker_cmd}} {{poetry_run}} python manage.py compilescss
    just collectstatic

shell:
    {{poetry_run}} python manage.py shell

test app="":
    {{poetry_run}} python manage.py test {{app}} --buffer --parallel --settings config.settings_test

unittest app="":
    {{poetry_run}} python manage.py test {{app}} --settings config.settings_test

update:
    poetry install --no-root --without dev
    just deploy

upgrade:
    $(EXEC_CMD) poetry update
    $(EXEC_CMD) pre-commit autoupdate
    $(EXEC_CMD) npm update
