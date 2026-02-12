import os
from pathlib import Path
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Paths that never require auth (the UI itself must load to show the login form).
PUBLIC_PATHS = frozenset({"/", "/api/health", "/api/auth/status", "/api/auth/verify"})

_data_dir = Path(os.environ.get("GH_ISSUES_LOCAL_DATA_DIR", str(Path.home())))
TOKEN_FILE = _data_dir / ".gh-issues-local-token"


def ensure_token() -> str:
    """Return the existing auth token or generate and persist a new one."""
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token + "\n")
    TOKEN_FILE.chmod(0o600)
    return token


class AuthMiddleware(BaseHTTPMiddleware):
    """Require a Bearer token on non-public paths when auth is enabled."""

    async def dispatch(self, request: Request, call_next):
        if not request.app.state.auth_required:
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token == request.app.state.auth_token:
                return await call_next(request)

        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
