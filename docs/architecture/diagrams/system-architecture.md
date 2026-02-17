# System Architecture Diagrams

Visual documentation of the Vaultize Analytics Platform architecture.

## Data Flow

```mermaid
graph LR
    subgraph Sources
        A[Application Logs] --> |file tail| FB
        B[Syslog / Network] --> |forward protocol| FB
        C[Custom Scripts] --> |REST API| FB
    end

    subgraph Ingestion
        FB[Fluent Bit] --> |HTTP/HTTPS| OS
    end

    subgraph Storage & Search
        OS[OpenSearch Cluster]
        OS1[Node 1] --- OS
        OS2[Node 2] --- OS
        OS3[Node 3] --- OS
    end

    subgraph Services
        API[Analytics API] --> |queries| OS
        ALT[Alerting Service] --> |queries| OS
        ALT --> |state/history| OS
    end

    subgraph Visualization
        OSD[OpenSearch Dashboards] --> |queries| OS
        GF[Grafana] --> |queries| OS
        GF --> |metrics| PM[Prometheus]
    end

    subgraph Users
        U[Users/Operators] --> API
        U --> OSD
        U --> GF
    end
```

## Network Architecture

```mermaid
graph TB
    subgraph Docker Network - vaultize-network [172.25.0.0/16]
        subgraph OpenSearch Cluster
            OS1[opensearch-node-1<br/>:9200]
            OS2[opensearch-node-2<br/>:9201]
            OS3[opensearch-node-3<br/>:9202]
        end

        OSD[OpenSearch Dashboards<br/>:5601]
        FB[Fluent Bit<br/>:24224, :2020]
        API[Analytics API<br/>:8000]
        ALT[Alerting Service<br/>:8001]
        PM[Prometheus<br/>:9090]
        GF[Grafana<br/>:3000]
    end

    EXT[External Access] --> |:5601| OSD
    EXT --> |:8000| API
    EXT --> |:8001| ALT
    EXT --> |:9200| OS1
    EXT --> |:3000| GF
```

## Security Architecture

```mermaid
graph TB
    subgraph External
        U[User/Client]
    end

    subgraph Auth Layer
        JWT[JWT Authentication<br/>AUTH_ENABLED=true]
        RL[Rate Limiting<br/>per-IP token bucket]
    end

    subgraph TLS Layer
        CERT[TLS Certificates<br/>Self-signed CA]
    end

    subgraph OpenSearch Security
        SEC[Security Plugin<br/>internal_users.yml]
        RBAC[Role-Based Access<br/>roles.yml]
    end

    U --> |HTTPS + Bearer token| JWT
    JWT --> |validated| RL
    RL --> |allowed| API[Analytics API]
    API --> |HTTPS + Basic Auth| SEC
    SEC --> |authorized| RBAC
    RBAC --> |permitted| OS[(OpenSearch)]

    FB[Fluent Bit] --> |HTTPS + Basic Auth| SEC
    ALT[Alerting Service] --> |HTTPS + Basic Auth| SEC
```

## Alerting Pipeline

```mermaid
sequenceDiagram
    participant Scheduler
    participant Engine as Alert Engine
    participant OS as OpenSearch
    participant WH as Webhook Receiver

    loop Every evaluation interval
        Scheduler->>Engine: Trigger evaluation
        Engine->>OS: Execute alert query
        OS-->>Engine: Query results
        Engine->>Engine: Compare threshold
        alt Threshold exceeded
            Engine->>Engine: Update state: OK → FIRING
            Engine->>OS: Write alert history
            Engine->>WH: POST notification
        else Below threshold
            alt Was FIRING
                Engine->>Engine: Update state: FIRING → RESOLVED
                Engine->>OS: Write resolution history
                Engine->>WH: POST resolution
            end
        end
    end
```

## Deployment Modes

### Development Mode (Default)

```
docker compose up -d
```

- Security plugin: **disabled**
- Authentication: **disabled**
- CORS: **allow all**
- TLS: **off**

### Secure Mode

```
bash scripts/ops/start_secure.sh
```

- Security plugin: **enabled**
- Authentication: **enabled** (JWT)
- CORS: **restricted**
- TLS: **on** (self-signed CA)

## Component Summary

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| OpenSearch (x3) | OpenSearch 2.11.1 | 9200-9202 | Search & analytics engine |
| OpenSearch Dashboards | OSD 2.11.1 | 5601 | Visualization UI |
| Fluent Bit | Fluent Bit 2.2.0 | 24224, 2020 | Log ingestion |
| Analytics API | FastAPI (Python) | 8000 | REST API for search/agg |
| Alerting Service | FastAPI (Python) | 8001 | Alert evaluation & notification |
| Prometheus | Prometheus v2.48.1 | 9090 | Metrics collection (optional) |
| Grafana | Grafana 10.2.3 | 3000 | Unified dashboards (optional) |
