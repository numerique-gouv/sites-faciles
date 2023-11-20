#!/bin/sh -l
set -ex

poetry run python manage.py migrate

exec "$@"
