#!/usr/bin/env bash
#
# Vaultize Analytics Platform - First-Time Bootstrap
#
# Sets up the platform for first use:
# 1. Waits for OpenSearch to be ready
# 2. Creates index templates
# 3. Sets up ILM policies
# 4. Generates sample data
# 5. Imports dashboards
#
# Usage: ./bootstrap.sh [--skip-data] [--skip-dashboards]
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL="${OPENSEARCH_URL:-http://localhost:9200}"
DASHBOARDS_URL="${DASHBOARDS_URL:-http://localhost:5601}"
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MAX_RETRIES=30
RETRY_INTERVAL=5

SKIP_DATA=false
SKIP_DASHBOARDS=false

for arg in "$@"; do
    case $arg in
        --skip-data) SKIP_DATA=true ;;
        --skip-dashboards) SKIP_DASHBOARDS=true ;;
    esac
done

# ============================================================================
# Helpers
# ============================================================================

info() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*" >&2; }
error() { echo "[ERROR] $*" >&2; exit 1; }

wait_for_service() {
    local url="$1"
    local name="$2"
    local retries=0

    info "Waiting for $name to be ready..."
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
            info "$name is ready"
            return 0
        fi
        retries=$((retries + 1))
        info "  Attempt $retries/$MAX_RETRIES - retrying in ${RETRY_INTERVAL}s..."
        sleep "$RETRY_INTERVAL"
    done

    error "$name did not become ready after $MAX_RETRIES attempts"
}

# ============================================================================
# Main Bootstrap
# ============================================================================

info "=============================================="
info "Vaultize Analytics Platform - Bootstrap"
info "=============================================="
info ""

# Step 1: Wait for services
wait_for_service "${OPENSEARCH_URL}/_cluster/health" "OpenSearch"

# Step 2: Apply index templates
info ""
info "--- Applying Index Templates ---"
for template_file in "$PROJECT_ROOT"/configs/index-templates/*.json; do
    if [ -f "$template_file" ]; then
        template_name=$(basename "$template_file" .json)
        info "Applying template: $template_name"
        curl -s -X PUT "${OPENSEARCH_URL}/_index_template/${template_name}" \
            -H "Content-Type: application/json" \
            -d @"$template_file" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ', 'OK' if d.get('acknowledged') else d)" 2>/dev/null || true
    fi
done

# Step 3: Apply ILM policies
info ""
info "--- Applying ILM Policies ---"
for policy_file in "$PROJECT_ROOT"/configs/ilm-policies/*.json; do
    if [ -f "$policy_file" ]; then
        policy_name=$(basename "$policy_file" .json)
        info "Applying ILM policy: $policy_name"
        curl -s -X PUT "${OPENSEARCH_URL}/_plugins/_ism/policies/${policy_name}" \
            -H "Content-Type: application/json" \
            -d @"$policy_file" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ', 'OK' if d.get('_id') else d)" 2>/dev/null || true
    fi
done

# Step 4: Generate sample data
if [ "$SKIP_DATA" = false ]; then
    info ""
    info "--- Generating Sample Data ---"
    if [ -f "$PROJECT_ROOT/scripts/data/generate_sample_data.py" ]; then
        python3 "$PROJECT_ROOT/scripts/data/generate_sample_data.py" --count 100 || warn "Sample data generation failed (non-fatal)"
    fi
    if [ -f "$PROJECT_ROOT/scripts/data/generate_sample_log_files.py" ]; then
        python3 "$PROJECT_ROOT/scripts/data/generate_sample_log_files.py" --count 50 || warn "Log file generation failed (non-fatal)"
    fi
else
    info ""
    info "--- Skipping sample data (--skip-data) ---"
fi

# Step 5: Import dashboards
if [ "$SKIP_DASHBOARDS" = false ]; then
    info ""
    info "--- Importing Dashboards ---"
    wait_for_service "${DASHBOARDS_URL}/api/status" "OpenSearch Dashboards"

    SAVED_OBJECTS_DIR="$PROJECT_ROOT/dashboards/opensearch-dashboards/saved-objects"
    if [ -d "$SAVED_OBJECTS_DIR" ]; then
        for ndjson_file in "$SAVED_OBJECTS_DIR"/*.ndjson; do
            if [ -f "$ndjson_file" ]; then
                fname=$(basename "$ndjson_file")
                info "Importing: $fname"
                curl -s -X POST "${DASHBOARDS_URL}/api/saved_objects/_import?overwrite=true" \
                    -H "osd-xsrf: true" \
                    --form file=@"$ndjson_file" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ', f\"success={d.get('success')}, count={d.get('successCount', 0)}\")" 2>/dev/null || true
            fi
        done
    else
        warn "Saved objects directory not found: $SAVED_OBJECTS_DIR"
    fi
else
    info ""
    info "--- Skipping dashboard import (--skip-dashboards) ---"
fi

# Done
info ""
info "=============================================="
info "Bootstrap complete!"
info "=============================================="
info ""
info "Services:"
info "  OpenSearch:           ${OPENSEARCH_URL}"
info "  OpenSearch Dashboards: ${DASHBOARDS_URL}"
info "  Analytics API:        http://localhost:8000"
info "  Alerting Service:     http://localhost:8001"
