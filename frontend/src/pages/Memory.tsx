import { MemoryCard } from '../components/MemoryCard'
import { useMemories } from '../hooks/useMemories'
import { useLanguage } from '../i18n/LanguageContext'

export function Memory() {
  const { memories, loading, remove, clearAll } = useMemories()
  const { t } = useLanguage()

  return (
    <div>
      <div className="page-header">
        <h1>{t('memory.title')}</h1>
        <p>{t('memory.subtitle')}</p>
      </div>

      {!loading && memories.length > 0 && (
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
          <button type="button" className="btn-danger-text" onClick={clearAll}>
            {t('memory.clearAll')}
          </button>
        </div>
      )}

      {!loading && memories.length === 0 && <div className="memory-empty">{t('memory.empty')}</div>}

      <div className="memory-list">
        {!loading && memories.map((m) => <MemoryCard key={m.id} memory={m} onDelete={remove} />)}
      </div>
    </div>
  )
}
