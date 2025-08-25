FROM python:3.13-slim AS builder

# Add SSL bypass environment variables
ENV PYTHONHTTPSVERIFY=0
ENV PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org pypi.python.org"

WORKDIR /app

COPY pyproject.toml .

RUN apt-get update && apt-get install -y python3-venv

COPY requirements.txt .

RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && /app/venv/bin/pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org" \
    && /app/venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org --upgrade pip \
    && /app/venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt


FROM python:3.13-slim AS runtime

# Add SSL bypass environment variables
ENV PYTHONHTTPSVERIFY=0
ENV PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org pypi.python.org"

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

COPY server_startup.sh .
COPY . .

COPY --from=builder /app/venv /app/venv/

RUN chmod +x run_all_etl_jobs.sh \
    && chmod +x server_startup.sh \
    && chown -R appuser:appuser /app \
    && chown appuser:appuser server_startup.sh \
    && chown appuser:appuser run_all_etl_jobs.sh

USER appuser

EXPOSE 5003

CMD ["/app/server_startup.sh"]
