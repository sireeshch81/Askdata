#!/usr/bin/env bash

cd /app || exit 1
. .env
. /app/venv/bin/activate && alembic upgrade head
