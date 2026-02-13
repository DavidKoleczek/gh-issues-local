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
