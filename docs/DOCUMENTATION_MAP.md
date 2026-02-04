# Documentation Map

> Guide to where different types of documentation are located

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-04

---

## Purpose of This Document

This map ensures documentation is organized logically and prevents duplication. Use this guide to know **where to put** and **where to find** specific information.

---

## Documentation Structure

```
docs/
├── DOCUMENTATION_MAP.md           ← You are here
├── SESSION_NOTES.md               ← Session-to-session progress
├── architecture/                  ← System design
│   ├── README.md
│   ├── system-overview.md
│   ├── components.md
│   ├── data-flow.md
│   ├── tech-stack.md             ✅ Complete
│   ├── design-decisions.md
│   ├── scalability.md
│   └── security.md
├── deployment/                    ← Installation & configuration
│   ├── README.md
│   ├── quickstart.md             ✅ Complete
│   ├── prerequisites.md
│   ├── docker-compose.md
│   ├── kubernetes.md
│   ├── configuration.md          ✅ Complete
│   ├── environment-setup.md      ✅ Complete
│   └── upgrading.md
├── operations/                    ← Day-to-day operations
│   ├── README.md
│   ├── operations-guide.md
│   ├── monitoring.md
│   ├── backup-restore.md
│   ├── troubleshooting.md
│   ├── performance-tuning.md
│   ├── ilm-policies.md
│   ├── disaster-recovery.md
│   └── security-ops.md
├── api/                          ← API documentation
│   ├── README.md
│   ├── overview.md
│   ├── authentication.md
│   ├── search.md
│   ├── aggregations.md
│   ├── index-management.md
│   ├── alerts.md
│   └── openapi.yaml
└── user-guides/                  ← End-user guides
    ├── README.md
    ├── getting-started.md
    ├── searching-logs.md
    ├── creating-dashboards.md
    ├── setting-up-alerts.md
    ├── visualizations.md
    ├── saved-searches.md
    └── best-practices.md
```

---

## What Goes Where?

### Root Files

| File | Purpose | Audience |
|------|---------|----------|
| [README.md](../README.md) | Project overview, quick start, links to docs | Everyone (first stop) |
| [LICENSE.md](../LICENSE.md) | Legal license terms | Legal, contributors |
| [AUTHORS.md](../AUTHORS.md) | Author and contributor list | Contributors |
| [CHANGELOG.md](../CHANGELOG.md) | Version history and changes | Developers, operators |
| [MILESTONES.md](../MILESTONES.md) | Project milestones and progress | Project team |
| [TODO.md](../TODO.md) | Current task list | Developers |
| [Claude.md](../Claude.md) | Agent instructions | Claude (not for users) |

### Architecture Documentation

**Location**: `docs/architecture/`

**Put here**:
- System design and architecture diagrams
- Component descriptions and interactions
- Technology choices and rationale
- Scalability and performance considerations
- Security architecture

**Don't put here**:
- How to install (that's deployment docs)
- How to use (that's user guides)
- API endpoints (that's API docs)

**Examples**:
- ✅ "Why we chose OpenSearch over Elasticsearch" → architecture/design-decisions.md
- ✅ "How the alerting system works" → architecture/components.md
- ❌ "How to install OpenSearch" → deployment/quickstart.md
- ❌ "How to create an alert" → user-guides/setting-up-alerts.md

### Deployment Documentation

**Location**: `docs/deployment/`

**Put here**:
- Installation instructions
- Configuration reference
- Environment setup (dev/staging/prod)
- Upgrade procedures
- Prerequisites and requirements

**Don't put here**:
- Daily operations (that's operations docs)
- How to use features (that's user guides)
- System design (that's architecture docs)

**Examples**:
- ✅ "Installing on Docker Compose" → deployment/docker-compose.md
- ✅ "Environment variables reference" → deployment/configuration.md
- ❌ "How to backup data" → operations/backup-restore.md
- ❌ "How to search logs" → user-guides/searching-logs.md

### Operations Documentation

**Location**: `docs/operations/`

**Put here**:
- Day-to-day operational tasks
- Monitoring and health checks
- Backup and restore procedures
- Troubleshooting guides
- Performance tuning
- Security operations

**Don't put here**:
- Initial installation (that's deployment docs)
- Feature usage (that's user guides)
- API calls (that's API docs)

**Examples**:
- ✅ "How to backup OpenSearch" → operations/backup-restore.md
- ✅ "Troubleshooting cluster issues" → operations/troubleshooting.md
- ❌ "How to install" → deployment/quickstart.md
- ❌ "How to create dashboards" → user-guides/creating-dashboards.md

### API Documentation

**Location**: `docs/api/`

**Put here**:
- API endpoint documentation
- Request/response schemas
- Authentication methods
- Code examples
- OpenAPI specification

**Don't put here**:
- System architecture (that's architecture docs)
- Installation (that's deployment docs)
- UI usage (that's user guides)

**Examples**:
- ✅ "POST /api/v1/search endpoint" → api/search.md
- ✅ "API authentication with JWT" → api/authentication.md
- ❌ "How the API service works internally" → architecture/components.md
- ❌ "How to use the UI search" → user-guides/searching-logs.md

### User Guides

**Location**: `docs/user-guides/`

**Put here**:
- Feature usage tutorials
- Step-by-step guides
- Best practices
- FAQ
- UI navigation

**Don't put here**:
- System administration (that's operations docs)
- API calls (that's API docs)
- Installation (that's deployment docs)

**Examples**:
- ✅ "How to create a dashboard in the UI" → user-guides/creating-dashboards.md
- ✅ "Search syntax guide" → user-guides/searching-logs.md
- ❌ "API search endpoint" → api/search.md
- ❌ "Troubleshooting search performance" → operations/troubleshooting.md

---

## Cross-Referencing Guidelines

### When to Cross-Reference

**DO** cross-reference when:
- A concept spans multiple areas
- Users might look in multiple places
- Context from another section is helpful

**Example**:
```markdown
For API-based searching, see [Search API](../api/search.md).
For UI-based searching, see [Searching Logs](../user-guides/searching-logs.md).
```

### How to Cross-Reference

**Use relative links**:
```markdown
<!-- From deployment/ to operations/ -->
For backup procedures, see [Backup & Restore](../operations/backup-restore.md).

<!-- From user-guides/ to api/ -->
For programmatic access, see [API Documentation](../api/README.md).
```

---

## Specific Documentation Rules

### Deployment Instructions

**Should appear in**:
1. **README.md** - Quick start only (4-5 commands max)
2. **docs/deployment/quickstart.md** - Detailed step-by-step
3. **docs/deployment/docker-compose.md** - Production deployment
4. **docs/deployment/kubernetes.md** - Kubernetes deployment

**Should NOT appear in**:
- Architecture docs
- User guides
- API docs
- Operations docs (except references)

### Usage Instructions

**Should appear in**:
1. **docs/user-guides/** - UI-based usage
2. **docs/api/** - API-based usage
3. **README.md** - Brief "what you can do" overview

**Should NOT appear in**:
- Deployment docs (only installation)
- Architecture docs (only how it works)
- Operations docs (only maintenance)

### Configuration

**Should appear in**:
1. **docs/deployment/configuration.md** - Complete variable reference
2. **docs/deployment/environment-setup.md** - Environment-specific configs
3. **.env.example** - Inline comments for each variable

**Should NOT appear in**:
- README.md (too detailed)
- User guides (users don't configure)
- Architecture docs (implementation details)

---

## Documentation Checklist

When creating new documentation:

- [ ] Determined correct location using this map
- [ ] Checked for duplication in other sections
- [ ] Added cross-references where needed
- [ ] Updated parent README if needed
- [ ] Used consistent formatting
- [ ] Added "Last Updated" date
- [ ] Included author attribution

---

## Common Mistakes to Avoid

### ❌ Don't Do This

1. **Deployment instructions in user guides**
   ```markdown
   <!-- user-guides/getting-started.md -->
   First, install Docker and run `docker compose up`...  ❌
   ```
   → Put in `deployment/quickstart.md` instead

2. **API documentation in user guides**
   ```markdown
   <!-- user-guides/searching.md -->
   Call POST /api/v1/search with {"query": "error"}...  ❌
   ```
   → Put in `api/search.md` instead

3. **Troubleshooting in deployment docs**
   ```markdown
   <!-- deployment/quickstart.md -->
   If the cluster is red, check shard allocation...  ❌
   ```
   → Put in `operations/troubleshooting.md` instead

4. **Architecture details in README**
   ```markdown
   <!-- README.md -->
   The alerting engine uses APScheduler with...  ❌
   ```
   → Put in `architecture/components.md` instead

### ✅ Do This Instead

1. **Deployment in deployment docs**
   ```markdown
   <!-- deployment/quickstart.md -->
   ### Step 1: Install Docker
   ...detailed instructions...
   ```

2. **API docs in API section**
   ```markdown
   <!-- api/search.md -->
   ## POST /api/v1/search
   ...endpoint documentation...
   ```

3. **Troubleshooting in operations**
   ```markdown
   <!-- operations/troubleshooting.md -->
   ### Red Cluster Status
   ...troubleshooting steps...
   ```

4. **High-level in README**
   ```markdown
   <!-- README.md -->
   For deployment, see [Quick Start](docs/deployment/quickstart.md)
   ```

---

## Updating Documentation

### When Code Changes

Update these docs:
- [ ] CHANGELOG.md (what changed)
- [ ] Relevant API docs (if endpoints changed)
- [ ] Configuration docs (if new env vars)
- [ ] User guides (if UI changed)

### When Architecture Changes

Update these docs:
- [ ] architecture/components.md
- [ ] architecture/tech-stack.md (if technology changed)
- [ ] architecture/design-decisions.md (document why)

### When Deployment Changes

Update these docs:
- [ ] deployment/quickstart.md
- [ ] deployment/configuration.md
- [ ] .env.example (inline comments)

---

## Documentation Maintenance

### Weekly

- [ ] Review SESSION_NOTES.md
- [ ] Update TODO.md
- [ ] Check for broken links

### Monthly

- [ ] Review and update "Last Updated" dates
- [ ] Check for outdated screenshots
- [ ] Verify all commands still work
- [ ] Update version numbers

### Per Release

- [ ] Update CHANGELOG.md
- [ ] Update MILESTONES.md
- [ ] Review all documentation
- [ ] Update README.md version

---

## Need Help?

If unsure where documentation belongs:
1. Check this map
2. Look at existing docs in that section
3. Ask yourself: "Who is the audience?"
   - Developers installing → deployment/
   - Operators maintaining → operations/
   - Users using features → user-guides/
   - Developers calling API → api/
   - Understanding design → architecture/

---

**Last Updated**: 2026-02-04
