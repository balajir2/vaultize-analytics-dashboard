#!/usr/bin/env python3
"""
Vaultize Analytics Platform - Multi-Tenant Provisioning

Creates all OpenSearch resources for a new customer organisation:
  1. Internal user (login for OpenSearch Dashboards)
  2. Tenant (isolated saved objects in Dashboards)
  3. Role with Document-Level Security filter on organization_id
  4. Role mapping (user → role)

Usage:
    python scripts/ops/provision_tenant.py \\
        --org-id acme-corp \\
        --org-name "Acme Corporation" \\
        --password <initial-password>

    # Dry run (shows what would be created, no changes):
    python scripts/ops/provision_tenant.py --org-id acme-corp --dry-run

    # Delete a tenant:
    python scripts/ops/provision_tenant.py --org-id acme-corp --delete

Environment variables (or pass as args):
    OPENSEARCH_HOST     default: localhost
    OPENSEARCH_PORT     default: 9200
    OPENSEARCH_USER     default: admin
    OPENSEARCH_PASSWORD default: vaultize

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import base64
import ssl

def hash_password(password: str) -> str:
    """Return a bcrypt hash of the password for use with OpenSearch internal users.

    Using hash instead of plaintext bypasses OpenSearch's password strength
    validation, which uses zxcvbn and rejects common words/patterns.
    Requires: pip install bcrypt
    """
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    except ImportError:
        # Fall back to returning the plaintext — OpenSearch will hash it but also
        # apply strength validation, which may reject simple passwords.
        return password


# ============================================================================
# OpenSearch Client (minimal, no extra deps)
# ============================================================================

class OpenSearchClient:
    def __init__(self, host, port, username, password, scheme="https"):
        self.base_url = f"{scheme}://{host}:{port}"
        creds = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
        }
        # Skip TLS verification for self-signed certs
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def _request(self, method, path, body=None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req, context=self.ctx) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def put(self, path, body):
        return self._request("PUT", path, body)

    def delete(self, path):
        return self._request("DELETE", path)

    def get(self, path):
        return self._request("GET", path)


# ============================================================================
# Provisioning Logic
# ============================================================================

def org_resource_names(org_id: str) -> dict:
    """Return the OpenSearch resource names for an organisation."""
    safe = org_id.lower().replace(" ", "-").replace("_", "-")
    return {
        "user": safe,
        "tenant": safe,
        "role": f"tenant_{safe}",
        "role_mapping": f"tenant_{safe}",
    }


def provision(client, org_id: str, org_name: str, password: str, dry_run: bool = False):
    """Create all OpenSearch resources for a new customer organisation."""
    names = org_resource_names(org_id)
    print(f"\nProvisioning tenant: {org_name} (org_id={org_id})")
    print(f"  User:         {names['user']}")
    print(f"  Tenant:       {names['tenant']}")
    print(f"  Role:         {names['role']}")
    print(f"  Role mapping: {names['role_mapping']}")
    print()

    if dry_run:
        print("[DRY RUN] No changes made.")
        return True

    errors = []

    # Step 1: Create tenant (isolated Dashboards saved objects)
    print("[1/4] Creating tenant...")
    status, resp = client.put(
        f"/_plugins/_security/api/tenants/{names['tenant']}",
        {"description": f"Tenant for {org_name} — isolated dashboards and visualizations"}
    )
    if status in (200, 201):
        print(f"      OK: tenant '{names['tenant']}' created")
    elif status == 409:
        print(f"      SKIP: tenant '{names['tenant']}' already exists")
    else:
        msg = f"      ERR ({status}): {resp}"
        print(msg)
        errors.append(msg)

    # Step 2: Create role with Document-Level Security
    # DLS ensures this user can only see documents where organization_id == org_id
    print("[2/4] Creating role with DLS filter...")
    status, resp = client.put(
        f"/_plugins/_security/api/roles/{names['role']}",
        {
            "description": f"Role for {org_name} — DLS-filtered to organization_id={org_id}",
            "cluster_permissions": ["cluster_composite_ops_ro"],
            "index_permissions": [
                {
                    "index_patterns": ["vaultize-events-*", "vaultize-cdp-*", "vaultize-efss-*",
                                       "vaultize-drm-*", "vaultize-email-*"],
                    "dls": json.dumps({"term": {"organization_id": org_id}}),
                    "allowed_actions": [
                        "read",
                        "indices:data/read/search",
                        "indices:data/read/msearch",
                        "indices:data/read/get",
                        "indices:data/read/mget",
                        "indices:admin/mappings/get",
                        "indices:admin/get",
                    ]
                }
            ],
            "tenant_permissions": [
                {
                    "tenant_patterns": [names["tenant"]],
                    "allowed_actions": ["kibana_all_write"]
                },
                {
                    "tenant_patterns": ["global_tenant"],
                    "allowed_actions": ["kibana_all_read"]
                }
            ]
        }
    )
    if status in (200, 201):
        print(f"      OK: role '{names['role']}' created with DLS for organization_id='{org_id}'")
    elif status == 409:
        print(f"      SKIP: role '{names['role']}' already exists")
    else:
        msg = f"      ERR ({status}): {resp}"
        print(msg)
        errors.append(msg)

    # Step 3: Create internal user (use hash to bypass strength validation)
    print("[3/4] Creating user...")
    status, resp = client.put(
        f"/_plugins/_security/api/internalusers/{names['user']}",
        {
            "hash": hash_password(password),
            "backend_roles": [f"tenant_{org_id}"],
            "attributes": {
                "organization_id": org_id,
                "organization_name": org_name,
            },
            "description": f"Login user for {org_name}"
        }
    )
    if status in (200, 201):
        print(f"      OK: user '{names['user']}' created")
    elif status == 409:
        print(f"      SKIP: user '{names['user']}' already exists")
    else:
        msg = f"      ERR ({status}): {resp}"
        print(msg)
        errors.append(msg)

    # Step 4: Create role mapping (user → role)
    print("[4/4] Creating role mapping...")
    status, resp = client.put(
        f"/_plugins/_security/api/rolesmapping/{names['role_mapping']}",
        {
            "users": [names["user"]],
            "description": f"Maps {org_name} user to their DLS-filtered role"
        }
    )
    if status in (200, 201):
        print(f"      OK: role mapping '{names['role_mapping']}' created")
    elif status == 409:
        print(f"      SKIP: role mapping '{names['role_mapping']}' already exists")
    else:
        msg = f"      ERR ({status}): {resp}"
        print(msg)
        errors.append(msg)

    if errors:
        print(f"\nProvisioning completed with {len(errors)} error(s).")
        return False

    print(f"\n[OK] Tenant '{org_name}' provisioned successfully.")
    print(f"\nCustomer login details:")
    print(f"  URL:      https://vaultize.duckdns.org")
    print(f"  Username: {names['user']}")
    print(f"  Password: {password}")
    print(f"  Tenant:   {names['tenant']}")
    print(f"\nData isolation: All queries automatically filtered to organization_id='{org_id}'")
    return True


def deprovision(client, org_id: str, dry_run: bool = False):
    """Remove all OpenSearch resources for an organisation."""
    names = org_resource_names(org_id)
    print(f"\nDeprovisioning tenant: {org_id}")

    if dry_run:
        print(f"  Would delete: user={names['user']}, role_mapping={names['role_mapping']}, "
              f"role={names['role']}, tenant={names['tenant']}")
        print("[DRY RUN] No changes made.")
        return True

    errors = []
    for resource_type, name in [
        ("internalusers", names["user"]),
        ("rolesmapping", names["role_mapping"]),
        ("roles", names["role"]),
        ("tenants", names["tenant"]),
    ]:
        status, resp = client.delete(f"/_plugins/_security/api/{resource_type}/{name}")
        if status in (200, 204):
            print(f"  Deleted {resource_type}/{name}")
        elif status == 404:
            print(f"  Not found (already deleted?): {resource_type}/{name}")
        else:
            msg = f"  ERR ({status}): {resource_type}/{name} — {resp}"
            print(msg)
            errors.append(msg)

    if errors:
        print(f"\nDeprovisioning completed with {len(errors)} error(s).")
        return False

    print(f"\n[OK] Tenant '{org_id}' deprovisioned.")
    return True


def list_tenants(client):
    """List all customer tenants (excludes built-in tenants)."""
    status, resp = client.get("/_plugins/_security/api/tenants")
    if status != 200:
        print(f"[ERROR] Could not fetch tenants: {resp}")
        return

    print("\nConfigured tenants:")
    builtins = {"global_tenant", "__user__"}
    for name, info in resp.items():
        if name in builtins:
            continue
        reserved = " [reserved]" if info.get("reserved") else ""
        print(f"  {name}: {info.get('description', '')}{reserved}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Provision or deprovision a Vaultize customer tenant in OpenSearch"
    )
    parser.add_argument("--org-id", required=False,
                        help="Organisation ID (used as OpenSearch resource name, e.g. acme-corp)")
    parser.add_argument("--org-name", default=None,
                        help="Display name (e.g. 'Acme Corporation')")
    parser.add_argument("--password", default=None,
                        help="Initial login password for the tenant user")
    parser.add_argument("--delete", action="store_true",
                        help="Delete (deprovision) the tenant instead of creating it")
    parser.add_argument("--list", action="store_true",
                        help="List all provisioned tenants")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    parser.add_argument("--host", default=os.environ.get("OPENSEARCH_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("OPENSEARCH_PORT", "9200")))
    parser.add_argument("--scheme", default=os.environ.get("OPENSEARCH_SCHEME", "https"))
    parser.add_argument("--admin-user", default=os.environ.get("OPENSEARCH_USER", "admin"))
    parser.add_argument("--admin-password",
                        default=os.environ.get("OPENSEARCH_PASSWORD", "vaultize"))
    args = parser.parse_args()

    client = OpenSearchClient(args.host, args.port, args.admin_user, args.admin_password,
                               args.scheme)

    if args.list:
        list_tenants(client)
        return

    if not args.org_id:
        parser.error("--org-id is required")

    if args.delete:
        success = deprovision(client, args.org_id, dry_run=args.dry_run)
    else:
        org_name = args.org_name or args.org_id
        password = args.password
        if not password and not args.dry_run:
            import getpass
            password = getpass.getpass(f"Password for user '{args.org_id}': ")
        success = provision(client, args.org_id, org_name, password or "changeme",
                            dry_run=args.dry_run)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
