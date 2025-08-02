#!/bin/bash

echo "Health Check Report - $(date)"

services=(
  "dw-backend:http://localhost:5001/health"
  "oltp-backend:http://localhost:5002/health"
  "etl-services:http://localhost:5003/health"
  "ollama:http://localhost:11434/health"
  "chromadb:http://localhost:9000/health"
  "streamlit:http://localhost:8501"
  "keycloak:http://localhost:8080"
)

for service in "${services[@]}"; do
  name="${service%%:*}"
  url="${service#*:}"

  # Send request with timeout 5s and get HTTP status code only
  http_code=$(curl -o /dev/null -s -w "%{http_code}" --max-time 5 "$url")

  # Interpret common codes
  case $http_code in
    200)
      status="OK"
      ;;
    302)
      status="Redirect"
      ;;
    404)
      status="Not Found"
      ;;
    000)
      status="No Response"
      ;;
    *)
      status="HTTP $http_code"
      ;;
  esac

  echo "$name: $status"
done

