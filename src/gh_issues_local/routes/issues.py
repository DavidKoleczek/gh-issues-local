"""Issues -- Core API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from gh_issues_local.models import CreateIssueRequest, UpdateIssueRequest
from gh_issues_local.storage import IssueStore

router = APIRouter()


def _base_url(request: Request) -> str:
    """Derive the base URL from the incoming request (no trailing slash)."""
    return str(request.base_url).rstrip("/")


def _get_store(request: Request) -> IssueStore:
    return request.app.state.issue_store


# ---------------------------------------------------------------------------
# 1. GET /issues  --  issues/list
# ---------------------------------------------------------------------------
@router.get("/issues")
async def list_issues(
    request: Request,
    state: str = "open",
    sort: str = "created",
    direction: str = "desc",
    labels: str | None = None,
    since: str | None = None,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> list[dict[str, Any]]:
    store = _get_store(request)
    return store.list_all(
        state=state,
        sort=sort,
        direction=direction,
        labels=labels,
        since=since,
        per_page=per_page,
        page=page,
    )


# ---------------------------------------------------------------------------
# 2. GET /orgs/{org}/issues  --  issues/list-for-org
# ---------------------------------------------------------------------------
@router.get("/orgs/{org}/issues")
async def list_org_issues(
    request: Request,
    org: str,
    state: str = "open",
    sort: str = "created",
    direction: str = "desc",
    labels: str | None = None,
    since: str | None = None,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> list[dict[str, Any]]:
    store = _get_store(request)
    return store.list_for_org(
        org,
        state=state,
        sort=sort,
        direction=direction,
        labels=labels,
        since=since,
        per_page=per_page,
        page=page,
    )


# ---------------------------------------------------------------------------
# 3. GET /user/issues  --  issues/list-for-authenticated-user
# ---------------------------------------------------------------------------
@router.get("/user/issues")
async def list_user_issues(
    request: Request,
    state: str = "open",
    sort: str = "created",
    direction: str = "desc",
    labels: str | None = None,
    since: str | None = None,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> list[dict[str, Any]]:
    store = _get_store(request)
    return store.list_all(
        state=state,
        sort=sort,
        direction=direction,
        labels=labels,
        since=since,
        per_page=per_page,
        page=page,
    )


# ---------------------------------------------------------------------------
# 4. GET /repos/{owner}/{repo}/issues  --  issues/list-for-repo
# ---------------------------------------------------------------------------
@router.get("/repos/{owner}/{repo}/issues")
async def list_repo_issues(
    request: Request,
    owner: str,
    repo: str,
    state: str = "open",
    sort: str = "created",
    direction: str = "desc",
    labels: str | None = None,
    since: str | None = None,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> list[dict[str, Any]]:
    store = _get_store(request)
    return store.list_for_repo(
        owner,
        repo,
        state=state,
        sort=sort,
        direction=direction,
        labels=labels,
        since=since,
        per_page=per_page,
        page=page,
    )


# ---------------------------------------------------------------------------
# 5. POST /repos/{owner}/{repo}/issues  --  issues/create
# ---------------------------------------------------------------------------
@router.post("/repos/{owner}/{repo}/issues", status_code=201)
async def create_issue(
    request: Request,
    owner: str,
    repo: str,
    body: CreateIssueRequest,
) -> JSONResponse:
    store = _get_store(request)
    issue = store.create(
        owner=owner,
        repo=repo,
        title=str(body.title),
        body=body.body,
        labels=body.labels,
        assignee=body.assignee,
        assignees=body.assignees,
        base_url=_base_url(request),
    )
    return JSONResponse(
        content=issue,
        status_code=201,
        headers={"Location": issue["url"]},
    )


# ---------------------------------------------------------------------------
# 6. GET /repos/{owner}/{repo}/issues/{issue_number}  --  issues/get
# ---------------------------------------------------------------------------
@router.get("/repos/{owner}/{repo}/issues/{issue_number}")
async def get_issue(
    request: Request,
    owner: str,
    repo: str,
    issue_number: int,
) -> JSONResponse:
    store = _get_store(request)
    issue = store.get(owner, repo, issue_number)
    if issue is None:
        return JSONResponse(
            status_code=404,
            content={
                "message": "Not Found",
                "documentation_url": "https://docs.github.com/rest",
            },
        )
    return JSONResponse(content=issue)


# ---------------------------------------------------------------------------
# 7. PATCH /repos/{owner}/{repo}/issues/{issue_number}  --  issues/update
# ---------------------------------------------------------------------------
@router.patch("/repos/{owner}/{repo}/issues/{issue_number}")
async def update_issue(
    request: Request,
    owner: str,
    repo: str,
    issue_number: int,
    body: UpdateIssueRequest,
) -> JSONResponse:
    store = _get_store(request)

    # Build a changes dict containing only the fields explicitly sent.
    # Pydantic v2: model_fields_set tracks which fields were in the payload.
    changes: dict[str, Any] = {}
    for field_name in body.model_fields_set:
        changes[field_name] = getattr(body, field_name)

    issue = store.update(
        owner=owner,
        repo=repo,
        number=issue_number,
        changes=changes,
        base_url=_base_url(request),
    )
    if issue is None:
        return JSONResponse(
            status_code=404,
            content={
                "message": "Not Found",
                "documentation_url": "https://docs.github.com/rest",
            },
        )
    return JSONResponse(content=issue)


# ---------------------------------------------------------------------------
# 8. GET /search/issues  --  search/issues-and-pull-requests
# ---------------------------------------------------------------------------
@router.get("/search/issues")
async def search_issues(
    request: Request,
    q: str = Query(...),
    sort: str | None = None,
    order: str = "desc",
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> dict[str, Any]:
    store = _get_store(request)
    return store.search(
        q,
        sort=sort,
        order=order,
        per_page=per_page,
        page=page,
    )
