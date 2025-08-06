FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml .

# Copy Zscaler root certificate into the trusted CA store
COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Set permissions and update CA certificates inside the container
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt && update-ca-certificates

# Set environment variables so Python and pip use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONUNBUFFERED=1

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
COPY .env .

# Copy Zscaler root certificate into the trusted CA store
COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Set permissions and update CA certificates inside the container
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt && update-ca-certificates

# Set environment variables so Python and pip use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONUNBUFFERED=1
ENV YOUR_API_KEY="AIzaSyBXdG0nUWgFhrCKOewbUr34RM7_wBz0OCQ"

RUN apt-get update && apt-get install -y netcat-openbsd \
    && apt-get install -y --no-install-recommends python3-venv curl ca-certificates vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set permissions
RUN useradd --create-home --shell /bin/bash appuser \
    && echo "alias ll='ls -lahF'" >> /home/appuser/.bashrc \
    && echo "API-BACKEND: Running in container" >> /home/appuser/hostinfo.txt

COPY server_startup.sh .
COPY . .

COPY --from=builder /app/venv /app/venv/

RUN chmod +x server_startup.sh \
    && chown -R appuser:appuser /app \
    && chown appuser:appuser server_startup.sh

USER appuser

EXPOSE 5004

CMD ["/app/server_startup.sh"]
