#!/bin/bash

# Ensure the Docker web container is running and healthy (no-op when USE_DOCKER != 1)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

[ "${USE_DOCKER:-0}" != "1" ] && { echo "USE_DOCKER is not set, skipping Docker check."; exit 0; }

[ -f "${SCRIPT_DIR}/../.env" ] && . "${SCRIPT_DIR}/../.env"

[ "${USE_DOCKER:-0}" != "1" ] && { echo "USE_DOCKER is not set, skipping Docker check."; exit 0; }

echo "Ensuring Docker web container is running..."

docker compose ps --services --filter status=running 2>/dev/null | grep -q "^web$" \
    || { echo "Starting Docker containers..."; docker compose up -d; }

WEB_ID=$(docker compose ps -q web 2>/dev/null)

echo "Waiting for web container to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' "$WEB_ID" 2>/dev/null)" = "healthy" ]; do
    sleep 3
done
echo "Docker web container is healthy."
