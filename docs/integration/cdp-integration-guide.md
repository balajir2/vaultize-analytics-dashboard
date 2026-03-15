# Vaultize CDP Integration Guide

> **For the Vaultize CDP developer**: How to send your events to the analytics platform.

---

## What You Need to Do

Every time a file is backed up, restored, or a policy is applied, your CDP module sends
one JSON event to the analytics platform. That's it.

The platform handles storage, search, and dashboards automatically.

---

## Step 1 — Your Credentials

You'll need the credentials for your customer's organisation. Ask the platform admin to
run provisioning for your test org (they'll use `provision_tenant.py`).

You get back:
```
URL:      https://vaultize.duckdns.org
Username: acme-corp
Password: AcmeTest@123
```

These are **HTTP Basic** credentials. Your backend service uses them to authenticate writes.

For production, use a **dedicated service account** (not a user account). The platform admin
can create one with write-only permissions to `vaultize-events-*`.

---

## Step 2 — Build Your Event

Every event is a JSON object. These fields are **mandatory** in every event:

```json
{
  "organization_id": "acme-corp",
  "tenant_name":     "Acme Corporation",
  "event_id":        "550e8400-e29b-41d4-a716-446655440000",
  "event_type":      "CDP.BACKUP_CREATED",
  "module":          "CDP",
  "@timestamp":      "2026-03-15T10:30:00Z",
  "schema_version":  "1.0"
}
```

Then add user, file, and CDP-specific fields. Full field reference: [vaultize-event-schema.md](../schemas/vaultize-event-schema.md)

### Minimal CDP event (copy this):

```json
{
  "organization_id":   "acme-corp",
  "tenant_name":       "Acme Corporation",
  "event_id":          "GENERATE-UUID-HERE",
  "event_type":        "CDP.BACKUP_CREATED",
  "module":            "CDP",
  "@timestamp":        "2026-03-15T10:30:00Z",
  "schema_version":    "1.0",

  "user_id":           "U-12345",
  "user_email":        "alice@acme-corp.com",
  "user_display_name": "Alice Smith",
  "user_department":   "Finance",
  "user_group":        "finance-team",
  "user_location":     "US-NYC",
  "user_device_id":    "DEV-WIN-001",
  "user_ip":           "192.168.1.10",

  "file_id":           "F-abc123",
  "file_name":         "budget-2026.xlsx",
  "file_name_text":    "budget-2026.xlsx",
  "file_extension":    "xlsx",
  "file_size_bytes":   1048576,
  "file_path":         "/Users/alice/Documents/budget-2026.xlsx",
  "file_hash_sha256":  "abc123...",
  "file_mime_type":    "application/vnd.ms-excel",

  "data_classification":        "CONFIDENTIAL",
  "nist_impact_level":          "MODERATE",
  "contains_pii":               false,
  "contains_sensitive_pii":     false,
  "contains_financial_data":    true,
  "contains_health_data":       false,
  "contains_ip":                false,
  "contains_export_controlled": false,
  "contains_cui":               false,
  "contains_classified":        false,
  "geo_restricted":             true,
  "geo_restriction_region":     "US",
  "ai_use_restricted":          false,
  "data_categories":            ["FINANCIAL"],

  "cross_border_transfer":   false,
  "sovereignty_violation":   false,
  "source_country":          "US",
  "destination_country":     "US",

  "is_anomaly":         false,
  "anomaly_score":      0.0,
  "anomaly_flags":      [],
  "baseline_period_days": 365,

  "cdp_backup_id":           "BK-001234",
  "cdp_folder_path":         "C:\\Users\\alice\\Documents",
  "cdp_folder_mapping_id":   "FM-42",
  "cdp_retention_policy":    "30-day-daily",
  "cdp_backup_size_bytes":   1048576,
  "cdp_version_number":      1,
  "cdp_restore_point":       "2026-03-15T10:30:00Z",
  "cdp_device_os":           "Windows 11",
  "cdp_agent_version":       "4.2.1"
}
```

**event_type values for CDP:**
- `CDP.BACKUP_CREATED` — new file version backed up
- `CDP.BACKUP_UPDATED` — existing backup updated
- `CDP.BACKUP_DELETED` — backup version deleted (per retention policy)
- `CDP.RESTORE_INITIATED` — restore request started
- `CDP.RESTORE_COMPLETED` — restore completed
- `CDP.POLICY_APPLIED` — folder mapping / retention policy changed

---

## Step 3 — Send the Event

### Option A: Direct to OpenSearch (simplest)

```bash
curl -X POST \
  --insecure \
  -u acme-corp:AcmeTest@123 \
  -H "Content-Type: application/json" \
  https://vaultize.duckdns.org/vaultize-events-2026.03.15/_doc \
  -d '{ ...your event... }'
```

Index name format: `vaultize-events-YYYY.MM.DD`

### Option B: Via Vaultize Analytics API (recommended — adds validation)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  https://vaultize.duckdns.org/vaultize/api/v1/ingest \
  -d '{ ...your event... }'
```

*(API is being built — use Option A for now)*

### Option C: Python (for your backend service)

```python
import json, uuid, httpx
from datetime import datetime, timezone

def send_cdp_event(org_id, org_name, user, file, backup_details, credentials):
    """Send a CDP backup event to the analytics platform."""
    event = {
        "organization_id": org_id,
        "tenant_name":     org_name,
        "event_id":        str(uuid.uuid4()),
        "event_type":      "CDP.BACKUP_CREATED",
        "module":          "CDP",
        "@timestamp":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_version":  "1.0",
        **user,
        **file,
        **backup_details,
        # Fill in data classification based on your file classification service
        "data_classification":        file.get("classification", "INTERNAL"),
        "nist_impact_level":          "LOW",
        "contains_pii":               False,
        "contains_sensitive_pii":     False,
        "contains_financial_data":    False,
        "contains_health_data":       False,
        "contains_ip":                False,
        "contains_export_controlled": False,
        "contains_cui":               False,
        "contains_classified":        False,
        "geo_restricted":             False,
        "geo_restriction_region":     "US",
        "ai_use_restricted":          False,
        "data_categories":            [],
        "source_country":             "US",
        "destination_country":        "US",
        "cross_border_transfer":      False,
        "sovereignty_violation":      False,
        "is_anomaly":                 False,
        "anomaly_score":              0.0,
        "anomaly_flags":              [],
        "baseline_period_days":       365,
    }

    today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    index = f"vaultize-events-{today}"
    url = f"https://vaultize.duckdns.org/{index}/_doc"

    response = httpx.post(
        url,
        json=event,
        auth=(credentials["username"], credentials["password"]),
        verify=False  # self-signed cert in dev; use proper cert in prod
    )
    response.raise_for_status()
    return response.json()
```

---

## Step 4 — Verify Your Data Arrived

Log into the Dashboards at `https://vaultize.duckdns.org` with your org credentials.

Or check via API:
```bash
# Count events for your org
curl --insecure \
  -u acme-corp:AcmeTest@123 \
  'https://vaultize.duckdns.org/vaultize-events-*/_count'
```

---

## Data Classification — What to Send

The platform needs classification metadata to power DLP dashboards. If your CDP agent
doesn't have classification information yet, send defaults and update later.

| Scenario | Fields to set |
|---|---|
| Unknown classification | `data_classification: "INTERNAL"`, all `contains_*: false` |
| File has PII (names, emails, IDs) | `contains_pii: true`, `data_categories: ["PII"]` |
| Financial documents (.xls, reports) | `contains_financial_data: true`, `data_categories: ["FINANCIAL"]` |
| Health records | `contains_health_data: true`, `contains_pii: true`, `data_categories: ["HEALTH","PII"]` |
| Source code, design docs | `contains_ip: true`, `data_classification: "CONFIDENTIAL"` |
| Unclassified but sensitive govt data | `contains_cui: true`, `nist_impact_level: "MODERATE"` |

If you integrate with a classification engine (e.g., Microsoft Purview, Boldon James),
map the classification labels to these fields.

---

## Folder Mapping

CDP backs up monitored folders. The `cdp_folder_mapping_id` links to the policy that
monitors that folder. This enables the "Life Journey of a File" view in dashboards —
you can see a file's entire history across backup, share, and access events.

Use the same `file_id` for the same logical file across all events. The `file_id`
is how the platform reconstructs file history.

---

## Troubleshooting

**403 Unauthorized**
Your credentials are wrong or the user doesn't have write access.
Check with the platform admin.

**400 Bad Request: unknown field**
You're sending a field not in the index mapping. Check [vaultize-event-schema.md](../schemas/vaultize-event-schema.md).
Common mistake: using `timestamp` instead of `@timestamp`.

**400 Bad Request: strict dynamic mapping**
Same as above — only send fields that exist in the schema.

**Your events appear but count is wrong**
DLS (Document Level Security) is working correctly — you can only see events for your
`organization_id`. The admin will see the full count.

---

*Last Updated: 2026-03-15*
