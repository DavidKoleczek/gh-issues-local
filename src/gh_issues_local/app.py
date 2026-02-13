import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from storage_provider import create_storage

from gh_issues_local.auth import TOKEN_FILE, AuthMiddleware, ensure_token
from gh_issues_local.routes.issues import router as issues_router
from gh_issues_local.storage import IssueStore

STATIC_DIR = Path(__file__).parent / "static"

# Built frontend output (produced by `pnpm build` in web/).
FRONTEND_DIST = Path(__file__).parents[2] / "web" / "dist"


class VerifyRequest(BaseModel):
    token: str


def _ensure_storage_config(data_dir: Path) -> None:
    """Create default .storage.yaml and .local_storage.yaml if missing."""
    storage_yaml = data_dir / ".storage.yaml"
    if storage_yaml.is_file():
        return
    storage_yaml.write_text("provider: local\n")
    local_yaml = data_dir / ".local_storage.yaml"
    if not local_yaml.is_file():
        local_yaml.write_text("root_path: ./storage\n")


def create_app(auth_required: bool = False) -> FastAPI:
    app = FastAPI(title="GitHub Issues API", version="0.1.0")

    # Auth state -- set before middleware so it's available on first request.
    app.state.auth_required = auth_required
    app.state.auth_token = ensure_token() if auth_required else None
    app.state.auth_token_path = str(TOKEN_FILE)

    # Storage -- resolved from config files (.storage.yaml) in the data directory.
    # If no config exists yet, create a default local-storage setup so the
    # server can start without manual configuration.
    data_dir = Path(os.environ.get("GH_ISSUES_LOCAL_DATA_DIR", str(Path.home())))
    _ensure_storage_config(data_dir)
    storage = create_storage(config_dir=data_dir)
    app.state.issue_store = IssueStore(storage)

    app.add_middleware(AuthMiddleware)  # type: ignore[invalid-argument-type]  # BaseHTTPMiddleware subclass; ty can't resolve the generic factory signature

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
    # Serve the Vite build output as an SPA (html=True enables index.html
    # fallback for client-side routing).  Falls back to the legacy inline
    # index.html when no build exists (e.g. during backend-only development).
    frontend_dir = Path(os.environ.get("GH_ISSUES_LOCAL_FRONTEND_DIR", str(FRONTEND_DIST)))
    if frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    else:

        @app.get("/")
        async def index():
            return FileResponse(STATIC_DIR / "index.html")

    return app
