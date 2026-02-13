#!/usr/bin/env python3
"""
E2E smoke test

Starts the server in two modes (no-auth and auth-enabled), exercises every
endpoint, and prints clear pass/fail results with diagnostics on failure.

This is an AI-debugging tool, not a unit test suite. Run it to verify the
server works end to end, and read the output to understand what broke.

Usage:
    uv run python scripts/smoke_test.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# -- Config -----------------------------------------------------------------

NO_AUTH_PORT = 10102
AUTH_PORT = 10103
STARTUP_TIMEOUT = 10  # seconds


# -- HTTP helper ------------------------------------------------------------


def http(
    method: str,
    url: str,
    *,
    body: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Make an HTTP request. Returns (status_code, response_body)."""
    hdrs = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs.setdefault("Content-Type", "application/json")
    req = Request(url, data=data, headers=hdrs, method=method)
    try:
        with urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except HTTPError as e:
        return e.code, e.read().decode()


# -- Server lifecycle -------------------------------------------------------


def write_storage_config(data_dir: str) -> None:
    """Write .storage.yaml + .local_storage.yaml so create_storage() works."""
    dir_path = Path(data_dir)
    (dir_path / ".storage.yaml").write_text("provider: local\n")
    (dir_path / ".local_storage.yaml").write_text("root_path: ./storage\n")


def start_server(
    port: int,
    *,
    auth_required: bool = False,
    data_dir: str | None = None,
) -> subprocess.Popen:
    """Start the server as a subprocess using the app factory directly."""
    env = os.environ.copy()
    if data_dir:
        env["GH_ISSUES_LOCAL_DATA_DIR"] = data_dir
    # Inline script avoids needing __main__.py or the console-script on PATH.
    script = (
        "import uvicorn; "
        "from gh_issues_local.app import create_app; "
        f"uvicorn.run(create_app(auth_required={auth_required}), "
        f'host="127.0.0.1", port={port}, log_level="warning")'
    )
    return subprocess.Popen(
        [sys.executable, "-c", script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def wait_ready(port: int, timeout: int = STARTUP_TIMEOUT) -> bool:
    """Block until /api/health responds 200 or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            status, _ = http("GET", f"http://127.0.0.1:{port}/api/health")
            if status == 200:
                return True
        except (URLError, ConnectionError, OSError):
            pass
        time.sleep(0.2)
    return False


def stop_server(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


# -- Check definition & runner ----------------------------------------------


class Check:
    """One named expectation about an HTTP call."""

    def __init__(
        self,
        name: str,
        method: str,
        path: str,
        *,
        base: str,
        body: dict | None = None,
        headers: dict[str, str] | None = None,
        expect_status: int = 200,
        expect_json: dict | None = None,
        expect_json_contains: dict | None = None,
        expect_json_list_length: int | None = None,
        expect_body_contains: str | None = None,
    ):
        self.name = name
        self.method = method
        self.path = path
        self.base = base
        self.body = body
        self.headers = headers
        self.expect_status = expect_status
        self.expect_json = expect_json
        self.expect_json_contains = expect_json_contains
        self.expect_json_list_length = expect_json_list_length
        self.expect_body_contains = expect_body_contains

    def run(self) -> tuple[bool, str]:
        """Execute the check. Returns (passed, diagnostic_detail)."""
        url = f"{self.base}{self.path}"
        try:
            status, resp_body = http(
                self.method,
                url,
                body=self.body,
                headers=self.headers,
            )
        except Exception as exc:
            return False, f"  Request failed with exception: {exc}"

        lines: list[str] = []
        passed = True

        if status != self.expect_status:
            passed = False
            lines.append(f"  Expected status: {self.expect_status}")
            lines.append(f"  Got status:      {status}")
            lines.append(f"  Response body:   {resp_body[:500]}")

        if self.expect_json is not None:
            try:
                got = json.loads(resp_body)
            except (json.JSONDecodeError, ValueError):
                passed = False
                lines.append(f"  Expected JSON:   {self.expect_json}")
                lines.append(f"  Got non-JSON:    {resp_body[:300]}")
            else:
                if got != self.expect_json:
                    passed = False
                    lines.append(f"  Expected JSON:   {self.expect_json}")
                    lines.append(f"  Got JSON:        {got}")

        if self.expect_json_contains is not None:
            try:
                got = json.loads(resp_body)
            except (json.JSONDecodeError, ValueError):
                passed = False
                lines.append(f"  Expected JSON containing: {self.expect_json_contains}")
                lines.append(f"  Got non-JSON: {resp_body[:300]}")
            else:
                for key, expected_val in self.expect_json_contains.items():
                    actual_val = got.get(key, "<MISSING>")
                    if actual_val != expected_val:
                        passed = False
                        lines.append(f"  JSON key {key!r}: expected {expected_val!r}, got {actual_val!r}")

        if self.expect_json_list_length is not None:
            try:
                got = json.loads(resp_body)
            except (json.JSONDecodeError, ValueError):
                passed = False
                lines.append(f"  Expected JSON list of length {self.expect_json_list_length}")
                lines.append(f"  Got non-JSON: {resp_body[:300]}")
            else:
                if not isinstance(got, list):
                    passed = False
                    lines.append(f"  Expected JSON list, got {type(got).__name__}")
                elif len(got) != self.expect_json_list_length:
                    passed = False
                    lines.append(f"  Expected list length: {self.expect_json_list_length}")
                    lines.append(f"  Got list length:      {len(got)}")

        if self.expect_body_contains is not None and self.expect_body_contains not in resp_body:
            passed = False
            lines.append(f"  Expected body to contain: {self.expect_body_contains!r}")
            lines.append(f"  Got body ({len(resp_body)} chars): {resp_body[:300]}")

        return passed, "\n".join(lines)


# -- Check definitions ------------------------------------------------------


def no_auth_checks(base: str) -> list[Check]:
    """Checks for a server started with auth_required=False."""
    return [
        # -- Infrastructure checks ------------------------------------------
        Check(
            "health",
            "GET",
            "/api/health",
            base=base,
            expect_json={"status": "ok"},
        ),
        Check(
            "auth_status_reports_false",
            "GET",
            "/api/auth/status",
            base=base,
            expect_json={"required": False},
        ),
        Check(
            "verify_accepts_any_token",
            "POST",
            "/api/auth/verify",
            base=base,
            body={"token": "literally-anything"},
            expect_json={"valid": True},
        ),
        Check(
            "landing_page_serves_html",
            "GET",
            "/",
            base=base,
            expect_body_contains="gh-issues-local",
        ),
        Check(
            "swagger_docs_available",
            "GET",
            "/docs",
            base=base,
            expect_body_contains="swagger",
        ),
        Check(
            "unknown_route_returns_404",
            "GET",
            "/api/nonexistent",
            base=base,
            expect_status=404,
        ),
        # -- Issues API: Create ---------------------------------------------
        Check(
            "create_issue",
            "POST",
            "/repos/test-owner/test-repo/issues",
            base=base,
            body={"title": "First issue", "body": "This is the body"},
            expect_status=201,
            expect_json_contains={"number": 1, "title": "First issue", "state": "open"},
        ),
        Check(
            "create_second_issue",
            "POST",
            "/repos/test-owner/test-repo/issues",
            base=base,
            body={"title": "Second issue", "labels": ["bug", "urgent"]},
            expect_status=201,
            expect_json_contains={"number": 2, "title": "Second issue", "state": "open"},
        ),
        # -- Issues API: Get ------------------------------------------------
        Check(
            "get_issue",
            "GET",
            "/repos/test-owner/test-repo/issues/1",
            base=base,
            expect_json_contains={"number": 1, "title": "First issue", "body": "This is the body"},
        ),
        Check(
            "get_missing_issue_returns_404",
            "GET",
            "/repos/test-owner/test-repo/issues/999",
            base=base,
            expect_status=404,
            expect_body_contains="Not Found",
        ),
        # -- Issues API: Update ---------------------------------------------
        Check(
            "update_issue_title",
            "PATCH",
            "/repos/test-owner/test-repo/issues/1",
            base=base,
            body={"title": "Updated title"},
            expect_json_contains={"number": 1, "title": "Updated title"},
        ),
        Check(
            "close_issue",
            "PATCH",
            "/repos/test-owner/test-repo/issues/1",
            base=base,
            body={"state": "closed", "state_reason": "completed"},
            expect_json_contains={"number": 1, "state": "closed", "state_reason": "completed"},
        ),
        # -- Issues API: List for repo --------------------------------------
        Check(
            "list_repo_issues_open_only",
            "GET",
            "/repos/test-owner/test-repo/issues",
            base=base,
            # Issue #1 is closed, only #2 is open.
            expect_json_list_length=1,
        ),
        Check(
            "list_repo_issues_all_states",
            "GET",
            "/repos/test-owner/test-repo/issues?state=all",
            base=base,
            expect_json_list_length=2,
        ),
        # -- Issues API: List all -------------------------------------------
        Check(
            "list_all_issues",
            "GET",
            "/issues",
            base=base,
            # Only open issues: issue #2.
            expect_json_list_length=1,
        ),
        # -- Issues API: List user issues -----------------------------------
        Check(
            "list_user_issues",
            "GET",
            "/user/issues",
            base=base,
            expect_json_list_length=1,
        ),
        # -- Issues API: List org issues ------------------------------------
        Check(
            "list_org_issues",
            "GET",
            "/orgs/test-owner/issues",
            base=base,
            expect_json_list_length=1,
        ),
        Check(
            "list_org_issues_wrong_org",
            "GET",
            "/orgs/nonexistent-org/issues",
            base=base,
            expect_json_list_length=0,
        ),
        # -- Issues API: Search ---------------------------------------------
        Check(
            "search_issues",
            "GET",
            "/search/issues?q=Second",
            base=base,
            expect_json_contains={"total_count": 1, "incomplete_results": False},
        ),
        Check(
            "search_issues_no_results",
            "GET",
            "/search/issues?q=nonexistent-query-xyz",
            base=base,
            expect_json_contains={"total_count": 0},
        ),
        # -- Issues API: Validation -----------------------------------------
        Check(
            "create_issue_missing_title",
            "POST",
            "/repos/test-owner/test-repo/issues",
            base=base,
            body={},
            expect_status=422,
        ),
        Check(
            "update_missing_issue_returns_404",
            "PATCH",
            "/repos/test-owner/test-repo/issues/999",
            base=base,
            body={"title": "nope"},
            expect_status=404,
        ),
    ]


def auth_checks(base: str, token: str) -> list[Check]:
    """Checks for a server started with auth_required=True."""
    return [
        Check(
            "auth_status_reports_true",
            "GET",
            "/api/auth/status",
            base=base,
            expect_json={"required": True},
        ),
        Check(
            "health_still_public",
            "GET",
            "/api/health",
            base=base,
            expect_json={"status": "ok"},
        ),
        Check(
            "verify_rejects_wrong_token",
            "POST",
            "/api/auth/verify",
            base=base,
            body={"token": "wrong-token"},
            expect_json={"valid": False},
        ),
        Check(
            "verify_accepts_correct_token",
            "POST",
            "/api/auth/verify",
            base=base,
            body={"token": token},
            expect_json={"valid": True},
        ),
        Check(
            "protected_route_rejects_no_token",
            "GET",
            "/docs",
            base=base,
            expect_status=401,
            expect_json={"detail": "Unauthorized"},
        ),
        Check(
            "protected_route_accepts_valid_token",
            "GET",
            "/docs",
            base=base,
            headers={"Authorization": f"Bearer {token}"},
            expect_status=200,
        ),
        Check(
            "protected_route_rejects_bad_token",
            "GET",
            "/docs",
            base=base,
            headers={"Authorization": "Bearer wrong-token"},
            expect_status=401,
            expect_json={"detail": "Unauthorized"},
        ),
        # -- SPA routes are public (no auth needed to load the shell) ---------
        Check(
            "spa_login_route_is_public",
            "GET",
            "/login",
            base=base,
            expect_status=200,
        ),
        Check(
            "spa_arbitrary_route_is_public",
            "GET",
            "/owner/repo/issues",
            base=base,
            expect_status=200,
        ),
        Check(
            "favicon_is_public",
            "GET",
            "/favicon.ico",
            base=base,
            expect_status=200,
        ),
        # -- Issues endpoints require auth ----------------------------------
        Check(
            "issues_list_rejects_no_token",
            "GET",
            "/repos/test-owner/test-repo/issues",
            base=base,
            expect_status=401,
            expect_json={"detail": "Unauthorized"},
        ),
        Check(
            "issues_create_rejects_no_token",
            "POST",
            "/repos/test-owner/test-repo/issues",
            base=base,
            body={"title": "should fail"},
            expect_status=401,
            expect_json={"detail": "Unauthorized"},
        ),
        Check(
            "issues_create_with_token",
            "POST",
            "/repos/test-owner/test-repo/issues",
            base=base,
            headers={"Authorization": f"Bearer {token}"},
            body={"title": "Auth issue", "body": "Created with auth"},
            expect_status=201,
            expect_json_contains={"number": 1, "title": "Auth issue"},
        ),
        Check(
            "issues_get_with_token",
            "GET",
            "/repos/test-owner/test-repo/issues/1",
            base=base,
            headers={"Authorization": f"Bearer {token}"},
            expect_json_contains={"number": 1, "title": "Auth issue"},
        ),
        Check(
            "search_rejects_no_token",
            "GET",
            "/search/issues?q=test",
            base=base,
            expect_status=401,
            expect_json={"detail": "Unauthorized"},
        ),
    ]


# -- Main -------------------------------------------------------------------


def run_checks(label: str, checks: list[Check]) -> tuple[int, int, list[str]]:
    """Run a batch of checks, printing results. Returns (passed, failed, failure_names)."""
    print(f"\n--- {label} ---")
    passed = 0
    failed = 0
    failures: list[str] = []

    for check in checks:
        ok, detail = check.run()
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {check.name}: {check.method} {check.path}")
        if ok:
            passed += 1
        else:
            if detail:
                print(detail)
            failed += 1
            failures.append(check.name)

    return passed, failed, failures


def check_dev_server_starts() -> tuple[bool, str]:
    """Verify the dev command (uvicorn --factory) starts without errors.

    Uses a temp data directory with NO pre-existing .storage.yaml to confirm
    that create_app auto-creates default storage config.  This catches the
    class of bug where create_app crashes at import/call time due to missing
    config files.
    """
    empty_data_dir = tempfile.mkdtemp(prefix="gh-issues-devstart-")
    port = 10104
    env = os.environ.copy()
    env["GH_ISSUES_LOCAL_DATA_DIR"] = empty_data_dir

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "gh_issues_local.app:create_app",
            "--factory",
            f"--port={port}",
            "--host=127.0.0.1",
            "--log-level=warning",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        if wait_ready(port, timeout=STARTUP_TIMEOUT):
            return True, ""
        # Server did not start -- grab stderr for diagnostics.
        proc.terminate()
        proc.wait(timeout=5)
        stderr_out = proc.stderr.read().decode() if proc.stderr else ""
        return False, f"  Server did not become ready.\n  stderr: {stderr_out[:1000]}"
    finally:
        stop_server(proc)


def main() -> int:
    print("=== gh-issues-local e2e smoke test ===")

    procs: list[subprocess.Popen] = []
    total_passed = 0
    total_failed = 0
    all_failures: list[str] = []

    try:
        # -- Phase 0: dev server startup ------------------------------------
        # Catches factory/config crashes that break `uvicorn --factory`.

        print("\n--- Phase 0: Dev server startup (empty data dir) ---")
        ok, detail = check_dev_server_starts()
        if ok:
            print("[PASS] dev_server_starts: uvicorn --factory with no pre-existing config")
            total_passed += 1
        else:
            print("[FAIL] dev_server_starts: uvicorn --factory with no pre-existing config")
            if detail:
                print(detail)
            total_failed += 1
            all_failures.append("dev_server_starts")

        # -- Phase 1: no-auth mode ------------------------------------------

        no_auth_data_dir = tempfile.mkdtemp(prefix="gh-issues-noauth-")
        write_storage_config(no_auth_data_dir)
        print(f"\nStarting no-auth server on :{NO_AUTH_PORT} (data_dir={no_auth_data_dir}) ...")
        no_auth_proc = start_server(NO_AUTH_PORT, auth_required=False, data_dir=no_auth_data_dir)
        procs.append(no_auth_proc)

        if not wait_ready(NO_AUTH_PORT):
            print(f"FATAL: Server did not become ready on :{NO_AUTH_PORT}")
            stderr = no_auth_proc.stderr
            if stderr:
                print(f"Server stderr:\n{stderr.read().decode()[:2000]}")
            return 1

        base_no_auth = f"http://127.0.0.1:{NO_AUTH_PORT}"
        p, f, names = run_checks(
            f"Phase 1: No-auth mode (port {NO_AUTH_PORT})",
            no_auth_checks(base_no_auth),
        )
        total_passed += p
        total_failed += f
        all_failures.extend(names)

        # -- Phase 2: auth-enabled mode -------------------------------------

        auth_data_dir = tempfile.mkdtemp(prefix="gh-issues-test-")
        write_storage_config(auth_data_dir)
        print(f"\nStarting auth server on :{AUTH_PORT} (data_dir={auth_data_dir}) ...")
        auth_proc = start_server(
            AUTH_PORT,
            auth_required=True,
            data_dir=auth_data_dir,
        )
        procs.append(auth_proc)

        if not wait_ready(AUTH_PORT):
            print(f"FATAL: Server did not become ready on :{AUTH_PORT}")
            stderr = auth_proc.stderr
            if stderr:
                print(f"Server stderr:\n{stderr.read().decode()[:2000]}")
            return 1

        token_path = Path(auth_data_dir) / ".gh-issues-local-token"
        token = token_path.read_text().strip()
        print(f"Read auth token from {token_path}")

        base_auth = f"http://127.0.0.1:{AUTH_PORT}"
        p, f, names = run_checks(
            f"Phase 2: Auth mode (port {AUTH_PORT})",
            auth_checks(base_auth, token),
        )
        total_passed += p
        total_failed += f
        all_failures.extend(names)

    finally:
        for proc in procs:
            stop_server(proc)

    # -- Summary ------------------------------------------------------------

    total = total_passed + total_failed
    print(f"\n=== Results: {total_passed} passed, {total_failed} failed ({total} total) ===")
    if all_failures:
        print(f"Failed checks: {', '.join(all_failures)}")
    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
