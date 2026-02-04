# Deployment Documentation

> Installation and deployment guides for Vaultize Analytics Platform

---

## Overview

This section contains everything you need to deploy the Vaultize Analytics Platform in various environments.

---

## Documents

### [Quick Start](./quickstart.md)
Get the platform running locally in under 10 minutes.

**Topics Covered**:
- Prerequisites check
- Quick installation steps
- Verify deployment
- Access the platform

**Status**: 🔴 Not Started

---

### [Prerequisites](./prerequisites.md)
System requirements and dependencies.

**Topics Covered**:
- Hardware requirements
- Software dependencies
- Network requirements
- Storage requirements
- OS compatibility

**Status**: 🔴 Not Started

---

### [Docker Compose Deployment](./docker-compose.md)
Complete guide for Docker Compose deployment (recommended for most use cases).

**Topics Covered**:
- Architecture for Docker Compose
- Step-by-step deployment
- Configuration options
- Multi-node setup
- Production considerations

**Status**: 🔴 Not Started

---

### [Kubernetes Deployment](./kubernetes.md)
Deploy to Kubernetes for enterprise scale.

**Topics Covered**:
- Kubernetes requirements
- Helm charts (if available)
- Namespace setup
- Storage classes
- Ingress configuration
- Scaling configuration

**Status**: 🔴 Not Started

---

### [Configuration Reference](./configuration.md)
Complete configuration options reference.

**Topics Covered**:
- Environment variables
- Configuration files
- OpenSearch settings
- Fluent Bit configuration
- Service configurations
- Security settings

**Status**: 🔴 Not Started

---

### [Environment Setup](./environment-setup.md)
Setting up development vs. production environments.

**Topics Covered**:
- Development environment
- Staging environment
- Production environment
- Environment-specific configurations
- Resource sizing by environment

**Status**: 🔴 Not Started

---

### [Upgrading](./upgrading.md)
How to upgrade to newer versions.

**Topics Covered**:
- Upgrade process
- Backup before upgrade
- Rolling upgrades
- Rollback procedures
- Breaking changes by version

**Status**: 🔴 Not Started

---

## Deployment Paths

### Path 1: Local Development (Recommended for Testing)
```bash
# Clone repository
git clone <repo-url>
cd vaultize-analytics

# Start all services
docker compose up -d

# Verify deployment
./scripts/ops/health-check.sh

# Access OpenSearch Dashboards
open http://localhost:5601
```

**Use Case**: Local development, testing, proof of concept

---

### Path 2: On-Premise Production (Docker Compose)
```bash
# Clone repository on production server
git clone <repo-url>
cd vaultize-analytics

# Configure for production
cp .env.example .env.production
# Edit .env.production with production settings

# Deploy with production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Initialize cluster
./scripts/ops/bootstrap.sh

# Verify deployment
./scripts/ops/health-check.sh
```

**Use Case**: Small to medium deployments, single-server or few-server setups

---

### Path 3: Kubernetes Production (Enterprise Scale)
```bash
# Configure kubectl context
kubectl config use-context production

# Create namespace
kubectl create namespace vaultize-analytics

# Apply configurations
kubectl apply -f infrastructure/kubernetes/base/

# Apply environment-specific overlays
kubectl apply -k infrastructure/kubernetes/overlays/prod/

# Verify deployment
kubectl get pods -n vaultize-analytics
```

**Use Case**: Large-scale deployments, high availability, enterprise environments

---

## Architecture Comparison

| Feature | Docker Compose | Kubernetes |
|---------|----------------|------------|
| **Complexity** | Low | High |
| **Scale** | Up to ~100K logs/sec | Unlimited |
| **HA** | Limited | Full |
| **Auto-scaling** | Manual | Automatic |
| **Resource Management** | Basic | Advanced |
| **Multi-node** | Manual | Built-in |
| **Best For** | Small-Medium | Enterprise |

---

## Quick Reference

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB (plus log retention)
- **OS**: Linux (Ubuntu 20.04+, RHEL 8+, etc.)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Recommended Production
- **CPU**: 16+ cores
- **RAM**: 32+ GB
- **Storage**: 500+ GB SSD (for OpenSearch data)
- **Network**: 1 Gbps+
- **OpenSearch Nodes**: 3+ (for HA)

---

## Common Deployment Scenarios

1. **Single-Server Development**
   - 1 OpenSearch node
   - All services on one host
   - SQLite for alert state
   - Use: Development, testing

2. **Multi-Server Production**
   - 3+ OpenSearch nodes
   - Separate ingestion tier
   - External database for alert state
   - Use: Production deployments

3. **Kubernetes Cluster**
   - OpenSearch StatefulSet
   - Auto-scaling ingestion
   - Persistent volumes
   - Use: Enterprise scale

---

## Next Steps

1. Review [Prerequisites](./prerequisites.md)
2. Follow [Quick Start](./quickstart.md) for local deployment
3. For production, see [Docker Compose Deployment](./docker-compose.md)
4. Configure based on [Configuration Reference](./configuration.md)

---

**Last Updated**: 2026-02-04
