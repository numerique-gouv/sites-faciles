#!/bin/sh -l
set -ex

# Commands run from inside docker shouldn't be prefixed
export USE_UV=0
export USE_DOCKER=0

just deploy

if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:$CONTAINER_PORT
else
    gunicorn config.wsgi:application --bind 0.0.0.0:$CONTAINER_PORT --access-logfile - --error-logfile -
fi

exec "$@"
