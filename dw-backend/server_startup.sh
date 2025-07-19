#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for MySQL DW database to be ready..."
while ! nc -z $MYSQL_DW_HOST $MYSQL_DW_PORT; do
  sleep 1
done
echo "MySQL DW database is ready!"

# Start the FastAPI application with Gunicorn using Uvicorn workers
echo "Starting DW Backend API server with Gunicorn..."
gunicorn --bind 0.0.0.0:5001 --workers 4 main:app
