# Project Brief: stemtrace

## Overview

**stemtrace** is a lightweight, open-source Celery task flow visualizer that helps developers debug complex workflows by showing task graphs, timelines, retries, and parent-child relationships.

## Core Problem

Existing Celery monitoring tools (Flower, Prometheus+Grafana, OpenTelemetry) answer "what exists" but fail to answer **"what happened"**:

- **Flower**: Basic task list, no real graph, no causal view, useless for debugging complex workflows
- **Prometheus+Grafana**: Great metrics for SREs, but not task-centric, no per-execution visibility
- **OpenTelemetry**: Heavy setup, vendor lock-in, overkill for many teams

Teams end up writing ad-hoc tables, dumping task metadata to Postgres, and hacking UIs — a clear pain signal.

## Solution

A two-component architecture:

1. **Library** (`stemtrace`): Installed in Celery projects, hooks into signals, sends events to the broker. Zero overhead, fire-and-forget.

2. **Server** (`stemtrace server`): Separate container that reads events, builds task graphs, serves a read-only web UI. Safe for production.

## Core Features (MVP)

- Task lifecycle tracking via Celery signals
- Task list with filtering (by name, status)
- Single execution view (timeline, retries, errors)
- Simple task graph visualization (parent → children)
- **Broker-agnostic** event transport (Redis, RabbitMQ, etc.)
- Event storage with TTL

## Key Differentiators

- **Complements Flower**, doesn't compete
- **Broker-agnostic** — works with Redis, RabbitMQ, and other Celery brokers
- **Zero config happy path** — auto-detects broker from Celery config
- **Read-only** — safe for production
- **Lightweight** — no heavy dependencies, no vendor lock-in

## Target Users

- Python developers using Celery for background tasks
- Teams with complex task workflows (chains, groups, chords)
- Anyone debugging "why did this task fail?" or "what triggered this?"

## Success Criteria

- Easy to install (`pip install stemtrace`)
- Works in < 5 minutes with existing Celery setup
- Provides clear visibility into task flows
- Good enough UX to earn GitHub stars

## Technical Constraints

- Python 3.10+
- Celery 5.x support
- **Broker-agnostic** event transport (Redis, RabbitMQ, with extensible registry)
- Strict typing (mypy strict mode)
- Clean architecture patterns

## Open Source Goals

- MIT License
- Clear contribution guidelines
- Comprehensive documentation
- CI/CD with GitHub Actions
- Published to PyPI and Docker Hub/GHCR

