#!/bin/bash
set -e

start_time=$SECONDS

echo "Stopping all running containers..."
step_start=$(date +%s)
docker-compose down
step_end=$(date +%s)
echo "Time taken to stop containers: $((step_end - step_start)) seconds"

echo "Removing unused images..."
step_start=$(date +%s)
docker image prune -af
step_end=$(date +%s)
echo "Time taken to remove images: $((step_end - step_start)) seconds"

echo "Pruning unused volumes and networks..."
step_start=$(date +%s)
docker volume prune -f
docker network prune -f
step_end=$(date +%s)
echo "Time taken to prune volumes and networks: $((step_end - step_start)) seconds"

echo "Rebuilding and starting all containers..."
step_start=$(date +%s)
docker-compose up -d --build
step_end=$(date +%s)
echo "Time taken to rebuild and start containers: $((step_end - step_start)) seconds"

total_time=$((SECONDS - start_time))
echo "Total elapsed time: $total_time seconds"

echo "Current running containers:"
docker ps -a
