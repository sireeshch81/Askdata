#!/bin/bash

# Fail on any error
set -e

# Load environment variables from the .env file if it exists
if [ -f /app/.env ]; then
  set -a
  . /app/.env
  set +a
else
  echo "Warning: /app/.env not found. Continuing without environment variables."
fi

echo "Starting ETL Services API server with Uvicorn..."

# Activate virtual environment and start the server
source /app/.venv/bin/activate
exec uvicorn main:app --host 0.0.0.0 --port 5003
