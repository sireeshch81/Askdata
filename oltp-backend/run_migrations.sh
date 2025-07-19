#!/usr/bin/env bash

cd /app || exit 1
. /app/venv/bin/activate && alembic upgrade head
