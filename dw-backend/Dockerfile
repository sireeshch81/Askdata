FROM python:3.13-slim

LABEL authors="AskData Team 2"

WORKDIR /app

# Install dependencies and system tools
COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat-openbsd \
    && apt-get install -y --no-install-recommends python3-venv curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install uv \
    && uv sync

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x server_startup.sh

# Expose port
EXPOSE 5001

# Command to run the application
CMD ["./server_startup.sh"]

