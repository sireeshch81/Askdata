#!/bin/bash
set -e

#. .env
. /app/.env

# Wait for the database to be ready
echo "Waiting for database to be ready..."
#while ! nc -z "$MYSQL_DW_HOST" "$MYSQL_DW_PORT"; do
#  sleep 2
#done
echo "database is ready!"

. /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 5006
