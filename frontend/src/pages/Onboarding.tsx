import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { DataSourceToggle } from '../components/DataSourceToggle'
import { useDataSources } from '../hooks/useDataSources'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n/LanguageContext'
import { Logo } from '../components/Logo'
import { LanguageSwitcher } from '../components/LanguageSwitcher'

export function Onboarding() {
  const { sources, loading, toggle } = useDataSources()
  const { user } = useAuth()
  const { t } = useLanguage()
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)

  const firstName = (user?.name || user?.email.split('@')[0] || '').split(' ')[0]

  async function handleContinue() {
    setSaving(true)
    if (user) localStorage.setItem(`lumi-onboarded-${user.id}`, 'true')
    navigate('/chat')
  }

  return (
    <div className="onboard-shell">
      <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 1 }}>
        <LanguageSwitcher />
      </div>
      <div className="onboard-card">
        <div className="onboard-mark">
          <Logo size={44} />
        </div>
        <h1>{t('onboarding.heading', { name: firstName })}</h1>
        <p className="onboard-lede">{t('onboarding.lede')}</p>

        <div className="source-list">
          {!loading &&
            sources.map((source) => (
              <div className="source-row" key={source.id}>
                <div className="source-row-text">
                  <strong>{source.label}</strong>
                  <span>{source.description}</span>
                </div>
                <DataSourceToggle
                  enabled={source.enabled}
                  label={source.label}
                  onChange={(next) => toggle(source.id, next)}
                />
              </div>
            ))}
        </div>

        <div className="onboard-actions">
          <button type="button" className="btn btn-primary" onClick={handleContinue} disabled={saving}>
            {t('onboarding.continue')}
          </button>
        </div>
        <p className="onboard-note">{t('onboarding.note')}</p>
      </div>
    </div>
  )
}
