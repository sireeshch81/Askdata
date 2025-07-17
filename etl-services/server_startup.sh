#!/usr/bin/env bash

. /app/venv/bin/activate

cd /app/
alembic upgrade head
gunicorn --bind 0.0.0.0:5001 --workers 4 main:app
