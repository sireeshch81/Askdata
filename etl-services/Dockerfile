FROM ubuntu:noble
LABEL authors="askdata-team-2"

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (TODO: Remove vim prior to production)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv curl ca-certificates sudo vim && \
    rm -rf /var/lib/apt/lists/*

# Copy Python project files
COPY pyproject.toml ./
COPY . .

# Create a non-root user with UID 1500 and set permissions
RUN useradd -m -u 1500 askdata && \
    chown -R askdata:askdata /app && \
    chmod +x server_startup.sh

USER askdata

ENV UV_PROJECT_ENVIRONMENT=/app/venv
ENV PATH="/app/venv/bin:$PATH"

# Set up virtual environment and install dependencies as non-root user
RUN rm -rf /app/venv && \
    python3 -m venv /app/venv && \
    ls -l /app/venv/bin && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install uv && \
    /app/venv/bin/uv sync

EXPOSE 5009

# Alembic env setup
ENV PYTHONPATH=/app

# Run Alembic migrations on container start, then start FastAPI
CMD ["/app/server_startup.sh"]
