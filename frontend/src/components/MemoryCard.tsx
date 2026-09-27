import type { Memory } from '../types'

interface Props {
  memory: Memory
  onDelete: (id: string) => void
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const hours = Math.round(diffMs / (1000 * 60 * 60))
  if (hours < 1) return 'just now'
  if (hours < 24) return `${hours}h ago`
  const days = Math.round(hours / 24)
  return `${days}d ago`
}

export function MemoryCard({ memory, onDelete }: Props) {
  return (
    <div className="memory-card">
      <div>
        <div className="memory-card-text">{memory.text}</div>
        <div className="memory-card-meta">
          <span className="memory-source-tag">{memory.sourceId}</span>
          <span>{timeAgo(memory.createdAt)}</span>
        </div>
      </div>
      <button
        type="button"
        className="icon-btn"
        aria-label="Delete this memory"
        onClick={() => onDelete(memory.id)}
        title="Delete memory"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 6h18" strokeLinecap="round" />
          <path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2" strokeLinecap="round" />
          <path d="M19 6l-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </div>
  )
}
