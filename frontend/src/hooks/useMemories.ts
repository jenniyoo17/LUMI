import { useCallback, useEffect, useState } from 'react'
import type { Memory } from '../types'
import { lumiService } from '../services/lumiService'

export function useMemories() {
  const [memories, setMemories] = useState<Memory[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    lumiService.getMemories().then((data) => {
      if (!cancelled) {
        setMemories(data)
        setLoading(false)
      }
    })
    return () => {
      cancelled = true
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    setMemories((prev) => prev.filter((m) => m.id !== id))
    const updated = await lumiService.deleteMemory(id)
    setMemories(updated)
  }, [])

  const clearAll = useCallback(async () => {
    setMemories([])
    await lumiService.clearAllMemories()
  }, [])

  return { memories, loading, remove, clearAll }
}
