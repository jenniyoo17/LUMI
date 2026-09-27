export function TypingIndicator() {
  return (
    <div className="bubble-row lumi">
      <div className="avatar-lumi" aria-hidden="true" />
      <div className="typing-row" aria-label="Lumi is typing">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  )
}
