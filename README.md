# gh-issues-local

A local implementation of the GitHub Issues API built with FastAPI.
Runs locally or in a container, with an optional web UI and token-based auth for network access.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [Node.js](https://nodejs.org/) 20+ with [pnpm](https://pnpm.io/) (for the web UI; enable via `corepack enable`)

## Quick Start

```bash
uv run gh-issues-local
```

Opens on http://127.0.0.1:8000 with auth disabled.

To serve the React web UI, use production mode (downloads a pre-built frontend from GitHub Releases):

```bash
uv run gh-issues-local --production
```

Or build the frontend locally:

```bash
cd web && pnpm install && pnpm build && cd ..
uv run gh-issues-local
```

## API

The target API surface is defined in [docs/ISSUES_SPEC.md](docs/ISSUES_SPEC.md). Swagger docs are served at `/docs` when the server is running.

## Storage

Issue data is persisted through the [storage-provider](https://github.com/DavidKoleczek/storage-provider) abstraction. The server reads config from `$GH_ISSUES_LOCAL_DATA_DIR` (defaults to `$HOME`).

Required config files in the data directory:

```yaml
# .storage.yaml -- selects which storage backend
provider: local   # or: git

# .local_storage.yaml -- local backend config
root_path: ./storage

# .git_storage.yaml -- git backend config (if provider: git)
repo_path: ./data
remote_url: null
auto_sync: true
```

The `create_storage()` factory reads `.storage.yaml` and instantiates the matching provider. Swap between `local` and `git` backends by changing the config -- no code changes needed.

Data layout inside the storage root:

```
repos/{owner}/{repo}/
  counter.txt
  issues/{number}/
    issue.json
```

## Auth

Auth is **off** when bound to `127.0.0.1` (the default) and **on** when bound to any other address.

| Flag | Effect |
|------|--------|
| `--host 0.0.0.0` | Bind to all interfaces, enables auth |
| `--no-auth` | Explicitly disable auth on any bind address |
| `--port PORT` | Listen on a different port (default: 8000) |
| `--production` | Download frontend from GitHub Releases, bind to `0.0.0.0` |
| `--update-frontend` | Force re-download of the frontend build (implies `--production`) |

When auth is enabled a random token is generated and stored in `~/.gh-issues-local-token`
(or `$GH_ISSUES_LOCAL_DATA_DIR/.gh-issues-local-token` if the env var is set).
All Issues API endpoints require a `Bearer` token when auth is enabled. Infrastructure endpoints (`/`, `/api/health`, `/api/auth/status`, `/api/auth/verify`) are always public.

## Development

Backend only (no frontend hot-reload):

```bash
uv sync
uv run uvicorn gh_issues_local.app:create_app --factory --reload
```

Full-stack with frontend hot-reload (two terminals):

```bash
# Terminal 1 -- FastAPI backend
uv run uvicorn gh_issues_local.app:create_app --factory --reload

# Terminal 2 -- Vite dev server with API proxy
cd web && pnpm install && pnpm dev
```

Open http://localhost:5173 for the React UI with hot module reload. API calls are proxied to the FastAPI server on port 8000.

When the frontend is built (`web/dist/` exists), FastAPI serves it as a single-page app at `/` with client-side routing support. The `GH_ISSUES_LOCAL_FRONTEND_DIR` env var can override the frontend directory path.

## Git Hooks

This project uses [prek](https://github.com/j178/prek) for git hooks. See [`.pre-commit-config.yaml`](.pre-commit-config.yaml) for the full configuration.

Install prek and set up the hooks:

```bash
uv tool install prek
prek install
```

Run all hooks manually:

```bash
prek run --all-files
```

### Smoke Test

Run the end-to-end smoke test to verify the server works across both auth modes:

```bash
uv run python scripts/smoke_test.py
```

This starts the server twice (no-auth and auth-enabled), hits every endpoint, and prints pass/fail results. The test creates isolated temp directories with storage config files so runs are repeatable.

### Code Quality

Format code:

```bash
uv run ruff format
```

Lint code:

```bash
uv run ruff check --fix
```

Type check:

```bash
uv run ty check
```
