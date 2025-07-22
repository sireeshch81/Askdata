FROM ubuntu:noble AS builder

# Configure apt for better reliability
RUN echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout \
    && echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends software-properties-common \
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

# Create a non-root user and set permissions in builder
RUN useradd --create-home --shell /bin/bash appuser \
    && echo "alias ll='ls -lahF'" >> /home/appuser/.bashrc \
    && chown -R appuser:appuser /home/appuser \
    && chown -R appuser:appuser /app

USER appuser

# Create virtual environment and install dependencies as appuser
RUN python3.12 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && python3.12 -m ensurepip --upgrade \
    && pip install --upgrade pip \
    && pip install uv \
    && uv pip install --no-cache-dir \
        "pandas>=2.2.0" \
        jupyterlab \
        ipykernel \
    && uv pip install --upgrade certifi \
    && python3 -m pip install --upgrade setuptools wheel pip \
    && uv sync --active

USER root

FROM ubuntu:noble AS runtime

LABEL authors="AskData Team 2"

WORKDIR /app

# Configure apt for better reliability
RUN echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout \
    && echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and system tools
COPY pyproject.toml .
COPY server_startup.sh .

# Install only runtime dependencies
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends software-properties-common netcat-openbsd \
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

# Copy Java from builder
COPY --from=builder /usr/lib/jvm/openjdk-21 /usr/lib/jvm/openjdk-21

# Create a non-root user and set permissions in runtime
RUN useradd --create-home --shell /bin/bash appuser \
    && echo "alias ll='ls -lahF'" >> /home/appuser/.bashrc

# Copy Python virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Set Java environment variables
ENV JAVA_HOME="/usr/lib/jvm/openjdk-21"
ENV PATH="${JAVA_HOME}/bin:/app/venv/bin:${PATH}"

COPY . .

RUN chmod +x server_startup.sh \
    && chown -R appuser:appuser /app \
    && chown appuser:appuser server_startup.sh

USER appuser

EXPOSE 5002

CMD ["/app/server_startup.sh"]
