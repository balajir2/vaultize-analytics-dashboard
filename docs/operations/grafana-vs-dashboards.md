# Grafana vs OpenSearch Dashboards — When to Use Which

> **Decision guide**: Both tools are deployed in the Vaultize Analytics Platform.
> This document explains what each is good for and which to use for any given task.

---

## One-Line Answer

- **OpenSearch Dashboards** — for everything Vaultize: DLP analytics, file journeys, tenant dashboards, search
- **Grafana** — for system health and infrastructure monitoring of the platform itself

---

## The Core Difference

| | OpenSearch Dashboards | Grafana |
|---|---|---|
| **Data source** | OpenSearch (logs, events, documents) | Prometheus (metrics, time-series) |
| **What it shows** | "What happened to this file / user?" | "Is the platform healthy?" |
| **Primary user** | Vaultize customer (tenant admin, analyst) | Vaultize platform operator |
| **Multi-tenancy** | Yes — each customer sees only their data (DLS) | No — single shared view |
| **Full-text search** | Yes — search by file name, user, content | No |
| **Aggregations** | Yes — pivot on any field | Limited (metric only) |
| **Alerting** | Yes — OpenSearch alerting plugin | Yes — Grafana alerts |

---

## Use OpenSearch Dashboards for...

### Customer-facing analytics (all DLP use cases)
- **Life Journey of a File** — every event touching a specific file: backups, shares, accesses, DRM operations
- **Life Journey of a User** — everything a user has ever done
- **Sharing activity** — who shared what, with whom, from where
- **Data classification breakdown** — how much PII, financial data, IP is moving
- **Cross-border / sovereignty** — data leaving restricted regions
- **Anomaly investigation** — drill into flagged events
- **Time-of-day patterns** — heatmaps of sharing activity
- **Domain analysis** — which external domains receive data

### Search
- Find any file by name, hash, user, department
- Search event logs across the full 30-day+ history
- Filter by module (CDP, EFSS, DRM, EMAIL)

### Tenant-isolated dashboards
Each customer gets their own **tenant** in Dashboards. Their saved dashboards,
index patterns, and visualizations are completely isolated. One customer cannot
see another customer's saved searches or dashboards.

### URL
`https://vaultize.duckdns.org` (root — goes to OpenSearch Dashboards)

---

## Use Grafana for...

### Platform infrastructure health (operator use)
- OpenSearch cluster health: JVM heap, GC pauses, shard count, indexing rate
- Ingestion pipeline: Fluent Bit buffer size, drop rate, throughput
- API service latency and error rates (from Prometheus)
- Alerting service health
- Host-level: CPU, memory, disk on the EC2 instance

### Why not OpenSearch Dashboards for this?
Prometheus metrics (numeric time-series) are not stored in OpenSearch. They're stored
in Prometheus's own time-series database. Grafana reads from Prometheus directly.
OpenSearch Dashboards can only query OpenSearch.

### URL
`https://vaultize.duckdns.org/grafana/` (subpath)

---

## Decision Flowchart

```
Is the question about customer data?
    Yes → OpenSearch Dashboards
    No  → Is it about platform infrastructure health?
              Yes → Grafana
              No  → Ask yourself: does the data live in OpenSearch or Prometheus?
                        OpenSearch (events, logs, documents) → OpenSearch Dashboards
                        Prometheus (metrics, gauges, counters) → Grafana
```

---

## Alerting — Which Tool?

**OpenSearch Alerting Plugin** (in OpenSearch Dashboards):
- Alert when a customer's data behaviour changes (e.g., "acme-corp shared 10x more files than baseline")
- Alert on sovereignty violations (data leaving geo-restricted region)
- Alert on anomaly score spikes
- Alert on unusual sharing activity
- **These alerts are tenant-scoped** — each customer can configure their own

**Grafana Alerting** (or Vaultize Alerting Service):
- Alert when the platform is degraded (OpenSearch cluster turns RED)
- Alert when ingestion lag exceeds 30 seconds
- Alert when API error rate > 1%
- **These are operational alerts for the platform team, not customers**

---

## Quick Reference

| Task | Tool | Where |
|---|---|---|
| See files shared by a user | OpenSearch Dashboards | Main UI |
| Find all events for a specific file | OpenSearch Dashboards | Discover → filter by file_id |
| See cross-border data transfers | OpenSearch Dashboards | DLP dashboard |
| Check if OpenSearch cluster is healthy | Grafana | grafana/d/opensearch |
| Check API response times | Grafana | grafana/d/api-health |
| Set up a DLP alert for a customer | OpenSearch Alerting | Alerting → Create monitor |
| Set up a platform health alert | Grafana Alerting | Grafana → Alert rules |
| Add a new visualization for a customer | OpenSearch Dashboards | Visualize → Create |
| Add a new infrastructure panel | Grafana | Dashboard → Add panel |

---

*Last Updated: 2026-03-15*
