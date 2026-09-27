import type { ChatMessage, DataSource, Memory } from '../types'

export const initialDataSources: DataSource[] = [
  {
    id: 'notes',
    label: 'Notes',
    description: 'Lecture notes, documents, anything you write or upload.',
    usage: 'Lets Lumi reference what you\'re studying or working on.',
    enabled: true,
  },
  {
    id: 'calendar',
    label: 'Calendar',
    description: 'Upcoming events, deadlines, exams.',
    usage: 'Lets Lumi know what\'s coming up in your day.',
    enabled: true,
  },
  {
    id: 'health',
    label: 'Health',
    description: 'Sleep, activity, and wearable data.',
    usage: 'Lets Lumi notice patterns, never to diagnose.',
    enabled: false,
  },
  {
    id: 'camera',
    label: 'Camera',
    description: 'Visual surroundings, only when you open it.',
    usage: 'Lets Lumi see what you show it, on request.',
    enabled: false,
  },
  {
    id: 'microphone',
    label: 'Microphone',
    description: 'Voice input for talking to Lumi.',
    usage: 'Lets you talk to Lumi instead of typing.',
    enabled: false,
  },
  {
    id: 'location',
    label: 'Location',
    description: 'Where you are, in general terms.',
    usage: 'Lets Lumi give context that depends on where you are.',
    enabled: false,
  },
  {
    id: 'messages',
    label: 'Messages',
    description: 'Texts and conversations you choose to share.',
    usage: 'Lets Lumi understand what\'s going on in your life.',
    enabled: false,
  },
]

export const initialMemories: Memory[] = [
  {
    id: 'mem-1',
    text: 'Exam tomorrow morning',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    sourceId: 'calendar',
  },
  {
    id: 'mem-2',
    text: 'Studying Computer Science Engineering',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 6).toISOString(),
    sourceId: 'notes',
  },
  {
    id: 'mem-3',
    text: 'Uploaded notes on database normalization',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
    sourceId: 'notes',
  },
]

export const initialMessages: ChatMessage[] = [
  {
    id: 'msg-1',
    role: 'lumi',
    text: 'Hey. Good to see you — how\'s today going?',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
]

/** A tiny library of canned Lumi replies keyed by a keyword, so the demo feels alive. */
export const scriptedReplies: { keywords: string[]; reply: string; usesSources: DataSource['id'][] }[] = [
  {
    keywords: ['stressed', 'stress', 'anxious', 'nervous', 'worried'],
    reply:
      "You have an exam tomorrow, and your notes show you've been going over normalization for a few days. Want to go through it together, or just talk for a bit?",
    usesSources: ['calendar', 'notes'],
  },
  {
    keywords: ['exam', 'test'],
    reply:
      'Your calendar has that exam tomorrow at 9. Based on your notes, normalization is the last topic you touched — want a quick recap?',
    usesSources: ['calendar', 'notes'],
  },
  {
    keywords: ['tired', 'sleep', 'exhausted'],
    reply:
      "Noted. If it helps, I won't add anything to your plate right now — just let me know if you want company or quiet.",
    usesSources: [],
  },
  {
    keywords: ['normalization', 'database'],
    reply:
      "From your notes: normalization is about organizing tables to reduce redundancy — 1NF, 2NF, 3NF build on each other. Want me to walk through an example from your own notes?",
    usesSources: ['notes'],
  },
  {
    keywords: ['hi', 'hello', 'hey'],
    reply: 'Hey! Nothing urgent on your plate right now that I can see. What\'s on your mind?',
    usesSources: [],
  },
]

export const defaultReply =
  "I hear you. I don't have enough context connected yet to say something more specific — but I'm listening."

export function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
