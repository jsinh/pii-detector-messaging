# syntax=docker/dockerfile:1

# ---- Base image -------------------------------------------------------------
# Slim Debian-based image: small, glibc-based (broad wheel compatibility),
# multi-architecture (works on Intel and Apple Silicon / arm64).
FROM python:3.13-slim AS runtime

# Predictable Python behaviour in containers.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy only what's needed to install the package. Copying metadata + source
# (not tests/data) keeps the build context lean and the image small.
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# Install the package and its runtime dependencies (no dev extras).
RUN pip install --upgrade pip && pip install .

# Run as an unprivileged user, not root.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Container-facing configuration (override at `docker run` time with -e).
ENV PII_HOST=0.0.0.0 \
    PII_PORT=8000 \
    PII_ENVIRONMENT=production

EXPOSE 8000

# Liveness check using only the stdlib (curl isn't in the slim image).
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request as u, sys; sys.exit(0 if u.urlopen('http://127.0.0.1:8000/healthz').status == 200 else 1)"

# The installed console script — the same entry point as `make run`.
CMD ["pii-detector"]
