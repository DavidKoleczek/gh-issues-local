import { useState, useEffect } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { listIssuesForRepo } from "@/api"
import { useIssues } from "@/hooks/useIssues"
import { IssueRow } from "@/components/IssueRow"
import { Pagination } from "@/components/Pagination"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { ErrorMessage } from "@/components/ErrorMessage"
import { EmptyState } from "@/components/EmptyState"
import { Button } from "@/components/ui/button"
import { CircleDot, CheckCircle2 } from "lucide-react"

const PER_PAGE = 25

export default function IssueList() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>()
  const [searchParams, setSearchParams] = useSearchParams()

  const stateFilter = (searchParams.get("state") as "open" | "closed") || "open"
  const page = Number(searchParams.get("page")) || 1
  const sort = searchParams.get("sort") || "created"
  const direction = searchParams.get("direction") || "desc"
  const labelFilter = searchParams.get("labels") || undefined

  const [openCount, setOpenCount] = useState<number | null>(null)
  const [closedCount, setClosedCount] = useState<number | null>(null)

  // Fetch counts on mount
  useEffect(() => {
    if (!owner || !repo) return
    listIssuesForRepo(owner, repo, { state: "open", per_page: 100 }).then(
      r => setOpenCount(r.length),
    )
    listIssuesForRepo(owner, repo, { state: "closed", per_page: 100 }).then(
      r => setClosedCount(r.length),
    )
  }, [owner, repo])

  const { data: issues, loading, error, refetch } = useIssues(owner!, repo!, {
    state: stateFilter,
    sort: sort as "created" | "updated" | "comments",
    direction: direction as "asc" | "desc",
    labels: labelFilter,
    per_page: PER_PAGE,
    page,
  })

  // Extract unique labels from current results for the filter
  const allLabels = Array.from(
    new Map(issues.flatMap(i => i.labels).map(l => [l.name, l])).values(),
  )

  const setParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    next.set(key, value)
    if (key !== "page") next.delete("page")
    setSearchParams(next)
  }

  const formatCount = (n: number | null) => {
    if (n === null) return "..."
    return n >= 100 ? "100+" : String(n)
  }

  if (!owner || !repo) return null

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
            {owner}
          </Link>
          <span className="text-sm text-muted-foreground"> / </span>
          <Link to={`/${owner}/${repo}/issues`} className="text-sm font-semibold hover:text-blue-600">
            {repo}
          </Link>
        </div>
        <Link to={`/${owner}/${repo}/issues/new`}>
          <Button className="bg-green-600 hover:bg-green-700 text-white">New issue</Button>
        </Link>
      </div>

      {/* Filter/toolbar + issue table */}
      <div className="rounded-lg border">
        <div className="flex flex-wrap items-center gap-4 bg-muted/50 px-4 py-3 border-b">
          {/* State tabs */}
          <button
            className={`flex items-center gap-1.5 text-sm font-medium ${stateFilter === "open" ? "text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            onClick={() => setParam("state", "open")}
          >
            <CircleDot className="h-4 w-4" />
            {formatCount(openCount)} Open
          </button>
          <button
            className={`flex items-center gap-1.5 text-sm font-medium ${stateFilter === "closed" ? "text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            onClick={() => setParam("state", "closed")}
          >
            <CheckCircle2 className="h-4 w-4" />
            {formatCount(closedCount)} Closed
          </button>

          <div className="ml-auto flex items-center gap-2">
            {/* Label filter */}
            {allLabels.length > 0 && (
              <select
                className="rounded border bg-background px-2 py-1 text-xs"
                value={labelFilter || ""}
                onChange={e => {
                  const next = new URLSearchParams(searchParams)
                  if (e.target.value) next.set("labels", e.target.value)
                  else next.delete("labels")
                  next.delete("page")
                  setSearchParams(next)
                }}
              >
                <option value="">Label</option>
                {allLabels.map(l => (
                  <option key={l.name} value={l.name}>
                    {l.name}
                  </option>
                ))}
              </select>
            )}

            {/* Sort */}
            <select
              className="rounded border bg-background px-2 py-1 text-xs"
              value={`${sort}-${direction}`}
              onChange={e => {
                const [s, d] = e.target.value.split("-")
                const next = new URLSearchParams(searchParams)
                next.set("sort", s)
                next.set("direction", d)
                next.delete("page")
                setSearchParams(next)
              }}
            >
              <option value="created-desc">Newest</option>
              <option value="created-asc">Oldest</option>
              <option value="comments-desc">Most commented</option>
              <option value="updated-desc">Recently updated</option>
            </select>
          </div>
        </div>

        {/* Issue rows */}
        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <ErrorMessage message={error.message} onRetry={refetch} />
        ) : issues.length === 0 ? (
          stateFilter === "open" ? (
            openCount === 0 && closedCount === 0 ? (
              <EmptyState
                icon={CircleDot}
                title="Welcome to issues!"
                description="Create your first issue to get started."
                action={
                  <Link to={`/${owner}/${repo}/issues/new`}>
                    <Button className="bg-green-600 hover:bg-green-700 text-white">
                      New issue
                    </Button>
                  </Link>
                }
              />
            ) : (
              <EmptyState
                icon={CircleDot}
                title="No open issues"
                action={
                  <button
                    className="text-sm text-muted-foreground hover:text-foreground underline"
                    onClick={() => setParam("state", "closed")}
                  >
                    View closed issues
                  </button>
                }
              />
            )
          ) : (
            <EmptyState title="No closed issues" />
          )
        ) : (
          <div>
            {issues.map(issue => (
              <IssueRow key={issue.id} issue={issue} owner={owner} repo={repo} />
            ))}
          </div>
        )}
      </div>

      <Pagination
        page={page}
        hasNext={issues.length >= PER_PAGE}
        onPageChange={p => setParam("page", String(p))}
      />
    </div>
  )
}
