# Strategic Analysis: stemtrace Positioning

**Date:** 2025-12-29  
**Context:** Independent assessment of stemtrace vs competitors (Kanchi)

---

## Competitive Landscape

### stemtrace Strengths

| Strength | Description |
|----------|-------------|
| **Flow visualization** | DAG reconstruction for groups, chords, chains — unique differentiator |
| **Zero infrastructure** | Uses existing Redis, no PostgreSQL required |
| **FastAPI embedding** | Mount directly in existing apps |
| **Read-only** | Safe for production, no task control side effects |
| **Canvas awareness** | Synthetic GROUP/CHORD nodes for visual grouping |
| **Lightweight** | Single binary, minimal dependencies |

### stemtrace Gaps (vs Kanchi)

| Gap | Impact | Resolution |
|-----|--------|------------|
| No anomaly detection | Users can't tell when tasks are stuck/orphaned | Phase 8 + 8.5 |
| No worker lifecycle | Can't detect worker crashes or unregistered tasks | Phase 8 |
| No dashboard | First impression is a task list, not actionable insights | Phase 9 |
| Redis-only | RabbitMQ users locked out | Phase 11 |

### Kanchi Strengths

- Full-featured production monitoring (workers, queues, health)
- Orphan detection out of the box
- PostgreSQL persistence for long-term analytics
- Slack integration, workflow automation
- Broker-agnostic (Redis + RabbitMQ)

### Kanchi Weaknesses (vs stemtrace)

- Heavier footprint (requires database, Next.js frontend)
- No canvas graph reconstruction
- Monitoring-focused, not visualization-focused
- More complex deployment

---

## Strategic Positioning

> **stemtrace models Celery as a graph of executions derived from events.**

### Target Personas

1. **Debugging Developer** — "Why did this chord callback never fire?"
2. **Platform Engineer** — "I want lightweight monitoring without adding PostgreSQL"
3. **FastAPI Team** — "I want task visibility embedded in my existing app"

### Non-Targets

- Ops teams needing PagerDuty/Slack alerting (use existing monitoring stacks)
- Compliance teams needing 7-year retention (use OTEL export → proper observability)
- Teams wanting task control (retry/revoke) — stays read-only

---

## Priority Roadmap

### Tier 1: Critical for Production Adoption

| Phase | Feature | Why Critical |
|-------|---------|--------------|
| 8 | Worker Lifecycle | Prerequisite for anomaly detection |
| 8.5 | Anomaly Detection | Users need to know when things break |
| 10 | OTEL + Webhook Export | Long-term analytics via external tools |

### Tier 2: Competitive Parity

| Phase | Feature | Why Important |
|-------|---------|---------------|
| 9 | Dashboard Page | First-impression UX, actionable insights |
| 11 | RabbitMQ Support | Unlocks half the Celery user base |

### Tier 3: Differentiation (Extend the Lead)

| Feature | Description |
|---------|-------------|
| Nested canvas visualization | Chain inside group, group inside chord |
| Time-travel replay | Scrub through execution timeline |
| Diff mode | Highlight slow paths vs baseline |
| pytest-stemtrace | Visualize flows from tests |

---

## Persistence Strategy

### Current: Redis Streams with TTL

- Events persist in Redis with configurable TTL (default 24h)
- In-memory GraphStore rebuilt from Redis on startup
- Zero additional infrastructure required

### Assessment

✅ **Sufficient for primary use case** — Debugging recent workflows  
✅ **Aligns with "zero-infra" positioning**  
✅ **Simple operational model**

### Long-Term Retention

**Decision:** Do NOT add PostgreSQL/SQLite as core persistence.

**Rationale:**
1. Dilutes "zero-infra" positioning
2. Two storage backends = double maintenance burden
3. OTEL export solves long-term analytics better
4. If someone needs 30-day retention, they need proper observability tooling

**If demand emerges:** SQLite archive (append-only, file-based) is the only acceptable option:
- Preserves "no extra services" story
- Separate from live GraphStore
- New `/api/history` endpoints for archived data
- Enable via `--archive-db ./stemtrace.db`

**Priority:** Low. Ship OTEL export first. If users still ask for SQLite after that, reassess.

---

## Strategic "Won't Do"

| Feature | Reason |
|---------|--------|
| Task control (retry/revoke) | Stays read-only, safe in production |
| Alerting (PagerDuty/Slack) | Users have existing monitoring stacks |
| Workflow automation | Not an ops platform |
| PostgreSQL persistence | Zero-infra is the differentiator |

---

## Release Roadmap

```
v0.1.0 (Current)
├── Canvas graph reconstruction ✅
├── Synthetic GROUP/CHORD nodes ✅
└── Timing display in graphs ✅

v0.2.0 (Production-Ready)
├── Phase 8: Worker Lifecycle
├── Phase 8.5: Anomaly Detection
└── Phase 10: OTEL + Webhook Export

v0.3.0 (Competitive Parity)
├── Phase 9: Dashboard Page
└── Phase 11: RabbitMQ Support

v1.0.0 (Stability)
├── Nested canvas visualization
├── Battle-testing
└── Documentation polish
```

---

## Key Insight

> The flow visualization is the moat. Kanchi can't easily replicate it. But production teams won't adopt without anomaly detection. Ship Phase 8/8.5, and stemtrace becomes a compelling alternative. Ship the dashboard, and you win on DX.

---

## References

- [Kanchi](https://kanchi.io/) — Primary competitor
- [stemtrace GitHub](https://github.com/iansokolskyi/stemtrace)
- See `progress.md` for detailed task lists per phase

