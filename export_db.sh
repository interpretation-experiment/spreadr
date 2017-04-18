#!/bin/bash -e
# Export all relevant models of a database to a json file

if [ $# != 2 ]; then
  echo "Usage: $(basename $0) <db-name> <out-file>"
  exit 1
fi

DB_NAME=$1
OUT=$2

if [ -e $OUT ]; then
  echo "'$OUT' already exists, not overwriting it."
  echo "Abort."
  exit 1
fi

DB_NAME=$DB_NAME python manage.py dumpdata \
  --settings spreadr.settings_analysis \
  --format json \
  --indent 2 \
  --output "$OUT" \
  gists auth.user sites account.emailaddress
