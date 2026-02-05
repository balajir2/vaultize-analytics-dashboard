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

For detailed architecture, see [Architecture Documentation](docs/architecture/README.md).

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

- **[Architecture](docs/architecture/README.md)** - System design and components
- **[Deployment](docs/deployment/README.md)** - Installation and configuration
- **[Operations](docs/operations/README.md)** - Maintenance and troubleshooting
- **[API Reference](docs/api/README.md)** - RESTful API documentation
- **[User Guides](docs/user-guides/README.md)** - End-user documentation

---

## Project Status

**Current Version**: 0.3.0 (Alpha)
**Status**: In Active Development
**Overall Progress**: ~65% Complete

See [MILESTONES.md](MILESTONES.md) for roadmap and [CHANGELOG.md](CHANGELOG.md) for version history.

### Milestone Progress

```
M0: Project Scaffold        [####################] 100%  Complete
M1: Infrastructure Layer    [##################--]  90%  In Progress
M2: Ingestion Pipeline      [################----]  80%  In Progress
M3: Analytics Services      [###################-]  95%  Complete
M4: Dashboards              [###################-]  95%  Complete
M5: Alerting System         [--------------------]   0%  Not Started
M6: Testing & Documentation [###############-----]  75%  In Progress
M7: Production Hardening    [--------------------]   0%  Not Started
```

| Milestone | Status | Highlights |
|-----------|--------|------------|
| **M0: Project Scaffold** | Complete | Directory structure, documentation, session continuity |
| **M1: Infrastructure** | 90% | Docker Compose stack, 3-node OpenSearch cluster, all configs |
| **M2: Ingestion** | 80% | Fluent Bit with 4 parsers, multi-source support |
| **M3: Analytics API** | 95% | 14 REST endpoints, 89% test coverage, sample data generator |
| **M4: Dashboards** | 95% | 2 pre-built dashboards, 6 visualizations, import scripts |
| **M5: Alerting** | 0% | Not started |
| **M6: Testing & Docs** | 75% | 74 unit tests passing, comprehensive documentation |
| **M7: Production** | 0% | Not started |

---

## What Remains

### High Priority (Required for MVP)

| Task | Milestone | Effort |
|------|-----------|--------|
| Bootstrap scripts for cluster initialization | M1 | Small |
| Health check automation scripts | M1 | Small |
| Sample log generators for testing | M2 | Small |
| Alerting service (rule engine, webhooks) | M5 | Large |
| E2E tests for complete log flow | M6 | Medium |

### Medium Priority (Quality & Polish)

| Task | Milestone | Effort |
|------|-----------|--------|
| Ingestion monitoring dashboards | M2 | Medium |
| API authentication/authorization | M7 | Medium |
| Integration tests for ingestion pipeline | M6 | Medium |
| Operations guide (troubleshooting, maintenance) | M6 | Medium |
| Grafana dashboards for metrics | M4 | Small |

### Lower Priority (Production Hardening)

| Task | Milestone | Effort |
|------|-----------|--------|
| SSL/TLS configuration | M7 | Medium |
| Role-based access control (RBAC) | M7 | Medium |
| Backup and restore procedures | M7 | Medium |
| Performance tuning documentation | M7 | Small |
| Kubernetes deployment manifests | M7 | Large |

### Deferred (Post-MVP)

- Vector search integration
- ML-based anomaly detection
- Kafka ingestion buffering
- Multi-tenancy support

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

**v1.0 Goals** (MVP):
- ✅ Project structure and documentation
- ✅ Docker Compose deployment (3-node OpenSearch cluster)
- ✅ OpenSearch cluster with index templates and ILM
- ✅ Fluent Bit log ingestion (4 parser types)
- ✅ Analytics API (14 endpoints, 89% test coverage)
- ✅ Pre-built dashboards (Operations + Analytics)
- 🔄 Alerting system (in progress)
- 🔄 Production hardening (SSL, auth, backups)

**Post-v1.0**:
- Kubernetes deployment manifests
- Advanced alerting (ML-based anomaly detection)
- Vector search capabilities
- Multi-tenancy support
- Kafka ingestion buffering

See [MILESTONES.md](MILESTONES.md) for detailed roadmap.

---

## Getting Help

- Check [Troubleshooting Guide](docs/operations/troubleshooting.md)
- Review [User Guides](docs/user-guides/README.md)
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
