import { useParams, Link } from "react-router-dom"
import { useIssue } from "@/hooks/useIssue"
import { updateIssue } from "@/api"
import { IssueStateBadge } from "@/components/IssueStateBadge"
import { LabelBadge } from "@/components/LabelBadge"
import { RelativeTime } from "@/components/RelativeTime"
import { StateActions } from "@/components/StateActions"
import { InlineEdit } from "@/components/InlineEdit"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { ErrorMessage } from "@/components/ErrorMessage"

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
