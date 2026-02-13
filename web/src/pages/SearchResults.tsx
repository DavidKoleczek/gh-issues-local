import { useSearchParams } from "react-router-dom"
import { useSearch } from "@/hooks/useSearch"
import { IssueRow } from "@/components/IssueRow"
import { Pagination } from "@/components/Pagination"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { ErrorMessage } from "@/components/ErrorMessage"
import { EmptyState } from "@/components/EmptyState"
import { Search } from "lucide-react"

const PER_PAGE = 25

export default function SearchResults() {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get("q") || ""
  const page = Number(searchParams.get("page")) || 1

  const { data, loading, error, refetch } = useSearch(query, {
    per_page: PER_PAGE,
    page,
  })

  const handlePageChange = (p: number) => {
    const next = new URLSearchParams(searchParams)
    next.set("page", String(p))
    setSearchParams(next)
  }

  // Parse owner/repo from repository_url
  const parseRepo = (url: string) => {
    const parts = url.split("/repos/")[1]
    if (!parts) return { owner: "", repo: "" }
    const [owner, repo] = parts.split("/")
    return { owner, repo }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">
        {data ? `${data.total_count} result${data.total_count === 1 ? "" : "s"}` : "Search results"}
      </h1>
      {query && (
        <p className="text-sm text-muted-foreground">
          Showing results for &quot;{query}&quot;
        </p>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message={error.message} onRetry={refetch} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Search}
          title={query ? `No results found for '${query}'` : "Enter a search term"}
        />
      ) : (
        <div className="rounded-lg border">
          {data.items.map(issue => {
            const { owner, repo } = parseRepo(issue.repository_url)
            return (
              <IssueRow
                key={`${owner}/${repo}/${issue.number}`}
                issue={issue}
                owner={owner}
                repo={repo}
                showRepo
              />
            )
          })}
        </div>
      )}

      {data && (
        <Pagination
          page={page}
          hasNext={data.items.length >= PER_PAGE}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  )
}
