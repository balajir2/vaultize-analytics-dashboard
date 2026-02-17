# Alerting Service - Dockerfile
#
# Multi-stage build for optimized production image
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0

# ============================================================================
# Stage 1: Builder
# ============================================================================

FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================

FROM python:3.11-slim

LABEL maintainer="Balaji Rajan"
LABEL description="Vaultize Alerting Service - Threshold-based alerting for OpenSearch"
LABEL version="0.1.0"

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash alertuser

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/alertuser/.local

# Copy application code
COPY --chown=alertuser:alertuser . /app/

# Set PATH to include user-installed packages
ENV PATH=/home/alertuser/.local/bin:$PATH

# Switch to non-root user
USER alertuser

# Expose management API port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/health/liveness || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
