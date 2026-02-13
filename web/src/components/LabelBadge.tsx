import { contrastColor } from "@/lib/color"
import type { Label } from "@/types"

interface LabelBadgeProps {
  label: Label
}

export function LabelBadge({ label }: LabelBadgeProps) {
  const bg = `#${label.color}`
  const fg = contrastColor(label.color)

  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
      style={{ backgroundColor: bg, color: fg }}
    >
      {label.name}
    </span>
  )
}
