#!/bin/sh -l
set -ex

uv run python manage.py migrate

if [ "$DEBUG" = "True" ]; then
    uv run python manage.py runserver 0.0.0.0:$CONTAINER_PORT
else
    uv run gunicorn config.wsgi:application --bind 0.0.0.0:$CONTAINER_PORT
fi

exec "$@"
