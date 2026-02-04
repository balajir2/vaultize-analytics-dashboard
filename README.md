# Vaultize Analytics Dashboard

An on-premise analytics and observability platform inspired by Splunk, built entirely using open-source components.

## Overview

This platform provides:
- Centralized log ingestion
- Search and analytics over logs/events
- Dashboards and visualizations
- Alerting on log-derived signals
- Optional metrics integration

## Architecture

```
Applications / Servers
        |
        v
  Fluent Bit / Logstash
        |
        v
   OpenSearch Cluster
        |
        v
 OpenSearch Dashboards
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Search Engine | OpenSearch (self-hosted) |
| Visualization | OpenSearch Dashboards, Grafana (optional) |
| Log Ingestion | Fluent Bit (primary), Logstash (optional) |
| Metrics | Prometheus (optional) |
| Services | Python 3.11+ with FastAPI |
| Deployment | Docker Compose |

## Project Structure

```
infrastructure/   - Deployment configs, Docker Compose
ingestion/        - Log collection pipelines and agents
analytics/        - Services (API, alerting, indexing)
configs/          - Index templates, ILM policies, alert rules
dashboards/       - Saved visualizations and dashboards
scripts/          - Operational tooling
docs/             - Architecture and usage documentation
tests/            - Unit, integration, regression, and E2E tests
tools/            - Development utilities
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### Running Locally

```bash
# Clone the repository
git clone https://github.com/balajir2/vaultize-analytics-dashboard.git
cd vaultize-analytics-dashboard

# Start the stack
docker-compose up -d

# Access OpenSearch Dashboards
open http://localhost:5601
```

## Design Principles

- **On-Prem Only**: No cloud dependencies, fully self-hosted
- **Configuration-Driven**: YAML/JSON configs over hardcoded logic
- **Logs First**: Primary focus on log analytics
- **Simple Deployment**: Docker Compose for v1, Kubernetes later

## Documentation

- [Architecture Overview](docs/architecture/README.md)
- [Tech Stack Details](docs/architecture/tech-stack.md)
- [Deployment Guide](docs/deployment/README.md)
- [API Documentation](docs/api/README.md)
- [Operations Guide](docs/operations/README.md)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=analytics --cov=ingestion --cov-report=html
```

## License

This project is open source. See LICENSE for details.

## Contributing

Contributions are welcome. Please read the contributing guidelines before submitting pull requests.
