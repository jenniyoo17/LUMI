import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChatBubble } from '../components/ChatBubble'
import { TypingIndicator } from '../components/TypingIndicator'
import { useChat } from '../hooks/useChat'
import { useDataSources } from '../hooks/useDataSources'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n/LanguageContext'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

function greetingKey(): 'chat.greetingMorning' | 'chat.greetingAfternoon' | 'chat.greetingEvening' {
  const hour = new Date().getHours()
  if (hour < 12) return 'chat.greetingMorning'
  if (hour < 18) return 'chat.greetingAfternoon'
  return 'chat.greetingEvening'
}

export function Chat() {
  const { messages, loading, sending, send } = useChat()
  const { sources } = useDataSources()
  const { user } = useAuth()
  const { t, speechLocale } = useLanguage()
  const navigate = useNavigate()
  const [draft, setDraft] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  const micEnabled = sources.find((s) => s.id === 'microphone')?.enabled ?? false

  const { listening, supported, start, stop } = useSpeechRecognition({
    lang: speechLocale,
    onFinalResult: (text) => setDraft((prev) => (prev ? `${prev} ${text}` : text)),
  })

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, sending])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!draft.trim() || sending) return
    send(draft)
    setDraft('')
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  function handleMicClick() {
    if (!micEnabled) {
      navigate('/data')
      return
    }
    if (listening) stop()
    else start()
  }

  const firstName = (user?.name || user?.email.split('@')[0] || '').split(' ')[0]

  return (
    <div className="chat-shell">
      <div className="page-header">
        <h1 className="chat-greeting">{t(greetingKey(), { name: firstName })}</h1>
        <p>{t('chat.subtitle')}</p>
      </div>

      <div className="chat-scroll" ref={scrollRef}>
        {!loading && messages.map((m) => <ChatBubble key={m.id} message={m} />)}
        {sending && <TypingIndicator />}
      </div>

      <form className="chat-composer" onSubmit={handleSubmit}>
        <button
          type="button"
          className={`mic-btn${listening ? ' listening' : ''}${!micEnabled ? ' locked' : ''}`}
          onClick={handleMicClick}
          aria-label={micEnabled ? 'Toggle voice input' : 'Microphone is off'}
          title={
            !supported
              ? t('chat.micUnsupported')
              : !micEnabled
                ? t('chat.micLocked')
                : listening
                  ? t('chat.micListening')
                  : undefined
          }
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <rect x="9" y="3" width="6" height="11" rx="3" />
            <path d="M5 11a7 7 0 0 0 14 0" strokeLinecap="round" />
            <path d="M12 18v3" strokeLinecap="round" />
          </svg>
        </button>

        <textarea
          className="chat-input"
          placeholder={t('chat.placeholder')}
          rows={1}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={!draft.trim() || sending}
          aria-label="Send message"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 12L20 4L13 20L11 13L4 12Z" strokeLinejoin="round" strokeLinecap="round" />
          </svg>
        </button>
      </form>
      {!micEnabled && <p className="mic-hint">{t('chat.micLocked')}</p>}
    </div>
  )
}
