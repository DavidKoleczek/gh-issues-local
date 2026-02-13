import { useState } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { createIssue } from "@/api"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

export default function NewIssue() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>()
  const navigate = useNavigate()

  const [title, setTitle] = useState("")
  const [body, setBody] = useState("")
  const [labels, setLabels] = useState("")
  const [assignees, setAssignees] = useState("")
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setError("Title is required")
      return
    }
    if (!owner || !repo) return

    setError("")
    setSubmitting(true)
    try {
      const issue = await createIssue(owner, repo, {
        title: title.trim(),
        body: body || undefined,
        labels: labels
          ? labels.split(",").map(s => s.trim()).filter(Boolean)
          : undefined,
        assignees: assignees
          ? assignees.split(",").map(s => s.trim()).filter(Boolean)
          : undefined,
      })
      navigate(`/${owner}/${repo}/issues/${issue.number}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create issue")
    } finally {
      setSubmitting(false)
    }
  }

  if (!owner || !repo) return null

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div>
        <Link to={`/${owner}/${repo}/issues`} className="text-sm text-muted-foreground hover:text-foreground">
          &larr; Back to issues
        </Link>
      </div>

      <h1 className="text-2xl font-bold">New issue</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="title" className="text-sm font-medium">
            Title
          </label>
          <Input
            id="title"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Title"
            autoFocus
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <div className="space-y-2">
          <label htmlFor="body" className="text-sm font-medium">
            Description
          </label>
          <Textarea
            id="body"
            value={body}
            onChange={e => setBody(e.target.value)}
            placeholder="Leave a comment"
            rows={10}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="labels" className="text-sm font-medium">
              Labels
            </label>
            <Input
              id="labels"
              value={labels}
              onChange={e => setLabels(e.target.value)}
              placeholder="bug, enhancement"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="assignees" className="text-sm font-medium">
              Assignees
            </label>
            <Input
              id="assignees"
              value={assignees}
              onChange={e => setAssignees(e.target.value)}
              placeholder="user1, user2"
            />
          </div>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <Button
            type="submit"
            className="bg-green-600 hover:bg-green-700 text-white"
            disabled={submitting}
          >
            {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Submit new issue
          </Button>
          <Link
            to={`/${owner}/${repo}/issues`}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  )
}
