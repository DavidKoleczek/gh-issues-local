"""Comments API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from gh_issues_local.models import CreateCommentRequest, UpdateCommentRequest
from gh_issues_local.storage import IssueStore

router = APIRouter()

NOT_FOUND = {"message": "Not Found", "documentation_url": "https://docs.github.com/rest"}


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _get_store(request: Request) -> IssueStore:
    return request.app.state.issue_store


# ---------------------------------------------------------------------------
# 1. GET /repos/{owner}/{repo}/issues/comments  --  issues/list-comments-for-repo
# ---------------------------------------------------------------------------
@router.get("/repos/{owner}/{repo}/issues/comments")
async def list_comments_for_repo(
    request: Request,
    owner: str,
    repo: str,
    sort: str = "created",
    direction: str = "desc",
    since: str | None = None,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> list[dict[str, Any]]:
    store = _get_store(request)
    return store.list_comments_for_repo(
        owner,
        repo,
        sort=sort,
        direction=direction,
        since=since,
        per_page=per_page,
        page=page,
    )


# ---------------------------------------------------------------------------
# 2. GET /repos/{owner}/{repo}/issues/comments/{comment_id}  --  issues/get-comment
# ---------------------------------------------------------------------------
@router.get("/repos/{owner}/{repo}/issues/comments/{comment_id}")
async def get_comment(
    request: Request,
    owner: str,
    repo: str,
    comment_id: int,
) -> JSONResponse:
    store = _get_store(request)
    comment = store.get_comment(owner, repo, comment_id)
    if comment is None:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(content=comment)


# ---------------------------------------------------------------------------
# 3. PATCH /repos/{owner}/{repo}/issues/comments/{comment_id}  --  issues/update-comment
# ---------------------------------------------------------------------------
@router.patch("/repos/{owner}/{repo}/issues/comments/{comment_id}")
async def update_comment(
    request: Request,
    owner: str,
    repo: str,
    comment_id: int,
    body: UpdateCommentRequest,
) -> JSONResponse:
    store = _get_store(request)
    comment = store.update_comment(
        owner,
        repo,
        comment_id,
        body=body.body,
        base_url=_base_url(request),
    )
    if comment is None:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(content=comment)


# ---------------------------------------------------------------------------
# 4. DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}  --  issues/delete-comment
# ---------------------------------------------------------------------------
@router.delete("/repos/{owner}/{repo}/issues/comments/{comment_id}", status_code=204)
async def delete_comment(
    request: Request,
    owner: str,
    repo: str,
    comment_id: int,
) -> JSONResponse:
    store = _get_store(request)
    deleted = store.delete_comment(owner, repo, comment_id)
    if not deleted:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(status_code=204, content=None)


# ---------------------------------------------------------------------------
# 5. PUT /repos/{owner}/{repo}/issues/comments/{comment_id}/pin  --  issues/pin-comment
# ---------------------------------------------------------------------------
@router.put("/repos/{owner}/{repo}/issues/comments/{comment_id}/pin")
async def pin_comment(
    request: Request,
    owner: str,
    repo: str,
    comment_id: int,
) -> JSONResponse:
    store = _get_store(request)
    comment = store.pin_comment(owner, repo, comment_id)
    if comment is None:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(content=comment)


# ---------------------------------------------------------------------------
# 6. DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}/pin  --  issues/unpin-comment
# ---------------------------------------------------------------------------
@router.delete("/repos/{owner}/{repo}/issues/comments/{comment_id}/pin", status_code=204)
async def unpin_comment(
    request: Request,
    owner: str,
    repo: str,
    comment_id: int,
) -> JSONResponse:
    store = _get_store(request)
    removed = store.unpin_comment(owner, repo, comment_id)
    if not removed:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(status_code=204, content=None)


# ---------------------------------------------------------------------------
# 7. GET /repos/{owner}/{repo}/issues/{issue_number}/comments  --  issues/list-comments
# ---------------------------------------------------------------------------
@router.get("/repos/{owner}/{repo}/issues/{issue_number}/comments")
async def list_comments(
    request: Request,
    owner: str,
    repo: str,
    issue_number: int,
    since: str | None = None,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> JSONResponse:
    store = _get_store(request)
    comments = store.list_comments_for_issue(
        owner,
        repo,
        issue_number,
        since=since,
        per_page=per_page,
        page=page,
    )
    if comments is None:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(content=comments)


# ---------------------------------------------------------------------------
# 8. POST /repos/{owner}/{repo}/issues/{issue_number}/comments  --  issues/create-comment
# ---------------------------------------------------------------------------
@router.post("/repos/{owner}/{repo}/issues/{issue_number}/comments", status_code=201)
async def create_comment(
    request: Request,
    owner: str,
    repo: str,
    issue_number: int,
    body: CreateCommentRequest,
) -> JSONResponse:
    store = _get_store(request)
    comment = store.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=body.body,
        base_url=_base_url(request),
    )
    if comment is None:
        return JSONResponse(status_code=404, content=NOT_FOUND)
    return JSONResponse(
        content=comment,
        status_code=201,
        headers={"Location": comment["url"]},
    )
