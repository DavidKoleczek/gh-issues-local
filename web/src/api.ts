// Typed API client for gh-issues-local.
// All calls use relative URLs (/api/...) which in dev route through the Vite
// proxy and in production go directly to the FastAPI server.

import type { Issue, Comment, CreateIssueRequest, UpdateIssueRequest } from "./types"

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem("auth_token")
  const headers: Record<string, string> = {
    ...((init?.headers as Record<string, string>) ?? {}),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  if (init?.body && typeof init.body === "string") {
    headers["Content-Type"] = "application/json"
  }

  const res = await fetch(path, { ...init, headers })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status}: ${detail}`)
  }
  return res.json() as Promise<T>
}

// -- Auth -------------------------------------------------------------------

export function getAuthStatus(): Promise<{ required: boolean }> {
  return request("/api/auth/status")
}

export function verifyToken(token: string): Promise<{ valid: boolean }> {
  return request("/api/auth/verify", {
    method: "POST",
    body: JSON.stringify({ token }),
  })
}

// -- Health -----------------------------------------------------------------

export function getHealth(): Promise<{ status: string }> {
  return request("/api/health")
}

// -- Issues -----------------------------------------------------------------

export interface ListIssuesParams {
  state?: "open" | "closed" | "all"
  sort?: "created" | "updated" | "comments"
  direction?: "asc" | "desc"
  labels?: string
  since?: string
  per_page?: number
  page?: number
}

function toQuery(params: Record<string, unknown>): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null,
  )
  if (entries.length === 0) return ""
  return "?" + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString()
}

export function listIssuesForRepo(
  owner: string,
  repo: string,
  params: ListIssuesParams = {},
): Promise<Issue[]> {
  return request(`/repos/${owner}/${repo}/issues${toQuery(params as Record<string, unknown>)}`)
}

export function getIssue(
  owner: string,
  repo: string,
  issueNumber: number,
): Promise<Issue> {
  return request(`/repos/${owner}/${repo}/issues/${issueNumber}`)
}

export function createIssue(
  owner: string,
  repo: string,
  body: CreateIssueRequest,
): Promise<Issue> {
  return request(`/repos/${owner}/${repo}/issues`, {
    method: "POST",
    body: JSON.stringify(body),
  })
}

export function updateIssue(
  owner: string,
  repo: string,
  issueNumber: number,
  body: UpdateIssueRequest,
): Promise<Issue> {
  return request(`/repos/${owner}/${repo}/issues/${issueNumber}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  })
}

// Global issue list (all repos). Used for repo discovery.
export function listAllIssues(
  params: ListIssuesParams = {},
): Promise<Issue[]> {
  return request(`/issues${toQuery(params as Record<string, unknown>)}`)
}

export function searchIssues(
  q: string,
  params: { per_page?: number; page?: number } = {},
): Promise<{ total_count: number; items: Issue[] }> {
  return request(`/search/issues${toQuery({ q, ...params })}`)
}

// -- Comments ---------------------------------------------------------------

export interface ListCommentsParams {
  since?: string
  per_page?: number
  page?: number
}

export function listComments(
  owner: string,
  repo: string,
  issueNumber: number,
  params: ListCommentsParams = {},
): Promise<Comment[]> {
  return request(
    `/repos/${owner}/${repo}/issues/${issueNumber}/comments${toQuery(params as Record<string, unknown>)}`,
  )
}

export function createComment(
  owner: string,
  repo: string,
  issueNumber: number,
  body: string,
): Promise<Comment> {
  return request(`/repos/${owner}/${repo}/issues/${issueNumber}/comments`, {
    method: "POST",
    body: JSON.stringify({ body }),
  })
}

export function updateComment(
  owner: string,
  repo: string,
  commentId: number,
  body: string,
): Promise<Comment> {
  return request(`/repos/${owner}/${repo}/issues/comments/${commentId}`, {
    method: "PATCH",
    body: JSON.stringify({ body }),
  })
}

export async function deleteComment(
  owner: string,
  repo: string,
  commentId: number,
): Promise<void> {
  const token = localStorage.getItem("auth_token")
  const headers: Record<string, string> = {}
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  const res = await fetch(`/repos/${owner}/${repo}/issues/comments/${commentId}`, {
    method: "DELETE",
    headers,
  })
  if (!res.ok && res.status !== 204) {
    const detail = await res.text()
    throw new Error(`${res.status}: ${detail}`)
  }
}
