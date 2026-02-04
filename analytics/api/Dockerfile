# Analytics API - Dockerfile
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
LABEL description="Vaultize Analytics API - RESTful API for OpenSearch"
LABEL version="0.1.0"

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash apiuser

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/apiuser/.local

# Copy application code
COPY --chown=apiuser:apiuser . /app/

# Set PATH to include user-installed packages
ENV PATH=/home/apiuser/.local/bin:$PATH

# Switch to non-root user
USER apiuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
