import { useState, useEffect, useCallback } from "react"
import { listComments } from "@/api"
import type { Comment } from "@/types"

export function useComments(owner: string, repo: string, issueNumber: number) {
  const [data, setData] = useState<Comment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchComments = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const comments = await listComments(owner, repo, issueNumber)
      setData(comments)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setLoading(false)
    }
  }, [owner, repo, issueNumber])

  useEffect(() => { fetchComments() }, [fetchComments])

  return { data, loading, error, refetch: fetchComments }
}
