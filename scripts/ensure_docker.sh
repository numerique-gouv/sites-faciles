#!/bin/bash

# Ensure the Docker web container is running and healthy (no-op when USE_DOCKER != 1)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
[ -f "${SCRIPT_DIR}/../.env" ] && . "${SCRIPT_DIR}/../.env"

[ "${USE_DOCKER:-0}" != "1" ] && exit 0

docker compose ps --services --filter status=running 2>/dev/null | grep -q "^web$" \
    || docker compose up -d

WEB_ID=$(docker compose ps -q web 2>/dev/null)

until [ "$(docker inspect --format='{{.State.Health.Status}}' "$WEB_ID" 2>/dev/null)" = "healthy" ]; do
    sleep 3
done
