# Stage 1: Builder
FROM ubuntu:noble AS builder

LABEL authors="AskData Team 2"

# Configure apt for better reliability
RUN echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout \
    && echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install ca-certificates first so update-ca-certificates is available
RUN apt-get update -y && apt-get install -y --no-install-recommends ca-certificates

# Copy Zscaler root certificate into the trusted CA store
COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Set permissions and update CA certificates inside the container
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt \
    && update-ca-certificates

# Set environment variables so Python and requests use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install system dependencies
RUN apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    unzip \
    wget \
    libpq-dev \
    unixodbc-dev \
    python3.12-full \
    python3.12-dev \
    python3-venv \
    libkrb5-dev \
    krb5-config \
    krb5-user \
    libaio-dev \
    alien \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
#RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
#ENV PATH="/root/.cargo/bin:${PATH}"

# Install Java
RUN curl -O https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/openjdk-21.0.2_linux-x64_bin.tar.gz \
    && tar -xf openjdk-21.0.2_linux-x64_bin.tar.gz \
    && rm openjdk-21.0.2_linux-x64_bin.tar.gz \
    && mkdir -p /usr/lib/jvm \
    && mv jdk-21.0.2 /usr/lib/jvm/openjdk-21

WORKDIR /app

# Copy requirements file and source files
COPY pyproject.toml .
COPY requirements.txt .

# Install/update pip and create virtual environment
RUN python3.12 -m venv /app/.venv \
    && . /app/.venv/bin/activate \
    && python3.12 -m ensurepip --upgrade \
    && pip install --upgrade pip \
    && pip install uv

# Install JupyterLab and essential packages first
RUN . /app/.venv/bin/activate && uv pip install --no-cache-dir \
    "pandas>=2.2.0" \
    jupyterlab \
    ipykernel

# Install Tableau Hyper API first (if available)
RUN . /app/.venv/bin/activate && uv pip install --no-cache-dir tableauhyperapi pantab || echo "tableauhyperapi or pantab not available"

# Then install other requirements
RUN . /app/.venv/bin/activate && uv pip install -r requirements.txt --no-cache-dir

# Install Python packages and stringcompare
RUN . /app/.venv/bin/activate \
    && uv pip install --upgrade certifi \
    && python3 -m pip install --upgrade setuptools wheel pip \
    && uv pip install ipykernel \
    && python3 -m ipykernel install --sys-prefix


# Stage 2: Runtime
FROM ubuntu:noble AS runtime

LABEL authors="AskData Team 2"

# Set SageMaker specific parameters
ARG APPUSER="appuser"
ARG APPUSER_UID=2000
ARG APPUSER_GID=100

# Configure apt for better reliability
RUN echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout \
    && echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install ca-certificates first in runtime stage and add Zscaler cert before any apt operations
RUN apt-get update -y && apt-get install -y --no-install-recommends ca-certificates

# Copy Zscaler root certificate from builder to runtime
COPY --from=builder /usr/local/share/ca-certificates/zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

# Update CA certificates in runtime
RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt \
    && update-ca-certificates

# Set SSL env vars
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install only runtime dependencies
RUN apt-get update -y && apt-get upgrade -y \
    # TODO: Remove sudo & vim once image is stable
    && apt-get install -y --no-install-recommends software-properties-common sudo vim netcat-openbsd \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install -y --no-install-recommends \
    git \
    libpq5 \
    unixodbc \
    python3.12 \
    python3-venv \
    libkrb5-3 \
    krb5-config \
    krb5-user \
    libaio1t64 \
    && apt-get remove -y software-properties-common \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Java from builder
COPY --from=builder /usr/lib/jvm/openjdk-21 /usr/lib/jvm/openjdk-21

COPY . .

# Clear out the laptop's VENV if it exists following the copy above
RUN rm -rf /app/.venv/ || true \
    && python3.12 -m venv /app/.venv

# Copy Python virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY server_startup.sh .

ENV JAVA_HOME="/usr/lib/jvm/openjdk-21"
ENV PATH="/app/.venv/bin:${JAVA_HOME}/bin:${PATH}"

# Create SageMaker user and set permissions
RUN useradd -m -s /bin/bash -N -u ${APPUSER_UID} ${APPUSER} \
    && chmod g+w /etc/passwd

# Security cleanup - remove test and key files
RUN rm -rf /usr/lib/python3.12/test/certdata/ || true \
    && rm /app/.venv/lib/python3.12/site-packages/tornado/test/test.key || true

RUN chown -R ${APPUSER}:${APPUSER_GID} /app \
    && chmod +x /app/server_startup.sh \
    && chown ${APPUSER}:${APPUSER_GID} /home \
    && echo "alias ll='ls -lahF'" >> /home/${APPUSER}/.bashrc

USER ${APPUSER}

EXPOSE 5002

CMD ["/app/server_startup.sh"]
