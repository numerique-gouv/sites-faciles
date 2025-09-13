#! /bin/bash

# Get the latest PostgreSQL backup for the production app

# Manage environment variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export BASE_PATH=$(dirname ${SCRIPT_DIR})
export APP="content-manager"

set -a
[ -f  ${SCRIPT_DIR}/../.env ] && . ${SCRIPT_DIR}/../.env && echo "Local env variables loaded"
set +a


if [[ -z "$BACKUP_DIR" ]]; then
    echo "Please set BACKUP_DIR to a directory outsite of the django path" 1>&2
    exit 1
fi

# Caution, as of the Scalingo CLI app 1.39.0, the pipe separator ('|') has been replaced with a "BOX DRAWINGS LIGHT VERTICAL" ('│')
pg_uuid=`scalingo --app ${APP} addons | grep "PostgreSQL" | awk -F ['│'] '{print $3}' | xargs`

echo "Backup UUID: ${pg_uuid}"

cd ${BACKUP_DIR}
scalingo --app ${APP} --addon $pg_uuid backups-download
echo "Prod backup saved at ${BACKUP_DIR}"
