import { useState } from "react"
import { Button } from "@/components/ui/button"
import { updateIssue } from "@/api"
import { Loader2 } from "lucide-react"

interface StateActionsProps {
  owner: string
  repo: string
  issueNumber: number
  state: "open" | "closed"
  onUpdated: () => void
}

export function StateActions({ owner, repo, issueNumber, state, onUpdated }: StateActionsProps) {
  const [loading, setLoading] = useState(false)

  const handleClose = async (reason: "completed" | "not_planned") => {
    setLoading(true)
    try {
      await updateIssue(owner, repo, issueNumber, {
        state: "closed",
        state_reason: reason,
      })
      onUpdated()
    } finally {
      setLoading(false)
    }
  }

  const handleReopen = async () => {
    setLoading(true)
    try {
      await updateIssue(owner, repo, issueNumber, { state: "open" })
      onUpdated()
    } finally {
      setLoading(false)
    }
  }

  if (state === "open") {
    return (
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          onClick={() => handleClose("not_planned")}
          disabled={loading}
        >
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Close as not planned
        </Button>
        <Button
          variant="default"
          className="bg-purple-600 hover:bg-purple-700"
          onClick={() => handleClose("completed")}
          disabled={loading}
        >
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Close issue
        </Button>
      </div>
    )
  }

  return (
    <Button
      variant="outline"
      className="border-green-600 text-green-600 hover:bg-green-50"
      onClick={handleReopen}
      disabled={loading}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      Reopen issue
    </Button>
  )
}
