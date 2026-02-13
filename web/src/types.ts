// TypeScript interfaces mirroring the FastAPI Pydantic models.

export interface Label {
  id: number
  name: string
  color: string
  description: string
}

export interface User {
  login: string
}

export interface Issue {
  id: number
  number: number
  title: string
  body: string | null
  state: "open" | "closed"
  labels: Label[]
  assignees: User[]
  locked: boolean
  created_at: string
  updated_at: string
  closed_at: string | null
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
  labels?: string[]
  assignees?: string[]
}
