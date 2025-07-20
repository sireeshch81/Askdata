#!/bin/bash
set -e

. .env

# Wait for the database to be ready
echo "Waiting for MySQL DW database to be ready..."
while ! nc -z $MYSQL_DW_HOST $MYSQL_DW_PORT; do
  sleep 2
done
echo "MySQL DW database is ready!"

echo "Running database migrations..."
cd /app/ && chmod ugo+x run_migrations.sh && ./run_migrations.sh

echo "Starting DW Backend API server with Uvicorn..."
. /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 5001
