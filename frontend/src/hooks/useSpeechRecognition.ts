import { useCallback, useEffect, useRef, useState } from 'react'

// Minimal shape of the (non-standard, vendor-prefixed) Web Speech API.
// TypeScript's DOM lib doesn't ship types for it, so we declare just what we use.
interface SpeechRecognitionResultLike {
  isFinal: boolean
  [index: number]: { transcript: string }
}
interface SpeechRecognitionEventLike {
  resultIndex: number
  results: ArrayLike<SpeechRecognitionResultLike>
}
interface SpeechRecognitionLike extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  start: () => void
  stop: () => void
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: ((event: unknown) => void) | null
  onend: (() => void) | null
}

function getSpeechRecognitionCtor(): (new () => SpeechRecognitionLike) | null {
  const w = window as unknown as {
    SpeechRecognition?: new () => SpeechRecognitionLike
    webkitSpeechRecognition?: new () => SpeechRecognitionLike
  }
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null
}

interface Options {
  lang: string
  onFinalResult: (text: string) => void
}

export function useSpeechRecognition({ lang, onFinalResult }: Options) {
  const [listening, setListening] = useState(false)
  const [supported, setSupported] = useState(true)
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const onFinalResultRef = useRef(onFinalResult)
  onFinalResultRef.current = onFinalResult

  useEffect(() => {
    setSupported(getSpeechRecognitionCtor() !== null)
  }, [])

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
  }, [])

  const start = useCallback(() => {
    const Ctor = getSpeechRecognitionCtor()
    if (!Ctor) {
      setSupported(false)
      return
    }
    const recognition = new Ctor()
    recognition.lang = lang
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event) => {
      const last = event.results[event.results.length - 1]
      if (last?.isFinal) {
        const transcript = last[0]?.transcript ?? ''
        if (transcript.trim()) onFinalResultRef.current(transcript.trim())
      }
    }
    recognition.onerror = () => setListening(false)
    recognition.onend = () => setListening(false)

    recognitionRef.current = recognition
    setListening(true)
    recognition.start()
  }, [lang])

  useEffect(() => stop, [stop])

  return { listening, supported, start, stop }
}
