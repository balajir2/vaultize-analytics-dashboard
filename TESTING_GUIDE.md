# Vaultize Analytics - Manual Testing Guide

**Last Updated**: 2026-02-04
**Authors**: Balaji Rajan and Claude (Anthropic)
**License**: Apache 2.0
**System Status**: Fully Operational ✅

---

## 🚀 Quick Start

### 1. Start All Services

```bash
cd "d:\GitHub\Vaultize Analytics Dashboard"
docker compose up -d
docker compose ps  # Verify all services are "Up (healthy)"
```

---

## 📊 Test 1: OpenSearch Dashboards (5-10 minutes)

**URL**: http://localhost:5601

### Step 1: Create Index Pattern
1. Open http://localhost:5601
2. Click hamburger menu (☰) → Management → Stack Management
3. Click "Index Patterns" (under Kibana section)
4. Click "Create index pattern"
5. Enter index pattern: `logs-*`
6. Click "Next step"
7. Select time field: `@timestamp`
8. Click "Create index pattern"

### Step 2: Discover Your Logs
1. Click hamburger menu → Analytics → Discover
2. You should see 1,000+ sample logs!
3. **Try these filters**:
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
9. Click "Update" (▶ button)
10. See your log level distribution!

**✅ Expected Result**: Beautiful pie chart showing DEBUG, INFO, WARN, ERROR, FATAL distribution

---

## 🔌 Test 2: Analytics API (10-15 minutes)

**URL**: http://localhost:8000/docs (Interactive Swagger UI)

### Test 2.1: Health Check
1. Open http://localhost:8000/docs
2. Find `GET /health/` endpoint (should be first)
3. Click "Try it out"
4. Click "Execute"

**✅ Expected**:
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

**✅ Expected**: Returns 10 error logs with pagination info

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

**✅ Expected**: Returns up to 20 errors from api-service in last 24 hours

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

**✅ Expected**: Shows which 5 services have the most errors

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

**✅ Expected**: Returns error count per hour (time series data)

### Test 2.6: Top Values Shortcut
1. Find `GET /api/v1/top-values/{field}`
2. Click "Try it out"
3. Parameters:
   - `field`: `level`
   - `size`: `5`
4. Click "Execute"

**✅ Expected**: Shows distribution of all log levels

### Test 2.7: Index Statistics
1. Find `GET /api/v1/indices/`
2. Click "Try it out"
3. Parameters:
   - `pattern`: `logs-*`
4. Click "Execute"

**✅ Expected**: Lists all log indices with document counts and sizes

---

## 📈 Test 3: Grafana (5 minutes)

**URL**: http://localhost:3100
**Login**: `admin` / `admin` (change password when prompted)

### Steps:
1. Open http://localhost:3100
2. Login with admin/admin
3. Set new password (or skip)
4. Explore default dashboards (left menu → Dashboards)
5. View system metrics (CPU, memory, disk)

**✅ Expected**: See Prometheus metrics visualized

---

## 💻 Test 4: Command Line (Optional - For Tech Users)

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

## 🎯 Fun Test Scenarios

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

## ✅ Testing Checklist

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
- [ ] Grafana loads (http://localhost:3100)
- [ ] Can login to Grafana

---

## 🐛 Troubleshooting

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

## 📸 What Success Looks Like

### OpenSearch Dashboards
- ✅ See logs with fields: timestamp, level, service, message, host
- ✅ Can filter by log level
- ✅ Time range selector works
- ✅ Visualizations render correctly

### Analytics API
- ✅ All 14 endpoints respond
- ✅ Health status is "green"
- ✅ Search returns results with pagination
- ✅ Aggregations show buckets with counts
- ✅ Response time < 100ms for most queries

### Overall System
- ✅ All services healthy
- ✅ Can query logs multiple ways
- ✅ Data is searchable and filterable
- ✅ API documentation is clear and interactive

---

## 🎓 Key Endpoints Reference

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health/` | GET | API health status | - |
| `/api/v1/search/simple` | GET | Quick search | `?q=level:ERROR&size=10` |
| `/api/v1/search` | POST | Advanced search | With time range, fields |
| `/api/v1/aggregate` | POST | Analytics aggregations | terms, date_histogram |
| `/api/v1/top-values/{field}` | GET | Top values for field | `level`, `service` |
| `/api/v1/indices/` | GET | List indices | `?pattern=logs-*` |

---

## 💡 Tips

1. **Start with OpenSearch Dashboards** - Most visual and intuitive
2. **Then try API** - Understand programmatic access
3. **Experiment with searches** - Try different queries
4. **Look at raw data** - Click expand on log entries to see all fields
5. **Check response times** - Note how fast queries execute

---

## 📞 Need Help?

- **API Documentation**: http://localhost:8000/docs
- **OpenSearch Docs**: https://opensearch.org/docs/latest/
- **Sample Data**: Generated from `scripts/data/generate_sample_logs.py`

---

## ✨ Have Fun Testing!

This is a fully functional log analytics platform. Play around, try different queries, and see what insights you can find in the sample data!

**Next Step**: After testing, we'll build beautiful dashboards in M4 to make this data even more accessible! 📊
