FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       git \
       curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PERSIST_DIRECTORY=/data \
    DEFAULT_COLLECTION=nlp_sql_pairs \
    ANONYMIZED_TELEMETRY=FALSE \
    EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    SENTENCE_TRANSFORMERS_HOME=/cache/sentence-transformers \
    HUGGINGFACE_HUB_CACHE=/cache/huggingface

WORKDIR /app

COPY pyproject.toml .
COPY requirements.txt .

RUN rm -rf /app/venv \
    && python -m venv /app/venv \
    && . /app/venv/bin/activate \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -r requirements.txt
#    && /app/venv/bin/pip install uv \
#    && /app/venv/bin/uv sync --active

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY pyproject.toml .
COPY . .

# Copy Zscaler root certificate into the trusted CA store
COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Set permissions and update CA certificates inside the container
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt && update-ca-certificates

# Set environment variables so Python and pip use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONUNBUFFERED=1
ENV GEMINI_API_KEY="AIzaSyBXdG0nUWgFhrCKOewbUr34RM7_wBz0OCQ"

RUN apt-get update && apt-get install -y netcat-openbsd \
    && apt-get install -y --no-install-recommends python3-venv curl ca-certificates vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /data /cache/sentence-transformers /cache/huggingface \
    && adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app /data /cache \
    && echo "alias ll='ls -lahF'" >> /home/appuser/.bashrc \
    && echo "DW-BACKEND: Running in container" >> /home/appuser/hostinfo.txt

COPY --from=builder /app/venv /app/venv/

RUN chmod +x server_startup.sh \
    && find /app/venv/bin -type f -executable -exec chmod +x {} \; \
    && rm -f /app/venv/bin/python* \
    && ln -s /usr/local/bin/python /app/venv/bin/python \
    && chown -R appuser:appuser /app \
    && chown appuser:appuser server_startup.sh

USER appuser

EXPOSE 5006

CMD ["/app/server_startup.sh"]

