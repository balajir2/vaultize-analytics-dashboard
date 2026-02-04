#!/bin/bash
#
# Import Dashboards Script
#
# Automatically imports saved objects (index patterns, visualizations, dashboards)
# into OpenSearch Dashboards.
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0

set -e

# Configuration
DASHBOARDS_URL="${DASHBOARDS_URL:-http://localhost:5601}"
SAVED_OBJECTS_DIR="$(dirname "$0")/saved-objects"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "OpenSearch Dashboards Import Script"
echo "=========================================="
echo ""
echo "Dashboards URL: $DASHBOARDS_URL"
echo "Saved Objects Directory: $SAVED_OBJECTS_DIR"
echo ""

# Check if OpenSearch Dashboards is running
echo -n "Checking OpenSearch Dashboards connectivity... "
if curl -s -f "$DASHBOARDS_URL/api/status" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Error: Cannot connect to OpenSearch Dashboards at $DASHBOARDS_URL"
    echo "Make sure OpenSearch Dashboards is running:"
    echo "  docker compose up -d opensearch-dashboards"
    exit 1
fi

echo ""

# Function to import saved objects
import_saved_objects() {
    local file=$1
    local name=$(basename "$file" .ndjson)

    echo -n "Importing $name... "

    response=$(curl -s -w "\n%{http_code}" -X POST "$DASHBOARDS_URL/api/saved_objects/_import?overwrite=true" \
        -H "osd-xsrf: true" \
        -H "Content-Type: multipart/form-data" \
        --form file=@"$file" 2>&1)

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}SUCCESS${NC}"

        # Parse and display counts
        success_count=$(echo "$body" | grep -o '"success":true' | wc -l)
        if [ $success_count -gt 0 ]; then
            echo "  └─ Imported $success_count objects"
        fi
    else
        echo -e "${RED}FAILED${NC} (HTTP $http_code)"
        echo "  └─ Response: $body"
    fi
}

# Import in correct order (dependencies first)
echo "Importing saved objects..."
echo ""

if [ -f "$SAVED_OBJECTS_DIR/index-pattern.ndjson" ]; then
    import_saved_objects "$SAVED_OBJECTS_DIR/index-pattern.ndjson"
fi

if [ -f "$SAVED_OBJECTS_DIR/visualizations.ndjson" ]; then
    import_saved_objects "$SAVED_OBJECTS_DIR/visualizations.ndjson"
fi

if [ -f "$SAVED_OBJECTS_DIR/dashboards.ndjson" ]; then
    import_saved_objects "$SAVED_OBJECTS_DIR/dashboards.ndjson"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Import Complete!${NC}"
echo "=========================================="
echo ""
echo "Access your dashboards at:"
echo "  $DASHBOARDS_URL/app/dashboards"
echo ""
echo "Available dashboards:"
echo "  - Operations Dashboard (real-time monitoring)"
echo "  - Analytics Dashboard (historical analysis)"
echo ""
