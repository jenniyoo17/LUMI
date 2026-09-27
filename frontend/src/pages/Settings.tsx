import { Link, useNavigate } from 'react-router-dom'
import { useDataSources } from '../hooks/useDataSources'
import { useMemories } from '../hooks/useMemories'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n/LanguageContext'
import { LanguageSwitcher } from '../components/LanguageSwitcher'

export function Settings() {
  const { sources } = useDataSources()
  const { memories, clearAll } = useMemories()
  const { user, logout } = useAuth()
  const { t } = useLanguage()
  const navigate = useNavigate()
  const connectedCount = sources.filter((s) => s.enabled).length

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div>
      <div className="page-header">
        <h1>{t('settings.title')}</h1>
        <p>{t('settings.subtitle')}</p>
      </div>

      <div className="settings-group">
        <h2>{t('settings.account')}</h2>
        <div className="settings-row">
          <div className="settings-row-text">
            <strong>{user?.name || user?.email}</strong>
            <span>{user?.email}</span>
          </div>
          <button type="button" className="btn-danger-text" onClick={handleLogout}>
            {t('settings.logout')}
          </button>
        </div>
      </div>

      <div className="settings-group">
        <h2>{t('settings.language')}</h2>
        <div className="settings-row">
          <div className="settings-row-text">
            <strong>{t('settings.language')}</strong>
            <span>{t('settings.languageDesc')}</span>
          </div>
          <LanguageSwitcher />
        </div>
      </div>

      <div className="settings-group">
        <h2>{t('settings.privacy')}</h2>
        <div className="settings-row">
          <div className="settings-row-text">
            <strong>{t('settings.privacyTitle')}</strong>
            <span>{t('settings.privacyDesc')}</span>
          </div>
          <Link to="/data" className="btn btn-ghost">
            {t('settings.review')}
          </Link>
        </div>
      </div>

      <div className="settings-group">
        <h2>{t('settings.connectedData')}</h2>
        <div className="settings-row">
          <div className="settings-row-text">
            <strong>{t('settings.connectedCount', { count: connectedCount })}</strong>
            <span>{t('settings.connectedDesc')}</span>
          </div>
          <Link to="/data" className="btn btn-ghost">
            {t('settings.manage')}
          </Link>
        </div>
      </div>

      <div className="settings-group">
        <h2>{t('settings.memory')}</h2>
        <div className="settings-row">
          <div className="settings-row-text">
            <strong>{t('settings.memoryCount', { count: memories.length })}</strong>
            <span>{t('settings.memoryDesc')}</span>
          </div>
          <Link to="/memory" className="btn btn-ghost">
            {t('settings.view')}
          </Link>
        </div>
        <div className="settings-row">
          <div className="settings-row-text">
            <strong>{t('settings.clearMemories')}</strong>
            <span>{t('settings.clearMemoriesDesc')}</span>
          </div>
          <button type="button" className="btn-danger-text" onClick={clearAll}>
            {t('settings.clearAll')}
          </button>
        </div>
      </div>

      <div className="settings-group">
        <h2>{t('settings.about')}</h2>
        <div className="about-card">{t('settings.aboutText')}</div>
      </div>
    </div>
  )
}
