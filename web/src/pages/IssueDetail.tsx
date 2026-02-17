import { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { useIssue } from "@/hooks/useIssue"
import { useComments } from "@/hooks/useComments"
import { updateIssue, createComment, updateComment, deleteComment } from "@/api"
import { IssueStateBadge } from "@/components/IssueStateBadge"
import { LabelBadge } from "@/components/LabelBadge"
import { RelativeTime } from "@/components/RelativeTime"
import { StateActions } from "@/components/StateActions"
import { InlineEdit } from "@/components/InlineEdit"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { ErrorMessage } from "@/components/ErrorMessage"
import type { Comment } from "@/types"

function CommentCard({
  comment,
  owner,
  repo,
  onUpdated,
}: {
  comment: Comment
  owner: string
  repo: string
  onUpdated: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [editBody, setEditBody] = useState(comment.body)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const handleSave = async () => {
    if (!editBody.trim()) return
    setSaving(true)
    try {
      await updateComment(owner, repo, comment.id, editBody)
      setEditing(false)
      onUpdated()
    } catch {
      // Keep editing open so the user can retry.
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await deleteComment(owner, repo, comment.id)
      onUpdated()
    } catch {
      setDeleting(false)
    }
  }

  return (
    <div className="rounded-lg border">
      <div className="flex items-center justify-between border-b bg-muted/50 px-4 py-2 text-xs font-medium text-muted-foreground">
        <span>
          {comment.user?.login ?? "unknown"} commented{" "}
          <RelativeTime date={comment.created_at} />
          {comment.updated_at !== comment.created_at && (
            <span className="ml-1">(edited)</span>
          )}
        </span>
        <span className="flex gap-1">
          <button
            onClick={() => { setEditing(!editing); setEditBody(comment.body) }}
            className="rounded px-1.5 py-0.5 hover:bg-muted"
          >
            {editing ? "Cancel" : "Edit"}
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="rounded px-1.5 py-0.5 text-red-600 hover:bg-red-50 disabled:opacity-50 dark:text-red-400 dark:hover:bg-red-950"
          >
            {deleting ? "..." : "Delete"}
          </button>
        </span>
      </div>
      <div className="p-4">
        {editing ? (
          <div className="space-y-2">
            <textarea
              value={editBody}
              onChange={e => setEditBody(e.target.value)}
              rows={4}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving || !editBody.trim()}
                className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Update comment"}
              </button>
              <button
                onClick={() => setEditing(false)}
                className="rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-muted"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <pre className="whitespace-pre-wrap break-words text-sm font-sans">
            {comment.body}
          </pre>
        )}
      </div>
    </div>
  )
}

function NewCommentForm({
  owner,
  repo,
  issueNumber,
  onCreated,
}: {
  owner: string
  repo: string
  issueNumber: number
  onCreated: () => void
}) {
  const [body, setBody] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!body.trim()) return
    setSubmitting(true)
    try {
      await createComment(owner, repo, issueNumber, body)
      setBody("")
      onCreated()
    } catch {
      // Keep the form content so the user can retry.
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border">
      <div className="border-b bg-muted/50 px-4 py-2 text-xs font-medium text-muted-foreground">
        Write a comment
      </div>
      <div className="p-4 space-y-3">
        <textarea
          value={body}
          onChange={e => setBody(e.target.value)}
          placeholder="Leave a comment"
          rows={4}
          className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting || !body.trim()}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {submitting ? "Submitting..." : "Comment"}
          </button>
        </div>
      </div>
    </form>
  )
}

export default function IssueDetail() {
  const { owner, repo, number } = useParams<{
    owner: string
    repo: string
    number: string
  }>()
  const { data: issue, loading, error, refetch } = useIssue(
    owner!,
    repo!,
    Number(number),
  )
  const {
    data: comments,
    loading: commentsLoading,
    error: commentsError,
    refetch: refetchComments,
  } = useComments(owner!, repo!, Number(number))

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} onRetry={refetch} />
  if (!issue || !owner || !repo) return null

  const handleTitleSave = async (title: string) => {
    await updateIssue(owner, repo, issue.number, { title })
    refetch()
  }

  const handleBodySave = async (body: string) => {
    await updateIssue(owner, repo, issue.number, { body })
    refetch()
  }

  const handleAssigneesSave = async (value: string) => {
    const assignees = value
      .split(",")
      .map(s => s.trim())
      .filter(Boolean)
    await updateIssue(owner, repo, issue.number, { assignees })
    refetch()
  }

  const handleLabelsSave = async (value: string) => {
    const labels = value
      .split(",")
      .map(s => s.trim())
      .filter(Boolean)
    await updateIssue(owner, repo, issue.number, { labels })
    refetch()
  }

  const handleCommentChange = () => {
    refetchComments()
    refetch() // Refresh issue to update comment count.
  }

  return (
    <div className="space-y-4">
      {/* Breadcrumb */}
      <div className="text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground">
          {owner}
        </Link>
        {" / "}
        <Link to={`/${owner}/${repo}/issues`} className="hover:text-foreground">
          {repo}
        </Link>
        {" / "}
        <span>#{issue.number}</span>
      </div>

      {/* Title */}
      <div className="flex items-start gap-2">
        <div className="flex-1">
          <h1 className="text-2xl font-bold">
            {issue.title}{" "}
            <span className="font-normal text-muted-foreground">#{issue.number}</span>
          </h1>
          <InlineEdit value={issue.title} onSave={handleTitleSave} placeholder="Title" />
        </div>
      </div>

      {/* Status line */}
      <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <IssueStateBadge state={issue.state} stateReason={issue.state_reason} />
        <span>
          {issue.user?.login ?? "unknown"} opened this issue{" "}
          <RelativeTime date={issue.created_at} />
          {" \u00b7 "}
          {issue.comments} comment{issue.comments !== 1 ? "s" : ""}
        </span>
      </div>

      <hr className="border-border" />

      {/* Main content + sidebar */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-[1fr_256px]">
        {/* Body */}
        <div className="space-y-4">
          <div className="rounded-lg border">
            <div className="border-b bg-muted/50 px-4 py-2 text-xs font-medium text-muted-foreground">
              {issue.user?.login ?? "unknown"} commented{" "}
              <RelativeTime date={issue.created_at} />
            </div>
            <div className="p-4">
              {issue.body ? (
                <pre className="whitespace-pre-wrap break-words text-sm font-sans">
                  {issue.body}
                </pre>
              ) : (
                <p className="text-sm text-muted-foreground italic">
                  No description provided.
                </p>
              )}
            </div>
          </div>
          <InlineEdit
            value={issue.body ?? ""}
            onSave={handleBodySave}
            multiline
            placeholder="Leave a description"
          />

          {/* Comments */}
          {commentsLoading ? (
            <div className="py-4 text-center text-sm text-muted-foreground">
              Loading comments...
            </div>
          ) : commentsError ? (
            <ErrorMessage message={commentsError.message} onRetry={refetchComments} />
          ) : (
            <>
              {comments.map(c => (
                <CommentCard
                  key={c.id}
                  comment={c}
                  owner={owner}
                  repo={repo}
                  onUpdated={handleCommentChange}
                />
              ))}
            </>
          )}

          <NewCommentForm
            owner={owner}
            repo={repo}
            issueNumber={issue.number}
            onCreated={handleCommentChange}
          />

          <hr className="border-border" />

          <StateActions
            owner={owner}
            repo={repo}
            issueNumber={issue.number}
            state={issue.state}
            onUpdated={refetch}
          />
        </div>

        {/* Sidebar */}
        <div className="space-y-6 text-sm">
          {/* Assignees */}
          <div>
            <h3 className="mb-2 font-medium text-muted-foreground">Assignees</h3>
            {issue.assignees.length > 0 ? (
              <div className="space-y-1">
                {issue.assignees.map(a => (
                  <div key={a.login} className="text-sm">{a.login}</div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No one</p>
            )}
            <InlineEdit
              value={issue.assignees.map(a => a.login).join(", ")}
              onSave={handleAssigneesSave}
              placeholder="Add assignees (comma-separated)"
            />
          </div>

          {/* Labels */}
          <div>
            <h3 className="mb-2 font-medium text-muted-foreground">Labels</h3>
            {issue.labels.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {issue.labels.map(l => (
                  <LabelBadge key={l.id} label={l} />
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">None yet</p>
            )}
            <InlineEdit
              value={issue.labels.map(l => l.name).join(", ")}
              onSave={handleLabelsSave}
              placeholder="Add labels (comma-separated)"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
