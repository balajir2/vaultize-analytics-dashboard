# OpenSearch Dashboards - Pre-built Dashboards

Pre-configured dashboards for the Vaultize Analytics Platform.

**Created**: 2026-02-04
**Authors**: Balaji Rajan and Claude (Anthropic)

---

## 📊 Available Dashboards

### 1. Operations Dashboard
**Purpose**: Real-time operational monitoring
**Refresh**: Auto-refresh every 30 seconds
**Time Range**: Last 24 hours
**URL**: http://localhost:5601/app/dashboards#/view/dashboard-operations

**Panels**:
- **Log Volume Over Time**: Line chart showing log ingestion rate
- **Log Level Distribution**: Pie chart showing DEBUG, INFO, WARN, ERROR, FATAL breakdown
- **Top Services**: Horizontal bar chart of most active services
- **Error Rate by Service**: Line chart tracking errors per service over time
- **Recent Critical Events**: Table of recent ERROR/FATAL logs

**Use Cases**:
- Monitor system health in real-time
- Quickly identify service issues
- Track error spikes
- Operational dashboards for NOC/SOC teams

---

### 2. Analytics Dashboard
**Purpose**: Historical analysis and deep-dive investigations
**Refresh**: Manual (no auto-refresh)
**Time Range**: Last 7 days
**URL**: http://localhost:5601/app/dashboards#/view/dashboard-analytics

**Panels**:
- **Log Volume Over Time**: Full-width timeline of log activity
- **Log Level Distribution**: Overview of log severity distribution
- **Top Services**: Service activity breakdown
- **Top Error Messages**: Table showing most common error messages by service
- **Error Rate by Service**: Multi-line chart comparing error rates across services

**Use Cases**:
- Root cause analysis
- Trend identification
- Historical comparisons
- Incident post-mortems

---

## 🚀 Quick Start

### Method 1: Automatic Import (Recommended)

**Windows (PowerShell)**:
```powershell
cd dashboards\opensearch-dashboards
.\import_dashboards.ps1
```

**Linux/Mac (Bash)**:
```bash
cd dashboards/opensearch-dashboards
chmod +x import_dashboards.sh
./import_dashboards.sh
```

**Expected Output**:
```
==========================================
OpenSearch Dashboards Import Script
==========================================

Dashboards URL: http://localhost:5601
Checking OpenSearch Dashboards connectivity... OK

Importing saved objects...

Importing index-pattern... SUCCESS
  └─ Imported 1 objects
Importing visualizations... SUCCESS
  └─ Imported 6 objects
Importing dashboards... SUCCESS
  └─ Imported 2 objects

==========================================
Import Complete!
==========================================
```

### Method 2: Manual Import

1. Open OpenSearch Dashboards: http://localhost:5601
2. Go to Stack Management (☰ → Management → Stack Management)
3. Click "Saved Objects"
4. Click "Import"
5. Upload files in this order:
   - `saved-objects/index-pattern.ndjson`
   - `saved-objects/visualizations.ndjson`
   - `saved-objects/dashboards.ndjson`
6. Enable "Automatically overwrite conflicts"
7. Click "Import"

---

## 📖 Using the Dashboards

### Accessing Dashboards

1. Open http://localhost:5601
2. Click ☰ menu → Dashboard
3. Select "Operations Dashboard" or "Analytics Dashboard"

### Filtering Data

**By Time Range** (top right):
- Click time picker
- Select preset (Last 15 minutes, Last 24 hours, Last 7 days)
- Or set custom range

**By Search Query** (top search bar):
- Examples:
  - `level:ERROR` - Show only errors
  - `service:api-service` - Filter by service
  - `status_code:500` - Find 500 errors
  - `level:ERROR AND service:web-service` - Combine filters

**By Clicking Visualizations**:
- Click on pie chart segments
- Click on bar chart bars
- Click on table rows
- Creates automatic filters

### Customizing Visualizations

1. Click "Edit" button (top right)
2. Click on any visualization panel
3. Modify:
   - Time ranges
   - Aggregations
   - Field selections
   - Chart types
4. Click "Save" when done

---

## 🎨 Dashboard Components

### Visualizations Included

| Visualization | Type | Purpose | Key Metrics |
|---------------|------|---------|-------------|
| Log Volume Over Time | Line Chart | Monitor ingestion rate | Logs per time interval |
| Log Level Distribution | Pie Chart | See log severity breakdown | Count by level |
| Top Services | Horizontal Bar | Identify most active services | Log count per service |
| Top Error Messages | Data Table | Find common errors | Error message, service, count |
| Error Rate by Service | Multi-line Chart | Compare error trends | Errors over time by service |
| Recent Critical Events | Data Table | View latest critical logs | Recent ERROR/FATAL logs |

### Index Pattern

**Name**: `logs-*`
**Time Field**: `@timestamp`
**Pattern**: Matches all indices starting with "logs-"

### Saved Searches

Dashboards use filtered searches:
- **All Logs**: No filters (default)
- **Errors Only**: `level:ERROR OR level:FATAL`

---

## 🔧 Customization Guide

### Creating New Visualizations

1. Go to Visualize (☰ → Analytics → Visualizations)
2. Click "Create visualization"
3. Select visualization type
4. Choose index pattern: `logs-*`
5. Configure:
   - **Metrics**: What to measure (count, avg, sum, etc.)
   - **Buckets**: How to group (terms, date histogram, etc.)
   - **Options**: Colors, labels, formatting
6. Click "Save"

### Adding Visualization to Dashboard

1. Edit dashboard (Edit button)
2. Click "Add" → "Add from library"
3. Select your visualization
4. Drag to position and resize
5. Click "Save"

### Example: Create "Top Hosts" Visualization

```
Type: Vertical Bar Chart
Index Pattern: logs-*

Metrics:
- Y-Axis: Count

Buckets:
- X-Axis: Terms
- Field: host
- Order By: metric: Count
- Order: Descending
- Size: 10
```

---

## 📊 Common Use Cases

### Use Case 1: Investigate Error Spike

1. Open Operations Dashboard
2. Notice spike in "Log Volume Over Time"
3. Click on spike time period
4. Check "Top Error Messages" panel
5. Click on specific error to drill down
6. View full log details in "Recent Critical Events"

### Use Case 2: Compare Service Health

1. Open Analytics Dashboard
2. Set time range to "Last 7 days"
3. View "Error Rate by Service" chart
4. Identify which service has highest error rate
5. Click on service name to filter
6. Analyze error patterns in "Top Error Messages"

### Use Case 3: Monitor Real-Time Operations

1. Open Operations Dashboard
2. Dashboard auto-refreshes every 30 seconds
3. Monitor "Log Volume Over Time" for anomalies
4. Watch "Recent Critical Events" for new issues
5. Check "Log Level Distribution" for overall health

---

## 🎯 Best Practices

### Dashboard Performance

- **Time Range**: Shorter time ranges = faster queries
- **Auto-refresh**: Use only for operations dashboard
- **Filters**: Apply filters to reduce data scanned
- **Visualizations**: Limit aggregation buckets to 10-20

### Data Analysis

1. **Start Wide**: Use longer time ranges to spot trends
2. **Drill Down**: Apply filters to narrow focus
3. **Compare**: Use multiple time ranges side-by-side
4. **Save**: Save interesting queries as searches

### Collaboration

- **Share Dashboards**: Copy dashboard URL to share view
- **Export**: Use "Share" → "PDF Reports" for stakeholders
- **Embed**: Generate iframe code for external systems

---

## 🔍 Troubleshooting

### Dashboard Shows "No Data"

**Check**:
1. Index pattern exists: Stack Management → Index Patterns
2. Time range includes data: Expand time range
3. Logs are indexed: Check `curl http://localhost:9200/logs-*/_count`
4. OpenSearch is running: `docker compose ps`

### Visualizations Not Loading

**Solutions**:
1. Refresh browser (Ctrl+F5)
2. Clear Dashboards cache: Settings → Advanced Settings → Clear cache
3. Reimport saved objects
4. Check browser console for errors (F12)

### Import Script Fails

**Common Issues**:
- OpenSearch Dashboards not running: `docker compose up -d opensearch-dashboards`
- Port conflict: Check port 5601 is not in use
- File permissions: Ensure .ndjson files are readable

---

## 📁 File Structure

```
dashboards/opensearch-dashboards/
├── README.md                          # This file
├── import_dashboards.sh               # Import script (Linux/Mac)
├── import_dashboards.ps1              # Import script (Windows)
└── saved-objects/
    ├── index-pattern.ndjson           # Index pattern configuration
    ├── visualizations.ndjson          # 6 pre-built visualizations
    └── dashboards.ndjson              # 2 dashboards