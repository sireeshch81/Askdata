#!/bin/bash

docker pull ubuntu:noble

# docker build --load -t askdata-ur-container .

docker buildx build -t askdata-ur-container:latest --load .

docker tag askdata-ur-container:latest local/askdata-ur-container:latest

# DOCKER_BUILDKIT=0 docker compose build api-backend
# --no-cache

