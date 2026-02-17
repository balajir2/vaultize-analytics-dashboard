# Vaultize Analytics Platform

> **On-Premise Log Analytics and Observability Platform**
>
> An open-source, self-hosted analytics platform comparable to Splunk, built with OpenSearch

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE.md)
[![OpenSearch](https://img.shields.io/badge/OpenSearch-2.x-blue)](https://opensearch.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue)](https://www.docker.com/)

---

## Overview

**Vaultize Analytics Platform** is a production-grade, on-premise log analytics and observability solution built entirely with open-source components. It provides enterprise-level capabilities for log ingestion, search, analytics, visualization, and alerting - all self-hosted with no cloud dependencies.

### Key Features

- 🔍 **Full-Text Search**: Powerful search capabilities powered by OpenSearch
- 📊 **Dashboards & Visualizations**: Interactive dashboards via OpenSearch Dashboards
- 🚨 **Alerting**: Threshold-based alerts with webhook notifications
- 📥 **Log Ingestion**: High-performance log collection with Fluent Bit
- 📈 **Metrics (Optional)**: System metrics via Prometheus and Grafana
- 🔐 **Security**: Built-in authentication, authorization, and TLS
- 🏢 **On-Premise**: 100% self-hosted, no cloud dependencies
- 📖 **Open Source**: Apache 2.0 license

---

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB+ recommended)
- 50GB disk space (plus log retention)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd vaultize-analytics

# Start the platform
docker compose up -d

# Verify all services are healthy
./scripts/ops/health-check.sh

# Access OpenSearch Dashboards
open http://localhost:5601
```

**Default Credentials**: `admin` / `admin` (change immediately!)

For detailed installation instructions, see [Deployment Guide](docs/deployment/quickstart.md).

---

## Architecture

```
Applications / Servers
        |
        v
  Fluent Bit (Log Collection)
        |
        v
   OpenSearch Cluster (Search & Analytics)
        |
        ├──> OpenSearch Dashboards (Visualization)
        ├──> Analytics API (RESTful API)
        ├──> Alerting Service (Threshold Alerts)
        └──> Grafana (Optional: Metrics + Logs)
             ↑
        Prometheus (Optional: Metrics)
```

For detailed architecture, see [Technology Stack](docs/architecture/tech-stack.md) and [System Architecture Diagrams](docs/architecture/diagrams/system-architecture.md).

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Search & Analytics** | OpenSearch 2.11 | Core engine - stores, indexes, and queries log data with full-text search and aggregations |
| **Visualization** | OpenSearch Dashboards 2.11 | Primary UI - interactive dashboards, log discovery, and visualizations |
| **Log Ingestion** | Fluent Bit 2.2 | Lightweight collector - parses logs from files, syslog, Docker and forwards to OpenSearch |
| **Metrics** | Prometheus 2.48 | Time-series database for system metrics and application performance (optional) |
| **Unified Dashboards** | Grafana 10.2 | Combined logs + metrics visualization with alerting capabilities (optional) |
| **API Services** | Python 3.11 + FastAPI | RESTful API - programmatic access to search, aggregations, and index management |
| **Deployment** | Docker + Docker Compose | Container orchestration - single-command deployment of entire stack |

### Why These Technologies?

| Choice | Rationale |
|--------|-----------|
| **OpenSearch over Elasticsearch** | Truly open-source (Apache 2.0), no licensing concerns, active community |
| **Fluent Bit over Logstash** | 10x lighter (~450KB vs ~1GB), written in C, minimal resource footprint |
| **FastAPI over Flask/Django** | Modern async support, automatic OpenAPI docs, Pydantic validation |
| **Docker Compose over Kubernetes** | Simpler for on-prem, faster iteration, sufficient for 100K logs/sec |

See [Technology Stack](docs/architecture/tech-stack.md) for complete details.

---

## Documentation

All documentation is accessible from the **[Documentation Hub](docs/README.md)**, including:

- **[Quick Start](docs/deployment/quickstart.md)** - Get running in minutes
- **[Technology Stack](docs/architecture/tech-stack.md)** - Component choices and rationale
- **[Configuration](docs/deployment/configuration.md)** - Environment variables and settings
- **[Testing Guide](docs/operations/testing-guide.md)** - Manual testing walkthrough (Tests 1-8)
- **[Security Hardening](docs/operations/security-hardening-checklist.md)** - Production security
- **[User Guides](docs/user-guides/README.md)** - Search cheat sheet, use cases, best practices
- **API Reference** - Interactive Swagger UI at `http://localhost:8000/docs`

---

## Project Status

**Current Version**: 1.0.0
**Status**: Complete
**Overall Progress**: 100%

See [MILESTONES.md](MILESTONES.md) for roadmap and [CHANGELOG.md](CHANGELOG.md) for version history.

### Milestone Progress

```
M0: Project Scaffold        [####################] 100%  Complete
M1: Infrastructure Layer    [####################] 100%  Complete
M2: Ingestion Pipeline      [####################] 100%  Complete
M3: Analytics Services      [####################] 100%  Complete
M4: Dashboards              [####################] 100%  Complete
M5: Alerting System         [####################] 100%  Complete
M6: Testing & Documentation [####################] 100%  Complete
M7: Production Hardening    [####################] 100%  Complete
```

| Milestone | Highlights |
|-----------|------------|
| **M0: Project Scaffold** | Directory structure, documentation, session continuity |
| **M1: Infrastructure** | Docker Compose stack, 3-node OpenSearch cluster, all configs |
| **M2: Ingestion** | Fluent Bit with 4 parsers, multi-source support, sample logs |
| **M3: Analytics API** | 17 REST endpoints, 89% test coverage, JWT auth |
| **M4: Dashboards** | 2 OpenSearch dashboards + 1 Grafana dashboard, import scripts |
| **M5: Alerting** | Threshold-based alerts, webhook notifications, state management |
| **M6: Testing & Docs** | 437 tests passing, 34 docs with zero dead links |
| **M7: Production** | TLS, RBAC, backup/restore, security hardening, ops scripts |

### Test Results

| Suite | Tests | Coverage |
|-------|-------|----------|
| Analytics API | 98 passing | 89% |
| Alerting Service | 101 passing | 81% |
| Regression (RT-001 to RT-018) | 238 passing | — |
| **Total** | **437 passing** | **>80%** |

---

## Contributing

We welcome contributions! Please see:

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [AUTHORS.md](AUTHORS.md) - Author and contributor list
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community guidelines

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch
3. Make your changes **with tests**
4. Update documentation
5. Submit a pull request

All contributions must include tests (see [Testing Requirements](tests/README.md)).

---

## Testing

This project maintains high testing standards:

- **Unit Tests**: >80% coverage required
- **Integration Tests**: All service integrations tested
- **Regression Tests**: Every bug fix requires a regression test
- **E2E Tests**: Critical user flows covered

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/regression/
```

See [Testing Documentation](tests/README.md) for details.

---

## Use Cases

- **Application Logging**: Centralized logs from microservices and applications
- **Infrastructure Monitoring**: Server and container logs with metrics
- **Security Auditing**: Authentication logs, access logs, security events
- **Troubleshooting**: Root cause analysis with full-text search
- **Compliance**: Log retention and audit trails
- **Performance Analysis**: Application performance metrics and trends

---

## Comparison

| Feature | Vaultize | Splunk | ELK Stack | Cloud Services |
|---------|----------|--------|-----------|----------------|
| **Cost** | Free (open-source) | Expensive | Free | Pay-as-you-go |
| **Deployment** | On-premise | On-prem or Cloud | On-premise | Cloud only |
| **License** | Apache 2.0 | Proprietary | Mixed (SSPL/AGPL) | Proprietary |
| **Data Sovereignty** | ✅ Full control | ✅ On-prem option | ✅ Full control | ❌ Cloud vendor |
| **Complexity** | Medium | High | High | Low |
| **Scalability** | High | Very High | High | Very High |

---

## License

This project is licensed under the **Apache License 2.0** - see [LICENSE.md](LICENSE.md) for details.

**TL;DR**: Free to use, modify, and distribute with attribution. No warranty provided.

### Third-Party Licenses

- OpenSearch: Apache 2.0
- Fluent Bit: Apache 2.0
- Prometheus: Apache 2.0
- Grafana: AGPL 3.0 (optional component)

See [Technology Stack](docs/architecture/tech-stack.md) for complete license information.

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

For commercial support inquiries, contact the project maintainers.

---

## Acknowledgments

Built with these excellent open-source projects:

- [OpenSearch](https://opensearch.org/) - Search and analytics
- [Fluent Bit](https://fluentbit.io/) - Log collection
- [Prometheus](https://prometheus.io/) - Metrics monitoring
- [Grafana](https://grafana.com/) - Visualization
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework

Special thanks to the entire open-source community.

---

## Authors

**Original Authors**:
- **Balaji Rajan** - Project Creator & Lead Developer
- **Claude (Anthropic)** - AI Co-Author & Development Assistant

See [AUTHORS.md](AUTHORS.md) for complete contributor list.

---

## Roadmap

**v1.0** (Complete):
- ✅ Project structure and documentation
- ✅ Docker Compose deployment (3-node OpenSearch cluster)
- ✅ OpenSearch cluster with index templates and ILM
- ✅ Fluent Bit log ingestion (4 parser types)
- ✅ Analytics API (17 endpoints, 89% test coverage, JWT auth)
- ✅ Pre-built dashboards (2 OpenSearch + 1 Grafana)
- ✅ Alerting system (threshold rules, webhooks, state management)
- ✅ Production hardening (TLS, RBAC, backup/restore, ops scripts)

**Post-v1.0** (Future):
- Kubernetes deployment manifests
- Advanced alerting (ML-based anomaly detection)
- Vector search capabilities
- Multi-tenancy support
- Kafka ingestion buffering

See [MILESTONES.md](MILESTONES.md) for detailed roadmap.

---

## Getting Help

- Check [Documentation Hub](docs/README.md)
- Review [User Guides](docs/user-guides/README.md)
- Review [Testing Guide](docs/operations/testing-guide.md)
- Search [existing issues](../../issues)
- Ask in [Discussions](../../discussions)

---

## Security

For security vulnerabilities, please email [security@example.com] instead of creating a public issue.

See [SECURITY.md](SECURITY.md) for our security policy.

---

**Star ⭐ this repo if you find it useful!**

---

<div align="center">

**Copyright © 2026 Balaji Rajan and Claude (Anthropic)**

Licensed under Apache License 2.0 | [Documentation](docs/) | [Contributing](CONTRIBUTING.md) | [License](LICENSE.md)

</div>
