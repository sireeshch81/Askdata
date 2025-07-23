# Use Python 3.12.3 base image
FROM python:3.12.3-slim-bookworm

# 1. Update system and install CA certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 2. Set working directory and copy requirements
WORKDIR /app
COPY requirements.txt .

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

