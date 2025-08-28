# NeonHud container (final polished dev+demo image)
FROM python:3.13-slim

LABEL org.opencontainers.image.title="NeonHud" \
      org.opencontainers.image.description="Linux-native performance HUD with cyberpunk TUI" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/<yourusername>/NeonHud"

# Install build deps (psutil needs gcc/libffi), then clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev \
 && pip install --upgrade pip \
 && apt-get purge -y gcc libffi-dev \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

# Install NeonHud + dev extras
RUN pip install -e .[dev]

# Entrypoint wrapper
COPY docker/entrypoint.sh /usr/local/bin/neonhud-entrypoint
RUN chmod +x /usr/local/bin/neonhud-entrypoint

ENTRYPOINT ["neonhud-entrypoint"]
CMD ["--help"]
