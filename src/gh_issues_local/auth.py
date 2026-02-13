import os
from pathlib import Path
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Infrastructure API paths that skip auth (needed for the SPA login flow).
PUBLIC_API_PATHS = frozenset({"/api/health", "/api/auth/status", "/api/auth/verify"})

# GitHub-style data API prefixes (no /api prefix -- they mirror GitHub's real
# paths).  Everything under these prefixes requires auth.
_API_PREFIXES = ("/repos/", "/search/", "/orgs/", "/user/")

# FastAPI auto-generated doc routes.
_DOC_PATHS = frozenset({"/docs", "/openapi.json", "/redoc"})


def _is_protected(path: str) -> bool:
    """Return True when *path* leads to a data endpoint that requires auth.

    The SPA shell and its assets are static HTML/JS/CSS -- they contain no
    user data and must be accessible without a token so the browser can
    render the login page.  Only the data API surface is gated.
    """
    if path in PUBLIC_API_PATHS:
        return False
    if path.startswith(_API_PREFIXES) or path == "/issues":
        return True
    if path.startswith("/api/"):
        return True
    return path in _DOC_PATHS


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

        path = request.url.path
        if not _is_protected(path):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token == request.app.state.auth_token:
                return await call_next(request)

        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
