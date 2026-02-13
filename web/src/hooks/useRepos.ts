import { useState, useEffect } from "react"
import { listAllIssues } from "@/api"

interface Repo {
  owner: string
  repo: string
}

export function useRepos() {
  const [data, setData] = useState<Repo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchRepos = async () => {
    setLoading(true)
    setError(null)
    try {
      const issues = await listAllIssues({ state: "all", per_page: 100 })
      const seen = new Set<string>()
      const repos: Repo[] = []
      for (const issue of issues) {
        if (!issue.repository_url) continue
        // repository_url format: http://host/repos/{owner}/{repo}
        const parts = issue.repository_url.split("/repos/")[1]
        if (!parts) continue
        const [owner, repo] = parts.split("/")
        const key = `${owner}/${repo}`
        if (!seen.has(key)) {
          seen.add(key)
          repos.push({ owner, repo })
        }
      }
      setData(repos)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchRepos() }, [])

  return { data, loading, error, refetch: fetchRepos }
}
