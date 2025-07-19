#!/usr/bin/env bash

cd /app || exit 1
alembic upgrade head
