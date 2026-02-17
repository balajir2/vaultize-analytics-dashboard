# Vaultize Analytics - Manual Testing Guide

**Last Updated**: 2026-02-17
**Authors**: Balaji Rajan and Claude (Anthropic)
**License**: Apache 2.0
**System Status**: Fully Operational

---

## Quick Start

### 1. Start All Services

```bash
cd "d:\GitHub\Vaultize Analytics Dashboard"
docker compose up -d
docker compose ps  # Verify all services are "Up (healthy)"
```

---

## Test 1: OpenSearch Dashboards (5-10 minutes)

**URL**: http://localhost:5601

### Step 1: Create Index Pattern

**IMPORTANT**: We need "Index Patterns" (NOT "Index Management" - that's different!)

**Correct Navigation**:
1. Open http://localhost:5601
2. Click the **hamburger menu** at top left
3. Scroll down to **"Management"** section (with gear icon)
4. Click **"Dashboards Management"**
5. Click **"Index Patterns"**
6. Click **"Create index pattern"** button
7. Enter index pattern: `logs-*`
8. Click "Next step" button
9. Select time field: `@timestamp`
10. Click "Create index pattern"

**Note**: Don't click "Index Management" - that's for ISM policies, not for viewing logs!

### Step 2: Discover Your Logs

**Navigate to Discover:**
- **Option 1**: Direct URL: http://localhost:5601/app/discover
- **Option 2**: Look in hamburger menu for "Discover" (may be under "OpenSearch Dashboards" or "Observability" section)

**Once in Discover:**
1. You should see 1,000+ sample logs!
2. **Try these filters**:
   - Click on `level` field → Select "ERROR" (see only errors)
   - Click on `service` field → Select "api-service"
   - Change time range (top right) to "Last 7 days"

### Step 3: Search Examples
Try these in the search bar (top of page):

```
level:ERROR
service:api-service
level:ERROR AND service:web-service
message:timeout
status_code:500
```

### Step 4: Quick Visualization
1. Click "Visualize" in left menu
2. Click "Create visualization"
3. Select "Pie" chart
4. Choose your `logs-*` index pattern
5. Aggregation: Count
6. Click "Add" under "Buckets"
7. Select "Terms"
8. Field: `level.keyword`
9. Click "Update" button
10. See your log level distribution!

**Expected Result**: Beautiful pie chart showing DEBUG, INFO, WARN, ERROR, FATAL distribution

---

## Test 2: Analytics API (10-15 minutes)

**URL**: http://localhost:8000/docs (Interactive Swagger UI)

### Test 2.1: Health Check
1. Open http://localhost:8000/docs
2. Find `GET /health/` endpoint (should be first)
3. Click "Try it out"
4. Click "Execute"

**Expected**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "opensearch": {
    "status": "green",
    "cluster_name": "vaultize-opensearch-cluster"
  }
}
```

### Test 2.2: Simple Search
1. Find `GET /api/v1/search/simple`
2. Click "Try it out"
3. Parameters:
   - `q`: `level:ERROR`
   - `size`: `10`
4. Click "Execute"

**Expected**: Returns 10 error logs with pagination info

### Test 2.3: Advanced Search with Time Range
1. Find `POST /api/v1/search`
2. Click "Try it out"
3. Paste this request body:

```json
{
  "query": "service:api-service AND level:ERROR",
  "time_range": {
    "field": "@timestamp",
    "start": "now-24h",
    "end": "now"
  },
  "size": 20
}
```

4. Click "Execute"

**Expected**: Returns up to 20 errors from api-service in last 24 hours

### Test 2.4: Top Services with Errors (Aggregation)
1. Find `POST /api/v1/aggregate`
2. Click "Try it out"
3. Paste this:

```json
{
  "query": "level:ERROR",
  "indices": ["logs-*"],
  "agg_type": "terms",
  "field": "service",
  "size": 5
}
```

4. Click "Execute"

**Expected**: Shows which 5 services have the most errors

### Test 2.5: Error Trends Over Time
1. Find `POST /api/v1/aggregate`
2. Use this request:

```json
{
  "query": "level:ERROR",
  "agg_type": "date_histogram",
  "field": "@timestamp",
  "interval": "1h"
}
```

**Expected**: Returns error count per hour (time series data)

### Test 2.6: Top Values Shortcut
1. Find `GET /api/v1/top-values/{field}`
2. Click "Try it out"
3. Parameters:
   - `field`: `level`
   - `size`: `5`
4. Click "Execute"

**Expected**: Shows distribution of all log levels

### Test 2.7: Index Statistics
1. Find `GET /api/v1/indices/`
2. Click "Try it out"
3. Parameters:
   - `pattern`: `logs-*`
4. Click "Execute"

**Expected**: Lists all log indices with document counts and sizes

---

## Test 3: Grafana (5 minutes)

**URL**: http://localhost:3100
**Login**: `admin` / `admin` (change password when prompted)

### Steps:
1. Open http://localhost:3100
2. Login with admin/admin
3. Set new password (or skip)
4. You'll see Grafana welcome screen

**Expected**: Grafana loads successfully and you can login

**Note**: Grafana is running but dashboards are not pre-configured. This is for future metrics visualization (optional M4 feature). For log analytics, use OpenSearch Dashboards instead.

---

## Test 4: M4 Dashboards (Pre-built Analytics Dashboards)

**Goal**: Import and test the pre-built Operations and Analytics dashboards

### Step 1: Import Dashboards Automatically

**Windows (PowerShell)**:
```powershell
cd "d:\GitHub\Vaultize Analytics Dashboard\dashboards\opensearch-dashboards"
.\import_dashboards.ps1
```

**Expected Output**:
```
==========================================
OpenSearch Dashboards Import Script
==========================================
Checking OpenSearch Dashboards connectivity... OK

Importing index-pattern... SUCCESS
Importing visualizations... SUCCESS
Importing dashboards... SUCCESS

Import Complete!
```

### Step 2: Access Operations Dashboard

**URL**: http://localhost:5601/app/dashboards

1. Navigate to Dashboards (hamburger menu → Dashboard)
2. Click **"Operations Dashboard"**

**What You Should See**:
- **Log Volume Over Time**: Line chart showing log activity
- **Log Level Distribution**: Pie chart (DEBUG, INFO, WARN, ERROR, FATAL)
- **Top Services**: Bar chart of most active services
- **Error Rate by Service**: Multi-line chart tracking errors
- **Recent Critical Events**: Table of recent ERROR/FATAL logs

**Dashboard Features**:
- Auto-refresh: Every 30 seconds
- Time range: Last 24 hours (adjustable)
- Click on charts to filter data
- Use search bar to query logs

### Step 3: Access Analytics Dashboard

**URL**: http://localhost:5601/app/dashboards

1. From Dashboards list, click **"Analytics Dashboard"**

**What You Should See**:
- **Full-width Log Volume Timeline**: Historical log activity
- **Log Level Breakdown**: Severity distribution
- **Service Activity Analysis**: Which services log most
- **Top Error Messages**: Table of common errors by service
- **Service Error Trends**: Comparison of error rates

**Dashboard Features**:
- Manual refresh (for investigation)
- Time range: Last 7 days (adjustable)
- Drill-down by clicking visualizations
- Export/share capabilities

### Step 4: Test Dashboard Interactions

**Try these interactions**:

1. **Filter by clicking**:
   - Click on "ERROR" slice in pie chart
   - Notice all panels now show only errors
   - Clear filter by clicking the "x" on the filter pill

2. **Adjust time range**:
   - Click time picker (top right)
   - Select "Last 15 minutes"
   - Notice data updates across all panels

3. **Search within dashboard**:
   - Use search bar: `service:api-service`
   - See data filtered to only api-service

4. **View panel details**:
   - Hover over any chart
   - Click the expand icon to see full-screen
   - Click inspect to see raw data

### Step 5: Verify All Visualizations Work

**Check each visualization loads**:
- [ ] Log Volume Over Time (line chart)
- [ ] Log Level Distribution (pie chart)
- [ ] Top Services (bar chart)
- [ ] Error Rate by Service (multi-line chart)
- [ ] Recent Critical Events (data table)
- [ ] Top Error Messages (data table)

**Success Criteria**:
- Both dashboards load without errors
- All visualizations display data
- Filters and time range selectors work
- Can drill down into data
- Charts are interactive (hover, click)

### Troubleshooting M4 Dashboards

**Dashboard shows "No data"**:
- Check index pattern exists: `logs-*`
- Verify time range includes your sample data
- Confirm logs are indexed: http://localhost:9200/logs-*/_count

**Import script failed**:
- Verify OpenSearch Dashboards is running: http://localhost:5601
- Check logs: `docker compose logs opensearch-dashboards`
- Try manual import via UI (Management → Saved Objects → Import)

**Visualizations not loading**:
- Refresh browser (Ctrl+F5)
- Check browser console (F12) for errors
- Verify all services healthy: `docker compose ps`

---

## Test 5: Command Line (Optional - For Tech Users)

### Health Check
```bash
curl http://localhost:8000/health/ | jq
```

### Search for Errors
```bash
curl "http://localhost:8000/api/v1/search/simple?q=level:ERROR&size=5" | jq .data.total
```

### Count Total Logs
```bash
curl "http://localhost:8000/api/v1/search/simple?q=*&size=1" | jq .data.total
```

### Top Services with Errors
```bash
curl -X POST http://localhost:8000/api/v1/aggregate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "level:ERROR",
    "agg_type": "terms",
    "field": "service",
    "size": 5
  }' | jq .data.buckets
```

### Direct OpenSearch Query
```bash
# Cluster health
curl http://localhost:9200/_cluster/health?pretty

# List indices
curl http://localhost:9200/_cat/indices?v

# Count logs
curl http://localhost:9200/logs-*/_count?pretty
```

---

## Fun Test Scenarios

### Scenario 1: "Find Critical Issues"
**Goal**: Find all ERROR and FATAL logs in last 24 hours

**In Dashboards**:
- Search: `level:ERROR OR level:FATAL`
- Time: Last 24 hours

**Via API**:
```json
POST /api/v1/search
{
  "query": "level:ERROR OR level:FATAL",
  "time_range": {
    "start": "now-24h",
    "end": "now"
  },
  "size": 50
}
```

### Scenario 2: "Which Service is Down?"
**Goal**: Find service with most errors

**Via API**:
```json
POST /api/v1/aggregate
{
  "query": "level:ERROR OR level:FATAL",
  "agg_type": "terms",
  "field": "service",
  "size": 10
}
```

### Scenario 3: "Database Issues"
**Goal**: Find database-related errors

**In Dashboards**: Search `service:db-service AND level:ERROR`

**Via API**: Use simple search with query `service:db-service AND level:ERROR`

---

## Test 6: Alerting Service (5-10 minutes)

**URL**: http://localhost:8001/docs (Interactive Swagger UI)

### Test 6.1: Health Check
1. Open http://localhost:8001/docs
2. Find `GET /health/` endpoint
3. Click "Try it out" → "Execute"

**Expected**: Status "healthy" with OpenSearch connected and scheduler running

### Test 6.2: List Alert Rules
1. Find `GET /api/v1/alerts/rules`
2. Click "Try it out" → "Execute"

**Expected**: Returns list of loaded alert rules (high-error-rate, slow-api-response)

### Test 6.3: Rule Status
1. Find `GET /api/v1/alerts/rules/{name}/status`
2. Enter rule name: `high-error-rate`
3. Click "Execute"

**Expected**: Returns current state (OK/FIRING), last check time, threshold config

### Test 6.4: Manual Trigger
1. Find `POST /api/v1/alerts/rules/{name}/trigger`
2. Enter rule name: `high-error-rate`
3. Click "Execute"

**Expected**: Returns evaluation result with current metric value vs threshold

---

## Test 7: Security Mode (Advanced)

**Goal**: Test TLS and authentication (opt-in)

### Start in Secure Mode
```bash
bash scripts/ops/start_secure.sh
bash scripts/ops/initialize_security.sh
```

### Test JWT Auth
```bash
# Get token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=<your-password>"

# Use token
curl http://localhost:8000/api/v1/search/simple?q=* \
  -H "Authorization: Bearer <token>"
```

### Test Rate Limiting
```bash
# Rapid requests (should get 429 after limit)
for i in $(seq 1 100); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health/; done
```

---

## Test 8: Grafana Dashboards (5 minutes)

**URL**: http://localhost:3100
**Login**: `admin` / `admin`

### Steps:
1. Login to Grafana
2. Navigate to Dashboards
3. Open **"Vaultize Platform Health"** dashboard

**What You Should See (14 panels)**:
- Total Services, Active Alerts, Error Rate, Uptime stats
- Service Health Status, Fluent Bit metrics
- OpenSearch log viewer with log levels

**Note**: Datasources (OpenSearch + Prometheus) are auto-provisioned.

---

## Testing Checklist

- [ ] All Docker containers running (`docker compose ps`)
- [ ] OpenSearch Dashboards loads (http://localhost:5601)
- [ ] Created index pattern `logs-*`
- [ ] Can see 1,000+ logs in Discover
- [ ] Can filter by log level (ERROR)
- [ ] Can search for specific service
- [ ] Analytics API Swagger UI loads (http://localhost:8000/docs)
- [ ] Health endpoint returns green status
- [ ] Simple search returns results
- [ ] Aggregation shows service distribution
- [ ] Alerting service loads (http://localhost:8001/docs)
- [ ] Alert rules are loaded and evaluating
- [ ] Grafana loads (http://localhost:3100)
- [ ] Can login to Grafana
- [ ] Platform Health dashboard available

---

## Troubleshooting

### Services Not Running?
```bash
docker compose up -d
docker compose logs analytics-api
docker compose logs opensearch-node1
```

### No Logs Visible?
```bash
# Regenerate sample data
cd scripts/data
python generate_sample_logs.py
```

### Port Already in Use?
```bash
# Check ports
netstat -ano | findstr :8000
netstat -ano | findstr :9200
netstat -ano | findstr :5601

# Stop conflicting service or change ports in .env file
```

### Container Unhealthy?
```bash
# Check logs
docker compose logs <service-name>

# Restart specific service
docker compose restart analytics-api
```

---

## What Success Looks Like

### OpenSearch Dashboards
- See logs with fields: timestamp, level, service, message, host
- Can filter by log level
- Time range selector works
- Visualizations render correctly

### Analytics API
- All 14 endpoints respond
- Health status is "green"
- Search returns results with pagination
- Aggregations show buckets with counts
- Response time < 100ms for most queries

### Overall System
- All services healthy
- Can query logs multiple ways
- Data is searchable and filterable
- API documentation is clear and interactive

---

## Key Endpoints Reference

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health/` | GET | API health status | - |
| `/api/v1/search/simple` | GET | Quick search | `?q=level:ERROR&size=10` |
| `/api/v1/search` | POST | Advanced search | With time range, fields |
| `/api/v1/aggregate` | POST | Analytics aggregations | terms, date_histogram |
| `/api/v1/top-values/{field}` | GET | Top values for field | `level`, `service` |
| `/api/v1/indices/` | GET | List indices | `?pattern=logs-*` |

---

## Tips

1. **Start with OpenSearch Dashboards** - Most visual and intuitive
2. **Then try API** - Understand programmatic access
3. **Experiment with searches** - Try different queries
4. **Look at raw data** - Click expand on log entries to see all fields
5. **Check response times** - Note how fast queries execute

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs
- **OpenSearch Docs**: https://opensearch.org/docs/latest/
- **Sample Data**: Generated from `scripts/data/generate_sample_logs.py`

---

## Session Change Log

This section tracks updates to the testing guide after each development session.

| Date | Changes |
|------|---------|
| 2026-02-04 | Initial testing guide created with OpenSearch Dashboards, Analytics API, Grafana, and M4 Dashboard tests |
| 2026-02-10 | M5 Alerting Service implemented. Added `docs/operations/full-platform-test-guide.md` for comprehensive end-to-end manual testing of the entire platform (33 test steps across 6 test areas). Alerting service endpoints: health (8001/health/), rules listing, manual trigger, history, reload. |
| 2026-02-17 | M7 Production Hardening + M6 Testing completion. Added: Test 6 (Alerting Service), Test 7 (Security Mode with TLS/JWT/rate limiting), Test 8 (Grafana dashboards with auto-provisioned datasources). Updated checklist with alerting and Grafana items. New test files: RT-012 through RT-018 (174 regression tests). E2E, integration, and performance test frameworks created. Total regression tests: 238. |

---
