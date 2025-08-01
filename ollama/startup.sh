#!/bin/sh
# Wait for Ollama server to be ready, then pull the model

set -e

ollama serve &

# Give the server some time to start
sleep 5

OLLAMA_PID=$!

echo "Ollama server is up. Pulling model..."
ollama pull mistral:7b
wait
echo "Model pulled."

# Keep the server running
# exec ollama serve

