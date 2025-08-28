# NeonHud base container (dev-oriented)
FROM python:3.13-slim

# System deps for psutil and friends
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy project metadata first (better layer caching)
COPY pyproject.toml README.md ./
# Copy source
COPY src ./src

# Install project + dev tools (editable for quick iteration)
RUN pip install --upgrade pip \
    && pip install -e .[dev]

# Runtime entrypoint (shell wrapper that forwards args to `neonhud`)
COPY docker/entrypoint.sh /usr/local/bin/neonhud-entrypoint
RUN chmod +x /usr/local/bin/neonhud-entrypoint

# Default: show CLI help (can be overridden by `docker run ... <cmd>`)
ENTRYPOINT ["neonhud-entrypoint"]
CMD ["--help"]
