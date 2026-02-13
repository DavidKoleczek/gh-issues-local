import { CircleDot, CheckCircle2, SkipForward } from "lucide-react"
import { cn } from "@/lib/utils"

interface IssueStateBadgeProps {
  state: "open" | "closed"
  stateReason?: "completed" | "not_planned" | "reopened" | null
}

export function IssueStateBadge({ state, stateReason }: IssueStateBadgeProps) {
  if (state === "open") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-green-600 px-2.5 py-0.5 text-xs font-medium text-white">
        <CircleDot className="h-3.5 w-3.5" />
        Open
      </span>
    )
  }

  const isNotPlanned = stateReason === "not_planned"

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium text-white",
        isNotPlanned ? "bg-muted-foreground" : "bg-purple-600",
      )}
    >
      {isNotPlanned ? <SkipForward className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
      Closed
    </span>
  )
}
