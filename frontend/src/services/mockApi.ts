import type {
  ChatMessage,
  ContextReference,
  DataSource,
  DataSourceId,
  Memory,
  PermissionMap,
  PermissionSource,
} from '../types'
import {
  defaultReply,
  initialDataSources,
  initialMemories,
  initialMessages,
  scriptedReplies,
  wait,
} from './mockData'

// In-memory store standing in for a backend/database.
// Everything here resets on page reload — that's expected for a mock layer.
let dataSources: DataSource[] = initialDataSources.map((s) => ({ ...s }))
let memories: Memory[] = [...initialMemories]
let messages: ChatMessage[] = [...initialMessages]
let deviceEnabled = false

function enabledSourceIds(): DataSourceId[] {
  return dataSources.filter((s) => s.enabled).map((s) => s.id)
}

function buildContextRefs(usesSources: DataSourceId[]): ContextReference[] {
  const enabled = new Set(enabledSourceIds())
  return usesSources
    .filter((id) => enabled.has(id))
    .map((id) => ({
      sourceId: id,
      label: dataSources.find((s) => s.id === id)?.label ?? id,
    }))
}

function craftReply(userText: string): { text: string; usedContext: ContextReference[] } {
  const lower = userText.toLowerCase()
  const match = scriptedReplies.find((entry) => entry.keywords.some((k) => lower.includes(k)))
  if (!match) {
    return { text: defaultReply, usedContext: [] }
  }
  const usedContext = buildContextRefs(match.usesSources)
  // If none of the sources this reply relies on are actually enabled, fall back to a generic tone.
  if (match.usesSources.length > 0 && usedContext.length === 0) {
    return {
      text: "I could probably help more with this if you connected your notes or calendar in Data Control — for now: tell me more?",
      usedContext: [],
    }
  }
  return { text: match.reply, usedContext }
}

/**
 * Mock Lumi API. This module is the ONLY place that should change when the
 * real backend is ready — see README.md "Connecting the real backend".
 */
export const mockApi = {
  async getDataSources(): Promise<DataSource[]> {
    await wait(200)
    return dataSources.map((s) => ({ ...s }))
  },

  async setDataSourceEnabled(id: DataSourceId, enabled: boolean): Promise<DataSource[]> {
    await wait(150)
    dataSources = dataSources.map((s) => (s.id === id ? { ...s, enabled } : s))
    return dataSources.map((s) => ({ ...s }))
  },

  async getPermissions(): Promise<PermissionMap> {
    await wait(150)
    return {
      notes: dataSources.find((source) => source.id === 'notes')?.enabled ?? false,
      calendar: dataSources.find((source) => source.id === 'calendar')?.enabled ?? false,
      health: dataSources.find((source) => source.id === 'health')?.enabled ?? false,
      device: deviceEnabled,
      messages: dataSources.find((source) => source.id === 'messages')?.enabled ?? false,
    }
  },

  async setPermission(
    source: PermissionSource,
    enabled: boolean,
  ): Promise<{ source: PermissionSource; enabled: boolean }> {
    await wait(150)
    if (source === 'device') {
      deviceEnabled = enabled
    } else {
      dataSources = dataSources.map((item) => (item.id === source ? { ...item, enabled } : item))
    }
    return { source, enabled }
  },

  async getMessages(): Promise<ChatMessage[]> {
    await wait(150)
    return [...messages]
  },

  async sendMessage(text: string): Promise<{ userMessage: ChatMessage; lumiMessage: ChatMessage }> {
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}-u`,
      role: 'user',
      text,
      timestamp: new Date().toISOString(),
    }
    messages = [...messages, userMessage]

    await wait(650) // simulate Lumi "thinking"

    const { text: replyText, usedContext } = craftReply(text)
    const lumiMessage: ChatMessage = {
      id: `msg-${Date.now()}-l`,
      role: 'lumi',
      text: replyText,
      timestamp: new Date().toISOString(),
      usedContext: usedContext.length > 0 ? usedContext : undefined,
    }
    messages = [...messages, lumiMessage]

    return { userMessage, lumiMessage }
  },

  async getMemories(): Promise<Memory[]> {
    await wait(200)
    return [...memories].sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1))
  },

  async deleteMemory(id: string): Promise<Memory[]> {
    await wait(150)
    memories = memories.filter((m) => m.id !== id)
    return [...memories]
  },

  async clearAllMemories(): Promise<Memory[]> {
    await wait(200)
    memories = []
    return []
  },
}
