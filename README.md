# gh-issues-local

A local implementation of the GitHub Issues API built with FastAPI.
Runs locally or in a container, with an optional web UI and token-based auth for network access.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Quick Start

```bash
uv run gh-issues-local
```

Opens on http://127.0.0.1:8000 with auth disabled.

## Auth

Auth is **off** when bound to `127.0.0.1` (the default) and **on** when bound to any other address.

| Flag | Effect |
|------|--------|
| `--host 0.0.0.0` | Bind to all interfaces, enables auth |
| `--no-auth` | Explicitly disable auth on any bind address |
| `--port PORT` | Listen on a different port (default: 8000) |

When auth is enabled a random token is generated and stored in `~/.gh-issues-local-token`
(or `$GH_ISSUES_LOCAL_DATA_DIR/.gh-issues-local-token` if the env var is set).
The web UI will prompt for the token and store it in browser localStorage.

## Development

```bash
uv sync
uv run fastapi dev src/gh_issues_local/app.py
```

This starts the server with auto-reload for development.

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

This starts the server twice (no-auth and auth-enabled), hits every endpoint, and prints pass/fail results.

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
