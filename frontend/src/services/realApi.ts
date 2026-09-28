import type {
  ChatMessage,
  ContextReference,
  DataSource,
  DataSourceId,
  Memory,
  PermissionMap,
  PermissionSource,
} from '../types'
import { mockApi } from './mockApi'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const CHAT_ERROR_MESSAGE = "I'm having trouble connecting right now. Please try again in a moment."

interface ChatResponse {
  response: string
  used_context?: { label: string; sourceId: string }[]
}

interface BackendMemory {
  id: string
  content: string
  source: string
  timestamp: string
}

interface BackendChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

const PERMISSION_SOURCES: PermissionSource[] = ['notes', 'calendar', 'health', 'device', 'messages']

function isPermissionMap(value: unknown): value is PermissionMap {
  if (typeof value !== 'object' || value === null) return false
  const permissions = value as Record<string, unknown>
  return PERMISSION_SOURCES.every((source) => typeof permissions[source] === 'boolean')
}

function isBackendMemory(value: unknown): value is BackendMemory {
  if (typeof value !== 'object' || value === null) return false
  const memory = value as Record<string, unknown>
  return (
    typeof memory.id === 'string' &&
    typeof memory.content === 'string' &&
    typeof memory.source === 'string' &&
    typeof memory.timestamp === 'string'
  )
}

function isBackendChatMessage(value: unknown): value is BackendChatMessage {
  if (typeof value !== 'object' || value === null) return false
  const message = value as Record<string, unknown>
  return (
    typeof message.id === 'string' &&
    (message.role === 'user' || message.role === 'assistant') &&
    typeof message.content === 'string' &&
    typeof message.timestamp === 'string'
  )
}

function isChatResponse(value: unknown): value is ChatResponse {
  if (typeof value !== 'object' || value === null) return false
  const body = value as Record<string, unknown>
  return (
    typeof body.response === 'string' &&
    (body.used_context === undefined ||
      (Array.isArray(body.used_context) &&
        body.used_context.every(
          (item) =>
            typeof item === 'object' &&
            item !== null &&
            typeof (item as Record<string, unknown>).label === 'string' &&
            typeof (item as Record<string, unknown>).sourceId === 'string',
        )))
  )
}

function makeMessage(role: ChatMessage['role'], text: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    text,
    timestamp: new Date().toISOString(),
  }
}

export const realApi = {
  getDataSources(): Promise<DataSource[]> {
    return mockApi.getDataSources()
  },

  setDataSourceEnabled(id: DataSourceId, enabled: boolean): Promise<DataSource[]> {
    return mockApi.setDataSourceEnabled(id, enabled)
  },

  async getPermissions(): Promise<PermissionMap> {
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/permissions`)
    if (!response.ok) throw new Error(`Permission request failed (${response.status})`)

    const body: unknown = await response.json()
    if (!isPermissionMap(body)) throw new Error('Permission response was invalid')
    return body
  },

  async setPermission(
    source: PermissionSource,
    enabled: boolean,
  ): Promise<{ source: PermissionSource; enabled: boolean }> {
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/permissions/${source}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
    if (!response.ok) throw new Error(`Permission update failed (${response.status})`)

    const body: unknown = await response.json()
    if (
      typeof body !== 'object' ||
      body === null ||
      (body as Record<string, unknown>).source !== source ||
      typeof (body as Record<string, unknown>).enabled !== 'boolean'
    ) {
      throw new Error('Permission response was invalid')
    }
    return body as { source: PermissionSource; enabled: boolean }
  },

  getMessages(): Promise<ChatMessage[]> {
    return mockApi.getMessages()
  },

  async getChatHistory(): Promise<ChatMessage[]> {
    try {
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/chat/history`)
      if (!response.ok) throw new Error(`Chat history request failed (${response.status})`)

      const body: unknown = await response.json()
      if (!Array.isArray(body) || !body.every(isBackendChatMessage)) {
        throw new Error('Chat history response was invalid')
      }

      return body.map((message) => ({
        id: message.id,
        role: message.role,
        text: message.content,
        timestamp: message.timestamp,
      }))
    } catch {
      return mockApi.getChatHistory()
    }
  },

  async sendMessage(text: string): Promise<{ userMessage: ChatMessage; lumiMessage: ChatMessage }> {
    const userMessage = makeMessage('user', text)

    try {
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      if (!response.ok) throw new Error(`Chat request failed (${response.status})`)

      const body: unknown = await response.json()
      if (!isChatResponse(body)) throw new Error('Chat response was invalid')

      const lumiMessage = makeMessage('lumi', body.response)
      const usedContext: ContextReference[] | undefined = body.used_context?.map((item) => ({
        label: item.label,
        sourceId: item.sourceId as DataSourceId,
      }))
      if (usedContext?.length) lumiMessage.usedContext = usedContext

      return { userMessage, lumiMessage }
    } catch {
      return { userMessage, lumiMessage: makeMessage('lumi', CHAT_ERROR_MESSAGE) }
    }
  },

  async getMemories(): Promise<Memory[]> {
    try {
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/memory`)
      if (!response.ok) return []

      const body: unknown = await response.json()
      if (!Array.isArray(body) || !body.every(isBackendMemory)) return []

      return body.map((memory) => ({
        id: memory.id,
        text: memory.content,
        createdAt: memory.timestamp,
        sourceId: memory.source as DataSourceId,
      }))
    } catch {
      return []
    }
  },

  async deleteMemory(id: string): Promise<Memory[]> {
    try {
      await fetch(`${API_BASE_URL.replace(/\/$/, '')}/memory/${encodeURIComponent(id)}`, {
        method: 'DELETE',
      })
      return this.getMemories()
    } catch {
      return this.getMemories()
    }
  },

  async clearAllMemories(): Promise<Memory[]> {
    try {
      await fetch(`${API_BASE_URL.replace(/\/$/, '')}/memory`, {
        method: 'DELETE',
      })
      return this.getMemories()
    } catch {
      return this.getMemories()
    }
  },
}