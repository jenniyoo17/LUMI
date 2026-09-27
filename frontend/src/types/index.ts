// Core domain types shared across Lumi's frontend.
// Keep these in sync with whatever shape the real backend eventually returns —
// the service layer (src/services) is the only place that should need to change.

export type DataSourceId =
  | 'notes'
  | 'calendar'
  | 'health'
  | 'camera'
  | 'microphone'
  | 'location'
  | 'messages'

export interface DataSource {
  id: DataSourceId
  label: string
  description: string
  enabled: boolean
  /** Short, human phrase describing what Lumi does with this if it's on. */
  usage: string
}

export type ChatRole = 'user' | 'lumi'

export interface ContextReference {
  /** e.g. "Calendar", "Normalization notes" — shown as a small pill under a Lumi message */
  label: string
  sourceId: DataSourceId
}

export interface ChatMessage {
  id: string
  role: ChatRole
  text: string
  timestamp: string // ISO string
  /** Which connected sources Lumi drew on to produce this reply, if any. */
  usedContext?: ContextReference[]
}

export interface Memory {
  id: string
  text: string
  createdAt: string // ISO string
  sourceId: DataSourceId
}

export interface OnboardingSelection {
  sources: DataSourceId[]
  completed: boolean
}

// ---------- Auth ----------

export interface User {
  id: string
  email: string
  name?: string
}

export interface AuthResult {
  user: User
  token: string
}

