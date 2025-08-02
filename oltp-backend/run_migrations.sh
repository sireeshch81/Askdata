#!/usr/bin/bash

echo "Running database migrations with Alembic..."

cd /app || exit 1
. /app/.venv/bin/activate && alembic upgrade head

echo "Migrations completed."