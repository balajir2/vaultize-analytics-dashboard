# UI Manual Testing Guide

> Test the entire Vaultize Analytics Platform using only your web browser

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-17
**Prerequisite**: All services must be running. See [Testing Guide](./testing-guide.md) for startup steps.

---

## Service URLs

| Service | URL | Default Login |
|---------|-----|---------------|
| OpenSearch Dashboards | http://localhost:5601 | No auth (dev mode) |
| Analytics API (Swagger) | http://localhost:8000/docs | No auth (dev mode) |
| Alerting Service (Swagger) | http://localhost:8001/docs | No auth (dev mode) |
| Grafana | http://localhost:3100 | admin / admin |
| Prometheus | http://localhost:9090 | No auth |

---

## Test 1: OpenSearch Dashboards

**URL**: http://localhost:5601

### 1.1 Create Index Pattern

1. Open http://localhost:5601
2. Click the **hamburger menu** (three lines, top-left corner)
3. Scroll down to the **Management** section (gear icon)
4. Click **Dashboards Management**
5. Click **Index Patterns** in the left sidebar
6. Click the **Create index pattern** button
7. Type `logs-*` in the "Index pattern name" field
8. Click **Next step**
9. Select `@timestamp` from the "Time field" dropdown
10. Click **Create index pattern**

**Expected**: Index pattern created. You see a list of fields (message, level, service, host, etc.)

### 1.2 Discover Logs

1. Click the **hamburger menu**
2. Click **Discover** (under "OpenSearch Dashboards" section)
3. Make sure `logs-*` is selected as the index pattern (top-left dropdown)
4. Set time range to **Last 7 days** (click the calendar icon, top-right)
5. You should see **1,000+ log entries** displayed

**Try these interactions**:
- Click on any log entry to expand it and see all fields
- In the left sidebar, click **level** field → click "ERROR" to filter
- Click the **X** on the filter pill at the top to clear the filter
- In the left sidebar, click **service** field → click any service name
- Click the time range picker → select "Last 15 minutes" → then "Last 7 days"

### 1.3 Search Queries

Type each of these in the **search bar** at the top and press Enter:

| Query | What it finds |
|-------|---------------|
| `level:ERROR` | All error logs |
| `level:ERROR AND service:api-service` | Errors from api-service only |
| `level:ERROR OR level:FATAL` | All errors and fatal logs |
| `message:"connection timeout"` | Logs with exact phrase |
| `status_code:[400 TO 499]` | Client error status codes |
| `service:api*` | Services starting with "api" |
| `NOT level:DEBUG` | Everything except debug logs |

**Expected**: Each query filters the results. Hit count changes in the top-left.

### 1.4 Create a Visualization

**Pie Chart — Log Level Distribution**:
1. Click the **hamburger menu** → **Visualize**
2. Click **Create visualization**
3. Select **Pie**
4. Choose `logs-*` as the data source
5. Under **Buckets**, click **Add** → select **Split slices**
6. Aggregation: **Terms**
7. Field: `level.keyword`
8. Click the **Update** button (blue play icon)
9. You should see a pie chart with slices for DEBUG, INFO, WARN, ERROR, FATAL
10. Click **Save** → name it "Log Level Distribution" → click **Save**

**Bar Chart — Top Services**:
1. Click **Visualize** → **Create visualization**
2. Select **Vertical bar**
3. Choose `logs-*` as the data source
4. Under **Buckets**, click **Add** → select **X-axis**
5. Aggregation: **Terms**
6. Field: `service.keyword`
7. Size: `10`
8. Click **Update**
9. You should see a bar chart showing the top 10 most active services
10. Click **Save** → name it "Top Services" → click **Save**

### 1.5 Import Pre-Built Dashboards

1. Click the **hamburger menu** → **Dashboards Management**
2. Click **Saved Objects** in the left sidebar
3. Click the **Import** button (top-right)
4. Click **Select a file to import**
5. Navigate to the project folder → `dashboards/opensearch-dashboards/` → select the NDJSON export file
6. Click **Import**
7. If prompted about conflicts, select **Overwrite**

**Expected**: Import succeeds. You see new saved objects listed.

### 1.6 Operations Dashboard

1. Click the **hamburger menu** → **Dashboard**
2. Click **Operations Dashboard** from the list

**Verify these 5 panels load with data**:
- [ ] Log Volume Over Time (line chart)
- [ ] Log Level Distribution (pie chart)
- [ ] Top Services (bar chart)
- [ ] Error Rate by Service (multi-line chart)
- [ ] Recent Critical Events (data table)

**Test interactions**:
- Click on the "ERROR" slice in the pie chart → all panels filter to errors only
- Click the **X** on the filter pill to clear
- Change time range to "Last 15 minutes" → then back to "Last 24 hours"
- Click the expand icon on any panel to view full-screen
- Click the down-arrow on any panel → **Inspect** to see raw data

### 1.7 Analytics Dashboard

1. Go back to Dashboard list (click **Dashboard** in the breadcrumb)
2. Click **Analytics Dashboard**

**Verify these panels load with data**:
- [ ] Full-width Log Volume Timeline
- [ ] Log Level Breakdown
- [ ] Service Activity Analysis
- [ ] Top Error Messages (data table)
- [ ] Service Error Trends

**Test interactions**:
- Use the search bar within the dashboard: type `service:api-service` and press Enter
- All panels should now show only api-service data
- Clear the search to restore all data
- Try the "Last 7 days" time range

---

## Test 2: Analytics API — Swagger UI

**URL**: http://localhost:8000/docs

Open this URL in your browser. You will see an interactive API documentation page. For each test below, find the endpoint, click **Try it out**, fill in the parameters, and click **Execute**.

### 2.1 Health Check

1. Find **GET /health/** (under "Health" section)
2. Click **Try it out** → click **Execute**

**Expected Response** (Status 200):
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "opensearch": {
    "cluster_name": "vaultize-opensearch-cluster",
    "status": "green"
  }
}
```

### 2.2 Cluster Health

1. Find **GET /health/cluster**
2. Click **Try it out** → click **Execute**

**Expected**: Returns detailed OpenSearch cluster info wrapped in `{"status": "success", "data": {...}}`

### 2.3 Readiness and Liveness

1. Find **GET /health/readiness** → Try it out → Execute
   - **Expected**: `{"status": "ready"}`
2. Find **GET /health/liveness** → Try it out → Execute
   - **Expected**: `{"status": "alive"}`

### 2.4 Simple Search

1. Find **GET /api/v1/search/simple**
2. Click **Try it out**
3. Fill in:
   - **q**: `level:ERROR`
   - **indices**: `logs-*`
   - **size**: `10`
4. Click **Execute**

**Expected**: Returns 10 error logs with fields like `_index`, `_id`, `_source` containing message, level, service, etc.

### 2.5 Advanced Search

1. Find **POST /api/v1/search/search**
2. Click **Try it out**
3. Paste this in the request body:

```json
{
  "query": "service:api-service AND level:ERROR",
  "indices": ["logs-*"],
  "time_range": {
    "field": "@timestamp",
    "start": "now-24h",
    "end": "now"
  },
  "size": 20,
  "from_": 0
}
```

4. Click **Execute**

**Expected**: Returns up to 20 error logs from api-service in the last 24 hours, with pagination metadata.

### 2.6 Document Count

1. Find **GET /api/v1/search/count**
2. Click **Try it out**
3. Fill in:
   - **q**: `level:ERROR`
   - **indices**: `logs-*`
4. Click **Execute**

**Expected**: Returns `{"status": "success", "data": {"count": <number>}}`

### 2.7 Aggregation — Top Services with Errors

1. Find **POST /api/v1/aggregate**
2. Click **Try it out**
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

4. Click **Execute**

**Expected**: Returns the 5 services with the most errors, with `doc_count` for each.

### 2.8 Aggregation — Error Trends Over Time

1. Find **POST /api/v1/aggregate**
2. Paste this:

```json
{
  "query": "level:ERROR",
  "indices": ["logs-*"],
  "agg_type": "date_histogram",
  "field": "@timestamp",
  "interval": "1h"
}
```

**Expected**: Returns error count per hour as time-series buckets.

### 2.9 Top Values

1. Find **GET /api/v1/top-values/{field}**
2. Click **Try it out**
3. Enter `level` as the field
4. Click **Execute**

**Expected**: Shows distribution of all log levels (DEBUG, INFO, WARN, ERROR, FATAL) with counts.

### 2.10 Index List

1. Find **GET /api/v1/indices/**
2. Click **Try it out**
3. Set **pattern** to `logs-*`
4. Click **Execute**

**Expected**: Returns a list of all log indices with name, health, status, and document count.

### 2.11 Index Stats

1. Find **GET /api/v1/indices/{name}/stats**
2. Click **Try it out**
3. Enter an index name from the list above (e.g., `logs-2026-02-17`)
4. Click **Execute**

**Expected**: Returns document count, store size, and shard information for that index.

---

## Test 3: Alerting Service — Swagger UI

**URL**: http://localhost:8001/docs

### 3.1 Health Check

1. Find **GET /health/**
2. Click **Try it out** → click **Execute**

**Expected**: Returns status "healthy" with OpenSearch connection status and scheduler status (running).

### 3.2 List Alert Rules

1. Find **GET /api/v1/alerts/rules**
2. Click **Try it out** → click **Execute**

**Expected**: Returns a list of loaded alert rules. You should see at least:
- `high-error-rate` — fires when error count exceeds threshold
- `slow-api-response` — fires when API response time is too high

### 3.3 Rule Status

1. Find **GET /api/v1/alerts/rules/{name}/status**
2. Click **Try it out**
3. Enter `high-error-rate` as the rule name
4. Click **Execute**

**Expected**: Returns current state (OK or FIRING), last check time, threshold configuration, and current metric value.

### 3.4 Manual Trigger

1. Find **POST /api/v1/alerts/rules/{name}/trigger**
2. Click **Try it out**
3. Enter `high-error-rate` as the rule name
4. Click **Execute**

**Expected**: Returns the evaluation result — the current metric value compared against the threshold, and whether the condition is met.

### 3.5 Alert History

1. Find **GET /api/v1/alerts/history**
2. Click **Try it out** → click **Execute**

**Expected**: Returns a list of past alert events (may be empty if no alerts have fired). Each event includes rule name, state change, timestamp, and metric value.

### 3.6 Reload Rules

1. Find **POST /api/v1/alerts/rules/reload**
2. Click **Try it out** → click **Execute**

**Expected**: Returns confirmation that rules were reloaded from disk. Use this after modifying alert rule JSON files.

---

## Test 4: Grafana

**URL**: http://localhost:3100

### 4.1 Login

1. Open http://localhost:3100
2. Enter username: `admin`
3. Enter password: `admin`
4. When prompted, set a new password (or click "Skip")

**Expected**: You see the Grafana home page.

### 4.2 Check Datasources

1. Click the **gear icon** (Configuration) in the left sidebar
2. Click **Data Sources**

**Verify these datasources exist**:
- [ ] **OpenSearch** — connected to the OpenSearch cluster
- [ ] **Prometheus** — connected to the Prometheus server

Click on each one and look for a green "Data source is working" message (or click **Test** button).

### 4.3 Platform Health Dashboard

1. Click the **four-square icon** (Dashboards) in the left sidebar
2. Click **Browse**
3. Open **Vaultize Platform Health** dashboard

**Verify these panels load**:
- [ ] Total Services counter
- [ ] Active Alerts counter
- [ ] Error Rate gauge
- [ ] Uptime stats
- [ ] Service Health Status table
- [ ] Fluent Bit metrics
- [ ] OpenSearch log viewer with log levels

### 4.4 Panel Interactions

- **Hover** over any chart to see tooltip data
- Click a panel title → **View** to see it full-screen
- Click a panel title → **Inspect** → **Data** to see raw data
- Change time range using the picker in the top-right corner
- Click the **refresh icon** to reload all panels

---

## Test 5: Prometheus

**URL**: http://localhost:9090

### 5.1 Check Targets

1. Open http://localhost:9090
2. Click **Status** in the top navigation bar
3. Click **Targets**

**Expected**: You see a list of scrape targets. Each should show state **UP** (green). If any show **DOWN** (red), the corresponding service may not be running.

### 5.2 Run a Query

1. Click **Graph** in the top navigation bar
2. In the query box, type: `up`
3. Click the **Execute** button

**Expected**: A table showing which services are up (value = 1) or down (value = 0).

### 5.3 Graph View

1. With the `up` query still active, click the **Graph** tab (next to Table)
2. You should see a time-series line chart

**Try another query**: Type `process_resident_memory_bytes` and click Execute to see memory usage of monitored services.

---

## Testing Checklist

### OpenSearch Dashboards
- [ ] Page loads at http://localhost:5601
- [ ] Created `logs-*` index pattern
- [ ] Can see 1,000+ logs in Discover
- [ ] Search bar filters results correctly
- [ ] Can filter by clicking field values
- [ ] Created a pie chart visualization
- [ ] Operations Dashboard loads with 5 panels
- [ ] Analytics Dashboard loads with 5 panels
- [ ] Dashboard filter-by-click works
- [ ] Time range picker works across all panels

### Analytics API (Swagger UI)
- [ ] Page loads at http://localhost:8000/docs
- [ ] Health check returns "healthy" with green OpenSearch
- [ ] Cluster health returns detailed cluster info
- [ ] Readiness returns "ready"
- [ ] Liveness returns "alive"
- [ ] Simple search returns log results
- [ ] Advanced search with time range works
- [ ] Document count returns a number
- [ ] Terms aggregation shows service distribution
- [ ] Date histogram shows time-series buckets
- [ ] Top values shows log level distribution
- [ ] Index list returns index names
- [ ] Index stats returns document count and size

### Alerting Service (Swagger UI)
- [ ] Page loads at http://localhost:8001/docs
- [ ] Health check returns "healthy"
- [ ] Rules list shows loaded alert rules
- [ ] Rule status shows current state and threshold
- [ ] Manual trigger returns evaluation result
- [ ] Alert history returns (may be empty if no alerts fired)
- [ ] Rule reload succeeds

### Grafana
- [ ] Page loads at http://localhost:3100
- [ ] Can login with admin/admin
- [ ] OpenSearch datasource is connected
- [ ] Prometheus datasource is connected
- [ ] Platform Health dashboard loads with panels
- [ ] Can interact with panels (hover, expand, inspect)

### Prometheus
- [ ] Page loads at http://localhost:9090
- [ ] Targets page shows services as UP
- [ ] Can execute a query and see results
- [ ] Graph view renders a time-series chart

---

## Troubleshooting (Browser-Only)

### Page Not Loading

| Problem | Solution |
|---------|----------|
| "This site can't be reached" | The service may not be running. Ask your administrator to start services. |
| Page loads but shows error | Try refreshing with Ctrl+F5 (hard refresh) |
| Slow to load | Wait 30-60 seconds — services may still be starting up |
| Works in one browser, not another | Try Chrome, Firefox, or Edge. Clear browser cache. |

### OpenSearch Dashboards Issues

| Problem | Solution |
|---------|----------|
| "No index patterns" message | Follow step 1.1 to create the `logs-*` index pattern |
| Discover shows "No results found" | Change the time range to "Last 7 days" or "Last 30 days" |
| Dashboard panels show "No data" | Verify the time range includes when logs were generated |
| Visualization won't load | Click the panel's down-arrow → Inspect → check for errors |

### Swagger UI Issues

| Problem | Solution |
|---------|----------|
| "Try it out" button missing | Scroll up — the button is at the top of each endpoint section |
| Response shows "Failed to fetch" | The API service may not be running |
| 500 Internal Server Error | OpenSearch may be unreachable. Check the /health/ endpoint first. |
| 404 Not Found | Double-check the endpoint path and parameters |

### Grafana Issues

| Problem | Solution |
|---------|----------|
| Login fails with admin/admin | Password may have been changed. Ask your administrator. |
| Dashboard shows "No data" | Check that datasources are configured and working |
| Panels show "Panel plugin not found" | Refresh the page. Grafana may still be loading plugins. |

### Prometheus Issues

| Problem | Solution |
|---------|----------|
| Targets show "DOWN" | The monitored service is not running or not exposing metrics |
| Query returns empty | Try a simpler query like `up` to verify Prometheus is working |

---

**Authors**: Balaji Rajan and Claude (Anthropic)
**License**: Apache 2.0
