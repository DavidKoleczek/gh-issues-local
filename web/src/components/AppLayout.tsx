import { useState } from "react"
import { Link, Navigate, Outlet, useNavigate } from "react-router-dom"
import { CircleDot, Search } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { Input } from "@/components/ui/input"
import { LoadingSpinner } from "@/components/LoadingSpinner"

export function AppLayout() {
  const { required, authenticated, loading } = useAuth()
  const [query, setQuery] = useState("")
  const navigate = useNavigate()

  if (loading) return <LoadingSpinner />
  if (required && !authenticated) return <Navigate to="/login" replace />

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = query.trim()
    if (trimmed) {
      navigate(`/search?q=${encodeURIComponent(trimmed)}`)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-4 px-4">
          <Link to="/" className="flex items-center gap-2 font-semibold shrink-0">
            <CircleDot className="h-5 w-5" />
            gh-issues-local
          </Link>
          <form onSubmit={handleSearch} className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search all issues"
                className="pl-9 h-8 text-sm"
              />
            </div>
          </form>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
