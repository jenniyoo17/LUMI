import type { ChatMessage } from '../types'

interface Props {
  message: ChatMessage
}

export function ChatBubble({ message }: Props) {
  const isUser = message.role === 'user'
  return (
    <div className={`bubble-row ${isUser ? 'user' : 'lumi'}`}>
      {!isUser && <div className="avatar-lumi" aria-hidden="true" />}
      <div>
        <div className={`bubble ${isUser ? 'user' : 'lumi'}`}>{message.text}</div>
        {!isUser && message.usedContext && message.usedContext.length > 0 && (
          <div className="bubble-meta">
            {message.usedContext.map((ref) => (
              <span key={ref.sourceId} className="context-pill">
                Using {ref.label}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
