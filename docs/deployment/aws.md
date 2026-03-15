# AWS Deployment Guide

> **Purpose**: Configuration and conventions for the temporary AWS PoC deployment of the Vaultize Analytics Platform.
> **Intent**: AWS is used as IaaS only. The platform runs identically on bare-metal datacenter VMs. No AWS-managed services are used.

---

## CLI Profile

| Field | Value |
|---|---|
| **Profile name** | `vaultize` |
| **IAM User** | `vaultize-poc` |
| **Account ID** | `211125671504` |
| **Region** | `us-east-1` |

**CLI usage**:
```bash
aws <command> --profile vaultize
```

**boto3 usage**:
```python
import boto3
session = boto3.Session(profile_name="vaultize")
s3 = session.client("s3")
```

---

## Resource Naming Convention

**All AWS resources must be prefixed with `vaultize-`** and tagged `Project=vaultize`.

| Resource Type | Pattern | Example |
|---|---|---|
| EC2 instances | `vaultize-<role>` | `vaultize-poc-server` |
| S3 buckets | `vaultize-<purpose>` | `vaultize-poc-storage` |
| VPC | `vaultize-vpc` | `vaultize-vpc` |
| Subnets | `vaultize-<type>-<az>` | `vaultize-public-1a` |
| Security Groups | `vaultize-<role>-sg` | `vaultize-app-sg` |
| IAM roles | `vaultize-<role>-role` | `vaultize-ec2-role` |
| IAM policies | `vaultize-<scope>-policy` | `vaultize-s3-policy` |
| Key pairs | `vaultize-<env>-key` | `vaultize-poc-key` |
| Elastic IPs | Tag: `Name=vaultize-eip` | — |
| EBS volumes | Tag: `Name=vaultize-<purpose>` | `vaultize-data` |

**All resources must carry**: `Project=vaultize`

This ensures cost tracking in AWS Cost Explorer (filter by tag) and safe bulk cleanup.

---

## Infrastructure Layout

```
AWS Account: 211125671504
  └── VPC: vaultize-vpc (10.0.0.0/16)
        ├── Public Subnet: vaultize-public-1a (10.0.1.0/24)
        │     └── EC2: vaultize-poc-server (t3.2xlarge)
        │           ├── EBS root:  30GB  gp3  (OS + Docker)
        │           └── EBS data: 150GB  gp3  (Docker volumes)
        └── Internet Gateway: vaultize-igw
```

---

## EC2 Instance

| Field | Value |
|---|---|
| **Name** | `vaultize-poc-server` |
| **Instance type** | `t3.2xlarge` (8 vCPU, 32GB RAM) |
| **AMI** | Ubuntu 22.04 LTS |
| **Key pair** | `vaultize-poc-key` |
| **IAM role** | `vaultize-ec2-role` |

### Security Group: `vaultize-app-sg`

| Port | Protocol | Source | Purpose |
|---|---|---|---|
| 22 | TCP | Admin IP only | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP → redirect to 443 |
| 443 | TCP | 0.0.0.0/0 | HTTPS → Nginx |

All internal service ports (9200, 5601, 8000, 8001, 3000, 9090) are **not exposed** — Nginx proxies them internally.

---

## S3 Bucket

| Field | Value |
|---|---|
| **Name** | `vaultize-poc-storage` |
| **Region** | `us-east-1` |
| **Purpose** | OpenSearch snapshots + user log file uploads |

### Bucket Layout

```
vaultize-poc-storage/
  ├── snapshots/    ← OpenSearch backup snapshots (backup_opensearch.py)
  └── uploads/      ← User-uploaded log files (s3_poller.py picks these up)
```

### IAM Policy: `vaultize-s3-policy`

Attached to `vaultize-ec2-role` (instance profile — no hardcoded keys):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::vaultize-poc-storage",
        "arn:aws:s3:::vaultize-poc-storage/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:DeleteObject"],
      "Resource": "arn:aws:s3:::vaultize-poc-storage/snapshots/*"
    }
  ]
}
```

---

## Nginx Routing

Nginx runs directly on EC2 (not in Docker). All services are behind Nginx — no service ports are publicly exposed.

| Path | Backend |
|---|---|
| `/` | OpenSearch Dashboards `:5601` |
| `/grafana/` | Grafana `:3000` |
| `/api/` | Analytics API `:8000` |
| `/alerting/` | Alerting Service `:8001` |
| `/prometheus/` | Prometheus `:9090` |
| `/upload/` | File Upload UI (static HTML) |

---

## Docker Compose Changes for AWS

Only `.env` overrides needed — no Compose file edits:

```env
# Tune heap for t3.2xlarge (32GB RAM)
OPENSEARCH_JAVA_OPTS=-Xms8g -Xmx8g

# Production settings
ENVIRONMENT=production
AUTH_ENABLED=true
API_SECRET_KEY=<generated-secret>
GRAFANA_ADMIN_PASSWORD=<strong-password>
OPENSEARCH_ADMIN_PASSWORD=<strong-password>

# S3 for snapshots
S3_BUCKET=vaultize-poc-storage
S3_REGION=us-east-1
# No S3_ENDPOINT_URL needed on EC2 (uses instance profile + default endpoint)
# In datacenter: S3_ENDPOINT_URL=http://minio:9000
```

---

## Cost Summary (PoC)

| Scenario | Monthly Cost |
|---|---|
| `t3.2xlarge` running 8 hrs/day | ~$89 |
| `t3.2xlarge` running 24/7 | ~$252 |
| `m6i.xlarge` running 8 hrs/day | ~$55 |

EBS (150GB gp3) costs ~$12/month regardless of instance state.
S3 storage is negligible for PoC volumes (~$1/month).

**Tip**: Stop the instance when not in use — EBS persists all data across stop/start.

---

## Datacenter Migration

When moving from AWS to a datacenter:

1. Provision VMs with Docker + Docker Compose (Ubuntu 22.04 recommended)
2. Copy the repo — all configs are identical
3. Change one env var: `S3_ENDPOINT_URL=http://minio:9000` (MinIO replaces S3)
4. Restore OpenSearch snapshot from MinIO
5. Update DNS A record to new IP
6. Terminate EC2 instance

**No code changes required.**
