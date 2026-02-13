import { useState, useEffect, useCallback } from "react"
import { getIssue } from "@/api"
import type { Issue } from "@/types"

export function useIssue(owner: string, repo: string, number: number) {
  const [data, setData] = useState<Issue | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchIssue = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const issue = await getIssue(owner, repo, number)
      setData(issue)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setLoading(false)
    }
  }, [owner, repo, number])

  useEffect(() => { fetchIssue() }, [fetchIssue])

  return { data, loading, error, refetch: fetchIssue }
}
