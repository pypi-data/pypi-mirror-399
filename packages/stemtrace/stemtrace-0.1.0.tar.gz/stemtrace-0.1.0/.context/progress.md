# Progress: stemtrace

## Current Status: Ready for v0.1.0 Release

**Phase:** Phase 7 Complete (Canvas Graph Reconstruction)  
**Sprint:** v0.1.0 Release  
**Last Updated:** 2025-12-29

---

## What Works

- [x] Project concept defined
- [x] Architecture decisions made
- [x] Project name confirmed (stemtrace, PyPI available)
- [x] README.md created
- [x] Project context files created (.context/)
- [x] Cursor rules created (.cursor/rules/)
- [x] pyproject.toml with all dependencies, mypy, ruff, pytest config
- [x] **Broker-agnostic design** - Redis, RabbitMQ, extensible registry
- [x] **FastAPI pluggability design** - Mount as router in user's FastAPI app
- [x] **UI technology decided** - React SPA, pre-built with Vite
- [x] **Library component complete** - init(), signals, transports
- [x] **Server component complete** - GraphStore, EventConsumer, REST API, WebSocket, React UI

## What's Left to Build

### Phase 1: Project Setup ✅
- [x] pyproject.toml with all dependencies
- [x] Source directory structure (src/stemtrace/)
- [x] py.typed marker
- [x] pre-commit configuration
- [x] GitHub Actions CI
- [x] LICENSE file
- [x] CONTRIBUTING.md

### Phase 2: Core Domain ✅
- [x] TaskEvent dataclass *(frozen, with full fields)*
- [x] TaskState enum *(all states, str inheritance)*
- [x] TaskNode and TaskGraph models *(full implementation)*
- [x] Port interfaces (Protocols) *(EventTransport, TaskRepository)*
- [x] Unit tests for edge cases *(45 tests, 96% coverage)*
- [x] Documentation strings review *(Google style, examples included)*

### Phase 3: Library Component ✅
- [x] Celery signal handlers *(task_prerun, task_postrun, task_failure, task_retry, task_revoked)*
- [x] Redis publisher *(RedisTransport with Redis Streams)*
- [x] Memory transport *(MemoryTransport for testing)*
- [x] Transport registry *(get_transport() factory with scheme detection)*
- [x] init() public API *(wires config, transport, signals)*
- [x] Configuration handling *(StemtraceConfig frozen model)*

### Phase 4: Server Component ✅
- [x] Broker-agnostic event consumer *(EventConsumer, AsyncEventConsumer)*
- [x] In-memory graph store *(GraphStore with thread-safe access)*
- [x] FastAPI REST API *(tasks, graphs, health endpoints)*
- [x] FastAPI pluggable router *(`create_router()` factory)*
- [x] `StemtraceExtension` with lifespan/embedded consumer
- [x] Auth helpers *(require_basic_auth, require_api_key, no_auth)*
- [x] WebSocket support *(WebSocketManager, real-time event broadcasting)*
- [x] React SPA UI *(TanStack Router + Query, react-flow for graphs)*
- [x] Static file serving from bundled assets
- [x] Build pipeline *(hatchling hook for npm build)*

### Phase 5: Polish ✅

#### Testing
- [x] Write unit tests for server components (GraphStore, Consumer, WebSocket, Auth, Routes)
- [x] Integration tests for low-coverage modules (StemtraceExtension, create_router, WebSocket endpoint)
- [x] Integration tests with real Redis transport (7 tests)

#### CLI Implementation
- [x] Implement `stemtrace server` command *(uvicorn + StemtraceExtension)*
- [x] Implement `stemtrace consume` command *(standalone consumer with signal handling)*

#### Infrastructure
- [x] Docker setup (Dockerfile, docker-compose.yml, .dockerignore)

#### Release
- [x] PyPI release preparation (build verification, twine check, version bump)
- [x] CI pipeline enhancements (concurrency, caching, frontend checks, build verification)
- [x] Release automation (release.yml for PyPI + Docker + GitHub releases)
- [x] Dependabot for automated dependency updates
- [x] CI and coverage badges in README

### Phase 6: UX/DX Enhancements ✅

#### Task Data Capture
- [x] Capture PENDING state via task_sent signal (fires on .delay())
- [x] Capture RECEIVED state via worker bootstep (fires when worker picks up task)
- [x] Capture task args/kwargs in PENDING and STARTED events
- [x] Capture task result in SUCCESS event
- [x] Capture exception + traceback in FAILURE/RETRY events
- [x] Robust event ordering (retry_count, state_priority, timestamp)
- [x] Frontend deduplication of PENDING/RECEIVED from retry re-queues

#### Sensitive Data Scrubbing
- [x] `library/scrubbing.py` with Sentry-style key matching
- [x] Default sensitive keys (password, api_key, token, credit_card, etc.)
- [x] Configurable `additional_sensitive_keys` and `safe_keys`

#### Task Registry
- [x] `/api/tasks/registry` endpoint
- [x] Registry UI page with search

#### UI Enhancements
- [x] Parameters section in task detail view
- [x] Result section in task detail view
- [x] Expandable error details (exception + traceback)

#### Examples
- [x] `fetch_api_data` — retry demo with real exceptions
- [x] `process_user_data` — sensitive data scrubbing demo
- [x] `always_fails` — failure with traceback demo
- [x] CLI demo runner (`python examples/celery_app.py <demo>`)

### Pre-Release: E2E Testing ✅

Complete E2E test coverage before v0.1.0 release.

#### Docker-based API E2E
- [x] Docker Compose test environment (Redis + Worker + Server)
- [x] E2E test: task execution → event capture → API visibility
- [x] E2E test: workflow (chain/group) → graph construction
- [x] E2E test: WebSocket real-time updates

#### Playwright Browser E2E
- [x] Playwright setup and configuration
- [x] E2E test: Tasks page navigation and filtering
- [x] E2E test: Task detail view (timeline, parameters, results)
- [x] E2E test: Graph visualization renders correctly
- [x] E2E test: Registry page search

#### CI Integration
- [x] E2E tests in GitHub Actions (separate workflow)
- [x] Playwright report artifacts

### Phase 7: Canvas Graph Reconstruction ✅

**Implemented:** group_id capture and synthetic GROUP node generation.

#### What's Implemented
- [x] Add `group_id` field to `TaskEvent` model
- [x] Capture `group_id` from `task.request.group` in signal handlers
- [x] Capture `group_id` from message headers in bootstep
- [x] `NodeType` enum (TASK/GROUP/CHORD)
- [x] Detect group: multiple tasks with same `group_id`
- [x] Create synthetic GROUP node when 2+ tasks share group_id
- [x] Upgrade GROUP to CHORD when callback detected
- [x] Link CHORD node to callback task
- [x] `/api/graphs/{id}` returns synthetic nodes with `node_type`
- [x] Render GROUP/CHORD nodes with distinct styling
- [x] Show start time + duration in graph node labels
- [x] Unit tests (41 graph tests, 23 signal tests)
- [x] Integration tests (15 FastAPI tests including synthetic group nodes)

#### What's Deferred
- [ ] Nested canvas detection (chain inside group)
- [ ] RabbitMQ group_id capture

#### What Works Now
| Celery Pattern | Status |
|---------------|--------|
| `chain(a, b, c)` | ✅ a→b→c edges via parent_id |
| `group(a, b, c)` | ✅ Grouped via synthetic GROUP node |
| `chord(group, callback)` | ✅ CHORD node with callback linking |
| Dynamic `task.delay()` inside task | ✅ Works (parent_id) |

### Phase 8: Execution & Worker Lifecycle Enrichment ⚡ HIGH PRIORITY

**Strategic importance:** Prerequisite for anomaly detection (Phase 8.5). Without worker lifecycle events, we can't detect orphaned tasks or worker crashes. See `strategic-analysis.md`.

Enrich events with worker/queue context, capture worker lifecycle, and detect anomalies.

#### Task Enrichment
- [ ] Add `worker` field to TaskEvent (hostname of executing worker)
- [ ] Add `queue` field to TaskEvent (routing key / queue name)
- [ ] Update signal handlers to capture worker/queue from task request

#### Worker Lifecycle Events 🆕

Celery provides these signals for worker lifecycle:
- `worker_ready` — Worker online (hostname, pid, registered tasks)
- `worker_shutdown` — Worker going offline (graceful)
- `worker_process_init` / `worker_process_shutdown` — Pool process lifecycle

Implementation:
- [ ] Add `WorkerEvent` model (worker_id, hostname, pid, state, timestamp, registered_tasks)
- [ ] Hook `worker_ready` signal → emit WORKER_READY event
- [ ] Hook `worker_shutdown` signal → emit WORKER_SHUTDOWN event
- [ ] Store worker sessions in GraphStore (worker_id → WorkerSession)
- [ ] Track registered tasks per worker for registry cross-check

#### Interrupted Task Detection 🆕

When worker shuts down, correlate with in-flight tasks:
- [ ] On WORKER_SHUTDOWN, find tasks in STARTED state for that worker
- [ ] Mark as INTERRUPTED (virtual state) or add `interrupted: true` flag
- [ ] Handle `acks_late` case: duplicate STARTED events after restart

#### Monitoring APIs
- [ ] `GET /api/workers` — Active workers with current task counts
- [ ] `GET /api/workers/{id}/history` — Worker sessions with start/stop times
- [ ] `GET /api/stats` — Duration percentiles, failure rates by task name
- [ ] `GET /api/orphans` — Tasks stuck in STARTED > threshold OR interrupted

### Phase 8.5: Anomaly Detection & Visibility 🆕 ⚡ CRITICAL

**Strategic importance:** #1 blocker for production adoption. Users need to know when things break. See `strategic-analysis.md`.

Detect task anomalies and clearly communicate problems to users. Builds on Phase 8's worker lifecycle capture.

#### Unregistered Task Detection

**Problem:** Tasks submitted to unregistered names show as PENDING forever. Workers silently fail with `KeyError` before any stemtrace signals fire.

Detection (depends on Phase 8 WorkerEvent with registered_tasks):
- [ ] Build global registry from all active workers' registered_tasks
- [ ] On new PENDING event, check if task name exists in global registry
- [ ] Add `registered: bool` field to task/node responses
- [ ] Fallback: timeout-based detection for PENDING > N minutes

#### Stuck/Orphan Task Detection

| Scenario | Detection |
|----------|-----------|
| PENDING + unregistered | No worker has task in registry |
| PENDING + timeout | PENDING > 5 min (configurable) |
| STARTED + worker crash | Worker SHUTDOWN event with no task completion |
| STARTED + timeout | STARTED > 30 min (configurable) |

- [ ] Compute `anomaly` field on tasks: `null | 'unregistered' | 'stuck' | 'interrupted'`
- [ ] `GET /api/tasks/anomalies` — All problematic tasks

#### UI Indicators
- [ ] Warning badge on tasks with anomalies
- [ ] Tooltip explaining the issue ("Task not in any worker registry", etc.)
- [ ] Filter: "Problematic tasks" in task list
- [ ] Dashboard section: Anomaly summary

#### Worker Session Timeline 🆕

Visualize task executions segmented by worker sessions:
- [ ] In task list: Insert "Worker @host started" / "Worker @host stopped" markers
- [ ] In graphs page: Show which worker session each graph belongs to
- [ ] On worker restart: Show "2 new tasks registered" diff indicator

### Phase 9: UI Reorganization

Restructure UI to Dashboard-first architecture.

#### Navigation
- [ ] New navigation: Dashboard | Executions | Registry
- [ ] Merge Tasks + Graphs into unified Executions page
- [ ] Enhance Registry with runtime stats (runs, duration, failure rate)

#### Dashboard Page (`/`)
- [ ] Stats cards: Total tasks (24h), success rate, avg duration
- [ ] Recent failures: Last 5 failed tasks
- [ ] Orphan alerts: Stale STARTED tasks
- [ ] Live activity: Mini timeline of recent events

#### Executions Page (`/executions`)
- [ ] Keep List/Timeline toggle
- [ ] Add "Flows only" filter (root tasks)
- [ ] Click task → detail with inline flow graph

#### Execution Detail (`/executions/$taskId`)
- [ ] Add flow graph section showing execution in context
- [ ] Highlight current task in the flow graph

#### Registry Page (`/registry`)
- [ ] Show runs (24h), last run, avg duration, failure rate per task
- [ ] Click → filtered Executions view

### Phase 10: Export and Integration ⚡ HIGH PRIORITY

**Strategic importance:** Enables long-term retention without adding database complexity. OTEL export is the answer for users needing 30-day analytics. See `strategic-analysis.md`.

Enable long-term analytics via external systems. stemtrace stays lean; users bring their own storage.

#### OpenTelemetry Export
- [ ] Optional dependency: `opentelemetry-sdk`
- [ ] Config: `otel_endpoint` in init() or env var
- [ ] Map ExecutionGraph → OTEL Trace with spans
- [ ] Push to Jaeger, Tempo, Honeycomb, Datadog

#### Webhook Export
- [ ] `init(app, webhook_url="...")` for fire-and-forget event push
- [ ] Non-blocking POST to user endpoint

#### JSON Export API
- [ ] `GET /api/export/executions?from=...&to=...`
- [ ] Download execution data as JSON

### Phase 11: Ecosystem Polish

#### RabbitMQ Transport
- [ ] `RabbitMQTransport` using fanout exchange
- [ ] Auto-detect from `amqp://` URL scheme

#### Documentation
- [ ] Update README roadmap
- [ ] Add integration examples (Jaeger, Grafana)
- [ ] Architecture diagrams

### Not Planned (Strategic Decisions)

See `strategic-analysis.md` for full competitive rationale.

| Feature | Reason |
|---------|--------|
| PostgreSQL persistence | Zero-infra advantage — use OTEL export instead |
| SQLite persistence | Low priority; ship OTEL first, reassess if demand emerges |
| Task control (retry/cancel) | Stay read-only for production safety |
| Ops alerting (PagerDuty, etc.) | Users have existing monitoring stacks |
| Workflow automation | Not an ops platform, stay focused on visualization |

---

## Current Sprint Tasks

**v0.1.0 Release**

Phase 7 (Canvas Graph Reconstruction) complete. Ready to release:
1. Tag v0.1.0: `git tag v0.1.0 && git push origin v0.1.0`
2. Configure PyPI trusted publishing
3. GitHub release will trigger PyPI + Docker publish

---

## Known Issues

- **Coverage at 90%+** — All checks passing
- **All tests passing** — 350+ Python tests (unit + integration), plus Playwright E2E tests

### Unregistered Tasks Appear Stuck in PENDING

**Priority: High (UX issue)**

When a task is submitted but the worker doesn't have it registered:
1. `task_sent` fires → PENDING event captured ✓
2. Worker receives message → `KeyError: 'task.name'` in Celery internals
3. Task stays PENDING forever in stemtrace (never progresses)

**Root cause:** Celery's task routing fails before any worker signals fire. The error:
```
celery/worker/consumer/consumer.py, line 670, in on_task_received
    strategy = strategies[type_]
KeyError: 'examples.celery_app.parallel_chord'
```

**Planned fix:** See Phase 8.5 below — Detect unregistered/orphan tasks.

### Remaining Low Coverage (edge cases only)

| Module | Coverage | Missing |
|--------|----------|---------|
| `consumer.py` | 84% | Error handling paths |
| `extension.py` | 83% | UI serving when dist exists |
| `static.py` | 90% | 404 fallback path |

---

## Strategic Principles

- **Lead with flow** — Model Celery as a graph of executions, not just task statuses
- **Match monitoring** — Orphans, workers, stats emerge naturally from flow data
- **Stay read-only** — No task control, safe for production
- **Zero new infrastructure** — Redis only, no PostgreSQL requirement
- **Export for long-term** — Integrate with existing observability stacks (OTEL, webhooks)

## Notes

- Clean architecture: `core/` → `library/` / `server/` (no cross-imports)
- Broker-agnostic: Redis Streams (implemented), RabbitMQ (planned)
- FastAPI: `StemtraceExtension` for full integration

## References

- **Frontend build pipeline**: See `tech-context.md`
- **Design decisions**: See `system-patterns.md`
- **Competitive positioning**: See `strategic-analysis.md`
