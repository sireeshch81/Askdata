#!/usr/bin/env bash
#!/bin/bash

echo "Running database migrations with Alembic..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

echo "Migrations completed."
cd /app || exit 1
. /app/venv/bin/activate && alembic upgrade head
