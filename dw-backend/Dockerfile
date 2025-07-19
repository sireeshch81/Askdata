FROM python:3.13-slim

LABEL authors="AskData Team 2"

WORKDIR /app

# Install dependencies and system tools
COPY pyproject.toml .
RUN apt-get update && apt-get install -y netcat-openbsd \
    && apt-get install -y --no-install-recommends python3-venv curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set permissions
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install uv \
    && uv sync

COPY . .

RUN chmod +x server_startup.sh \
    && chown appuser:appuser server_startup.sh

USER appuser

EXPOSE 5001

# Command to run the application
CMD ["./server_startup.sh"]

