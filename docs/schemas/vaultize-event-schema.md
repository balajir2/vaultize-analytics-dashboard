# Vaultize Analytics Event Schema

> **For Vaultize developers**: This document defines the exact JSON field names and types
> your modules must emit when sending events to the analytics platform.

---

## Overview

All events from all modules (CDP, EFSS, DRM, Email) are indexed into OpenSearch.
Each event is a JSON document with a flat (not nested) structure for query performance.

**Index naming**: `vaultize-events-YYYY.MM.DD` (daily, auto-rotated)

**Ingest endpoint**: POST to the Vaultize Analytics API at
`https://vaultize.duckdns.org/vaultize/api/v1/ingest`
or directly to OpenSearch via Fluent Bit.

---

## Mandatory Fields (All Modules)

These fields **must** be present in every event. Without them, multi-tenancy breaks.

| Field | Type | Description | Example |
|---|---|---|---|
| `organization_id` | `keyword` | Customer org identifier — used for DLS tenant isolation | `"acme-corp"` |
| `tenant_name` | `keyword` | Human-readable org name | `"Acme Corporation"` |
| `event_id` | `keyword` | UUID for the event (generate at source) | `"a1b2c3d4-..."` |
| `event_type` | `keyword` | Module + action (see per-module values) | `"CDP.BACKUP_CREATED"` |
| `module` | `keyword` | Source module: `CDP`, `EFSS`, `DRM`, `EMAIL` | `"EFSS"` |
| `@timestamp` | `date` | ISO 8601 UTC timestamp of the event | `"2026-03-15T10:30:00Z"` |
| `schema_version` | `keyword` | Schema version for forward compat | `"1.0"` |

---

## User and Identity Fields

| Field | Type | Description | Example |
|---|---|---|---|
| `user_id` | `keyword` | Internal user ID in customer's system | `"U-12345"` |
| `user_email` | `keyword` | User's email address | `"alice@acme.com"` |
| `user_display_name` | `text` | Full name | `"Alice Smith"` |
| `user_department` | `keyword` | Department | `"Engineering"` |
| `user_group` | `keyword` | Primary group | `"developers"` |
| `user_location` | `keyword` | Office / country | `"US-NYC"` |
| `user_device_id` | `keyword` | Endpoint device identifier | `"DEV-WIN-001"` |
| `user_ip` | `ip` | Client IP address | `"192.168.1.10"` |

---

## File / Document Fields

| Field | Type | Description | Example |
|---|---|---|---|
| `file_id` | `keyword` | Stable file identifier (survives renames) | `"F-abc123"` |
| `file_name` | `keyword` | File name with extension | `"budget-2026.xlsx"` |
| `file_name_text` | `text` | Analyzed copy for full-text search | `"budget-2026.xlsx"` |
| `file_extension` | `keyword` | Extension (no dot, lowercase) | `"xlsx"` |
| `file_size_bytes` | `long` | File size in bytes | `1048576` |
| `file_path` | `keyword` | Full path on device or in EFSS | `"/Finance/Q1/budget-2026.xlsx"` |
| `file_hash_sha256` | `keyword` | SHA-256 of file content | `"abc123..."` |
| `file_mime_type` | `keyword` | MIME type | `"application/vnd.ms-excel"` |

---

## Data Classification Fields

| Field | Type | Description | Values |
|---|---|---|---|
| `data_classification` | `keyword` | Primary classification label | `"CONFIDENTIAL"`, `"RESTRICTED"`, `"PUBLIC"`, `"INTERNAL"` |
| `nist_impact_level` | `keyword` | NIST SP 800-60 level | `"LOW"`, `"MODERATE"`, `"HIGH"` |
| `contains_pii` | `boolean` | Contains personally identifiable information | `true` / `false` |
| `contains_sensitive_pii` | `boolean` | Contains special-category PII (health, biometric, racial) | `true` / `false` |
| `contains_financial_data` | `boolean` | Contains financial records | `true` / `false` |
| `contains_health_data` | `boolean` | Contains health / medical records (HIPAA) | `true` / `false` |
| `contains_ip` | `boolean` | Contains intellectual property / trade secrets | `true` / `false` |
| `contains_export_controlled` | `boolean` | Export-controlled data (ITAR, EAR) | `true` / `false` |
| `contains_cui` | `boolean` | Controlled Unclassified Information | `true` / `false` |
| `contains_classified` | `boolean` | Classified national security data | `true` / `false` |
| `geo_restricted` | `boolean` | Data must not leave specific country/region | `true` / `false` |
| `geo_restriction_region` | `keyword` | Country/region code | `"EU"`, `"US"` |
| `ai_use_restricted` | `boolean` | AI processing prohibited or restricted | `true` / `false` |
| `data_categories` | `keyword[]` | List of all applicable categories | `["PII", "FINANCIAL"]` |

---

## CDP Module Fields (Continuous Data Protection / Endpoint Backup)

`event_type` values: `CDP.BACKUP_CREATED`, `CDP.BACKUP_UPDATED`, `CDP.BACKUP_DELETED`,
`CDP.RESTORE_INITIATED`, `CDP.RESTORE_COMPLETED`, `CDP.POLICY_APPLIED`

| Field | Type | Description | Example |
|---|---|---|---|
| `cdp_backup_id` | `keyword` | Backup job/snapshot ID | `"BK-001234"` |
| `cdp_folder_path` | `keyword` | Monitored folder path | `"C:\\Users\\alice\\Documents"` |
| `cdp_folder_mapping_id` | `keyword` | Policy folder mapping ID | `"FM-42"` |
| `cdp_retention_policy` | `keyword` | Applied retention policy | `"30-day-daily"` |
| `cdp_backup_size_bytes` | `long` | Total backup size | `524288000` |
| `cdp_version_number` | `integer` | File version (incremented on each change) | `5` |
| `cdp_restore_point` | `date` | Timestamp of the restore point used | `"2026-03-10T08:00:00Z"` |
| `cdp_device_os` | `keyword` | Endpoint OS | `"Windows 11"` |
| `cdp_agent_version` | `keyword` | CDP agent version | `"4.2.1"` |

---

## EFSS Module Fields (Enterprise File Sync and Share)

`event_type` values: `EFSS.FILE_SHARED`, `EFSS.FILE_ACCESSED`, `EFSS.FILE_UPLOADED`,
`EFSS.FILE_DOWNLOADED`, `EFSS.FILE_DELETED`, `EFSS.SHARE_REVOKED`, `EFSS.LINK_CREATED`

| Field | Type | Description | Example |
|---|---|---|---|
| `efss_share_id` | `keyword` | Share link / permission record ID | `"SH-9876"` |
| `efss_share_type` | `keyword` | `INTERNAL`, `EXTERNAL`, `LINK` | `"EXTERNAL"` |
| `efss_recipient_email` | `keyword` | Recipient email | `"bob@partner.com"` |
| `efss_recipient_domain` | `keyword` | Recipient domain (extracted) | `"partner.com"` |
| `efss_recipient_is_external` | `boolean` | True if outside org domain | `true` |
| `efss_permission_type` | `keyword` | `VIEW`, `DOWNLOAD`, `EDIT`, `FULL_CONTROL` | `"VIEW"` |
| `efss_share_expiry` | `date` | Share expiry timestamp | `"2026-04-15T00:00:00Z"` |
| `efss_share_has_password` | `boolean` | Share protected with password | `false` |
| `efss_access_location_country` | `keyword` | Country of access (GeoIP) | `"DE"` |
| `efss_access_location_city` | `keyword` | City of access | `"Berlin"` |
| `efss_chain_depth` | `integer` | Degree of sharing (0=original, 1=forwarded once) | `0` |
| `efss_shared_from_user_id` | `keyword` | User ID of original sharer (for chain tracking) | `"U-12345"` |
| `efss_domain_whitelist_match` | `boolean` | Recipient domain on whitelist | `true` |
| `efss_ip_whitelist_match` | `boolean` | Access from whitelisted IP | `false` |

---

## DRM Module Fields (Persistent Document Protection via EFSS)

`event_type` values: `DRM.PROTECTION_APPLIED`, `DRM.DOCUMENT_OPENED`,
`DRM.DOCUMENT_PRINTED`, `DRM.DOCUMENT_SCREENSHOT_ATTEMPTED`, `DRM.ACCESS_REVOKED`,
`DRM.POLICY_CHANGED`, `DRM.WATERMARK_ADDED`

| Field | Type | Description | Example |
|---|---|---|---|
| `drm_document_id` | `keyword` | Protected document ID | `"DRM-55432"` |
| `drm_policy_id` | `keyword` | Applied DRM policy ID | `"POL-CONFIDENTIAL"` |
| `drm_policy_name` | `keyword` | Policy display name | `"Confidential - No Print"` |
| `drm_protection_expiry` | `date` | When protection expires | `"2027-01-01T00:00:00Z"` |
| `drm_watermark_text` | `keyword` | Applied watermark text | `"CONFIDENTIAL - Alice Smith"` |
| `drm_print_allowed` | `boolean` | Printing permitted | `false` |
| `drm_copy_allowed` | `boolean` | Copy/paste permitted | `false` |
| `drm_offline_access_allowed` | `boolean` | Offline access permitted | `true` |
| `drm_access_count` | `integer` | Total opens since protection applied | `12` |
| `drm_revocation_reason` | `keyword` | Why access was revoked | `"EMPLOYEE_LEFT"` |

---

## Email Body Protection Fields

`event_type` values: `EMAIL.PROTECTION_APPLIED`, `EMAIL.EMAIL_SENT`,
`EMAIL.EXTERNAL_RECIPIENT_DETECTED`, `EMAIL.POLICY_TRIGGERED`

| Field | Type | Description | Example |
|---|---|---|---|
| `email_message_id` | `keyword` | Email message ID | `"MSG-20260315-001"` |
| `email_subject` | `keyword` | Email subject (hashed in high-security mode) | `"Q1 Budget Review"` |
| `email_sender` | `keyword` | Sender email address | `"alice@acme.com"` |
| `email_recipients` | `keyword[]` | All recipient addresses | `["bob@acme.com"]` |
| `email_recipient_domains` | `keyword[]` | Recipient domains | `["acme.com","partner.com"]` |
| `email_has_external_recipient` | `boolean` | Any recipient outside org | `true` |
| `email_attachment_count` | `integer` | Number of attachments | `2` |
| `email_attachment_file_ids` | `keyword[]` | File IDs of DRM-protected attachments | `["F-abc123"]` |
| `email_body_protected` | `boolean` | Body protection applied | `true` |
| `email_policy_id` | `keyword` | Email security policy applied | `"EP-EXTERNAL-BLOCK"` |
| `email_direction` | `keyword` | `OUTBOUND`, `INBOUND` | `"OUTBOUND"` |

---

## Anomaly and Baseline Fields

These fields are populated by the anomaly detection layer (post-processing, not at ingest).

| Field | Type | Description | Example |
|---|---|---|---|
| `anomaly_score` | `float` | Deviation from baseline (0.0–1.0) | `0.87` |
| `anomaly_flags` | `keyword[]` | What triggered the anomaly | `["UNUSUAL_HOUR", "LARGE_FILE"]` |
| `baseline_period_days` | `integer` | Baseline window used | `365` |
| `is_anomaly` | `boolean` | Whether this event is flagged | `true` |

---

## Cross-Border / Sovereignty Fields

| Field | Type | Description | Example |
|---|---|---|---|
| `source_country` | `keyword` | Country of the acting user | `"US"` |
| `destination_country` | `keyword` | Country of recipient / access | `"DE"` |
| `cross_border_transfer` | `boolean` | Data crossed country boundary | `true` |
| `sovereignty_violation` | `boolean` | Crossed a geo-restriction boundary | `false` |

---

## Complete Example Event (EFSS share)

```json
{
  "organization_id": "acme-corp",
  "tenant_name": "Acme Corporation",
  "event_id": "a1b2c3d4-1111-2222-3333-444455556666",
  "event_type": "EFSS.FILE_SHARED",
  "module": "EFSS",
  "@timestamp": "2026-03-15T10:30:00Z",
  "schema_version": "1.0",

  "user_id": "U-12345",
  "user_email": "alice@acme.com",
  "user_display_name": "Alice Smith",
  "user_department": "Finance",
  "user_group": "finance-team",
  "user_location": "US-NYC",
  "user_device_id": "DEV-WIN-001",
  "user_ip": "192.168.1.10",

  "file_id": "F-abc123",
  "file_name": "budget-2026.xlsx",
  "file_name_text": "budget-2026.xlsx",
  "file_extension": "xlsx",
  "file_size_bytes": 1048576,
  "file_path": "/Finance/Q1/budget-2026.xlsx",
  "file_hash_sha256": "abc123def456...",
  "file_mime_type": "application/vnd.ms-excel",

  "data_classification": "CONFIDENTIAL",
  "nist_impact_level": "MODERATE",
  "contains_pii": false,
  "contains_financial_data": true,
  "contains_health_data": false,
  "contains_ip": true,
  "contains_export_controlled": false,
  "contains_cui": false,
  "contains_classified": false,
  "contains_sensitive_pii": false,
  "geo_restricted": true,
  "geo_restriction_region": "US",
  "ai_use_restricted": false,
  "data_categories": ["FINANCIAL", "IP"],

  "efss_share_id": "SH-9876",
  "efss_share_type": "EXTERNAL",
  "efss_recipient_email": "bob@partner.com",
  "efss_recipient_domain": "partner.com",
  "efss_recipient_is_external": true,
  "efss_permission_type": "VIEW",
  "efss_share_expiry": "2026-04-15T00:00:00Z",
  "efss_share_has_password": false,
  "efss_access_location_country": "US",
  "efss_access_location_city": "New York",
  "efss_chain_depth": 0,
  "efss_shared_from_user_id": "U-12345",
  "efss_domain_whitelist_match": true,
  "efss_ip_whitelist_match": true,

  "cross_border_transfer": false,
  "sovereignty_violation": false,
  "source_country": "US",
  "destination_country": "US",

  "is_anomaly": false,
  "anomaly_score": 0.12
}
```

---

## OpenSearch Index Template

Use [configs/index-templates/vaultize-events.json](../../configs/index-templates/vaultize-events.json)
to create the index template before ingesting data.

Key settings:
- `organization_id` → `keyword` (required for DLS)
- All boolean fields → `boolean`
- All timestamp fields → `date`
- `*_text` fields → `text` (analyzed, for full-text search)
- Everything else → `keyword` (exact match, aggregatable)

---

*Last Updated: 2026-03-15*
