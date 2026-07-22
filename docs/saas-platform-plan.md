# SaaS Platform Plan

## Decisions Made

| Decision | Choice |
|---|---|
| Database | **Neon** (serverless PostgreSQL) |
| User auth | **Clerk** (GitHub/Google OAuth + magic links) |
| SaaS model | **Both** — internal key for backend + direct API keys for partners |
| v1 scope | **Full** — orgs, users, API keys in DB, usage tracking, persisted audit, billing-ready metrics |
| Rate limiting | **DB counters** (no Redis for v1) |

---

## Phases

### Phase 1: Database Foundation

**Goal:** Neon connected, new tables created, SQLite migration path ready.

**New files:**
```
app/db/
├── __init__.py
├── engine.py           ← create_engine, get_session, init_db
└── models/
    ├── __init__.py
    ├── rag.py           ← MedicalSource, SourceDocument, DocumentChunk (moved from rag/schemas.py)
    ├── platform.py      ← Organization, User, ApiKey, UsageRecord
    └── audit.py         ← AuditTrace, AuditEvent
```

**`app/db/models/platform.py`:**
```python
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    id: int | None = Field(default=None, primary_key=True)
    clerk_org_id: str = Field(unique=True, index=True)  # Clerk's org ID
    name: str
    slug: str = Field(unique=True)
    plan: str = "free"  # free | pro | enterprise
    is_active: bool = True
    created_at: datetime
    users: list["User"] = Relationship(back_populates="organization")
    api_keys: list["ApiKey"] = Relationship(back_populates="organization")

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    clerk_user_id: str = Field(unique=True, index=True)
    email: str
    name: str | None
    role: str = "member"  # admin | member
    organization_id: int = Field(foreign_key="organizations.id")
    organization: Organization = Relationship(back_populates="users")
    created_at: datetime

class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"
    id: str = Field(primary_key=True)  # UUID
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    organization: Organization = Relationship(back_populates="api_keys")
    label: str
    key_hash: str  # SHA-256 of raw key
    prefix: str    # first 12 chars of raw key
    created_at: datetime
    expires_at: datetime | None
    is_active: bool = True
    last_used_at: datetime | None
    created_by: int | None = None  # user_id who created it
```

**`app/db/models/audit.py`:**
```python
class AuditTrace(SQLModel, table=True):
    __tablename__ = "audit_traces"
    id: int | None = Field(default=None, primary_key=True)
    trace_id: str = Field(unique=True, index=True)
    organization_id: int | None = Field(default=None, foreign_key="organizations.id", index=True)
    workflow: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    outcome: str | None  # success | blocked | error
    request_id: str | None
    api_key_id: str | None
    events: list["AuditEvent"] = Relationship(back_populates="trace")

class AuditEvent(SQLModel, table=True):
    __tablename__ = "audit_events"
    id: int | None = Field(default=None, primary_key=True)
    trace_id: str = Field(foreign_key="audit_traces.trace_id", index=True)
    trace: AuditTrace = Relationship(back_populates="events")
    event_type: str
    timestamp: datetime
    data: dict = Field(default_factory=dict, sa_type=JSON)  # JSONB in PG
```

**`app/db/models/usage.py`:**
```python
class UsageRecord(SQLModel, table=True):
    __tablename__ = "usage_records"
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    api_key_id: str | None
    date: str  # YYYY-MM-DD
    endpoint: str
    request_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0

class UsageDailyTotals(SQLModel, table=True):  ← materialized/aggregated
    __tablename__ = "usage_daily_totals"
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    date: str
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    unique_endpoints: int
```

**`app/db/engine.py`:**
```python
from sqlmodel import SQLModel, Session, create_engine

engine = None

def get_engine(database_url: str):
    global engine
    if engine is None:
        engine = create_engine(database_url, pool_pre_ping=True)
    return engine

def init_db(database_url: str):
    e = get_engine(database_url)
    SQLModel.metadata.create_all(e)

def get_session():
    return Session(get_engine())
```

**Modified files:**
| File | Change |
|---|---|
| `app/core/config.py` | Update `database_url` default to Neon |
| `app/rag/schemas.py` | Remove table models, keep only `Citation` (non-table schema) |
| `app/rag/registry.py` | Import models from `app.db.models.rag`, remove `check_same_thread` |
| `pyproject.toml` | Add `psycopg` dependency |

---

### Phase 2: Persist Audit Traces

**Goal:** Replace in-memory `AuditTraceWriter` with DB writes. Query audit by org + date range.

**Modified files:**
| File | Change |
|---|---|
| `app/ai/audit/writer.py` | Full rewrite — `start_trace`, `record_event`, `end_trace` write to `audit_traces` + `audit_events` tables |
| `app/ai/audit/models.py` | Keep dataclasses for in-memory use, or remove if DB handles everything |
| `app/ai/orchestrator/orchestrator.py` | Pass `organization_id` to `start_trace()` |
| `app/api/routes/audit.py` | Update to support `org_id`, `from`, `to` query params |
| `app/main.py` | Remove no-op init, wire DB-backed audit writer |

**`AuditTraceWriter` new behaviour:**
```python
class AuditTraceWriter:
    def start_trace(self, trace_id, workflow, metadata):
        org_id = metadata.get("organization_id")
        # INSERT INTO audit_traces ...

    def record_event(self, trace_id, event_type, data):
        # INSERT INTO audit_events ...

    def end_trace(self, trace_id, summary):
        # UPDATE audit_traces SET completed_at, duration_ms, outcome ...

    def get_trace(self, trace_id):
        # SELECT + JOIN events

    def get_recent_traces(self, limit, org_id=None, from_date=None, to_date=None):
        # SELECT with filters
```

**Key design: `start_trace` / `record_event` / `end_trace` are synchronous DB writes.** For production, you might want an async queue, but for v1 direct writes are fine — audit is append-only and Neon handles it well.

---

### Phase 3: Move API Keys to DB

**Goal:** Replace in-memory `ApiKeyStore` with DB queries.

**Modified files:**
| File | Change |
|---|---|
| `app/api/keys/service.py` | Rewrite all methods to query `api_keys` table |
| `app/core/middleware/api_key.py` | Validate key against DB instead of in-memory store |
| `app/api/routes/keys.py` | Add `org_id` association, route under `/v1/organizations/{org_id}/api-keys` |

**`ApiKeyStore` new behavior:**
- `create_key(org_id, label, expires_at)` — INSERT, return raw key (shown once)
- `validate_key(raw_key)` — hash input, SELECT by hash from DB
- `list_keys(org_id)` — SELECT WHERE org_id
- `rotate_key(key_id)` — UPDATE hash + prefix, return new raw key
- `revoke_key(key_id)` — UPDATE is_active = false
- `bootstrap_static_keys` — still works, seeds internal key into DB

**Internal key flow:**
1. On startup, `ZAM_AI_INTERNAL_API_KEYS` env var is read
2. Each key is inserted into `api_keys` with `organization_id = null` (internal)
3. Backend-to-backend calls use these keys — no org attached

**Partner key flow:**
1. Partner creates API key via `POST /v1/organizations/{org_id}/api-keys`
2. Key is stored with their `organization_id`
3. Requests with this key get tagged with the org for audit + billing

---

### Phase 4: SaaS Auth Endpoints

**Goal:** Clerk webhook syncs users/orgs. Partners can see usage.

**New endpoints:**
| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/auth/webhook` | Clerk webhook — `user.created`, `organization.created`, `organization_membership.created` |
| `GET` | `/v1/organizations/me` | Current org details + plan |
| `GET` | `/v1/organizations/me/usage?from=&to=` | Usage breakdown by endpoint |
| `GET` | `/v1/organizations/me/api-keys` | List this org's API keys |
| `POST` | `/v1/organizations/me/api-keys` | Create new API key |
| `POST` | `/v1/organizations/me/api-keys/{id}/rotate` | Rotate key |
| `POST` | `/v1/organizations/me/api-keys/{id}/revoke` | Revoke key |

**New files:**
```
app/api/routes/
├── auth.py         ← Clerk webhook
└── organizations.py ← org info, usage, per-org key management
```

**Middleware update:**
Add Clerk JWT verification for user-facing endpoints. Pattern:
```python
class ClerkAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/v1/auth/"):
            return await call_next(request)
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token:
            payload = verify_clerk_jwt(token)
            request.state.clerk_user_id = payload["sub"]
            request.state.organization_id = payload.get("org_id")
        return await call_next(request)
```

Internal API key middleware stays as-is for backend-to-backend calls. Both middleware chains together:
1. If `X-Zam-AI-Key` header present → validate internal key (current behaviour)
2. Else if `Authorization: Bearer <jwt>` present → validate Clerk JWT
3. Else → 401

---

### Phase 5: Usage Tracking & Rate Limiting

**Goal:** Every request logs a usage record. Rate limits enforced from DB.

**New middleware or hooks:**
```python
class UsageTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if should_track(request):
            # INSERT INTO usage_records ...
            # organization_id from request.state
            # endpoint from request.url.path
            # tokens from response headers (set by orchestrator)
        return response
```

**Rate limiting:** Before processing request, check recent request count from `usage_records` for this org + window. If over limit → 429.

**`app/db/models/usage.py`** has `UsageRecord` (per-request granularity) and `UsageDailyTotals` (aggregated for fast queries).

---

## File Change Summary

### New files (7)
| File | Lines est. |
|---|---|
| `app/db/__init__.py` | 1 |
| `app/db/engine.py` | 20 |
| `app/db/models/__init__.py` | 5 |
| `app/db/models/rag.py` | 60 |
| `app/db/models/platform.py` | 60 |
| `app/db/models/audit.py` | 30 |
| `app/db/models/usage.py` | 25 |

### New route files (2)
| File | Lines est. |
|---|---|
| `app/api/routes/auth.py` | 60 |
| `app/api/routes/organizations.py` | 120 |

### Modified files (12)
| File | Change |
|---|---|
| `app/core/config.py` | Update `database_url`, add Clerk settings |
| `app/rag/schemas.py` | Remove table models, keep `Citation` |
| `app/rag/registry.py` | Update imports, remove SQLite hack |
| `app/ai/audit/writer.py` | Rewrite to use DB |
| `app/ai/audit/models.py` | Optional cleanup |
| `app/ai/orchestrator/orchestrator.py` | Pass `organization_id` to audit |
| `app/api/keys/service.py` | Rewrite to use DB |
| `app/api/routes/keys.py` | Add org scoping |
| `app/api/routes/audit.py` | Add org/date filters |
| `app/core/middleware/api_key.py` | Validate against DB |
| `app/main.py` | Init DB, wire new middleware |
| `pyproject.toml` | Add `psycopg`, remove unused deps |

### Deleted files (0)

---

## Risk & Mitigation

| Risk | Mitigation |
|---|---|
| **SQLite → Neon migration** | Write a migration script that reads from SQLite, writes to Neon. Test with a copy of prod DB. |
| **Clerk webhook downtime** | Webhooks are retried for 24h. Sync on first login as fallback. |
| **Audit DB writes slow down requests** | Writes are fire-and-forget (no await needed for audit). If it becomes an issue, add a background queue. |
| **Rate limit DB queries slow down requests** | Use a simple in-memory cache (dict) with TTL as first pass, DB as fallback. |
