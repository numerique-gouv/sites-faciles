#!/bin/bash

# Roll a Scalingo app back to a database backup and to the code of a given git ref
#
# Usage: rollback_scalingo.sh APP [REF=production] [REGION=osc-fr1]
#
# Tables created after the chosen backup (by newer migrations) are not part of the dump,
# so `pg_restore --clean` would leave them in place: they are detected and dropped first.

# Manage environment variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

set -a
[ -f  ${SCRIPT_DIR}/../.env ] && . ${SCRIPT_DIR}/../.env && echo "Local env variables loaded"
set +a

set -euo pipefail

APP=${1:-}
REF=${2:-production}
REGION=${3:-osc-fr1}
TUNNEL_PORT=${TUNNEL_PORT:-10000}
REPO_URL="https://github.com/numerique-gouv/sites-conformes.git"
REPO_ARCHIVE_URL="https://github.com/numerique-gouv/sites-conformes/archive/${REF}.tar.gz"

if [[ -z "$APP" ]]; then
    echo "Usage: $0 APP [REF=production] [REGION=osc-fr1]" 1>&2
    exit 1
fi

if [[ -z "${BACKUP_DIR:-}" ]]; then
    echo "Please set BACKUP_DIR to a directory outsite of the django path" 1>&2
    exit 1
fi

for cmd in scalingo pg_restore psql curl git; do
    if ! command -v $cmd &> /dev/null; then
        echo "Missing command: ${cmd}" 1>&2
        exit 1
    fi
done

sc() {
    scalingo --region ${REGION} --app ${APP} "$@"
}

if ! curl -sfIL -o /dev/null ${REPO_ARCHIVE_URL}; then
    echo "Git ref ${REF} not found on GitHub (${REPO_ARCHIVE_URL})" 1>&2
    exit 1
fi

WORK_DIR=${BACKUP_DIR}/rollback-${APP}-`date '+%Y%m%d-%H%M%S'`
mkdir -p ${WORK_DIR}

# Caution, as of the Scalingo CLI app 1.39.0, the pipe separator ('|') has been replaced with a "BOX DRAWINGS LIGHT VERTICAL" ('│')
pg_uuid=`sc addons | grep "PostgreSQL" | awk -F ['│'] '{print $3}' | xargs`
if [[ -z "$pg_uuid" ]]; then
    echo "No PostgreSQL addon found for ${APP}" 1>&2
    exit 1
fi
echo "PostgreSQL addon: ${pg_uuid}"

# Choose the backup
echo
echo "Recent deployments:"
sc deployments | head -n 12
echo
echo "Available backups:"
sc --addon ${pg_uuid} backups
if [[ -z "${BACKUP_ID:-}" ]]; then
    echo
    read -r -p "ID of the backup to restore (it must predate the deployment to roll back): " BACKUP_ID
fi
if [[ -z "$BACKUP_ID" ]]; then
    echo "No backup chosen, aborting" 1>&2
    exit 1
fi

# Download and extract the backup
echo "Downloading backup ${BACKUP_ID} to ${WORK_DIR}"
sc --addon ${pg_uuid} backups-download --backup ${BACKUP_ID} --output ${WORK_DIR}/backup.tar.gz
tar xzf ${WORK_DIR}/backup.tar.gz -C ${WORK_DIR}
DUMP_FILE=`find ${WORK_DIR} -name '*.pgsql' | head -1`
if [[ -z "$DUMP_FILE" ]]; then
    echo "No .pgsql file found in the backup archive" 1>&2
    exit 1
fi

# Open the database tunnel
DB_URL=`sc env-get SCALINGO_POSTGRESQL_URL | sed -E "s#@[^/]+/#@127.0.0.1:${TUNNEL_PORT}/#"`
sc db-tunnel -p ${TUNNEL_PORT} SCALINGO_POSTGRESQL_URL > ${WORK_DIR}/tunnel.log 2>&1 &
TUNNEL_PID=$!
trap 'kill ${TUNNEL_PID} 2> /dev/null || true' EXIT

echo "Opening the database tunnel on port ${TUNNEL_PORT}"
for i in $(seq 1 30); do
    psql "${DB_URL}" -Atqc "SELECT 1" &> /dev/null && break
    if [[ $i -eq 30 ]]; then
        echo "Could not connect through the tunnel, see ${WORK_DIR}/tunnel.log" 1>&2
        exit 1
    fi
    sleep 1
done

# Tables present in the database but absent from the dump
# (sort and comm must share the same collation: the C locale avoids locale-dependent orders)
extra_tables() {
    LC_ALL=C comm -13 \
        <(pg_restore -l ${DUMP_FILE} | awk '$4 == "TABLE" && $5 == "public" {print $6}' | LC_ALL=C sort -u) \
        <(psql "${DB_URL}" -Atc "SELECT tablename FROM pg_tables WHERE schemaname = 'public'" | LC_ALL=C sort -u)
}
EXTRA_TABLES=`extra_tables`

echo
echo "================================================================"
echo " App:     ${APP} (${REGION})"
echo " Backup:  ${BACKUP_ID}"
echo " Code:    ${REF}"
echo " Tables created since the backup, to be dropped:"
echo "${EXTRA_TABLES:-  (none)}" | sed 's/^/   /'
echo
echo " The current database will be REPLACED by the backup."
echo "================================================================"
read -r -p "Type the app name to confirm: " CONFIRM
if [[ "$CONFIRM" != "$APP" ]]; then
    echo "Aborted" 1>&2
    exit 1
fi

# Skip the safety backup if a completed one is recent enough (the restored backup does not count)
SAFETY_BACKUP_MAX_AGE=$((4 * 3600))
last_backup_date=`sc --addon ${pg_uuid} backups | sed 's/\x1b\[[0-9;]*m//g' \
    | awk -F '│' -v restored="${BACKUP_ID}" '$5 ~ /done/ && (restored == "" || !index($2, restored)) {print $3; exit}' | xargs`
if [[ -n "$last_backup_date" ]] \
    && (( $(date +%s) - $(date -d "$last_backup_date" +%s) < SAFETY_BACKUP_MAX_AGE )); then
    echo "Skipping the safety backup, a backup was made less than 4 hours ago (${last_backup_date})"
else
    echo "Creating a safety backup of the current database"
    sc --addon ${pg_uuid} backups-create
fi

# Stop the web containers so that the current code does not write during the restoration
WEB_AMOUNT=`sc ps | grep -cE '│ *web-[0-9]+ ' || true`
if [[ "$WEB_AMOUNT" -eq 0 ]]; then
    read -r -p "Could not read the number of web containers, how many should be restarted? " WEB_AMOUNT
fi
sc scale web:0

if [[ -n "$EXTRA_TABLES" ]]; then
    echo "Dropping the tables created since the backup"
    psql "${DB_URL}" -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS $(echo ${EXTRA_TABLES} | sed 's/ /, /g') CASCADE;"
fi

echo "Restoring the backup"
# Errors on extensions or comments are expected with the Scalingo user rights
pg_restore --clean --if-exists --no-owner --no-privileges --no-comments -d "${DB_URL}" ${DUMP_FILE} \
    || echo "pg_restore reported errors (see above), check that they are only about extensions or comments"

REMAINING_TABLES=`extra_tables`
if [[ -n "$REMAINING_TABLES" ]]; then
    echo "Some tables are still absent from the backup, aborting before deploying:" 1>&2
    echo "${REMAINING_TABLES}" 1>&2
    exit 1
fi

kill ${TUNNEL_PID} 2> /dev/null || true

# The database is restored: restart the web containers even if the deployment fails
trap 'sc scale web:${WEB_AMOUNT}' EXIT

echo "Deploying ${REF}"
# Archive deployments can fail in the apt buildpack: go through the GitHub integration when possible
# (it can only deploy branches)
if sc integration-link 2> /dev/null | grep -q "Repository:" \
    && git ls-remote --exit-code --heads ${REPO_URL} ${REF} &> /dev/null; then
    sc integration-link-manual-deploy --follow ${REF}
else
    sc deploy ${REPO_ARCHIVE_URL} ${REF}
fi

echo
echo "Rollback done. Next steps:"
echo " - check the migrations: scalingo --region ${REGION} --app ${APP} run python manage.py showmigrations"
echo " - if a GitHub integration with auto-deploy is linked (scalingo --region ${REGION} --app ${APP} integration-link),"
echo "   the next push on its branch will deploy that code again"
echo " - media files uploaded after the backup are still on the S3 bucket, but no longer referenced"
