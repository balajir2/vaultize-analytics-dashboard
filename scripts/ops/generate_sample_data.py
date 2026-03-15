#!/usr/bin/env python3
"""
Vaultize Analytics Platform - Sample Data Generator

Generates realistic sample events across all modules for multiple tenants.
Used to populate the analytics platform for demonstrations and testing.

Coverage:
  - 2 tenants: acme-corp, techstart
  - 4 modules: CDP, EFSS, DRM, EMAIL
  - Data categories: PII, financial, health, IP, CUI, classified, export-controlled
  - Security events: anomalies, cross-border transfers, sovereignty violations
  - Time range: last 30 days (configurable)

Usage:
    python scripts/ops/generate_sample_data.py
    python scripts/ops/generate_sample_data.py --days 90 --count 500

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import argparse
import json
import os
import random
import uuid
import urllib.request
import urllib.error
import base64
import ssl
from datetime import datetime, timedelta, timezone


# ============================================================================
# Data Fixtures
# ============================================================================

TENANTS = [
    {"organization_id": "acme-corp",  "tenant_name": "Acme Corporation"},
    {"organization_id": "techstart",  "tenant_name": "TechStart Inc"},
]

USERS = {
    "acme-corp": [
        {"user_id": "U-1001", "user_email": "alice.smith@acme-corp.com", "user_display_name": "Alice Smith",   "user_department": "Finance",      "user_group": "finance-team",    "user_location": "US-NYC"},
        {"user_id": "U-1002", "user_email": "bob.jones@acme-corp.com",   "user_display_name": "Bob Jones",     "user_department": "Legal",        "user_group": "legal-team",      "user_location": "US-SFO"},
        {"user_id": "U-1003", "user_email": "carol.wu@acme-corp.com",    "user_display_name": "Carol Wu",      "user_department": "Engineering",  "user_group": "developers",      "user_location": "US-SEA"},
        {"user_id": "U-1004", "user_email": "david.lee@acme-corp.com",   "user_display_name": "David Lee",     "user_department": "HR",           "user_group": "hr-team",         "user_location": "US-NYC"},
        {"user_id": "U-1005", "user_email": "eva.martin@acme-corp.com",  "user_display_name": "Eva Martin",    "user_department": "Sales",        "user_group": "sales-team",      "user_location": "UK-LON"},
    ],
    "techstart": [
        {"user_id": "U-2001", "user_email": "james.k@techstart.io",      "user_display_name": "James Kumar",   "user_department": "Product",      "user_group": "product-team",    "user_location": "IN-BLR"},
        {"user_id": "U-2002", "user_email": "priya.n@techstart.io",      "user_display_name": "Priya Nair",    "user_department": "Engineering",  "user_group": "developers",      "user_location": "IN-MUM"},
        {"user_id": "U-2003", "user_email": "tom.b@techstart.io",        "user_display_name": "Tom Brown",     "user_department": "Finance",      "user_group": "finance-team",    "user_location": "SG-SGP"},
        {"user_id": "U-2004", "user_email": "lisa.c@techstart.io",       "user_display_name": "Lisa Chen",     "user_department": "Sales",        "user_group": "sales-team",      "user_location": "SG-SGP"},
    ],
}

FILES = [
    {"file_id": "F-001", "file_name": "budget-2026.xlsx",            "file_extension": "xlsx",  "file_size_bytes": 1048576,   "file_mime_type": "application/vnd.ms-excel",             "data_classification": "CONFIDENTIAL", "contains_financial_data": True},
    {"file_id": "F-002", "file_name": "employee-records.xlsx",       "file_extension": "xlsx",  "file_size_bytes": 524288,    "file_mime_type": "application/vnd.ms-excel",             "data_classification": "RESTRICTED",   "contains_pii": True, "contains_sensitive_pii": True},
    {"file_id": "F-003", "file_name": "product-roadmap-2026.pptx",   "file_extension": "pptx",  "file_size_bytes": 5242880,   "file_mime_type": "application/vnd.ms-powerpoint",        "data_classification": "CONFIDENTIAL", "contains_ip": True},
    {"file_id": "F-004", "file_name": "patient-data-q1.csv",         "file_extension": "csv",   "file_size_bytes": 2097152,   "file_mime_type": "text/csv",                             "data_classification": "RESTRICTED",   "contains_health_data": True, "contains_pii": True},
    {"file_id": "F-005", "file_name": "export-license-specs.pdf",    "file_extension": "pdf",   "file_size_bytes": 786432,    "file_mime_type": "application/pdf",                      "data_classification": "CONFIDENTIAL", "contains_export_controlled": True},
    {"file_id": "F-006", "file_name": "source-code-v2.zip",          "file_extension": "zip",   "file_size_bytes": 10485760,  "file_mime_type": "application/zip",                      "data_classification": "CONFIDENTIAL", "contains_ip": True},
    {"file_id": "F-007", "file_name": "contract-nda-signed.pdf",     "file_extension": "pdf",   "file_size_bytes": 262144,    "file_mime_type": "application/pdf",                      "data_classification": "CONFIDENTIAL"},
    {"file_id": "F-008", "file_name": "quarterly-report.pdf",        "file_extension": "pdf",   "file_size_bytes": 3145728,   "file_mime_type": "application/pdf",                      "data_classification": "INTERNAL",     "contains_financial_data": True},
    {"file_id": "F-009", "file_name": "security-audit-2025.docx",    "file_extension": "docx",  "file_size_bytes": 1572864,   "file_mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "data_classification": "RESTRICTED", "contains_cui": True},
    {"file_id": "F-010", "file_name": "hr-policy-handbook.pdf",      "file_extension": "pdf",   "file_size_bytes": 4194304,   "file_mime_type": "application/pdf",                      "data_classification": "INTERNAL",     "contains_pii": False},
]

DOMAINS = {
    "external": ["partner.com", "vendor.io", "consulting-firm.co", "client-corp.com", "law-firm.legal", "gmail.com", "outlook.com"],
    "risky":    ["unknown-domain.ru", "temp-mail.org", "mailinator.com"],
}

COUNTRIES = ["US", "GB", "DE", "FR", "IN", "SG", "JP", "CA", "AU", "BR", "CN", "RU"]


def random_ts(days_back: int) -> str:
    now = datetime.now(timezone.utc)
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return (now - delta).strftime("%Y-%m-%dT%H:%M:%SZ")


def base_event(tenant: dict, user: dict, file: dict, event_type: str, module: str, days_back: int) -> dict:
    """Build the mandatory fields shared by all events."""
    file_fields = {
        "file_id":         file.get("file_id", ""),
        "file_name":       file.get("file_name", ""),
        "file_name_text":  file.get("file_name", ""),
        "file_extension":  file.get("file_extension", ""),
        "file_size_bytes": file.get("file_size_bytes", 0),
        "file_path":       f"/{user.get('user_department', 'Shared')}/{file.get('file_name', '')}",
        "file_hash_sha256": uuid.uuid4().hex * 2,
        "file_mime_type":  file.get("file_mime_type", "application/octet-stream"),
    }

    data_cats = []
    if file.get("contains_pii"):          data_cats.append("PII")
    if file.get("contains_financial_data"): data_cats.append("FINANCIAL")
    if file.get("contains_health_data"):  data_cats.append("HEALTH")
    if file.get("contains_ip"):           data_cats.append("IP")
    if file.get("contains_cui"):          data_cats.append("CUI")
    if file.get("contains_export_controlled"): data_cats.append("EXPORT_CONTROLLED")

    nist = "LOW"
    if file.get("data_classification") == "RESTRICTED":  nist = "HIGH"
    elif file.get("data_classification") == "CONFIDENTIAL": nist = "MODERATE"

    src_country = user.get("user_location", "US").split("-")[0]
    return {
        **tenant,
        "event_id":     str(uuid.uuid4()),
        "event_type":   event_type,
        "module":       module,
        "@timestamp":   random_ts(days_back),
        "schema_version": "1.0",

        **{k: v for k, v in user.items()},
        "user_device_id": f"DEV-{random.randint(100,999)}",
        "user_ip":      f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",

        **file_fields,

        "data_classification":        file.get("data_classification", "INTERNAL"),
        "nist_impact_level":          nist,
        "contains_pii":               file.get("contains_pii", False),
        "contains_sensitive_pii":     file.get("contains_sensitive_pii", False),
        "contains_financial_data":    file.get("contains_financial_data", False),
        "contains_health_data":       file.get("contains_health_data", False),
        "contains_ip":                file.get("contains_ip", False),
        "contains_export_controlled": file.get("contains_export_controlled", False),
        "contains_cui":               file.get("contains_cui", False),
        "contains_classified":        False,
        "geo_restricted":             file.get("data_classification") in ("RESTRICTED", "CONFIDENTIAL"),
        "geo_restriction_region":     src_country,
        "ai_use_restricted":          file.get("contains_health_data", False) or file.get("contains_pii", False),
        "data_categories":            data_cats,

        "source_country":             src_country,
        "destination_country":        src_country,
        "cross_border_transfer":      False,
        "sovereignty_violation":      False,

        "is_anomaly":     False,
        "anomaly_score":  round(random.uniform(0.0, 0.3), 3),
        "anomaly_flags":  [],
        "baseline_period_days": 365,
    }


# ============================================================================
# Module Event Generators
# ============================================================================

def gen_cdp_event(tenant, user, file, days_back):
    event_types = ["CDP.BACKUP_CREATED", "CDP.BACKUP_UPDATED", "CDP.BACKUP_CREATED",
                   "CDP.BACKUP_CREATED", "CDP.RESTORE_INITIATED"]
    event_type = random.choice(event_types)
    ev = base_event(tenant, user, file, event_type, "CDP", days_back)
    ev.update({
        "cdp_backup_id":         f"BK-{random.randint(10000,99999)}",
        "cdp_folder_path":       f"C:\\Users\\{user['user_display_name'].split()[0]}\\Documents",
        "cdp_folder_mapping_id": f"FM-{random.randint(1,20)}",
        "cdp_retention_policy":  random.choice(["30-day-daily", "90-day-weekly", "1-year-monthly"]),
        "cdp_backup_size_bytes": random.randint(1024, 100 * 1024 * 1024),
        "cdp_version_number":    random.randint(1, 50),
        "cdp_restore_point":     random_ts(days_back + 10),
        "cdp_device_os":         random.choice(["Windows 11", "Windows 10", "macOS 14"]),
        "cdp_agent_version":     random.choice(["4.2.1", "4.2.0", "4.1.5"]),
    })
    return ev


def gen_efss_event(tenant, user, file, days_back):
    event_types = ["EFSS.FILE_SHARED", "EFSS.FILE_SHARED", "EFSS.FILE_ACCESSED",
                   "EFSS.FILE_DOWNLOADED", "EFSS.FILE_UPLOADED", "EFSS.SHARE_REVOKED"]
    event_type = random.choice(event_types)
    is_external = random.random() > 0.4

    # Occasionally use a risky domain
    risky = random.random() > 0.85
    if is_external:
        domain = random.choice(DOMAINS["risky"] if risky else DOMAINS["external"])
        recipient = f"recipient{random.randint(1,99)}@{domain}"
    else:
        domain = tenant["organization_id"] + ".com"
        recipient = f"internal{random.randint(1,20)}@{domain}"

    dest_country = random.choice(COUNTRIES) if is_external else user.get("user_location", "US").split("-")[0]
    src_country = user.get("user_location", "US").split("-")[0]
    cross_border = src_country != dest_country

    # Sovereignty violation: geo-restricted data leaving restricted region
    sov_violation = cross_border and file.get("data_classification") in ("RESTRICTED", "CONFIDENTIAL") and \
                    file.get("geo_restricted", False)

    # Anomaly: unusual recipient, unusual time, large file
    anomaly_score = round(random.uniform(0.0, 0.3), 3)
    anomaly_flags = []
    if risky:
        anomaly_score = round(random.uniform(0.7, 0.99), 3)
        anomaly_flags.append("SUSPICIOUS_DOMAIN")
    if cross_border and sov_violation:
        anomaly_flags.append("SOVEREIGNTY_VIOLATION")

    ev = base_event(tenant, user, file, event_type, "EFSS", days_back)
    ev.update({
        "destination_country":      dest_country,
        "cross_border_transfer":    cross_border,
        "sovereignty_violation":    sov_violation,
        "is_anomaly":               len(anomaly_flags) > 0 or anomaly_score > 0.7,
        "anomaly_score":            anomaly_score,
        "anomaly_flags":            anomaly_flags,

        "efss_share_id":            f"SH-{random.randint(10000,99999)}",
        "efss_share_type":          "EXTERNAL" if is_external else "INTERNAL",
        "efss_recipient_email":     recipient,
        "efss_recipient_domain":    domain,
        "efss_recipient_is_external": is_external,
        "efss_permission_type":     random.choice(["VIEW", "VIEW", "DOWNLOAD", "EDIT"]),
        "efss_share_expiry":        random_ts(30),  # future expiry
        "efss_share_has_password":  random.random() > 0.7,
        "efss_access_location_country": dest_country,
        "efss_access_location_city": random.choice(["New York", "London", "Berlin", "Singapore", "Tokyo"]),
        "efss_chain_depth":         random.choices([0, 1, 2, 3], weights=[70, 20, 7, 3])[0],
        "efss_shared_from_user_id": user["user_id"],
        "efss_domain_whitelist_match": not risky,
        "efss_ip_whitelist_match":  random.random() > 0.2,
    })
    return ev


def gen_drm_event(tenant, user, file, days_back):
    event_types = ["DRM.PROTECTION_APPLIED", "DRM.DOCUMENT_OPENED", "DRM.DOCUMENT_OPENED",
                   "DRM.DOCUMENT_PRINTED", "DRM.ACCESS_REVOKED", "DRM.WATERMARK_ADDED"]
    event_type = random.choice(event_types)
    ev = base_event(tenant, user, file, event_type, "DRM", days_back)
    policy = random.choice(["POL-CONFIDENTIAL", "POL-RESTRICTED", "POL-VIEW-ONLY"])
    policy_names = {
        "POL-CONFIDENTIAL": "Confidential - No Print No Copy",
        "POL-RESTRICTED": "Restricted - Read Only",
        "POL-VIEW-ONLY": "View Only - Watermarked",
    }
    ev.update({
        "drm_document_id":            f"DRM-{random.randint(10000,99999)}",
        "drm_policy_id":              policy,
        "drm_policy_name":            policy_names[policy],
        "drm_protection_expiry":      random_ts(180),
        "drm_watermark_text":         f"CONFIDENTIAL - {user['user_display_name']}",
        "drm_print_allowed":          policy == "POL-CONFIDENTIAL" and random.random() > 0.7,
        "drm_copy_allowed":           policy != "POL-CONFIDENTIAL",
        "drm_offline_access_allowed": random.random() > 0.5,
        "drm_access_count":           random.randint(1, 100),
        "drm_revocation_reason":      random.choice(["EMPLOYEE_LEFT", "CONTRACT_ENDED", "POLICY_CHANGE", ""]),
    })
    return ev


def gen_email_event(tenant, user, file, days_back):
    event_types = ["EMAIL.PROTECTION_APPLIED", "EMAIL.EMAIL_SENT", "EMAIL.EMAIL_SENT",
                   "EMAIL.EXTERNAL_RECIPIENT_DETECTED", "EMAIL.POLICY_TRIGGERED"]
    event_type = random.choice(event_types)
    has_external = random.random() > 0.5
    recipients = [f"colleague{i}@{tenant['organization_id']}.com" for i in range(1, random.randint(2, 4))]
    recipient_domains = [tenant["organization_id"] + ".com"]
    if has_external:
        ext_domain = random.choice(DOMAINS["external"])
        recipients.append(f"external@{ext_domain}")
        recipient_domains.append(ext_domain)
    ev = base_event(tenant, user, file, event_type, "EMAIL", days_back)
    ev.update({
        "email_message_id":             f"MSG-{uuid.uuid4().hex[:12]}",
        "email_subject":                random.choice([
            "Q1 Budget Review", "NDA for Review", "Project Roadmap", "Contract Draft",
            "HR Policy Update", "Security Audit Results", "Quarterly Report"
        ]),
        "email_sender":                 user["user_email"],
        "email_recipients":             recipients,
        "email_recipient_domains":      list(set(recipient_domains)),
        "email_has_external_recipient": has_external,
        "email_attachment_count":       random.randint(0, 3),
        "email_attachment_file_ids":    [file["file_id"]] if random.random() > 0.4 else [],
        "email_body_protected":         file.get("data_classification") in ("CONFIDENTIAL", "RESTRICTED"),
        "email_policy_id":              random.choice(["EP-DEFAULT", "EP-EXTERNAL-MONITOR", "EP-RESTRICTED"]),
        "email_direction":              "OUTBOUND",
    })
    return ev


# ============================================================================
# Bulk Indexing
# ============================================================================

class OpenSearchClient:
    def __init__(self, host, port, username, password, scheme="https"):
        self.base_url = f"{scheme}://{host}:{port}"
        creds = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-ndjson",
        }
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def bulk_index(self, index: str, docs: list):
        lines = []
        for doc in docs:
            lines.append(json.dumps({"index": {"_index": index}}))
            lines.append(json.dumps(doc))
        body = "\n".join(lines) + "\n"
        url = f"{self.base_url}/_bulk"
        req = urllib.request.Request(url, data=body.encode(), headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=self.ctx) as resp:
                result = json.loads(resp.read())
                errors = [i for i in result.get("items", []) if "error" in i.get("index", {})]
                return len(docs) - len(errors), len(errors)
        except urllib.error.HTTPError as e:
            print(f"  [ERR] Bulk index failed: {e.code} {e.read()[:200]}")
            return 0, len(docs)


# ============================================================================
# Main
# ============================================================================

def generate_events(total_count: int, days_back: int) -> list:
    events = []
    generators = [gen_cdp_event, gen_efss_event, gen_efss_event, gen_drm_event, gen_email_event]

    for _ in range(total_count):
        tenant = random.choice(TENANTS)
        user = random.choice(USERS[tenant["organization_id"]])
        file = random.choice(FILES)
        gen = random.choice(generators)
        events.append(gen(tenant, user, file, days_back))

    return events


def main():
    parser = argparse.ArgumentParser(description="Generate Vaultize sample events")
    parser.add_argument("--count", type=int, default=200, help="Number of events to generate (default: 200)")
    parser.add_argument("--days", type=int, default=30, help="Date range in days back (default: 30)")
    parser.add_argument("--host", default=os.environ.get("OPENSEARCH_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("OPENSEARCH_PORT", "9200")))
    parser.add_argument("--scheme", default=os.environ.get("OPENSEARCH_SCHEME", "https"))
    parser.add_argument("--user", default=os.environ.get("OPENSEARCH_USER", "admin"))
    parser.add_argument("--password", default=os.environ.get("OPENSEARCH_PASSWORD", "vaultize"))
    parser.add_argument("--dry-run", action="store_true", help="Print events, don't index")
    args = parser.parse_args()

    print(f"Generating {args.count} events across {len(TENANTS)} tenants, {args.days} days...")
    events = generate_events(args.count, args.days)

    if args.dry_run:
        print(json.dumps(events[0], indent=2))
        print(f"\n[DRY RUN] Would index {len(events)} events.")
        return

    client = OpenSearchClient(args.host, args.port, args.user, args.password, args.scheme)

    # Group by date for daily indices
    from collections import defaultdict
    by_date = defaultdict(list)
    for ev in events:
        date = ev["@timestamp"][:10].replace("-", ".")
        by_date[f"vaultize-events-{date}"].append(ev)

    total_ok = total_err = 0
    for index, docs in sorted(by_date.items()):
        ok, err = client.bulk_index(index, docs)
        total_ok += ok
        total_err += err
        print(f"  {index}: {ok} indexed, {err} errors")

    print(f"\nDone. {total_ok} events indexed, {total_err} errors.")

    # Print breakdown by tenant and module
    from collections import Counter
    tenant_counts = Counter(e["organization_id"] for e in events)
    module_counts = Counter(e["module"] for e in events)
    print(f"\nBreakdown by tenant: {dict(tenant_counts)}")
    print(f"Breakdown by module: {dict(module_counts)}")
    anomaly_count = sum(1 for e in events if e.get("is_anomaly"))
    cross_border = sum(1 for e in events if e.get("cross_border_transfer"))
    sovereignty = sum(1 for e in events if e.get("sovereignty_violation"))
    print(f"Anomalies: {anomaly_count}, Cross-border: {cross_border}, Sovereignty violations: {sovereignty}")


if __name__ == "__main__":
    main()
