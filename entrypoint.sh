#!/bin/sh -l
set -ex

python manage.py migrate

exec "$@"
