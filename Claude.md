# `claude.md`

## Project Context

This repository contains a **multi-tenant analytics and observability platform** for the **Vaultize data security product**, built entirely using open-source components. It is inspired by Splunk in architecture but purpose-built for DLP (Data Loss Prevention) and data security analytics.

The platform serves **Vaultize customers** — each customer organisation is a tenant that logs in and sees only their own data.

**Vaultize modules this platform analyses:**
* **CDP** — Continuous Data Protection (endpoint backup via folder mapping)
* **EFSS** — Enterprise File Sync and Share (secure sharing)
* **DRM** — Persistent document protection (via EFSS)
* **Email Body Protection**

The system is intended to be:

* Multi-tenant — one deployment, many customer organisations, strict data isolation
* Self-hosted / on-prem deployable (datacenter is the final target)
* Production-grade
* Modular and extensible

This is **not** a cloud-native SaaS project and **must not introduce managed cloud dependencies**.

---

## Core Goal

Build a platform that supports:

* Centralised ingestion of Vaultize security events (CDP, EFSS, DRM, Email)
* Per-tenant analytics — each customer sees only their own data
* File lifecycle and user behaviour dashboards
* Alerting on security policy violations
* Compliance reporting across NIST, PII, financial, health, and other data categories

The primary engine is **OpenSearch** (self-hosted).

---

## Multi-Tenancy Architecture

**Approach**: Shared OpenSearch index + Document-Level Security (DLS). See full ADR in [docs/architecture/decisions.md](docs/architecture/decisions.md).

**Critical rule**: Every event document **must** include `organization_id` as the first field. Without it, tenant isolation breaks.

**Tenant provisioning per customer**:
1. Create OpenSearch user with hashed password
2. Create role with DLS filter: `{ "term": { "organization_id": "<org-id>" } }`
3. Assign role to user
4. Create OpenSearch Dashboards tenant for the org
5. Customer logs into `https://vaultize.duckdns.org` — sees only their data

See provisioning scripts in `scripts/ops/provision_tenant.py` (to be created).

---

## Hard Constraints (Do Not Violate)

Claude **must respect these constraints** when generating code, structure, or recommendations:

* **Deployment**: On-prem only (datacenter is the final target)
* **Search engine**: OpenSearch (self-hosted)
* **Visualization**: OpenSearch Dashboards (primary), Grafana (optional)
* **Log ingestion**: Fluent Bit preferred, Logstash optional
* **Metrics**: Prometheus (optional, complementary)
* **No AWS-managed services**
* **No SaaS dependencies**
* **No proprietary software**
* **No assumption of Kubernetes in v1** (Docker Compose first)

---

## AWS Usage Policy (Temporary PoC Only)

The platform is currently deployed on AWS **strictly as IaaS** — rented compute, storage, and networking only. AWS is a temporary host, not a platform. The final target is an on-prem datacenter.

### Permitted AWS Usage

| Service | Permitted Use | Datacenter Equivalent |
|---|---|---|
| EC2 | Run the Docker Compose stack | Bare metal / VM |
| EBS | Block storage for Docker volumes | Local disk / SAN |
| VPC | Private network isolation | VLAN / private LAN |
| Security Groups | Firewall rules | iptables / pfSense |
| Elastic IP | Stable public IP | Static IP assignment |
| S3 | Backups and log file uploads only | MinIO (S3-compatible) |

### Prohibited AWS Usage

Never use the following — they create migration blockers:

* ❌ Amazon OpenSearch Service — use self-hosted OpenSearch on EC2
* ❌ ECS / EKS / Fargate — use Docker Compose directly on EC2
* ❌ ALB / NLB — use Nginx on EC2
* ❌ CloudWatch — use Prometheus + Grafana (already in the stack)
* ❌ AWS Secrets Manager — use `.env` files or self-hosted Vault
* ❌ RDS / ElastiCache — not needed; avoid introducing them
* ❌ SQS / SNS / Lambda — no event-driven AWS glue
* ❌ AWS Certificate Manager — use Let's Encrypt or self-signed certs
* ❌ Route 53 — use any DNS provider; just an A record

### The Portability Test

Before introducing any AWS service or SDK call, ask:
> *"Can I replace this with a self-hosted equivalent by changing one config value?"*

If the answer is **no**, do not use it.

| Acceptable | Why |
|---|---|
| S3 via boto3 | `endpoint_url` → MinIO, zero code change |
| EC2 instance profile | Replaced by env vars or Vault in datacenter |

### Migration Path

The deployment is designed so that moving to a datacenter requires:
1. Provision VMs with Docker + Docker Compose
2. Change `S3_ENDPOINT_URL` to point at MinIO
3. Update the DNS A record
4. Restore OpenSearch snapshot
5. Terminate EC2 — **no code changes, no refactoring**

---

## Mental Model to Use

Claude should reason using this model:

* OpenSearch = **search + analytics engine**, not a vector DB
* Logs are the **primary data type**
* Metrics are **complementary**, not a replacement for logs
* Dashboards are **derived artifacts**, not the core system
* Configuration > code where possible

Avoid framing the system as:

* A BI tool
* A pure observability stack
* A vector database platform
* A cloud-native SaaS

---

## Expected Architecture (Conceptual)

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

Optional additions:

* Prometheus for metrics
* Grafana for unified dashboards
* Kafka for ingestion buffering (future)

---

## Repository Design Expectations

Claude should assume a **mono-repo** with clear separation of concerns.

High-level structure should resemble:

* `infrastructure/` – deployment, Docker, configs
* `ingestion/` – log pipelines and agents
* `analytics/` – index templates, queries, alerts
* `dashboards/` – saved dashboards and visualizations
* `configs/` – shared YAML/JSON configuration
* `scripts/` – operational tooling
* `docs/` – architecture and usage documentation

Each directory must have:

* A clear responsibility
* Minimal coupling to others

---

## Coding Guidelines

When generating code:

* Prefer **Python** for scripts and services
* Prefer **YAML / JSON** for configuration
* Avoid over-engineering
* Favor readability over clever abstractions
* Assume other engineers will maintain this

Do **not** generate:

* Massive frameworks
* Overly generic abstractions
* Unnecessary microservices

---

## Testing Requirements

**CRITICAL**: Every new functionality MUST have associated regression tests.

### Test Coverage Mandate

Claude **must** adhere to these testing requirements:

1. **Unit Tests Required**
   - All Python functions/methods must have unit tests
   - Target: >80% code coverage minimum
   - Location: `<module>/tests/test_<feature>.py`
   - Framework: pytest

2. **Integration Tests Required**
   - All service integrations must have integration tests
   - Test actual connections to OpenSearch, APIs, etc.
   - Location: `tests/integration/`
   - Use test fixtures and mocks appropriately

3. **Regression Tests Required**
   - Every bug fix must include a regression test
   - Every new feature must have regression test coverage
   - Location: `tests/regression/`
   - Tests must be named clearly: `test_regression_<issue_number>_<description>.py`

4. **E2E Tests for Critical Flows**
   - Complete log ingestion → search → visualization flow
   - Alert creation → trigger → notification flow
   - Location: `tests/e2e/`

### Test Development Workflow

When adding new functionality:

1. **Write tests first** (TDD approach preferred) or immediately after implementation
2. **Run tests locally** before committing
3. **Update regression suite** in `tests/regression/` with new test cases
4. **Document test coverage** in code comments and docstrings
5. **Never commit untested code**

### Test Standards (non-negotiable)

- Tests must always **pass or fail definitively** — never implement skip logic or conditional skipping
- All tests must run with **real data**, not fabricated placeholders
- If a test fails, fix the underlying issue — do not suppress or work around the failure
- **Failure to provide tests for new functionality is considered incomplete work**

See [tests/README.md](tests/README.md) for directory structure, naming conventions, and run commands.

---

## Debugging

When fixing bugs, Claude **must** follow this approach:

1. **Verify the root cause** before implementing any fix - check if the issue is in data extraction, data passing, or backend processing
2. **Trace the data flow** end-to-end to isolate where the problem actually occurs
3. **Test with edge cases** like zero values, null values, empty strings, and boundary conditions
4. **Do not apply speculative fixes** - understand the problem first, then fix it

---

## Workflow

- Always **complete multi-part tasks fully** before ending - if the user requests multiple changes (e.g., merge files AND update a checklist), track and complete all parts
- Use the TodoWrite tool to track multi-part requests and mark each part as completed
- Do not consider a task done until every part of the request has been addressed

---

## Alerting Philosophy

Alerts should be:

* Derived from OpenSearch queries
* Threshold-based initially
* Config-driven
* Transport-agnostic (webhook-first)

Avoid ML-based alerting in v1 unless explicitly requested.

---

## Metrics Philosophy (Prometheus)

Prometheus, if referenced, should be used for:

* System health
* Resource utilization
* Latency and error rates

Prometheus **must not** replace:

* Log search
* Root-cause analysis
* Event forensics

---

## Vector Search Guidance

Vector search:

* Is **optional**
* Is **not a primary design goal**
* Should be treated as a future extension point only

Claude should not redesign the system around embeddings unless explicitly asked.

---

## Output Expectations

When responding, Claude should:

* Be explicit about trade-offs
* Clearly label assumptions
* Prefer architectural clarity
* Think like a platform engineer, not a tutorial author
* Avoid marketing language

---

## Success Criteria

A senior engineer should be able to:

* Understand the system in minutes
* Run it locally with Docker Compose
* Extend it safely
* Operate it on-prem without cloud dependencies

---

## Key Architecture Decisions

10 foundational decisions govern this platform. Full ADRs (rationale, alternatives, impact) are in [docs/architecture/decisions.md](docs/architecture/decisions.md).

| # | Decision | Choice | Trade-off |
|---|---|---|---|
| 1 | Search engine | OpenSearch over Elasticsearch | Open source licensing |
| 2 | Deployment | Docker Compose first, K8s later | Less scalable initially |
| 3 | Language | Python 3.11+ | Slower runtime than Go |
| 4 | Log collector | Fluent Bit over Logstash | Less powerful parsing |
| 5 | Config approach | YAML/JSON-driven over code | More config files |
| 6 | Data primary type | Logs first, metrics complementary | Separate metrics storage |
| 7 | Alerts transport | Webhooks | Requires receiver endpoint |
| 8 | Deployment model | On-prem only, no cloud dependencies | No managed service convenience |
| 9 | Alert logic | Threshold-based (no ML in v1) | Less intelligent |
| 10 | Repo structure | Mono-repo | Larger repo size |

---

## Session Continuity Protocol

**CRITICAL**: At the end of each session, Claude **must** update the following files to ensure continuity across sessions:

1. **`TODO.md`**
   - Update current tasks with latest status (pending/in-progress/completed)
   - Add new tasks discovered during the session
   - Mark completed tasks with completion date
   - Document any blockers or issues

2. **`CHANGELOG.md`**
   - Log all significant changes made during the session
   - Include file creations, modifications, deletions
   - Note configuration changes
   - Document any architectural decisions

3. **`MILESTONES.md`**
   - Update milestone progress
   - Mark completed milestones with completion date
   - Add new milestones if scope has changed
   - Update percentage completion estimates

4. **`docs/SESSION_NOTES.md`**
   - Write a brief session summary
   - Document what was accomplished
   - Note next steps
   - Record any important context or decisions
   - Include current state of the system (what's working, what's not)

5. **`docs/operations/testing-guide.md`**
   - Update the "Session Change Log" table at the bottom of the file
   - Add new test scenarios for any new features implemented
   - Update existing tests if endpoints or behavior changed
   - Add troubleshooting entries for any issues encountered and resolved

**When to update**: Before the user ends the session (e.g., phrases like "let's stop for today", "closing for the day", "that's all for now", etc.)

**Purpose**: These files serve as the primary mechanism for session continuity since conversation context doesn't persist between sessions.

---

## AWS Deployment

**CLI profile**: `vaultize` | **Account**: `211125671504` | **IAM user**: `vaultize-poc`

All resources prefixed `vaultize-` with tag `Project=vaultize`. All CLI and boto3 calls use `--profile vaultize` / `boto3.Session(profile_name="vaultize")`.

See full configuration, naming conventions, and cost guide: [docs/deployment/aws.md](docs/deployment/aws.md)

