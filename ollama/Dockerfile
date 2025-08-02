FROM ollama/ollama:latest

# Install CA certificates utilities
USER root
RUN apt-get update && apt-get install -y ca-certificates

# Copy Zscaler root certificate into the trusted CA store
COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Set permissions and update CA certificates inside the container
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt && update-ca-certificates

# Set environment variables so Python and pip use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONUNBUFFERED=1

# Expose the Ollama server port
EXPOSE 11434

# Copy the startup script into the container
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Use the startup script as the entrypoint
ENTRYPOINT ["/startup.sh"]
