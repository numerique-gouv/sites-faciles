set dotenv-load
set shell := ["bash", "-uc"]

poetry_run := if env("USE_POETRY", "0") == "1" { "poetry run" } else { "" }

default:
    just -l

coverage app="":
    {{poetry_run}} coverage run --source='.' manage.py test {{app}}
    {{poetry_run}} coverage html
    firefox htmlcov/index.html

alias mm:= makemigrations
makemigrations app="":
    {{poetry_run}} python manage.py makemigrations {{app}}

alias mi := migrate
migrate app="" version="":
    {{poetry_run}} python manage.py migrate {{app}} {{version}}

mmi:
    just makemigrations
    just migrate

shell:
    {{poetry_run}} python manage.py shell

test app="":
    {{poetry_run}} python manage.py test {{app}} --buffer --parallel --settings config.settings_test

unittest app="":
    {{poetry_run}} python manage.py test {{app}} --settings config.settings_test
