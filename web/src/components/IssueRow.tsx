import { Link } from "react-router-dom"
import type { Issue } from "@/types"
import { IssueStateIcon } from "./IssueStateIcon"
import { LabelBadge } from "./LabelBadge"
import { RelativeTime } from "./RelativeTime"

interface IssueRowProps {
  issue: Issue
  owner: string
  repo: string
  showRepo?: boolean
}

export function IssueRow({ issue, owner, repo, showRepo }: IssueRowProps) {
  const linkBase = `/${owner}/${repo}/issues/${issue.number}`

  return (
    <div className="flex items-start gap-3 border-b px-4 py-3 hover:bg-muted/50">
      <div className="mt-0.5 shrink-0">
        <IssueStateIcon state={issue.state} stateReason={issue.state_reason} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-1.5">
          <Link to={linkBase} className="font-semibold hover:text-blue-600 truncate">
            {showRepo && (
              <span className="font-normal text-muted-foreground">{owner}/{repo} </span>
            )}
            {issue.title}
          </Link>
          {issue.labels.map(label => (
            <LabelBadge key={label.id} label={label} />
          ))}
        </div>
        <div className="mt-0.5 text-xs text-muted-foreground">
          {issue.state === "open" ? (
            <>
              #{issue.number} opened <RelativeTime date={issue.created_at} /> by {issue.user?.login ?? "unknown"}
            </>
          ) : (
            <>
              #{issue.number} by {issue.user?.login ?? "unknown"} was closed{" "}
              <RelativeTime date={issue.closed_at ?? issue.updated_at} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
