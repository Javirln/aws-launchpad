#!/bin/bash

DATABASE_URI=$(python /app/manage.py sqldsn -s uri -q)

until psql "$DATABASE_URI" -l 2 >/dev/null 2>&1; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done

echo >&2 "Postgres is up - executing command"

echo >&2 "Executing migrations..."

python /app/manage.py migrate
EXIT_CODE=$?
echo >&2 "Migrations applied, exit code: ${EXIT_CODE}"

exec "$@"
