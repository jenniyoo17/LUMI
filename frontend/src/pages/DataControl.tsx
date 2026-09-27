import { DataSourceToggle } from '../components/DataSourceToggle'
import { useDataSources } from '../hooks/useDataSources'
import { useLanguage } from '../i18n/LanguageContext'

export function DataControl() {
  const { sources, loading, toggle } = useDataSources()
  const { t } = useLanguage()

  return (
    <div>
      <div className="page-header">
        <h1>{t('data.title')}</h1>
        <p>{t('data.subtitle')}</p>
      </div>

      <div className="data-control-list">
        {!loading &&
          sources.map((source) => (
            <div className="source-row" key={source.id}>
              <div className="source-row-text">
                <strong>{source.label}</strong>
                <span>{source.usage}</span>
              </div>
              <DataSourceToggle
                enabled={source.enabled}
                label={source.label}
                onChange={(next) => toggle(source.id, next)}
              />
            </div>
          ))}
      </div>
    </div>
  )
}
