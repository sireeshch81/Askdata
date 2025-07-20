FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml .

RUN apt-get update && apt-get install -y python3-venv

RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install uv \
    && /app/venv/bin/uv sync --active


FROM python:3.13-slim AS runtime

LABEL authors="AskData Team 2"

WORKDIR /app

# Install dependencies and system tools
COPY pyproject.toml .
RUN apt-get update && apt-get install -y netcat-openbsd \
    && apt-get install -y --no-install-recommends python3-venv curl ca-certificates vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set permissions
RUN useradd --create-home --shell /bin/bash appuser \
    && echo "alias ll='ls -lahF'" >> /home/appuser/.bashrc

#RUN python3 -m venv /app/venv \
#    && . /app/venv/bin/activate \
#    && pip install --upgrade pip \
#    && pip install uv \
#    && uv sync

COPY ../.env .env
COPY server_startup.sh .
COPY . .

COPY --from=builder /app/venv /app/venv/

RUN chmod +x server_startup.sh \
    && chown -R appuser:appuser /app \
    && chown appuser:appuser server_startup.sh

USER appuser

EXPOSE 5001

CMD ["/app/server_startup.sh"]
