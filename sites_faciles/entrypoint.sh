#!/bin/sh -l
set -ex

export PATH="${PATH}:${POETRY_VENV}/bin"
poetry run python manage.py migrate

exec "$@"
