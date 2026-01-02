# Project Structure: stemtrace

## Directory Tree

```
stemtrace/
│
├── 📁 .context/                    # Project context (Memory Bank)
│   ├── project-brief.md            # Foundation document
│   ├── product-context.md          # Why, problems, UX goals
│   ├── active-context.md           # Current focus, next steps
│   ├── system-patterns.md          # Architecture, design patterns
│   ├── tech-context.md             # Stack, tools, configuration
│   ├── progress.md                 # Task tracking
│   └── project-structure.md        # This file
│
├── 📁 .cursor/
│   └── 📁 rules/                   # Cursor AI rules
│       ├── project.mdc             # General project rules
│       ├── python.mdc              # Python-specific rules
│       ├── architecture.mdc        # Architecture rules
│       ├── testing.mdc             # Testing standards
│       ├── workflow.mdc            # Development workflow
│       ├── open-source.mdc         # OSS standards
│       └── ui-websocket.mdc        # React/WebSocket rules
│
├── 📁 .github/
│   ├── dependabot.yml              # Automated dependency updates
│   └── 📁 workflows/               # GitHub Actions
│       ├── ci.yml                  # Test, lint, type check
│       ├── e2e.yml                 # E2E tests (Docker + Playwright)
│       └── release.yml             # PyPI & Docker publish
│
├── 📁 src/
│   └── 📁 stemtrace/             # Main package
│       ├── __init__.py             # Public API: init()
│       ├── py.typed                # PEP 561 type marker
│       │
│       ├── 📁 core/                # Domain layer (pure Python)
│       │   ├── __init__.py
│       │   ├── events.py           # TaskEvent, TaskState
│       │   ├── graph.py            # TaskNode, TaskGraph
│       │   ├── ports.py            # Protocol definitions
│       │   └── exceptions.py       # Domain exceptions
│       │
│       ├── 📁 library/             # Library component
│       │   ├── __init__.py
│       │   ├── signals.py          # Celery signal handlers
│       │   ├── bootsteps.py        # Worker bootsteps (RECEIVED events)
│       │   ├── config.py           # Configuration handling
│       │   ├── scrubbing.py        # Sensitive data scrubbing
│       │   └── 📁 transports/      # Broker-agnostic transports
│       │       ├── __init__.py     # get_transport() factory
│       │       ├── redis.py        # Redis Streams transport
│       │       └── memory.py       # In-memory (testing)
│       │
│       └── 📁 server/              # Server component
│           ├── __init__.py         # Public exports
│           ├── __main__.py         # CLI: stemtrace server
│           ├── consumer.py         # EventConsumer, AsyncEventConsumer
│           ├── store.py            # GraphStore (thread-safe)
│           ├── websocket.py        # WebSocketManager
│           │
│           ├── 📁 fastapi/         # FastAPI integration
│           │   ├── __init__.py     # create_router, StemtraceExtension
│           │   ├── router.py       # Router factory
│           │   ├── extension.py    # Full extension with lifespan
│           │   └── auth.py         # require_basic_auth, require_api_key
│           │
│           ├── 📁 api/             # REST endpoints
│           │   ├── __init__.py
│           │   ├── routes.py       # Task, graph, health endpoints
│           │   ├── schemas.py      # Pydantic response models
│           │   └── websocket.py    # WebSocket endpoint
│           │
│           └── 📁 ui/              # React SPA
│               ├── __init__.py
│               ├── static.py       # Static file serving
│               └── 📁 frontend/    # React source
│                   ├── package.json
│                   ├── vite.config.ts
│                   ├── tsconfig.json
│                   ├── index.html
│                   ├── playwright.config.ts  # E2E test config
│                   ├── 📁 src/
│                   │   ├── main.tsx
│                   │   ├── index.css
│                   │   ├── 📁 routes/      # TanStack Router
│                   │   ├── 📁 components/  # React components
│                   │   ├── 📁 hooks/       # Custom hooks
│                   │   └── 📁 api/         # API client
│                   └── 📁 tests/           # Playwright E2E specs
│                       ├── tasks.spec.ts
│                       ├── task-detail.spec.ts
│                       ├── graphs.spec.ts
│                       └── registry.spec.ts
│
├── 📁 tests/
│   ├── conftest.py                 # Shared fixtures
│   ├── 📁 unit/                    # Unit tests (no I/O)
│   ├── 📁 integration/             # Integration tests
│   └── 📁 e2e/                     # End-to-end tests
│
├── 📁 examples/                    # Example usage
│   ├── celery_app.py               # Sample Celery app
│   ├── fastapi_integration.py      # Basic FastAPI setup
│   └── with_auth.py                # With authentication
│
├── build_ui.py                     # Hatchling UI build hook
├── pyproject.toml                  # Project config (PEP 621)
├── Makefile                        # Development shortcuts
├── Dockerfile                      # Production server image
├── Dockerfile.e2e                  # E2E test worker image
├── docker-compose.yml              # Development environment
├── docker-compose.e2e.yml          # E2E test environment
├── LICENSE                         # MIT
├── README.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Module Dependency Rules

See `.cursor/rules/architecture.mdc` for module boundary rules and diagrams.
