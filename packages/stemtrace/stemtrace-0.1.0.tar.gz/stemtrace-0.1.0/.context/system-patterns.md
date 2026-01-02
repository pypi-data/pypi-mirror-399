# System Patterns: stemtrace

## Architecture Overview

stemtrace supports two deployment modes: **standalone server** or **FastAPI plugin**.

### Standalone Server Mode

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              User's Application                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         Celery Workers                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │  │    Worker    │  │    Worker    │  │    Worker    │           │    │
│  │  │  stemtrace │  │  stemtrace │  │  stemtrace │           │    │
│  │  │   (signals)  │  │   (signals)  │  │   (signals)  │           │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │    │
│  └─────────┼─────────────────┼─────────────────┼────────────────────┘    │
│            └─────────────────┼─────────────────┘                         │
│                              │ events                                    │
│                              ▼                                           │
│                      ┌───────────────┐                                   │
│                      │   Transport   │  ◄── Broker-agnostic              │
│                      └───────────────┘                                   │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │   stemtrace     │  ◄── Separate container
                     │     server        │
                     │  (Consumer + UI)  │
                     └───────────────────┘
```

### FastAPI Plugin Mode (Recommended)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         User's FastAPI Application                       │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │
│  │   User Routes    │  │ stemtrace      │  │   Celery Workers     │   │
│  │   /api/...       │  │ Router           │  │   + stemtrace      │   │
│  │                  │  │ /stemtrace/... │  │   (signals)          │   │
│  └──────────────────┘  └────────┬─────────┘  └──────────┬───────────┘   │
│                                 │                       │                │
│                          ┌──────▼──────┐                │                │
│                          │  Consumer   │◄───────────────┘                │
│                          │(background) │     events                      │
│                          └──────┬──────┘                                 │
│                                 │                                        │
│                          ┌──────▼──────┐                                 │
│                          │ Graph Store │                                 │
│                          └──────┬──────┘                                 │
│                                 │                                        │
│                          ┌──────▼──────┐                                 │
│                          │  React UI   │                                 │
│                          └─────────────┘                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

## Core Patterns

### Hexagonal Architecture (Ports & Adapters)

See `.cursor/rules/architecture.mdc` for detailed module boundary rules and diagrams.

**Key rules:**
- `core/` has no external dependencies except Pydantic
- `library/` and `server/` import only from `core/`
- Never import sideways (library ↔ server)

### Data Flow

```
Task Execution → Signal Handlers → Event Creation → Transport → Broker
                                                                   ↓
UI ← API ← Graph Builder ← Consumer ←──────────────────────────────┘
```

## Data Models

| Model | Type | Key Fields |
|-------|------|------------|
| `TaskEvent` | Immutable | task_id, name, state, timestamp, parent_id, root_id, trace_id, retries, args, kwargs, result, exception, traceback |
| `TaskNode` | Mutable | task_id, name, state, events[], children[], parent_id |
| `TaskGraph` | Mutable | nodes{}, root_ids[] |

See `core/events.py` and `core/graph.py` for implementations.

## Celery Canvas Patterns

### Event Fields from Celery

| Field | Source | Description | Status |
|-------|--------|-------------|--------|
| `task_id` | `task.request.id` | Unique identifier | ✅ Captured |
| `parent_id` | `task.request.parent_id` | Direct parent (chains, subtasks) | ✅ Captured |
| `root_id` | `task.request.root_id` | Original workflow root | ✅ Captured |
| `group_id` | `task.request.group` | Shared by group/chord members | ✅ Captured |

Synthetic GROUP and CHORD nodes are created automatically when tasks share a `group_id`.

### TaskEvent Data Capture

| Field | Captured In | Notes |
|-------|-------------|-------|
| `args` | PENDING, STARTED | Positional args (scrubbed) |
| `kwargs` | PENDING, STARTED | Keyword args (scrubbed) |
| `result` | SUCCESS | Return value (scrubbed) |
| `exception` | FAILURE, RETRY | Exception message |
| `traceback` | FAILURE, RETRY | Full traceback string |

### Signal Handlers & Bootsteps

| Mechanism | State | Fires On |
|-----------|-------|----------|
| `task_sent` signal | PENDING | Client (when `.delay()` called) |
| `ReceivedEventStep` bootstep | RECEIVED | Worker (when task message received) |
| `task_prerun` signal | STARTED | Worker (before execution) |
| `task_postrun` signal | SUCCESS | Worker (after execution) |
| `task_failure` signal | FAILURE | Worker (unhandled exception) |
| `task_retry` signal | RETRY | Worker (retry requested) |
| `task_revoked` signal | REVOKED | Worker (task cancelled) |

**Note:** PENDING and RECEIVED only emit once per task (not for retry re-queues).

### Worker Lifecycle Signals 🆕

Celery provides signals for worker lifecycle events:

| Signal | When | Data Available |
|--------|------|----------------|
| `worker_ready` | Worker online | hostname, pid |
| `worker_shutdown` | Graceful shutdown | hostname |
| `worker_process_init` | Pool process started | - |
| `worker_process_shutdown` | Pool process stopped | - |

**Capturing worker lifecycle** enables:
1. Registry tracking (which tasks each worker knows about)
2. Interrupted task detection (STARTED when worker shut down)
3. Session segmentation (group tasks by worker session)

### Task Anomaly Detection

| Anomaly | Detection | Resolution |
|---------|-----------|------------|
| Unregistered | PENDING task name not in any worker's registry | Fix task import, redeploy worker |
| Stuck PENDING | PENDING > timeout, task IS registered | Check worker health, queue backlog |
| Interrupted | STARTED when worker SHUTDOWN | Task may requeue (if acks_late) or lost |
| Stuck STARTED | STARTED > timeout, no completion | Worker crashed without shutdown signal |

### Unregistered Task Edge Case

When a task is submitted but no worker has it registered:

```
Client: task.delay() → task_sent fires → PENDING event ✓
Worker: receives message → KeyError in Celery internals → NO signals fire
Result: Task stuck in PENDING forever with no error visibility
```

**Detection approach:** Capture registered tasks via `worker_ready` signal. On each PENDING event, cross-check against global registry. See Phase 8 + 8.5 in `progress.md`.

### Interrupted Task Edge Case

When a worker shuts down with tasks in-flight:

```
Task: STARTED → worker receives SIGTERM → worker_shutdown fires
Result: Task stuck in STARTED forever (unless acks_late=True)
```

**Detection approach:** On WORKER_SHUTDOWN event, find all tasks in STARTED state for that worker → mark as INTERRUPTED. See Phase 8 in `progress.md`.

### Sensitive Data Scrubbing

Sentry-style scrubbing in `library/scrubbing.py`:
- Case-insensitive partial matching (e.g., `user_password` matches `password`)
- Default keys: password, api_key, token, secret, credit_card, etc.
- Configurable via `additional_sensitive_keys` and `safe_keys`

## Broker-Agnostic Transport

| Broker | Transport | Mechanism | Status |
|--------|-----------|-----------|--------|
| Redis | `RedisTransport` | Redis Streams (XADD/XREAD) | ✅ Implemented |
| RabbitMQ | `RabbitMQTransport` | Fanout exchange | 🚧 Planned |
| Memory | `MemoryTransport` | In-process (testing) | ✅ Implemented |

Auto-detection from URL scheme:
```python
def get_transport(url: str) -> EventTransport:
    scheme = urlparse(url).scheme  # "redis", "amqp", etc.
    return TRANSPORTS[scheme].from_url(url)
```

## FastAPI Integration

```python
from stemtrace.server import StemtraceExtension

# Recommended: Full extension with embedded consumer
flow = StemtraceExtension(broker_url="redis://localhost:6379/0")
app = FastAPI(lifespan=flow.lifespan)
app.include_router(flow.router, prefix="/stemtrace")
```

### Consumer Modes

| Mode | Use Case | Graph Store |
|------|----------|-------------|
| **Embedded** | Development, simple apps | In-memory, shared with API |
| **External** | Production, scale | Shared via Redis/API |

### Authentication

Auth via FastAPI dependency injection:
```python
router = create_router(broker_url="...", auth_dependency=Depends(require_admin))
```

## Error Handling

**Fire-and-forget publishing** — never block the Celery task:
```python
def publish(self, event: TaskEvent) -> None:
    try:
        self._transport.send(event)
    except TransportError:
        logger.warning("Failed to publish event", exc_info=True)
        # Continue - dropped events are acceptable
```

## Testing

See `.cursor/rules/testing.mdc` for testing standards including:
- Test organization (unit/integration/e2e)
- Fakes over mocks pattern
- Naming conventions and fixtures

## Graph Node Display

Each node in the graph visualization shows:
- Task ID (first 8 chars)
- Task name (last segment after `.`)
- State badge (color-coded)
- Start time (when task began)
- Duration (execution time)

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Framework | React SPA | Interactive graphs, pre-built (no runtime Node.js) |
| UI Routing | TanStack Router | Type-safe, file-based routing |
| UI State | TanStack Query | Server state caching, auto-refetching |
| Graph Visualization | react-flow | Interactive DAG visualization |
| FastAPI Integration | Pluggable router | Most users already have FastAPI |
| Consumer Model | Hybrid | Embedded for dev, external for production |
| Auth | Flexible | Built-in basic auth + user's `Depends()` |
| Redis Transport | Redis Streams | Durable, ordered, supports consumer groups |
| Config Model | Frozen Pydantic | Immutable after init(), easy validation |
| Real-time Updates | WebSocket | Push-based, invalidates TanStack Query cache |
