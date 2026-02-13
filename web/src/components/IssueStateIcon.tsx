import { CircleDot, CheckCircle2, SkipForward } from "lucide-react"
import { cn } from "@/lib/utils"

interface IssueStateIconProps {
  state: "open" | "closed"
  stateReason?: "completed" | "not_planned" | "reopened" | null
  className?: string
}

export function IssueStateIcon({ state, stateReason, className }: IssueStateIconProps) {
  if (state === "open") {
    return <CircleDot className={cn("h-4 w-4 text-green-600", className)} />
  }
  if (stateReason === "not_planned") {
    return <SkipForward className={cn("h-4 w-4 text-muted-foreground", className)} />
  }
  return <CheckCircle2 className={cn("h-4 w-4 text-purple-600", className)} />
}
