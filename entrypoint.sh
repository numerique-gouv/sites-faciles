#!/bin/sh -l
set -ex

pipenv run python manage.py migrate

exec "$@"
