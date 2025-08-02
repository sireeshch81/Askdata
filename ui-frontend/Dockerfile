# Use Python 3.12.3 base image
FROM python:3.12.3-slim-bookworm

# 1. Set working directory and copy requirements
WORKDIR /app
COPY requirements.txt .


# Copy Zscaler root certificate into the trusted CA store
COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Set permissions and update CA certificates inside the container
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt && update-ca-certificates

# Set environment variables so Python and pip use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONUNBUFFERED=1


# 2. Update system and install CA certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y curl



# 3. Install dependencies with trusted hosts
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# 4. Copy application code
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]

