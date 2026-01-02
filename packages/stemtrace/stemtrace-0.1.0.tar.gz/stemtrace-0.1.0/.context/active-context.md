# Active Context: stemtrace

## Current Focus

**Phase 7 Complete - Ready for v0.1.0 Release**

Canvas Graph Reconstruction (group_id capture, synthetic GROUP nodes) implemented and tested. All checks passing. Ready to tag and release.

## Phase 7: Canvas Graph Reconstruction ✅

1. [x] Add `group_id` field to TaskEvent model
2. [x] Capture `group_id` from `task.request.group` in signal handlers
3. [x] Capture `group_id` from message headers in bootsteps
4. [x] Add `NodeType` enum (TASK/GROUP/CHORD) to core/graph.py
5. [x] Add `node_type` and `group_id` fields to TaskNode model
6. [x] Implement synthetic GROUP node generation in TaskGraph.add_event()
7. [x] Add `node_type` and `group_id` to API response schemas
8. [x] Render GROUP nodes with distinct styling in TaskGraph.tsx
9. [x] Show start time and duration in graph node labels
10. [x] Unit tests for group detection and synthetic node creation (41 graph tests)
11. [x] Integration tests for synthetic group nodes (15 FastAPI tests)

## Release Checklist

1. [ ] Tag v0.1.0: `git tag v0.1.0 && git push origin v0.1.0`
2. [ ] Configure PyPI trusted publishing
3. [ ] Verify GitHub release automation

## Strategic Direction

> **stemtrace models Celery as a graph of executions derived from events.**

See `progress.md` for full strategic principles.  
See `strategic-analysis.md` for competitive positioning and roadmap priorities.

## Roadmap Overview

| Phase | Focus | Status |
|-------|-------|--------|
| 6 | UX/DX Enhancements | ✅ Complete |
| Pre-Release | E2E Testing (Docker + Playwright) | ✅ Complete |
| 7 | Canvas Graph Reconstruction (group_id, synthetic nodes) | ✅ Complete |
| v0.1.0 | Release | **Current** |
| 8 | Execution & Worker Lifecycle (worker events, registry capture) | Planned |
| 8.5 | Anomaly Detection (unregistered, stuck, interrupted tasks) | Planned 🆕 |
| 9 | UI reorganization (Dashboard + Executions + Registry) | Planned |
| 10 | Export & Integration (OpenTelemetry, webhooks) | Planned |
| 11 | RabbitMQ + documentation polish | Planned |

See `progress.md` for detailed task lists.

## Project State

| Metric | Value |
|--------|-------|
| Tests | All passing (350+ Python tests + Playwright E2E) |
| Coverage | 90%+ |
| Python | 3.10+ |
| Status | Ready for v0.1.0 release |

## Competitive Position

vs. Kanchi (see `strategic-analysis.md` for full breakdown):

**Our Strengths:**
- **Zero infrastructure** — No PostgreSQL requirement, uses existing Redis
- **Flow-first** — DAG visualization is the killer feature Kanchi lacks
- **FastAPI embedding** — Mount in existing app
- **Read-only** — Safe for production
- **Canvas awareness** — Synthetic GROUP/CHORD nodes

**Gaps to Close:**
- Anomaly detection (Phase 8.5) — #1 priority for production adoption
- Worker lifecycle (Phase 8) — Prerequisite for anomaly detection
- Dashboard (Phase 9) — First-impression UX
- RabbitMQ (Phase 11) — Unlocks half the Celery user base

## What's New in Phase 7

### group_id Capture
Events now capture `group_id` from Celery task requests, enabling tracking of tasks spawned via `group()` and `chord()`.

### Synthetic GROUP & CHORD Nodes
When 2+ tasks share the same `group_id`, a synthetic GROUP node is automatically created:
- GROUP nodes are roots in the graph
- Member tasks become children of the GROUP node
- GROUP state is computed from member states (all SUCCESS = SUCCESS, any FAILURE = FAILURE, etc.)
- When a group has a callback (chord), GROUP is upgraded to CHORD with callback linking

### UI Enhancements
- GROUP nodes rendered with dashed indigo borders
- CHORD nodes rendered with dashed purple borders
- Task nodes show start time and duration directly in the graph
- Clear visual distinction between TASK, GROUP, and CHORD node types

## Known Issues

### Task Visibility Gaps

Three scenarios where tasks get "stuck" with no clear indication to users:

| Scenario | What User Sees | Root Cause |
|----------|----------------|------------|
| Unregistered task | PENDING forever | Worker can't find task, KeyError before signals |
| Worker crash | STARTED forever | No shutdown signal, no completion event |
| Worker graceful stop | STARTED (maybe) | Depends on acks_late config |

**Planned fix:** Phase 8 (worker lifecycle) + Phase 8.5 (anomaly detection)

### Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 8: Worker Lifecycle Events                            │
│ - Capture worker_ready (hostname, pid, registered_tasks)    │
│ - Capture worker_shutdown                                   │
│ - Build global registry from all workers                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 8.5: Anomaly Detection                                │
│ - Unregistered: PENDING task not in any registry           │
│ - Stuck: PENDING/STARTED > timeout                          │
│ - Interrupted: STARTED when worker SHUTDOWN                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ UI: Visibility                                              │
│ - Warning badges on anomalous tasks                         │
│ - Worker session timeline markers                           │
│ - "2 new tasks registered" on worker restart                │
└─────────────────────────────────────────────────────────────┘
```

See `progress.md` → Phase 8 and 8.5 for detailed task lists.

## Known Blockers

None.
