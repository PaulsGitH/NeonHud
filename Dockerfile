# NeonHud base container
# Dev-focused image: lightweight, Python + tooling, not yet optimized for production

FROM python:3.13-slim

# System deps for psutil and other optional tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create working dir
WORKDIR /app

# Install NeonHud in editable mode
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip \
    && pip install -e .[dev]

# Default command: show help
ENTRYPOINT ["neonhud"]
CMD ["--help"]
