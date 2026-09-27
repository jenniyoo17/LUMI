import { useCallback, useEffect, useState } from 'react'
import type { DataSource, DataSourceId } from '../types'
import { lumiService } from '../services/lumiService'

export function useDataSources() {
  const [sources, setSources] = useState<DataSource[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    lumiService.getDataSources().then((data) => {
      if (!cancelled) {
        setSources(data)
        setLoading(false)
      }
    })
    return () => {
      cancelled = true
    }
  }, [])

  const toggle = useCallback(async (id: DataSourceId, enabled: boolean) => {
    // Optimistic update so the switch feels instant.
    setSources((prev) => prev.map((s) => (s.id === id ? { ...s, enabled } : s)))
    const updated = await lumiService.setDataSourceEnabled(id, enabled)
    setSources(updated)
  }, [])

  return { sources, loading, toggle }
}
