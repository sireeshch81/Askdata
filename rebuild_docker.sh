#!/bin/bash
set -e

CONTAINERS=("oltp-db" "dw-db" "askdata-mongodb")
IMAGES=("mysql:latest" "mongo:6.0")

echo "Stopping specific containers..."
docker stop "${CONTAINERS[@]}" || true

echo "Removing specific containers..."
docker rm "${CONTAINERS[@]}" || true

echo "Removing specific images..."
docker rmi -f "${IMAGES[@]}" || true

echo "Pruning unused volumes and networks..."
docker volume prune -f
docker network prune -f

echo "Starting docker-compose with rebuild..."
docker-compose up -d --build

echo "Current running containers:"
docker ps -a
