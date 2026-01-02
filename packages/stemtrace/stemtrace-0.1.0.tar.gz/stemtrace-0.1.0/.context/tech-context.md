# Tech Context: stemtrace

## Technology Stack

### Core Runtime
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.10+ | Modern typing, pattern matching |
| Task Queue | Celery | 5.x | Target integration |
| Data Models | Pydantic | 2.x | Validation, serialization |
| Event Transport | **Broker-agnostic** | - | Redis, RabbitMQ, etc. |

### Server Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | FastAPI | REST API, async support, pluggable router |
| CLI Framework | Typer | Modern CLI with type hints |
| ASGI Server | Uvicorn | Production server |
| UI Framework | React | Interactive SPA dashboard |
| Build Tool | Vite | Fast React bundling |
| Static Serving | `importlib.resources` | Bundled assets from package |

### Development Tools
| Tool | Purpose | Configuration |
|------|---------|---------------|
| mypy | Static type checking | Strict mode |
| ruff | Linting + formatting | Single tool for both |
| pytest | Testing | With pytest-asyncio |
| pre-commit | Git hooks | Enforce standards |
| uv | Package management | Fast, modern |

### CI/CD
| Tool | Purpose |
|------|---------|
| GitHub Actions | CI pipeline |
| PyPI | Package distribution |
| GHCR | Docker images |

## Python Version Requirements

**Minimum: Python 3.10**

Reasons:
- `match` statements for cleaner code
- `ParamSpec` and `TypeVarTuple` for better typing
- Union syntax with `|` operator
- Improved error messages

## Dependencies

See `pyproject.toml` for all dependencies. Key optional extras:
- `rabbitmq` - RabbitMQ transport (pika)
- `dev` - Development tools (mypy, ruff, pytest, etc.)

## Parameter Naming Convention

| Component | Parameter | Notes |
|-----------|-----------|-------|
| `init()` | `transport_url` | Library-side event transport URL |
| `StemtraceExtension` | `broker_url` | Server-side broker connection URL |

Both refer to the same connection URL (e.g., `redis://localhost:6379/0`). The different names reflect their context: library "transports" events, server "consumes" from broker.

## Project Structure

See [project-structure.md](project-structure.md) for full directory layout.

Key modules:
- `core/` - Pure domain logic (no external deps)
- `library/` - Celery integration, transports
- `server/` - FastAPI, API, UI

## Tool Configuration

All tool configs (mypy, ruff, pytest, coverage) are in `pyproject.toml`.

## Testing Strategy

| Category | Location | Purpose |
|----------|----------|---------|
| Unit | `tests/unit/` | Core domain logic, no I/O |
| Integration | `tests/integration/` | Redis, Celery signal handling |
| E2E (API) | `tests/e2e/` | Docker-based API tests |
| E2E (Browser) | `frontend/tests/` | Playwright browser tests |

See `.cursor/rules/testing.mdc` for testing standards.

## Development Setup

```bash
# Clone and enter
git clone https://github.com/iansokolskyi/stemtrace.git
cd stemtrace

# Create virtual environment (using uv)
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev,server]"

# Setup pre-commit
pre-commit install

# Run checks
mypy src/
ruff check src/
pytest
```

## Docker Development

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  worker:
    build: .
    command: celery -A example.app worker --loglevel=info
    depends_on:
      - redis
  
  server:
    build: .
    command: stemtrace server
    ports:
      - "8000:8000"
    depends_on:
      - redis
```

## React UI Build Pipeline

### Directory Structure

```
src/stemtrace/server/ui/frontend/
├── package.json          # React dependencies
├── vite.config.ts        # Vite build config
├── tsconfig.json         # TypeScript config
├── postcss.config.js     # PostCSS (Tailwind configured here)
├── index.html            # Entry HTML
└── src/
    ├── main.tsx          # React entry point
    ├── index.css         # Tailwind imports
    ├── routes/           # TanStack Router file-based routes
    ├── components/       # React components
    ├── hooks/            # Custom hooks (useWebSocket)
    └── api/              # API client + TanStack Query
```

### Build Process

React UI is pre-built at **package build time** via hatchling hook:

```bash
# Triggered by: pip install . or hatch build
# See build_ui.py for implementation

cd src/stemtrace/server/ui/frontend
npm install && npm run build
# Assets output to: frontend/dist/
```

### Static File Serving

```python
# server/ui/static.py
from fastapi.staticfiles import StaticFiles

_FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"

def get_static_router() -> APIRouter | None:
    """Create router for UI static files. Returns None if dist/ missing."""
    ...
```

### Why Pre-built?

1. **No Node.js required** at runtime
2. **Faster startup** — no build step on server start
3. **Reproducible** — same assets across all deployments
4. **Smaller image** — no node_modules in Docker

## Example Applications

Located in `examples/`:

| File | Purpose |
|------|---------|
| `celery_app.py` | Main demo app with multiple task types |
| `fastapi_integration.py` | Basic FastAPI embedded setup |
| `with_auth.py` | FastAPI with authentication |

### Demo Tasks in `celery_app.py`

| Task | Demo Purpose |
|------|--------------|
| `workflow_example` | Complex chain + group workflow |
| `fetch_api_data` | Retry with real ConnectionError |
| `process_user_data` | Sensitive data scrubbing (password, credit_card) |
| `always_fails` | Permanent failure with traceback |

### Running Demos

```bash
# Start worker
celery -A examples.celery_app worker --loglevel=info

# Start server
stemtrace server

# Run specific demo
python examples/celery_app.py workflow  # Complex workflow
python examples/celery_app.py retry     # Retry demo
python examples/celery_app.py scrub     # Scrubbing demo
python examples/celery_app.py fail      # Failure demo
```

