#!/bin/bash

# Restore the latest downloaded medias from production

# Manage environment variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

set -a
[ -f  ${SCRIPT_DIR}/../.env ] && . ${SCRIPT_DIR}/../.env && echo "Local env variables loaded"
set +a


if [[ -z "$BACKUP_DIR" ]]; then
    echo "Please set BACKUP_DIR to a directory outsite of the django path" 1>&2
    exit 1
fi

MEDIA_BACKUP_FILE=`ls ${BACKUP_DIR}/sites-faciles-local-medias-*.tar.gz -c | head -1`
BASE_PATH="${SCRIPT_DIR}/.."

echo "Moving media files from ${MEDIA_BACKUP_FILE} to ${MEDIA_ROOT:=medias}"

cd ${BASE_PATH}
echo `pwd`
rm ${MEDIA_ROOT}/* -rf && tar xvzf ${MEDIA_BACKUP_FILE}
