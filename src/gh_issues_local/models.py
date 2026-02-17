"""Pydantic models for GitHub Issues API request validation."""

from __future__ import annotations

from pydantic import BaseModel


class CreateIssueRequest(BaseModel):
    """Request body for POST /repos/{owner}/{repo}/issues."""

    title: str | int
    body: str | None = None
    assignee: str | None = None
    milestone: str | int | None = None
    labels: list[str] | None = None
    assignees: list[str] | None = None


class UpdateIssueRequest(BaseModel):
    """Request body for PATCH /repos/{owner}/{repo}/issues/{issue_number}."""

    title: str | int | None = None
    body: str | None = None
    assignee: str | None = None
    state: str | None = None
    state_reason: str | None = None
    milestone: str | int | None = None
    labels: list[str] | None = None
    assignees: list[str] | None = None


class CreateCommentRequest(BaseModel):
    """Request body for POST /repos/{owner}/{repo}/issues/{issue_number}/comments."""

    body: str


class UpdateCommentRequest(BaseModel):
    """Request body for PATCH /repos/{owner}/{repo}/issues/comments/{comment_id}."""

    body: str
