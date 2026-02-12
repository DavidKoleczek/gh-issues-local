import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Issues API server")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (default: 127.0.0.1, use 0.0.0.0 for network access)",
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
    args = parser.parse_args()

    # Auth is required when binding to non-localhost unless explicitly disabled.
    auth_required = args.host != "127.0.0.1" and not args.no_auth

    # Delay imports so --help stays fast.
    import uvicorn

    from gh_issues_local.app import create_app

    app = create_app(auth_required=auth_required)

    print(f"Starting gh-issues-local on http://{args.host}:{args.port}")
    if auth_required:
        print(f"Auth enabled. Token file: {app.state.auth_token_path}")
        print(f"Token: {app.state.auth_token}")
    else:
        print("Auth disabled (localhost-only).")

    uvicorn.run(app, host=args.host, port=args.port)
