# DRM Integration Guide: Vaultize Analytics Platform

> **Document Version**: 1.0
> **Last Updated**: 2026-02-05
> **Audience**: DRM Engineering Team
> **Authors**: Platform Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [What is SIEM and Why Do We Need It?](#2-what-is-siem-and-why-do-we-need-it)
3. [Introducing Vaultize Analytics Platform](#3-introducing-vaultize-analytics-platform)
4. [Sample Dashboards and Use Cases](#4-sample-dashboards-and-use-cases)
5. [Integration Architecture](#5-integration-architecture)
6. [What the DRM Engineering Team Needs to Do](#6-what-the-drm-engineering-team-needs-to-do)
7. [Event Schema Specification](#7-event-schema-specification)
8. [Integration Options](#8-integration-options)
9. [FAQ](#9-faq)
10. [Appendix](#10-appendix)

---

## 1. Executive Summary

This document describes how to integrate the DRM (Document Rights Management) system with the **Vaultize Analytics Platform** - our centralized audit logging and security analytics solution.

### Key Points

- **No SDK or Fluent Bit packaging required** - Your application just emits JSON events
- **Simple HTTP or TCP integration** - Multiple integration options available
- **Immediate value** - Pre-built dashboards for document activity monitoring
- **Compliance-ready** - Full audit trail for regulatory requirements

### Integration Effort Estimate

| Task | Complexity |
|------|------------|
| Add event emission to DRM codebase | Low-Medium |
| Configure event transport | Low |
| Testing and validation | Low |

---

## 2. What is SIEM and Why Do We Need It?

### 2.1 What is SIEM?

**SIEM** (Security Information and Event Management) is a system that:

- **Collects** security-relevant events from applications and infrastructure
- **Stores** events in a searchable, indexed format
- **Analyzes** patterns to detect anomalies and threats
- **Alerts** on suspicious activity
- **Reports** for compliance and forensics

### 2.2 Why Does DRM Need SIEM?

| Requirement | How SIEM Helps |
|-------------|----------------|
| **Audit Compliance** | Complete trail of who accessed what document, when, and what they did |
| **Security Monitoring** | Detect unauthorized access attempts, unusual patterns, potential data exfiltration |
| **Forensics** | Reconstruct the complete history of a leaked or compromised document |
| **Usage Analytics** | Understand how documents are being used across the organization |
| **Incident Response** | Quickly answer "What happened?" when security incidents occur |
| **Regulatory Requirements** | Meet GDPR, HIPAA, SOX, and other compliance mandates for data access logging |

### 2.3 Real-World Scenarios

**Scenario 1: Data Breach Investigation**
> "A confidential document was leaked. We need to know everyone who accessed it in the last 90 days."

With SIEM: Run a single query, get complete access history in seconds.

**Scenario 2: Compliance Audit**
> "Auditors need proof that only authorized users accessed PII documents."

With SIEM: Generate compliance reports showing access controls and actual access patterns.

**Scenario 3: Insider Threat Detection**
> "An employee downloaded 500 documents the week before resigning."

With SIEM: Alert triggers on unusual download volume, security team notified immediately.

---

## 3. Introducing Vaultize Analytics Platform

### 3.1 What Is It?

**Vaultize Analytics Platform** is our on-premise, open-source security analytics and log management solution. Think of it as a self-hosted Splunk alternative built specifically for our infrastructure.

### 3.2 Core Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VAULTIZE ANALYTICS PLATFORM                       │
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐   │
│  │              │   │              │   │                        │   │
│  │  Fluent Bit  │──▶│  OpenSearch  │──▶│  OpenSearch Dashboards │   │
│  │  (Ingestion) │   │  (Storage)   │   │  (Visualization)       │   │
│  │              │   │              │   │                        │   │
│  └──────────────┘   └──────────────┘   └────────────────────────┘   │
│                                                                      │
│  Optional:  ┌──────────────┐   ┌──────────────┐                     │
│             │  Prometheus  │──▶│   Grafana    │                     │
│             │  (Metrics)   │   │ (Dashboards) │                     │
│             └──────────────┘   └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Key Capabilities

| Capability | Description |
|------------|-------------|
| **Full-Text Search** | Search across millions of events in milliseconds |
| **Real-Time Dashboards** | Live visualization of document activity |
| **Historical Analysis** | Query events from days, weeks, or months ago |
| **Alerting** | Automated notifications on security events |
| **Retention Policies** | Automatic data lifecycle management (hot → warm → cold → delete) |
| **High Availability** | 3-node cluster with data replication |

### 3.4 Why Not Use a Cloud Service?

- **Data Sovereignty**: Audit logs never leave our infrastructure
- **Cost Control**: No per-GB ingestion fees
- **Compliance**: Meets on-premise data residency requirements
- **No Vendor Lock-in**: Open-source stack, fully portable

---

## 4. Sample Dashboards and Use Cases

### 4.1 Operations Dashboard

**Purpose**: Real-time monitoring of document activity across the organization.

**Refresh Rate**: Every 30 seconds (auto-refresh)

| Panel | Visualization | Description |
|-------|---------------|-------------|
| Event Volume | Line Chart | Events per minute over the last hour |
| Event Types | Pie Chart | Distribution of event types (access, permission change, download, etc.) |
| Top Active Users | Bar Chart | Users with most document interactions |
| Recent Activity | Table | Last 50 events with details |
| Error Rate | Metric | Failed access attempts percentage |

**Use Cases**:
- Monitor live system activity
- Spot unusual spikes in document access
- Quick health check of DRM system

---

### 4.2 Document Audit Dashboard

**Purpose**: Deep-dive into a specific document's complete history.

**Refresh Rate**: Manual (investigation tool)

| Panel | Visualization | Description |
|-------|---------------|-------------|
| Document Timeline | Timeline | All events for a document in chronological order |
| Access History | Table | Who accessed, when, from where |
| Permission Changes | Table | Complete permission modification history |
| Access by User | Bar Chart | Which users accessed most frequently |
| Geographic Access | Map | Access locations (if IP geolocation enabled) |

**Use Cases**:
- Investigate leaked documents
- Audit document access for compliance
- Understand document usage patterns

---

### 4.3 User Activity Dashboard

**Purpose**: Analyze all actions by a specific user.

**Refresh Rate**: Manual (investigation tool)

| Panel | Visualization | Description |
|-------|---------------|-------------|
| User Activity Timeline | Timeline | All user actions chronologically |
| Documents Accessed | Table | List of documents user interacted with |
| Action Types | Pie Chart | Breakdown of user's action types |
| Access Patterns | Heatmap | When does this user typically access documents? |
| Unusual Activity | Alerts | Flags for anomalous behavior |

**Use Cases**:
- Investigate suspicious user behavior
- Offboarding audit (what did departing employee access?)
- User activity reports for compliance

---

### 4.4 Security Alerts Dashboard

**Purpose**: Real-time security monitoring and threat detection.

**Refresh Rate**: Every 10 seconds (auto-refresh)

| Panel | Visualization | Description |
|-------|---------------|-------------|
| Failed Access Attempts | Metric + Trend | Access denied events |
| Bulk Download Alerts | Table | Users downloading unusual volumes |
| After-Hours Access | Table | Document access outside business hours |
| Permission Escalations | Table | Users granted elevated permissions |
| Geographic Anomalies | Map | Access from unusual locations |

**Use Cases**:
- Real-time threat monitoring
- Detect potential data exfiltration
- Identify compromised accounts

---

### 4.5 Compliance Report Dashboard

**Purpose**: Generate compliance reports for auditors.

**Refresh Rate**: Manual (reporting tool)

| Panel | Visualization | Description |
|-------|---------------|-------------|
| Access Summary | Table | Summary of all document access in period |
| Permission Audit | Table | Current permissions and when granted |
| Sensitive Document Access | Table | Access to classified/confidential documents |
| User Access Review | Table | What each user can access |
| Compliance Score | Gauge | Overall compliance metrics |

**Use Cases**:
- GDPR/HIPAA/SOX compliance audits
- Internal security reviews
- Access certification reports

---

## 5. Integration Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           YOUR INFRASTRUCTURE                                │
│                                                                              │
│  ┌─────────────────┐                                                        │
│  │                 │                                                        │
│  │  DRM Application│                                                        │
│  │                 │                                                        │
│  │  ┌───────────┐  │     JSON Events                                        │
│  │  │  Event    │  │────────────────────┐                                   │
│  │  │  Emitter  │  │                    │                                   │
│  │  └───────────┘  │                    │                                   │
│  │                 │                    │                                   │
│  └─────────────────┘                    │                                   │
│                                         ▼                                   │
│                           ┌─────────────────────────┐                       │
│                           │    Vaultize Analytics   │                       │
│                           │        Platform         │                       │
│                           │                         │                       │
│                           │  ┌─────────────────┐    │                       │
│                           │  │   Fluent Bit    │    │   Port 24224 (TCP)    │
│                           │  │   (Ingestion)   │◀───┼── or HTTP endpoint    │
│                           │  └────────┬────────┘    │                       │
│                           │           │             │                       │
│                           │           ▼             │                       │
│                           │  ┌─────────────────┐    │                       │
│                           │  │   OpenSearch    │    │                       │
│                           │  │   (Storage)     │    │                       │
│                           │  └────────┬────────┘    │                       │
│                           │           │             │                       │
│                           │           ▼             │                       │
│                           │  ┌─────────────────┐    │                       │
│                           │  │   Dashboards    │    │   Port 5601 (Web UI)  │
│                           │  │ (Visualization) │────┼──▶ Users access here  │
│                           │  └─────────────────┘    │                       │
│                           │                         │                       │
│                           └─────────────────────────┘                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

1. **DRM Application** performs an action (user accesses document, permission changed, etc.)
2. **Event Emitter** (code you add) creates a JSON event
3. **Event is sent** to Vaultize Analytics Platform (Fluent Bit endpoint)
4. **Fluent Bit** receives, parses, enriches, and forwards to OpenSearch
5. **OpenSearch** indexes the event for search and analytics
6. **Dashboards** visualize the data in real-time

### 5.3 Network Requirements

| Source | Destination | Port | Protocol | Purpose |
|--------|-------------|------|----------|---------|
| DRM Application | Fluent Bit | 24224 | TCP | Event ingestion (forward protocol) |
| DRM Application | Fluent Bit | 8888 | HTTP | Event ingestion (HTTP alternative) |
| Users | OpenSearch Dashboards | 5601 | HTTPS | Dashboard access |

---

## 6. What the DRM Engineering Team Needs to Do

### 6.1 Summary of Required Work

| Task | Description | Effort |
|------|-------------|--------|
| **1. Identify Events** | List all events that should be logged | 1-2 days |
| **2. Implement Event Emission** | Add code to emit events at appropriate points | 3-5 days |
| **3. Choose Transport** | Select HTTP or TCP transport method | 1 day |
| **4. Test Integration** | Verify events appear in dashboards | 1-2 days |

### 6.2 What You DON'T Need to Do

- **Package Fluent Bit** - It runs as a separate service in Vaultize Analytics Platform
- **Manage OpenSearch** - Platform team handles storage and indexing
- **Build dashboards** - Pre-built dashboards provided (customization available)
- **Handle retention** - Automatic lifecycle management configured

### 6.3 Step-by-Step Implementation

#### Step 1: Identify Events to Emit

Review your codebase and identify all security-relevant actions. At minimum, emit events for:

**Required Events** (must have):
| Event Type | When to Emit |
|------------|--------------|
| `document.created` | New document added to system |
| `document.accessed` | Document opened/viewed |
| `document.downloaded` | Document downloaded |
| `document.modified` | Document content changed |
| `document.deleted` | Document removed |
| `permission.granted` | Access permission given to user |
| `permission.revoked` | Access permission removed |
| `permission.modified` | Permission level changed |
| `access.denied` | Unauthorized access attempt |

**Recommended Events** (nice to have):
| Event Type | When to Emit |
|------------|--------------|
| `document.shared` | Document shared with external party |
| `document.printed` | Document sent to printer |
| `document.copied` | Document copied to clipboard |
| `user.login` | User authenticated to DRM system |
| `user.logout` | User session ended |
| `policy.created` | New DRM policy created |
| `policy.modified` | DRM policy changed |

#### Step 2: Implement Event Emission

Add event emission code at each identified point. See [Section 7](#7-event-schema-specification) for the exact JSON schema.

**Example (Python)**:
```python
import json
import socket
from datetime import datetime, timezone

class DRMEventEmitter:
    def __init__(self, host='vaultize-analytics', port=24224):
        self.host = host
        self.port = port

    def emit(self, event_type: str, data: dict):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "service": "drm-application",
            "version": "1.0",
            **data
        }
        self._send(event)

    def _send(self, event: dict):
        # Simple TCP send - production should use connection pooling
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(json.dumps(event).encode() + b'\n')

# Usage
emitter = DRMEventEmitter()

# When document is accessed
emitter.emit("document.accessed", {
    "document_id": "doc-12345",
    "document_name": "Financial-Report-Q4.pdf",
    "user_id": "user-789",
    "user_email": "john.doe@company.com",
    "access_type": "view",
    "ip_address": request.remote_addr,
    "user_agent": request.headers.get('User-Agent')
})
```

**Example (Java)**:
```java
public class DRMEventEmitter {
    private final String host;
    private final int port;
    private final ObjectMapper mapper = new ObjectMapper();

    public DRMEventEmitter(String host, int port) {
        this.host = host;
        this.port = port;
    }

    public void emit(String eventType, Map<String, Object> data) {
        Map<String, Object> event = new HashMap<>(data);
        event.put("timestamp", Instant.now().toString());
        event.put("event_type", eventType);
        event.put("service", "drm-application");
        event.put("version", "1.0");

        send(event);
    }

    private void send(Map<String, Object> event) {
        try (Socket socket = new Socket(host, port);
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {
            out.println(mapper.writeValueAsString(event));
        } catch (IOException e) {
            logger.error("Failed to send event", e);
        }
    }
}

// Usage
DRMEventEmitter emitter = new DRMEventEmitter("vaultize-analytics", 24224);

emitter.emit("document.accessed", Map.of(
    "document_id", "doc-12345",
    "document_name", "Financial-Report-Q4.pdf",
    "user_id", "user-789",
    "user_email", "john.doe@company.com",
    "access_type", "view",
    "ip_address", request.getRemoteAddr()
));
```

**Example (Node.js)**:
```javascript
const net = require('net');

class DRMEventEmitter {
    constructor(host = 'vaultize-analytics', port = 24224) {
        this.host = host;
        this.port = port;
    }

    emit(eventType, data) {
        const event = {
            timestamp: new Date().toISOString(),
            event_type: eventType,
            service: 'drm-application',
            version: '1.0',
            ...data
        };

        const client = new net.Socket();
        client.connect(this.port, this.host, () => {
            client.write(JSON.stringify(event) + '\n');
            client.destroy();
        });
    }
}

// Usage
const emitter = new DRMEventEmitter();

emitter.emit('document.accessed', {
    document_id: 'doc-12345',
    document_name: 'Financial-Report-Q4.pdf',
    user_id: 'user-789',
    user_email: 'john.doe@company.com',
    access_type: 'view',
    ip_address: req.ip
});
```

#### Step 3: Configure Transport

Choose your preferred transport method and configure the endpoint:

| Environment | Fluent Bit Host | Port |
|-------------|-----------------|------|
| Development | `localhost` | 24224 |
| Staging | `vaultize-staging.internal` | 24224 |
| Production | `vaultize-prod.internal` | 24224 |

#### Step 4: Test Integration

1. Emit a test event from your application
2. Open OpenSearch Dashboards: `http://vaultize-analytics:5601`
3. Go to **Discover** → Select `logs-*` index pattern
4. Search for your event: `event_type: "document.accessed"`
5. Verify all fields are correctly indexed

---

## 7. Event Schema Specification

### 7.1 Base Event Schema (Required for ALL Events)

Every event MUST include these fields:

```json
{
    "timestamp": "2026-02-05T14:30:00.000Z",
    "event_type": "document.accessed",
    "service": "drm-application",
    "version": "1.0"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 string | **Yes** | When the event occurred (UTC) |
| `event_type` | string | **Yes** | Event type identifier (see below) |
| `service` | string | **Yes** | Source application name |
| `version` | string | **Yes** | Event schema version |

### 7.2 Document Events

#### `document.created`
```json
{
    "timestamp": "2026-02-05T14:30:00.000Z",
    "event_type": "document.created",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "document_type": "pdf",
    "document_size_bytes": 2458624,
    "classification": "confidential",
    "owner_id": "user-123",
    "owner_email": "jane.smith@company.com",
    "folder_path": "/finance/reports/2026",
    "tags": ["finance", "quarterly", "internal"],
    "metadata": {
        "department": "Finance",
        "retention_policy": "7-years"
    }
}
```

#### `document.accessed`
```json
{
    "timestamp": "2026-02-05T14:35:00.000Z",
    "event_type": "document.accessed",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "user_id": "user-456",
    "user_email": "john.doe@company.com",
    "user_department": "Marketing",
    "access_type": "view",
    "ip_address": "192.168.1.50",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "device_type": "desktop",
    "location": {
        "city": "New York",
        "country": "US",
        "timezone": "America/New_York"
    },
    "session_id": "sess-abc123",
    "duration_seconds": null
}
```

#### `document.downloaded`
```json
{
    "timestamp": "2026-02-05T14:40:00.000Z",
    "event_type": "document.downloaded",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "user_id": "user-456",
    "user_email": "john.doe@company.com",
    "ip_address": "192.168.1.50",
    "download_format": "pdf",
    "file_size_bytes": 2458624,
    "watermarked": true,
    "watermark_text": "john.doe@company.com - 2026-02-05"
}
```

#### `document.modified`
```json
{
    "timestamp": "2026-02-05T15:00:00.000Z",
    "event_type": "document.modified",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "user_id": "user-123",
    "user_email": "jane.smith@company.com",
    "modification_type": "content_update",
    "previous_version": "v2",
    "new_version": "v3",
    "changes_summary": "Updated revenue figures"
}
```

#### `document.deleted`
```json
{
    "timestamp": "2026-02-05T16:00:00.000Z",
    "event_type": "document.deleted",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "user_id": "user-123",
    "user_email": "jane.smith@company.com",
    "deletion_type": "soft_delete",
    "reason": "Document superseded by new version",
    "recoverable": true,
    "retention_until": "2026-03-05T16:00:00.000Z"
}
```

### 7.3 Permission Events

#### `permission.granted`
```json
{
    "timestamp": "2026-02-05T14:20:00.000Z",
    "event_type": "permission.granted",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "actor_id": "user-123",
    "actor_email": "jane.smith@company.com",
    "target_id": "user-456",
    "target_email": "john.doe@company.com",
    "target_type": "user",
    "permission_level": "view",
    "permission_scope": ["view", "download"],
    "expiration": "2026-03-05T00:00:00.000Z",
    "reason": "Project collaboration",
    "approval_required": false
}
```

#### `permission.revoked`
```json
{
    "timestamp": "2026-02-05T17:00:00.000Z",
    "event_type": "permission.revoked",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "actor_id": "user-123",
    "actor_email": "jane.smith@company.com",
    "target_id": "user-456",
    "target_email": "john.doe@company.com",
    "previous_permission": "view",
    "reason": "Project completed",
    "revocation_type": "manual"
}
```

#### `permission.modified`
```json
{
    "timestamp": "2026-02-05T14:25:00.000Z",
    "event_type": "permission.modified",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "actor_id": "user-123",
    "actor_email": "jane.smith@company.com",
    "target_id": "user-456",
    "target_email": "john.doe@company.com",
    "previous_permission": "view",
    "new_permission": "edit",
    "reason": "Needs to make corrections"
}
```

### 7.4 Access Control Events

#### `access.denied`
```json
{
    "timestamp": "2026-02-05T14:45:00.000Z",
    "event_type": "access.denied",
    "service": "drm-application",
    "version": "1.0",
    "document_id": "doc-78291",
    "document_name": "Q4-Financial-Report.pdf",
    "user_id": "user-789",
    "user_email": "bob.wilson@company.com",
    "requested_action": "download",
    "denial_reason": "insufficient_permissions",
    "user_permission_level": "view",
    "required_permission_level": "download",
    "ip_address": "192.168.1.75",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
}
```

### 7.5 Field Reference

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `document_id` | string | Unique document identifier | `"doc-78291"` |
| `document_name` | string | Human-readable document name | `"Q4-Report.pdf"` |
| `user_id` | string | Unique user identifier | `"user-456"` |
| `user_email` | string | User's email address | `"john@company.com"` |
| `ip_address` | string | Client IP address | `"192.168.1.50"` |
| `access_type` | string | Type of access | `"view"`, `"edit"`, `"download"` |
| `permission_level` | string | Permission level | `"none"`, `"view"`, `"edit"`, `"admin"` |
| `classification` | string | Document sensitivity | `"public"`, `"internal"`, `"confidential"`, `"restricted"` |

---

## 8. Integration Options

### 8.1 Option A: TCP Forward Protocol (Recommended)

**Best for**: High-throughput, production environments

```
DRM App ──TCP:24224──▶ Fluent Bit ──▶ OpenSearch
```

**Pros**:
- Lowest latency
- Connection pooling possible
- Binary-efficient protocol

**Implementation**: See code examples in Section 6.3

---

### 8.2 Option B: HTTP POST

**Best for**: Simplicity, firewall-friendly environments

```
DRM App ──HTTP:8888──▶ Fluent Bit ──▶ OpenSearch
```

**Pros**:
- Uses standard HTTP
- Easy to debug
- Works through proxies

**Implementation**:
```python
import requests

def emit_event(event_type: str, data: dict):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "service": "drm-application",
        "version": "1.0",
        **data
    }

    requests.post(
        "http://vaultize-analytics:8888/drm.events",
        json=event,
        timeout=5
    )
```

---

### 8.3 Option C: Log File + Fluent Bit Sidecar

**Best for**: Containerized deployments, minimal code changes

```
DRM App ──writes──▶ /var/log/drm/events.log ◀──tails── Fluent Bit ──▶ OpenSearch
```

**Pros**:
- No network dependency from app
- Works if analytics platform is down (buffered in file)
- Minimal code changes (just write JSON lines to file)

**Implementation**:
```python
import json
from datetime import datetime

def emit_event(event_type: str, data: dict):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "service": "drm-application",
        "version": "1.0",
        **data
    }

    with open("/var/log/drm/events.log", "a") as f:
        f.write(json.dumps(event) + "\n")
```

**Note**: Requires Fluent Bit sidecar container or agent on the same host.

---

### 8.4 Option Comparison

| Criteria | TCP Forward | HTTP POST | Log File |
|----------|-------------|-----------|----------|
| Latency | Lowest | Low | Medium |
| Reliability | High | High | Highest (buffered) |
| Complexity | Medium | Low | Low |
| Firewall-friendly | No | Yes | N/A |
| Code changes | Medium | Medium | Minimal |
| Sidecar required | No | No | Yes |

**Recommendation**: Start with **HTTP POST** for simplicity, migrate to **TCP Forward** if performance requires it.

---

## 9. FAQ

### Q: Do we need to package Fluent Bit with our application?

**No.** Fluent Bit runs as part of the Vaultize Analytics Platform. Your application only needs to send events to it over the network (TCP or HTTP).

---

### Q: What happens if the analytics platform is down?

Events will be lost unless you implement local buffering. Options:
1. **Application-side queue**: Buffer events in memory, retry on failure
2. **Log file approach**: Write to file, Fluent Bit catches up when available
3. **Message queue**: Use Redis/RabbitMQ as intermediate buffer (advanced)

For most cases, simple retry logic is sufficient.

---

### Q: How long are events retained?

Default retention policy:
- **Hot storage**: 7 days (fast SSD, full-speed queries)
- **Warm storage**: 30 days (compressed, slightly slower)
- **Cold storage**: 90 days (highly compressed, slower queries)
- **Deleted**: After 90 days

This is configurable per index pattern.

---

### Q: Can we query events programmatically?

Yes! The Analytics API provides REST endpoints:

```bash
# Search for events
curl -X POST "http://vaultize-analytics:8000/api/v1/search/simple" \
  -H "Content-Type: application/json" \
  -d '{"index": "logs-*", "query": "event_type:document.accessed AND user_email:john*"}'

# Get aggregations
curl -X POST "http://vaultize-analytics:8000/api/v1/aggregations/terms" \
  -H "Content-Type: application/json" \
  -d '{"index": "logs-*", "field": "event_type", "size": 10}'
```

---

### Q: What about sensitive data in events?

**Recommendations**:
- **Do NOT** log passwords, tokens, or secrets
- **Do** log user IDs/emails (needed for audit)
- **Consider** masking sensitive document content
- **Use** classification fields to mark sensitivity

Data in OpenSearch is encrypted at rest and access-controlled.

---

### Q: Can we add custom fields?

Yes! The schema is flexible. Any additional fields you include will be automatically indexed. Just maintain consistency across events.

---

### Q: How do we handle high event volumes?

The platform is designed for high throughput:
- Fluent Bit: ~100K events/second
- OpenSearch cluster: Horizontally scalable

If you expect >10K events/second, contact the Platform team for capacity planning.

---

## 10. Appendix

### 10.1 Event Type Reference

| Event Type | Category | Description |
|------------|----------|-------------|
| `document.created` | Document | New document added |
| `document.accessed` | Document | Document viewed |
| `document.downloaded` | Document | Document downloaded |
| `document.modified` | Document | Document content changed |
| `document.deleted` | Document | Document removed |
| `document.shared` | Document | Document shared externally |
| `document.printed` | Document | Document printed |
| `permission.granted` | Permission | Access given |
| `permission.revoked` | Permission | Access removed |
| `permission.modified` | Permission | Access level changed |
| `access.denied` | Security | Unauthorized access attempt |
| `user.login` | User | User authenticated |
| `user.logout` | User | Session ended |
| `policy.created` | Policy | DRM policy created |
| `policy.modified` | Policy | DRM policy changed |

### 10.2 Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| Platform Team | platform-team@company.com | Vaultize Analytics Platform |
| Security Team | security@company.com | Security policy questions |
| DRM Team Lead | drm-lead@company.com | DRM integration questions |

### 10.3 Related Documentation

- [Vaultize Analytics Platform - Architecture](../architecture/README.md)
- [Vaultize Analytics Platform - API Reference](../api/README.md)
- [Vaultize Analytics Platform - Deployment Guide](../deployment/quickstart.md)
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [Fluent Bit Documentation](https://docs.fluentbit.io/)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Platform Team | Initial version |

---

*This document is maintained by the Platform Team. For questions or updates, contact platform-team@company.com.*
