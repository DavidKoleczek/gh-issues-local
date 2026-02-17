// TypeScript interfaces mirroring the FastAPI Pydantic models.

export interface Label {
  id: number
  name: string
  color: string
  description: string
}

export interface User {
  login: string
  avatar_url: string
}

export interface Issue {
  id: number
  number: number
  title: string
  body: string | null
  state: "open" | "closed"
  state_reason: "completed" | "not_planned" | "reopened" | null
  labels: Label[]
  assignees: User[]
  user: User
  closed_by: User | null
  comments: number
  locked: boolean
  created_at: string
  updated_at: string
  closed_at: string | null
  repository_url: string
}

export interface Comment {
  id: number
  node_id: string
  url: string
  html_url: string
  issue_url: string
  user: User
  created_at: string
  updated_at: string
  body: string
  author_association: string
  pinned?: boolean
}

export interface CreateIssueRequest {
  title: string
  body?: string
  labels?: string[]
  assignees?: string[]
}

export interface UpdateIssueRequest {
  title?: string
  body?: string
  state?: "open" | "closed"
  state_reason?: "completed" | "not_planned" | "reopened"
  labels?: string[]
  assignees?: string[]
}
