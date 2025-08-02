#!/bin/bash
set -e

. .env

# Wait for the database to be ready
echo "Waiting for MySQL OLTP database to be ready..."
while ! nc -z "$MYSQL_OLTP_HOST" "$MYSQL_OLTP_PORT"; do
  sleep 2
done
echo "MySQL OLTP database is ready!"

echo "Starting OLTP Backend API server with Uvicorn..."
. /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 5004
