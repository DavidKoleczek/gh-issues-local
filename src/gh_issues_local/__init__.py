import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Issues API server")
    parser.add_argument(
        "--host",
        default=None,
        help="Bind address (default: 127.0.0.1, or 0.0.0.0 in production mode)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port (default: 8000)",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable auth even when bound to a network-accessible address",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Download the frontend build from GitHub Releases and serve it",
    )
    parser.add_argument(
        "--update-frontend",
        action="store_true",
        help="Force re-download of the frontend build (implies --production)",
    )
    args = parser.parse_args()

    if args.update_frontend:
        args.production = True

    host = args.host or ("0.0.0.0" if args.production else "127.0.0.1")

    # In production mode, download the frontend build before starting.
    if args.production:
        from gh_issues_local.frontend import fetch_frontend

        data_dir = Path(os.environ.get("GH_ISSUES_LOCAL_DATA_DIR", str(Path.home())))
        cache_dir = data_dir / "frontend_cache"
        frontend_dir = fetch_frontend(cache_dir, force=args.update_frontend)
        os.environ["GH_ISSUES_LOCAL_FRONTEND_DIR"] = str(frontend_dir)

    # Auth is required when binding to non-localhost unless explicitly disabled.
    auth_required = host != "127.0.0.1" and not args.no_auth

    # Delay imports so --help stays fast.
    import uvicorn

    from gh_issues_local.app import create_app

    app = create_app(auth_required=auth_required)

    print(f"Starting gh-issues-local on http://{host}:{args.port}")
    if auth_required:
        print(f"Auth enabled. Token file: {app.state.auth_token_path}")
        print(f"Token: {app.state.auth_token}")
    else:
        print("Auth disabled (localhost-only).")

    uvicorn.run(app, host=host, port=args.port)
