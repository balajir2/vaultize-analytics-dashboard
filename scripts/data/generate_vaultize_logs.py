#!/usr/bin/env python3
"""
Vaultize Document Management Log Generator

Generates realistic log data simulating a Vaultize-style enterprise
document management and data protection platform.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import requests

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
INDEX_PREFIX = "logs"
NUM_LOGS = 5000
TIME_RANGE_HOURS = 72  # 3 days of data

# ============================================================================
# Vaultize Domain Data
# ============================================================================

SERVICES = [
    "doc-gateway",       # Document upload/download gateway
    "vault-storage",     # Encrypted file storage engine
    "access-control",    # RBAC and permissions
    "sync-engine",       # Device sync and replication
    "audit-service",     # Compliance audit trail
    "drm-engine",        # Digital rights management
    "policy-engine",     # Data loss prevention policies
    "search-indexer",    # Full-text document search
    "notification-svc",  # Email/push notifications
    "admin-console",     # Admin web interface
]

HOSTS = [
    "vault-prod-01", "vault-prod-02", "vault-prod-03",
    "vault-sync-01", "vault-sync-02",
    "vault-index-01", "vault-admin-01",
]

USERS = [
    "balaji.rajan", "priya.sharma", "rahul.kumar", "sneha.patel",
    "amit.verma", "deepika.nair", "arjun.reddy", "kavitha.iyer",
    "vikram.singh", "ananya.menon", "svc-sync", "svc-backup",
    "admin@vaultize.local", "compliance-bot",
]

DEPARTMENTS = [
    "Engineering", "Finance", "Legal", "HR", "Marketing",
    "Sales", "Executive", "Operations", "Compliance", "IT",
]

FILE_TYPES = [
    ".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".csv",
    ".jpg", ".png", ".zip", ".dwg", ".eml", ".msg",
]

FILE_NAMES = [
    "Q4-Financial-Report", "Board-Meeting-Minutes", "Employee-Handbook",
    "Product-Roadmap-2026", "Client-Contract-Draft", "NDA-Template",
    "Architecture-Diagram", "Sales-Forecast", "Budget-Proposal",
    "Compliance-Audit-Report", "Patent-Filing-Draft", "Marketing-Plan",
    "Risk-Assessment", "Incident-Report", "Data-Classification-Policy",
    "Vendor-Agreement", "Project-Timeline", "Security-Review",
    "Merger-Documents", "Tax-Filing-2025", "Insurance-Policy",
    "Legal-Opinion", "Due-Diligence-Report", "Strategic-Plan",
    "Org-Chart", "Performance-Review-Template", "Travel-Expense-Report",
    "Customer-Data-Export", "Backup-Recovery-Plan", "SLA-Agreement",
]

DLP_POLICIES = [
    "PII-Detection", "Credit-Card-Scanner", "SSN-Protection",
    "HIPAA-Compliance", "GDPR-Right-to-Erasure", "Financial-Data-Guard",
    "Confidential-Watermark", "External-Share-Block", "USB-Copy-Prevention",
    "Print-Restriction",
]

DEVICES = [
    "Windows-Laptop", "MacBook-Pro", "iPhone-15", "iPad-Air",
    "Android-Phone", "Web-Browser", "Outlook-Plugin", "Desktop-Agent",
]

SHARE_TARGETS = [
    "external-auditor@kpmg.com", "legal@partnerfirm.com",
    "investor@fundgroup.com", "contractor@vendor.io",
    "client@enterprise.com", "board-member@company.com",
]

# ============================================================================
# Log Templates by Service
# ============================================================================

def _rand_file():
    return f"{random.choice(FILE_NAMES)}{random.choice(FILE_TYPES)}"

def _rand_size():
    return random.choice([
        f"{random.randint(10, 999)} KB",
        f"{random.randint(1, 50)} MB",
        f"{random.randint(51, 500)} MB",
    ])

def _rand_vault():
    return random.choice([
        "Corporate-Vault", "Legal-Vault", "Finance-Vault",
        "HR-Confidential", "Engineering-Shared", "Executive-Suite",
        "Compliance-Archive", "Project-Alpha", "Client-Documents",
    ])


def gen_doc_gateway(level, user):
    """Document gateway operations."""
    ops = {
        "DEBUG": [
            f"Chunked upload started: {_rand_file()} ({_rand_size()}) from {random.choice(DEVICES)}",
            f"Download stream opened for {_rand_file()} by {user}",
            f"Multipart upload chunk {random.randint(1,20)}/{random.randint(20,25)} received",
        ],
        "INFO": [
            f"Document uploaded: {_rand_file()} ({_rand_size()}) to {_rand_vault()} by {user}",
            f"Document downloaded: {_rand_file()} by {user} from {random.choice(DEVICES)}",
            f"Document version created: {_rand_file()} v{random.randint(2,15)} by {user}",
            f"Bulk upload completed: {random.randint(5,50)} files ({random.randint(10,500)} MB) by {user}",
            f"Document preview generated: {_rand_file()} (thumbnail + PDF)",
            f"Document moved: {_rand_file()} from {_rand_vault()} to {_rand_vault()} by {user}",
            f"Document renamed: {_rand_file()} by {user}",
        ],
        "WARN": [
            f"Large file upload: {_rand_file()} ({random.randint(200,999)} MB) - may impact performance",
            f"Duplicate file detected: {_rand_file()} already exists in {_rand_vault()}",
            f"Upload retry attempt {random.randint(2,5)} for {_rand_file()} - network instability",
            f"File type not in allowed list: .exe blocked for {user}",
        ],
        "ERROR": [
            f"Upload failed: {_rand_file()} - storage quota exceeded for {_rand_vault()}",
            f"Download failed: {_rand_file()} - file corrupted (checksum mismatch)",
            f"Upload timeout: {_rand_file()} ({_rand_size()}) after 300s - connection dropped",
            f"Document conversion failed: {_rand_file()} - unsupported format",
        ],
        "FATAL": [
            f"Storage backend unreachable - all uploads suspended",
            f"Gateway certificate expired - TLS handshake failing for all clients",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_vault_storage(level, user):
    """Encrypted storage operations."""
    ops = {
        "DEBUG": [
            f"AES-256 encryption applied to {_rand_file()} (block {random.randint(1,100)})",
            f"Deduplication check: {_rand_file()} hash={random.randbytes(8).hex()}",
            f"Storage tier evaluation: {_rand_file()} -> {'hot' if random.random() > 0.5 else 'cold'}",
        ],
        "INFO": [
            f"File encrypted and stored: {_rand_file()} in {_rand_vault()} ({_rand_size()})",
            f"File decrypted for download: {_rand_file()} requested by {user}",
            f"Vault created: {_rand_vault()} with AES-256 encryption by {user}",
            f"Storage migration completed: {random.randint(100,5000)} files moved to cold tier",
            f"Deduplication saved {random.randint(1,50)} GB across {_rand_vault()}",
            f"Backup snapshot completed: {_rand_vault()} ({random.randint(1,100)} GB)",
        ],
        "WARN": [
            f"Storage utilization at {random.randint(80,95)}% for {_rand_vault()} - approaching quota",
            f"Encryption key rotation due in {random.randint(1,7)} days for {_rand_vault()}",
            f"Cold storage retrieval slow: {_rand_file()} took {random.randint(10,60)}s",
        ],
        "ERROR": [
            f"Encryption failed: {_rand_file()} - HSM module unavailable",
            f"Storage write failed: {_rand_vault()} - disk I/O error on vault-prod-{random.randint(1,3):02d}",
            f"Backup failed: {_rand_vault()} - insufficient backup storage",
            f"File integrity check failed: {_rand_file()} - corrupted blocks detected",
        ],
        "FATAL": [
            f"HSM module offline - all encryption operations suspended",
            f"Primary storage array failure - initiating failover to DR site",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_access_control(level, user):
    """RBAC and permissions."""
    ops = {
        "DEBUG": [
            f"Permission check: {user} requesting '{random.choice(['read','write','delete','share'])}' on {_rand_file()}",
            f"Token validated for {user} (expires in {random.randint(5,120)} min)",
            f"Role membership resolved: {user} -> {random.choice(DEPARTMENTS)}-{random.choice(['Viewer','Editor','Admin'])}",
        ],
        "INFO": [
            f"Access granted: {user} ({random.choice(DEPARTMENTS)}) -> {_rand_file()} [{random.choice(['read','write','download'])}]",
            f"Permission updated: {_rand_file()} shared with {random.choice(DEPARTMENTS)} department by {user}",
            f"User login: {user} from {random.choice(DEVICES)} (IP: 10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)})",
            f"User logout: {user} session duration {random.randint(5,480)} minutes",
            f"Role assigned: {user} -> {random.choice(DEPARTMENTS)}-{random.choice(['Viewer','Editor','Admin'])} by admin@vaultize.local",
            f"MFA verified: {user} via {random.choice(['authenticator-app', 'SMS', 'hardware-token', 'email-OTP'])}",
        ],
        "WARN": [
            f"Failed login attempt {random.randint(2,4)}/5 for {user} from IP 203.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            f"Suspicious access pattern: {user} accessed {random.randint(50,200)} files in {random.randint(1,5)} minutes",
            f"Permission denied: {user} attempted '{random.choice(['delete','share-external','admin-access'])}' on {_rand_file()}",
            f"Session token near expiry for {user} - {random.randint(1,5)} minutes remaining",
        ],
        "ERROR": [
            f"Account locked: {user} - 5 consecutive failed login attempts",
            f"Authentication failed: {user} - invalid MFA code (3 attempts exhausted)",
            f"LDAP sync failed: unable to resolve group membership for {random.choice(DEPARTMENTS)}",
            f"SSO callback error: SAML assertion validation failed for {user}",
        ],
        "FATAL": [
            f"LDAP/AD connection lost - authentication fallback to local accounts only",
            f"Certificate authority unreachable - client certificate validation disabled",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_sync_engine(level, user):
    """Device sync operations."""
    ops = {
        "DEBUG": [
            f"Sync delta calculated: {random.randint(1,50)} files changed for {user} on {random.choice(DEVICES)}",
            f"Conflict detection: comparing local vs server version of {_rand_file()}",
        ],
        "INFO": [
            f"Sync completed: {random.randint(1,100)} files ({_rand_size()}) for {user} on {random.choice(DEVICES)}",
            f"Selective sync updated: {user} added {_rand_vault()} to {random.choice(DEVICES)}",
            f"Offline cache prepared: {random.randint(10,200)} files for {user} ({_rand_size()})",
            f"Remote wipe executed: {random.choice(DEVICES)} for {user} by admin@vaultize.local",
            f"Device registered: {random.choice(DEVICES)} for {user} (device #{random.randint(1,5)})",
        ],
        "WARN": [
            f"Sync conflict: {_rand_file()} modified on both server and {random.choice(DEVICES)} by {user}",
            f"Slow sync: {user} on {random.choice(DEVICES)} - {random.randint(30,120)}s for {random.randint(5,20)} files",
            f"Device offline for {random.randint(24,168)} hours: {random.choice(DEVICES)} ({user})",
        ],
        "ERROR": [
            f"Sync failed: {user} on {random.choice(DEVICES)} - server unreachable after {random.randint(3,5)} retries",
            f"Remote wipe failed: {random.choice(DEVICES)} ({user}) - device not responding",
            f"Sync corruption detected: {_rand_file()} on {random.choice(DEVICES)} - forcing re-download",
        ],
        "FATAL": [
            f"Sync service database corrupted - emergency rebuild initiated",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_audit_service(level, user):
    """Compliance audit trail."""
    ops = {
        "DEBUG": [
            f"Audit event queued: {random.choice(['file_access','file_share','policy_change','user_login'])} by {user}",
        ],
        "INFO": [
            f"Audit log: {user} shared {_rand_file()} externally to {random.choice(SHARE_TARGETS)}",
            f"Audit log: {user} deleted {_rand_file()} from {_rand_vault()} (moved to trash, {random.randint(30,90)}-day retention)",
            f"Audit log: {user} exported {random.randint(10,500)} records from {_rand_vault()}",
            f"Compliance report generated: {random.choice(['SOC2','HIPAA','GDPR','ISO27001'])} for {random.choice(DEPARTMENTS)}",
            f"Audit log: {user} printed {_rand_file()} ({random.randint(1,50)} pages) from {random.choice(DEVICES)}",
            f"Retention policy applied: {random.randint(100,1000)} files archived in {_rand_vault()}",
            f"Audit log: {user} changed permissions on {_rand_vault()} ({random.choice(DEPARTMENTS)} access revoked)",
            f"Chain of custody verified: {_rand_file()} - {random.randint(3,12)} access events in last 30 days",
        ],
        "WARN": [
            f"Audit log gap detected: {random.randint(5,30)} events missing between {random.randint(10,14)}:00-{random.randint(14,18)}:00 UTC",
            f"Retention policy violation: {_rand_file()} in {_rand_vault()} past {random.randint(365,730)}-day retention",
            f"High-volume data export: {user} exported {random.randint(500,5000)} files from {_rand_vault()}",
        ],
        "ERROR": [
            f"Audit log write failed: event queue overflow ({random.randint(10000,50000)} pending events)",
            f"Compliance report generation failed: {random.choice(['SOC2','HIPAA'])} - data source timeout",
            f"Tamper detection: audit log checksum mismatch for period {random.choice(['2026-03-08','2026-03-09','2026-03-10'])}",
        ],
        "FATAL": [
            f"Audit database unreachable - compliance logging suspended (CRITICAL COMPLIANCE RISK)",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_drm_engine(level, user):
    """Digital rights management."""
    ops = {
        "DEBUG": [
            f"DRM policy evaluated: {_rand_file()} -> {random.choice(['allow-print','block-copy','watermark','expire-access'])}",
        ],
        "INFO": [
            f"Watermark applied: {_rand_file()} with '{user} - {random.choice(DEPARTMENTS)} - CONFIDENTIAL'",
            f"DRM policy enforced: {_rand_file()} - copy/paste disabled for {user}",
            f"Access expired: {_rand_file()} link for {random.choice(SHARE_TARGETS)} (set by {user})",
            f"View-only access granted: {_rand_file()} to {random.choice(SHARE_TARGETS)} by {user}",
            f"Document recalled: {_rand_file()} access revoked for all {random.randint(2,10)} external recipients by {user}",
            f"Screen capture blocked: {user} attempted screenshot of {_rand_file()} on {random.choice(DEVICES)}",
        ],
        "WARN": [
            f"DRM bypass attempt: {user} tried to print restricted document {_rand_file()}",
            f"Forwarding blocked: {user} attempted to forward {_rand_file()} to unauthorized recipient",
            f"Watermark removal detected: {_rand_file()} metadata stripped by {user} on {random.choice(DEVICES)}",
        ],
        "ERROR": [
            f"DRM license server timeout: unable to validate rights for {_rand_file()}",
            f"Watermark rendering failed: {_rand_file()} - image processing error",
        ],
        "FATAL": [
            f"DRM license server offline - all protected documents inaccessible",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_policy_engine(level, user):
    """Data loss prevention."""
    ops = {
        "DEBUG": [
            f"DLP scan initiated: {_rand_file()} ({_rand_size()}) - policy: {random.choice(DLP_POLICIES)}",
        ],
        "INFO": [
            f"DLP scan passed: {_rand_file()} - no sensitive data detected",
            f"DLP policy applied: {random.choice(DLP_POLICIES)} on {_rand_vault()} by admin@vaultize.local",
            f"Classification assigned: {_rand_file()} -> {random.choice(['Public','Internal','Confidential','Restricted'])} by {user}",
            f"DLP policy updated: {random.choice(DLP_POLICIES)} - {random.choice(['threshold adjusted','new pattern added','scope expanded'])}",
        ],
        "WARN": [
            f"DLP violation: {_rand_file()} contains {random.choice(['SSN patterns','credit card numbers','PII data','health records'])} - upload blocked",
            f"DLP violation: {user} attempted external share of {random.choice(['Confidential','Restricted'])}-classified {_rand_file()}",
            f"Sensitive data detected: {_rand_file()} contains {random.randint(2,20)} {random.choice(['email addresses','phone numbers','passport numbers'])}",
            f"Unclassified document: {_rand_file()} in {_rand_vault()} has no data classification label",
        ],
        "ERROR": [
            f"DLP scan timeout: {_rand_file()} ({_rand_size()}) - exceeded {random.randint(30,120)}s scan limit",
            f"Classification engine error: unable to process {_rand_file()} - OCR module failure",
            f"Policy sync failed: {random.choice(DLP_POLICIES)} not propagated to {random.randint(2,5)} endpoints",
        ],
        "FATAL": [
            f"DLP engine crashed - content inspection bypassed for all uploads (SECURITY RISK)",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_search_indexer(level, user):
    """Full-text document search."""
    ops = {
        "DEBUG": [
            f"Indexing document: {_rand_file()} - extracted {random.randint(100,10000)} tokens",
            f"OCR processing: {_rand_file()} - {random.randint(1,50)} pages scanned",
        ],
        "INFO": [
            f"Search query: '{random.choice(['quarterly report','contract','invoice','policy','budget'])}' by {user} - {random.randint(5,200)} results in {random.randint(50,500)}ms",
            f"Index rebuilt: {_rand_vault()} - {random.randint(1000,50000)} documents ({random.randint(1,100)} GB)",
            f"Document indexed: {_rand_file()} - full text + metadata extracted",
            f"Faceted search: {user} filtered by {random.choice(DEPARTMENTS)} + {random.choice(FILE_TYPES)} - {random.randint(10,500)} results",
        ],
        "WARN": [
            f"Slow query: '{random.choice(['*','report','all documents'])}' by {user} took {random.randint(2000,10000)}ms",
            f"Index lag: {random.randint(100,500)} documents pending indexing (queue depth high)",
            f"OCR quality low: {_rand_file()} - confidence {random.randint(30,60)}% (expected >80%)",
        ],
        "ERROR": [
            f"Index corruption detected: {_rand_vault()} - triggering automatic rebuild",
            f"OCR failed: {_rand_file()} - password-protected PDF, unable to extract text",
            f"Search query failed: syntax error in query from {user}",
        ],
        "FATAL": [
            f"Search index cluster RED - all search operations unavailable",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_notification_svc(level, user):
    """Notifications."""
    ops = {
        "DEBUG": [
            f"Notification queued: {random.choice(['email','push','in-app'])} for {user}",
        ],
        "INFO": [
            f"Email sent: '{_rand_file()} shared with you' to {random.choice(SHARE_TARGETS)} by {user}",
            f"Push notification: 'New version of {_rand_file()} available' to {user} on {random.choice(DEVICES)}",
            f"Digest email sent: {random.randint(5,30)} updates for {user} ({random.choice(DEPARTMENTS)})",
            f"Alert sent: storage quota {random.randint(80,95)}% for {_rand_vault()} to vault admins",
        ],
        "WARN": [
            f"Email delivery delayed: {random.choice(SHARE_TARGETS)} - SMTP queue backlog",
            f"Push notification failed: {user} on {random.choice(DEVICES)} - token expired",
        ],
        "ERROR": [
            f"Email delivery failed: {random.choice(SHARE_TARGETS)} - SMTP connection refused",
            f"Notification template rendering failed: missing variable 'file_name' in share template",
        ],
        "FATAL": [
            f"SMTP server unreachable - all email notifications queued ({random.randint(100,1000)} pending)",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


def gen_admin_console(level, user):
    """Admin console operations."""
    ops = {
        "DEBUG": [
            f"Admin dashboard loaded: {random.choice(['users','storage','policies','audit'])} tab by {user}",
        ],
        "INFO": [
            f"User created: {random.choice(USERS)} in {random.choice(DEPARTMENTS)} by {user}",
            f"Vault provisioned: {_rand_vault()} with {random.randint(10,500)} GB quota by {user}",
            f"Bulk user import: {random.randint(10,100)} users added from CSV by {user}",
            f"System settings updated: {random.choice(['password-policy','session-timeout','MFA-enforcement','backup-schedule'])} by {user}",
            f"License usage: {random.randint(150,480)}/500 users active, {random.randint(500,4000)}/{random.randint(4000,5000)} GB storage used",
            f"System health check: all {random.randint(8,12)} services operational",
        ],
        "WARN": [
            f"License warning: {random.randint(450,490)}/500 user seats consumed ({random.randint(90,98)}%)",
            f"System load high: CPU {random.randint(70,90)}%, Memory {random.randint(75,95)}% on vault-prod-{random.randint(1,3):02d}",
            f"Scheduled maintenance window approaching: {random.choice(['database optimization','certificate renewal','security patch'])}",
        ],
        "ERROR": [
            f"User provisioning failed: {random.choice(USERS)} - LDAP group not found",
            f"Report generation timeout: monthly usage report exceeded 300s limit",
            f"Configuration save failed: {random.choice(['backup-schedule','retention-policy'])} - validation error",
        ],
        "FATAL": [
            f"Admin console database migration failed - service degraded",
        ],
    }
    return random.choice(ops.get(level, ops["INFO"]))


# Service -> generator mapping
SERVICE_GENERATORS = {
    "doc-gateway": gen_doc_gateway,
    "vault-storage": gen_vault_storage,
    "access-control": gen_access_control,
    "sync-engine": gen_sync_engine,
    "audit-service": gen_audit_service,
    "drm-engine": gen_drm_engine,
    "policy-engine": gen_policy_engine,
    "search-indexer": gen_search_indexer,
    "notification-svc": gen_notification_svc,
    "admin-console": gen_admin_console,
}

# ============================================================================
# Log Level Weights (realistic distribution)
# ============================================================================

LEVEL_WEIGHTS = {
    "DEBUG": 15,
    "INFO": 50,
    "WARN": 20,
    "ERROR": 12,
    "FATAL": 3,
}

# Service weights (some services generate more logs)
SERVICE_WEIGHTS = {
    "doc-gateway": 25,
    "vault-storage": 15,
    "access-control": 20,
    "sync-engine": 10,
    "audit-service": 10,
    "drm-engine": 5,
    "policy-engine": 5,
    "search-indexer": 5,
    "notification-svc": 3,
    "admin-console": 2,
}

# ============================================================================
# Log Generation
# ============================================================================

def weighted_choice(options_weights: Dict[str, int]) -> str:
    items = list(options_weights.keys())
    weights = list(options_weights.values())
    return random.choices(items, weights=weights, k=1)[0]


def generate_log_entry(timestamp: datetime) -> Dict[str, Any]:
    level = weighted_choice(LEVEL_WEIGHTS)
    service = weighted_choice(SERVICE_WEIGHTS)
    user = random.choice(USERS)
    host = random.choice(HOSTS)
    department = random.choice(DEPARTMENTS)

    generator = SERVICE_GENERATORS[service]
    message = generator(level, user)

    log_entry = {
        "@timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(0,999):03d}Z",
        "level": level,
        "service": service,
        "message": message,
        "host": host,
        "environment": "production",
        "user": user,
        "department": department,
        "request_id": f"req-{random.randbytes(6).hex()}",
        "duration_ms": random.randint(1, 200) if level in ["DEBUG", "INFO"] else random.randint(100, 5000),
        "client_ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
    }

    if level in ["ERROR", "FATAL"]:
        log_entry["error_code"] = f"VLT-{random.randint(1000,9999)}"
        log_entry["stack_trace"] = f"at {service.replace('-','.')}.handler.process() -> {service.replace('-','.')}.core.execute()"
        log_entry["status_code"] = random.choice([400, 401, 403, 404, 500, 502, 503])
    elif level == "WARN":
        log_entry["status_code"] = random.choice([200, 202, 207, 400, 429])
    else:
        log_entry["status_code"] = random.choice([200, 201, 202, 204])

    return log_entry


def generate_logs(count: int, time_range_hours: int) -> List[Dict[str, Any]]:
    logs = []
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=time_range_hours)

    # Create realistic traffic patterns (more logs during business hours)
    for _ in range(count):
        random_offset = random.uniform(0, time_range_hours * 3600)
        timestamp = start_time + timedelta(seconds=random_offset)

        # Weight towards business hours (9 AM - 6 PM UTC)
        hour = timestamp.hour
        if 9 <= hour <= 18:
            # Business hours - keep this log
            logs.append(generate_log_entry(timestamp))
        elif random.random() < 0.3:
            # Off-hours - 30% chance to keep (background jobs, sync, etc.)
            logs.append(generate_log_entry(timestamp))
        else:
            # Generate another log during business hours instead
            biz_hour = random.randint(9, 18)
            timestamp = timestamp.replace(hour=biz_hour, minute=random.randint(0, 59))
            logs.append(generate_log_entry(timestamp))

    logs.sort(key=lambda x: x["@timestamp"])
    return logs


# ============================================================================
# OpenSearch Indexing
# ============================================================================

def create_index(index_name: str):
    response = requests.head(f"{OPENSEARCH_URL}/{index_name}")
    if response.status_code == 404:
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}},
                    "host": {"type": "keyword"},
                    "environment": {"type": "keyword"},
                    "user": {"type": "keyword"},
                    "department": {"type": "keyword"},
                    "request_id": {"type": "keyword"},
                    "duration_ms": {"type": "integer"},
                    "status_code": {"type": "integer"},
                    "client_ip": {"type": "ip"},
                    "error_code": {"type": "keyword"},
                    "stack_trace": {"type": "text"},
                }
            }
        }
        resp = requests.put(f"{OPENSEARCH_URL}/{index_name}", json=mapping,
                          headers={"Content-Type": "application/json"})
        if resp.status_code in [200, 201]:
            print(f"  [OK] Created index: {index_name}")
        else:
            print(f"  [ERROR] Failed to create index {index_name}: {resp.text}")
            sys.exit(1)
    else:
        print(f"  [OK] Index exists: {index_name}")


def index_logs(logs: List[Dict[str, Any]], index_name: str):
    bulk_body = []
    for log in logs:
        bulk_body.append(json.dumps({"index": {"_index": index_name}}))
        bulk_body.append(json.dumps(log))

    bulk_data = "\n".join(bulk_body) + "\n"

    response = requests.post(
        f"{OPENSEARCH_URL}/_bulk",
        data=bulk_data,
        headers={"Content-Type": "application/x-ndjson"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("errors"):
            error_count = sum(1 for item in result["items"] if "error" in item.get("index", {}))
            print(f"  [WARN] {error_count} errors out of {len(logs)} documents")
        else:
            print(f"  [OK] Indexed {len(logs)} documents")
    else:
        print(f"  [ERROR] Bulk indexing failed: {response.text}")
        sys.exit(1)


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("Vaultize Document Management - Log Generator")
    print("=" * 70)
    print()
    print(f"  OpenSearch:  {OPENSEARCH_URL}")
    print(f"  Total logs:  {NUM_LOGS}")
    print(f"  Time range:  Last {TIME_RANGE_HOURS} hours ({TIME_RANGE_HOURS // 24} days)")
    print(f"  Services:    {len(SERVICES)}")
    print(f"  Users:       {len(USERS)}")
    print()

    # Check connection
    try:
        resp = requests.get(OPENSEARCH_URL)
        info = resp.json()
        print(f"  [OK] Connected to OpenSearch {info['version']['number']}")
    except Exception as e:
        print(f"  [ERROR] Cannot connect: {e}")
        sys.exit(1)

    print()

    # Generate logs
    print("Generating logs...")
    logs = generate_logs(NUM_LOGS, TIME_RANGE_HOURS)

    # Group by date for multi-day indexing
    logs_by_date: Dict[str, List[Dict[str, Any]]] = {}
    for log in logs:
        date = log["@timestamp"][:10]
        logs_by_date.setdefault(date, []).append(log)

    print(f"  Generated {len(logs)} logs across {len(logs_by_date)} days")
    print()

    # Index per day
    print("Indexing into OpenSearch...")
    for date, day_logs in sorted(logs_by_date.items()):
        index_name = f"{INDEX_PREFIX}-{date}"
        create_index(index_name)
        index_logs(day_logs, index_name)

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()

    print("Log Level Distribution:")
    for level in ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]:
        count = sum(1 for log in logs if log["level"] == level)
        pct = count / len(logs) * 100
        bar = "#" * int(pct / 2)
        print(f"  {level:6s}  {count:5d} ({pct:5.1f}%)  {bar}")

    print()
    print("Service Distribution:")
    svc_counts = {}
    for log in logs:
        svc_counts[log["service"]] = svc_counts.get(log["service"], 0) + 1
    for svc, count in sorted(svc_counts.items(), key=lambda x: -x[1]):
        pct = count / len(logs) * 100
        print(f"  {svc:20s}  {count:5d} ({pct:5.1f}%)")

    print()
    print("Department Distribution:")
    dept_counts = {}
    for log in logs:
        dept_counts[log["department"]] = dept_counts.get(log["department"], 0) + 1
    for dept, count in sorted(dept_counts.items(), key=lambda x: -x[1]):
        print(f"  {dept:15s}  {count:5d}")

    print()
    error_count = sum(1 for log in logs if log["level"] in ["ERROR", "FATAL"])
    print(f"  Total errors/fatals: {error_count}")
    print(f"  Error rate: {error_count / len(logs) * 100:.1f}%")

    print()
    print("Dashboards:")
    print("  OpenSearch Dashboards:  http://localhost:5601")
    print("  Grafana Log Analytics:  http://localhost:3100/d/vaultize-log-analytics")
    print("  Grafana Platform Health: http://localhost:3100/d/vaultize-platform-health")
    print("  Analytics API:          http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
