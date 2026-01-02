# Product Context: stemtrace

## Why This Project Exists

Celery is the de-facto standard for Python task queues, but observability into task flows is surprisingly poor. When a complex workflow fails, developers spend hours tracing what happened:

- Which task spawned this one?
- What tasks ran in parallel?
- Where did the chain break?
- Which retry actually succeeded?

**stemtrace exists to answer these questions instantly.**

## Problems It Solves

### 1. "Why is this task slow/stuck?"
Show the timeline: when it was queued, when picked up, how long in each state.

### 2. "What spawned this task?"
Display parent-child relationships, trace back to the originating request.

### 3. "What tasks fan-out / fan-in?"
Visualize groups and chords as a DAG, not just a flat list.

### 4. "Which retries actually happened?"
Show retry count, timing, and failure reasons for each attempt.

### 5. "What happened for this one request end-to-end?"
Correlate all tasks triggered by a single API request via trace_id.

## How It Should Work

### For the Developer (Library User)

```python
from stemtrace import init
init(app)  # Done. That's it.
```

- Zero configuration required
- No code changes to existing tasks
- No performance impact (fire-and-forget)

### For the FastAPI User (Pluggable Integration)

```python
from fastapi import FastAPI
from stemtrace.server import StemtraceExtension

flow = StemtraceExtension(broker_url="redis://localhost:6379/0")
app = FastAPI(lifespan=flow.lifespan)
app.include_router(flow.router, prefix="/stemtrace")
```

- Mount directly into existing FastAPI app
- No separate server to deploy
- Leverage existing auth middleware
- Optional embedded consumer (background task)

### For the Observer (UI User)

1. Open the web UI (standalone or mounted at `/stemtrace`)
2. See a list of recent task executions
3. Click on any task to see:
   - Full execution timeline
   - Parent/child relationships
   - Retry history with full exception details
   - Task arguments and return values
   - Sensitive data automatically scrubbed (passwords, API keys, etc.)
4. View flow graphs for complex workflows
5. Browse the Task Registry to see all discovered task definitions

## User Experience Goals

### Simplicity
- Install in < 5 minutes
- No infrastructure changes (reuse existing broker)
- Sensible defaults, optional configuration
- **Plug into existing FastAPI** — no new containers

### Clarity
- Clear visual hierarchy
- Obvious state indicators (pending, running, success, failure)
- No information overload
- **React-based UI** — responsive, interactive graphs

### Safety
- Read-only by design
- Never interferes with task execution
- Can be deployed/removed without affecting production
- **Flexible auth** — use your existing FastAPI auth or built-in defaults

### Flexibility
- **Standalone server** — run separately via CLI
- **FastAPI plugin** — mount as a router in your app
- **Hybrid consumer** — embedded background task or separate process

## Positioning

| Tool | Focus | stemtrace's Relationship |
|------|-------|---------------------------|
| Flower | Worker status, task list | Complements (we show flows) |
| Prometheus | Metrics, alerting | Complements (we show executions) |
| Sentry | Error tracking | Complements (we show context) |
| Jaeger/Zipkin | Distributed tracing | Alternative (simpler, Celery-specific) |

**We don't replace monitoring. We add understanding.**

