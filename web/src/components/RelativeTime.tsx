import { relativeTime } from "@/lib/time"

interface RelativeTimeProps {
  date: string
  className?: string
}

export function RelativeTime({ date, className }: RelativeTimeProps) {
  return (
    <time dateTime={date} title={new Date(date).toLocaleString()} className={className}>
      {relativeTime(date)}
    </time>
  )
}
