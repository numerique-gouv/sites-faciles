set dotenv-load
set shell := ["bash", "-uc"]

poetry_run := if env("USE_POETRY", "0") == "1" { "poetry run" } else { "" }

default:
    just -l

collectstatic:
    {{poetry_run}} python manage.py collectstatic --noinput --ignore=*.sass

coverage app="":
    {{poetry_run}} coverage run --source='.' manage.py test {{app}}
    {{poetry_run}} coverage html
    firefox htmlcov/index.html

createsuperuser:
    {{poetry_run}} python manage.py createsuperuser

index:
    {{poetry_run}} python manage.py update_index

alias messages := makemessages
makemessages:
    {{poetry_run}} django-admin makemessages -l fr --ignore=manage.py --ignore=config --ignore=medias --ignore=__init__.py --ignore=setup.py --ignore=staticfiles
    {{poetry_run}} django-admin makemessages -d djangojs -l fr --ignore=config --ignore=medias --ignore=staticfiles

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
    {{poetry_run}} python manage.py compilescss
    just collectstatic

shell:
    {{poetry_run}} python manage.py shell

test app="":
    {{poetry_run}} python manage.py test {{app}} --buffer --parallel --settings config.settings_test

unittest app="":
    {{poetry_run}} python manage.py test {{app}} --settings config.settings_test
