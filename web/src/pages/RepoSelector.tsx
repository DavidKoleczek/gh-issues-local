import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useRepos } from "@/hooks/useRepos"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { ErrorMessage } from "@/components/ErrorMessage"
import { CircleDot, ArrowRight } from "lucide-react"

export default function RepoSelector() {
  const { data: repos, loading, error, refetch } = useRepos()
  const [direct, setDirect] = useState("")
  const navigate = useNavigate()

  const handleDirect = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = direct.trim()
    if (trimmed.includes("/")) {
      navigate(`/${trimmed}/issues`)
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} onRetry={refetch} />

  return (
    <div className="mx-auto max-w-lg space-y-8 py-8">
      <div className="text-center">
        <CircleDot className="mx-auto h-10 w-10 text-muted-foreground" />
        <h1 className="mt-4 text-2xl font-bold">gh-issues-local</h1>
        <p className="mt-1 text-muted-foreground">Select a repository to browse issues</p>
      </div>

      <form onSubmit={handleDirect} className="flex gap-2">
        <Input
          value={direct}
          onChange={e => setDirect(e.target.value)}
          placeholder="owner/repo"
          className="flex-1"
        />
        <Button type="submit" variant="outline" disabled={!direct.includes("/")}>
          <ArrowRight className="h-4 w-4" />
        </Button>
      </form>

      {repos.length === 0 ? (
        <div className="text-center space-y-3 py-8">
          <p className="text-muted-foreground">No issues yet. Create your first issue.</p>
          <form
            onSubmit={handleDirect}
            className="flex gap-2 max-w-xs mx-auto"
          >
            <Input
              value={direct}
              onChange={e => setDirect(e.target.value)}
              placeholder="owner/repo"
              className="flex-1"
            />
            <Button
              type="button"
              disabled={!direct.includes("/")}
              onClick={() => {
                if (direct.includes("/")) navigate(`/${direct.trim()}/issues/new`)
              }}
            >
              New issue
            </Button>
          </form>
        </div>
      ) : (
        <div className="space-y-2">
          {repos.map(r => (
            <Link
              key={`${r.owner}/${r.repo}`}
              to={`/${r.owner}/${r.repo}/issues`}
              className="flex items-center gap-3 rounded-lg border p-4 hover:bg-muted/50 transition-colors"
            >
              <CircleDot className="h-5 w-5 text-muted-foreground shrink-0" />
              <span className="font-medium">{r.owner}/{r.repo}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
