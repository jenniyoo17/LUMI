import type { ChatMessage, DataSource, DataSourceId, Memory } from '../types'
import { mockApi } from './mockApi'

/**
 * lumiService is the single boundary between UI code and "wherever the data
 * actually comes from". Every page/hook imports FROM HERE, never from
 * mockApi directly. When the real backend exists, swap the implementation
 * below for real fetch()/websocket calls — no component changes needed.
 *
 * See README.md → "Connecting the real backend" for the swap-in steps.
 */
export interface LumiService {
  getDataSources(): Promise<DataSource[]>
  setDataSourceEnabled(id: DataSourceId, enabled: boolean): Promise<DataSource[]>
  getMessages(): Promise<ChatMessage[]>
  sendMessage(text: string): Promise<{ userMessage: ChatMessage; lumiMessage: ChatMessage }>
  getMemories(): Promise<Memory[]>
  deleteMemory(id: string): Promise<Memory[]>
  clearAllMemories(): Promise<Memory[]>
}

export const lumiService: LumiService = mockApi
