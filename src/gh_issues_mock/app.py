from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from gh_issues_mock.auth import TOKEN_FILE, AuthMiddleware, ensure_token

STATIC_DIR = Path(__file__).parent / "static"


class VerifyRequest(BaseModel):
    token: str


def create_app(auth_required: bool = False) -> FastAPI:
    app = FastAPI(title="GitHub Issues Mock", version="0.1.0")

    # Auth state -- set before middleware so it's available on first request.
    app.state.auth_required = auth_required
    app.state.auth_token = ensure_token() if auth_required else None
    app.state.auth_token_path = str(TOKEN_FILE)

    app.add_middleware(AuthMiddleware)  # type: ignore[invalid-argument-type]  # BaseHTTPMiddleware subclass; ty can't resolve the generic factory signature

    # -- public endpoints (no auth) -----------------------------------------

    @app.get("/")
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

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

    return app
