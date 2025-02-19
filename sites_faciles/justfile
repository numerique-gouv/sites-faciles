set dotenv-load
set shell := ["bash", "-uc"]

poetry_run := if env("USE_POETRY", "0") == "1" { "poetry run" } else { "" }

default:
    just -l

alias mm:= makemigrations
makemigrations app="":
    {{poetry_run}} python manage.py makemigrations {{app}}

alias mi := migrate
migrate app="" version="":
    {{poetry_run}} python manage.py migrate {{app}} {{version}}

mmi:
    just makemigrations
    just migrate

test app="":
    {{poetry_run}} python manage.py test {{app}} --buffer --parallel

unittest app="":
    {{poetry_run}} python manage.py test {{app}} --settings config.settings_test
