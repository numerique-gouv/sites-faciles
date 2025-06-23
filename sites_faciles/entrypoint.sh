#!/bin/sh -l
set -ex

export PATH="${PATH}:${POETRY_VENV}/bin"
poetry run python manage.py migrate

if [ "$DEBUG" = "True" ]; then
    poetry run python manage.py runserver 0.0.0.0:$CONTAINER_PORT
else
    poetry run gunicorn config.wsgi:application --bind 0.0.0.0:$CONTAINER_PORT
fi

exec "$@"
