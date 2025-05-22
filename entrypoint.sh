#!/bin/sh -l
set -ex

export PATH="${PATH}:${POETRY_VENV}/bin"
python manage.py migrate

if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:$CONTAINER_PORT
else
    gunicorn config.wsgi:application --bind 0.0.0.0:$CONTAINER_PORT
fi

exec "$@"
