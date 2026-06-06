# Ubuntu 23.10 (Mantic Minotaur) uses Glibc 2.38 natively
FROM ubuntu:23.10

# Switch to old-releases mirrors since 23.10 is EOL (End of Life)
RUN sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list

# Install essential compilation, debugging, and exploitation tools
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gdb \
    make \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    patchelf \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory inside the container
WORKDIR /challenge

# Copy all files from your current host directory into the container
COPY . .

# Default command leaves a bash shell open
CMD ["/bin/bash"]
