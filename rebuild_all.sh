#!/bin/bash
set -e  # Stop on first error
echo "Starting AskData full rebuild..."

# 1️⃣ Build shared container image
echo "Step 1: Building shared container image..."
./rebuild_askdata_container.sh

# 2️⃣ Build individual service containers
echo "Step 2: Building individual service containers..."
DOCKER_BUILDKIT=0 docker compose build --no-cache

# 3️⃣ Start all services
echo "Step 3: Starting all services..."
docker compose up -d
echo " #####################"
echo " "
echo " "
echo "✅ AskData rebuild complete!"
echo " "
echo " #####################"
docker ps


