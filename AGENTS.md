# General Instructions

- DO NOT make any commits or pushes to any repos without the user's explicit permission.
- Before commit and pushing, make sure under all circumstances that no secrets or private information is being committed.
- Shortcuts are not appropriate. When in doubt, you must work with the user for guidance.
- Anything is possible. Do not blame external factors after something doesn't work on the first try. Instead, investigate and test assumptions through debugging through first principles.
- Keep the README up to date with any changes to the app's user facing interfaces, features, or usage instructions. Keep it short, concise, and in the existing style.
- Make sure any comments in code are necessary. A necessary comment captures intent that cannot be encoded in names, types, or structure. Comments should be reserved for the "why", only used to record rationale, trade-offs, links to specs/papers, or non-obvious domain insights. They should add signal that code cannot.
- When writing documentation
  - Keep it very concise
  - No emojis or em dashes.
  - Documentation should be written exactly like it is for production-grade, polished, open-source applications.

# Dependency Context
- For libraries that are new to you or change frequently, you must refer to their official documentation or source code.
- There is a select set of repos cloned that constitute the dependencies for this project at `ai_working`. You must explore it directly when needed. It can be updated through the Claude command `/setup-reference-repos`  in this project.
  - `amplifier` - To understand the development environment. **Important** the architecture is highly modular, spread across multiple repos. You can discover the repos at `amplifier/docs/MODULES.md` and clone them as needed.
  - `rest-api-description` - GitHub's official OpenAPI descriptions for the REST API. This is the reference spec for the Issues API.
- When looking for something specific that might take a while, use a sub-agent to find it. Tell the sub-agent return the location (paths) of what is found so it can be referenced easily later.
- To figure out how things like `uv` work, start by using `uv --help`. This is a general pattern.

# Smoke Tests

`scripts/smoke_test.py` is the e2e smoke test for the server. It starts the server, calls every endpoint, and checks responses. It is not a unit test suite; it exists so the AI can quickly verify the server works end to end and diagnose failures from the output.
When you add, change, or remove an API endpoint, update the smoke test to cover it. The checks should mirror the real API surface: if a new route exists, there should be a check for it; if a route changes behavior, the check should match. Keep the two phases (no-auth and auth-enabled) in sync with the auth middleware's public paths list.

# Architecture

```
src/gh_issues_local/
  __init__.py       -- CLI entrypoint (argparse + uvicorn)
  app.py            -- FastAPI app factory, wires storage + routes + auth
  auth.py           -- Bearer token middleware, PUBLIC_PATHS whitelist
  frontend.py       -- Downloads pre-built frontend from GitHub Releases
  models.py         -- Pydantic request models (CreateIssueRequest, UpdateIssueRequest)
  storage.py        -- IssueStore: CRUD/list/search backed by storage-provider
  routes/
    issues.py       -- All 8 Issues -- Core endpoints
web/                -- React frontend (Vite + TypeScript + Tailwind + shadcn/ui)
  src/              -- React source (pages, components, api client, types)
  dist/             -- Build output (gitignored, created by `pnpm build`)
.github/workflows/
  build-frontend.yaml -- Builds web/ on push to main, publishes tarball as GitHub Release
```

## App Factory Pattern

`app.py` uses a **factory function** (`create_app()`), NOT a module-level `app` instance. This is required because `create_app` accepts an `auth_required` flag and initializes storage from config files that may not exist at import time.

Consequences:
- `fastapi dev` DOES NOT WORK. It requires a module-level `app` variable and cannot handle factories.
- The dev command is: `uv run uvicorn gh_issues_local.app:create_app --factory --reload`
- Do NOT add `app = create_app()` at module level in app.py. It will crash when `$HOME` lacks `.storage.yaml`.

## Storage

Storage is configured via `create_storage(config_dir=data_dir)` which reads `.storage.yaml` and the provider-specific config file from `$GH_ISSUES_LOCAL_DATA_DIR`. If no config exists, `create_app` auto-creates default local-storage config files (`_ensure_storage_config`). This is critical for the dev server startup and must not be removed.

Issues are stored as JSON files at `repos/{owner}/{repo}/issues/{number}/issue.json` with a `counter.txt` for auto-incrementing issue numbers.

## Frontend

The React frontend lives in `web/`. In dev, run the Vite dev server (`pnpm dev` in `web/`) alongside the backend; Vite proxies API requests to FastAPI on port 8000. For production, `pnpm build` outputs to `web/dist/`, and FastAPI serves it as an SPA with a catch-all route that returns `index.html` for client-side routing. The `GH_ISSUES_LOCAL_FRONTEND_DIR` env var can override the frontend directory.

A GitHub Actions workflow (`.github/workflows/build-frontend.yaml`) triggers on pushes to `main` that touch `web/**`. It builds the frontend, tarballs `dist/`, and publishes it as a rolling `frontend-latest` GitHub Release. The `frontend.py` module downloads and caches this tarball when the server is started with `--production`. The cache lives at `$GH_ISSUES_LOCAL_DATA_DIR/frontend_cache/` (or `~/frontend_cache/` by default). Use `--update-frontend` to force a re-download.

## Auth Middleware

The auth middleware (`auth.py`) uses an allowlist approach:
- `PUBLIC_PATHS`: exact paths that skip auth (`/`, `/api/health`, `/api/auth/status`, `/api/auth/verify`)
- `/assets/*`: also skips auth (Vite-built JS/CSS bundles needed to load the SPA)
- Everything else requires a Bearer token when auth is enabled

The GitHub Issues API routes (`/repos/...`, `/issues`, `/search/...`, `/orgs/...`) do NOT have an `/api` prefix because they mirror GitHub's real paths. Do not use "starts with /api" as the auth boundary.

# Key Files

@README.md
@docs/ISSUES_SPEC.md -- The target API surface. Implementation should match these endpoints.
