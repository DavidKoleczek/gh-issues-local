import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

interface InlineEditProps {
  value: string
  onSave: (value: string) => Promise<void>
  multiline?: boolean
  placeholder?: string
}

export function InlineEdit({ value, onSave, multiline, placeholder }: InlineEditProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      await onSave(draft)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setDraft(value)
    setEditing(false)
  }

  if (!editing) {
    return (
      <div className="group">
        <Button
          variant="ghost"
          size="sm"
          className="text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => { setDraft(value); setEditing(true) }}
        >
          Edit
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {multiline ? (
        <Textarea
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder={placeholder}
          rows={8}
          className="font-mono text-sm"
        />
      ) : (
        <Input
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder={placeholder}
        />
      )}
      <div className="flex gap-2">
        <Button size="sm" onClick={handleSave} disabled={saving}>
          {saving && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
          Save
        </Button>
        <Button size="sm" variant="ghost" onClick={handleCancel} disabled={saving}>
          Cancel
        </Button>
      </div>
    </div>
  )
}
