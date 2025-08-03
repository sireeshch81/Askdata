#!/bin/bash
set -e

#. .env
. /app/.env

# Wait for the database to be ready
echo "Waiting for Mongo database to be ready..."
while ! nc -z mongodb 27017; do
  sleep 2
done
echo "Mongo database is ready!"

echo "Starting Backend API server with Uvicorn..."
. /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 5004
