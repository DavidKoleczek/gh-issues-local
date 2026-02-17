import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from storage_provider import create_storage

from gh_issues_local.auth import TOKEN_FILE, AuthMiddleware, ensure_token
from gh_issues_local.config import Config
from gh_issues_local.routes.comments import router as comments_router
from gh_issues_local.routes.issues import router as issues_router
from gh_issues_local.storage import IssueStore

# Built frontend output (produced by `pnpm build` in web/).
FRONTEND_DIST = Path(__file__).parents[2] / "web" / "dist"


class VerifyRequest(BaseModel):
    token: str


def _ensure_storage_config(config: Config) -> None:
    """Create .storage.yaml and .local_storage.yaml if missing.

    When config.storage is provided (from a YAML config file), write those
    values. Otherwise write the same hardcoded defaults as before.
    """
    storage_yaml = config.data_dir / ".storage.yaml"
    if storage_yaml.is_file():
        return

    if config.storage:
        # Write provider selection.
        provider = config.storage.get("provider", "local")
        storage_yaml.write_text(f"provider: {provider}\n")
        # Write provider-specific config.
        provider_config = config.storage.get(provider)
        if provider_config:
            import yaml

            provider_yaml = config.data_dir / f".{provider}_storage.yaml"
            if not provider_yaml.is_file():
                provider_yaml.write_text(yaml.dump(provider_config, default_flow_style=False))
    else:
        # No config file -- write hardcoded defaults (backward compatible).
        storage_yaml.write_text("provider: local\n")
        local_yaml = config.data_dir / ".local_storage.yaml"
        if not local_yaml.is_file():
            local_yaml.write_text("root_path: ./storage\n")


def create_app(auth_required: bool = False, config: Config | None = None) -> FastAPI:
    if config is None:
        from gh_issues_local.config import load_config

        config = load_config()

    app = FastAPI(title="GitHub Issues API", version="0.1.0")

    # Config
    app.state.config = config

    # Auth state -- set before middleware so it's available on first request.
    app.state.auth_required = auth_required
    app.state.auth_token = ensure_token() if auth_required else None
    app.state.auth_token_path = str(TOKEN_FILE)

    # Storage -- resolved from config files (.storage.yaml) in the data directory.
    # If no config exists yet, create a default local-storage setup so the
    # server can start without manual configuration.
    _ensure_storage_config(config)
    storage = create_storage(config_dir=config.data_dir)
    app.state.issue_store = IssueStore(storage)

    app.add_middleware(AuthMiddleware)  # type: ignore[invalid-argument-type]  # BaseHTTPMiddleware subclass; ty can't resolve the generic factory signature

    # -- Comments API routes (registered before issues so literal paths like
    # /issues/comments are matched before the parameterized /issues/{number}).
    app.include_router(comments_router)

    # -- Issues API routes --------------------------------------------------
    app.include_router(issues_router)

    # -- public endpoints (no auth) -----------------------------------------

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/auth/status")
    async def auth_status():
        return {"required": app.state.auth_required}

    @app.post("/api/auth/verify")
    async def auth_verify(body: VerifyRequest):
        if not app.state.auth_required:
            return {"valid": True}
        return {"valid": body.token == app.state.auth_token}

    # -- Frontend static files ----------------------------------------------
    # Serve the Vite build output as an SPA.  Static assets (JS/CSS bundles)
    # are mounted at /assets, and a catch-all GET route serves index.html
    # for all unmatched paths so client-side routing works.
    frontend_dir = Path(os.environ.get("GH_ISSUES_LOCAL_FRONTEND_DIR", str(FRONTEND_DIST)))
    if frontend_dir.is_dir():
        assets_dir = frontend_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        spa_index = frontend_dir / "index.html"

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str):
            # Don't serve the SPA shell for unknown API paths.
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")
            return FileResponse(spa_index)

    return app
