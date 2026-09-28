import { useCallback, useEffect, useState } from 'react'
import type { DataSource, DataSourceId, PermissionSource } from '../types'
import { lumiService } from '../services/lumiService'

const PERMISSION_SOURCES: PermissionSource[] = ['notes', 'calendar', 'health', 'messages']

function hasBackendPermission(source: DataSourceId): source is Extract<PermissionSource, DataSourceId> {
  return PERMISSION_SOURCES.includes(source as PermissionSource)
}

export function useDataSources() {
  const [sources, setSources] = useState<DataSource[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    Promise.all([lumiService.getDataSources(), lumiService.getPermissions()])
      .then(([data, permissions]) => {
        if (!cancelled) {
          setSources(
            data.map((source) =>
              hasBackendPermission(source.id)
                ? { ...source, enabled: permissions[source.id] }
                : source,
            ),
          )
        }
      })
      .catch(() => {
        if (!cancelled) {
          return lumiService
            .getDataSources()
            .then(setSources)
            .catch(() => undefined)
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const toggle = useCallback(async (id: DataSourceId, enabled: boolean) => {
    try {
      if (hasBackendPermission(id)) {
        const result = await lumiService.setPermission(id, enabled)
        setSources((prev) =>
          prev.map((source) =>
            source.id === id ? { ...source, enabled: result.enabled } : source,
          ),
        )
      } else {
        const updated = await lumiService.setDataSourceEnabled(id, enabled)
        const updatedSource = updated.find((source) => source.id === id)
        if (updatedSource) {
          setSources((prev) =>
            prev.map((source) => (source.id === id ? updatedSource : source)),
          )
        }
      }
    } catch {
      // Keep the existing state when persistence fails.
    }
  }, [])

  return { sources, loading, toggle }
}
