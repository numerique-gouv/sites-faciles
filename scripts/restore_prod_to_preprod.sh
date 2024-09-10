#!/usr/bin/env bash

# Cf : https://doc.scalingo.com/platform/databases/duplicate
DUPLICATE_ADDON_KIND=postgresql
ARCHIVE_NAME="backup.tar.gz"

install-scalingo-cli

# 1. Login to Scalingo, using the token stored in `DUPLICATE_API_TOKEN`:
scalingo login --api-token "${DUPLICATE_API_TOKEN}"

# 3. Install postgres tools
dbclient-fetcher "${DUPLICATE_ADDON_KIND}"

# 4. Retrieve the addon id:
addon_id="$( scalingo --app "${PRODUCTION_APP}" addons \
  | grep "${DUPLICATE_ADDON_KIND}" \
  | cut -d "|" -f 3 \
  | tr -d " " )"

# 5. Download the latest backup available for the specified addon:
scalingo --app "${PRODUCTION_APP}" --addon "${addon_id}" \
backups-download --output "${ARCHIVE_NAME}"
# 6. Get the name of the backup file:
backup_file_name="$( tar --list --file="${ARCHIVE_NAME}" \
  | tail -n 1 \
  | cut -d "/" -f 2 )"

# 7. Extract the archive containing the downloaded backup:
tar --extract --verbose --file="${ARCHIVE_NAME}"

# 8. Restore the data:
for table in $(psql "${PREPROD_DATABASE_URL}" -t -c "SELECT \"tablename\" FROM pg_tables WHERE schemaname='public'"); do
     psql "${PREPROD_DATABASE_URL}" -c "DROP TABLE IF EXISTS \"${table}\" CASCADE;"
done
pg_restore --clean --no-acl --no-owner --no-privileges --dbname "${PREPROD_DATABASE_URL}" ${backup_file_name}
