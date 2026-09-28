import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChatMessage } from '../types'
import { lumiService } from '../services/lumiService'

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    lumiService
      .getChatHistory()
      .catch(() => lumiService.getMessages())
      .catch(() => [])
      .then((data) => {
        if (mounted.current) setMessages(data)
      })
      .finally(() => {
        if (mounted.current) setLoading(false)
      })
    return () => {
      mounted.current = false
    }
  }, [])

  const send = useCallback(async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return
    setSending(true)
    // Show the user's message immediately; reconcile once the mock replies.
    const optimistic: ChatMessage = {
      id: `optimistic-${Date.now()}`,
      role: 'user',
      text: trimmed,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, optimistic])

    const { lumiMessage } = await lumiService.sendMessage(trimmed)
    if (mounted.current) {
      setMessages((prev) => [...prev, lumiMessage])
      setSending(false)
    }
  }, [])

  return { messages, loading, sending, send }
}
