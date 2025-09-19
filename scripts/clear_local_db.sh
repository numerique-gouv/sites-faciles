#!/bin/bash

# Clears the local database

# Manage environment variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

set -a
[ -f  ${SCRIPT_DIR}/../.env ] && . ${SCRIPT_DIR}/../.env && echo "Local env variables loaded"
set +a

echo "Clearing database ${DATABASE_NAME}"

dropdb --host ${DATABASE_HOST} -U ${DATABASE_USER} ${DATABASE_NAME} --force
createdb --host ${DATABASE_HOST} -U ${DATABASE_USER} ${DATABASE_NAME}
