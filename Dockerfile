# Stage 1: Builder
FROM ubuntu:noble AS builder

LABEL authors="kellyfirkins"

# Configure apt for better reliability
RUN echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout \
    && echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Environment vars for build-time performance
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -y --no-install-recommends ca-certificates

COPY zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt \
    && update-ca-certificates

# Set environment variables so Python and requests use the updated CA cert bundle
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Build-time dependencies
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
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Java
RUN curl -O https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/openjdk-21.0.2_linux-x64_bin.tar.gz \
    && tar -xf openjdk-21.0.2_linux-x64_bin.tar.gz \
    && rm openjdk-21.0.2_linux-x64_bin.tar.gz \
    && mkdir -p /usr/lib/jvm \
    && mv jdk-21.0.2 /usr/lib/jvm/openjdk-21

WORKDIR /app

COPY pyproject.toml .

RUN python3.12 -m venv /app/.venv \
    && . /app/.venv/bin/activate \
    && python3.12 -m ensurepip --upgrade \
    && pip install --upgrade pip \
    && pip install uv

RUN . /app/.venv/bin/activate && uv pip install --no-cache-dir "pandas>=2.2.0" \
    && uv sync

RUN . /app/.venv/bin/activate \
    && uv pip install --upgrade certifi \
    && python3 -m pip install --upgrade setuptools wheel pip

# Stage 2: runtime
FROM ubuntu:noble AS runtime

LABEL authors="Kelly Firkins"
ARG APPUSER="appuser"
ARG APPUSER_UID=2000
ARG APPUSER_GID=1000

# Configure apt for better reliability
RUN echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout \
    && echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

ENV DEBIAN_FRONTEND=noninteractive

# Install ca-certificates first in runtime stage and add Zscaler cert before any apt operations
RUN apt-get update -y && apt-get install -y --no-install-recommends ca-certificates

# Copy Zscaler root certificate from builder to runtime
COPY --from=builder /usr/local/share/ca-certificates/zscaler-root.crt /usr/local/share/ca-certificates/zscaler-root.crt

RUN chmod 644 /usr/local/share/ca-certificates/zscaler-root.crt \
    && update-ca-certificates

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONUNBUFFERED=1

# Install only runtime dependencies
RUN apt-get update -y && apt-get upgrade -y \
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

COPY --from=builder /usr/lib/jvm/openjdk-21 /usr/lib/jvm/openjdk-21
COPY .env .

# Clear out the laptop's VENV if it exists following the copy above
RUN rm -rf /app/.venv/ || true \
    && python3.12 -m venv /app/.venv

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:${PATH}"

RUN useradd -m -s /bin/bash -U -u ${APPUSER_UID} ${APPUSER} \
    && chmod g+w /etc/passwd

RUN rm -rf /usr/lib/python3.12/test/certdata/ || true \
    && rm /app/.venv/lib/python3.12/site-packages/tornado/test/test.key || true

RUN touch /app/server_startup.sh && chown -R ${APPUSER}:users /app

#USER ${APPUSER}

EXPOSE 6000

# CMD ["/app/server_startup.sh"]
CMD ["/bin/bash"]