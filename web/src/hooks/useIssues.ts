import { useState, useEffect } from "react"
import { listIssuesForRepo, type ListIssuesParams } from "@/api"
import type { Issue } from "@/types"

export function useIssues(owner: string, repo: string, params: ListIssuesParams = {}) {
  const [data, setData] = useState<Issue[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchIssues = async () => {
    setLoading(true)
    setError(null)
    try {
      const issues = await listIssuesForRepo(owner, repo, params)
      setData(issues)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIssues()
    // Re-fetch when params change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [owner, repo, JSON.stringify(params)])

  return { data, loading, error, refetch: fetchIssues }
}
