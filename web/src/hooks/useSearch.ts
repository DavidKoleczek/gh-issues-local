import { useState, useEffect } from "react"
import { searchIssues } from "@/api"
import type { Issue } from "@/types"

interface SearchResult {
  total_count: number
  items: Issue[]
}

export function useSearch(query: string, params: { per_page?: number; page?: number } = {}) {
  const [data, setData] = useState<SearchResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchResults = async () => {
    if (!query) { setData(null); return }
    setLoading(true)
    setError(null)
    try {
      const result = await searchIssues(query, params)
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResults()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, JSON.stringify(params)])

  return { data, loading, error, refetch: fetchResults }
}
