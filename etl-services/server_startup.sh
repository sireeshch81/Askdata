#!/bin/bash

. .env

echo "Starting ETL Services API server with Uvicorn..."
. /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 5003
